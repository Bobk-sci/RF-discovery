# Bruit-de-fond-DAB

Détourage d'**astrocytes marqués DAB** avec **auto-calibrage par image**, produisant
deux sorties distinctes : un **masque d'analyse fidèle** (Sholl / YOLO) et un
**rendu figure esthétique** (publication).

## Principe

- **Auto-calibrage PAR IMAGE.** Chaque image estime, à partir de ses propres
  statistiques, son point blanc (percentile haut de luminosité = illumination de
  fond), son échelle d'OD et ses seuils (Otsu + plancher robuste médiane +
  *k*·MAD). La **logique** de décision est identique d'une image à l'autre ;
  seules les **valeurs numériques** s'adaptent. Aucun réglage manuel image par
  image. Toutes les valeurs auto-estimées sont **journalisées**
  (`calibration_log.json` / `.csv`) pour la traçabilité et la reproductibilité.

- **Soustraction du fond local (neuropile diffus).** Sur une lame réelle, le
  neuropile est lui-même marqué au DAB : un seuillage global échoue (soit il
  capture tout le neuropile, soit son plancher robuste explose et ne capture
  plus rien). Les astrocytes se distinguent par une densité **localement**
  supérieure. On calcule donc une carte de **prominence** = densité DAB moins son
  fond local (passe-haut gaussien, `sigma` auto-dérivé de la taille de l'image) :
  le neuropile diffus (basse fréquence) est ramené à ~0, tandis que les somas
  compacts et les prolongements fins survivent. C'est cette carte, à fond aplati,
  qui est seuillée — d'où « zéro résidu de neuropile ».

- **Seuillage par hystérésis.** Un seuil unique force un mauvais compromis (trop
  haut = prolongements amputés ; trop bas = neuropile qui fuit). On utilise donc
  deux niveaux auto-estimés : un seuil **haut** (germes = astrocyte certain) et un
  seuil **bas** ; seules les structures **connectées** à un germe sont conservées.
  Résultat : prolongements fins **complets** et neuropile faible isolé rejeté. Ce
  seuillage reste FIDÈLE (aucune morphologie cosmétique) et convient au mode
  analyse.

- **Objectif visuel.** Astrocytes nets et **complets** sur fond parfaitement propre
  (blanc pur **ou** transparent), zéro résidu de neuropile, zéro fragment épars.
  La sortie n'est **pas** un masque binaire : le masque final est appliqué sur
  l'image **originale** pour conserver le brun DAB et la texture interne.

## Deux modes de sortie

L'embellissement altère la morphologie, donc les deux sorties sont séparées —
mais elles partent du **même** masque de segmentation ; seule l'étape de rendu
final diffère.

| Mode | Fichier | Usage | Traitement |
|------|---------|-------|------------|
| **ANALYSE** | `*_analysis_mask.png` | Sholl / YOLO en aval | masque **fidèle** : seuillage + retrait des micro-débris. **Aucune** fermeture ni lissage cosmétique. |
| **FIGURE** (transparent) | `*_figure_transparent.png` | illustration / publication | fermeture douce (reconnecte les gaps), retrait des débris, **feathering du canal ALPHA uniquement**, rehaussement de contraste **local** sur le signal. |
| **FIGURE** (fond blanc) | `*_figure_white.png` | idem, fond blanc pur | idem, composé sur blanc pur. |

> ⚠️ **Ne jamais mesurer le Sholl sur le mode figure.** L'embellissement (fermeture,
> feathering) modifie la morphologie. Le mode figure est un **sur-ensemble** du
> masque fidèle : il reconnecte et lisse, mais ne peut jamais amputer de structure.

## Rendu figure

- Composition sur fond **RGBA transparent** (PNG) **et** variante **fond blanc pur**.
- **Bords adoucis** : anti-aliasing / feathering du **canal ALPHA seul** (léger flou
  ~1 px sur l'alpha, jamais sur les pixels du signal).
- **Fermeture morphologique douce** pour reconnecter les prolongements fragmentés,
  puis **retrait des spurs / micro-débris** par filtre de taille (sans éroder les
  prolongements fins).
- **Rehaussement de contraste LOCAL** (CLAHE) appliqué **uniquement** au signal
  conservé — jamais au fond.

## Contrôle qualité (QC)

Le panneau `*_qc.png` réunit d'un coup d'œil : (1) originale, (2) **prominence
DAB** (densité à fond local soustrait — ce qui est réellement seuillé),
(3) seuillage par hystérésis (germes hauts + croissance), (4) **masque analyse
fidèle**,
(5) masque figure embelli, **(6) rendu figure fond blanc**, **(7) rendu figure
transparent sur damier** (pour visualiser l'alpha), (8) carte d'alpha. Les
panneaux (6) et (7) sont côte à côte avec le masque fidèle (4) pour vérifier que
l'embellissement n'a ni amputé ni inventé de structure.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Une image
python -m bruit_de_fond_dab.cli lame.tif -o resultats/

# Un dossier entier (auto-calibrage indépendant par image)
python -m bruit_de_fond_dab.cli dossier_lames/ -o resultats/

# Démonstration sur image DAB synthétique (aucune lame requise)
python -m bruit_de_fond_dab.cli --demo -o resultats/
```

Options : `--no-qc`, `--no-local-contrast`, `--feather-sigma <px>`,
`--close-radius <px>`, `--background-sigma <px>` (tous en auto par défaut,
dérivés de l'échelle de l'image).

**Réglage sur lames denses.** Si le neuropile reste visible dans le rendu,
_diminuer_ `--background-sigma` (fond local plus fin, plus agressif) ; si des
prolongements ou de gros somas sont amputés, _augmenter_ `--background-sigma`.
Le panneau 2 du QC (« Prominence DAB ») montre exactement ce qui est seuillé :
son fond doit être noir et seuls les astrocytes lumineux.

### API Python

```python
from bruit_de_fond_dab import process_image
out = process_image("lame.tif", "resultats/")
print(out.calibration.threshold, out.segmentation.n_objects)
```

## Sorties écrites par image

```
<stem>_analysis_mask.png       masque fidèle (MODE ANALYSE)
<stem>_figure_transparent.png  rendu esthétique, fond transparent
<stem>_figure_white.png        rendu esthétique, fond blanc pur
<stem>_qc.png                  panneau QC (8 vignettes)
calibration_log.json / .csv    valeurs auto-estimées par image (append)
```

## Structure du code

```
bruit_de_fond_dab/
  calibration.py   auto-calibrage par image (point blanc, prominence, seuils)
  segmentation.py  masque FIDÈLE (base commune, sans embellissement)
  rendering.py     MODE FIGURE (fermeture, feathering alpha, contraste local)
  qc.py            panneau QC 8 vignettes
  pipeline.py      orchestration + journalisation
  synthetic.py     image DAB synthétique de test
  cli.py           interface ligne de commande
tests/             tests de fumée bout en bout
```

## Tests

```bash
python -m pytest tests/
```
