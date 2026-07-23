"""Classement composite des candidats et filtre de nouveauté (§7.4–7.5).

Combine le z-score du null par permutation (signal principal), le second avis par
embedding (le *désaccord* est un signal), la nouveauté à la Uzzi et la rafale. Le filtre
de nouveauté écarte les paires déjà reliées par une arête directe.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from graph.build import Graph
from graph.embed import embed_scores
from graph.metapaths import Metapath
from graph.permute import NullResult, dwpc_null
from score.novelty import novelty_scores


@dataclass
class Candidate:
    a_id: str
    c_id: str
    metapath: str
    dwpc: float
    z_score: float
    p_value: float
    embed_score: float
    novelty_z: float
    burst_score: float
    composite_rank: int = 0


def _zstd(x: np.ndarray) -> np.ndarray:
    mu, sd = float(np.mean(x)), float(np.std(x))
    return (x - mu) / sd if sd > 0 else np.zeros_like(x)


def _has_direct_edge(graph: Graph, a: str, c: str) -> bool:
    ia, ic = graph.index.get(a, -1), graph.index.get(c, -1)
    if ia < 0 or ic < 0:
        return False
    return any(mat[ia, ic] != 0 or mat[ic, ia] != 0 for mat in graph.adj.values())


def rank_candidates(
    graph: Graph,
    metapaths: Sequence[Metapath],
    pairs: Sequence[tuple[str, str]],
    *,
    null: NullResult | None = None,
    burst: Mapping[str, float] | None = None,
    n_permutations: int = 200,
    seed: int = 0,
    w: float = 0.4,
    drop_direct_edges: bool = True,
) -> list[Candidate]:
    """Score, filtre et classe les paires. Renvoie les candidats triés (rang 1 = meilleur)."""
    if null is None:
        null = dwpc_null(graph, metapaths, pairs, n_permutations=n_permutations, seed=seed, w=w)
    best_j = np.argmax(null.z, axis=1)
    best_z = null.z[np.arange(len(pairs)), best_j]
    best_dwpc = null.observed[np.arange(len(pairs)), best_j]
    embed = embed_scores(graph, pairs, seed=seed)
    novelty = novelty_scores(graph, pairs)
    burst = burst or {}

    cands: list[Candidate] = []
    for i, (a, c) in enumerate(pairs):
        if drop_direct_edges and _has_direct_edge(graph, a, c):
            continue
        cands.append(Candidate(
            a_id=a, c_id=c, metapath=metapaths[best_j[i]].label(),
            dwpc=float(best_dwpc[i]), z_score=float(best_z[i]),
            p_value=float(norm.sf(best_z[i])), embed_score=float(embed[i]),
            novelty_z=float(novelty[i]), burst_score=float(burst.get(c, 0.0)),
        ))
    if not cands:
        return []
    z = _zstd(np.array([c.z_score for c in cands]))
    e = _zstd(np.array([c.embed_score for c in cands]))
    nov = _zstd(np.array([c.novelty_z for c in cands]))
    bu = _zstd(np.array([c.burst_score for c in cands]))
    composite = 0.5 * z + 0.2 * e + 0.2 * nov + 0.1 * bu
    order = np.argsort(composite)[::-1]
    ranked = [cands[i] for i in order]
    for rank, cand in enumerate(ranked, start=1):
        cand.composite_rank = rank
    return ranked
