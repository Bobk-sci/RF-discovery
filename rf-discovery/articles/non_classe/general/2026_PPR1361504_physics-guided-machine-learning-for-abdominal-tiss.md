---
pmid: PPR1361504
doi: 10.20944/preprints202611.0752.v1
annee: 2026
journal: ''
titre: Physics-Guided Machine Learning for Abdominal Tissue Thickness Estimation Using
  RF Scattering Parameters
url: https://doi.org/10.20944/preprints202611.0752.v1
source: europepmc
acces_ouvert: ''
collecte: '2026-11-18'
mesh: []
types:
- Preprint
mots_cles: []
auteurs:
- Satriya AB
- Tan MJT
- Yoon Y
- Kim G
pmcid: ''
pdf_local: ''
volume: ''
pages: ''
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: general
theme_score: 0.0
theme_secondaires: []
theme_indices: []
bande: rf
bande_score: 3.0
bande_secondaires: []
bande_indices:
- radio frequency
- MHz
- GHz
tags:
- rf
- modele/non_classe
- theme/general
- bande/rf
- annee/2026
---

# Physics-Guided Machine Learning for Abdominal Tissue Thickness Estimation Using RF Scattering Parameters

*journal non renseigné — 2026*

## Résumé (texte d'origine)

Radio-frequency (RF) reflection measurements provide a non-ionizing approach for estimating biological tissue thickness; however, accurately resolving deeper tissues is difficult because their reflections are attenuated and superimposed with those from overlying layers. This study presents a physics-guided stacked-regression framework for estimating subcutaneous adipose tissue (SAT), muscle tissue (MT), and visceral adipose tissue (VAT) thicknesses from simulated scattering parameters. A planar multilayer abdominal model containing 120 combinations of SAT, MT, and VAT thicknesses was evaluated. The input features consisted of the magnitude of S11 at ten frequencies from 300 MHz to 2 GHz, including four intermediate frequencies at 600, 700, 800, and 900 MHz that were absent from the previous model. Target-specific frequency subsets were selected and evaluated using polynomial regression and five-fold cross-validation. Multilayer reflection theory was used to explain the nonlinear relationship between tissue thickness and the measured RF response. The extended-frequency models achieved errors of 1.96%, 7.60%, and 19.86% for SAT, MT, and VAT, respectively, compared with 2.56%, 11.42%, and 39.10% in the previous model. A selective stacked architecture was subsequently evaluated by using an estimated overlying tissue thickness as an additional input for a deeper-tissue estimator. Adding predicted SAT thickness degraded MT estimation, whereas adding predicted MT thickness improved VAT estimation. The final stacked VAT model achieved an RMSE of 0.14±0.11 mm, an R2 of 0.97±0.02, and an error of 12.49%, corresponding to a 68.06% error reduction relative to the previous VAT model. These findings demonstrate that denser frequency sampling and selectively applied anatomical guidance can improve RF-based estimation of deeper tissue layers.

[Référence d'origine](https://doi.org/10.20944/preprints202611.0752.v1)
