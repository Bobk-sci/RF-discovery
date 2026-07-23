"""Orchestrateur du pipeline (collecte → graphe → scoring → gate → digest).

Exécutable en mode ``--synthetic`` (aucun réseau) pour la CI et la démo : construit un
graphe temporel synthétique, franchit les étapes déterministes, écrit un digest markdown
et journalise le run dans DuckDB. Le mode réel (collecte via ``collect/``) réutilise
exactement les mêmes étages de scoring.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, date, datetime
from pathlib import Path

from graph.build import Edge, Node, build_graph
from graph.metapaths import MetaGraph, enumerate_metapaths
from graph.permute import dwpc_null
from graph.schema import connect
from report.digest import build_digest
from score.rank import rank_candidates
from synthetic import generate
from validate.timeslice import run_timeslice

ROOT = Path(__file__).resolve().parents[1]


def candidate_pairs(nodes, mg: MetaGraph, limit: int = 400) -> list[tuple[str, str]]:
    src = [n.node_id for n in nodes if n.node_type in mg.source_types]
    tgt = [n.node_id for n in nodes if n.node_type in mg.target_types]
    pairs = [(a, c) for a in src for c in tgt]
    return pairs[:limit]


def persist(con, nodes, edges, run_row: dict) -> None:
    con.execute("DELETE FROM nodes")
    con.executemany("INSERT INTO nodes (node_id, node_type, degree) VALUES (?, ?, 0)",
                    [(n.node_id, n.node_type) for n in nodes])
    con.execute("DELETE FROM edges")
    con.executemany(
        "INSERT INTO edges (source_id, target_id, predicate, first_year, n_papers) "
        "VALUES (?, ?, ?, ?, 1)",
        [(e.source_id, e.target_id, e.predicate, e.first_year) for e in edges])
    con.execute(
        "INSERT OR REPLACE INTO runs (run_date, n_new_papers, n_new_edges, n_candidates, "
        "status, error, duration_s) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (run_row["run_date"], 0, len(edges), run_row["n_candidates"],
         run_row["status"], run_row.get("error"), run_row["duration_s"]))


def run(db_path: str, *, synthetic: bool, seed: int = 0, n_perm: int = 50,
        top: int = 20) -> dict:
    t0 = time.time()
    cfg = ROOT / "config" / "metapaths.yaml"
    mg = MetaGraph.from_config(cfg)
    metapaths = enumerate_metapaths(mg)
    if synthetic:
        sg = generate(seed=seed)
        nodes, edges = sg.nodes, sg.edges
    else:  # pragma: no cover - chemin réseau, hors tests
        nodes, edges = _load_from_db(db_path)
    graph = build_graph(nodes, edges)
    pairs = candidate_pairs(nodes, mg)
    null = dwpc_null(graph, metapaths, pairs, n_permutations=n_perm, seed=seed)
    candidates = rank_candidates(graph, metapaths, pairs, null=null, seed=seed)
    gate = run_timeslice(nodes, edges, cfg, seed=seed)
    digest = build_digest(candidates, run_date=date.today(), top=top, gate=gate)
    _write_reports(digest, candidates, gate)
    con = connect(db_path)
    persist(con, nodes, edges, {
        "run_date": date.today(), "n_candidates": len(candidates),
        "status": "ok", "duration_s": time.time() - t0})
    con.close()
    return {"n_candidates": len(candidates), "gate": gate, "digest_len": len(digest)}


def _load_from_db(db_path: str) -> tuple[list[Node], list[Edge]]:  # pragma: no cover
    con = connect(db_path)
    node_rows = con.execute("SELECT node_id, node_type FROM nodes").fetchall()
    edge_rows = con.execute(
        "SELECT source_id, target_id, predicate, first_year FROM edges").fetchall()
    nodes = [Node(r[0], r[1]) for r in node_rows]
    edges = [Edge(r[0], r[1], r[2], r[3] or 0) for r in edge_rows]
    con.close()
    return nodes, edges


def _write_reports(digest: str, candidates, gate: dict) -> None:
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)
    stamp = date.today().isoformat()
    (ROOT / "reports" / f"digest-{stamp}.md").write_text(digest, encoding="utf-8")
    log = {"run_date": stamp, "utc": datetime.now(UTC).isoformat(),
           "n_candidates": len(candidates), "gate": gate}
    (ROOT / "logs" / f"run-{stamp}.json").write_text(json.dumps(log, default=str),
                                                     encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline RF-Discovery")
    ap.add_argument("--db", default=str(ROOT / "data" / "graph.duckdb"))
    ap.add_argument("--synthetic", action="store_true", help="démo/CI sans réseau")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--permutations", type=int, default=50)
    args = ap.parse_args()
    result = run(args.db, synthetic=args.synthetic, seed=args.seed, n_perm=args.permutations)
    print(json.dumps(result, default=str, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
