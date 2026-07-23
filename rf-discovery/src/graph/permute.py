"""Modèle nul par permutation XSwap préservant les degrés (§7.3).

L'échange d'arêtes s'effectue *au sein d'un même métaedge typé* : les types des
extrémités — et donc la séquence de degrés par type — sont préservés par construction.
Recalculer le DWPC sur les permutations donne ``μ`` et ``σ`` puis
``z(a,c,m) = (DWPC_obs − μ) / σ``. Un candidat sans z-score n'est pas un candidat.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix

from graph.build import Graph
from graph.dwpc import dwpc_features
from graph.metapaths import Metapath


def permute_graph(graph: Graph, rng: np.random.Generator, swaps_per_edge: int = 10) -> Graph:
    """Une réalisation du graphe nul (XSwap, degrés préservés par métaedge)."""
    new_adj: dict = {}
    for key, mat in graph.adj.items():
        coo = mat.tocoo()
        rows, cols = coo.row.copy(), coo.col.copy()
        edges = set(zip(rows.tolist(), cols.tolist(), strict=False))
        m = len(rows)
        for _ in range(swaps_per_edge * m):
            i, j = int(rng.integers(m)), int(rng.integers(m))
            if i == j:
                continue
            a, b, c, d = int(rows[i]), int(cols[i]), int(rows[j]), int(cols[j])
            if a == d or c == b or b == d or a == c:
                continue
            if (a, d) in edges or (c, b) in edges:
                continue
            edges.discard((a, b))
            edges.discard((c, d))
            edges.add((a, d))
            edges.add((c, b))
            cols[i], cols[j] = d, b
        new_adj[key] = csr_matrix((np.ones(m), (rows, cols)), shape=mat.shape)
    return Graph(
        graph.node_ids, graph.node_type, graph.index, new_adj, graph.degree.copy()
    )


@dataclass
class NullResult:
    observed: np.ndarray  # n_paires × n_métachemins
    mean: np.ndarray
    std: np.ndarray
    z: np.ndarray


def dwpc_null(
    graph: Graph,
    metapaths: Sequence[Metapath],
    pairs: Sequence[tuple[str, str]],
    *,
    n_permutations: int = 200,
    seed: int = 0,
    w: float = 0.4,
    swaps_per_edge: int = 10,
) -> NullResult:
    """Distribution nulle du DWPC par permutation (Welford, seedé et reproductible)."""
    observed = dwpc_features(graph, metapaths, pairs, w)
    rng = np.random.default_rng(seed)
    mean = np.zeros_like(observed)
    m2 = np.zeros_like(observed)
    for k in range(n_permutations):
        pg = permute_graph(graph, rng, swaps_per_edge)
        x = dwpc_features(pg, metapaths, pairs, w)
        delta = x - mean
        mean += delta / (k + 1)
        m2 += delta * (x - mean)
    std = np.sqrt(m2 / max(n_permutations - 1, 1))
    safe = np.where(std > 0, std, 1.0)
    z = (observed - mean) / safe
    return NullResult(observed=observed, mean=mean, std=std, z=z)
