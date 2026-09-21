"""Export des fiches vers RIS et BibTeX — les formats que lisent EndNote et Zotero.

Le RIS est le format natif d'EndNote ; Zotero l'importe aussi, comme le BibTeX. Le
classement de la bibliothèque est transporté en **mots-clés** (`KW` / `keywords`) :
`modele:in_vivo`, `theme:neurodeveloppement`. Zotero en fait des étiquettes, sur
lesquelles on peut reconstruire des collections en deux clics.

Rien n'est inventé ici non plus : un champ absent de la fiche est simplement omis, jamais
comblé. Si un PDF a été téléchargé (accès libre), son chemin part dans `L1`/`file`, ce qui
attache le fichier à la référence à l'import.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Types de publication PubMed -> type RIS. Par défaut : article de revue.
_RIS_TYPES = {"review": "JOUR", "meta-analysis": "JOUR", "journal article": "JOUR",
              "book": "BOOK", "book chapter": "CHAP"}
_BIB_KEY = re.compile(r"[^A-Za-z0-9]+")


def _tags(meta: dict[str, Any], axes: tuple[str, ...]) -> list[str]:
    tags = [f"{axis}:{meta[axis]}" for axis in axes if meta.get(axis)]
    for axis in axes:
        tags += [f"{axis}:{s}" for s in (meta.get(f"{axis}_secondaires") or [])]
    return tags + [str(k) for k in (meta.get("mots_cles") or [])]


def _ris_type(meta: dict[str, Any]) -> str:
    for t in meta.get("types") or []:
        if str(t).lower() in _RIS_TYPES:
            return _RIS_TYPES[str(t).lower()]
    return "JOUR"


def to_ris(records: list[dict[str, Any]], axes: tuple[str, ...],
           pdf_dir: Path | None = None) -> str:
    """Notices -> RIS. Un champ absent est omis ; aucune valeur n'est fabriquée."""
    out: list[str] = []
    for meta in records:
        lines = [f"TY  - {_ris_type(meta)}"]
        lines += [f"AU  - {a}" for a in (meta.get("auteurs") or [])]
        for tag, key in (("TI", "titre"), ("JO", "journal"), ("PY", "annee"),
                         ("VL", "volume"), ("SP", "pages"), ("AB", "resume"),
                         ("DO", "doi"), ("UR", "url")):
            value = str(meta.get(key) or "").strip().replace("\n", " ")
            if value:
                lines.append(f"{tag}  - {value}")
        if meta.get("pmid"):
            lines.append(f"AN  - {meta['pmid']}")
        lines += [f"KW  - {k}" for k in _tags(meta, axes)]
        pdf = _pdf_path(meta, pdf_dir)
        if pdf:
            lines.append(f"L1  - {pdf}")
        out.append("\n".join(lines) + "\nER  - \n")
    return "\n".join(out)


def _pdf_path(meta: dict[str, Any], pdf_dir: Path | None) -> str:
    """URI ``file://`` du PDF local, ou chaîne vide.

    Zotero n'exploite ``L1`` que si la valeur est une URI qu'il sait résoudre : un chemin
    Windows brut (``E:\\pdf\\1234.pdf``) est ignoré silencieusement, une URI
    ``file:///E:/pdf/1234.pdf`` attache le fichier. ``as_uri`` exige un chemin absolu,
    d'où la résolution préalable.
    """
    local = str(meta.get("pdf_local") or "")
    if local and Path(local).exists():
        return Path(local).resolve().as_uri()      # PDF apporté par l'utilisateur
    if pdf_dir is None or not meta.get("pmid"):
        return ""
    candidate = Path(pdf_dir).resolve() / f"{meta['pmid']}.pdf"
    return candidate.as_uri() if candidate.exists() else ""


def _bib_key(meta: dict[str, Any], used: set[str]) -> str:
    first = (meta.get("auteurs") or ["anon"])[0].split()[0].lower()
    key = _BIB_KEY.sub("", f"{first}{meta.get('annee', '')}") or "ref"
    suffix, candidate = 0, key
    while candidate in used:
        suffix += 1
        candidate = f"{key}{chr(ord('a') + suffix - 1)}"
    used.add(candidate)
    return candidate


def _bib_escape(value: str) -> str:
    return value.replace("{", "(").replace("}", ")").replace("\\", "").strip()


def to_bibtex(records: list[dict[str, Any]], axes: tuple[str, ...]) -> str:
    """Notices -> BibTeX (Zotero, LaTeX). Mêmes règles : aucun champ inventé."""
    used: set[str] = set()
    blocks = []
    for meta in records:
        fields = {
            "author": " and ".join(meta.get("auteurs") or []),
            "title": str(meta.get("titre") or ""),
            "journal": str(meta.get("journal") or ""),
            "year": str(meta.get("annee") or ""),
            "volume": str(meta.get("volume") or ""),
            "pages": str(meta.get("pages") or ""),
            "doi": str(meta.get("doi") or ""),
            "url": str(meta.get("url") or ""),
            "note": f"PMID: {meta['pmid']}" if meta.get("pmid") else "",
            "keywords": ", ".join(_tags(meta, axes)),
            "abstract": str(meta.get("resume") or "").replace("\n", " "),
        }
        body = "".join(f"  {k} = {{{_bib_escape(v)}}},\n" for k, v in fields.items() if v)
        blocks.append(f"@article{{{_bib_key(meta, used)},\n{body}}}\n")
    return "\n".join(blocks)
