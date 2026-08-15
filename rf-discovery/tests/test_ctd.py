"""Ingestion CTD : parsing en flux, mapping, datation PMID, restriction au voisinage."""
from __future__ import annotations

from pathlib import Path

from collect.ctd import iter_rows
from graph.schema import connect
from ingest_ctd import ingest_ctd
from normalize.ctd import (
    Accumulator,
    add_chem_gene,
    add_gene_disease,
    add_gene_pathway,
    mesh,
)
from normalize.pmid_year import first_year, year_from_pmid

FIX = Path(__file__).resolve().parent / "fixtures"
FILES = {
    "chem_gene": str(FIX / "ctd_chem_gene.tsv"),
    "gene_disease": str(FIX / "ctd_gene_disease.tsv"),
    "chem_disease": str(FIX / "ctd_chem_disease.tsv"),
    "gene_pathway": str(FIX / "ctd_gene_pathway.tsv"),
}


def test_iter_rows_reads_header_from_comments():
    rows = list(iter_rows(FILES["chem_gene"]))
    assert len(rows) == 3
    assert rows[0]["ChemicalID"] == "C006780" and rows[0]["GeneID"] == "627"


def test_year_from_pmid_is_monotonic_and_plausible():
    assert year_from_pmid(22000000) < year_from_pmid(31000000)
    assert 2011 <= year_from_pmid(22000000) <= 2013     # PMID 22M ≈ 2012
    assert 2019 <= year_from_pmid(31000000) <= 2021     # PMID 31M ≈ 2019-2020
    assert year_from_pmid("pas un nombre") == 0
    assert first_year("31000000|22000000") == year_from_pmid(22000000)  # la plus ancienne


def test_mesh_prefix_aligns_with_pubtator():
    assert mesh("C006780") == "MESH:C006780"
    assert mesh("MESH:D001321") == "MESH:D001321"


def test_chem_gene_predicates_and_organism_filter():
    acc = Accumulator()
    kept = add_chem_gene(acc, iter_rows(FILES["chem_gene"]))
    assert kept == 2                     # la ligne Danio rerio est écartée
    preds = {(e.source_id, e.predicate, e.target_id) for e in acc.edges.values()}
    assert ("MESH:C006780", "STIMULATES", "627") in preds   # increases
    assert ("MESH:D007854", "INHIBITS", "627") in preds     # decreases


def test_gene_disease_keeps_direct_evidence_only():
    acc = Accumulator()
    kept = add_gene_disease(acc, iter_rows(FILES["gene_disease"]))
    assert kept == 1                     # la ligne inférée (sans DirectEvidence) est écartée
    edge = next(iter(acc.edges.values()))
    assert (edge.source_id, edge.predicate, edge.target_id) == (
        "627", "ASSOCIATED_WITH", "MESH:D001321")
    assert edge.first_year >= 2019       # PMID 31M -> ~2019+


def test_gene_pathway_is_undated_scaffold():
    acc = Accumulator()
    add_gene_pathway(acc, iter_rows(FILES["gene_pathway"]))
    edge = next(iter(acc.edges.values()))
    assert edge.predicate == "PARTICIPATES_IN" and edge.first_year == 0
    assert acc.nodes["KEGG:hsa04722"].node_type == "Pathway"


def _seed_db(tmp_path):
    db = tmp_path / "g.duckdb"
    con = connect(db)
    con.executemany("INSERT INTO nodes (node_id, node_type, degree) VALUES (?, ?, 0)",
                    [("627", "Gene"), ("RF_EMF", "Exposure")])
    con.close()
    return db


def test_ingest_expands_around_existing_entities(tmp_path):
    db = _seed_db(tmp_path)
    out = ingest_ctd(db, offline_files=FILES)
    assert out["ctd_edges"] > 0
    con = connect(db)
    types = dict(con.execute("SELECT node_type, count(*) FROM nodes GROUP BY 1").fetchall())
    preds = dict(con.execute("SELECT predicate, count(*) FROM edges GROUP BY 1").fetchall())
    deg = con.execute("SELECT degree FROM nodes WHERE node_id = '627'").fetchone()[0]
    con.close()
    # le maillon manquant Gene->Pathway est enfin présent
    assert types.get("Pathway", 0) >= 1 and preds.get("PARTICIPATES_IN", 0) >= 1
    assert types.get("Disease", 0) >= 1 and preds.get("ASSOCIATED_WITH", 0) >= 1
    assert deg >= 3                      # le gène amorce est bien connecté


def test_prefilter_skips_inferred_rows():
    from collect.ctd import has_direct_evidence

    rows = list(iter_rows(FILES["gene_disease"], prefilter=has_direct_evidence))
    assert len(rows) == 1 and rows[0]["DirectEvidence"] == "marker/mechanism"


def test_second_ingest_is_skipped_unless_forced(tmp_path):
    db = _seed_db(tmp_path)
    first = ingest_ctd(db, offline_files=FILES)
    assert first["ctd_edges"] > 0
    # la charpente gène→voie est là : on ne relit pas des heures de fichiers
    assert "skipped" in ingest_ctd(db, offline_files=FILES)
    assert "skipped" not in ingest_ctd(db, offline_files=FILES, force=True)


def test_ingest_refuses_empty_graph(tmp_path):
    db = tmp_path / "empty.duckdb"
    connect(db).close()
    assert ingest_ctd(db, offline_files=FILES)["n_edges"] == 0
