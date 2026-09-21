---
pmid: '41988296'
doi: 10.21037/jtd-2025-1-2741
annee: 2026
journal: ''
titre: 'A multimodal radiomics model to predict disease-free survival in resected
  non-small cell lung cancer: integrating clinicopathology, dual-energy CT, and deep
  learning features.'
url: https://pubmed.ncbi.nlm.nih.gov/41988296/
source: europepmc
acces_ouvert: open
collecte: '2026-09-21'
mesh: []
types:
- research-article
- Journal Article
mots_cles:
- Non-small cell lung cancer (NSCLC)
- Disease-free Survival (Dfs)
- Radiomics
- Dual-energy Computed Tomography (Dect)
- Deep Learning (Dl)
auteurs:
- Zhao W
- Li T
- Zhou X
- Fan W
- Wang Y
- Zhou H
- Li S
- Wang J
- Gu Y
- Xie Z
- Su F
pmcid: PMC13077411
pdf_local: ''
volume: ''
pages: '227'
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: neuro_comportement_cognition
theme_score: 2.5
theme_secondaires: []
theme_indices:
- learning
tags:
- rf
- modele/non_classe
- theme/neuro_comportement_cognition
- annee/2026
---

# A multimodal radiomics model to predict disease-free survival in resected non-small cell lung cancer: integrating clinicopathology, dual-energy CT, and deep learning features.

*journal non renseigné — 2026*

## Résumé (texte d'origine)

<h4>Background</h4>Predicting disease-free survival (DFS) after surgery for non-small cell lung cancer (NSCLC) is crucial for personalized treatment decisions. However, traditional clinical models have limited predictive efficacy. Moreover, the combined value of dual-energy computed tomography (DECT) quantitative parameters, radiomic features, and deep learning (DL) in assessing NSCLC prognosis remains unclear. This study aimed to develop and validate a multimodal machine learning model using feature-level fusion to improve the accuracy of predicting postoperative disease recurrence in NSCLC.<h4>Methods</h4>We retrospectively included 171 NSCLC patients who underwent surgical resection and were pathologically confirmed between January 2019 and October 2023. All patients underwent dual-phase DECT scanning preoperatively. We extracted four types of features from multimodal (I) DECT quantitative parameters; (II) clinicopathological features; (III) radiomic features based on PyRadiomics; and (IV) deep features extracted from a pre-trained three-dimensional (3D) DenseNet121 model. We applied a four-step cascading feature selection pipeline to identify the most predictive feature subset. Subsequently, single-modal predictive models were built using seven machine learning algorithms-logistic regression (LR), K-nearest neighbors (KNN), support vector machine (SVM), random forest (RF), extreme random trees (ExtraTrees), naive Bayes, and extreme gradient boosting (XGBoost)-with hyperparameters optimized via five-fold cross-validation. The fusion model employed a feature-level pre-fusion strategy, synchronously training with the same seven algorithms to maintain comparability. The optimal model for each modality was selected based on the area under the receiver operating characteristic (ROC) curve (AUC). Finally, a comprehensive performance comparison was conducted between the selected optimal fusion model and each single-modal champion model and model interpretation.<h4>Results</h4>The Fusion-ExtraTrees model constructed based on 12 optimal features showed great performance on the validation set, with an AUC of 0.889, significantly outperforming the single-modal champion models Clinic-LR, Rad-LR, and DECT-RF (all DeLong test P<0.05). It demonstrated performance similar to DL-3D-DenseNet121 but with better generalization and a lower risk of overfitting. Decision curve analysis (DCA) further confirmed that the fusion model had good clinical net benefit. SHapley Additive exPlanations (SHAP) analysis clearly revealed the contributions of key features from different modalities to the model's predictions, enhancing the model's interpretability.<h4>Conclusions</h4>This study successfully constructed and validated a multimodal machine learning model integrating DECT quantitative parameters, clinical features, radiomics, and DL-3D features. The model demonstrated excellent discriminative ability in predicting DFS after NSCLC surgery and significantly outperformed traditional single-modal models. It offers a reliable decision support tool for personalized post-surgery management of NSCLC patients.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41988296/)
