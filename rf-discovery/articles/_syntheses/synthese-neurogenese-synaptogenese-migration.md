---
type: synthese
question: "Neurodéveloppement au sens cellulaire : neurogenèse, synaptogenèse, migration cellulaire, croissance des neurites, myélinisation — que dit le corpus sur les effets des radiofréquences ?"
date: 2026-10-01
fiches_lues: 42
revision: 2
corpus: 2470
---

# Radiofréquences et mécanismes du neurodéveloppement

> **Deuxième version.** La première portait sur un corpus de 1 370 fiches. L'ajout de la
> source OpenAlex l'a porté à **2 470**, dont 125 publications antérieures à l'an 2000 que
> les requêtes PubMed et Europe PMC ne ramenaient pas. Douze fiches mécanistiques nouvelles
> ont été lues. **Trois conclusions de la première version changent** et sont signalées
> comme telles.

Question posée : sur quels processus cellulaires les radiofréquences agiraient-elles ?
Prolifération des progéniteurs, survie, différenciation, migration, croissance des
neurites, formation et maturation des synapses, myélinisation.

La remarque de méthode reste entière : **cette question n'a ni modèle épidémiologique ni
modèle humain expérimental.** On ne compte pas les cellules en division dans l'hippocampe
d'un enfant vivant. Tout ce qui suit est rongeur ou culture cellulaire.

---

## 1. Neurogenèse

### 1.1 Un comptage direct, qui manquait à la première version

L'apport le plus net du corpus élargi. Des rates gestantes exposées à **900 MHz, 60 min par
jour du premier au dernier jour de gestation** ; la descendance est sacrifiée à 4 semaines
et les cellules granulaires du gyrus denté sont comptées au **fractionnateur optique**. Le
nombre est significativement diminué (p < 0,01), et les auteurs attribuent cette perte à une
inhibition de la neurogenèse granulaire (18761003, 6 descendants exposés contre 5 témoins).

C'est, dans ce corpus, **le seul comptage stéréologique direct d'une population neuronale
issue de la neurogenèse après exposition prénatale**. Il manquait à ma première synthèse.

Deux études complètent le tableau dans les niches neurogéniques. Exposition prénatale à
2,45 GHz, 2 h/jour : modifications du nombre de cellules en prolifération et en mort
**dépendantes de l'âge de l'animal et de la région**, et maturation atténuée des neurones
nitrergiques du flux migratoire rostral (39286040). Comparaison explicite juvénile/adulte au
même protocole 2,45 GHz : chez le juvénile la prolifération est peu touchée, mais **la mort
cellulaire reste affectée deux mois après la fin de l'irradiation**, avec hyperactivité et
évaluation du risque diminuée à l'âge adulte (29527915).

À 900 MHz en pré- et postnatal (0,08 et 0,4 W/kg), les cellules prolifératives BrdU+ et le
BDNF diminuent chez le raton à PND8 et PND17 (40907581).

### 1.2 Perte neuronale et réaction astrocytaire

Exposition chronique à **835 MHz, SAR 1,6 W/kg, 3 mois** : perte d'interneurones et de
cellules pyramidales en CA1, perte de cellules granulaires, immunoréactivité à la calbindine
diminuée, GFAP augmenté, et cellules apoptotiques détectées par TUNEL en CA1, CA3 et gyrus
denté (20546709).

Chez le rat de 8 semaines exposé à 900 MHz 1 h/jour pendant 30 jours, le comptage
stéréologique donne un nombre total de neurones pyramidaux significativement abaissé
(26239913). L'histomorphométrie sur souris à 900-1800 MHz trouve une densité réduite en CA1,
CA2 et DGDB mais **augmentée en CA3 et DGVB** (27656427) — l'inconsistance de direction
interne à cette étude demeure.

La réaction astrocytaire, elle, converge : GFAP augmenté dans trois études indépendantes
(20546709, 33759170, 32476377).

### 1.3 Migration : le corpus reste muet

Deux travaux examinent le flux migratoire rostral (39286040, 29527915), mais y comptent des
divisions et des morts, pas des trajectoires, des vitesses ni des destinations. La seule
observation touchant au devenir des neuroblastes reste la maturation nitrergique atténuée.

**Sur 2 470 fiches, aucune étude de migration neuronale au sens propre.** L'élargissement du
corpus n'a rien changé à ce constat, ce qui le renforce : ce n'est pas un défaut de collecte.

---

## 2. Prolifération et cycle cellulaire — ce que je concluais à tort

**Première version :** « le corpus ne permet pas de dire dans quel sens les radiofréquences
affectent la prolifération ». Le corpus élargi permet d'être plus précis, et la réponse
penche nettement.

Deux études directement conçues pour cette question répondent **non**.

Sur des **cellules souches neurales embryonnaires** exposées à 1800 MHz aux SAR de 1, 2 et
4 W/kg pendant 1, 2 et 3 jours, l'exposition **n'influence ni l'apoptose, ni la
prolifération, ni le cycle cellulaire, ni l'expression des gènes correspondants**, et **ne
modifie pas le rapport neurones / astrocytes** issus de la différenciation (24869783). Sur
des cellules Mono Mac 6 humaines exposées 12 h à 1800 MHz GSM-DTX à 2 W/kg, aucune
différence sur le cycle cellulaire, l'incorporation de BrdU, l'apoptose ou la nécrose — alors
que les témoins positifs réagissent comme attendu (16953672).

| PMID | Modèle | Exposition | Prolifération |
|---|---|---|---|
| 24869783 | cellules souches neurales embryonnaires | 1800 MHz, 1-4 W/kg, 3 j | **inchangée** |
| 16953672 | Mono Mac 6 humaines | 1800 MHz GSM, 2 W/kg, 12 h | **inchangée** |
| 19479910 | SN56, neurones corticaux primaires | 900 MHz GSM, 1 W/kg, 144 h | **inchangée** |
| 34196262 | SH-SY5Y (neuroblastome) | 1760 MHz LTE, 4 W/kg | diminuée — sénescence Akt/mTOR, sans dommage à l'ADN |
| 33074167 | V79 (fibroblastes) | 915 MHz GSM, 0,23-1,6 W/kg | diminuée, après atteinte des microtubules |
| 40907581 | cellules souches neurales | 900 MHz, 0,08 W/kg | augmentée (Ki-67+) |

**Trois résultats nuls contre trois résultats positifs de directions opposées**, et les trois
nuls portent sur les modèles les plus pertinents — progéniteurs neuraux, neurones primaires.
La lecture que les données autorisent : **la prolifération n'est pas la cible principale**.
Les deux baisses rapportées concernent une lignée tumorale et une lignée de fibroblastes de
hamster, où la sénescence et le cytosquelette sont en jeu, pas la neurogenèse.

---

## 3. Croissance des neurites — le mécanisme le mieux établi

**Première version :** un seul mécanisme testé causalement. **Désormais deux voies
moléculaires indépendantes et une observation in vivo, toutes dans le même sens.**

**Voie EPHA5.** Après séquençage ARN à haut débit, les transcrits du développement des
neurites ressortent comme influencés par l'exposition à 1800 MHz pendant la différenciation
neuronale. Longueur totale des neurites et nombre de branchements diminuent, dans des
neurones dérivés de cellules souches neurales **et** dans des Neuro-2A. EPHA5, requis pour la
croissance des neurites, est fortement inhibé — et **renforcer la signalisation EPHA5 annule
l'effet**. CREB et RhoA sont les effecteurs en aval (33912567).

**Voie proneurale Ngn1 / NeuroD / Hes1.** Dans la même étude qui ne trouve aucun effet sur la
prolifération, la croissance des neurites des neurones différenciés **est** inhibée après
3 jours à 4 W/kg, avec une baisse de l'ARNm et des protéines **Ngn1** et **NeuroD**, deux
gènes proneuraux indispensables à cette croissance, et une hausse de leur inhibiteur **Hes1**
(24869783).

**Observation in vivo.** À 1850 MHz, SAR 4,0 W/kg, chez la souris dès PND28 : réduction des
épines dendritiques en champignon du cortex préfrontal, baisse des puncta PSD-95, inhibition
de la croissance des neurites et baisse des gènes de formation synaptique (CADM, CDK5), avec
altération de l'apprentissage spatial (39201275).

Deux laboratoires, deux voies moléculaires sans rapport l'une avec l'autre, une expérience de
sauvetage, une confirmation in vivo, et une étude qui **sépare** l'effet neuritique de
l'absence d'effet prolifératif dans le même protocole. **C'est le résultat le plus solide du
dossier.** Les trois convergent par ailleurs autour de 4 W/kg — un SAR élevé, bien au-dessus
des niveaux environnementaux.

---

## 4. Synapses

### 4.1 Versant post-synaptique : PSD-95, et une contradiction

PSD-95 reste à la baisse dans trois études indépendantes : 1850 MHz chez le souriceau
(39201275), 30 mW/cm² chez le rat adulte par la voie SNK-SPAR (29180226), et après exposition
prénatale chez le rat âgé, avec SYN et BDNF (32581772).

**Mais le corpus élargi apporte une contradiction frontale.** Une exposition **unique de
30 minutes à 1,8 GHz, SAR 3,3 W/kg**, chez la souris : l'index de reconnaissance d'objet
nouveau **augmente** de façon dose-dépendante, et le marquage de Golgi montre une densité et
une longueur des épines dendritiques **accrues** dans l'hippocampe et le cortex préfrontal,
avec modification du potentiel de repos et de la forme du potentiel d'action des neurones
pyramidaux (28303965). Les auteurs eux-mêmes placent ce SAR hors de la gamme rencontrée dans
la vie courante et évoquent une piste thérapeutique.

Densité d'épines **diminuée** après exposition répétée sur des semaines (39201275, 29180226)
contre **augmentée** après une exposition unique de 30 minutes (28303965). Le corpus ne
tranche pas ; il suggère que la durée et le caractère répété comptent autant que le SAR, sans
le démontrer.

### 4.2 Versant présynaptique : trois études convergentes, un phénotype absent

À **835 MHz, SAR 4,0 W/kg, 5 h/jour** : densité des vésicules synaptiques significativement
réduite dans les boutons présynaptiques du cortex cérébral, avec baisse des gènes et
protéines **synapsines I/II** (29045446). Au même protocole porté à 12 semaines, dans
l'hypothalamus : nombre et taille des vésicules réduits, **densité des vésicules en position
d'arrimage et de fusion dans les zones actives** diminuée, synapsine I/II, synaptotagmine 1 et
canal calcique à la baisse (31411574).

À un SAR bien plus élevé (14,1 W/kg, 30 mW/cm², 5 minutes), les protéines vésiculaires du
cortex et de l'hippocampe sont perturbées de façon non monotone dans le temps : synapsine I,
synaptophysine, VAMP-2, syntaxine, et l'interaction VAMP-2 / syntaxine réduite de 3 à 7 jours
(19603498). Après exposition longue à 2,856 et 9,375 GHz, la structure du gyrus denté est
altérée, Snapin diminue et les vésicules présynaptiques s'accumulent (36782203).

**Une réserve que les auteurs posent eux-mêmes, et qui pèse :** malgré ces changements
moléculaires nets, l'étude hypothalamique **ne trouve aucun changement phénotypique**
— température corporelle, poids, test de la croquette enfouie tous normaux (31411574). Un
marqueur qui bouge n'est pas une fonction qui se dégrade.

Une analyse protéomique iTRAQ de l'hippocampe après micro-ondes accumulées (2,856 GHz puis
1,5 GHz, 10 mW/cm²) rapporte 391 protéines différentiellement exprimées, dont les processus
biologiques incluent le développement cérébral et la neurogenèse, et les voies KEGG le cycle
des vésicules synaptiques et la potentialisation à long terme ; l'exposition cumulée produit
plus de changements que chaque bande seule (31012066).

### 4.3 Plasticité fonctionnelle

À 2,45 GHz, SAR corps entier de **0,017 W/kg**, 2 h/jour pendant 40 jours : induction de la
potentialisation à long terme et excitabilité des CA1 réduites, densité neuronale CA1
diminuée, la plasticité à court terme restant intacte (30345889). Exposition gestationnelle à
900 MHz pulsé : excitabilité réduite des CA1 avec mémoire altérée dans les deux sexes
(24604340) ; mêmes altérations sur les cellules de Purkinje **sans** conséquence
comportementale (23906636).

---

## 5. BDNF : un mécanisme, désormais

**Première version :** BDNF en baisse dans deux études, sans explication.

Le corpus élargi en propose une. Un modèle de rat irradié présente des déficits
d'apprentissage et de mémoire, une plasticité synaptique altérée dans les neurones
hippocampiques matures **et une prolifération et un développement des cellules souches
neurales entravés**. Mécanistiquement, la baisse de **HNRNPA2B1** réduit la liaison m⁶A de
l'ARNm de **TrkB** et favorise sa dégradation ; cette boucle aboutit à une **expression basse
du BDNF** et, selon les auteurs, aux troubles cognitifs (39999628). Résultat répliqué dans un
modèle de co-culture sans contact.

Avec 40907581 et 32581772, le BDNF apparaît donc dans trois études, et pour la première fois
avec une voie de régulation proposée.

---

## 6. Myélinisation : d'une étude à trois sources

**Première version :** « une seule étude, un seul organe, les mâles uniquement ». Ce n'est
plus exact.

- Exposition prénatale à 850-1900 MHz, 6 h ou 24 h/jour : dans le groupe longue durée,
  **MBP et NF-L diminués, GFAP augmenté**, proportionnellement à la durée (32476377).
- Exposition prénatale et postnatale précoce à 1800 MHz, SAR 1,79 W/kg : **nombre d'axones
  myélinisés significativement diminué**, avec MDA augmenté, GSH diminué, GFAP augmenté, et
  atteinte du nerf trijumeau ; les effets sont plus marqués en mode conversation qu'en
  veille (33759170).
- Une revue dédiée recense les données disponibles sur myéline et RF : lésions morphologiques
  de la gaine de myéline chez le rat, risque accru de sclérose en plaques dans un sous-groupe
  d'une étude, effets sur des protéines de la production de myéline. Les auteurs soulignent
  eux-mêmes qu'il y a **étonnamment peu de données dans chaque domaine**, et désignent comme
  les plus vulnérables les sujets exposés de la vie intra-utérine au milieu de l'adolescence
  (25205214).

Sur la moelle épinière, l'analyse stéréologique à J35 ne trouve **aucune différence** sur les
rapports substance grise / substance blanche ni sur le volume total, malgré une dégénérescence
motoneuronale et une désorganisation axonale à l'examen ultrastructural (40694058).

---

## 7. Cellules souches non neuronales

Des cellules engainantes olfactives — une glie qui présente des caractéristiques de cellules
souches — exposées 10, 15 ou 20 minutes à 900 MHz, en onde continue ou modulée en amplitude :
à 20 minutes, la viabilité diminue de façon significative et différente selon la forme de
l'onde, avec des changements d'expression de S-100, nestine, GFAP et vimentine et une
activation de la caspase-3 variable selon l'enveloppe du signal (32041804). Les auteurs
notent qu'il existe **peu de données sur l'auto-renouvellement des progéniteurs neuraux** —
ce que ce corpus confirme.

Le volet in vitro de 40907581 reste le seul résultat sur progéniteurs issus du cerveau en
développement : à 0,08 W/kg, hausse des Ki-67+, de l'apoptose et des cassures double brin,
avec moins de cellules B1 et davantage de progéniteurs d'oligodendrocytes et d'astrocytes.

La méta-analyse de 300 publications et 1 127 observations in vitro (1990-2015) garde son
intérêt principal dans sa stratification : les effets se concentreraient sur les types
cellulaires **à croissance rapide et peu différenciés**, tandis que glie, glioblastome et
lymphocytes adultes ne montrent pas de différence significative (32199316). Les auteurs
signalent ne pas avoir tenu compte du biais de financement, et il s'agit d'une méta-analyse
de fréquences de résultats positifs, pas d'effets.

---

## 8. Épidémiologie et humain expérimental : rien, par construction

Aucune étude épidémiologique ni expérimentale humaine du corpus — 2 470 fiches désormais — ne
mesure la neurogenèse, la synaptogenèse, la migration cellulaire ou la myélinisation. Il n'y
a **aucun pont expérimental** entre les mécanismes décrits ci-dessus et l'humain.

---

## 9. Revues

Une revue narrative affirme que les champs électromagnétiques inhibent la formation et la
différenciation des cellules souches neurales pendant le développement embryonnaire
(26686296). Je la rapporte comme une position d'auteurs : son résumé n'en donne ni la base
quantitative ni l'évaluation du risque de biais. À noter que 18761003 ouvre sur exactement la
même affirmation — les deux proviennent du même milieu, ce n'est donc pas une confirmation
indépendante.

Une revue sur les enfants juge l'information sur les processus développementaux
**insuffisante** et appelle à des protocoles cohérents (26661935).

La revue systématique du projet OMS, quantifiée et graduée, garde le dernier mot sur le
critère structurel intégré : **le poids du cerveau n'est pas affecté par une exposition in
utero (SMD 0,10 ; IC 95 % −0,09 à 0,29), avec une certitude modérée**, et l'apprentissage et
la mémoire non plus (SMD −0,54 ; −1,24 à 0,17), à certitude faible à très faible (37729852).
La revue sur enfants et adolescents juge le corps de preuve faible à inadéquat (35648738).

---

## 10. Bilan

**Fiches lues : 42**, sur un corpus de 2 470.

### Ce qui a changé depuis la première version

1. **La neurogenèse a désormais un comptage direct** : cellules granulaires du gyrus denté
   diminuées après exposition prénatale à 900 MHz, au fractionnateur optique (18761003).
2. **La prolifération n'est probablement pas la cible.** Trois études nulles sur les modèles
   les plus pertinents, dont une conçue pour la question sur des cellules souches neurales
   embryonnaires (24869783, 16953672, 19479910). Ma première version présentait cela comme
   indécidable ; ce n'est plus le cas.
3. **La croissance des neurites est le mécanisme le mieux établi** : deux voies moléculaires
   indépendantes (EPHA5/CREB/RhoA et Ngn1/NeuroD/Hes1), une expérience de sauvetage, une
   confirmation in vivo (33912567, 24869783, 39201275).
4. **La myélinisation passe d'une étude à trois sources** (32476377, 33759170, 25205214).
5. **Le BDNF a un mécanisme proposé** (39999628).

### Désaccords

- **Épines dendritiques, directions opposées** : densité diminuée après exposition répétée
  pendant des semaines (39201275, 29180226), **augmentée** après une exposition unique de
  30 minutes, avec mémoire de reconnaissance améliorée (28303965).
- **Prolifération** : trois nuls, deux baisses sur lignées non neurales, une hausse sur
  progéniteurs (voir § 2).
- **Densité neuronale à l'intérieur d'une même étude** : diminuée en CA1, CA2, DGDB,
  augmentée en CA3 et DGVB (27656427).
- **Marqueurs contre fonction** : vésicules synaptiques, synapsines et synaptotagmine
  nettement modifiées dans l'hypothalamus — et **aucun changement phénotypique** mesurable
  (31411574). Même dissociation pour les cellules de Purkinje (23906636) et la moelle épinière
  (40694058).
- **Cellules contre structure** : altérations cellulaires nombreuses d'un côté, poids du
  cerveau non affecté avec certitude modérée (37729852) et organogenèse cérébrale intacte au
  comptage cellulaire direct dès 1984 (6487382).

### Ce que le corpus ne permet toujours pas de conclure

- **La migration neuronale n'est pas étudiée.** Zéro étude sur 2 470 fiches. L'élargissement
  du corpus confirme qu'il s'agit d'une lacune de la littérature, pas de la collecte.
- **Les doses ne sont pas comparables.** De **0,017 W/kg** (30345889) à **14,1 W/kg**
  (19603498) — près de mille fois — et plusieurs travaux ne rapportent qu'une densité de
  puissance. Fait notable : les trois études sur la croissance des neurites convergent autour
  de **4 W/kg**, bien au-dessus des niveaux environnementaux.
- **Développement contre adulte.** Plusieurs mécanismes majeurs viennent d'animaux adultes —
  SNK-SPAR (29180226), vésicules synaptiques (29045446, 31411574, 19603498), LTP (30345889),
  calbindine et GFAP (20546709), cellules souches hippocampiques adultes (35882410). Ils
  relèvent de la neurogenèse adulte et de la plasticité, pas de la construction du cerveau.
- **Les effectifs restent petits** quand ils figurent : 6 contre 5 descendants (18761003),
  6 par groupe (26239913), 8 par groupe (24604340, 32476377), 10 par groupe (23906636).
- **Aucun pont vers l'humain**, et le seul critère structurel méta-analysé est négatif avec
  une certitude modérée.

### Formulation que les données autorisent

Chez le rongeur et en culture, l'exposition aux radiofréquences laisse la prolifération des
progéniteurs neuraux largement inchangée mais **inhibe la croissance des neurites**, par au
moins deux voies moléculaires dont l'une a été testée par sauvetage. Plusieurs équipes
rapportent en parallèle une raréfaction des épines dendritiques, une baisse de PSD-95 et du
BDNF, une perturbation de la machinerie vésiculaire présynaptique, une réaction astrocytaire,
et — dans une étude — une diminution du nombre de cellules granulaires du gyrus denté après
exposition prénatale. D'autres équipes, avec d'autres protocoles, ne retrouvent rien, et une
étude rapporte l'effet inverse sur les épines. Ces observations sont majoritairement obtenues
à des SAR de l'ordre de 4 W/kg. Il n'est pas établi qu'elles modifient la construction du
cerveau au niveau structurel, qu'elles surviennent aux niveaux d'exposition environnementaux,
ni qu'elles concernent l'humain.
