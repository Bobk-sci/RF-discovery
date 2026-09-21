---
pmid: '41548019'
doi: 10.1038/s41598-026-36495-1
annee: 2026
journal: ''
titre: Modelling selective heating in microwave-heated packed-bed reactors.
url: https://pubmed.ncbi.nlm.nih.gov/41548019/
source: europepmc
acces_ouvert: open
collecte: '2026-09-21'
mesh: []
types:
- research-article
- Journal Article
mots_cles:
- Process Intensification
- Multiphysics Simulation
- Plastic Waste Recycling Technologies
- Industrial Electrification
- Microwave-assisted Processes
auteurs:
- Niño CG
pmcid: PMC12891532
volume: ''
pages: '5636'
modele: non_classe
modele_score: 0.0
modele_secondaires: []
modele_indices: []
theme: thermique
theme_score: 2.5
theme_secondaires: []
theme_indices:
- heating
tags:
- rf
- modele/non_classe
- theme/thermique
- annee/2026
---

# Modelling selective heating in microwave-heated packed-bed reactors.

*journal non renseigné — 2026*

## Résumé (texte d'origine)

The design of efficient microwave-assisted reactors for industrially relevant processes, such as plastic waste thermochemical recycling via pyrolysis, presents substantial challenges due to the tight coupling of electromagnetic, thermal, and fluid flow phenomena within heterogeneous and anisotropic media. This study introduces a robust and reproducible methodological framework for reactor-scale simulation of microwave-heated packed beds, tailored to systems employing silicon carbide (SiC) susceptors. Realistic packed-bed geometries are first generated via Discrete Element Method (DEM) simulations, capturing the spatial arrangement of susceptor particles. To enable electromagnetic modeling, a custom de-interpenetration algorithm processes the DEM output, eliminating overlaps while preserving physical tangency. Rather than simulating the full discrete geometry — which incurs prohibitive computational costs — the final reactor model adopts a temperature-dependent effective medium representation. The medium’s complex permittivity is calibrated through a Python–COMSOL optimization loop, which matches the electromagnetic energy absorption and storage of the homogenized domain to that of DEM-based unit cells across a wide temperature range. These properties are then integrated into a coupled multiphysics model that resolves electromagnetic wave propagation, nitrogen flow through free and porous media, and dual-temperature heat transfer in a SiC–nitrogen packed bed, with microwave losses selectively applied to the susceptor phase and no explicit plastic phase or chemical reactions modelled. A proof-of-concept application demonstrates the ability of the framework to predict operational regimes that achieve pyrolysis-relevant temperatures without thermal runaway.

[Référence d'origine](https://pubmed.ncbi.nlm.nih.gov/41548019/)
