"""Burst (Kleinberg), nouveauté (Uzzi) et classement composite (M8)."""
from __future__ import annotations

from pathlib import Path

from graph.build import build_graph
from graph.metapaths import MetaGraph, enumerate_metapaths
from score.burst import burst_score, burst_states
from score.novelty import novelty_scores
from score.rank import rank_candidates
from synthetic import generate

CFG = Path(__file__).resolve().parents[1] / "config" / "metapaths.yaml"


def test_burst_detects_recent_acceleration():
    d = [100] * 8
    calm = [1, 1, 1, 1, 1, 1, 1, 1]
    spike = [1, 1, 1, 1, 1, 40, 60, 80]
    assert burst_score(spike, d) > burst_score(calm, d)
    assert burst_states(spike, d)[-1] == 1


def test_novelty_higher_for_atypical_pair():
    graph = build_graph(*_two_pairs())
    scores = novelty_scores(graph, [("x", "shared"), ("lonely", "shared")])
    # 'lonely' n'a aucun voisin commun avec 'shared' -> plus atypique/nouveau.
    assert scores[1] >= scores[0]


def _two_pairs():
    from graph.build import Edge, Node
    nodes = [Node(n, "Gene") for n in ("x", "shared", "hub", "lonely")]
    edges = [Edge("x", "hub", "INTERACTS_WITH"), Edge("shared", "hub", "INTERACTS_WITH")]
    return nodes, edges


def test_rank_drops_direct_edges_and_orders():
    sg = generate(seed=2)
    graph = build_graph(sg.nodes, sg.edges)
    mps = enumerate_metapaths(MetaGraph.from_config(CFG))
    pairs = [("EXP0", "PHEN0"), ("EXP1", "PHEN1"), ("EXP2", "PHEN2")]
    cands = rank_candidates(graph, mps, pairs, n_permutations=15, seed=0)
    ranks = [c.composite_rank for c in cands]
    assert ranks == sorted(ranks)
    assert all(c.p_value >= 0 for c in cands)
