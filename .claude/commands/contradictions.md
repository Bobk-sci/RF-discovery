---
description: Repère les résultats qui se contredisent dans le corpus sur un sujet donné
argument-hint: <sujet> (ex. perméabilité de la barrière hémato-encéphalique)
---

Cherche dans `rf-discovery/articles/` les études qui **se contredisent** sur : **$ARGUMENTS**

Rends un tableau : PMID · année · modèle d'étude · effet rapporté (positif / nul /
protecteur) · conditions d'exposition mentionnées (fréquence, SAR, durée) · effectif.

Puis, pour chaque désaccord, propose les explications que les fiches permettent
réellement d'examiner :

- modèle d'étude différent (in vivo / in vitro / humain) ;
- fréquence, modulation, SAR ou durée d'exposition différents ;
- moment de l'exposition (prénatal, juvénile, adulte) ;
- absence ou présence d'un groupe sham ;
- ancienneté (les protocoles de dosimétrie ont changé).

Règles :

- Aucune référence, aucun chiffre inventé. Ce qui n'est pas dans le résumé n'existe pas
  pour cette analyse : écris « non précisé dans le résumé » plutôt que de combler.
- Ne tranche pas un débat que les données ne tranchent pas. Une contradiction non
  résolue reste une contradiction.
- Signale si les études en désaccord viennent des mêmes équipes.
