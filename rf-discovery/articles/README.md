# Bibliothèque RF

**1626 articles** rangés le 2026-09-21 (publications 1960–2026).

Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source (données PubMed / Europe PMC, NLM & EMBL-EBI).

## Répartition

| Modèle | Thème | Articles |
| --- | --- | ---: |
| non_classe | general | 119 |
| dosimetrie_modelisation | dosimetrie_exposition | 86 |
| in_vivo | stress_oxydatif | 82 |
| in_vivo | neuro_comportement_cognition | 73 |
| epidemiologie | general | 60 |
| epidemiologie | neurodeveloppement | 60 |
| epidemiologie | neuro_comportement_cognition | 59 |
| ingenierie_materiel | general | 58 |
| ingenierie_materiel | dosimetrie_exposition | 57 |
| in_vivo | neurodeveloppement | 52 |
| non_classe | neuro_comportement_cognition | 48 |
| in_vivo | general | 44 |
| non_classe | thermique | 35 |
| dosimetrie_modelisation | general | 34 |
| revue | general | 33 |
| in_vivo | reproduction | 32 |
| epidemiologie | eeg_sommeil | 30 |
| in_vitro | apoptose_mitochondrie | 29 |
| in_vitro | stress_oxydatif | 29 |
| in_vivo | apoptose_mitochondrie | 28 |
| non_classe | neurodeveloppement | 27 |
| non_classe | dosimetrie_exposition | 26 |
| revue | reproduction | 25 |
| dosimetrie_modelisation | thermique | 24 |
| epidemiologie | cancer | 23 |
| in_vivo | genotoxicite_epigenetique | 23 |
| in_vivo | thermique | 22 |
| dosimetrie_modelisation | neurodeveloppement | 20 |
| revue | neuro_comportement_cognition | 20 |
| in_vitro | general | 19 |
| in_vitro | genotoxicite_epigenetique | 19 |
| humain_experimental | eeg_sommeil | 17 |
| non_classe | stress_oxydatif | 17 |
| revue | thermique | 16 |
| in_vitro | cancer | 15 |
| ingenierie_materiel | neuro_comportement_cognition | 15 |
| revue | cancer | 14 |
| revue | neurodeveloppement | 13 |
| revue | stress_oxydatif | 13 |
| non_classe | eeg_sommeil | 11 |
| in_vivo | neuroinflammation | 10 |
| in_vivo | barriere_hemato_encephalique | 9 |
| dosimetrie_modelisation | neuro_comportement_cognition | 8 |
| epidemiologie | dosimetrie_exposition | 8 |
| humain_experimental | general | 8 |
| in_vivo | dosimetrie_exposition | 8 |
| revue | dosimetrie_exposition | 8 |
| revue | genotoxicite_epigenetique | 8 |
| humain_experimental | neuro_comportement_cognition | 7 |
| in_vivo | cancer | 7 |
| non_classe | apoptose_mitochondrie | 7 |
| in_vitro | reproduction | 6 |
| in_vitro | thermique | 6 |
| dosimetrie_modelisation | cancer | 5 |
| dosimetrie_modelisation | stress_oxydatif | 5 |
| epidemiologie | reproduction | 5 |
| in_vivo | eeg_sommeil | 5 |
| in_vivo | plasticite_synaptique | 5 |
| non_classe | cancer | 5 |
| non_classe | genotoxicite_epigenetique | 5 |
| dosimetrie_modelisation | apoptose_mitochondrie | 4 |
| dosimetrie_modelisation | genotoxicite_epigenetique | 4 |
| in_vitro | neuroinflammation | 4 |
| ingenierie_materiel | thermique | 4 |
| revue | apoptose_mitochondrie | 4 |
| revue | eeg_sommeil | 4 |
| dosimetrie_modelisation | eeg_sommeil | 3 |
| epidemiologie | thermique | 3 |
| humain_experimental | neurodeveloppement | 3 |
| in_vitro | barriere_hemato_encephalique | 3 |
| non_classe | reproduction | 3 |
| dosimetrie_modelisation | reproduction | 2 |
| epidemiologie | stress_oxydatif | 2 |
| humain_experimental | dosimetrie_exposition | 2 |
| in_vitro | dosimetrie_exposition | 2 |
| in_vitro | neuro_comportement_cognition | 2 |
| in_vitro | neurodeveloppement | 2 |
| dosimetrie_modelisation | barriere_hemato_encephalique | 1 |
| dosimetrie_modelisation | neuroinflammation | 1 |
| epidemiologie | genotoxicite_epigenetique | 1 |
| epidemiologie | plasticite_synaptique | 1 |
| humain_experimental | genotoxicite_epigenetique | 1 |
| humain_experimental | stress_oxydatif | 1 |
| humain_experimental | thermique | 1 |
| in_vitro | plasticite_synaptique | 1 |
| ingenierie_materiel | cancer | 1 |
| ingenierie_materiel | reproduction | 1 |
| revue | barriere_hemato_encephalique | 1 |
| revue | calcium_canaux_ioniques | 1 |
| revue | plasticite_synaptique | 1 |

## Comment c'est rangé

`<modele>/<theme>/<année>_<pmid>_<titre>.md`

Le classement compte les mots-clés de `config/taxonomy.yaml` dans le titre (×2.5) et le résumé ; la catégorie la mieux notée l'emporte, sous 1.0 point l'article part en catégorie par défaut. Les mots-clés qui ont déclenché la décision sont notés dans l'en-tête de chaque fiche (`*_indices`), donc vérifiables. Pour reclasser le corpus, modifier `taxonomy.yaml` et relancer avec `--reclasser`.

`index.csv` reprend tout le corpus en une ligne par article.

## Requête Europe PMC

```
("radiofrequency electromagnetic field" OR "radiofrequency radiation" OR "radiofrequency exposure" OR "electromagnetic field exposure" OR "microwave radiation" OR "microwave exposure" OR "base station" OR "cell tower" OR "electromagnetic hypersensitivity" OR "radar exposure" OR "5G exposure" OR "3.5 GHz" OR "mobile phone radiation" OR "cell phone radiation" OR "wireless radiation" OR "Wi-Fi exposure" OR "GSM exposure" OR "UMTS exposure" OR "LTE exposure" OR "5G exposure" OR "millimeter wave exposure" OR "specific absorption rate" OR "900 MHz" OR "1800 MHz" OR "2.45 GHz") AND (FIRST_PDATE:[1990-01-01 TO 3000-12-31]) AND (HAS_ABSTRACT:Y)
```
