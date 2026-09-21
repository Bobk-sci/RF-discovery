---
pmid: '41615330'
doi: 10.1002/smll.202510453
annee: 2026
journal: Small (Weinheim an der Bergstrasse, Germany)
titre: Machine Learning on Systematically Curated Data Reveals Key Determinants of
  Magnetic Hyperthermia Performance.
url: https://pubmed.ncbi.nlm.nih.gov/41615330/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Machine Learning
- Hyperthermia, Induced
- Boosting Machine Learning Algorithms
- Bayes Theorem
- Magnetic Iron Oxide Nanoparticles
- Predictive Learning Models
- Algorithms
- Reproducibility of Results
types:
- Journal Article
mots_cles:
- Bayesian optimization
- CatBoost
- SHAP analysis
- conformal prediction
- feature importance
- machine learning
- magnetic hyperthermia
- specific absorption rate
- superparamagnetic iron oxide nanoparticles
auteurs:
- Vega-Carrasco ER
- Ansari SR
- Zhao J
- Del Carmen Suárez-López Y
- Larsson P
- Teleki A
pmcid: PMC13003278
pdf_local: ''
volume: '22'
pages: e10453
modele: dosimetrie_modelisation
modele_score: 3.0
modele_secondaires: []
modele_indices:
- SAR
- specific absorption rate
theme: neuro_comportement_cognition
theme_score: 2.5
theme_secondaires:
- thermique
- dosimetrie_exposition
theme_indices:
- learning
tags:
- rf
- modele/dosimetrie_modelisation
- theme/neuro_comportement_cognition
- theme/thermique
- theme/dosimetrie_exposition
- annee/2026
---

# Machine Learning on Systematically Curated Data Reveals Key Determinants of Magnetic Hyperthermia Performance.

*Small (Weinheim an der Bergstrasse, Germany) — 2026*

## Résumé (texte d'origine)

Accurate prediction of the specific absorption rate (SAR) of superparamagnetic iron oxide nanoparticles (SPIONs) is critical for optimizing their performance in magnetic hyperthermia applications. This study presents the development of a predictive model for SAR using advanced machine learning techniques and a systematically curated dataset comprising 1850 entries from 84 published studies, capturing 30 predictive features related to SPION properties and experimental parameters. Twelve machine learning algorithms were evaluated and optimized using Bayesian hyperparameter tuning. The CatBoost algorithm emerged as the top-performing model (R2 = 0.98) with the lowest prediction errors. Shapley additive explanation analysis revealed alternating magnetic field amplitude and frequency as the most influential factors determining SAR, followed by SPION concentration and core surface area. Model reliability was confirmed through conformal prediction, providing a prediction interval of ±62 W g-1. Validation using an independent dataset of SPIONs with varying sizes (7-30 nm) and dopants (Zn, Mn, Mg, Co) demonstrated strong predictive performance for small nanoparticles (≈7 nm), with increased variability for larger particles. These findings demonstrate that advanced machine learning models enable accurate SAR prediction and provide critical insights into nanoparticle design, supporting the systematic optimization of SPIONs for clinical magnetic hyperthermia applications.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41615330/)
