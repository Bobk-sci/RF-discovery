---
pmid: '41327160'
doi: 10.1186/s12885-025-15107-7
annee: 2025
journal: BMC cancer
titre: Enhancing prediction accuracy for muscle invasion in bladder cancer using a
  dual-energy CT-based interpretable model incorporating habitat radiomics and deep
  learning.
url: https://pubmed.ncbi.nlm.nih.gov/41327160/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Humans
- Urinary Bladder Neoplasms
- Male
- Tomography, X-Ray Computed
- Female
- Deep Learning
- Retrospective Studies
- Middle Aged
- Aged
- Neoplasm Invasiveness
- ROC Curve
- Aged, 80 and over
- Radiomics
types:
- Journal Article
mots_cles:
- Bladder cancer
- Computed tomography
- Deep learning
- Habitat radiomics
- SHAP
auteurs:
- Du C
- Wei W
- Hu M
- He J
- Shen J
- Liu Y
- Li J
- Liu L
pmcid: PMC12667133
pdf_local: ''
volume: '25'
pages: '1842'
modele: epidemiologie
modele_score: 1.0
modele_secondaires: []
modele_indices:
- cohort
theme: neuro_comportement_cognition
theme_score: 2.5
theme_secondaires: []
theme_indices:
- learning
tags:
- rf
- modele/epidemiologie
- theme/neuro_comportement_cognition
- annee/2025
---

# Enhancing prediction accuracy for muscle invasion in bladder cancer using a dual-energy CT-based interpretable model incorporating habitat radiomics and deep learning.

*BMC cancer — 2025*

## Résumé (texte d'origine)

BACKGROUND: Accurately predicting muscle invasion status in bladder cancer (BCa) is essential for developing personalized treatment plans. This study integrates habitat analysis and 2.5-dimension (2.5D) deep learning (DL) to create an interpretable model using dual-energy computed tomography (DECT) images to enhance the preoperative assessment of muscle invasion status in BCa.

METHODS: This study retrospectively recruited 200 BCa patients who underwent DECT urography and divided them into a training cohort (n = 140) and a test cohort (n = 60). Quantitative parameters from DECT images were measured, and independent predictors of muscle invasion were identified through stepwise regression analysis to develop a DECT model. Radiomics and 2.5D DL models were constructed using iodine-based material decomposition (IMD) images. Tumors were classified into distinct sub-regions using K-means clustering. Through feature extraction and selection, a traditional radiomics model, a habitat model, four 2.5D DL models, and the integrated model combining above models were developed. The predictive performance of the models was assessed using receiver operating characteristic (ROC) curve analysis and calibration curve analysis. The SHAP method was utilized to interpret the optimal model and visualize its decision-making process.

RESULTS: The effective atomic number (Zeff) was recognized as an independent predictor of muscle invasion in BCa. The integrated model, combining Zeff, habitat features, and ResNet 101-based DL features (DECT-DLH), represented the optimal model for predicting muscle invasion in BCa. The area under the curve (AUC) using the optima model was 0.981 (95% CI: 0.963-0.998) in the training cohort and 0.874 (95% CI: 0.785-0.964) in the test cohort. Calibration curves validated the model's reliability for clinical applications. Additionally, SHAP elucidated the decision-making processes associated with the model's predicted outcomes.

CONCLUSION: The integrated model, combining DECT quantitative parameters, habitat features, and 2.5D DL features, enhances the accuracy of preoperative predictions for muscle invasion status in BCa. The SHAP methodology improves the interpretability of decision-making within the model and provides valuable support for clinicians in developing personalized treatment strategies.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41327160/)
