---
pmid: '41588287'
doi: 10.1007/s10278-026-01847-w
annee: 2026
journal: Journal of imaging informatics in medicine
titre: Generating Training Data for Ureter Segmentation Using Dual-Energy CT Two-Material
  Decomposition.
url: https://pubmed.ncbi.nlm.nih.gov/41588287/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh: []
types:
- Journal Article
mots_cles:
- Deep learning
- Dual-energy computed tomography
- Image segmentation
- Ureter
- Virtual unenhanced imaging
auteurs:
- Jung DC
- Lee J
- Lee S
- Jung SI
- Lee MS
- Moon MH
pmcid: '6284017'
pdf_local: ''
volume: ''
pages: ''
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: neuro_comportement_cognition
theme_score: 2.0
theme_secondaires: []
theme_indices:
- learning
tags:
- rf
- modele/non_classe
- theme/neuro_comportement_cognition
- annee/2026
---

# Generating Training Data for Ureter Segmentation Using Dual-Energy CT Two-Material Decomposition.

*Journal of imaging informatics in medicine — 2026*

## Résumé (texte d'origine)

This study aimed to evaluate the utility of dual-energy CT (DECT)-based two-material decomposition in facilitating the generation of training data for ureter segmentation. This retrospective two-center study included 180 patients who underwent DECT urography between April and July 2020, including 150 from Institution 1 and 30 from Institution 2. Virtual unenhanced (VUE) images were generated from the late excretory phase (LEP) images using a two-material decomposition technique. Ground truth segmentation masks were created by segmenting contrast-filled ureteral regions on LEP images and were then paired with the corresponding VUE images. These VUE images and their corresponding ground truth masks were used to construct training, validation, and test datasets. A deep learning-based segmentation model was developed using the nnU-Net framework. Its performance was evaluated using the Dice coefficient, precision, and recall. In the internal test dataset, the model achieved excellent performance, with a median Dice coefficient of 0.89 (95% CI 0.88-0.90), precision of 0.90 (95% CI 0.88-0.92), and recall of 0.88 (95% CI 0.86-0.91). In contrast, the external validation dataset yielded limited performance, with a median Dice coefficient of 0.43 (95% CI 0.31-0.61) and recall of 0.28 (95% CI 0.18-0.45), while precision remained high at 0.95 (95% CI 0.93-0.96). There were statistically significant differences in all metrics between the internal and external datasets (P < 0.01). DECT-based two-material decomposition is a feasible method for generating training data for ureter segmentation. Although external validation performance was limited, this approach shows promise for ureter segmentation on non-contrast CT scans.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41588287/)
