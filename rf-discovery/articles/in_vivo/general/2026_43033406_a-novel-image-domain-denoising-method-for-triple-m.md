---
pmid: '43033406'
doi: 10.1002/mp.70723
annee: 2026
journal: ''
titre: A novel image-domain denoising method for triple-material decomposition in
  dual-energy CT.
url: https://pubmed.ncbi.nlm.nih.gov/43033406/
source: europepmc
acces_ouvert: ''
collecte: '2026-11-16'
mesh:
- Animals
- Mice
- Tomography, X-Ray Computed
- Phantoms, Imaging
- Algorithms
- Image Processing, Computer-Assisted
- Signal-To-Noise Ratio
types:
- Journal Article
mots_cles:
- Denoising
- Dual‐Energy Ct
- Triple‐material Decomposition
auteurs:
- Wu J
- Yuan X
- Yang Y
pmcid: ''
pdf_local: ''
volume: ''
pages: e70723
modele: in_vivo
modele_score: 6.0
modele_secondaires:
- dosimetrie_modelisation
modele_indices:
- animals
- mice
- mouse
- in vivo
theme: general
theme_score: 0.0
theme_secondaires: []
theme_indices: []
tags:
- rf
- modele/in_vivo
- modele/dosimetrie_modelisation
- theme/general
- annee/2026
---

# A novel image-domain denoising method for triple-material decomposition in dual-energy CT.

*journal non renseigné — 2026*

## Résumé (texte d'origine)

<h4>Background</h4>Triple-material decomposition (TMD) holds significant clinical value in dual-energy computed tomography (DECT), as it enables simultaneous differentiation of bone, soft tissue, and contrast agents-three key components commonly targeted in clinical imaging assessments. However, the inherent noise amplification artifact associated with material decomposition remains a critical technical bottleneck that restricts its widespread clinical translation.<h4>Purpose</h4>To address this limitation, this study proposes an image-domain denoising strategy to mitigate noise amplification, thereby improving the quantitative accuracy and qualitative quality of TMD in DECT.<h4>Method</h4>First, DECT images were transformed into amplitude and argument components via vectorization. Second, a spectral joint bilateral filtering algorithm was developed to specifically denoise the argument images, leveraging inter-spectral correlation to preserve structural details while suppressing noise. Subsequently, denoised DECT images were reconstructed using the original amplitude and denoised argument components. TMD was performed with soft tissue, bone, and contrast agent as basis materials, utilizing two decomposition approaches: direct matrix inversion (DMI) and the penalized weighted least squares-expectation maximization-loop (PWLS-EP-LOOP) iterative method. The proposed denoising strategy was validated on a benchtop micro-CT system, with evaluations conducted on both a customized anthropomorphic phantom and an in vivo mouse model injected with ExiTron nano 6000 contrast agent.<h4>Results</h4>For DMI-based decomposition, the proposed method achieved noise reduction rates (NRRs) of 68.9% in soft tissue images, 74.4% in contrast-enhanced images, and 78.7% in bone images. For PWLS-EP-LOOP-based iterative decomposition, the corresponding NRRs were 22.4% (soft tissue), 48.6% (contrast agent), and 37.5% (bone). Furthermore, the number of iteration cycles required for convergence in the PWLS-EP-LOOP algorithm was reduced by 75.4%, substantially improving computational efficiency.<h4>Conclusion</h4>Experimental results demonstrate that the proposed image-domain denoising method, tailored for DECT TMD, effectively suppresses noise in both DMI and iterative workflows while preserving structural fidelity. This work thus provides a promising solution to enhance the clinical utility of DECT material decomposition.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/43033406/)
