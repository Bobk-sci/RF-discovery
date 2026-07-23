"""Schéma DuckDB (M0) et orchestrateur bout-en-bout synthétique."""
from __future__ import annotations

from graph.schema import connect, init_empty
from run import run


def test_schema_creates_tables(tmp_path):
    db = tmp_path / "graph.duckdb"
    init_empty(db)
    con = connect(db)
    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    assert {"papers", "nodes", "edges", "candidates", "runs"} <= tables
    con.close()


def test_run_synthetic_end_to_end(tmp_path):
    db = tmp_path / "graph.duckdb"
    result = run(str(db), synthetic=True, seed=0, n_perm=15, top=10, out_dir=tmp_path)
    assert result["n_candidates"] > 0
    assert result["gate"]["passes_gate"] is True
    con = connect(db)
    n_runs = con.execute("SELECT count(*) FROM runs").fetchone()[0]
    n_edges = con.execute("SELECT count(*) FROM edges").fetchone()[0]
    con.close()
    assert n_runs == 1 and n_edges > 0
