---
pmid: '42620040'
doi: ''
annee: 2026
journal: ArXiv
titre: MWF-MIMOSA for efficient simultaneous relaxometry and myelin water fraction
  mapping.
url: https://pubmed.ncbi.nlm.nih.gov/42620040/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh: []
types:
- Journal Article
- Preprint
mots_cles: []
auteurs:
- Chen Y
- Jun Y
- Shin HG
- Li S
- Fujita S
- Yong X
- Kim J
- Lee J
- Piredda GF
- Hilbert T
- Bhatt A
- Huang SY
- Liu H
- Ye H
- Nasr S
- Gagoski B
- Chan KS
- Bilgic B
pmcid: PMC13484418
pdf_local: ''
volume: ''
pages: ''
modele: dosimetrie_modelisation
modele_score: 2.0
modele_secondaires:
- in_vivo
modele_indices:
- SAR
- specific absorption rate
theme: neuro_comportement_cognition
theme_score: 1.0
theme_secondaires:
- dosimetrie_exposition
theme_indices:
- learning
tags:
- rf
- modele/dosimetrie_modelisation
- modele/in_vivo
- theme/neuro_comportement_cognition
- theme/dosimetrie_exposition
- annee/2026
---

# MWF-MIMOSA for efficient simultaneous relaxometry and myelin water fraction mapping.

*ArXiv — 2026*

## Résumé (texte d'origine)

Quantitative magnetic resonance imaging (qMRI) provides improved sensitivity and specificity to tissue composition and pathological alterations compared with conventional contrast-weighted imaging. Among various qMRI biomarkers, myelin water imaging is of particular interest because myelin plays a central role in brain function and its alteration is closely associated with many neurological diseases. However, conventional myelin water fraction (MWF) mapping techniques are often limited by long scan times, low spatial resolution, reduced signal-to-noise ratio (SNR), and high specific absorption rate (SAR). Here, we propose MWF-MIMOSA for efficient simultaneous T1, T2, T2* mapping, magnetic susceptibility source separation, and MWF estimation. To achieve this, multi-contrast and multi-slice zero-shot self-supervised learning (MZS-SSL) was used to jointly reconstruct whole-brain complex-valued images. To improve computational efficiency of the parameter estimation step, a multilayer perceptron (MLP) was trained within the GACELLE GPU-accelerated parameter estimation framework to circumvent the computationally intensive Bloch simulation process, resulting in a >100-fold computational speed-up in MWF estimation. Numerical simulations were performed to evaluate the accuracy and precision of MWF-MIMOSA, and in-vivo results further demonstrated its robustness. Comparison with existing myelin water imaging methods showed that MWF-MIMOSA is highly correlated with established approaches, while providing complementary quantitative parameter maps at higher spatial resolution and with shorter scan times. Notably, simultaneous multi-parametric mapping was achieved in 5 min at 1 mm isotropic resolution, and in 10 min at 0.7 mm isotropic resolution. These results demonstrate the potential of MWF-MIMOSA for fast, high-resolution simultaneous relaxometry and myelin water imaging.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/42620040/)
