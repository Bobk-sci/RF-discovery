---
pmid: '42934140'
doi: 10.7507/1001-5515.202509051
annee: 2026
journal: ''
titre: '[A deep learning-based method for rapid reconstruction and prediction of electromagnetic
  exposure in pacemaker patients].'
url: https://pubmed.ncbi.nlm.nih.gov/42934140/
source: europepmc
acces_ouvert: ''
collecte: '2026-11-02'
mesh:
- Humans
- Pacemaker, Artificial
- Finite Element Analysis
- Electromagnetic Fields
- Microwaves
- Deep Learning
types:
- research-article
- Journal Article
- English Abstract
mots_cles:
- Induced electric field
- Cardiac Pacemaker
- Specific Absorption Rate
- Electromagnetic Exposure
- U-net Neural Network
auteurs:
- Wei J
- Tian R
- Zhang R
- Lu M
pmcid: PMC13713248
pdf_local: ''
volume: ''
pages: 1035-1043
modele: dosimetrie_modelisation
modele_score: 4.0
modele_secondaires: []
modele_indices:
- SAR
- specific absorption rate
- numerical simulation
theme: neuro_comportement_cognition
theme_score: 2.0
theme_secondaires:
- dosimetrie_exposition
theme_indices:
- learning
tags:
- rf
- modele/dosimetrie_modelisation
- theme/neuro_comportement_cognition
- theme/dosimetrie_exposition
- annee/2026
---

# [A deep learning-based method for rapid reconstruction and prediction of electromagnetic exposure in pacemaker patients].

*journal non renseigné — 2026*

## Résumé (texte d'origine)

Microwave ovens and other electromagnetic devices may leak electromagnetic fields, which can interfere with implanted cardiac pacemakers in patients. The traditional finite element method (FEM) is time-consuming and difficult to meet the needs of rapid risk assessment. This paper proposes a fast reconstruction and prediction method for electromagnetic exposure based on 3D U-Net to predict the electromagnetic exposure in patients with implanted cardiac pacemakers caused by microwave oven leakage under random scenarios. First, the FEM was used to simulate the thoracic electric field, specific absorption rate (SAR), and induced electric field in the pacemaker under different electromagnetic exposure conditions, and a sample set was constructed after preprocessing. Second, the 3D U-Net model was trained with spatial coordinates, microwave oven power, distance between the human body and the microwave oven, and oven door gap as inputs, and the thoracic electric field, SAR, and induced electric field in the pacemaker as labels. The results showed that the predicted thoracic electric field, SAR, and induced electric field in the pacemaker were in good agreement with the FEM simulation results. On the validation set, the relative error rates of the thoracic electric field, SAR, and induced electric field in the pacemaker were 0.78%, 0.72%, and 0.94%, respectively. The prediction time for a single case was only 0.93 s. This method can serve as an effective supplement to traditional numerical simulation and provides a new approach for rapid assessment of electromagnetic exposure in patients with implanted cardiac pacemakers.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/42934140/)
