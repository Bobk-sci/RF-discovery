"""XSwap préserve les degrés ; le null est reproductible (M5)."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from graph.build import build_graph
from graph.metapaths import MetaGraph, enumerate_metapaths
from graph.permute import dwpc_null, permute_graph
from synthetic import generate

CFG = Path(__file__).resolve().parents[1] / "config" / "metapaths.yaml"


def _graph():
    sg = generate(seed=1)
    return build_graph(sg.nodes, sg.edges)


def test_xswap_preserves_degrees():
    graph = _graph()
    rng = np.random.default_rng(0)
    perm = permute_graph(graph, rng, swaps_per_edge=5)
    assert np.array_equal(graph.degree, perm.degree)
    for key, mat in graph.adj.items():
        pm = perm.adj[key]
        assert np.array_equal(np.asarray(mat.sum(1)).ravel(),
                              np.asarray(pm.sum(1)).ravel())  # degré sortant par nœud
        assert np.array_equal(np.asarray(mat.sum(0)).ravel(),
                              np.asarray(pm.sum(0)).ravel())  # degré entrant par nœud
        assert mat.nnz == pm.nnz


def test_null_is_deterministic_and_finite():
    graph = _graph()
    mg = MetaGraph.from_config(CFG)
    mps = enumerate_metapaths(mg)[:6]
    pairs = [("EXP0", "PHEN0"), ("EXP1", "PHEN1")]
    a = dwpc_null(graph, mps, pairs, n_permutations=20, seed=7)
    b = dwpc_null(graph, mps, pairs, n_permutations=20, seed=7)
    assert np.allclose(a.z, b.z, equal_nan=True)
    assert np.isfinite(a.z).all()
