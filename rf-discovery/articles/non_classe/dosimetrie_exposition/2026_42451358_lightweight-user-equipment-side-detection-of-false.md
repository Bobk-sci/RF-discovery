---
pmid: '42451358'
doi: 10.3390/s26134116
annee: 2026
journal: ''
titre: Lightweight User Equipment-Side Detection of False Base Station Attacks Using
  a First-Order Markov Chain.
url: https://pubmed.ncbi.nlm.nih.gov/42451358/
source: europepmc
acces_ouvert: open
collecte: '2026-09-21'
mesh: []
types:
- research-article
- Journal Article
mots_cles:
- Markov Chain
- Anomaly Detection
- Lte
- 5G
- Cellular Network Security
- User Equipment
- False Base Station
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: dosimetrie_exposition
theme_score: 2.5
theme_secondaires: []
theme_indices:
- base station
---

# Lightweight User Equipment-Side Detection of False Base Station Attacks Using a First-Order Markov Chain.

*journal non renseigné — 2026*

## Résumé (texte d'origine)

False base station (FBS) attacks exploit the attach window before the network authenticates to the device. Existing User Equipment (UE)-side detectors typically need either labeled attack data, which is scarce and does not generalize to unseen attacks, or models too heavy for the resource budget of a smartphone or embedded endpoint. This study presents a lightweight UE-side detector built on a first-order Markov chain over a four-tuple state of packet type, direction, message identifier, and access-network type. A single counting pass fits the 119 KB chain, and thresholds are derived from normal traffic, so no attack labels are consulted. The capture path requires root and Qualcomm modem diagnostic access. Attacks surface as low-probability transitions, rare field values, and anomalous pacing, fused into a per session verdict with per-message attribution. On 192 commercial, testbed, and public LTE and 5G captures, the detector flags 51 of 53 attacks at an F1 of 88.70% in leakage-free leave-one-session-out evaluation and 96.23% once calibration covers the scored sessions. In five-fold cross-validation its F1 of 86.21% trails the strongest supervised baselines by margins that are not statistically significant, and it records the lowest latency (0.46 ms) and smallest working set (8.8 MB) among the eleven detectors benchmarked.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/42451358/)
