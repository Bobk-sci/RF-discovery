# Bibliothèque RF — collecte et classement d'articles CEM-RF

> Ce dépôt n'héberge plus qu'un **outil de veille**. Le moteur de découverte par graphe
> (DWPC, permutations XSwap, gate rétrospectif) a été retiré : voir l'historique git.

## Objectif
Collecter les articles scientifiques du domaine radiofréquences et les ranger dans une
arborescence lisible : `articles/<modèle d'étude>/<thème>/<année>_<pmid>_<titre>.md`.

## Règles non négociables
- **Aucune référence inventée.** Une fiche ne peut naître que d'une notice réellement
  renvoyée par une source. Titre, résumé et métadonnées sont recopiés mot pour mot ; un
  champ absent reste vide ; le PMID/DOI est présent et cliquable.
- **Aucun modèle de langue dans la chaîne.** Le classement est un comptage de mots-clés
  pondéré (titre ×`title_boost`, descripteurs MeSH ×`meta_boost`, résumé ×1), entièrement
  défini par `config/taxonomy.yaml`. Il est déterministe : mêmes entrées, même rangement.
- **Traçabilité.** Les mots-clés qui ont décidé du rangement sont écrits dans l'en-tête de
  chaque fiche (`modele_indices`, `theme_indices`).
- **Écarter plutôt que forcer.** Une notice hors sujet est écartée avec son motif ; une
  notice dont le plan d'étude n'est pas explicite va en catégorie par défaut.

## Modules (`src/`)
`collect/` (europepmc, pubmed, emfportal, cache) · `normalize/dedupe.py` ·
`library/` (classify, organize, importer) · `collect_library.py` (CLI).

## Contraintes techniques
Python 3.11+, fonctions ≤ 50 lignes, docstrings en français, couche réseau injectable
(les tests utilisent des fixtures, jamais le réseau), ruff + mypy propres.
