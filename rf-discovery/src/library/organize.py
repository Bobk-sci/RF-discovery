"""Écriture de la bibliothèque : une fiche Markdown par article, rangée en sous-dossiers.

Arborescence produite ::

    articles/
      in_vivo/neurodeveloppement/2019_31234567_effects-of-900-mhz....md
      in_vitro/stress_oxydatif/...
      index.csv          # tout le corpus, une ligne par article
      README.md          # compte par catégorie, régénéré à chaque run

Chaque fiche porte un en-tête YAML (métadonnées **recopiées** d'Europe PMC) puis le
résumé d'origine, mot pour mot. Rien n'est reformulé, rien n'est complété : un champ
absent de la source reste vide, et un article sans résumé le dit explicitement.
"""
from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from collect.europepmc import Paper
from library.classify import Assignment, Taxonomy

INDEX_NAME = "index.csv"
README_NAME = "README.md"
COLUMNS = ["pmid", "doi", "annee", "modele", "theme", "themes_secondaires",
           "journal", "titre", "url", "fichier"]
_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_len: int = 60) -> str:
    slug = _SLUG.sub("-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-") or "sans-titre"


def article_url(paper: Paper) -> str:
    """Lien vers la référence réelle ; vide si la source n'a fourni aucun identifiant."""
    if paper.pmid and paper.pmid.isdigit():
        return f"https://pubmed.ncbi.nlm.nih.gov/{paper.pmid}/"
    if paper.doi:
        return f"https://doi.org/{paper.doi}"
    return ""


def _stem(paper: Paper) -> str:
    ident = paper.pmid or slugify(paper.doi, 30) or "sans-id"
    year = str(paper.year or "0000")
    return f"{year}_{ident}_{slugify(paper.title, 50)}"


def article_path(root: str | Path, paper: Paper,
                 assignments: dict[str, Assignment], axes: tuple[str, ...]) -> Path:
    """Chemin de la fiche : un dossier par axe, dans l'ordre déclaré par la taxonomie."""
    folders = [assignments[a].category for a in axes if a in assignments]
    return Path(root).joinpath(*folders, f"{_stem(paper)}.md")


def _front_matter(paper: Paper, assignments: dict[str, Assignment],
                  axes: tuple[str, ...]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "pmid": paper.pmid,
        "doi": paper.doi,
        "annee": paper.year or "",
        "journal": paper.journal,
        "titre": paper.title,
        "url": article_url(paper),
        "source": paper.source,
        "acces_ouvert": paper.oa_status or "",
        "collecte": date.today().isoformat(),
        # Descripteurs d'origine : ils ont servi au classement et restent vérifiables.
        "mesh": list(paper.extra.get("mesh") or []),
        "types": list(paper.extra.get("types") or []),
        "mots_cles": list(paper.extra.get("keywords") or []),
        # De quoi produire une référence complète (EndNote/Zotero) et retrouver le PDF.
        "auteurs": list(paper.extra.get("authors") or []),
        "pmcid": str(paper.extra.get("pmcid") or ""),
        "volume": str(paper.extra.get("volume") or ""),
        "pages": str(paper.extra.get("pages") or ""),
    }
    for axis in axes:
        a = assignments.get(axis)
        if a is None:
            continue
        meta[axis] = a.category
        meta[f"{axis}_score"] = a.score
        meta[f"{axis}_secondaires"] = a.secondaires
        meta[f"{axis}_indices"] = a.matched
    return meta


def render_article(paper: Paper, assignments: dict[str, Assignment],
                   axes: tuple[str, ...]) -> str:
    """Fiche Markdown : en-tête YAML + résumé d'origine (aucune reformulation)."""
    meta = _front_matter(paper, assignments, axes)
    head = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).rstrip()
    body = paper.abstract.strip() or "_Résumé non fourni par la source._"
    link = f"\n\n[Référence d'origine]({meta['url']})" if meta["url"] else ""
    return (f"---\n{head}\n---\n\n# {paper.title}\n\n"
            f"*{paper.journal or 'journal non renseigné'}"
            f"{f' — {paper.year}' if paper.year else ''}*\n\n"
            f"## Résumé (texte d'origine)\n\n{body}{link}\n")


def write_article(root: str | Path, paper: Paper, assignments: dict[str, Assignment],
                  axes: tuple[str, ...]) -> Path:
    path = article_path(root, paper, assignments, axes)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_article(paper, assignments, axes), encoding="utf-8")
    return path


def read_front_matter(path: str | Path) -> dict[str, Any]:
    """Relit l'en-tête YAML d'une fiche (index reconstruit depuis le disque)."""
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    _, _, rest = text.partition("---\n")
    head, _, _ = rest.partition("\n---")
    data = yaml.safe_load(head) or {}
    return data if isinstance(data, dict) else {}


_BODY_MARK = "## Résumé (texte d'origine)"


def read_article(path: str | Path) -> Paper:
    """Reconstruit l'article depuis sa fiche (reclassement sans re-collecte)."""
    meta = read_front_matter(path)
    text = Path(path).read_text(encoding="utf-8")
    _, _, body = text.partition(_BODY_MARK)
    abstract = body.split("\n\n[Référence d'origine]")[0].strip()
    if abstract.startswith("_Résumé non fourni"):
        abstract = ""
    return Paper(
        pmid=str(meta.get("pmid", "") or ""),
        doi=str(meta.get("doi", "") or ""),
        title=str(meta.get("titre", "") or ""),
        abstract=abstract,
        year=int(meta.get("annee") or 0),
        journal=str(meta.get("journal", "") or ""),
        source=str(meta.get("source", "") or ""),
        oa_status=str(meta.get("acces_ouvert", "") or ""),
        extra={"mesh": list(meta.get("mesh") or []),
               "types": list(meta.get("types") or []),
               "keywords": list(meta.get("mots_cles") or []),
               "authors": list(meta.get("auteurs") or []),
               "pmcid": str(meta.get("pmcid") or ""),
               "volume": str(meta.get("volume") or ""),
               "pages": str(meta.get("pages") or "")},
    )


def prune_empty_dirs(root: str | Path) -> int:
    """Supprime les dossiers vidés par un reclassement (l'arborescence reste lisible)."""
    removed = 0
    for path in sorted(Path(root).rglob("*"), key=lambda p: -len(p.parts)):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            removed += 1
    return removed


def scan_library(root: str | Path) -> list[dict[str, Any]]:
    """Inventorie toutes les fiches présentes sur le disque (run incrémental inclus)."""
    root = Path(root)
    records = []
    for path in sorted(root.rglob("*.md")):
        if path.name == README_NAME:
            continue
        meta = read_front_matter(path)
        if not meta:
            continue
        meta["fichier"] = str(path.relative_to(root))
        records.append(meta)
    return records


def _row(meta: dict[str, Any], axes: tuple[str, ...]) -> dict[str, Any]:
    first, second = (axes + ("", ""))[0], (axes + ("", ""))[1]
    secondaires = meta.get(f"{second}_secondaires") or []
    return {
        "pmid": meta.get("pmid", ""),
        "doi": meta.get("doi", ""),
        "annee": meta.get("annee", ""),
        "modele": meta.get(first, ""),
        "theme": meta.get(second, ""),
        "themes_secondaires": ";".join(secondaires),
        "journal": meta.get("journal", ""),
        "titre": meta.get("titre", ""),
        "url": meta.get("url", ""),
        "fichier": meta.get("fichier", ""),
    }


def write_index(root: str | Path, records: list[dict[str, Any]],
                axes: tuple[str, ...]) -> Path:
    """Index CSV du corpus complet, trié (stable d'un run à l'autre)."""
    path = Path(root) / INDEX_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted((_row(m, axes) for m in records),
                  key=lambda r: (r["modele"], r["theme"], -int(r["annee"] or 0), r["pmid"]))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _counts_table(records: list[dict[str, Any]], axes: tuple[str, ...]) -> list[str]:
    first, second = (axes + ("", ""))[0], (axes + ("", ""))[1]
    pairs = Counter((m.get(first, ""), m.get(second, "")) for m in records)
    lines = ["| Modèle | Thème | Articles |", "| --- | --- | ---: |"]
    for (modele, theme), n in sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {modele} | {theme} | {n} |")
    return lines


def write_readme(root: str | Path, records: list[dict[str, Any]],
                 tax: Taxonomy, query: str = "") -> Path:
    """Sommaire lisible : volume par catégorie, rappel de la méthode et des limites."""
    axes = tuple(ax.name for ax in tax.axes)
    years = [int(m.get("annee") or 0) for m in records if m.get("annee")]
    span = f"{min(years)}–{max(years)}" if years else "—"
    lines = [
        "# Bibliothèque RF",
        "",
        f"**{len(records)} articles** rangés le {date.today().isoformat()} "
        f"(publications {span}).",
        "",
        "Chaque fiche est un article **réel** indexé par Europe PMC, PubMed ou "
        "EMF-Portal : titre, résumé et métadonnées sont recopiés tels quels, jamais "
        "reformulés ni complétés. Le PMID/DOI de chaque fiche renvoie à la source "
        "(données PubMed / Europe PMC, NLM & EMBL-EBI).",
        "",
        "## Répartition",
        "",
        *_counts_table(records, axes),
        "",
        "## Comment c'est rangé",
        "",
        f"`{'/'.join(f'<{a}>' for a in axes)}/<année>_<pmid>_<titre>.md`",
        "",
        "Le classement compte les mots-clés de `config/taxonomy.yaml` dans le titre "
        f"(×{tax.title_boost}) et le résumé ; la catégorie la mieux notée l'emporte, "
        f"sous {tax.min_score} point l'article part en catégorie par défaut. "
        "Les mots-clés qui ont déclenché la décision sont notés dans l'en-tête de "
        "chaque fiche (`*_indices`), donc vérifiables. Pour reclasser le corpus, "
        "modifier `taxonomy.yaml` et relancer avec `--reclasser`.",
        "",
        f"`{INDEX_NAME}` reprend tout le corpus en une ligne par article.",
    ]
    if query:
        lines += ["", "## Requête Europe PMC", "", "```", query, "```"]
    path = Path(root) / README_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
