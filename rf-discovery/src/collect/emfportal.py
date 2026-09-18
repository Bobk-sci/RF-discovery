"""Collecte EMF-Portal (RWTH Aachen) — la base de référence sur les CEM.

EMF-Portal ne publie pas d'API : on ne peut donc pas s'appuyer sur une structure de
page qui changera. La stratégie retenue est **insensible à la mise en page** et ne
fabrique jamais de référence :

1. on récupère le texte d'une page de résultats (URL du portail **ou** fichier
   enregistré/exporté depuis le navigateur) ;
2. on en extrait les seuls identifiants stables : PMID et DOI ;
3. on va chercher les métadonnées auprès de PubMed / Europe PMC, qui font foi.

Conséquence : si le portail change ou devient inaccessible, l'étape rend zéro article
— jamais une notice approximative. L'URL de recherche est un **gabarit paramétrable**
(``--emfportal-url``) : copier depuis le navigateur l'URL d'une recherche EMF-Portal et
y remplacer les termes par ``{query}``.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from collect import pubmed
from collect.cache import get_text
from collect.europepmc import Paper

# Gabarit par défaut ; à confirmer/remplacer par l'URL réelle vue dans le navigateur.
DEFAULT_URL = "https://www.emf-portal.org/en/article/search?query={query}"

_PMID_PATTERNS = (
    re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d{4,9})"),
    re.compile(r"ncbi\.nlm\.nih\.gov/pubmed/(\d{4,9})"),
    re.compile(r"PMID[:\s]+(\d{4,9})", re.IGNORECASE),
)
_DOI = re.compile(r"10\.\d{4,9}/[^\s\"'<>&)\]]+")


def extract_ids(text: str) -> tuple[list[str], list[str]]:
    """Identifiants trouvés dans une page/export : (PMID, DOI), dédupliqués, ordre stable."""
    pmids: list[str] = []
    for pattern in _PMID_PATTERNS:
        for pmid in pattern.findall(text or ""):
            if pmid not in pmids:
                pmids.append(pmid)
    dois: list[str] = []
    for raw in _DOI.findall(text or ""):
        doi = raw.rstrip(".,;:").lower()
        if doi not in dois:
            dois.append(doi)
    return pmids, dois


def fetch_pages(query: str, *, url_template: str = DEFAULT_URL, pages: int = 1,
                fetcher_text: Callable[[str, dict[str, Any]], str] | None = None,
                cache_dir: str = "data/cache/emfportal") -> list[str]:
    """Texte brut des pages de résultats (le portail reste maître de son format)."""
    fetch = fetcher_text or (lambda u, p: get_text(u, p, cache_dir=cache_dir))
    texts = []
    for page in range(1, max(pages, 1) + 1):
        url = url_template.format(query=quote_plus(query), page=page)
        try:
            texts.append(fetch(url, {"page": page}) or "")
        except Exception:      # portail indisponible : on n'invente rien, on passe
            break
    return texts


def read_files(paths: Iterable[str | Path]) -> list[str]:
    """Pages/exports EMF-Portal enregistrés localement (HTML, RIS, texte)."""
    return [Path(p).read_text(encoding="utf-8", errors="replace") for p in paths
            if Path(p).exists()]


def _by_doi(dois: list[str], search_epmc, batch: int = 40) -> list[Paper]:
    papers: list[Paper] = []
    for start in range(0, len(dois), batch):
        chunk = dois[start:start + batch]
        query = " OR ".join(f'DOI:"{d}"' for d in chunk)
        papers.extend(search_epmc(query, max_results=len(chunk)))
    return papers


def resolve(texts: Iterable[str], *, domain: str = "emfportal", api_key: str = "",
            email: str = "", max_results: int = 500,
            fetcher_text: Callable[[str, dict[str, Any]], str] | None = None,
            search_epmc: Callable[..., list[Paper]] | None = None,
            cache_dir: str = "data/cache/pubmed") -> list[Paper]:
    """Identifiants EMF-Portal -> notices complètes issues de PubMed / Europe PMC."""
    pmids: list[str] = []
    dois: list[str] = []
    for text in texts:
        page_pmids, page_dois = extract_ids(text)
        pmids += [p for p in page_pmids if p not in pmids]
        dois += [d for d in page_dois if d not in dois]
    papers = pubmed.fetch_records(pmids[:max_results], api_key=api_key, email=email,
                                  domain=domain, fetcher_text=fetcher_text,
                                  cache_dir=cache_dir)
    known = {p.doi.lower() for p in papers if p.doi}
    if search_epmc is not None:
        rest = [d for d in dois if d not in known][:max_results]
        papers += _by_doi(rest, search_epmc)
    for paper in papers:
        paper.extra.setdefault("via", "emf-portal")
    return papers
