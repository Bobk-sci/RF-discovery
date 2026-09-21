---
description: Synthétise l'état des connaissances sur un thème à partir des fiches du corpus
argument-hint: <thème ou question> (ex. stress oxydatif hippocampe, exposition prénatale)
---

Synthétise ce que dit le corpus sur : **$ARGUMENTS**

Méthode :

1. Cherche les fiches concernées dans `rf-discovery/articles/` (Grep sur le titre, le
   résumé, les descripteurs MeSH ; les dossiers disent déjà le modèle d'étude et le thème).
   Sers-toi aussi de `articles/index.csv` pour repérer vite les candidats.
2. Lis les fiches retenues — le résumé y est recopié mot pour mot depuis la source.
3. Organise la synthèse **par modèle d'étude** : in vivo, in vitro, épidémiologie, humain
   expérimental. Les niveaux de preuve ne se mélangent pas.
4. Pour chaque affirmation, cite le PMID entre parenthèses. Une affirmation sans PMID est
   interdite.
5. Termine par : le nombre de fiches lues, les désaccords entre études, et ce que le
   corpus **ne** permet pas de conclure.

Règles :

- N'invente aucune référence, aucun résultat, aucun chiffre. Si une donnée n'est pas dans
  les fiches lues, dis-le au lieu de la produire.
- Un résumé n'est pas un article : les effectifs, la dosimétrie (SAR, durée) et les
  conditions d'exposition manquent souvent. Signale-le quand la conclusion en dépend.
- Distingue « les auteurs rapportent » de « il est établi que ».
- Si moins de cinq fiches correspondent, dis que la base est trop mince plutôt que de
  généraliser.
