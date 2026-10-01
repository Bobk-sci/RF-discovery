# Bibliothèque RF

**2470 articles** rangés le 2026-10-01 (publications 1960–2026).

Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source (données PubMed / Europe PMC, NLM & EMBL-EBI).

## Répartition

| Modèle | Thème | Articles |
| --- | --- | ---: |
| non_classe | general | 175 |
| dosimetrie_modelisation | dosimetrie_exposition | 151 |
| epidemiologie | general | 108 |
| in_vivo | stress_oxydatif | 99 |
| in_vivo | neuro_comportement_cognition | 95 |
| in_vivo | general | 90 |
| in_vivo | neurodeveloppement | 84 |
| dosimetrie_modelisation | general | 79 |
| epidemiologie | neurodeveloppement | 71 |
| revue | general | 69 |
| ingenierie_materiel | dosimetrie_exposition | 66 |
| in_vitro | genotoxicite_epigenetique | 65 |
| in_vitro | apoptose_mitochondrie | 59 |
| in_vivo | thermique | 58 |
| in_vitro | stress_oxydatif | 56 |
| epidemiologie | neuro_comportement_cognition | 52 |
| dosimetrie_modelisation | thermique | 51 |
| epidemiologie | cancer | 50 |
| in_vivo | reproduction | 48 |
| in_vivo | genotoxicite_epigenetique | 43 |
| revue | neuro_comportement_cognition | 37 |
| epidemiologie | eeg_sommeil | 36 |
| non_classe | neuro_comportement_cognition | 35 |
| revue | cancer | 35 |
| in_vivo | apoptose_mitochondrie | 34 |
| revue | neurodeveloppement | 34 |
| in_vitro | general | 33 |
| revue | reproduction | 33 |
| dosimetrie_modelisation | neurodeveloppement | 31 |
| in_vitro | cancer | 31 |
| non_classe | neurodeveloppement | 31 |
| non_classe | thermique | 28 |
| non_classe | cancer | 25 |
| in_vivo | cancer | 24 |
| in_vitro | thermique | 23 |
| humain_experimental | eeg_sommeil | 21 |
| revue | thermique | 21 |
| in_vivo | dosimetrie_exposition | 20 |
| revue | stress_oxydatif | 19 |
| humain_experimental | general | 18 |
| ingenierie_materiel | general | 17 |
| revue | genotoxicite_epigenetique | 17 |
| non_classe | stress_oxydatif | 16 |
| revue | dosimetrie_exposition | 16 |
| in_vitro | dosimetrie_exposition | 15 |
| epidemiologie | dosimetrie_exposition | 14 |
| in_vivo | neuroinflammation | 14 |
| revue | eeg_sommeil | 14 |
| dosimetrie_modelisation | neuro_comportement_cognition | 12 |
| non_classe | eeg_sommeil | 12 |
| dosimetrie_modelisation | cancer | 10 |
| dosimetrie_modelisation | eeg_sommeil | 10 |
| humain_experimental | neuro_comportement_cognition | 10 |
| in_vivo | barriere_hemato_encephalique | 10 |
| in_vitro | neuroinflammation | 9 |
| in_vivo | eeg_sommeil | 9 |
| epidemiologie | reproduction | 8 |
| in_vitro | reproduction | 8 |
| in_vivo | plasticite_synaptique | 8 |
| non_classe | dosimetrie_exposition | 8 |
| in_vitro | neuro_comportement_cognition | 7 |
| dosimetrie_modelisation | stress_oxydatif | 6 |
| in_vitro | neurodeveloppement | 6 |
| revue | barriere_hemato_encephalique | 6 |
| non_classe | reproduction | 5 |
| dosimetrie_modelisation | apoptose_mitochondrie | 4 |
| dosimetrie_modelisation | genotoxicite_epigenetique | 4 |
| epidemiologie | stress_oxydatif | 4 |
| in_vitro | calcium_canaux_ioniques | 4 |
| ingenierie_materiel | cancer | 4 |
| ingenierie_materiel | neuro_comportement_cognition | 4 |
| non_classe | genotoxicite_epigenetique | 4 |
| epidemiologie | thermique | 3 |
| humain_experimental | neurodeveloppement | 3 |
| in_vitro | barriere_hemato_encephalique | 3 |
| non_classe | apoptose_mitochondrie | 3 |
| revue | apoptose_mitochondrie | 3 |
| dosimetrie_modelisation | reproduction | 2 |
| epidemiologie | genotoxicite_epigenetique | 2 |
| humain_experimental | dosimetrie_exposition | 2 |
| humain_experimental | stress_oxydatif | 2 |
| revue | neuroinflammation | 2 |
| dosimetrie_modelisation | barriere_hemato_encephalique | 1 |
| dosimetrie_modelisation | neuroinflammation | 1 |
| epidemiologie | plasticite_synaptique | 1 |
| humain_experimental | genotoxicite_epigenetique | 1 |
| humain_experimental | thermique | 1 |
| in_vitro | plasticite_synaptique | 1 |
| in_vivo | calcium_canaux_ioniques | 1 |
| ingenierie_materiel | reproduction | 1 |
| ingenierie_materiel | thermique | 1 |
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
