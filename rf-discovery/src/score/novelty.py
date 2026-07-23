"""Nouveauté : combinaison atypique à la Uzzi (2013) + modularité inter-domaines (§7.5).

Un pont vaut d'autant plus que les deux communautés s'ignorent. On mesure l'écart du
nombre de voisins communs d'une paire à son espérance sous un modèle de configuration
(préservant les degrés). Peu de voisins communs face à l'attendu ⇒ combinaison atypique
⇒ ``novelty_z`` élevé. La distribution nulle est explicite (pas de « plausibilité » sans
null, §2).
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.sparse import csr_matrix

from graph.build import Graph


def _undirected(graph: Graph) -> csr_matrix:
    n = graph.n_nodes
    total = csr_matrix((n, n), dtype=np.float64)
    for mat in graph.adj.values():
        total = total + mat
    sym = (total + total.transpose()).tocsr()
    sym.data[:] = 1.0
    return sym


def novelty_scores(graph: Graph, pairs: Sequence[tuple[str, str]]) -> np.ndarray:
    """``novelty_z`` par paire : élevé = combinaison atypique (moins de ponts qu'attendu)."""
    adj = _undirected(graph)
    deg = np.asarray(adj.sum(axis=1)).ravel()
    two_m = float(deg.sum()) or 1.0
    out = np.zeros(len(pairs), dtype=np.float64)
    for i, (a, c) in enumerate(pairs):
        ia, ic = graph.index.get(a, -1), graph.index.get(c, -1)
        if ia < 0 or ic < 0:
            continue
        observed = float(adj[ia].multiply(adj[ic]).sum())
        expected = deg[ia] * deg[ic] / two_m
        if expected <= 0:
            continue
        z = (observed - expected) / np.sqrt(expected)
        out[i] = -z  # peu de voisins communs (z négatif) -> nouveauté positive
    return out


def label_propagation(graph: Graph, seed: int = 0, iters: int = 20) -> np.ndarray:
    """Communautés déterministes par propagation de labels (pour la modularité)."""
    adj = _undirected(graph)
    n = graph.n_nodes
    labels = np.arange(n)
    rng = np.random.default_rng(seed)
    for _ in range(iters):
        changed = False
        for v in rng.permutation(n):
            neigh = adj.indices[adj.indptr[v]:adj.indptr[v + 1]]
            if len(neigh) == 0:
                continue
            vals, counts = np.unique(labels[neigh], return_counts=True)
            best = vals[np.argmax(counts)]
            if labels[v] != best:
                labels[v] = best
                changed = True
        if not changed:
            break
    return labels


def cross_community(graph: Graph, pairs: Sequence[tuple[str, str]], seed: int = 0) -> np.ndarray:
    """1.0 si les deux nœuds d'une paire sont dans des communautés différentes."""
    labels = label_propagation(graph, seed=seed)
    out = np.zeros(len(pairs), dtype=np.float64)
    for i, (a, c) in enumerate(pairs):
        ia, ic = graph.index.get(a, -1), graph.index.get(c, -1)
        if ia >= 0 and ic >= 0 and labels[ia] != labels[ic]:
            out[i] = 1.0
    return out
