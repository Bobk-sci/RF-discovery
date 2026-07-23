"""Second avis par embedding de graphe (§2).

Le désaccord entre le DWPC et l'embedding est un signal en soi. On produit des
embeddings déterministes par décomposition spectrale (SVD tronquée) de l'adjacence
symétrisée — substitut léger et reproductible à node2vec/ComplEx, sans dépendance
supplémentaire. ``embed_score(a,c)`` = similarité cosinus des deux vecteurs.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

from graph.build import Graph


def _symmetric_adjacency(graph: Graph) -> csr_matrix:
    n = graph.n_nodes
    total = csr_matrix((n, n), dtype=np.float64)
    for mat in graph.adj.values():
        total = total + mat
    return (total + total.transpose()).tocsr()


def node_embeddings(graph: Graph, dim: int = 16, seed: int = 0) -> np.ndarray:
    """Embeddings ``N × dim`` déterministes (SVD tronquée, vecteur de départ fixé)."""
    adj = _symmetric_adjacency(graph)
    k = min(dim, max(1, min(adj.shape) - 1))
    rng = np.random.default_rng(seed)
    v0 = rng.standard_normal(adj.shape[0])
    try:
        u, s, _ = svds(adj.astype(np.float64), k=k, v0=v0)
    except Exception:  # graphe minuscule : repli dense reproductible
        dense = adj.toarray()
        u, s, _ = np.linalg.svd(dense)
        u, s = u[:, :k], s[:k]
    emb = u * s  # N × k
    if emb.shape[1] < dim:
        emb = np.pad(emb, ((0, 0), (0, dim - emb.shape[1])))
    return emb


def embed_scores(
    graph: Graph, pairs: Sequence[tuple[str, str]], dim: int = 16, seed: int = 0
) -> np.ndarray:
    """Similarité cosinus d'embedding pour chaque paire (0 si nœud absent)."""
    emb = node_embeddings(graph, dim=dim, seed=seed)
    norms = np.linalg.norm(emb, axis=1)
    out = np.zeros(len(pairs), dtype=np.float64)
    for i, (a, c) in enumerate(pairs):
        ia, ic = graph.index.get(a, -1), graph.index.get(c, -1)
        if ia < 0 or ic < 0 or norms[ia] == 0 or norms[ic] == 0:
            continue
        out[i] = float(emb[ia] @ emb[ic] / (norms[ia] * norms[ic]))
    return out
