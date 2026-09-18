# Bibliothèque RF

**1173 articles** rangés le 2026-09-18 (publications 1960–2026).

Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source (données PubMed / Europe PMC, NLM & EMBL-EBI).

## Répartition

| Modèle | Thème | Articles |
| --- | --- | ---: |
| dosimetrie_modelisation | dosimetrie_exposition | 86 |
| non_classe | general | 75 |
| in_vivo | stress_oxydatif | 69 |
| epidemiologie | neuro_comportement_cognition | 58 |
| epidemiologie | neurodeveloppement | 57 |
| epidemiologie | general | 56 |
| in_vivo | neuro_comportement_cognition | 55 |
| in_vivo | neurodeveloppement | 46 |
| in_vivo | general | 33 |
| non_classe | neuro_comportement_cognition | 31 |
| epidemiologie | eeg_sommeil | 27 |
| in_vitro | apoptose_mitochondrie | 27 |
| in_vivo | reproduction | 27 |
| in_vitro | stress_oxydatif | 26 |
| dosimetrie_modelisation | general | 25 |
| non_classe | neurodeveloppement | 25 |
| epidemiologie | cancer | 23 |
| revue | general | 23 |
| in_vivo | apoptose_mitochondrie | 22 |
| in_vivo | thermique | 19 |
| revue | reproduction | 19 |
| in_vivo | genotoxicite_epigenetique | 17 |
| revue | neuro_comportement_cognition | 17 |
| dosimetrie_modelisation | neurodeveloppement | 16 |
| dosimetrie_modelisation | thermique | 15 |
| humain_experimental | eeg_sommeil | 15 |
| in_vitro | genotoxicite_epigenetique | 15 |
| in_vitro | cancer | 13 |
| in_vitro | general | 12 |
| non_classe | stress_oxydatif | 11 |
| non_classe | thermique | 11 |
| revue | neurodeveloppement | 11 |
| revue | stress_oxydatif | 11 |
| in_vivo | barriere_hemato_encephalique | 9 |
| in_vivo | neuroinflammation | 9 |
| revue | cancer | 9 |
| epidemiologie | dosimetrie_exposition | 8 |
| non_classe | eeg_sommeil | 8 |
| revue | thermique | 8 |
| in_vivo | dosimetrie_exposition | 7 |
| revue | genotoxicite_epigenetique | 7 |
| dosimetrie_modelisation | neuro_comportement_cognition | 6 |
| in_vitro | reproduction | 6 |
| epidemiologie | reproduction | 5 |
| humain_experimental | general | 5 |
| humain_experimental | neuro_comportement_cognition | 5 |
| in_vivo | cancer | 5 |
| in_vivo | plasticite_synaptique | 5 |
| dosimetrie_modelisation | cancer | 4 |
| dosimetrie_modelisation | genotoxicite_epigenetique | 4 |
| dosimetrie_modelisation | stress_oxydatif | 4 |
| in_vitro | thermique | 4 |
| in_vivo | eeg_sommeil | 4 |
| non_classe | cancer | 4 |
| non_classe | dosimetrie_exposition | 4 |
| non_classe | genotoxicite_epigenetique | 4 |
| revue | dosimetrie_exposition | 4 |
| revue | eeg_sommeil | 4 |
| dosimetrie_modelisation | apoptose_mitochondrie | 3 |
| in_vitro | barriere_hemato_encephalique | 3 |
| in_vitro | neuroinflammation | 3 |
| non_classe | apoptose_mitochondrie | 3 |
| non_classe | reproduction | 3 |
| revue | apoptose_mitochondrie | 3 |
| epidemiologie | thermique | 2 |
| humain_experimental | dosimetrie_exposition | 2 |
| in_vitro | dosimetrie_exposition | 2 |
| in_vitro | neuro_comportement_cognition | 2 |
| dosimetrie_modelisation | barriere_hemato_encephalique | 1 |
| dosimetrie_modelisation | eeg_sommeil | 1 |
| dosimetrie_modelisation | reproduction | 1 |
| epidemiologie | genotoxicite_epigenetique | 1 |
| epidemiologie | plasticite_synaptique | 1 |
| epidemiologie | stress_oxydatif | 1 |
| humain_experimental | stress_oxydatif | 1 |
| in_vitro | neurodeveloppement | 1 |
| in_vitro | plasticite_synaptique | 1 |
| revue | barriere_hemato_encephalique | 1 |
| revue | calcium_canaux_ioniques | 1 |
| revue | plasticite_synaptique | 1 |

## Comment c'est rangé

`<modele>/<theme>/<année>_<pmid>_<titre>.md`

Le classement compte les mots-clés de `config/taxonomy.yaml` dans le titre (×2.5) et le résumé ; la catégorie la mieux notée l'emporte, sous 1.0 point l'article part en catégorie par défaut. Les mots-clés qui ont déclenché la décision sont notés dans l'en-tête de chaque fiche (`*_indices`), donc vérifiables. Pour reclasser le corpus, modifier `taxonomy.yaml` et relancer avec `--reclasser`.

`index.csv` reprend tout le corpus en une ligne par article.

## Requête Europe PMC

```
("radiofrequency electromagnetic field" OR "radiofrequency radiation" OR "mobile phone radiation" OR "cell phone radiation" OR "wireless radiation" OR "Wi-Fi exposure" OR "GSM exposure" OR "UMTS exposure" OR "LTE exposure" OR "5G exposure" OR "millimeter wave exposure" OR "specific absorption rate" OR "900 MHz" OR "1800 MHz" OR "2.45 GHz") AND (FIRST_PDATE:[1990-01-01 TO 3000-12-31]) AND (HAS_ABSTRACT:Y)
```
