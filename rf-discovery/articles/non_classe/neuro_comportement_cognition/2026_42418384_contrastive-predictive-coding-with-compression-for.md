---
pmid: '42418384'
doi: 10.1109/tnnls.2026.3709216
annee: 2026
journal: ''
titre: Contrastive Predictive Coding With Compression for Enhanced Channel State Feedback
  in Wireless Networks.
url: https://pubmed.ncbi.nlm.nih.gov/42418384/
source: europepmc
acces_ouvert: ''
collecte: '2026-09-21'
mesh: []
types:
- Journal Article
mots_cles: []
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: neuro_comportement_cognition
theme_score: 1.0
theme_secondaires:
- dosimetrie_exposition
theme_indices:
- learning
---

# Contrastive Predictive Coding With Compression for Enhanced Channel State Feedback in Wireless Networks.

*journal non renseigné — 2026*

## Résumé (texte d'origine)

Accurate and timely channel state information (CSI) is essential for next-generation wireless systems, yet existing works treat CSI compression and CSI prediction as separate problems, both in academia and in current third Generation Partnership Project (3GPP) studies. Consequently, channel aging remains insufficiently addressed within standardized CSI feedback pipelines. In this brief, we propose a unified compression-prediction framework that integrates contrastive predictive coding (CPC) directly into the 3GPP-compliant CSI compression architecture. Instead of predicting high-dimensional CSI matrices, our approach forecasts future latent representations and jointly optimizes reconstruction fidelity and temporal predictive coherence via a combined 1-SGCS and InfoNCE objective. This design enables temporal representation learning without increasing feedback overhead. We present two variants: CPC-before-compression, which performs autoregressive modeling on encoded features prior to quantization, and CPC-after-compression, which shifts temporal modeling to the base station to reduce the complexity of users' devices. Evaluations on 3GPP-compliant datasets from Nokia, Oppo, and CATT show that CPC-before-compression achieves over 90% reconstruction accuracy with $32\times $ lower decoder GFLOPs than the 3GPP baseline, while CPC-after-compression preserves an identical encoder footprint and the same 64-bit feedback overhead. By unifying compression and prediction within a standardized pipeline, the proposed framework provides an age aware, computationally efficient CSI feedback solution. The source code is publicly available at: https://github.com/AhmedRadwan02/cpc-3gpp.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/42418384/)
