---
pmid: '42455849'
doi: 10.1371/journal.pone.0353163
annee: 2026
journal: ''
titre: 'Machine learning-enhanced 3GPP channel modeling for 5G networks: A vendor-calibrated
  framework with cross-scenario validation.'
url: https://pubmed.ncbi.nlm.nih.gov/42455849/
source: europepmc
acces_ouvert: open
collecte: '2026-09-21'
mesh:
- Calibration
- Algorithms
- Machine Learning
- Cell Phone
- Neural Networks, Computer
types:
- research-article
- Journal Article
mots_cles: []
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: neuro_comportement_cognition
theme_score: 2.0
theme_secondaires: []
theme_indices:
- learning
---

# Machine learning-enhanced 3GPP channel modeling for 5G networks: A vendor-calibrated framework with cross-scenario validation.

*journal non renseigné — 2026*

## Résumé (texte d'origine)

Accurate channel characterization across diverse propagation environments is foundational to 5G network planning, yet existing machine learning approaches rarely integrate standardized 3GPP frameworks with vendor-specific equipment parameters. This study presents a regression-based framework combining 3GPP TR 38.901 channel models with five supervised learning algorithms-linear regression, polynomial regression (degree 2), support vector regression (SVR), decision tree, and artificial neural network (ANN)-trained on 10,000 deterministic samples spanning Urban Macro (UMa), Urban Micro (UMi), Rural Macro (RMa), and Indoor Hotspot (InH) scenarios at five carrier frequencies (0.7-60 GHz). Vendor-calibrated parameterization using authenticated Nokia AirScale 64T64R, Huawei AAU5940, and ZTE AAU 5G specifications grounds the simulated link budgets in commercial equipment characteristics, providing deployment-aligned (though formula-derived rather than field-measured) performance estimates (see Limitations). All five regression architectures are evaluated identically across all five carrier frequencies and all scenario types, enabling direct comparison under controlled conditions. For throughput prediction, the ANN and decision tree achieve the highest accuracy (R2 = 0.998, RMSE ≤ 24 Mbps averaged across five independent random splits; 95% CI: R2∈[0.997,0.999], RMSE ∈[19.1,22.4] Mbps), while linear and polynomial regressors show substantial error (R2≤0.56), reflecting the strongly nonlinear throughput surface. For path loss estimation under Urban Micro NLOS conditions, all models attain near-perfect fit (R2≈1.0, MSE < 0.02 dB2), confirming that simple regressors suffice for log-distance targets. Vendor link budgets quantify the Nokia-Huawei throughput gap (1.88× at 100 m) and the ZTE 28 GHz peak capacity (1688.6 Mbps at 100 m), establishing a breakeven inter-site distance of approximately 150 m below which FR2 outperforms FR1. Cross-scenario generalization experiments reveal a critical failure mode: models trained on LOS-urban data yield strongly negative R2 on Rural Macro scenarios (<-3), while mixed-scenario training recovers generalization to R2 > 0.75 across all environments. Permutation-based feature importance identifies distance as the dominant predictor (importance 0.65-0.85), with frequency importance rising to ≈0.40 at millimeter-wave bands. Sensitivity analysis confirms robustness (R2 > 0.90) under realistic parameter perturbations (±10% distance, ±5% frequency, ±2 dB EIRP). These results provide evidence-based guidelines for model selection, training data composition, and deployment in 5G/6G network planning.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/42455849/)
