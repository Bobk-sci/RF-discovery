"""Compte rendu d'une collecte : ce qui est entré dans la bibliothèque, et où.

Une collecte silencieuse qui ajoute des articles ne se distingue pas d'une collecte qui
n'en ajoute aucun. Chaque run écrit donc une note dans ``articles/_veilles/`` :
les nouveaux articles groupés par catégorie, liés en wikilinks, lisibles dans Obsidian
au même titre que le reste du coffre.

Le compte rendu ne dit que ce qui s'est passé : nombres, titres, catégories. Aucune
synthèse, aucun résumé reformulé — ce n'est pas un modèle de langue qui l'écrit.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path

from library.organize import read_front_matter

VEILLES = "_veilles"


def _ligne(meta: dict, nom: str) -> str:
    annee = meta.get("annee") or "s.d."
    journal = str(meta.get("journal") or "").strip()
    auteurs = meta.get("auteurs") or []
    signature = f"{auteurs[0]} et al." if len(auteurs) > 2 else ", ".join(auteurs)
    details = " · ".join(x for x in (str(annee), signature, journal) if x)
    return f"- [[{nom}]] — {details}"


def rendre(fiches: list[Path], racine: Path, counts: dict[str, int],
           jour: str) -> str:
    """Texte du compte rendu ; ``fiches`` sont les chemins écrits par cette collecte."""
    ecartes = counts.get("_ecartes", 0)
    entete = [f"# Veille RF — {jour}", "",
              f"**{len(fiches)} nouveaux articles**"
              + (f", {ecartes} notices écartées (hors sujet)." if ecartes else ".")]
    if not fiches:
        return "\n".join(entete + ["", "Rien de nouveau : les sources n'ont renvoyé que "
                                   "des articles déjà rangés."]) + "\n"

    par_categorie: dict[tuple[str, str], list[tuple[dict, str]]] = defaultdict(list)
    for chemin in fiches:
        meta = read_front_matter(chemin)
        if not meta:
            continue
        parties = chemin.relative_to(racine).parts
        cle = (parties[0] if parties else "?", parties[1] if len(parties) > 1 else "")
        par_categorie[cle].append((meta, chemin.stem))

    lignes = entete + ["", "> Ce compte rendu liste ce qui est entré. Il ne résume "
                       "aucun article : les résumés sont dans les fiches, mot pour mot.", ""]
    for (modele, theme), entrees in sorted(par_categorie.items()):
        titre = f"{modele} / {theme}" if theme else modele
        lignes += [f"## {titre} ({len(entrees)})", ""]
        lignes += [_ligne(meta, nom)
                   for meta, nom in sorted(entrees, key=lambda e: -int(e[0].get("annee") or 0))]
        lignes.append("")
    return "\n".join(lignes) + "\n"


def write_digest(out: Path, fiches: list[Path], counts: dict[str, int],
                 jour: str | None = None) -> Path:
    """Écrit le compte rendu du jour dans ``articles/_veilles/``."""
    jour = jour or date.today().isoformat()
    dossier = Path(out) / VEILLES
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"veille-{jour}.md"
    chemin.write_text(rendre(fiches, Path(out), counts, jour), encoding="utf-8")
    return chemin
