"""Persistance du graphe dans DuckDB : upsert nœuds/arêtes, degrés, chargement (§6, M3).

Fournit aussi la distribution des degrés et un ajustement log-log pour vérifier le critère
d'acceptation M2 (distribution en loi de puissance).
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from graph.build import Edge, Node
from normalize.semmed import AggEdge, AggNode


def upsert(con, nodes: Sequence[AggNode], edges: Sequence[AggEdge]) -> None:
    """Insère/replace nœuds et arêtes puis recalcule les degrés."""
    con.executemany(
        "INSERT OR REPLACE INTO nodes (node_id, node_type, name, synonyms, first_year, "
        "degree) VALUES (?, ?, ?, [], ?, 0)",
        [(n.node_id, n.node_type, n.name, n.first_year) for n in nodes])
    con.executemany(
        "INSERT OR REPLACE INTO edges (source_id, target_id, predicate, n_papers, "
        "first_year, last_year, pmids, confidence) VALUES (?, ?, ?, ?, ?, ?, ?, 1.0)",
        [(e.source_id, e.target_id, e.predicate, e.n_papers, e.first_year, e.last_year,
          e.pmids) for e in edges])
    recompute_degrees(con)


def recompute_degrees(con) -> None:
    """Degré = nombre d'arêtes incidentes (source ou cible)."""
    con.execute("UPDATE nodes SET degree = 0")
    con.execute("""
        CREATE OR REPLACE TEMP TABLE _deg AS
        SELECT node_id, COUNT(*) AS d FROM (
            SELECT source_id AS node_id FROM edges
            UNION ALL SELECT target_id AS node_id FROM edges
        ) GROUP BY node_id
    """)
    con.execute("UPDATE nodes SET degree = _deg.d FROM _deg WHERE _deg.node_id = nodes.node_id")
    con.execute("DROP TABLE IF EXISTS _deg")


def load_graph(con) -> tuple[list[Node], list[Edge]]:
    """Recharge nœuds/arêtes typés pour le scoring."""
    node_rows = con.execute("SELECT node_id, node_type FROM nodes").fetchall()
    edge_rows = con.execute(
        "SELECT source_id, target_id, predicate, first_year FROM edges").fetchall()
    nodes = [Node(r[0], r[1]) for r in node_rows]
    edges = [Edge(r[0], r[1], r[2], int(r[3] or 0)) for r in edge_rows]
    return nodes, edges


def degree_distribution(con) -> list[tuple[int, int]]:
    """Renvoie [(degré, nombre de nœuds)] trié par degré croissant."""
    rows = con.execute(
        "SELECT degree, COUNT(*) FROM nodes WHERE degree > 0 GROUP BY degree ORDER BY degree"
    ).fetchall()
    return [(int(d), int(c)) for d, c in rows]


def powerlaw_slope(distribution: Sequence[tuple[int, int]]) -> float:
    """Pente de la régression log-log (degré, fréquence). Une loi de puissance donne < 0."""
    pts = [(d, c) for d, c in distribution if d > 0 and c > 0]
    if len(pts) < 2:
        return float("nan")
    x = np.log(np.array([d for d, _ in pts], dtype=float))
    y = np.log(np.array([c for _, c in pts], dtype=float))
    slope = np.polyfit(x, y, 1)[0]
    return float(slope)
