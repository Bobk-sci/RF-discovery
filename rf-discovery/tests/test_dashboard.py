"""Dashboard GitHub Pages : rendu HTML statique depuis DuckDB (M10)."""
from __future__ import annotations

import json
import re

from graph.schema import connect
from report.dashboard import build_dashboard, fetch_dashboard_data


def _populate(db):
    con = connect(db)
    con.executemany("INSERT INTO nodes (node_id, node_type, degree) VALUES (?, ?, ?)",
                    [("EXP0", "Exposure", 3), ("PHEN0", "Phenotype", 2),
                     ("GENE0", "Gene", 4), ("PATH0", "Pathway", 2)])
    con.executemany(
        "INSERT INTO edges (source_id, target_id, predicate, first_year, n_papers) "
        "VALUES (?, ?, ?, 2005, 1)",
        [("EXP0", "GENE0", "AFFECTS"), ("GENE0", "PATH0", "PARTICIPATES_IN")])
    con.execute("INSERT INTO runs (run_date, n_new_papers, n_new_edges, n_candidates, "
                "status, error, duration_s) VALUES ('2025-01-06', 0, 2, 2, 'ok', NULL, 1.5)")
    con.executemany(
        "INSERT INTO candidates (run_date, a_id, c_id, metapath, dwpc, z_score, p_value, "
        "embed_score, novelty_z, burst_score, composite_rank, llm_explanation, human_verdict)"
        " VALUES ('2025-01-06', ?, ?, 'Exposure -> Phenotype', 0.5, ?, 0.01, 0.2, ?, 0.3, ?, "
        "NULL, ?)",
        [("EXP0", "PHEN0", 3.1, 1.4, 1, "plausible"),
         ("EXP0", "GENE0", 2.0, 0.9, 2, None)])
    con.close()


def test_fetch_counts_verdicts(tmp_path):
    db = tmp_path / "d.duckdb"
    _populate(db)
    con = connect(db)
    data = fetch_dashboard_data(con)
    con.close()
    assert data["latest"] is not None
    assert data["total_candidates"] == 2
    assert data["verdicts"].get("plausible") == 1
    assert len(data["candidates"]) == 2


def test_render_html_is_self_contained(tmp_path):
    db = tmp_path / "d.duckdb"
    _populate(db)
    out = tmp_path / "site" / "index.html"
    con = connect(db)
    html = build_dashboard(con, out_path=out)
    con.close()
    assert out.exists()
    assert html.startswith("<!doctype html>")
    # aucune dépendance externe (script/style distants)
    assert "http://" not in html.split("<script>")[0] or "lang" in html  # entête ok
    assert "src=" not in html and "cdn" not in html.lower()
    # jetons tous remplacés
    assert "__GRAPH_JSON__" not in html and "__CANDS_ROWS__" not in html
    # contenus attendus
    assert "EXP0" in html and "PHEN0" in html and "plausible" in html
    assert "2025-01-06" in html


def test_embedded_graph_json_is_valid(tmp_path):
    db = tmp_path / "d.duckdb"
    _populate(db)
    con = connect(db)
    html = build_dashboard(con)
    con.close()
    match = re.search(r"const DATA = (\{.*?\});", html, re.DOTALL)
    assert match, "données du graphe introuvables"
    payload = json.loads(match.group(1))
    ids = {n["id"] for n in payload["nodes"]}
    assert {"EXP0", "PHEN0"} <= ids
    assert any(ln["kind"] == "candidate" for ln in payload["links"])
