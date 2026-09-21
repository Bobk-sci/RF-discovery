---
pmid: '34095816'
doi: 10.3389/frai.2021.543176
annee: 2021
journal: Frontiers in artificial intelligence
titre: CNN-Based LCD Transcription of Blood Pressure From a Mobile Phone Camera.
url: https://pubmed.ncbi.nlm.nih.gov/34095816/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh: []
types:
- Journal Article
mots_cles:
- blood pressure
- convolutional neural network
- digital transcription
- hypertension
- optical character recognition
- preeclampsia
modele: revue
modele_score: 1.0
modele_secondaires:
- epidemiologie
modele_indices:
- state of the art
theme: neurodeveloppement
theme_score: 1.0
theme_secondaires: []
theme_indices:
- pregnancy
---

# CNN-Based LCD Transcription of Blood Pressure From a Mobile Phone Camera.

*Frontiers in artificial intelligence — 2021*

## Résumé (texte d'origine)

Routine blood pressure (BP) measurement in pregnancy is commonly performed using automated oscillometric devices. Since no wireless oscillometric BP device has been validated in preeclamptic populations, a simple approach for capturing readings from such devices is needed, especially in low-resource settings where transmission of BP data from the field to central locations is an important mechanism for triage. To this end, a total of 8192 BP readings were captured from the Liquid Crystal Display (LCD) screen of a standard Omron M7 self-inflating BP cuff using a cellphone camera. A cohort of 49 lay midwives captured these data from 1697 pregnant women carrying singletons between 6 weeks and 40 weeks gestational age in rural Guatemala during routine screening. Images exhibited a wide variability in their appearance due to variations in orientation and parallax; environmental factors such as lighting, shadows; and image acquisition factors such as motion blur and problems with focus. Images were independently labeled for readability and quality by three annotators (BP range: 34-203 mm Hg) and disagreements were resolved. Methods to preprocess and automatically segment the LCD images into diastolic BP, systolic BP and heart rate using a contour-based technique were developed. A deep convolutional neural network was then trained to convert the LCD images into numerical values using a multi-digit recognition approach. On readable low- and high-quality images, this proposed approach achieved a 91% classification accuracy and mean absolute error of 3.19 mm Hg for systolic BP and 91% accuracy and mean absolute error of 0.94 mm Hg for diastolic BP. These error values are within the FDA guidelines for BP monitoring when poor quality images are excluded. The performance of the proposed approach was shown to be greatly superior to state-of-the-art open-source tools (Tesseract and the Google Vision API). The algorithm was developed such that it could be deployed on a phone and work without connectivity to a network.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/34095816/)
