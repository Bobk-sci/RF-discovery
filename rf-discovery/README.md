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

## Collecte (harvester) — le pipeline va chercher les données lui-même

`src/harvest.py` est le chef d'orchestre de la collecte : pour chaque domaine de
`config/domains.yaml`, il interroge **Europe PMC** (PMIDs + résumés) puis **PubTator3**
(entités + relations pré-annotées, par lots), déduplique via `data/seen.json`, et écrit
articles + nœuds + arêtes dans DuckDB.

```bash
python -m harvest --db data/graph.duckdb      # collecte tous les domaines
python -m run     --db data/graph.duckdb --permutations 200   # score + gate + digest
```

**Aucun PDF à fournir.** Le pipeline consomme des résumés et des entités/relations déjà
extraites — pas du texte intégral. La collecte a besoin d'un **réseau ouvert** : elle tourne
sur **GitHub Actions** (`weekly.yml`, runner avec Internet) ou sur votre machine, pas dans un
environnement à politique réseau restreinte. Les réponses brutes sont mises en cache dans
`data/cache/` (un rerun ne re-sollicite pas les API) et respectent les rate limits (backoff
exponentiel, `User-Agent` avec email de contact). La couche réseau est injectable : les tests
utilisent des fixtures enregistrées, jamais le réseau.

PubTator3 étant ouvert (sans licence), le harvester amorce un graphe réel **sans** SemMedDB.
Pour un substrat plus riche, on ajoute SemMedDB par-dessus (section suivante) — les deux
sources normalisent vers les mêmes nœuds/arêtes (`normalize/records.py`), d'où la jointure.

## Ingestion SemMedDB (substrat du graphe)

SemMedDB fournit les triplets sujet-prédicat-objet sur tout MEDLINE — le substrat du
graphe (§4). Les dumps s'obtiennent gratuitement auprès de la NLM sous licence UMLS
([SemRep/SemMedDB](https://lhncbc.nlm.nih.gov/ii/tools/SemRep_SemMedDB_SKR.html)). Aucun
réseau : on lit les fichiers locaux (`.sql`, `.sql.gz` ou `.tsv`) **en flux**, sans MySQL.

```bash
python -m ingest \
  --predications semmedVER43_R_PREDICATION.sql.gz \
  --citations   semmedVER43_R_CITATIONS.sql.gz \
  --db data/graph.duckdb --max 2000000
```

L'ingestion mappe les types sémantiques UMLS vers les types de nœuds
(`config/umls_semtypes.yaml`), filtre les prédicats hors de l'ensemble retenu, rejette les
prédications négatives (`NEG_*`) et les hubs sémantiques vides (`config/metapaths.yaml`),
hérite l'année de publication depuis `CITATIONS`, agrège les arêtes multi-articles, puis
recalcule les degrés. Le résumé reporte la pente log-log de la distribution des degrés
(loi de puissance attendue, critère M2). Le corpus complet étant volumineux, `--max`
échantillonne ; un pré-filtrage par CUI/domaine en amont est recommandé pour un run ciblé.

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

## Dashboard GitHub Pages (M10)

`src/report/dashboard.py` génère un **site statique autonome** (HTML/CSS/JS en ligne,
aucune dépendance externe, coût nul) depuis la base DuckDB : historique des runs, table
des candidats du dernier run, **historique des verdicts humains** (`human_verdict`), et un
**graphe de force navigable** en JavaScript pur reliant les extrémités des meilleurs
candidats (liens proposés en pointillé rouge) à leur voisinage connu.

```bash
python -m report.dashboard --db data/graph.duckdb --out _site/index.html
```

Le dashboard est aussi régénéré à chaque `python -m run` (dans `docs/index.html`) et
déployé par `.github/workflows/pages.yml` via `actions/deploy-pages`. Les candidats sont
archivés à chaque run dans la table `candidates` (jamais supprimés, §12) : la colonne
`human_verdict`, annotée à la main, devient le jeu d'entraînement de la version suivante et
alimente l'historique des verdicts du dashboard.

## Automatisation

`.github/workflows/weekly.yml` (lundi 06:00 UTC) collecte, met à jour le graphe, score,
rédige le digest, commite `data/graph.duckdb` + `reports/`, et ouvre une Issue
`weekly-digest`. Toute exception ouvre une Issue `pipeline-failure`.
`.github/workflows/validate.yml` relance lint + tests + gate.

## Corpus curé

`data/seeds/curated_214.csv` est un **stub** : y déposer le corpus curé réel de 214 articles
(colonnes `pmid,title,abstract,label,domain`) — c'est la vérité terrain du triage.
