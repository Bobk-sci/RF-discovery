# RF-Discovery

Pipeline autonome de **découverte inter-domaines** reliant l'exposition aux champs
électromagnétiques radiofréquences (CEM-RF) à des processus neurodéveloppementaux et
neurotoxiques. Le moteur de scoring est **déterministe et fondé sur un graphe hétérogène** ;
le LLM est strictement périphérique (voir `CLAUDE.md`).

## Principe

Le pipeline ne résume pas la littérature : il **prédit des liens non encore écrits**, les
classe par un score doté d'une **distribution nulle par permutation**, et se **valide
rétrospectivement** (time-slicing). Un candidat sans z-score n'est pas un candidat.

Chaîne de scoring : `métachemins → DWPC (degree-weighted path count) → null par XSwap
préservant les degrés → z-scores → combinaison logistique → nouveauté (Uzzi) + rafales
(Kleinberg) → classement composite`.

## Gate bloquant (§9)

Entraîné sur la littérature ≤ 2018, le pipeline doit retrouver les liens apparus en
2019–2025 avec **AUROC > 0.70** (échec sous 0.65). Sans ce gate, aucune hypothèse produite
n'est défendable. La validation tourne dans `src/validate/timeslice.py`.

## Démarrage

```bash
uv venv --python 3.11 .venv && . .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q                      # suite déterministe (fixtures, aucun réseau)
python -m run --synthetic      # démo bout-en-bout : scoring + gate + digest
```

`--synthetic` construit un graphe temporel structuré (`src/synthetic.py`) et démontre la
chaîne complète hors-ligne, gate compris. Le mode réel réutilise les mêmes étages de
scoring sur les données collectées via `src/collect/` (Europe PMC, PubTator3, …).

## Structure

| Répertoire | Rôle |
|---|---|
| `config/` | domaines, métachemins/métagraphe, sources, ordre des fournisseurs LLM |
| `src/collect/` | collecte (réseau injectable, cache disque, backoff) |
| `src/normalize/` | déduplication, mapping entités/prédicats |
| `src/graph/` | modèle sparse, métachemins, **DWPC**, **permutation XSwap**, embeddings |
| `src/score/` | nouveauté (Uzzi), rafales (Kleinberg), classement composite |
| `src/triage/` | embeddings de documents + classifieur supervisé |
| `src/llm/` | client à bascule de fournisseurs + explication (périphérique) |
| `src/validate/` | **time-slicing (gate)** et métriques |
| `src/report/` | digest markdown + corps d'Issues |

## Automatisation

`.github/workflows/weekly.yml` (lundi 06:00 UTC) collecte, met à jour le graphe, score,
rédige le digest, commite `data/graph.duckdb` + `reports/`, et ouvre une Issue
`weekly-digest`. Toute exception ouvre une Issue `pipeline-failure`.
`.github/workflows/validate.yml` relance lint + tests + gate.

## Corpus curé

`data/seeds/curated_214.csv` est un **stub** : y déposer le corpus curé réel de 214 articles
(colonnes `pmid,title,abstract,label,domain`) — c'est la vérité terrain du triage.
