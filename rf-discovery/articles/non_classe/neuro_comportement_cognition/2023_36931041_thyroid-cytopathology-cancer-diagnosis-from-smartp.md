---
pmid: '36931041'
doi: 10.1016/j.modpat.2023.100129
annee: 2023
journal: 'Modern pathology : an official journal of the United States and Canadian
  Academy of Pathology, Inc'
titre: Thyroid Cytopathology Cancer Diagnosis from Smartphone Images Using Machine
  Learning.
url: https://pubmed.ncbi.nlm.nih.gov/36931041/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Humans
- Smartphone
- Thyroid Neoplasms
- Machine Learning
- Cytodiagnosis
types:
- Journal Article
- Research Support, N.I.H., Extramural
mots_cles:
- artificial intelligence
- cytopathology
- fine needle aspiration
- machine learning
- mobile imaging
- thyroid
auteurs:
- Assaad S
- Dov D
- Davis R
- Kovalsky S
- Lee WT
- Kahmke R
- Rocke D
- Cohen J
- Henao R
- Carin L
- Range DE
pmcid: PMC10293075
volume: '36'
pages: '100129'
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: neuro_comportement_cognition
theme_score: 2.5
theme_secondaires: []
theme_indices:
- learning
---

# Thyroid Cytopathology Cancer Diagnosis from Smartphone Images Using Machine Learning.

*Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc — 2023*

## Résumé (texte d'origine)

We examined the performance of deep learning models on the classification of thyroid fine-needle aspiration biopsies using microscope images captured in 2 ways: with a high-resolution scanner and with a mobile phone camera. Our training set consisted of images from 964 whole-slide images captured with a high-resolution scanner. Our test set consisted of 100 slides; 20 manually selected regions of interest (ROIs) from each slide were captured in 2 ways as mentioned above. Applying a baseline machine learning algorithm trained on scanner ROIs resulted in performance deterioration when applied to the smartphone ROIs (97.8% area under the receiver operating characteristic curve [AUC], CI = [95.4%, 100.0%] for scanner images vs 89.5% AUC, CI = [82.3%, 96.6%] for mobile images, P = .019). Preliminary analysis via histogram matching showed that the baseline model was overly sensitive to slight color variations in the images (specifically, to color differences between mobile and scanner images). Adding color augmentation during training reduces this sensitivity and narrows the performance gap between mobile and scanner images (97.6% AUC, CI = [95.0%, 100.0%] for scanner images vs 96.0% AUC, CI = [91.8%, 100.0%] for mobile images, P = .309), with both modalities on par with human pathologist performance (95.6% AUC, CI = [91.6%, 99.5%]) for malignancy prediction (P = .398 for pathologist vs scanner and P = .875 for pathologist vs mobile). For indeterminate cases (pathologist-assigned Bethesda category of 3, 4, or 5), color augmentations confer some improvement (88.3% AUC, CI = [73.7%, 100.0%] for the baseline model vs 96.2% AUC, CI = [90.9%, 100.0%] with color augmentations, P = .158). In addition, we found that our model's performance levels off after 15 ROIs, a promising indication that ROI data collection would not be time-consuming for our diagnostic system. Finally, we showed that the model has sensible Bethesda category (TBS) predictions (increasing risk malignancy rate with predicted TBS category, with 0% malignancy for predicted TBS 2 and 100% malignancy for TBS 6).

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/36931041/)
