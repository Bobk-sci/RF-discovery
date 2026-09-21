# Bibliothèque RF

**1534 articles** rangés le 2026-09-21 (publications 1960–2026).

Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source (données PubMed / Europe PMC, NLM & EMBL-EBI).

## Répartition

| Modèle | Thème | Articles |
| --- | --- | ---: |
| non_classe | general | 98 |
| dosimetrie_modelisation | dosimetrie_exposition | 90 |
| in_vivo | stress_oxydatif | 84 |
| in_vivo | neuro_comportement_cognition | 77 |
| epidemiologie | general | 62 |
| epidemiologie | neurodeveloppement | 55 |
| in_vivo | neurodeveloppement | 53 |
| in_vivo | general | 51 |
| ingenierie_materiel | dosimetrie_exposition | 51 |
| epidemiologie | neuro_comportement_cognition | 49 |
| revue | general | 39 |
| dosimetrie_modelisation | general | 38 |
| in_vitro | apoptose_mitochondrie | 38 |
| non_classe | neuro_comportement_cognition | 34 |
| in_vivo | reproduction | 33 |
| epidemiologie | eeg_sommeil | 31 |
| in_vitro | stress_oxydatif | 31 |
| in_vivo | apoptose_mitochondrie | 27 |
| epidemiologie | cancer | 26 |
| non_classe | neurodeveloppement | 26 |
| revue | reproduction | 25 |
| in_vivo | thermique | 24 |
| in_vivo | genotoxicite_epigenetique | 23 |
| in_vitro | genotoxicite_epigenetique | 21 |
| dosimetrie_modelisation | neurodeveloppement | 20 |
| dosimetrie_modelisation | thermique | 20 |
| in_vitro | cancer | 20 |
| revue | neuro_comportement_cognition | 20 |
| in_vitro | general | 18 |
| non_classe | thermique | 18 |
| revue | cancer | 18 |
| humain_experimental | eeg_sommeil | 17 |
| non_classe | cancer | 17 |
| ingenierie_materiel | general | 15 |
| revue | neurodeveloppement | 15 |
| non_classe | stress_oxydatif | 13 |
| revue | stress_oxydatif | 13 |
| in_vivo | neuroinflammation | 10 |
| non_classe | eeg_sommeil | 10 |
| dosimetrie_modelisation | neuro_comportement_cognition | 9 |
| humain_experimental | general | 9 |
| in_vivo | barriere_hemato_encephalique | 9 |
| in_vivo | dosimetrie_exposition | 9 |
| revue | thermique | 9 |
| epidemiologie | dosimetrie_exposition | 8 |
| in_vitro | thermique | 8 |
| in_vivo | cancer | 8 |
| revue | genotoxicite_epigenetique | 8 |
| revue | dosimetrie_exposition | 7 |
| dosimetrie_modelisation | cancer | 6 |
| epidemiologie | reproduction | 6 |
| humain_experimental | neuro_comportement_cognition | 6 |
| in_vitro | reproduction | 6 |
| in_vivo | eeg_sommeil | 6 |
| non_classe | dosimetrie_exposition | 6 |
| revue | eeg_sommeil | 6 |
| dosimetrie_modelisation | stress_oxydatif | 5 |
| in_vivo | plasticite_synaptique | 5 |
| in_vitro | dosimetrie_exposition | 4 |
| in_vitro | neuroinflammation | 4 |
| ingenierie_materiel | neuro_comportement_cognition | 4 |
| non_classe | reproduction | 4 |
| dosimetrie_modelisation | apoptose_mitochondrie | 3 |
| dosimetrie_modelisation | eeg_sommeil | 3 |
| dosimetrie_modelisation | genotoxicite_epigenetique | 3 |
| epidemiologie | thermique | 3 |
| humain_experimental | neurodeveloppement | 3 |
| in_vitro | barriere_hemato_encephalique | 3 |
| in_vitro | neuro_comportement_cognition | 3 |
| revue | apoptose_mitochondrie | 3 |
| dosimetrie_modelisation | reproduction | 2 |
| epidemiologie | stress_oxydatif | 2 |
| humain_experimental | dosimetrie_exposition | 2 |
| in_vitro | neurodeveloppement | 2 |
| ingenierie_materiel | cancer | 2 |
| non_classe | genotoxicite_epigenetique | 2 |
| revue | barriere_hemato_encephalique | 2 |
| dosimetrie_modelisation | barriere_hemato_encephalique | 1 |
| dosimetrie_modelisation | neuroinflammation | 1 |
| epidemiologie | genotoxicite_epigenetique | 1 |
| epidemiologie | plasticite_synaptique | 1 |
| humain_experimental | genotoxicite_epigenetique | 1 |
| humain_experimental | stress_oxydatif | 1 |
| humain_experimental | thermique | 1 |
| in_vitro | plasticite_synaptique | 1 |
| ingenierie_materiel | reproduction | 1 |
| ingenierie_materiel | thermique | 1 |
| non_classe | apoptose_mitochondrie | 1 |
| non_classe | barriere_hemato_encephalique | 1 |
| revue | calcium_canaux_ioniques | 1 |
| revue | plasticite_synaptique | 1 |

## Comment c'est rangé

`<modele>/<theme>/<année>_<pmid>_<titre>.md`

Le classement compte les mots-clés de `config/taxonomy.yaml` dans le titre (×2.5) et le résumé ; la catégorie la mieux notée l'emporte, sous 1.0 point l'article part en catégorie par défaut. Les mots-clés qui ont déclenché la décision sont notés dans l'en-tête de chaque fiche (`*_indices`), donc vérifiables. Pour reclasser le corpus, modifier `taxonomy.yaml` et relancer avec `--reclasser`.

`index.csv` reprend tout le corpus en une ligne par article.

## Requête Europe PMC

```
("radiofrequency electromagnetic field" OR "radiofrequency radiation" OR "radiofrequency exposure" OR "electromagnetic field exposure" OR "microwave radiation" OR "microwave exposure" OR "electromagnetic hypersensitivity" OR "radar exposure" OR "5G exposure" OR "3.5 GHz" OR "mobile phone radiation" OR "cell phone radiation" OR "wireless radiation" OR "Wi-Fi exposure" OR "GSM exposure" OR "UMTS exposure" OR "LTE exposure" OR "millimeter wave exposure" OR "specific absorption rate" OR "900 MHz" OR "1800 MHz" OR "2.45 GHz" OR "nonionizing radiation" OR "microwave irradiation" OR "915 MHz" OR "2450 MHz" OR "1.8 GHz" OR "W-CDMA" OR "DECT" OR "ultra-wideband") AND (FIRST_PDATE:[1970-01-01 TO 3000-12-31]) AND (HAS_ABSTRACT:Y)
```
