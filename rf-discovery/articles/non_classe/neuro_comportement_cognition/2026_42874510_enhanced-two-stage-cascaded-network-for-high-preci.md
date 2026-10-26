---
pmid: '42874510'
doi: 10.1016/j.apradiso.2026.113012
annee: 2026
journal: ''
titre: Enhanced two-stage cascaded network for high-precision stopping power ratio
  and functional image generation from conventional CT.
url: https://pubmed.ncbi.nlm.nih.gov/42874510/
source: europepmc
acces_ouvert: ''
collecte: '2026-10-26'
mesh: []
types:
- Journal Article
mots_cles:
- Functional Imaging
- Electron Density
- Dual-energy Ct
- Stopping Power Ratio
- Cascaded Networks
auteurs:
- Zhu H
- Wang S
- Bai L
- Zhu Q
- Li W
- Yu L
- Liu X
- Zhang Y
- Liu S
- Yang B
- Qiu J
pmcid: ''
pdf_local: ''
volume: ''
pages: '113012'
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: neuro_comportement_cognition
theme_score: 1.0
theme_secondaires: []
theme_indices:
- learning
tags:
- rf
- modele/non_classe
- theme/neuro_comportement_cognition
- annee/2026
---

# Enhanced two-stage cascaded network for high-precision stopping power ratio and functional image generation from conventional CT.

*journal non renseigné — 2026*

## Résumé (texte d'origine)

<h4>Purpose</h4>Accurate stopping power ratio (SPR) estimation is essential for proton therapy dose calculation; however, SPR and related functional images-electron density (ED), effective atomic number (Zeff), and iodine concentration (IC)-currently require dual-energy CT (DECT), whose clinical adoption is limited by high cost and restricted availability. To our knowledge, no previous study has synthesized DECT-derived functional images directly from conventional single-energy CT (SECT). This study proposes, for the first time, a deep learning framework that generates SPR, ED, Zeff, and IC maps simultaneously from conventional CT, and investigates whether a physics-informed two-stage cascaded architecture can outperform conventional single-stage networks.<h4>Methods</h4>Seventy-four head-and-neck cancer patients scanned with a dual-layer DECT scanner were retrospectively analyzed. Integrated detector-layer signals provided SECT-equivalent input images, while DECT-derived maps served as references. Four networks were compared: a single-output UNet (UNet-1), a multi-output UNet (UNet-4), a two-stage cascaded UNet (Cascade-UNet), and the proposed enhanced two-stage cascaded model (Cascade-New), which incorporates an asymmetric encoder-decoder with residual vision modules and Mamba-based dense connectivity, and exploits the physical dependency chain CT → ED/Zeff → SPR through a three-term training loss. Models were evaluated on an independent test set using mean absolute error (MAE), peak signal-to-noise ratio (PSNR), structural similarity index measure (SSIM), and Pearson correlation coefficient (PCC), with pairwise Wilcoxon signed-rank tests.<h4>Results</h4>The proposed Cascade-New model achieved the best overall performance: the lowest SPR MAE (11.65 ± 1.58 in units of SPR × 10<sup>-3</sup> vs. 12.99 ± 1.46 for UNet-4, a 10.3% relative reduction), the highest SSIM (0.9971 ± 0.0016), and the strongest correlation (PCC = 0.9996 ± 0.0002). Improvements over UNet-4 in ED, Zeff, and IC synthesis were all statistically significant (all p = 0.031). Visual and error map analyses confirmed its improved performance, particularly in bone and heterogeneous tissue regions.<h4>Conclusion</h4>This study provides the first demonstration that SPR and other DECT-derived functional images can be synthesized directly from conventional SECT with high precision. The proposed physics-informed cascaded framework offers a cost-effective alternative to DECT, enabling radiotherapy centers to obtain accurate SPR maps with conventional CT for proton dose calculation, potentially reducing range uncertainty and expanding access to high-precision functional imaging.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/42874510/)
