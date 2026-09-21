---
pmid: '42197786'
doi: 10.3390/s26102977
annee: 2026
journal: Sensors (Basel, Switzerland)
titre: 'Virtual Mice, Real Errors: A Sensor-Aware Generative Framework for In Silico
  Ethology.'
url: https://pubmed.ncbi.nlm.nih.gov/42197786/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Animals
- Mice
- Ethology
- Computer Simulation
- Algorithms
- Behavior, Animal
types:
- Journal Article
mots_cles:
- computational ethology
- digital twin
- domain shift
- generative modeling
- line-of-sight (LoS)
- non-line-of-sight (NLoS)
- semi-Markov model
- sensor-aware modeling
- trajectory generation
- ultra-wideband (UWB)
auteurs:
- Sayfoori R
- Vaisi G
- Cao H
pmcid: PMC13210631
pdf_local: ''
volume: '26'
pages: ''
modele: in_vivo
modele_score: 4.5
modele_secondaires: []
modele_indices:
- animals
- mice
theme: neuro_comportement_cognition
theme_score: 2.0
theme_secondaires: []
theme_indices:
- behavior
tags:
- rf
- modele/in_vivo
- theme/neuro_comportement_cognition
- annee/2026
---

# Virtual Mice, Real Errors: A Sensor-Aware Generative Framework for In Silico Ethology.

*Sensors (Basel, Switzerland) — 2026*

## Résumé (texte d'origine)

Long-duration animal trajectories are central to computational ethology, yet constructing large rodent cohorts remains costly, time-intensive, and constrained by animal-use considerations. We present a sensor-aware generative framework that separates latent behavioral dynamics from sensing-induced observation distortion to synthesize observed-domain trajectories that are behaviorally plausible while reproducing proxy-referenced observation distortions. The framework combines a run-level semi-Markov ethology model, occupancy calibration, and state-conditioned kinematic generation with a regime-dependent Ultra-Wideband observation channel that explicitly captures Line-of-Sight and Non-Line-of-Sight sensing conditions. Using four UWB sessions, this proof-of-concept study models three states-exploring, feeding, and burrowing-and evaluates realism through state occupancy, state-conditioned kinematic divergence, residual-domain agreement, and mean-squared displacement across time lags. We further assess whether sensor-aware conditioning improves robustness under LoS/NLoS domain shift in downstream trajectory classification. Sensor-aware conditioning yields stable mixed-domain performance with AUC = 0.995, whereas condition-agnostic baselines decline to AUC = 0.974 and AUC = 0.901. These results support the feasibility of sensor-aware in silico ethology as a proof-of-concept framework for controlled robustness studies and algorithm evaluation under proxy-referenced observation distortion. Because the present evaluation is based on four UWB sessions and uses a smoothed UWB-derived reference trajectory rather than independent ground truth, broader applications to synthetic-cohort generation, disease modeling, and statistical power-analysis workflows should be considered future directions requiring validation in larger datasets.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/42197786/)
