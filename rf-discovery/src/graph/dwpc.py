"""Degree-Weighted Path Count vectorisé (§7.2).

``DWPC(a,c,m) = Σ_paths Π_{n∈path} degree(n)^(-w)``.

Forme matricielle : ``DWPC_m = Dw · M1 · Dw · M2 · … · Mk · Dw`` où ``Dw = diag(degree^-w)``
et ``M_i`` est l'adjacence du i-ᵉ métaedge (transposée si le métaedge est inverse).
Le facteur ``Dw`` répété pénalise le passage par les nœuds très connectés.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.sparse import csr_matrix, diags

from graph.build import Graph
from graph.metapaths import Metaedge, Metapath


def degree_weight(degree: np.ndarray, w: float) -> np.ndarray:
    """``degree^(-w)`` avec convention ``0^(-w) = 0`` (nœud isolé sans poids)."""
    out = np.zeros_like(degree, dtype=np.float64)
    nz = degree > 0
    out[nz] = np.power(degree[nz], -w)
    return out


def _edge_matrix(graph: Graph, me: Metaedge) -> csr_matrix:
    if me.inverse:
        return graph.matrix((me.dst, me.predicate, me.src)).transpose().tocsr()
    return graph.matrix((me.src, me.predicate, me.dst))


def dwpc_source_matrix(graph: Graph, metapath: Metapath, w: float = 0.4) -> csr_matrix:
    """Matrice DWPC ``|source| × N`` : lignes = nœuds du type source du métachemin."""
    dw = degree_weight(graph.degree, w)
    diag = diags(dw)
    src_rows = graph.rows_of_type(metapath.source_type)
    state: csr_matrix = diag.tocsr()[src_rows]  # |src| × N, lignes pondérées
    for me in metapath.edges:
        state = state @ _edge_matrix(graph, me) @ diag
    return state.tocsr()


def dwpc_pair_matrix(
    graph: Graph, metapath: Metapath, w: float = 0.4
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Renvoie ``(source_rows, target_cols, valeurs_denses)`` pour toutes les paires."""
    src_rows = graph.rows_of_type(metapath.source_type)
    tgt_cols = graph.rows_of_type(metapath.target_type)
    state = dwpc_source_matrix(graph, metapath, w)
    dense = np.asarray(state[:, tgt_cols].todense(), dtype=np.float64)
    return src_rows, tgt_cols, dense


def dwpc_features(
    graph: Graph,
    metapaths: Sequence[Metapath],
    pairs: Sequence[tuple[str, str]],
    w: float = 0.4,
) -> np.ndarray:
    """Matrice de features ``n_paires × n_métachemins`` (DWPC par métachemin)."""
    feats = np.zeros((len(pairs), len(metapaths)), dtype=np.float64)
    pair_idx = [(graph.index.get(a, -1), graph.index.get(c, -1)) for a, c in pairs]
    for j, mp in enumerate(metapaths):
        state = dwpc_source_matrix(graph, mp, w)
        row_pos = {int(r): i for i, r in enumerate(graph.rows_of_type(mp.source_type))}
        for i, (a, c) in enumerate(pair_idx):
            if a in row_pos and c >= 0:
                feats[i, j] = state[row_pos[a], c]
    return feats
