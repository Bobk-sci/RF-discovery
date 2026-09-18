"""Import de notices déjà récupérées (export JSON) — utile hors ligne.

Trois formes acceptées, toutes issues de sources réelles :
  * export Europe PMC (``{"resultList": {"result": [...]}}``) ;
  * export PubMed/JSON (``{"articles": [...]}`` avec ``identifiers``/``publication_date``) ;
  * simple liste d'objets ``{"pmid": ..., "title": ..., "abstract": ...}``.

Aucun champ n'est complété d'office : ce que l'export ne contient pas reste vide.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from collect.europepmc import Paper
from collect.europepmc import _to_paper as epmc_paper


def _records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        for key in ("articles", "records", "results", "papers"):
            if isinstance(data.get(key), list):
                return [r for r in data[key] if isinstance(r, dict)]
        result = (data.get("resultList") or {}).get("result")
        if isinstance(result, list):
            return [r for r in result if isinstance(r, dict)]
    return []


def _year(rec: dict[str, Any]) -> int:
    date = rec.get("publication_date")
    if isinstance(date, dict):
        raw = date.get("year")
    else:
        raw = rec.get("pubYear") or rec.get("year") or rec.get("annee") or date
    try:
        return int(str(raw)[:4])
    except (TypeError, ValueError):
        return 0


def _listify(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v]
    return [str(value)] if value else []


def to_paper(rec: dict[str, Any], domain: str = "", source: str = "import") -> Paper | None:
    """Notice brute -> ``Paper`` ; ``None`` si elle ne porte aucun identifiant ni titre."""
    if "resultList" in rec or ("pubYear" in rec and "title" in rec):
        return epmc_paper(rec, domain)
    raw_ids = rec.get("identifiers")
    ids: dict[str, Any] = raw_ids if isinstance(raw_ids, dict) else {}
    journal = rec.get("journal")
    pmid = str(ids.get("pmid") or rec.get("pmid") or "")
    doi = str(ids.get("doi") or rec.get("doi") or "")
    title = str(rec.get("title") or rec.get("titre") or "")
    if not (pmid or doi or title):
        return None
    return Paper(
        pmid=pmid,
        doi=doi,
        title=title,
        abstract=str(rec.get("abstract") or rec.get("abstractText") or ""),
        year=_year(rec),
        journal=str(journal.get("title") if isinstance(journal, dict) else journal or ""),
        domain=domain,
        source=str(rec.get("source") or source),
        extra={
            "mesh": _listify(rec.get("mesh_terms") or rec.get("mesh")),
            "types": _listify(rec.get("article_types") or rec.get("types")),
            "keywords": _listify(rec.get("keywords")),
        },
    )


def papers_from_json(path: str | Path, domain: str = "",
                     source: str = "import") -> list[Paper]:
    """Lit un export JSON et rend les articles qu'il contient réellement.

    ``source`` conserve la provenance réelle de l'export (p. ex. ``pubmed``) dans la fiche.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    papers = (to_paper(rec, domain, source) for rec in _records(data))
    return [p for p in papers if p is not None]
