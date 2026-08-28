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
    mesh,
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


def _already_ingested(con) -> bool:
    """CTD est déjà dans le graphe si la charpente gène→voie est présente.

    On se fonde sur les ARÊTES, pas sur les libellés : baser la décision sur les noms
    créait une boucle (noms absents → réingestion complète → dépassement de la limite de
    6 h d'Actions → rien de committé → noms toujours absents). Les noms sont restaurés
    séparément par ``backfill_names``, qui ne lit que de petits fichiers de vocabulaire.
    """
    row = con.execute(
        "SELECT count(*) FROM edges WHERE predicate = 'PARTICIPATES_IN'").fetchone()
    return bool(row and row[0] > 0)


def backfill_names(con, cache_dir: str = "data/cache/ctd",
                   offline_vocab: dict[str, str] | None = None) -> int:
    """Renseigne les noms manquants depuis les fichiers de vocabulaire CTD (quelques Mo).

    Récupérer les libellés ne doit pas coûter la relecture des fichiers de relations
    (des heures) : les vocabulaires suffisent et se lisent en quelques secondes.
    """
    missing = {r[0] for r in con.execute(
        "SELECT node_id FROM nodes WHERE name IS NULL OR name = ''").fetchall()}
    if not missing:
        return 0
    updates: list[tuple[str, str]] = []
    for key, (filename, id_col, name_col) in ctd.VOCAB_FILES.items():
        local = (offline_vocab or {}).get(key)
        try:
            path: str | Path = local or ctd.download(filename, cache_dir=cache_dir)
            rows = list(ctd.iter_rows(path))
        except Exception as exc:      # un vocabulaire indisponible ne doit pas tuer le run
            logging.warning("vocabulaire CTD %s ignoré : %s", key, exc)
            continue
        for row in rows:
            raw, name = row.get(id_col, "").strip(), row.get(name_col, "").strip()
            if not raw or not name:
                continue
            for candidate in {raw, mesh(raw), raw.split(":")[-1]}:
                if candidate in missing:
                    updates.append((name, candidate))
                    missing.discard(candidate)
                    break
    if updates:
        con.executemany("UPDATE nodes SET name = ? WHERE node_id = ?", updates)
    return len(updates)


def ingest_ctd(
    db_path: str | Path,
    *,
    cache_dir: str = "data/cache/ctd",
    max_rows: int | None = None,
    offline_files: dict[str, str] | None = None,
    offline_vocab: dict[str, str] | None = None,
    force: bool = False,
) -> dict:
    """Télécharge (ou lit) les dumps CTD et enrichit le graphe autour des entités connues.

    Les données CTD évoluent au plus mensuellement : si la charpente est déjà présente,
    on saute l'étape (elle coûte des heures de lecture) sauf ``force=True``.
    """
    con = connect(db_path)
    seeds = _existing_ids(con)
    if not seeds:
        con.close()
        return {"error": "graphe vide : lancer d'abord la collecte PubTator", "n_edges": 0}
    if _already_ingested(con) and not force:
        filled = backfill_names(con, cache_dir=cache_dir, offline_vocab=offline_vocab)
        con.close()
        return {"skipped": "CTD déjà ingéré (--force pour rafraîchir)",
                "names_backfilled": filled}

    def rows_for(name: str, prefilter=None):
        path = (offline_files or {}).get(name) or ctd.download(name, cache_dir=cache_dir)
        return ctd.iter_rows(path, limit=max_rows, prefilter=prefilter)

    direct = ctd.has_direct_evidence   # écarte les inférences avant de construire le dict
    acc = Accumulator()
    counts: dict[str, int] = {}
    counts["chem_gene"] = add_chem_gene(
        acc, _touching(rows_for("chem_gene"), seeds, ("ChemicalID", "GeneID"), _ident))
    counts["gene_disease"] = add_gene_disease(
        acc, _touching(rows_for("gene_disease", direct), seeds,
                       ("GeneID", "DiseaseID"), _ident))
    counts["chem_disease"] = add_chem_disease(
        acc, _touching(rows_for("chem_disease", direct), seeds,
                       ("ChemicalID", "DiseaseID"), _ident))
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
    ap.add_argument("--force", action="store_true",
                    help="réingère CTD même si la charpente est déjà présente")
    args = ap.parse_args()
    print(json.dumps(ingest_ctd(args.db, cache_dir=args.cache_dir, max_rows=args.max_rows,
                                force=args.force), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
