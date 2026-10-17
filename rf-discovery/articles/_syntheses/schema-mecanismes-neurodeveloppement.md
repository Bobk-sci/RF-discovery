---
type: schema
question: "Schéma des processus mécanistiques : par quelles voies les radiofréquences agiraient-elles sur le neurone en développement ?"
date: 2026-10-17
fiches_lues: 42
corpus: 2470
source: "[[synthese-neurogenese-synaptogenese-migration]]"
---

# Schéma des mécanismes

Lecture du diagramme : un trait plein marque une chaîne répliquée ou testée causalement,
un trait pointillé une chaîne reposant sur une seule étude. Les encadrés gris sont les
effets **non retrouvés**. Aucun maillon n'est dessiné qui ne vienne d'une fiche lue.

```mermaid
flowchart TD
  RF["Exposition RF<br/>0,017 à 14,1 W/kg selon les études"]

  RF --> NEU["<b>Croissance des neurites</b><br/>le mieux établi"]
  RF --> SYN["<b>Synapse</b>"]
  RF --> NG["<b>Neurogenèse</b>"]
  RF --> MY["<b>Myéline et glie</b>"]
  RF -.-> NUL["<b>Prolifération et cycle cellulaire</b><br/>effet NON retrouvé"]

  NEU --> E1["EPHA5 ↓ → CREB · RhoA<br/>PMID 33912567<br/><i>sauvetage : rétablir EPHA5 annule l'effet</i>"]
  NEU --> E2["Ngn1 ↓ · NeuroD ↓ · Hes1 ↑<br/>PMID 24869783"]
  E1 --> NOUT["Neurites plus courts,<br/>moins de branchements<br/>confirmé in vivo — PMID 39201275"]
  E2 --> NOUT

  SYN --> POST["SNK ↑ → SPAR ↓ → PSD-95 ↓<br/>épines rétrécies et perdues<br/>PMID 29180226 · 39201275 · 32581772"]
  SYN --> PRE["Synapsines I/II ↓ · synaptotagmine 1 ↓<br/>vésicules, arrimage et fusion ↓<br/>PMID 29045446 · 31411574 · 19603498"]
  SYN --> BD["HNRNPA2B1 ↓ → m6A de TrkB ↓<br/>→ TrkB dégradé → BDNF ↓<br/>PMID 39999628"]
  POST -.-> CONTRA["CONTRADICTION<br/>30 min uniques à 3,3 W/kg :<br/>épines ↑ et mémoire ↑<br/>PMID 28303965"]
  PRE -.-> NOPH["mais aucun changement<br/>phénotypique mesuré<br/>PMID 31411574"]

  NG --> GD["Cellules granulaires du gyrus denté ↓<br/>fractionnateur optique, p &lt; 0,01<br/>PMID 18761003"]
  NG --> RMS["Prolifération et mort cellulaire modifiées<br/>selon l'âge et la région — PMID 39286040 · 29527915"]

  MY --> MBP["MBP ↓ · NF-L ↓ · axones myélinisés ↓<br/>PMID 33759170 · 32476377 · 25205214"]
  MY --> GFAP["GFAP ↑ — astrogliose<br/>PMID 20546709 · 33759170 · 32476377"]

  NUL --> N1["Cellules souches neurales embryonnaires :<br/>ni apoptose, ni cycle, ni différenciation<br/>PMID 24869783 · 16953672 · 19479910"]

  NOUT --> PLAF
  POST --> PLAF
  GD --> PLAF
  PLAF["<b>Plafond</b> — poids du cerveau non affecté<br/>SMD 0,10 (−0,09 à 0,29), certitude modérée<br/>PMID 37729852 · 6487382"]

  RF -.-> ABS["<b>Migration neuronale</b><br/>0 étude sur 2 470 fiches"]

  classDef etabli fill:#d6ebea,stroke:#0d6a6d,stroke-width:2px,color:#141d27
  classDef conteste fill:#f6e6d2,stroke:#9d540d,stroke-width:2px,color:#141d27
  classDef nul fill:#dde3ea,stroke:#5c6a7b,stroke-width:1px,color:#141d27
  classDef absent fill:#e8dff0,stroke:#6c4a84,stroke-width:1px,stroke-dasharray:5 4,color:#141d27

  class NEU,E1,E2,NOUT,PRE,BD,NG,GD,RMS,MY,MBP,GFAP,SYN,POST etabli
  class CONTRA,NOPH conteste
  class NUL,N1,PLAF nul
  class ABS absent
```

## Les quatre choses à retenir du schéma

1. **Un seul maillon a été testé causalement.** Rétablir la signalisation EPHA5 annule
   l'inhibition des neurites (PMID 33912567). Partout ailleurs, on observe une corrélation
   entre une exposition et un marqueur.
2. **La prolifération n'est pas la cible.** Trois études nulles sur les modèles les plus
   pertinents, dont une conçue pour la question sur des cellules souches neurales
   embryonnaires (PMID 24869783, 16953672, 19479910).
3. **Deux dissociations marqueur / fonction.** Les vésicules présynaptiques bougent sans
   conséquence phénotypique (PMID 31411574) ; les épines et PSD-95 bougent alors que le
   poids du cerveau ne bouge pas (PMID 37729852).
4. **Les chaînes établies convergent vers 4 W/kg**, bien au-dessus des niveaux
   environnementaux — et aucun modèle humain ne permet de les vérifier.

Version interactive, avec la dosimétrie par maillon :
https://claude.ai/artifact/Xb6uQmbBASog6r7rb5R5X1

Synthèse complète : [[synthese-neurogenese-synaptogenese-migration]]
