"""Identifiants -> notices complètes, via PubMed puis Europe PMC (§ sources-pont).

Règle commune à toutes les sources qui n'offrent pas de métadonnées recopiables telles
quelles (EMF-Portal, qui n'a pas d'API ; OpenAlex, dont le résumé n'est publié que sous
forme d'index inversé) : **on ne retient de ces sources que les identifiants stables**
— PMID et DOI — et le titre, le résumé et les descripteurs sont allés chercher auprès
de PubMed / Europe PMC, qui font foi.

Conséquence : une source-pont injoignable rend **zéro** article, jamais une notice
reconstruite. C'est la seule façon de tenir la règle « aucune référence inventée »
tout en élargissant le filet de collecte.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from collect import pubmed
from collect.europepmc import Paper


def _by_doi(dois: list[str], search_epmc: Callable[..., list[Paper]],
            batch: int = 40) -> list[Paper]:
    """Notices Europe PMC pour des DOI, par paquets (une requête ``DOI:"…" OR …``)."""
    papers: list[Paper] = []
    for start in range(0, len(dois), batch):
        chunk = dois[start:start + batch]
        query = " OR ".join(f'DOI:"{d}"' for d in chunk)
        papers.extend(search_epmc(query, max_results=len(chunk)))
    return papers


def by_ids(pmids: Iterable[str], dois: Iterable[str], *, via: str,
           domain: str = "", api_key: str = "", email: str = "",
           max_results: int = 500,
           fetcher_text: Callable[[str, dict[str, Any]], str] | None = None,
           search_epmc: Callable[..., list[Paper]] | None = None,
           cache_dir: str = "data/cache/pubmed") -> list[Paper]:
    """Résout des identifiants en notices complètes ; marque leur provenance (``via``)."""
    pmid_list = list(dict.fromkeys(p for p in pmids if p))
    doi_list = list(dict.fromkeys(d.lower() for d in dois if d))
    papers = pubmed.fetch_records(pmid_list[:max_results], api_key=api_key, email=email,
                                  domain=domain, fetcher_text=fetcher_text,
                                  cache_dir=cache_dir)
    known = {p.doi.lower() for p in papers if p.doi}
    if search_epmc is not None:
        rest = [d for d in doi_list if d not in known][:max_results]
        papers += _by_doi(rest, search_epmc)
    for paper in papers:
        paper.extra.setdefault("via", via)
    return papers
