"""Cartes de lecture pour Obsidian — le corpus devient un coffre navigable.

Les fiches sont déjà du Markdown avec en-tête YAML : Obsidian les lit telles quelles. Il
manque seulement des points d'entrée. Ce module écrit dans ``articles/_cartes/`` :

* une carte par catégorie de premier axe (`in_vivo`, `epidemiologie`, …), les articles
  groupés par thème et triés du plus récent au plus ancien ;
* une carte d'accueil qui renvoie vers les précédentes.

Ces notes commencent par ``_`` : ``iter_fiches`` les ignore, elles ne sont donc jamais
prises pour des articles. Les liens sont des wikilinks ``[[nom de fichier]]``, la forme
qu'Obsidian résout sans configuration (les noms de fiches sont uniques).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

CARTES = "_cartes"
ACCUEIL = "Accueil.md"


def _lien(meta: dict[str, Any]) -> str:
    nom = Path(str(meta.get("fichier", ""))).stem
    annee = meta.get("annee") or "s.d."
    auteurs = meta.get("auteurs") or []
    signature = f"{auteurs[0]} et al." if len(auteurs) > 2 else ", ".join(auteurs)
    return f"- `{annee}` [[{nom}]] — {signature}" if signature else f"- `{annee}` [[{nom}]]"


def _carte(categorie: str, records: list[dict[str, Any]], second: str) -> str:
    par_theme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for meta in records:
        par_theme[str(meta.get(second) or "general")].append(meta)
    lignes = [f"# {categorie}", "", f"{len(records)} articles.", ""]
    for theme in sorted(par_theme):
        entrees = sorted(par_theme[theme], key=lambda m: -int(m.get("annee") or 0))
        lignes += [f"## {theme} ({len(entrees)})", ""]
        lignes += [_lien(m) for m in entrees]
        lignes.append("")
    return "\n".join(lignes)


def _derniers_comptes_rendus(root: Path, combien: int = 5) -> list[str]:
    """Liens vers les derniers comptes rendus de collecte, s'il y en a."""
    dossier = root / "_veilles"
    veilles = sorted(dossier.glob("veille-*.md"), reverse=True)[:combien] if \
        dossier.exists() else []
    if not veilles:
        return []
    return ["## Dernières veilles", "", *[f"- [[{v.stem}]]" for v in veilles], ""]


def write_maps(root: str | Path, records: list[dict[str, Any]],
               axes: tuple[str, ...]) -> int:
    """Écrit les cartes de lecture ; renvoie le nombre de fichiers produits."""
    if not axes:
        return 0
    premier, second = axes[0], (axes + ("",))[1]
    dossier = Path(root) / CARTES
    dossier.mkdir(parents=True, exist_ok=True)
    par_categorie: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for meta in records:
        par_categorie[str(meta.get(premier) or "non_classe")].append(meta)

    ecrits = 0
    for categorie, entrees in sorted(par_categorie.items()):
        (dossier / f"{categorie}.md").write_text(
            _carte(categorie, entrees, second), encoding="utf-8")
        ecrits += 1
    lignes = [
        "# Bibliothèque RF", "",
        f"{len(records)} articles, carte mise à jour le {date.today().isoformat()}.", "",
        "## Par modèle d'étude", "",
        *[f"- [[{c}]] ({len(e)})" for c, e in sorted(par_categorie.items())],
        "", *_derniers_comptes_rendus(Path(root)),
        "## Étiquettes", "",
        "Chaque fiche porte `modele/…`, `theme/…` et `annee/…` : le panneau des",
        "étiquettes d'Obsidian donne les mêmes entrées, croisées.",
    ]
    (dossier / ACCUEIL).write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return ecrits + 1
