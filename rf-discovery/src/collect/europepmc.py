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
    )


def search(
    query: str,
    *,
    domain: str = "",
    page_size: int = 100,
    fetcher: Fetcher | None = None,
    cache_dir: str = "data/cache",
) -> list[Paper]:
    """Recherche Europe PMC ; renvoie une liste de ``Paper`` normalisés."""
    fetch = fetcher or (lambda u, p: get_json(u, p, cache_dir=cache_dir))
    params = {"query": query, "format": "json", "pageSize": page_size, "resultType": "core"}
    data = fetch(_BASE, params)
    results = (data or {}).get("resultList", {}).get("result", [])
    return [_to_paper(r, domain) for r in results if (r.get("pmid") or r.get("id"))]
