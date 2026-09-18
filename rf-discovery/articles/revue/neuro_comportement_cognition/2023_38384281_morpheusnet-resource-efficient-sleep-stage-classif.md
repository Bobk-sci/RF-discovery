---
pmid: '38384281'
doi: 10.1109/SMC53992.2023.10394274
annee: 2023
journal: Conference proceedings. IEEE International Conference on Systems, Man, and
  Cybernetics
titre: 'MorpheusNet: Resource efficient sleep stage classifier for embedded on-line
  systems.'
url: https://pubmed.ncbi.nlm.nih.gov/38384281/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-18'
mesh: []
types:
- Journal Article
mots_cles:
- SSC
- deep learning
- resource efficient
modele: revue
modele_score: 1.0
modele_secondaires: []
modele_indices:
- state of the art
theme: neuro_comportement_cognition
theme_score: 4.0
theme_secondaires:
- eeg_sommeil
theme_indices:
- memory
- learning
- attention
---

# MorpheusNet: Resource efficient sleep stage classifier for embedded on-line systems.

*Conference proceedings. IEEE International Conference on Systems, Man, and Cybernetics — 2023*

## Résumé (texte d'origine)

Sleep Stage Classification (SSC) is a labor-intensive task, requiring experts to examine hours of electrophysiological recordings for manual classification. This is a limiting factor when it comes to leveraging sleep stages for therapeutic purposes. With increasing affordability and expansion of wearable devices, automating SSC may enable deployment of sleep-based therapies at scale. Deep Learning has gained increasing attention as a potential method to automate this process. Previous research has shown accuracy comparable to manual expert scores. However, previous approaches require sizable amount of memory and computational resources. This constrains the ability to classify in real time and deploy models on the edge. To address this gap, we aim to provide a model capable of predicting sleep stages in real-time, without requiring access to external computational sources (e.g., mobile phone, cloud). The algorithm is power efficient to enable use on embedded battery powered systems. Our compact sleep stage classifier can be deployed on most off-the-shelf microcontrollers (MCU) with constrained hardware settings. This is due to the memory footprint of our approach requiring significantly fewer operations. The model was tested on three publicly available data bases and achieved performance comparable to the state of the art, whilst reducing model complexity by orders of magnitude (up to 280 times smaller compared to state of the art). We further optimized the model with quantization of parameters to 8 bits with only an average drop of 0.95% in accuracy. When implemented in firmware, the quantized model achieves a latency of 1.6 seconds on an Arm Cortex-M4 processor, allowing its use for on-line SSC-based therapies.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/38384281/)
