"""Collecte (fetcher de fixture, jamais le réseau) + normalisation (M1–M3)."""
from __future__ import annotations

from collect.europepmc import build_query, search
from collect.pubtator import Annotation, parse_biocjson
from normalize.dedupe import dedupe, load_seen
from normalize.entities import (
    cooccurrence_edges,
    edges_from_relations,
    nodes_from_annotations,
)


def _fixture_fetch(_url, _params):
    return {"resultList": {"result": [
        {"pmid": "1", "doi": "10.1/x", "title": "A", "abstractText": "aa",
         "pubYear": "2020", "journalTitle": "J", "isOpenAccess": "Y"},
        {"pmid": "2", "title": "B", "pubYear": "2021"},
        {"title": "no id, ignoré"},
    ]}}


def test_search_parses_fixture():
    papers = search("q", domain="rf_in_vivo", fetcher=_fixture_fetch)
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


def test_build_query_bridge_never_has_rf_terms():
    q = build_query("neurodevelopment", ["GSM", "SAR"], rf_terms_allowed=False)
    assert "GSM" not in q and q == "neurodevelopment"
    q2 = build_query("brain", ["GSM"], rf_terms_allowed=True)
    assert "GSM" in q2


def test_cooccurrence_links_co_mentioned_entities():
    # Gène + Maladie + Chimique co-cités dans un article, SANS relation explicite.
    anns = [
        Annotation("9", "627", "Gene", "Bdnf", 2016),
        Annotation("9", "MESH:D001321", "Disease", "autism", 2016),
        Annotation("9", "MESH:C1", "Chemical", "compound", 2016),
    ]
    edges = cooccurrence_edges(anns, {"9": 2016})
    triples = {(e.source_id, e.predicate, e.target_id) for e in edges}
    assert ("627", "ASSOCIATED_WITH", "MESH:D001321") in triples   # Gene->Disease
    assert ("MESH:C1", "AFFECTS", "627") in triples                # Chemical->Gene
    assert ("MESH:C1", "CAUSES", "MESH:D001321") in triples        # Chemical->Disease
    assert all(e.first_year == 2016 for e in edges)


def test_cooccurrence_skips_dense_papers():
    anns = [Annotation("9", f"G{i}", "Gene", "g", 2016) for i in range(40)]
    anns.append(Annotation("9", "MESH:D1", "Disease", "d", 2016))
    assert cooccurrence_edges(anns, {"9": 2016}, max_entities=30) == []


def test_dedupe_idempotent(tmp_path):
    papers = search("q", fetcher=_fixture_fetch)
    seen = load_seen(tmp_path / "seen.json")
    fresh1, seen = dedupe(papers, seen)
    fresh2, seen = dedupe(papers, seen)
    assert len(fresh1) == 2
    assert fresh2 == []  # rerun -> 0 ligne (critère M1)


def test_pubtator_parse_and_entity_mapping():
    doc = {"pmid": "9", "year": 2015, "passages": [{"annotations": [
        {"text": "Bdnf", "infons": {"identifier": "627", "type": "Gene"}},
        {"text": "autism", "infons": {"identifier": "MESH:D001321", "type": "Disease"}},
        {"text": "?", "infons": {"identifier": "-", "type": "Gene"}},
    ]}], "relations": [
        {"infons": {"role1": "627", "role2": "MESH:D001321", "type": "associate"}}]}
    anns, rels = parse_biocjson(doc)
    assert len(anns) == 2  # l'annotation sans identifiant est ignorée
    nodes = nodes_from_annotations(anns)
    edges = edges_from_relations(rels, [n.node_id for n in nodes])
    assert {n.node_type for n in nodes} == {"Gene", "Disease"}
    assert edges[0].predicate == "ASSOCIATED_WITH"
    assert edges[0].first_year == 2015
