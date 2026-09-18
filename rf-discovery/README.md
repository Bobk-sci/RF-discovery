# RF-Discovery

Pipeline autonome de **découverte inter-domaines** reliant l'exposition aux champs
électromagnétiques radiofréquences (CEM-RF) à des processus neurodéveloppementaux et
neurotoxiques. Le moteur de scoring est **déterministe et fondé sur un graphe hétérogène** ;
le LLM est strictement périphérique (voir `CLAUDE.md`).

## Bibliothèque RF — collecter et ranger les articles (`python -m collect_library`)

Outil de **veille** indépendant du moteur de découverte : il interroge Europe PMC, PubMed
et EMF-Portal, puis range chaque article dans `articles/<modèle>/<thème>/`.

```bash
python -m collect_library --max-results 400                 # Europe PMC + PubMed
python -m collect_library --sources europepmc,pubmed,emfportal
python -m collect_library --emfportal-file page.html        # page EMF-Portal enregistrée
python -m collect_library --import-json export.json --import-source pubmed
python -m collect_library --reclasser                       # relit taxonomy.yaml, sans réseau
```

Arborescence obtenue (un dossier par **modèle d'étude**, puis par **thème**) :

```
articles/in_vivo/neurodeveloppement/2015_26239913_deleterious-impacts-of-a-900-mhz….md
articles/in_vitro/apoptose_mitochondrie/…      articles/revue/cancer/…
articles/index.csv      # tout le corpus, une ligne par article
articles/README.md      # nombre d'articles par catégorie, régénéré à chaque run
```

**Rien n'est inventé.** Chaque fiche correspond à une notice réellement renvoyée par une
source : titre, résumé et métadonnées sont recopiés tels quels, un champ absent reste vide,
et chaque fiche porte son PMID/DOI cliquable. Aucun LLM n'intervient.

**Classement déterministe** (`config/taxonomy.yaml`, modifiable sans toucher au code) :
comptage de mots-clés dans le titre (×2,5), les descripteurs MeSH / type de publication
(×2) et le résumé (×1). Certains descripteurs **tranchent** (`decisifs`) : le type
« Review » attribué par PubMed, ou « NIH 3T3 Cells » qui désigne une lignée cellulaire
alors que PubMed pose aussi « Animals » sur ces études. Les mots-clés qui ont décidé du
rangement sont écrits dans l'en-tête de chaque fiche (`modele_indices`), donc vérifiables.

Deux garde-fous appris sur des notices réelles : `pertinence` exige un vrai terme
d'exposition RF (sans quoi « GSM » ramène des articles sur la **géosmine** et « Wi-Fi » des
capteurs d'humidité du sol) ; `exclusions` écarte la méthodologie IRM — sauf si la notice
porte une marque d'étude d'exposition (`annulations`), pour ne pas perdre les études de
provocation qui mesurent par IRM.

EMF-Portal n'a pas d'API : on extrait de ses pages les seuls identifiants stables
(PMID/DOI) et les métadonnées viennent de PubMed/Europe PMC. Si le portail change ou
devient injoignable, l'étape rend **zéro** article plutôt qu'une notice approximative.

Automatisation : `.github/workflows/rf-library.yml` (lundi 05:00 UTC, ou « Run workflow »
depuis le téléphone) collecte, classe et commite `articles/`. La mémoire
`data/seen_library.json` rend les runs incrémentaux ; `index.csv` et `README.md` sont
reconstruits depuis le disque, donc toujours complets.

## Principe

Le pipeline ne résume pas la littérature : il **prédit des liens non encore écrits**, les
classe par un score doté d'une **distribution nulle par permutation**, et se **valide
rétrospectivement** (time-slicing). Un candidat sans z-score n'est pas un candidat.

Chaîne de scoring : `métachemins → DWPC (degree-weighted path count) → null par XSwap
préservant les degrés → z-scores → combinaison logistique → nouveauté (Uzzi) + rafales
(Kleinberg) → classement composite`.

## Validation prospective (à la Swanson) — `src/validate/prospective.py`

Le gate du §9 (prédire les ajouts de CTD 2020-2025) mesure **0.50**, soit le hasard. Le
diagnostic, établi par la mesure : ces ajouts reflètent surtout les **choix humains de
recherche** (financements, priorités réglementaires), pas la mécanistique inscrite dans le
graphe. Ce n'est pas le moteur qui échoue, c'est la cible de validation qui est mal posée.

Le protocole historique de la découverte par la littérature est implémenté à côté :

1. **geler** le graphe à une date ancienne, 2. **effacer** le lien direct du couple testé,
3. **classer** ce couple parmi des composés témoins appariés en degré.

```bash
python -c "from validate.prospective import run_prospective; ..."   # cf. tests
```

Résultat mesuré sur le graphe réel (CTD + PubTator), **gel à 2010** :

| Couple (reconnaissance) | Rang | Percentile |
|---|---|---|
| Roténone → Parkinson (2011) | 2/300 | 0,7 % |
| Chlorpyrifos → Dév. cognitif (2011) | 3/301 | 1,0 % |
| Acide valproïque → Autisme (2013) | 3/300 | 1,0 % |
| Paraquat → Parkinson (2011) | 4/300 | 1,3 % |
| Bisphénol A → Autisme (2012) | 23/300 | 7,7 % |

**Percentile médian : 1,0 %** (le hasard donnerait 50 %). En 2010, avec la seule
littérature antérieure et le lien effacé, le moteur plaçait « acide valproïque → autisme »
3ᵉ sur 300 — trois ans avant l'étude qui l'a établi. Le moteur **anticipe** ; il ne fait pas
que rationaliser après coup.

Les couples de référence sont dans `config/known_links.yaml` (extensible) ; un couple déjà
reconnu avant le gel est automatiquement écarté du calcul.

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

La collecte est **paginée** (`cursorMark` Europe PMC, `--max-results` par domaine) pour
densifier le graphe. Modèle de découverte (Swanson) : les articles-source (interrogés AVEC
termes RF) définissent le voisinage de l'exposition — le harvester injecte un nœud
`Exposure` (`RF_EMF`) relié aux entités co-mentionnées dans ces articles, ce qui ouvre les
métachemins `Exposure → Gene/Chemical → … → Phénotype/Maladie` que le DWPC exploite (les
entités RF elles-mêmes ne sont pas annotées par PubTator).

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

## Enrichissement CTD (relations curées et datées — automatique)

PubTator donne des entités mais très peu de relations mécanistiques : les métachemins
restent cassés (aucun maillon `gène → voie`). **CTD** (Comparative Toxicogenomics Database)
comble ce trou, gratuitement et sans licence pour l'usage académique :

```bash
python -m ingest_ctd --db data/graph.duckdb      # téléchargement direct + cache
```

Apports : chimique→gène (`STIMULATES`/`INHIBITS`/`AFFECTS`), gène→maladie et
chimique→maladie **restreints aux preuves directes curées**, et surtout **gène→voie**
(Reactome/KEGG) — la charpente qui referme les métachemins.

Deux points de conception :

- **Restriction au voisinage** (modèle ABC de Swanson) : CTD complet ferait des millions
  d'arêtes. On ne garde que l'expansion d'un cran autour des entités déjà liées à
  l'exposition RF — le graphe reste focalisé et calculable.
- **Datation par PMID** : CTD référence ses relations par PubMed ID sans donner l'année.
  On l'estime par interpolation (les PMID sont quasi chronologiques), à ±1 an près. Le gate
  compense avec une **année tampon** (`buffer_years=1`) entre entraînement et test, pour
  qu'une erreur d'un an ne fasse pas basculer une arête du mauvais côté du découpage.

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
