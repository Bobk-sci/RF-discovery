---
pmid: '41448143'
doi: 10.1002/mp.70252
annee: 2026
journal: Medical physics
titre: Comparison of methodological uncertainties in tissue parameter estimation for
  carbon ion dose calculation.
url: https://pubmed.ncbi.nlm.nih.gov/41448143/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Uncertainty
- Radiotherapy Planning, Computer-Assisted
- Heavy Ion Radiotherapy
- Monte Carlo Method
- Radiation Dosage
- Radiotherapy Dosage
- Phantoms, Imaging
- Humans
- Tomography, X-Ray Computed
types:
- Journal Article
- Comparative Study
mots_cles:
- carbon ion therapy
- dose uncertainty
- dual‐energy CT
- machine learning
- monte carlo simulation
auteurs:
- Yu S
- Li Y
- Li W
- Yang C
- Chang C
- Chen Y
- Xu C
- Wang M
- Li KW
- Geng LS
- Zhang Y
pmcid: ''
pdf_local: ''
volume: '53'
pages: e70252
modele: dosimetrie_modelisation
modele_score: 1.0
modele_secondaires: []
modele_indices:
- phantom
theme: neuro_comportement_cognition
theme_score: 2.0
theme_secondaires: []
theme_indices:
- learning
tags:
- rf
- modele/dosimetrie_modelisation
- theme/neuro_comportement_cognition
- annee/2026
---

# Comparison of methodological uncertainties in tissue parameter estimation for carbon ion dose calculation.

*Medical physics — 2026*

## Résumé (texte d'origine)

BACKGROUND: Accurate dose calculation is essential for securing the therapeutic benefit and safety of carbon ion radiotherapy. However, the uncertainty associated with tissue parameter estimation methods for Monte Carlo-based dose calculation has not been systematically evaluated, potentially limiting the reliability of quality assurance in clinical practice.

PURPOSE: To support more accurate treatment planning and quality assurance for carbon ion radiotherapy, this study aims to systematically assess how upstream uncertainties in tissue parameter estimation affect Monte Carlo-based carbon ion dose calculations. By comparing three elemental decomposition approaches, their impact on the consistency and reliability of dose distributions were quantitatively evaluated.

METHODS: Relevant sources of uncertainties in physical density and elemental composition were analyzed and propagated based on three methods: single-energy CT (SECT), parameterized dual-energy CT (PA-DECT), and machine learning-based DECT (ML-DECT). For validation, the ICRP 110 phantom was perturbed accordingly, and dose distributions were simulated using FLUKA with 10 samples for each method. Both physical and biological doses were evaluated. The voxel-wise uncertainty, gamma passing rate and range uncertainty were examined.

RESULTS: The ML-DECT method consistently yielded the lowest uncertainties across all tissue parameters, reducing the uncertainties for C, N, and O density by up to 77.4% compared to SECT. In dose simulations, ML-DECT achieved lower average relative uncertainties (∼5% physical, ∼7%-9% biological), a higher gamma passing rate (97.96  ±  0.28%), and reduced range uncertainty (0.5%) compared to other methods.

CONCLUSIONS: By more accurately modeling the relationship between CT numbers and tissue parameters, ML-DECT substantially reduces uncertainty in both input estimation and subsequent dose calculation. These findings support its integration into Monte Carlo-based carbon ion treatment planning workflows, contributing to more quantitative and uncertainty-aware quality assurance.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41448143/)
