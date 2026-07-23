"""Ingestion SemMedDB : parsing du dump, mapping, filtrage, persistance (M2–M3)."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from collect.semmeddb import iter_predications, parse_citations, parse_value_tuples
from graph.schema import connect
from graph.store import load_graph, powerlaw_slope
from ingest import ingest
from normalize.semmed import SemMedConfig, build_nodes_edges, normalize_cui

ROOT = Path(__file__).resolve().parents[1]
FIX = Path(__file__).resolve().parent / "fixtures"
CFG_ST = ROOT / "config" / "umls_semtypes.yaml"
CFG_MP = ROOT / "config" / "metapaths.yaml"


def test_value_scanner_handles_quotes_and_commas():
    seg = " (1,'a, b','O\\'Neil',NULL),(2,'x','y',3)"
    rows = list(parse_value_tuples(seg))
    assert rows[0] == ["1", "a, b", "O'Neil", None]
    assert rows[1] == ["2", "x", "y", "3"]


def test_iter_predications_and_citations():
    preds = list(iter_predications(FIX / "semmed_predication.sql"))
    assert len(preds) == 6
    assert preds[0].predicate == "INHIBITS"
    years = parse_citations(FIX / "semmed_citations.sql")
    assert years["23000001"] == 2005 and years["23000006"] == 2018


def test_normalize_cui_prefers_entrez_for_genes():
    assert normalize_cui("C0017337|1017", "Gene") == "1017"
    assert normalize_cui("C0018670", "Disease") == "C0018670"


def test_build_filters_hubs_negation_and_out_of_set():
    cfg = SemMedConfig.load(CFG_ST, CFG_MP)
    preds = list(iter_predications(FIX / "semmed_predication.sql"))
    years = parse_citations(FIX / "semmed_citations.sql")
    nodes, edges = build_nodes_edges(preds, years, cfg)
    preds_kept = {(e.source_id, e.predicate, e.target_id) for e in edges}
    # gardés : INHIBITS (gène Entrez), PARTICIPATES_IN, ASSOCIATED_WITH
    assert ("1017", "INHIBITS", "C0018670") in preds_kept
    assert ("1017", "PARTICIPATES_IN", "C0032131") in preds_kept
    assert ("C0000010", "ASSOCIATED_WITH", "C0002395") in preds_kept
    # rejetés : NEG_*, PROCESS_OF (hors ensemble), et l'arête via le hub C0007634
    assert not any(p == "NEG_STIMULATES" for _, p, _ in preds_kept)
    assert not any(p == "PROCESS_OF" for _, p, _ in preds_kept)
    assert all("C0007634" not in (s, o) for s, _, o in preds_kept)
    # année héritée des citations
    inhibits = next(e for e in edges if e.predicate == "INHIBITS")
    assert inhibits.first_year == 2005


def test_ingest_persists_and_recomputes_degrees(tmp_path):
    db = tmp_path / "graph.duckdb"
    summary = ingest(FIX / "semmed_predication.sql", db,
                     citations_path=FIX / "semmed_citations.sql")
    assert summary["n_edges"] == 3
    con = connect(db)
    nodes, edges = load_graph(con)
    # le nœud gène '1017' porte un degré = 2 (INHIBITS + PARTICIPATES_IN)
    deg = con.execute("SELECT degree FROM nodes WHERE node_id = '1017'").fetchone()[0]
    con.close()
    assert deg == 2
    assert len(edges) == 3 and any(n.node_id == "1017" for n in nodes)


def test_powerlaw_slope_negative_on_heavy_tail():
    rng = np.random.default_rng(0)
    degrees = rng.zipf(2.2, size=5000)
    vals, counts = np.unique(degrees, return_counts=True)
    dist = list(zip(vals.tolist(), counts.tolist(), strict=False))
    assert powerlaw_slope(dist) < 0
