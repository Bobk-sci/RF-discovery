"""Harvester : orchestration Europe PMC + PubTator → graphe DuckDB (fixtures, hors réseau)."""
from __future__ import annotations

from pathlib import Path

from graph.schema import connect
from harvest import harvest

FIX = Path(__file__).resolve().parent / "fixtures"
DOMAINS = FIX / "domains_small.yaml"

# PMIDs renvoyés par domaine + année de publication (Europe PMC).
_EPMC = {
    "neurodevelopment": [("200", 2019), ("201", 2019)],
    "default": [("100", 2016), ("101", 2016)],
}
# Annotations/relations PubTator par PMID.
_ANN = {
    "100": ("627", "Bdnf", "Gene", "MESH:D001321", "autism", "Disease"),
    "101": ("348", "APOE", "Gene", "MESH:D000544", "Alzheimer", "Disease"),
    "200": ("1017", "CDKN2A", "Gene", "MESH:D008607", "intoxication", "Disease"),
    "201": ("351", "APP", "Gene", "MESH:D002658", "development", "Disease"),
}


def _epmc_fetcher(_url, params):
    key = "neurodevelopment" if "neurodevelopment" in params["query"] else "default"
    results = [{"pmid": pmid, "title": f"T{pmid}", "abstractText": "abstract",
                "pubYear": str(year), "journalTitle": "J"} for pmid, year in _EPMC[key]]
    return {"resultList": {"result": results}}


def _pubtator_fetcher(_url, params):
    docs = []
    for pmid in params["pmids"].split(","):
        if pmid not in _ANN:
            continue
        g_id, g_txt, g_ty, d_id, d_txt, d_ty = _ANN[pmid]
        docs.append({"pmid": pmid, "passages": [{"annotations": [
            {"text": g_txt, "infons": {"identifier": g_id, "type": g_ty}},
            {"text": d_txt, "infons": {"identifier": d_id, "type": d_ty}},
        ]}], "relations": [
            {"infons": {"role1": g_id, "role2": d_id, "type": "associate"}}]})
    return docs


def test_harvest_builds_graph_from_fixtures(tmp_path):
    db = tmp_path / "graph.duckdb"
    res = harvest(db, domains_path=DOMAINS, seen_path=tmp_path / "seen.json",
                  epmc_fetcher=_epmc_fetcher, pubtator_fetcher=_pubtator_fetcher,
                  cache_dir=str(tmp_path / "cache"))
    assert res.n_papers == 4
    assert res.per_domain == {"rf_in_vitro_test": 2, "neurodevelopment_test": 2}
    assert res.n_nodes == 8 and res.n_edges == 4
    con = connect(db)
    assert con.execute("SELECT count(*) FROM papers").fetchone()[0] == 4
    # arête Gene->Disease, année héritée d'Europe PMC (2016 pour pmid 100)
    fy = con.execute("SELECT first_year FROM edges WHERE source_id = '627'").fetchone()[0]
    deg = con.execute("SELECT degree FROM nodes WHERE node_id = '627'").fetchone()[0]
    con.close()
    assert fy == 2016 and deg == 1


def test_harvest_rerun_is_idempotent(tmp_path):
    db = tmp_path / "graph.duckdb"
    seen = tmp_path / "seen.json"
    kw = dict(domains_path=DOMAINS, seen_path=seen, epmc_fetcher=_epmc_fetcher,
              pubtator_fetcher=_pubtator_fetcher, cache_dir=str(tmp_path / "cache"))
    first = harvest(db, **kw)
    second = harvest(db, **kw)  # seen.json -> aucun nouvel article
    assert first.n_papers == 4
    assert second.n_papers == 0


def test_harvest_survives_pubtator_error_and_skips_non_numeric(tmp_path):
    # Europe PMC renvoie aussi un ID preprint non numérique (PPR/PMC) ; PubTator plante.
    def epmc(_url, _params):
        return {"resultList": {"result": [
            {"pmid": "100", "title": "ok", "pubYear": "2016"},
            {"id": "PMC999", "title": "preprint sans PMID", "pubYear": "2020"}]}}

    def failing_pubtator(_url, params):
        assert "PMC999" not in params["pmids"], "les non-numériques ne doivent pas être envoyés"
        raise RuntimeError("400 Bad Request")

    res = harvest(tmp_path / "g.duckdb", domains_path=DOMAINS, seen_path=tmp_path / "s.json",
                  epmc_fetcher=epmc, pubtator_fetcher=failing_pubtator,
                  cache_dir=str(tmp_path / "c"))
    # le run ne plante pas : articles collectés, graphe vide car PubTator a échoué
    assert res.n_papers == 2 and res.n_nodes == 0 and res.n_edges == 0


def test_run_real_mode_on_harvested_graph(tmp_path):
    # Le mode réel (synthetic=False) charge le graphe collecté et score sans planter,
    # même si ce petit graphe de fixture ne produit aucune paire candidate.
    from run import run

    db = tmp_path / "graph.duckdb"
    harvest(db, domains_path=DOMAINS, seen_path=tmp_path / "seen.json",
            epmc_fetcher=_epmc_fetcher, pubtator_fetcher=_pubtator_fetcher,
            cache_dir=str(tmp_path / "cache"))
    result = run(str(db), synthetic=False, seed=0, n_perm=5, top=5)
    assert "gate" in result and "n_candidates" in result
