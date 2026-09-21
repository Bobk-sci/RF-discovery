---
description: Rédige un paragraphe scientifique sourcé, appuyé sur les fiches du corpus
argument-hint: <ce que doit dire le paragraphe>
---

Rédige un passage pour : **$ARGUMENTS**

Procédure, dans cet ordre :

1. **D'abord chercher, ensuite écrire.** Trouve les fiches pertinentes dans
   `rf-discovery/articles/`, lis-les, et seulement après rédige.
2. Écris un paragraphe continu, en français, ton scientifique sobre — pas de liste à
   puces, pas de superlatifs.
3. Chaque affirmation porte sa source sous la forme (Auteur et al., année, PMID xxxxxxx).
   Les auteurs figurent dans l'en-tête de la fiche (`auteurs`).
4. Sous le paragraphe, ajoute :
   - **Fiches utilisées** : la liste des chemins lus ;
   - **Références** : format prêt à copier, ou renvoi à `articles/bibliotheque-rf.ris`
     pour l'import EndNote ;
   - **Réserves** : ce que le paragraphe affirme au-delà de ce que les résumés
     établissent réellement, s'il y a lieu.

Règles absolues :

- **Aucune référence inventée.** Pas de PMID, d'auteur, d'année ou de revue qui ne
  figure pas dans une fiche que tu viens de lire. C'est la faute la plus grave possible
  ici : elle survit à la relecture et se retrouve dans un manuscrit publié.
- Aucun chiffre (effectif, SAR, p-value) qui ne soit pas écrit dans le résumé.
- Si le corpus ne soutient pas ce qu'on te demande d'écrire, dis-le et propose la
  formulation que les données autorisent.
- Attribue les effets au bon modèle : ce qui est observé sur des cellules ne se
  transpose pas à l'humain dans la phrase.

## Où écrire le résultat

Écris la réponse dans `rf-discovery/articles/_syntheses/redaction-<sujet-en-minuscules>.md`,
en commençant par un en-tête YAML :

```yaml
---
type: redaction
question: "<la demande, telle qu'elle a été formulée>"
date: <AAAA-MM-JJ>
fiches_lues: <nombre>
---
```

Ce dossier est dans le coffre Obsidian (jonction) : la note y apparaît aussitôt, et
Smart Connections l'indexera comme les autres. Le préfixe `_` le met à l'abri des
scripts de reclassement.

Affiche aussi la réponse dans la conversation, et termine par le chemin du fichier écrit.
