# Bibliothèque RF

Veille bibliographique sur les **champs électromagnétiques radiofréquences** (CEM-RF) :
l'outil interroge Europe PMC, PubMed et EMF-Portal, puis range chaque article dans
`rf-discovery/articles/<modèle d'étude>/<thème>/`.

➡️ Le corpus et le mode d'emploi sont dans [`rf-discovery/`](rf-discovery/) — voir son
[README](rf-discovery/README.md).

**Aucune référence n'est inventée.** Chaque fiche correspond à une notice réellement
renvoyée par une de ces bases : titre, résumé et métadonnées sont recopiés tels quels, un
champ absent reste vide, et le PMID/DOI renvoie à la source. Aucun modèle de langue
n'intervient : le classement est un comptage de mots-clés défini dans
`rf-discovery/config/taxonomy.yaml`, donc reproductible et vérifiable.

## Démarrage rapide

```bash
cd rf-discovery
uv venv --python 3.11 .venv && . .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q                                   # suite hors-ligne (fixtures)
python -m collect_library --max-results 400 # collecte + rangement
```

## Automatisation

`.github/workflows/rf-library.yml` (lundi 05:00 UTC, ou **Actions → rf-library → Run
workflow**) collecte, classe et committe `rf-discovery/articles/`. Les runs sont
incrémentaux : `data/seen_library.json` retient ce qui est déjà rangé, seuls les articles
nouveaux sont ajoutés.

`.github/workflows/rf-library-validate.yml` relance lint, typage et tests à chaque
modification du code.
