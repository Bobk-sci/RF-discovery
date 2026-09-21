# Bibliothèque RF

Collecte d'articles scientifiques sur les **champs électromagnétiques radiofréquences**
(CEM-RF) et rangement automatique en sous-dossiers.

```bash
python -m collect_library --max-results 400                  # Europe PMC + PubMed
python -m collect_library --sources europepmc,pubmed,emfportal
python -m collect_library --emfportal-file page.html         # page EMF-Portal enregistrée
python -m collect_library --import-json export.json --import-source pubmed
python -m collect_library --reclasser                        # relit taxonomy.yaml, sans réseau
```

## Arborescence produite

```
articles/
  in_vivo/neurodeveloppement/2015_26239913_deleterious-impacts-of-a-900-mhz….md
  in_vitro/apoptose_mitochondrie/…       epidemiologie/cancer/…
  revue/…   dosimetrie_modelisation/…    ingenierie_materiel/…
  index.csv     # tout le corpus, une ligne par article
  README.md     # nombre d'articles par catégorie, régénéré à chaque run
```

Chaque fiche porte un en-tête YAML — PMID, DOI, année, journal, descripteurs MeSH, type de
publication, et les mots-clés qui ont décidé du rangement — suivi du **résumé d'origine**.

## Aucune référence inventée

Une fiche ne peut venir que d'une notice réellement renvoyée par une source : titre et
résumé recopiés mot pour mot, champ absent laissé **vide** plutôt que comblé, PMID/DOI
cliquable vers l'original. Aucun modèle de langue n'intervient dans la chaîne.

## Classement déterministe

Tout est dans `config/taxonomy.yaml`, modifiable sans toucher au code, puis `--reclasser`
réorganise le corpus existant sans rien re-télécharger.

- Comptage de mots-clés : titre ×2,5, descripteurs MeSH et type de publication ×2,
  résumé ×1. La catégorie la mieux notée gagne ; sous `min_score`, l'article va dans la
  catégorie par défaut de l'axe.
- `decisifs` : certains descripteurs tranchent seuls — le type « Review » attribué par
  PubMed, ou « NIH 3T3 Cells » qui désigne une lignée cellulaire alors que PubMed pose
  aussi « Animals » sur ces études.
- `pertinence` : une notice doit porter un vrai terme d'exposition RF. Sans ce garde-fou,
  « GSM » ramène des articles sur la **géosmine** et « Wi-Fi » des capteurs d'humidité du
  sol.
- `exclusions` + `sauf_si` : la méthodologie IRM est écartée, sauf si la notice porte une
  marque d'étude d'exposition — sinon on perdrait les études de provocation qui mesurent
  par IRM.

Les deux axes actuels : **modèle d'étude** (in vivo, in vitro, épidémiologie, humain
expérimental, dosimétrie, ingénierie matériel, revue) × **thème** (neurodéveloppement,
cognition, EEG/sommeil, stress oxydatif, neuroinflammation, barrière hémato-encéphalique,
génotoxicité, apoptose, calcium, cancer, reproduction, thermique, dosimétrie).

## Sources

| Source | Accès | Remarque |
|---|---|---|
| Europe PMC | REST, pagination `cursorMark` | couvre aussi les prépublications |
| PubMed | E-utilities NCBI (`esearch` + `efetch`) | apporte MeSH et types de publication |
| EMF-Portal | pages publiques | pas d'API : on n'extrait que les identifiants |

EMF-Portal n'ayant pas d'API, l'outil ne lit de ses pages que les identifiants stables
(PMID/DOI) et va chercher les métadonnées auprès de PubMed/Europe PMC, qui font foi. Si le
portail change ou devient injoignable, l'étape rend **zéro** article plutôt qu'une notice
approximative. Le gabarit d'URL de recherche est paramétrable (`--emfportal-url`).

## Importer dans EndNote ou Zotero, et récupérer les PDF

```bash
python -m export_refs                                # articles/bibliotheque-rf.{ris,bib}
python -m fetch_pdfs --email vous@exemple.fr --out pdf
python -m export_refs --pdf-dir pdf                  # rattache les PDF aux références
```

`bibliotheque-rf.ris` s'importe directement dans **EndNote** (*File → Import*) et dans
**Zotero** (*Fichier → Importer*) ; `bibliotheque-rf.bib` convient à Zotero et à LaTeX.
Le classement voyage en mots-clés (`modele:in_vivo`, `theme:neurodeveloppement`) : Zotero
en fait des étiquettes, sur lesquelles on reconstruit l'arborescence en une recherche
sauvegardée.

**Les PDF, eux, ne sont pas tous récupérables.** `fetch_pdfs` interroge
[Unpaywall](https://unpaywall.org) — API publique, une adresse courriel suffit — et
télécharge uniquement les versions légalement gratuites. Un article sous abonnement est
compté dans `sans_acces_libre` et **n'est pas téléchargé** : contourner un péage
violerait les conditions des éditeurs. Pour ceux-là, la voie normale est l'accès
institutionnel — dans Zotero, *Préférences → Général → « Trouver le PDF disponible »* avec
le proxy de votre bibliothèque configuré (*Préférences → Avancé → Proxys*).

Les PDF atterrissent dans `pdf/`, **non versionné** (volume, et licences variables selon
l'éditeur).

## Travailler en local : disque dur, Obsidian, EndNote

```bash
# 1. le corpus sur le disque externe
git clone https://github.com/Bobk-sci/RF-discovery /Volumes/DISQUE/rf-library
cd /Volumes/DISQUE/rf-library/rf-discovery
uv venv --python 3.11 .venv && . .venv/bin/activate && uv pip install -e .

# 2. les PDF en accès libre, à côté des fiches
python -m fetch_pdfs --email votre@adresse.fr --out pdf

# 3. les références, PDF rattachés
python -m export_refs --pdf-dir pdf
```

**Obsidian** : *Ouvrir un dossier comme coffre* → `rf-discovery/articles`. Chaque fiche
est déjà une note Markdown avec en-tête YAML ; le champ `tags` (`modele/in_vivo`,
`theme/neurodeveloppement`, `annee/2019`) alimente le panneau des étiquettes, et
`_cartes/Accueil.md` sert de point d'entrée vers une carte par modèle d'étude, articles
groupés par thème. Aucun plugin n'est nécessaire pour naviguer.

Pour interroger le corpus avec un modèle local, les greffons *Smart Connections* ou
*Copilot* se branchent sur [Ollama](https://ollama.com) : ils découpent les notes,
calculent des plongements et répondent en citant les fiches. Un modèle de 7 à 14 milliards
de paramètres (Qwen, Llama, Mistral) suffit pour résumer et rapprocher des résumés ; les
modèles pédagogiques de type *nanochat* (classe GPT-2) sont faits pour comprendre
l'entraînement, pas pour analyser de la littérature.

**EndNote** : *File → Import → File*, type **Reference Manager (RIS)**, fichier
`articles/bibliotheque-rf.ris`. Les champs `L1` pointent vers les PDF téléchargés : les
fichiers s'attachent aux références à l'import.

## Analyser le corpus avec Claude Code (VS Code)

Ouvrez le dépôt cloné dans VS Code, installez l'extension **Claude Code** (Extensions →
« Claude Code »), connectez-vous, et le dossier `.claude/commands/` fournit quatre
commandes taillées pour ce corpus :

| Commande | Ce qu'elle fait |
|---|---|
| `/synthese <thème>` | état des connaissances, organisé par modèle d'étude, chaque affirmation portant son PMID |
| `/contradictions <sujet>` | tableau des études qui se contredisent, avec les conditions d'exposition |
| `/lacunes <domaine>` | ce que le corpus ne couvre pas, et les requêtes à ajouter |
| `/redaction <objet>` | paragraphe sourcé, fiches utilisées et réserves explicites |

Toutes imposent la même règle que la collecte : **aucune référence, aucun chiffre qui ne
soit dans une fiche lue**. `CLAUDE.md` est chargé automatiquement et rappelle ces
contraintes.

## Runs incrémentaux

`data/seen_library.json` retient ce qui est déjà rangé : un rerun ne ramène que les
nouveautés. `index.csv` et `README.md` sont reconstruits depuis le disque, donc toujours
complets même après un run partiel.

## Automatisation

`.github/workflows/rf-library.yml` — lundi 05:00 UTC, ou **Actions → rf-library → Run
workflow** (accessible depuis un téléphone). Le run collecte, classe et committe
`articles/`. Les réponses brutes sont mises en cache dans `data/cache/` et les appels
respectent les limites de débit (backoff exponentiel).

## Développement

```bash
uv venv --python 3.11 .venv && . .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q && ruff check src tests && mypy src
```

La couche réseau est injectable : les tests passent des fetchers de fixture et ne touchent
jamais le réseau.
