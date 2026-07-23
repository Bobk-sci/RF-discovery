"""Ingestion SemMedDB → graphe DuckDB (M3).

Usage :
    python -m ingest --predications semmedVER43_R_PREDICATION.sql.gz \\
                     --citations   semmedVER43_R_CITATIONS.sql.gz \\
                     --db data/graph.duckdb

Les dumps SemMedDB s'obtiennent gratuitement auprès de la NLM sous licence UMLS
(https://lhncbc.nlm.nih.gov/ii/tools/SemRep_SemMedDB_SKR.html). Aucun accès réseau ici :
on lit des fichiers locaux en flux. Le corpus complet étant volumineux, ``--max`` permet
d'échantillonner ou de pré-filtrer en amont.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections.abc import Iterator
from pathlib import Path

from collect.semmeddb import Predication, iter_predications, parse_citations
from graph.schema import connect
from graph.store import degree_distribution, powerlaw_slope, upsert
from normalize.semmed import SemMedConfig, build_nodes_edges

ROOT = Path(__file__).resolve().parents[1]


def ingest(
    predications_path: str | Path,
    db_path: str | Path,
    *,
    citations_path: str | Path | None = None,
    semtypes_path: str | Path | None = None,
    metapaths_path: str | Path | None = None,
    max_predications: int | None = None,
) -> dict:
    """Charge un dump SemMedDB dans la base DuckDB et renvoie un résumé."""
    cfg = SemMedConfig.load(
        semtypes_path or ROOT / "config" / "umls_semtypes.yaml",
        metapaths_path or ROOT / "config" / "metapaths.yaml",
    )
    year_map = parse_citations(citations_path) if citations_path else {}
    preds: Iterator[Predication] = iter_predications(predications_path)
    if max_predications is not None:
        preds = itertools.islice(preds, max_predications)
    nodes, edges = build_nodes_edges(preds, year_map, cfg)
    con = connect(db_path)
    upsert(con, nodes, edges)
    dist = degree_distribution(con)
    con.close()
    return {
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "n_citations": len(year_map),
        "powerlaw_slope": powerlaw_slope(dist),
        "max_degree": max((d for d, _ in dist), default=0),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingestion SemMedDB → DuckDB")
    ap.add_argument("--predications", required=True, help="dump PREDICATION (.sql/.sql.gz/.tsv)")
    ap.add_argument("--citations", default=None, help="dump CITATIONS pour les années")
    ap.add_argument("--db", default=str(ROOT / "data" / "graph.duckdb"))
    ap.add_argument("--max", type=int, default=None, dest="max_predications")
    args = ap.parse_args()
    summary = ingest(args.predications, args.db, citations_path=args.citations,
                     max_predications=args.max_predications)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
