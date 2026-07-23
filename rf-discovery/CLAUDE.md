# RF-Discovery — pipeline autonome de découverte inter-domaines (CEM-RF)

> Spécification de référence. Le moteur de scoring est **déterministe et fondé sur un
> graphe hétérogène**. Le LLM est confiné à trois rôles périphériques (normalisation,
> explication d'un candidat *déjà scoré*, rédaction du digest) et **n'entre jamais dans
> le chemin de scoring**.

## Objectif
Générer chaque semaine, à coût nul, un petit nombre d'hypothèses mécanistiques nouvelles
reliant l'exposition aux CEM-RF à des processus neurodéveloppementaux/neurotoxiques. Le
pipeline prédit des liens non encore écrits, les classe par un score doté d'une
distribution nulle, et se valide rétrospectivement.

**Gate bloquant (§9).** Entraîné sur la littérature ≤ 2018, le pipeline doit retrouver les
liens apparus en 2019–2025 avec AUROC > 0.70 (échec sous 0.65). Sans ce gate, aucune
hypothèse n'est défendable.

## Cœur algorithmique
- **Métachemins** longueur 2–4 entre `Exposure`/entité-RF et `Disease`/`Phenotype`
  neurodéveloppemental ; hubs sémantiques vides exclus.
- **DWPC** : `DWPC(a,c,m) = Σ_paths Π_{n∈path} degree(n)^(-w)`, `w = 0.4` (vectorisé, sparse).
- **Null par permutation** : 200 XSwap préservant les degrés → `z = (DWPC−μ)/σ`.
  *Un candidat sans z-score n'est pas un candidat.*
- **Combinaison** : régression logistique sur les features `z(a,c,m)`.
- **Nouveauté** : `novelty_z` à la Uzzi + modularité inter-domaines.
- **Rafales** : Kleinberg (2002) pour prioriser les termes B en accélération.
- **Triage** : SPECTER2 + régression logistique sur le corpus curé (`data/seeds/curated_214.csv`).

## Modules (`src/`)
`collect/` (europepmc, pubtator, cache) · `normalize/` (dedupe, entities) ·
`graph/` (schema, build, metapaths, dwpc, permute, embed) ·
`score/` (novelty, burst, rank) · `triage/` (specter, classify) ·
`llm/` (client, explain) · `validate/` (timeslice, metrics) · `report/` (digest, issue).

## Règles
Python 3.11+, déterministe (`random_state` fixé, permutations semées/journalisées), chaque
module testé (fixtures, jamais le réseau), fonctions ≤ 50 lignes, DWPC vectorisé, logs JSON,
digest markdown pur. Ne jamais supprimer une ligne de `candidates`.

Voir le dépôt racine pour la spécification longue d'origine ; ce fichier en est le résumé
opérationnel pour le sous-projet `rf-discovery/`.
