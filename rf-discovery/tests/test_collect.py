"""Collecte Europe PMC et déduplication — fetcher de fixture, jamais le réseau."""
from __future__ import annotations

from collect.europepmc import build_query, search
from normalize.dedupe import dedupe, load_seen


def _fixture_fetch(_url, _params):
    return {"resultList": {"result": [
        {"pmid": "1", "doi": "10.1/x", "title": "A", "abstractText": "aa",
         "pubYear": "2020", "journalTitle": "J", "isOpenAccess": "Y"},
        {"pmid": "2", "title": "B", "pubYear": "2021"},
        {"title": "sans identifiant, ignoré"},
    ]}}


def test_search_parses_fixture():
    papers = search("q", domain="rf", fetcher=_fixture_fetch)
    assert [p.pmid for p in papers] == ["1", "2"]
    assert papers[0].oa_status == "open"


def test_search_paginates_with_cursormark():
    pages = {
        "*": {"resultList": {"result": [{"pmid": "1", "pubYear": "2020"}]},
              "nextCursorMark": "C1"},
        "C1": {"resultList": {"result": [{"pmid": "2", "pubYear": "2021"}]},
               "nextCursorMark": "C1"},  # curseur identique -> arrêt
    }
    papers = search("q", fetcher=lambda _u, p: pages[p["cursorMark"]], max_results=100)
    assert [p.pmid for p in papers] == ["1", "2"]


def test_search_respects_max_results():
    page = {"resultList": {"result": [{"pmid": "1"}, {"pmid": "2"}, {"pmid": "3"}]}}
    papers = search("q", fetcher=lambda _u, _p: page, max_results=2)
    assert len(papers) == 2


def test_build_query_combine_ou_non_les_termes_rf():
    q = build_query("neurodevelopment", ["GSM", "SAR"], rf_terms_allowed=False)
    assert "GSM" not in q and q == "neurodevelopment"
    assert "GSM" in build_query("brain", ["GSM"], rf_terms_allowed=True)


def test_dedupe_idempotent(tmp_path):
    papers = search("q", fetcher=_fixture_fetch)
    seen = load_seen(tmp_path / "seen.json")
    fresh1, seen = dedupe(papers, seen)
    fresh2, seen = dedupe(papers, seen)
    assert len(fresh1) == 2
    assert fresh2 == []          # un rerun n'ajoute aucune ligne
