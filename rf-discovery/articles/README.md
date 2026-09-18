# Bibliothèque RF

**40 articles** rangés le 2026-09-18 (publications 2004–2025).

Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source (données PubMed / Europe PMC, NLM & EMBL-EBI).

## Répartition

| Modèle | Thème | Articles |
| --- | --- | ---: |
| in_vivo | stress_oxydatif | 13 |
| in_vivo | neurodeveloppement | 5 |
| in_vivo | apoptose_mitochondrie | 4 |
| in_vitro | apoptose_mitochondrie | 3 |
| in_vivo | neuro_comportement_cognition | 3 |
| in_vitro | stress_oxydatif | 2 |
| in_vivo | genotoxicite_epigenetique | 2 |
| dosimetrie_modelisation | neuro_comportement_cognition | 1 |
| dosimetrie_modelisation | neurodeveloppement | 1 |
| humain_experimental | neuro_comportement_cognition | 1 |
| in_vitro | reproduction | 1 |
| in_vivo | general | 1 |
| in_vivo | plasticite_synaptique | 1 |
| in_vivo | reproduction | 1 |
| revue | reproduction | 1 |

## Comment c'est rangé

`<modele>/<theme>/<année>_<pmid>_<titre>.md`

Le classement compte les mots-clés de `config/taxonomy.yaml` dans le titre (×2.5) et le résumé ; la catégorie la mieux notée l'emporte, sous 1.0 point l'article part en catégorie par défaut. Les mots-clés qui ont déclenché la décision sont notés dans l'en-tête de chaque fiche (`*_indices`), donc vérifiables. Pour reclasser le corpus, modifier `taxonomy.yaml` et relancer avec `--reclasser`.

`index.csv` reprend tout le corpus en une ligne par article.

## Requête Europe PMC

```
("radiofrequency electromagnetic field" OR "radiofrequency radiation" OR "mobile phone radiation" OR "cell phone radiation" OR "wireless radiation" OR "Wi-Fi exposure" OR "GSM exposure" OR "UMTS exposure" OR "LTE exposure" OR "5G exposure" OR "millimeter wave exposure" OR "specific absorption rate" OR "900 MHz" OR "1800 MHz" OR "2.45 GHz") AND (FIRST_PDATE:[1990-01-01 TO 3000-12-31]) AND (HAS_ABSTRACT:Y)
```
