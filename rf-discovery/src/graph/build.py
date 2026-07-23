"""Modèle de graphe hétérogène en mémoire (matrices creuses) et construction (§7).

Le graphe est représenté par une matrice d'adjacence creuse N×N *par métaedge typé*
``(src_type, predicate, dst_type)``. Toutes les matrices partageant le même index
global de nœuds, le DWPC se calcule par simple produit matriciel creux chaîné.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

import numpy as np
from scipy.sparse import csr_matrix

MetaedgeKey = tuple[str, str, str]  # (src_type, predicate, dst_type)


@dataclass(frozen=True)
class Node:
    node_id: str
    node_type: str


@dataclass(frozen=True)
class Edge:
    source_id: str
    target_id: str
    predicate: str
    first_year: int = 0


@dataclass
class Graph:
    """Graphe hétérogène indexé, prêt pour le calcul vectorisé du DWPC."""

    node_ids: list[str]
    node_type: list[str]
    index: dict[str, int]
    adj: dict[MetaedgeKey, csr_matrix]
    degree: np.ndarray
    _type_rows: dict[str, np.ndarray] = field(default_factory=dict)

    @property
    def n_nodes(self) -> int:
        return len(self.node_ids)

    def rows_of_type(self, node_type: str) -> np.ndarray:
        """Indices des nœuds d'un type donné (mémoïsés)."""
        if node_type not in self._type_rows:
            self._type_rows[node_type] = np.array(
                [i for i, t in enumerate(self.node_type) if t == node_type], dtype=np.int64
            )
        return self._type_rows[node_type]

    def matrix(self, key: MetaedgeKey) -> csr_matrix:
        """Adjacence d'un métaedge (matrice nulle si absent)."""
        if key in self.adj:
            return self.adj[key]
        return csr_matrix((self.n_nodes, self.n_nodes), dtype=np.float64)


def build_graph(
    nodes: Sequence[Node],
    edges: Iterable[Edge],
    *,
    exclude_nodes: Iterable[str] = (),
) -> Graph:
    """Construit un ``Graph`` à partir de listes de nœuds/arêtes.

    ``exclude_nodes`` retire des nœuds (hubs sémantiques vides, §7.1) avant construction.
    """
    excluded = set(exclude_nodes)
    kept = [n for n in nodes if n.node_id not in excluded]
    node_ids = [n.node_id for n in kept]
    node_type = [n.node_type for n in kept]
    index = {nid: i for i, nid in enumerate(node_ids)}
    n = len(node_ids)

    buckets: dict[MetaedgeKey, list[tuple[int, int]]] = {}
    degree = np.zeros(n, dtype=np.float64)
    for e in edges:
        if e.source_id not in index or e.target_id not in index:
            continue
        u, v = index[e.source_id], index[e.target_id]
        key = (node_type[u], e.predicate, node_type[v])
        buckets.setdefault(key, []).append((u, v))
        degree[u] += 1.0
        degree[v] += 1.0

    adj: dict[MetaedgeKey, csr_matrix] = {}
    for key, pairs in buckets.items():
        rows = np.fromiter((p[0] for p in pairs), dtype=np.int64, count=len(pairs))
        cols = np.fromiter((p[1] for p in pairs), dtype=np.int64, count=len(pairs))
        data = np.ones(len(pairs), dtype=np.float64)
        mat = csr_matrix((data, (rows, cols)), shape=(n, n))
        mat.data[:] = 1.0  # binaire : compte de chemins, pas de multiplicité
        adj[key] = mat

    return Graph(node_ids, node_type, index, adj, degree)
