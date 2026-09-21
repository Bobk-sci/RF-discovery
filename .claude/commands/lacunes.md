---
description: Identifie ce que le corpus ne couvre pas — angles morts et pistes de recherche
argument-hint: <domaine> (ex. neurodéveloppement, 5G, exposition professionnelle)
---

Analyse les angles morts du corpus sur : **$ARGUMENTS**

Démarche :

1. Compte ce qui existe : croise `articles/index.csv` (modèle × thème × année) pour ce
   domaine.
2. Nomme ce qui manque, en t'appuyant sur ce que tu observes :
   - modèles d'étude absents (p. ex. beaucoup d'in vitro, peu d'humain expérimental) ;
   - fréquences ou technologies peu couvertes (5G, ondes millimétriques, exposition
     multi-sources) ;
   - fenêtres d'exposition peu étudiées (gestation, adolescence, vieillissement) ;
   - effets long terme contre effets aigus ;
   - réplications manquantes : un résultat frappant cité une seule fois.
3. Distingue trois causes possibles, sans les confondre : sujet réellement peu étudié,
   sujet étudié mais hors de la requête de collecte, ou sujet présent mais mal classé
   (regarde alors `non_classe`).

Règles :

- Une lacune dans **ce** corpus n'est pas une lacune dans la littérature mondiale. Dis-le
  explicitement : la collecte couvre PubMed et Europe PMC via une requête donnée.
- N'invente pas d'étude « qui devrait exister ». Décris ce que tu vois, et ce que tu ne
  vois pas.
- Termine par les requêtes à ajouter dans `rf-discovery/config/taxonomy.yaml` pour
  combler ce qui semble manquer par construction.
