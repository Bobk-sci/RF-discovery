---
pmid: '28420605'
doi: 10.2196/jmir.6821
annee: 2017
journal: Journal of medical Internet research
titre: 'Scalable Passive Sleep Monitoring Using Mobile Phones: Opportunities and Obstacles.'
url: https://pubmed.ncbi.nlm.nih.gov/28420605/
source: pubmed
acces_ouvert: ''
collecte: '2026-09-21'
mesh:
- Adolescent
- Adult
- Aged
- Cell Phone
- Data Collection
- Female
- Humans
- Male
- Middle Aged
- Polysomnography
- Sleep
- Young Adult
types:
- Journal Article
mots_cles:
- classification
- decision trees
- mobile phones
- sleep monitoring
auteurs:
- Saeb S
- Cybulski TR
- Schueller SM
- Kording KP
- Mohr DC
pmcid: PMC5413802
volume: '19'
pages: e118
modele: epidemiologie
modele_score: 2.0
modele_secondaires: []
modele_indices:
- participants
- self-reported
theme: eeg_sommeil
theme_score: 4.5
theme_secondaires:
- neurodeveloppement
- neuro_comportement_cognition
theme_indices:
- sleep
- polysomnography
tags:
- rf
- modele/epidemiologie
- theme/eeg_sommeil
- theme/neurodeveloppement
- theme/neuro_comportement_cognition
- annee/2017
---

# Scalable Passive Sleep Monitoring Using Mobile Phones: Opportunities and Obstacles.

*Journal of medical Internet research — 2017*

## Résumé (texte d'origine)

BACKGROUND: Sleep is a critical aspect of people's well-being and as such assessing sleep is an important indicator of a person's health. Traditional methods of sleep assessment are either time- and resource-intensive or suffer from self-reporting biases. Recently, researchers have started to use mobile phones to passively assess sleep in individuals' daily lives. However, this work remains in its early stages, having only examined relatively small and homogeneous populations in carefully controlled contexts. Thus, it remains an open question as to how well mobile device-based sleep monitoring generalizes to larger populations in typical use cases.

OBJECTIVE: The aim of this study was to assess the ability of machine learning algorithms to detect the sleep start and end times for the main sleep period in a 24-h cycle using mobile devices in a diverse sample.

METHODS: We collected mobile phone sensor data as well as daily self-reported sleep start and end times from 208 individuals (171 females; 37 males), diverse in age (18-66 years; mean 39.3), education, and employment status, across the United States over 6 weeks. Sensor data consisted of geographic location, motion, light, sound, and in-phone activities. No specific instructions were given to the participants regarding phone placement. We used random forest classifiers to develop both personalized and global predictors of sleep state from the phone sensor data.

RESULTS: Using all available sensor features, the average accuracy of classifying whether a 10-min segment was reported as sleep was 88.8%. This is somewhat better than using the time of day alone, which gives an average accuracy of 86.9%. The accuracy of the model considerably varied across the participants, ranging from 65.1% to 97.3%. We found that low accuracy in some participants was due to two main factors: missing sensor data and misreports. After correcting for these, the average accuracy increased to 91.8%, corresponding to an average median absolute deviation (MAD) of 38 min for sleep start time detection and 36 min for sleep end time. These numbers are close to the range reported by previous research in more controlled situations.

CONCLUSIONS: We find that mobile phones provide adequate sleep monitoring in typical use cases, and that our methods generalize well to a broader population than has previously been studied. However, we also observe several types of data artifacts when collecting data in uncontrolled settings. Some of these can be resolved through corrections, but others likely impose a ceiling on the accuracy of sleep prediction for certain subjects. Future research will need to focus more on the understanding of people's behavior in their natural settings in order to develop sleep monitoring tools that work reliably in all cases for all people.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/28420605/)
