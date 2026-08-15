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
from graph.store import recompute_degrees
from report.dashboard import build_dashboard
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


def persist(con, nodes, edges, candidates, run_row: dict, *, write_graph: bool = True) -> None:
    """Persiste le run. ``write_graph=False`` en mode réel : le graphe **vient** de la base,
    le réécrire effacerait les noms, degrés et compteurs posés par la collecte et CTD."""
    if write_graph:
        con.execute("DELETE FROM nodes")
        if nodes:
            con.executemany(
                "INSERT INTO nodes (node_id, node_type, degree) VALUES (?, ?, 0)",
                [(n.node_id, n.node_type) for n in nodes])
        con.execute("DELETE FROM edges")
        if edges:
            con.executemany(
                "INSERT INTO edges (source_id, target_id, predicate, first_year, n_papers) "
                "VALUES (?, ?, ?, ?, 1)",
                [(e.source_id, e.target_id, e.predicate, e.first_year) for e in edges])
        recompute_degrees(con)
    _persist_candidates(con, run_row["run_date"], candidates)
    con.execute(
        "INSERT OR REPLACE INTO runs (run_date, n_new_papers, n_new_edges, n_candidates, "
        "status, error, duration_s) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (run_row["run_date"], 0, len(edges), run_row["n_candidates"],
         run_row["status"], run_row.get("error"), run_row["duration_s"]))


def _persist_candidates(con, run_date, candidates) -> None:
    """Ajoute les candidats du run (jamais de suppression, §12 — historique d'entraînement)."""
    con.execute("DELETE FROM candidates WHERE run_date = ?", (run_date,))  # rerun idempotent
    if not candidates:
        return
    con.executemany(
        "INSERT INTO candidates (run_date, a_id, c_id, metapath, dwpc, z_score, p_value, "
        "embed_score, novelty_z, burst_score, composite_rank, llm_explanation, human_verdict)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)",
        [(run_date, c.a_id, c.c_id, c.metapath, c.dwpc, c.z_score, c.p_value,
          c.embed_score, c.novelty_z, c.burst_score, c.composite_rank) for c in candidates])


def run(db_path: str, *, synthetic: bool, seed: int = 0, n_perm: int = 50,
        top: int = 20, out_dir: str | Path | None = None) -> dict:
    t0 = time.time()
    out = Path(out_dir) if out_dir else ROOT   # tests écrivent dans un tmp, pas dans le dépôt
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
    # buffer_years=1 : les années CTD viennent d'une estimation PMID (±1 an), on laisse
    # une zone morte pour ne pas classer une arête du mauvais côté du découpage (§9).
    gate = run_timeslice(nodes, edges, cfg, seed=seed, buffer_years=1)
    digest = build_digest(candidates, run_date=date.today(), top=top, gate=gate)
    _write_reports(digest, candidates, gate, out)
    con = connect(db_path)
    persist(con, nodes, edges, candidates, {
        "run_date": date.today(), "n_candidates": len(candidates),
        "status": "ok", "duration_s": time.time() - t0},
        write_graph=synthetic)
    dashboard_html = build_dashboard(con, out_path=out / "docs" / "index.html")
    con.close()
    return {"n_candidates": len(candidates), "gate": gate,
            "digest_len": len(digest), "dashboard_len": len(dashboard_html)}


def _load_from_db(db_path: str) -> tuple[list[Node], list[Edge]]:  # pragma: no cover
    from graph.store import load_graph

    con = connect(db_path)
    nodes, edges = load_graph(con)
    con.close()
    return nodes, edges


def _write_reports(digest: str, candidates, gate: dict, out: Path) -> None:
    (out / "reports").mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    (out / "reports" / f"digest-{stamp}.md").write_text(digest, encoding="utf-8")
    log = {"run_date": stamp, "utc": datetime.now(UTC).isoformat(),
           "n_candidates": len(candidates), "gate": gate}
    (out / "logs" / f"run-{stamp}.json").write_text(json.dumps(log, default=str),
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
