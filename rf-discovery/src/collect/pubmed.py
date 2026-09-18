"""Collecte PubMed via les E-utilities du NCBI (gratuit, clé d'API facultative).

Deux appels : ``esearch`` rend les PMID d'une requête, ``efetch`` rend les notices XML.
Europe PMC et PubMed ne se recouvrent pas complètement (indexation décalée, notices
« ahead of print ») : interroger les deux élargit réellement la moisson.

Le réseau est injectable (``fetcher_json`` / ``fetcher_text``) : les tests lisent des
fixtures XML, jamais le réseau. **Rien n'est inventé** : un champ absent de la notice
XML reste vide.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any
from xml.etree import ElementTree as ET

from collect.cache import get_json, get_text
from collect.europepmc import Paper

_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
_YEAR = re.compile(r"(1[89]\d{2}|20\d{2})")


def _params(extra: dict[str, Any], api_key: str, email: str) -> dict[str, Any]:
    params = {"db": "pubmed", "tool": "rf-discovery", **extra}
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    return params


def search_ids(query: str, *, max_results: int = 500, page_size: int = 200,
               fetcher_json: Callable[[str, dict[str, Any]], Any] | None = None,
               api_key: str = "", email: str = "",
               cache_dir: str = "data/cache/pubmed") -> list[str]:
    """PMID répondant à la requête (pagination ``retstart``, ordre PubMed conservé)."""
    fetch = fetcher_json or (lambda u, p: get_json(u, p, cache_dir=cache_dir))
    ids: list[str] = []
    while len(ids) < max_results:
        want = min(page_size, max_results - len(ids))
        extra = {"term": query, "retmode": "json", "retstart": len(ids), "retmax": want}
        data = fetch(f"{_EUTILS}/esearch.fcgi", _params(extra, api_key, email)) or {}
        batch = (data.get("esearchresult") or {}).get("idlist") or []
        ids.extend(str(i) for i in batch if str(i) not in ids)
        if not batch or len(batch) < want:
            break
    return ids[:max_results]


def _text(node: ET.Element | None) -> str:
    return "".join(node.itertext()).strip() if node is not None else ""


def _abstract(article: ET.Element) -> str:
    parts = []
    for chunk in article.findall(".//Abstract/AbstractText"):
        label = (chunk.get("Label") or "").strip()
        body = "".join(chunk.itertext()).strip()
        parts.append(f"{label}: {body}" if label else body)
    return "\n\n".join(p for p in parts if p)


def _year(article: ET.Element) -> int:
    for path in (".//JournalIssue/PubDate/Year", ".//JournalIssue/PubDate/MedlineDate",
                 ".//PubMedPubDate[@PubStatus='pubmed']/Year"):
        found = _YEAR.search(_text(article.find(path)))
        if found:
            return int(found.group(1))
    return 0


def _doi(article: ET.Element) -> str:
    for node in article.findall(".//ArticleId") + article.findall(".//ELocationID"):
        if (node.get("IdType") or node.get("EIdType") or "").lower() == "doi":
            return _text(node)
    return ""


def _descriptors(article: ET.Element) -> dict[str, Any]:
    """MeSH, types de publication et mots-clés d'auteur : descripteurs fournis par PubMed."""
    return {
        "mesh": [_text(n) for n in article.findall(".//MeshHeading/DescriptorName")],
        "types": [_text(n) for n in article.findall(".//PublicationType")],
        "keywords": [_text(n) for n in article.findall(".//KeywordList/Keyword")],
    }


def parse_pubmed_xml(xml_text: str, domain: str = "") -> list[Paper]:
    """Notices ``PubmedArticleSet`` -> ``Paper`` (recopie stricte des champs présents)."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    papers = []
    for article in root.findall(".//PubmedArticle"):
        pmid = _text(article.find(".//PMID"))
        if not pmid:
            continue
        papers.append(Paper(
            pmid=pmid,
            doi=_doi(article),
            title=_text(article.find(".//ArticleTitle")),
            abstract=_abstract(article),
            year=_year(article),
            journal=_text(article.find(".//Journal/Title")),
            domain=domain,
            source="pubmed",
            extra=_descriptors(article),
        ))
    return papers


def fetch_records(pmids: list[str], *, batch_size: int = 200,
                  fetcher_text: Callable[[str, dict[str, Any]], str] | None = None,
                  api_key: str = "", email: str = "", domain: str = "",
                  cache_dir: str = "data/cache/pubmed") -> list[Paper]:
    """Télécharge les notices par paquets et les convertit en ``Paper``."""
    fetch = fetcher_text or (lambda u, p: get_text(u, p, cache_dir=cache_dir))
    papers: list[Paper] = []
    for start in range(0, len(pmids), batch_size):
        chunk = pmids[start:start + batch_size]
        extra = {"id": ",".join(chunk), "retmode": "xml"}
        papers.extend(parse_pubmed_xml(
            fetch(f"{_EUTILS}/efetch.fcgi", _params(extra, api_key, email)) or "", domain))
    return papers


def search(query: str, *, max_results: int = 500, domain: str = "",
           fetcher_json: Callable[[str, dict[str, Any]], Any] | None = None,
           fetcher_text: Callable[[str, dict[str, Any]], str] | None = None,
           api_key: str = "", email: str = "",
           cache_dir: str = "data/cache/pubmed") -> list[Paper]:
    """Recherche PubMed complète : ``esearch`` puis ``efetch``."""
    ids = search_ids(query, max_results=max_results, fetcher_json=fetcher_json,
                     api_key=api_key, email=email, cache_dir=cache_dir)
    if not ids:
        return []
    return fetch_records(ids, fetcher_text=fetcher_text, api_key=api_key, email=email,
                         domain=domain, cache_dir=cache_dir)
