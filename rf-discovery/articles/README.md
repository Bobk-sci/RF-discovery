# Bibliothèque RF

**867 articles** rangés le 2026-09-18 (publications 1960–2026).

Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source (données PubMed / Europe PMC, NLM & EMBL-EBI).

## Répartition

| Modèle | Thème | Articles |
| --- | --- | ---: |
| epidemiologie | neurodeveloppement | 56 |
| in_vivo | stress_oxydatif | 56 |
| epidemiologie | neuro_comportement_cognition | 55 |
| epidemiologie | general | 54 |
| in_vivo | neuro_comportement_cognition | 44 |
| dosimetrie_modelisation | dosimetrie_exposition | 40 |
| in_vivo | neurodeveloppement | 40 |
| non_classe | general | 31 |
| epidemiologie | eeg_sommeil | 27 |
| in_vivo | general | 26 |
| in_vitro | apoptose_mitochondrie | 25 |
| non_classe | neuro_comportement_cognition | 24 |
| non_classe | neurodeveloppement | 24 |
| epidemiologie | cancer | 23 |
| in_vivo | apoptose_mitochondrie | 21 |
| in_vitro | stress_oxydatif | 20 |
| revue | general | 16 |
| in_vivo | thermique | 15 |
| dosimetrie_modelisation | neurodeveloppement | 13 |
| in_vivo | reproduction | 13 |
| dosimetrie_modelisation | general | 12 |
| humain_experimental | eeg_sommeil | 12 |
| in_vitro | genotoxicite_epigenetique | 12 |
| in_vivo | genotoxicite_epigenetique | 12 |
| revue | reproduction | 12 |
| in_vitro | general | 11 |
| in_vitro | cancer | 10 |
| revue | neuro_comportement_cognition | 10 |
| non_classe | stress_oxydatif | 9 |
| non_classe | eeg_sommeil | 8 |
| epidemiologie | dosimetrie_exposition | 7 |
| in_vivo | barriere_hemato_encephalique | 7 |
| revue | neurodeveloppement | 7 |
| in_vivo | neuroinflammation | 6 |
| dosimetrie_modelisation | thermique | 5 |
| in_vitro | reproduction | 5 |
| in_vivo | dosimetrie_exposition | 5 |
| revue | cancer | 5 |
| revue | genotoxicite_epigenetique | 5 |
| revue | stress_oxydatif | 5 |
| dosimetrie_modelisation | genotoxicite_epigenetique | 4 |
| epidemiologie | reproduction | 4 |
| humain_experimental | general | 4 |
| in_vitro | thermique | 4 |
| in_vivo | eeg_sommeil | 4 |
| in_vivo | plasticite_synaptique | 4 |
| non_classe | cancer | 4 |
| non_classe | genotoxicite_epigenetique | 4 |
| revue | dosimetrie_exposition | 4 |
| dosimetrie_modelisation | stress_oxydatif | 3 |
| humain_experimental | neuro_comportement_cognition | 3 |
| in_vitro | barriere_hemato_encephalique | 3 |
| in_vivo | cancer | 3 |
| non_classe | thermique | 3 |
| dosimetrie_modelisation | apoptose_mitochondrie | 2 |
| dosimetrie_modelisation | cancer | 2 |
| dosimetrie_modelisation | neuro_comportement_cognition | 2 |
| epidemiologie | thermique | 2 |
| in_vitro | neuro_comportement_cognition | 2 |
| in_vitro | neuroinflammation | 2 |
| non_classe | apoptose_mitochondrie | 2 |
| revue | eeg_sommeil | 2 |
| revue | thermique | 2 |
| dosimetrie_modelisation | barriere_hemato_encephalique | 1 |
| dosimetrie_modelisation | eeg_sommeil | 1 |
| dosimetrie_modelisation | reproduction | 1 |
| epidemiologie | stress_oxydatif | 1 |
| humain_experimental | stress_oxydatif | 1 |
| in_vitro | dosimetrie_exposition | 1 |
| in_vitro | neurodeveloppement | 1 |
| in_vitro | plasticite_synaptique | 1 |
| non_classe | reproduction | 1 |
| revue | apoptose_mitochondrie | 1 |

## Comment c'est rangé

`<modele>/<theme>/<année>_<pmid>_<titre>.md`

Le classement compte les mots-clés de `config/taxonomy.yaml` dans le titre (×2.5) et le résumé ; la catégorie la mieux notée l'emporte, sous 1.0 point l'article part en catégorie par défaut. Les mots-clés qui ont déclenché la décision sont notés dans l'en-tête de chaque fiche (`*_indices`), donc vérifiables. Pour reclasser le corpus, modifier `taxonomy.yaml` et relancer avec `--reclasser`.

`index.csv` reprend tout le corpus en une ligne par article.

## Requête Europe PMC

```
("radiofrequency electromagnetic field" OR "radiofrequency radiation" OR "mobile phone radiation" OR "cell phone radiation" OR "wireless radiation" OR "Wi-Fi exposure" OR "GSM exposure" OR "UMTS exposure" OR "LTE exposure" OR "5G exposure" OR "millimeter wave exposure" OR "specific absorption rate" OR "900 MHz" OR "1800 MHz" OR "2.45 GHz") AND (FIRST_PDATE:[1990-01-01 TO 3000-12-31]) AND (HAS_ABSTRACT:Y)
```
