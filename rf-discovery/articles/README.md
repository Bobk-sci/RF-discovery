# Bibliothèque RF

**526 articles** rangés le 2026-09-18 (publications 1977–2026).

Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source (données PubMed / Europe PMC, NLM & EMBL-EBI).

## Répartition

| Modèle | Thème | Articles |
| --- | --- | ---: |
| in_vivo | neuro_comportement_cognition | 36 |
| dosimetrie_modelisation | dosimetrie_exposition | 35 |
| epidemiologie | neurodeveloppement | 35 |
| in_vivo | stress_oxydatif | 33 |
| epidemiologie | neuro_comportement_cognition | 30 |
| in_vivo | neurodeveloppement | 25 |
| epidemiologie | eeg_sommeil | 21 |
| epidemiologie | cancer | 19 |
| in_vitro | apoptose_mitochondrie | 19 |
| epidemiologie | general | 18 |
| in_vivo | apoptose_mitochondrie | 16 |
| in_vitro | stress_oxydatif | 14 |
| non_classe | neuro_comportement_cognition | 13 |
| dosimetrie_modelisation | neurodeveloppement | 10 |
| in_vivo | thermique | 10 |
| non_classe | neurodeveloppement | 10 |
| revue | general | 10 |
| in_vitro | cancer | 9 |
| in_vitro | general | 9 |
| in_vivo | genotoxicite_epigenetique | 9 |
| in_vitro | genotoxicite_epigenetique | 8 |
| in_vivo | general | 8 |
| revue | reproduction | 8 |
| in_vivo | reproduction | 7 |
| non_classe | general | 7 |
| humain_experimental | eeg_sommeil | 6 |
| non_classe | stress_oxydatif | 6 |
| epidemiologie | dosimetrie_exposition | 5 |
| non_classe | eeg_sommeil | 5 |
| dosimetrie_modelisation | general | 4 |
| dosimetrie_modelisation | genotoxicite_epigenetique | 4 |
| in_vitro | reproduction | 4 |
| in_vivo | dosimetrie_exposition | 4 |
| in_vivo | neuroinflammation | 4 |
| in_vivo | plasticite_synaptique | 4 |
| revue | cancer | 4 |
| revue | neuro_comportement_cognition | 4 |
| dosimetrie_modelisation | thermique | 3 |
| in_vitro | thermique | 3 |
| in_vivo | barriere_hemato_encephalique | 3 |
| in_vivo | cancer | 3 |
| in_vivo | eeg_sommeil | 3 |
| revue | eeg_sommeil | 3 |
| revue | genotoxicite_epigenetique | 3 |
| revue | neurodeveloppement | 3 |
| revue | stress_oxydatif | 3 |
| dosimetrie_modelisation | apoptose_mitochondrie | 2 |
| dosimetrie_modelisation | neuro_comportement_cognition | 2 |
| epidemiologie | reproduction | 2 |
| epidemiologie | thermique | 2 |
| non_classe | cancer | 2 |
| non_classe | genotoxicite_epigenetique | 2 |
| revue | dosimetrie_exposition | 2 |
| revue | thermique | 2 |
| dosimetrie_modelisation | stress_oxydatif | 1 |
| epidemiologie | stress_oxydatif | 1 |
| humain_experimental | neuro_comportement_cognition | 1 |
| in_vitro | barriere_hemato_encephalique | 1 |
| in_vitro | dosimetrie_exposition | 1 |
| in_vitro | neuroinflammation | 1 |
| in_vitro | plasticite_synaptique | 1 |
| non_classe | apoptose_mitochondrie | 1 |
| non_classe | thermique | 1 |
| revue | apoptose_mitochondrie | 1 |

## Comment c'est rangé

`<modele>/<theme>/<année>_<pmid>_<titre>.md`

Le classement compte les mots-clés de `config/taxonomy.yaml` dans le titre (×2.5) et le résumé ; la catégorie la mieux notée l'emporte, sous 1.0 point l'article part en catégorie par défaut. Les mots-clés qui ont déclenché la décision sont notés dans l'en-tête de chaque fiche (`*_indices`), donc vérifiables. Pour reclasser le corpus, modifier `taxonomy.yaml` et relancer avec `--reclasser`.

`index.csv` reprend tout le corpus en une ligne par article.

## Requête Europe PMC

```
("radiofrequency electromagnetic field" OR "radiofrequency radiation" OR "mobile phone radiation" OR "cell phone radiation" OR "wireless radiation" OR "Wi-Fi exposure" OR "GSM exposure" OR "UMTS exposure" OR "LTE exposure" OR "5G exposure" OR "millimeter wave exposure" OR "specific absorption rate" OR "900 MHz" OR "1800 MHz" OR "2.45 GHz") AND (FIRST_PDATE:[1990-01-01 TO 3000-12-31]) AND (HAS_ABSTRACT:Y)
```
