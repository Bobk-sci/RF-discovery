"""Ingestion CTD → graphe DuckDB, automatisée (téléchargement direct, aucun fichier manuel).

Stratégie (modèle ABC de Swanson) : le substrat PubTator fournit les entités **B** liées à
l'exposition RF (**A**) ; CTD prolonge ces entités vers les maladies/voies (**C**) avec des
relations curées et datées. On ne garde donc que le **voisinage** des entités déjà
présentes — sinon le graphe complet CTD (millions d'arêtes) rendrait le scoring impossible.

Deux passes en flux :
1. chem-gène / gène-maladie / chimique-maladie : ligne gardée si une extrémité est déjà
   connue (une expansion d'un cran autour des entités RF).
2. gène→voie : ajoute la charpente mécanistique pour les gènes retenus.

Usage : ``python -m ingest_ctd --db data/graph.duckdb``
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from collect import ctd
from graph.schema import connect
from graph.store import upsert
from normalize.ctd import (
    Accumulator,
    add_chem_disease,
    add_chem_gene,
    add_gene_disease,
    add_gene_pathway,
)

ROOT = Path(__file__).resolve().parents[1]


def _existing_ids(con) -> set[str]:
    rows = con.execute("SELECT node_id FROM nodes").fetchall()
    return {r[0] for r in rows}


def _touching(rows, seeds: set[str], fields: tuple[str, ...], prefixer):
    """Ne laisse passer que les lignes dont une extrémité est déjà connue."""
    for r in rows:
        if any(prefixer(f, r.get(f, "")) in seeds for f in fields):
            yield r


def _ident(field: str, value: str) -> str:
    from normalize.ctd import mesh

    return value.strip() if field == "GeneID" else mesh(value)


def ingest_ctd(
    db_path: str | Path,
    *,
    cache_dir: str = "data/cache/ctd",
    max_rows: int | None = None,
    offline_files: dict[str, str] | None = None,
) -> dict:
    """Télécharge (ou lit) les dumps CTD et enrichit le graphe autour des entités connues."""
    con = connect(db_path)
    seeds = _existing_ids(con)
    if not seeds:
        con.close()
        return {"error": "graphe vide : lancer d'abord la collecte PubTator", "n_edges": 0}

    def rows_for(name: str):
        path = (offline_files or {}).get(name) or ctd.download(name, cache_dir=cache_dir)
        return ctd.iter_rows(path, limit=max_rows)

    acc = Accumulator()
    counts: dict[str, int] = {}
    counts["chem_gene"] = add_chem_gene(
        acc, _touching(rows_for("chem_gene"), seeds, ("ChemicalID", "GeneID"), _ident))
    counts["gene_disease"] = add_gene_disease(
        acc, _touching(rows_for("gene_disease"), seeds, ("GeneID", "DiseaseID"), _ident))
    counts["chem_disease"] = add_chem_disease(
        acc, _touching(rows_for("chem_disease"), seeds, ("ChemicalID", "DiseaseID"), _ident))
    genes = {nid for nid, n in acc.nodes.items() if n.node_type == "Gene"} | seeds
    counts["gene_pathway"] = add_gene_pathway(
        acc, _touching(rows_for("gene_pathway"), genes, ("GeneID",), _ident))

    upsert(con, list(acc.nodes.values()), list(acc.edges.values()))
    total_nodes = (con.execute("SELECT count(*) FROM nodes").fetchone() or (0,))[0]
    total_edges = (con.execute("SELECT count(*) FROM edges").fetchone() or (0,))[0]
    con.close()
    return {"rows_kept": counts, "ctd_nodes": len(acc.nodes), "ctd_edges": len(acc.edges),
            "graph_nodes": int(total_nodes), "graph_edges": int(total_edges)}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description="Ingestion CTD → graphe DuckDB")
    ap.add_argument("--db", default=str(ROOT / "data" / "graph.duckdb"))
    ap.add_argument("--cache-dir", default="data/cache/ctd")
    ap.add_argument("--max-rows", type=int, default=None,
                    help="borne le nombre de lignes lues par fichier (tests/démo)")
    args = ap.parse_args()
    print(json.dumps(ingest_ctd(args.db, cache_dir=args.cache_dir,
                                max_rows=args.max_rows), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
