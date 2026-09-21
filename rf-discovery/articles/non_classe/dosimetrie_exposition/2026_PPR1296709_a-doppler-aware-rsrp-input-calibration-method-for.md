---
pmid: PPR1296709
doi: 10.20944/preprints202608.0725.v1
annee: 2026
journal: ''
titre: A Doppler-Aware RSRP Input Calibration Method for Handover in High-Speed Railway
  5G-R
url: https://doi.org/10.20944/preprints202608.0725.v1
source: europepmc
acces_ouvert: ''
collecte: '2026-09-21'
mesh: []
types:
- Preprint
mots_cles: []
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: dosimetrie_exposition
theme_score: 1.0
theme_secondaires: []
theme_indices:
- base station
---

# A Doppler-Aware RSRP Input Calibration Method for Handover in High-Speed Railway 5G-R

*journal non renseigné — 2026*

## Résumé (texte d'origine)

Short-term fluctuations in reference signal received power (RSRP) under high-mobility conditions can repeatedly reset the time-to-trigger (TTT) timer and cause spatial dispersion of Event A3 handover triggers in high-speed railway 5G-R systems. To address this problem, this study develops a physics-driven, Doppler-aware RSRP input-calibration framework that preserves the standardized handover margin (HOM), TTT, Event A3 semantics, and Radio Resource Control (RRC) procedure. The relative residual Doppler shift is derived from train kinematics and base-station geometry and estimated online using a scalar Kalman filter. The resulting estimate is mapped to an orthogonal frequency-division multiplexing frequency-offset-induced equivalent RSRP loss subject to a physical upper bound. Geometry-based detrending, speed-adaptive causal smoothing of the residual component, and a low-weight bounded position-aided correction are subsequently applied to reconstruct the serving- and candidate-cell RSRP inputs. Event-driven simulations covering viaduct and mountainous railway scenarios, together with ablation, Doppler-sensitivity, speed-adaptability, and observation-error analyses, are conducted to evaluate the proposed method. At a train speed of 350 km/h, the method reduces the root-mean-square error of the inter-cell RSRP difference from 2.3449 to 1.9053 dB and decreases the mean handover trigger-location error from 54.79 to 42.35 m, while maintaining a handover success rate of 99.49%, comparable to the 99.29% achieved by conventional Event A3. The results further demonstrate that, under a carrier frequency of 2.1 GHz and a subcarrier spacing of 30 kHz, the overall performance improvement is governed primarily by geometric detrending, speed-adaptive residual smoothing, and bounded position correction, whereas Doppler-loss compensation provides a small but physically consistent correction of the deterministic measurement bias. The proposed framework therefore improves RSRP input quality and handover trigger-location consistency without modifying the standardized handover decision logic.

[Référence d'origine](https://doi.org/10.20944/preprints202608.0725.v1)
