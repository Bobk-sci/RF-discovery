"""Collecte OpenAlex — filet de découverte, pas source de métadonnées.

OpenAlex (≈250 millions de notices, sans clé d'accès) couvre des revues qu'aucun des
deux filets actuels n'indexe : PubMed s'arrête à la biomédecine, Europe PMC aux
sciences du vivant. Les revues d'ingénierie, de dosimétrie, de physique appliquée et
les revues nationales y échappent — et c'est précisément là que paraît une partie de
la littérature CEM-RF.

**Pourquoi seulement les identifiants.** OpenAlex ne publie pas le résumé en clair : il
le distribue sous forme d'« index inversé » (mot -> positions), pour des raisons de
droits. Le reconstruire donnerait un texte dont la ponctuation et les espaces ne sont
plus ceux de l'original — donc plus un résumé « recopié mot pour mot ». On applique
donc à OpenAlex la règle déjà retenue pour EMF-Portal : n'en retenir que **PMID et
DOI**, et aller chercher titre, résumé et descripteurs auprès de PubMed / Europe PMC
(voir ``collect.resolve``). Si OpenAlex devient injoignable, l'étape rend zéro article.

``mailto`` est le paramètre de courtoisie d'OpenAlex (« polite pool ») : il n'est
transmis que si l'appelant le fournit explicitement, jamais codé en dur.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from collect.cache import get_json
from collect.europepmc import Paper
from collect.resolve import by_ids

Fetcher = Callable[[str, dict[str, Any]], Any]
_BASE = "https://api.openalex.org/works"
_MAX_PAGE = 200


def _ids(rec: dict[str, Any]) -> tuple[str, str]:
    """(PMID, DOI) d'une notice OpenAlex ; les deux arrivent sous forme d'URL."""
    ids = rec.get("ids") or {}
    pmid = str(ids.get("pmid") or "").rstrip("/").rsplit("/", 1)[-1]
    doi = str(ids.get("doi") or rec.get("doi") or "")
    doi = doi.lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
    return (pmid if pmid.isdigit() else ""), doi


def _page(term: str, cursor: str, annee_min: int, mailto: str,
          per_page: int) -> dict[str, Any]:
    """Paramètres d'une page de résultats pour un terme d'exposition."""
    filtres = [f"title_and_abstract.search:{term}"]
    if annee_min:
        filtres.append(f"from_publication_date:{annee_min}-01-01")
    params: dict[str, Any] = {"filter": ",".join(filtres), "per-page": per_page,
                              "cursor": cursor}
    if mailto:
        params["mailto"] = mailto
    return params


def search_ids(terms: Iterable[str], *, annee_min: int = 0, per_term: int = 400,
               max_results: int = 4000, mailto: str = "",
               fetcher: Fetcher | None = None,
               cache_dir: str = "data/cache/openalex") -> tuple[list[str], list[str]]:
    """Identifiants trouvés pour chaque terme RF : (PMID, DOI), dédupliqués, ordre stable.

    Une requête par terme : OpenAlex n'accepte pas la même algèbre booléenne
    qu'Europe PMC, et une requête par terme reste déterministe et lisible dans le cache.
    """
    fetch = fetcher or (lambda u, p: get_json(u, p, cache_dir=cache_dir))
    pmids: dict[str, None] = {}
    dois: dict[str, None] = {}
    for term in terms:
        cursor, pris = "*", 0
        while pris < per_term and len(pmids) + len(dois) < max_results:
            params = _page(term, cursor, annee_min, mailto,
                           min(_MAX_PAGE, per_term - pris))
            try:
                data = fetch(_BASE, params) or {}
            except Exception:          # source indisponible : on n'invente rien
                break
            results = data.get("results") or []
            for rec in results:
                pmid, doi = _ids(rec)
                if pmid:
                    pmids.setdefault(pmid, None)
                elif doi:
                    dois.setdefault(doi, None)
            pris += len(results)
            cursor = str((data.get("meta") or {}).get("next_cursor") or "")
            if not results or not cursor:
                break
    return list(pmids), list(dois)


def resolve(terms: Iterable[str], *, annee_min: int = 0, domain: str = "openalex",
            api_key: str = "", email: str = "", mailto: str = "",
            per_term: int = 400, max_results: int = 4000,
            fetcher: Fetcher | None = None,
            fetcher_text: Callable[[str, dict[str, Any]], str] | None = None,
            search_epmc: Callable[..., list[Paper]] | None = None,
            cache_dir: str = "data/cache/pubmed") -> list[Paper]:
    """Termes RF -> identifiants OpenAlex -> notices complètes PubMed / Europe PMC."""
    pmids, dois = search_ids(terms, annee_min=annee_min, per_term=per_term,
                             max_results=max_results, mailto=mailto, fetcher=fetcher)
    return by_ids(pmids, dois, via="openalex", domain=domain, api_key=api_key,
                  email=email, max_results=max_results, fetcher_text=fetcher_text,
                  search_epmc=search_epmc, cache_dir=cache_dir)
