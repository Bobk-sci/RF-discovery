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


def _in_sorted(sorted_keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Appartenance vectorisée à un tableau trié (``searchsorted``)."""
    if len(sorted_keys) == 0:
        return np.zeros(len(values), dtype=bool)
    idx = np.clip(np.searchsorted(sorted_keys, values), 0, len(sorted_keys) - 1)
    return sorted_keys[idx] == values


def _valid_swaps(rows, cols, i, j, n, m) -> np.ndarray:
    """Masque des échanges licites : pas de boucle, pas d'arête dupliquée, un lot cohérent."""
    a, b, c, d = rows[i], cols[i], rows[j], cols[j]
    ok = (i != j) & (a != c) & (b != d) & (a != d) & (c != b)
    new1, new2 = a * n + d, c * n + b
    existing = np.sort(rows * n + cols)
    ok &= ~_in_sorted(existing, new1) & ~_in_sorted(existing, new2)
    # chaque arête ne doit être touchée qu'une fois dans le lot
    touched = np.zeros(m, dtype=np.int64)
    np.add.at(touched, i[ok], 1)
    np.add.at(touched, j[ok], 1)
    ok &= (touched[i] == 1) & (touched[j] == 1)
    # les nouvelles arêtes du lot doivent être distinctes entre elles
    both = np.concatenate([new1[ok], new2[ok]])
    _, inv, counts = np.unique(both, return_inverse=True, return_counts=True)
    unique_ok = counts[inv] == 1
    half = len(both) // 2
    keep = unique_ok[:half] & unique_ok[half:]
    sel = np.flatnonzero(ok)
    final = np.zeros(len(i), dtype=bool)
    final[sel[keep]] = True
    return final


def _xswap_columns(rows: np.ndarray, cols: np.ndarray, n: int,
                   rng: np.random.Generator, rounds: int) -> np.ndarray:
    """XSwap vectorisé par lots : les degrés sortants/entrants sont préservés exactement."""
    m = len(rows)
    for _ in range(rounds):
        i = rng.integers(m, size=m)
        j = rng.integers(m, size=m)
        ok = _valid_swaps(rows, cols, i, j, n, m)
        ii, jj = i[ok], j[ok]
        cols[ii], cols[jj] = cols[jj].copy(), cols[ii].copy()
    return cols


def permute_graph(graph: Graph, rng: np.random.Generator, swaps_per_edge: int = 10) -> Graph:
    """Une réalisation du graphe nul (XSwap, degrés préservés par métaedge)."""
    new_adj: dict = {}
    n = graph.n_nodes
    for key, mat in graph.adj.items():
        coo = mat.tocoo()
        rows = coo.row.astype(np.int64)
        cols = coo.col.astype(np.int64).copy()
        m = len(rows)
        if m >= 2:
            cols = _xswap_columns(rows, cols, n, rng, swaps_per_edge)
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
