---
pmid: '41755281'
doi: 10.3390/s26041342
annee: 2026
journal: Sensors (Basel, Switzerland)
titre: 'Toward Mobile Neuroimaging: Design of a Multi-Modal EEG/fNIRS Instrument for
  Real-Time Use.'
url: https://pubmed.ncbi.nlm.nih.gov/41755281/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Humans
- Electroencephalography
- Spectroscopy, Near-Infrared
- Signal Processing, Computer-Assisted
- Neuroimaging
- Brain
- Wireless Technology
- Equipment Design
- Cell Phone
types:
- Journal Article
mots_cles:
- ADS1299
- EEG
- ESP32-S2
- Lab Streaming Layer
- STM32H7
- TLC5940
- embedded system
- fNIRS
- mobile neuroimaging
- wireless brain monitoring
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: eeg_sommeil
theme_score: 2.5
theme_secondaires: []
theme_indices:
- EEG
---

# Toward Mobile Neuroimaging: Design of a Multi-Modal EEG/fNIRS Instrument for Real-Time Use.

*Sensors (Basel, Switzerland) — 2026*

## Résumé (texte d'origine)

In this study, we present the design and development of a mobile, multi-modal electroencephalography and functional near-infrared spectroscopy (EEG/fNIRS) device for wireless neurophysiological monitoring. The system was engineered to achieve high signal fidelity, low power consumption, and a fully untethered operation suitable for ambulatory brain research. The device integrates four Texas Instruments ADS1299 24-bit biopotential amplifiers, providing up to 32 simultaneous acquisition channels. Signal control, processing, and local storage via an SD card are managed by an STM32H7 microcontroller, while an ESP32-S2 module handles Wi-Fi communication. Dual-wavelength light-emitting diodes and OPT101 photodiodes form the optical front-end, driven by digitally controlled constant-current sources for stable illumination. The design employs galvanic isolation, multi-rail power management, and a four-layer PCB layout to minimise interference between analogue, power, and digital domains. Data are captured by a deterministic, clock-driven STM32 acquisition loop and forwarded to the ESP32, which operates under an RTOS and streams packets over Wi-Fi for collection on a mobile phone or PC using the Lab Streaming Layer (LSL) framework. The STM32H7 architecture was chosen for its capability to support future embedded edge-machine-learning functions, enabling on-device signal quality assessment and artefact rejection. Validation demonstrations include 32-channel synchronised acquisition using the ADS1299 internal test signal, eyes-open/eyes-closed alpha modulation visualised in EEGLAB, a forehead fNIRS breath-hold response with physiological spectral content, and real-time ECG/optical pulse streaming via LSL. The resulting system provides a compact platform with explicitly defined acquisition and data interfaces for synchronised EEG/fNIRS acquisition, enabling scalable, low-cost mobile neuroimaging research.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41755281/)
