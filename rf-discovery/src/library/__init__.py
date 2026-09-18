"""Bibliothèque RF : collecte d'articles réels et rangement en sous-dossiers.

Règle absolue : **aucune référence n'est inventée**. Chaque fiche provient d'un
enregistrement Europe PMC (PMID/DOI réels) ; un champ absent de la source reste vide.
Aucun texte n'est reformulé ni généré : titre, résumé et métadonnées sont recopiés tels
quels. Le classement est un comptage de mots-clés (``config/taxonomy.yaml``), donc
reproductible et vérifiable ligne à ligne.
"""
