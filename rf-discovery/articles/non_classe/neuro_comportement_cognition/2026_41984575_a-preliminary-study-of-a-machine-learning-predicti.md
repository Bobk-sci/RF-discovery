---
pmid: '41984575'
doi: 10.1097/RCT.0000000000001867
annee: 2026
journal: Journal of computer assisted tomography
titre: A Preliminary Study of a Machine Learning Prediction of Poorly Differentiated
  Hepatocellular Carcinoma Based on a Comprehensive Parameter Analysis Using Dual-Energy
  Computed Tomography.
url: https://pubmed.ncbi.nlm.nih.gov/41984575/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Humans
- Carcinoma, Hepatocellular
- Liver Neoplasms
- Tomography, X-Ray Computed
- Female
- Retrospective Studies
- Machine Learning
- Male
- Middle Aged
- Predictive Learning Models
- Aged
- Contrast Media
- Radiography, Dual-Energy Scanned Projection
- Sensitivity and Specificity
- Liver
- Radiographic Image Interpretation, Computer-Assisted
types:
- Journal Article
mots_cles:
- computed tomography
- dual-energy computed tomography
- hepatocellular carcinoma
- machine learning
- poorly differentiated hepatocellular carcinoma
auteurs:
- Takamatsu A
- Yoneda N
- Toshima F
- Kitagawa T
- Komori T
- Inoue D
- Kitao A
- Kozaka K
- Matsui O
- Kobayashi S
pmcid: ''
pdf_local: ''
volume: '50'
pages: ''
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: neuro_comportement_cognition
theme_score: 2.5
theme_secondaires:
- cancer
theme_indices:
- learning
tags:
- rf
- modele/non_classe
- theme/neuro_comportement_cognition
- theme/cancer
- annee/2026
---

# A Preliminary Study of a Machine Learning Prediction of Poorly Differentiated Hepatocellular Carcinoma Based on a Comprehensive Parameter Analysis Using Dual-Energy Computed Tomography.

*Journal of computer assisted tomography — 2026*

## Résumé (texte d'origine)

OBJECTIVE: To develop and evaluate the performance of a predictive machine learning model for poorly differentiated hepatocellular carcinoma (p-HCC) using comprehensive quantitative parameters from dual-energy computed tomography (DECT).

MATERIALS AND METHODS: We retrospectively analyzed 181 surgically resected, pathologically proven HCCs in 170 patients who had undergone preoperative DECT between April 2019 and November 2025. After propensity-score matching on age, sex, alpha-fetoprotein (AFP), tumor size on CT, and LI-RADS categories, the dataset was divided into a training set including 51 HCCs (17 p-HCCs and 34 non-p-HCCs) from 2019 to 2022 and a testing set including 33 HCCs (11 p-HCCs, 22 non-p-HCCs) from 2023 to 2025. Overall, 3516 DECT parameters were extracted from precontrast images and three contrast-enhanced images [arterial phase (AP), portal venous phase (PVP), and delayed phase (DP)] for each case. These parameters included virtual monochromatic imaging (VMI) CT values, effective atomic numbers (Effective-Z), material density, spectral curve slopes (Slope), and interphase differences (Diff). Clinical data, including etiology of liver disease, serum AFP level, and lesion size, were collected. A machine learning model based on an extra trees classifier was trained, and a Shapley additive explanations (SHAP) analysis was performed for each selected parameter following data preprocessing. Model performance was evaluated using accuracy, sensitivity, specificity, positive predictive value (PPV), negative predictive value (NPV), and the area under the receiver operating characteristic curve (AUC).

RESULTS: SHAP analysis revealed that the most highly influential features were delayed phase-related, with the average 40-keV VMI CT value in the delayed phase contributing most strongly. In addition, several Effective-Z-related features and selected material density parameters also showed substantial importance. In the testing set, the model demonstrated an accuracy, sensitivity, specificity, PPV, NPV, and AUC of 0.606, 0.818, 0.500, 0.450, 0.846, and 0.800, respectively.

CONCLUSIONS: The predictive machine learning model for p-HCC showed acceptable diagnostic performance and, although still preliminary, may contribute to a noninvasive assessment of HCC differentiation grades, guiding clinical decision-making.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41984575/)
