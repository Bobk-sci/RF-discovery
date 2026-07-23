"""Dashboard GitHub Pages (M10) — graphe navigable + historique des verdicts.

Génère un site statique **autonome** (HTML/CSS/JS en ligne, aucune dépendance externe,
coût nul) à partir de la base DuckDB : historique des runs, table des candidats du dernier
run, historique des verdicts humains (`human_verdict`), et un graphe de force en JS pur
reliant les extrémités des meilleurs candidats à leur voisinage connu.

Contrairement au digest (markdown pur, §12), le dashboard est un livrable web : le HTML y
est donc légitime. Déployé via `.github/workflows/pages.yml`.
"""
from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from pathlib import Path

from report.dashboard_template import TEMPLATE

TYPE_COLORS = {
    "Exposure": "#e4572e", "Chemical": "#f3a712", "Gene": "#4c9f70",
    "Disease": "#8367c7", "Phenotype": "#2191fb", "Pathway": "#17bebb",
    "CellType": "#c05299", "BrainRegion": "#5c6672",
}
_TOP_N = 30
_NEIGHBORS = 3
_MAX_NODES = 150


def _top_candidates(con, run_date, limit: int = _TOP_N) -> list[dict]:
    rows = con.execute(
        "SELECT a_id, c_id, metapath, z_score, p_value, novelty_z, burst_score, "
        "composite_rank, human_verdict FROM candidates WHERE run_date = ? "
        "ORDER BY composite_rank LIMIT ?", (run_date, limit)).fetchall()
    cols = ["a_id", "c_id", "metapath", "z_score", "p_value", "novelty_z",
            "burst_score", "composite_rank", "human_verdict"]
    return [dict(zip(cols, r, strict=False)) for r in rows]


def _node_meta(con, ids: list[str]) -> dict[str, tuple[str, int]]:
    if not ids:
        return {}
    placeholders = ",".join("?" * len(ids))
    rows = con.execute(
        f"SELECT node_id, node_type, degree FROM nodes WHERE node_id IN ({placeholders})",
        ids).fetchall()
    return {r[0]: (r[1] or "", int(r[2] or 0)) for r in rows}


def _graph_payload(con, cands: list[dict]) -> dict:
    seeds = {c["a_id"] for c in cands} | {c["c_id"] for c in cands}
    links = [{"source": c["a_id"], "target": c["c_id"], "kind": "candidate",
              "z": round(float(c["z_score"]), 2), "rank": c["composite_rank"],
              "verdict": c["human_verdict"] or ""} for c in cands]
    ids = set(seeds)
    for sid in list(seeds):
        rows = con.execute(
            "SELECT source_id, target_id, predicate FROM edges "
            "WHERE source_id = ? OR target_id = ? LIMIT ?", (sid, sid, _NEIGHBORS)).fetchall()
        for s, t, pred in rows:
            if len(ids) >= _MAX_NODES:
                break
            ids.update((s, t))
            links.append({"source": s, "target": t, "kind": "known", "predicate": pred})
    meta = _node_meta(con, sorted(ids))
    nodes = [{"id": i, "type": meta.get(i, ("", 0))[0], "degree": meta.get(i, ("", 0))[1],
              "seed": i in seeds} for i in sorted(ids)]
    links = [ln for ln in links if ln["source"] in meta and ln["target"] in meta]
    return {"nodes": nodes, "links": links, "colors": TYPE_COLORS}


def fetch_dashboard_data(con) -> dict:
    """Rassemble toutes les données du dashboard depuis DuckDB."""
    runs = con.execute(
        "SELECT run_date, n_new_edges, n_candidates, status, duration_s "
        "FROM runs ORDER BY run_date DESC").fetchall()
    latest = con.execute("SELECT max(run_date) FROM candidates").fetchone()[0]
    cands = _top_candidates(con, latest) if latest else []
    verdicts = dict(con.execute(
        "SELECT human_verdict, count(*) FROM candidates WHERE human_verdict IS NOT NULL "
        "GROUP BY human_verdict").fetchall())
    adjudicated = con.execute(
        "SELECT run_date, a_id, c_id, human_verdict FROM candidates "
        "WHERE human_verdict IS NOT NULL ORDER BY run_date DESC LIMIT 100").fetchall()
    total = con.execute("SELECT count(*) FROM candidates").fetchone()[0]
    return {"runs": runs, "latest": latest, "candidates": cands, "verdicts": verdicts,
            "adjudicated": adjudicated, "total_candidates": int(total or 0),
            "graph": _graph_payload(con, cands)}


def _e(value) -> str:
    return html.escape("" if value is None else str(value))


def _runs_rows(runs) -> str:
    return "\n".join(
        f"<tr><td>{_e(d)}</td><td>{_e(ne)}</td><td>{_e(nc)}</td>"
        f"<td>{_e(st)}</td><td>{_e(round(dur or 0, 1))}s</td></tr>"
        for d, ne, nc, st, dur in runs) or '<tr><td colspan="5">aucun run</td></tr>'


def _cands_rows(cands) -> str:
    out = []
    for c in cands:
        verdict = c["human_verdict"] or "—"
        out.append(
            f"<tr><td>{c['composite_rank']}</td><td>{_e(c['a_id'])}</td>"
            f"<td>{_e(c['c_id'])}</td><td>{float(c['z_score']):.2f}</td>"
            f"<td>{float(c['p_value']):.2g}</td><td>{float(c['novelty_z']):.2f}</td>"
            f"<td>{float(c['burst_score']):.2f}</td><td>{_e(verdict)}</td>"
            f"<td class='mp'>{_e(c['metapath'])}</td></tr>")
    return "\n".join(out) or '<tr><td colspan="9">aucun candidat</td></tr>'


def _verdict_cards(verdicts: dict, total: int) -> str:
    reviewed = sum(verdicts.values())
    cards = [f'<div class="card"><span class="num">{total}</span>candidats archivés</div>',
             f'<div class="card"><span class="num">{reviewed}</span>adjugés</div>']
    for label, count in sorted(verdicts.items()):
        cards.append(f'<div class="card"><span class="num">{count}</span>{_e(label)}</div>')
    return "\n".join(cards)


def _adj_rows(adjudicated) -> str:
    return "\n".join(
        f"<tr><td>{_e(d)}</td><td>{_e(a)}</td><td>{_e(c)}</td><td>{_e(v)}</td></tr>"
        for d, a, c, v in adjudicated) or '<tr><td colspan="4">aucun verdict encore</td></tr>'


def render_html(data: dict) -> str:
    """Assemble le HTML final (injection par jetons, pas de .format à cause du JS)."""
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    replacements = {
        "__GENERATED__": generated,
        "__LATEST__": _e(data["latest"] or "n/a"),
        "__RUNS_ROWS__": _runs_rows(data["runs"]),
        "__CANDS_ROWS__": _cands_rows(data["candidates"]),
        "__VERDICT_CARDS__": _verdict_cards(data["verdicts"], data["total_candidates"]),
        "__ADJ_ROWS__": _adj_rows(data["adjudicated"]),
        "__GRAPH_JSON__": json.dumps(data["graph"], ensure_ascii=False, sort_keys=True),
    }
    html_out = TEMPLATE
    for token, value in replacements.items():
        html_out = html_out.replace(token, value)
    return html_out


def build_dashboard(con, *, out_path: str | Path | None = None) -> str:
    """Génère le HTML du dashboard et l'écrit optionnellement sur disque."""
    html_out = render_html(fetch_dashboard_data(con))
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(html_out, encoding="utf-8")
    return html_out


def main() -> None:  # pragma: no cover - CLI
    import argparse

    from graph.schema import connect

    root = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description="Génère le dashboard GitHub Pages")
    ap.add_argument("--db", default=str(root / "data" / "graph.duckdb"))
    ap.add_argument("--out", default=str(root / "docs" / "index.html"))
    args = ap.parse_args()
    con = connect(args.db)
    build_dashboard(con, out_path=args.out)
    con.close()
    print(f"Dashboard écrit : {args.out}")


if __name__ == "__main__":
    main()
