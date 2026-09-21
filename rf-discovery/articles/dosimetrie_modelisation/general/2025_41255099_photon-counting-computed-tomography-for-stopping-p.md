---
pmid: '41255099'
doi: 10.1002/mp.70146
annee: 2025
journal: Medical physics
titre: Photon-counting computed tomography for stopping power ratio prediction in
  proton therapy.
url: https://pubmed.ncbi.nlm.nih.gov/41255099/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Proton Therapy
- Tomography, X-Ray Computed
- Photons
- Phantoms, Imaging
- Humans
types:
- Journal Article
mots_cles:
- photon counting computed tomography
- stopping power ratio
auteurs:
- Huijskens S
- van Straten M
- Lopes PC
- Rossi L
- Wohlfahrt P
- Hoogeman M
pmcid: PMC12627983
pdf_local: ''
volume: '52'
pages: e70146
modele: dosimetrie_modelisation
modele_score: 1.0
modele_secondaires: []
modele_indices:
- phantom
theme: general
theme_score: 0.0
theme_secondaires: []
theme_indices: []
tags:
- rf
- modele/dosimetrie_modelisation
- theme/general
- annee/2025
---

# Photon-counting computed tomography for stopping power ratio prediction in proton therapy.

*Medical physics — 2025*

## Résumé (texte d'origine)

BACKGROUND: A substantial source of error in proton therapy is predicting the stopping power ratio (SPR) of tissues from computed tomography (CT). Due to its systematic nature, it is crucial to minimize this error as much as possible. Photon-counting CT (PCCT) scanners, which utilize semiconductor detectors to resolve the energy of X-rays, can extract more information per voxel compared to conventional CT scanners, offering potential improvements in material characterization and higher accuracy in proton range estimation.

PURPOSE: This study explores the potential of PCCT for improving SPR predictions compared to conventional single-energy CT (SECT) and dual-energy CT (DECT).

METHODS: SECT, DECT and PCCT scans of the CIRS SPR/Density phantom with tissue-equivalent inserts were acquired in body and head configurations using comparable scan and quantitative reconstruction settings. The SPR of each insert was predicted from SECT (SPRSECT) using a clinical Hounsfield look-up table (HLUT) and directly derived from DECT (SPRDECT) and PCCT (SPRPCCT) scans using spectral information (DirectSPR application, provided by Siemens Healthineers). Results were compared against measurements (SPRMeasured), obtained via a multi-layer ionization chamber, and differences relative to water (∆SPR) were calculated. Mean absolute errors (MAE) over the inserts were calculated for each imaging modality in both body and head configurations and per tissue subgroup. As a proof-of-concept, proton plans for a lung and neurological case were created to assess the impact on dose distribution using the SECT-HLUT approach (with 3% range uncertainty) or DirectSPR from PCCT (with 2% range uncertainty).

RESULTS: PCCT predicted SPR within 1.0% agreement with SPRMeasured, except for the insert "100% gland" (1.4%). The largest ∆SPR observed across all inserts and imaging modalities were found in lung and adipose inserts. For the soft tissue and bone inserts, estimated SPRs generally agreed well with SPRMeasured (∆SPR ≤1.0%), except for the inserts soft tissue grey and cortical bone (both ∆SPRSECT,head = 1.3%). Among the three imaging modalities, the overall mean absolute error (MAE) was lowest for PCCT by a small margin (body: 0.58% for SECT, 0.72% for DECT, 0.57% for PCCT, head: 0.58% for SECT, 0.48% for DECT, 0.46% for PCCT). However, for each tissue subgroup separately, MAEs for PCCT were not consistently lowest and MAEs were comparable across imaging modalities, ranging from 0.22% to 2.83%. In the clinical cases, dose distributions for SECT-HLUT and PCCT plans showed dose differences particularly at the distal end of the beams, attributed to optimization with reduced range uncertainty in the PCCT plan or due to areas with thicker bone or air cavities.

CONCLUSIONS: The DirectSPR application for PCCT achieved promising accuracy in SPR prediction. Overall, the absolute deviations were small and comparable across all three imaging modalities. However, concerning the performance of SECT, it should be noted that the SECT-based HLUT was calibrated using the same CIRS phantom as used during the evaluation, whereby these results are the best-case scenario. Although the clinical cases showed minimal differences in dose distributions between SECT and PCCT plans, PCCT may offer improved reliability, as it provides patient-specific direct SPR predictions without relying on HLUT conversion.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41255099/)
