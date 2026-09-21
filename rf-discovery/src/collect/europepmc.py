"""Collecte Europe PMC (§4) — parsing pur, réseau injectable.

``search`` accepte un ``fetcher`` (callable ``(url, params) -> json``) ; par défaut
``collect.cache.get_json``. Les tests passent un fetcher de fixture : aucun accès réseau.
Règle §3 : pour un domaine-pont (``rf_terms_allowed=False``) la requête ne contient
jamais de terme RF — c'est à l'appelant de construire la requête en conséquence.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from collect.cache import get_json

Fetcher = Callable[[str, dict[str, Any]], Any]
_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


@dataclass
class Paper:
    pmid: str
    doi: str
    title: str
    abstract: str
    year: int
    journal: str
    domain: str = ""
    source: str = "europepmc"
    oa_status: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def build_query(base_query: str, rf_terms: list[str], rf_terms_allowed: bool) -> str:
    """Combine (ou non) les termes RF selon la classe du domaine (§3)."""
    if not rf_terms_allowed:
        return base_query
    rf = " OR ".join(f'"{t}"' for t in rf_terms)
    return f"({base_query}) AND ({rf})"


def _listed(rec: dict[str, Any], container: str, item: str, key: str) -> list[str]:
    """Extrait une liste imbriquée Europe PMC (MeSH, types de publication, mots-clés)."""
    node = rec.get(container) or {}
    entries = node.get(item) or [] if isinstance(node, dict) else []
    out = []
    for entry in entries:
        value = entry.get(key) if isinstance(entry, dict) else entry
        if value:
            out.append(str(value))
    return out


def _authors(rec: dict[str, Any]) -> list[str]:
    """Auteurs « Nom I. » — depuis la liste structurée, sinon depuis ``authorString``."""
    node = rec.get("authorList") or {}
    entries = node.get("author") or [] if isinstance(node, dict) else []
    names = [str(a.get("fullName") or "").strip()
             for a in entries if isinstance(a, dict) and a.get("fullName")]
    if names:
        return names
    raw = str(rec.get("authorString") or "").rstrip(".")
    return [n.strip() for n in raw.split(",") if n.strip()]


def _to_paper(rec: dict[str, Any], domain: str) -> Paper:
    return Paper(
        pmid=str(rec.get("pmid") or rec.get("id") or ""),
        doi=str(rec.get("doi") or ""),
        title=str(rec.get("title") or ""),
        abstract=str(rec.get("abstractText") or ""),
        year=int(rec.get("pubYear") or 0),
        journal=str(rec.get("journalTitle") or ""),
        domain=domain,
        oa_status="open" if rec.get("isOpenAccess") == "Y" else "",
        extra={
            # Descripteurs fournis par la source : ils servent au classement (§ classify).
            "mesh": _listed(rec, "meshHeadingList", "meshHeading", "descriptorName"),
            "types": _listed(rec, "pubTypeList", "pubType", ""),
            "keywords": _listed(rec, "keywordList", "keyword", ""),
            # Auteurs et identifiants de texte intégral : nécessaires pour exporter une
            # référence complète (EndNote/Zotero) et retrouver le PDF en accès libre.
            "authors": _authors(rec),
            "pmcid": str(rec.get("pmcid") or ""),
            "volume": str(rec.get("journalVolume") or ""),
            "pages": str(rec.get("pageInfo") or ""),
        },
    )


def search(
    query: str,
    *,
    domain: str = "",
    page_size: int = 1000,
    max_results: int = 1000,
    fetcher: Fetcher | None = None,
    cache_dir: str = "data/cache",
) -> list[Paper]:
    """Recherche Europe PMC avec pagination par ``cursorMark`` jusqu'à ``max_results``."""
    fetch = fetcher or (lambda u, p: get_json(u, p, cache_dir=cache_dir))
    papers: list[Paper] = []
    cursor, seen = "*", set()
    while len(papers) < max_results:
        params = {"query": query, "format": "json", "pageSize": min(page_size, 1000),
                  "resultType": "core", "cursorMark": cursor}
        data = fetch(_BASE, params) or {}
        results = data.get("resultList", {}).get("result", [])
        papers.extend(_to_paper(r, domain) for r in results if (r.get("pmid") or r.get("id")))
        nxt = data.get("nextCursorMark")
        if not results or not nxt or nxt == cursor or nxt in seen:
            break
        seen.add(cursor)
        cursor = nxt
    return papers[:max_results]
