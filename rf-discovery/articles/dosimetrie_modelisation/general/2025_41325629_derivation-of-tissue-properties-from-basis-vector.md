---
pmid: '41325629'
doi: 10.1088/2057-1976/ae2622
annee: 2025
journal: Biomedical physics & engineering express
titre: Derivation of tissue properties from basis-vector model weights for dual-energy
  CT-based Monte Carlo proton beam dose calculations.
url: https://pubmed.ncbi.nlm.nih.gov/41325629/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Monte Carlo Method
- Phantoms, Imaging
- Tomography, X-Ray Computed
- Humans
- Radiotherapy Planning, Computer-Assisted
- Proton Therapy
- Radiotherapy Dosage
- Computer Simulation
- Algorithms
- Protons
types:
- Journal Article
mots_cles:
- Monte Carlo dose calculations
- basis-vector model
- dual-energy CT
- material decomposition
- proton therapy
- stopping power estimation
- tissue property derivation
auteurs:
- Medrano MJ
- Chen X
- Burigo LN
- O'Sullivan JA
- Williamson JF
pmcid: PMC13070838
pdf_local: ''
volume: '12'
pages: ''
modele: dosimetrie_modelisation
modele_score: 1.0
modele_secondaires: []
modele_indices:
- phantom
theme: general
theme_score: 0.0
theme_secondaires: []
theme_indices: []
tags:
- rf
- modele/dosimetrie_modelisation
- theme/general
- annee/2025
---

# Derivation of tissue properties from basis-vector model weights for dual-energy CT-based Monte Carlo proton beam dose calculations.

*Biomedical physics & engineering express — 2025*

## Résumé (texte d'origine)

Objective.We propose a novel method, basis vector model material indexing (BVM-MI), for predicting atomic composition and mass density from two independent basis vector model weights derived from dual-energy CT (DECT) for Monte Carlo (MC) dose planning.Approach. BVM-MI employs multiple linear regression on BVM weights and their quotient to predict elemental composition and mass density for 70 representative tissues. Predicted values were imported into the TOPAS MC code to simulate proton dose deposition to a uniform cylinder phantom composed of each tissue type. The performance of BVM-MI was compared to the conventional Hounsfield Unit material indexing method (HU-MI), which estimates elemental composition and density based on CT numbers (HU). Evaluation metrics included absolute errors in predicted elemental compositions and relative percent errors in calculated mass density and mean excitation energy. Dose distributions were assessed by quantifying absolute error in the depth of 80% maximum scored dose (R80) and relative percent errors in stopping power (SP) between MC simulations using HU-MI, BVM-MI, and benchmark compositions. Lateral dose profiles were analyzed at R80 and Bragg Peak (RBP) depths for three tissues showing the largest discrepancies in R80 depth.Main Results. BVM-MI outperformed HU-MI in elemental composition predictions, with mean root-mean-square error (RMSE) of 1.30% (soft tissue) and 0.1% (bony tissue), compared to 4.20% and 1.9% for HU-MI. R80 depth RMSEs were 0.2 mm (soft) and 0.1 mm (bony) for BVM-MI, versus 1.8 mm and 0.7 mm for HU-MI. Lateral dose profile analysis showed overall smaller dose errors for BVM-MI across core, halo, and proximal aura regions.Significance. Fully utilizing the two-parameter BVM space for material indexing significantly improved TOPAS MC dose calculations by factors of 7 to 9 in RMSE compared to the conventional HU-MI method demonstrating the potential of BVM-MI to enhance proton therapy planning, particularly for tissues with substantial elemental variability.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41325629/)
