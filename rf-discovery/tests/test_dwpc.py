"""DWPC vérifié à la main sur une paire connue (critère M4)."""
from __future__ import annotations

import numpy as np

from graph.build import Edge, Node, build_graph
from graph.dwpc import degree_weight, dwpc_features
from graph.metapaths import Metaedge, Metapath


def test_dwpc_hand_computed():
    # A -R-> B -S-> C ; deux chemins a1->b1->c1 et a1->b2->c1.
    nodes = [Node("a1", "A"), Node("b1", "B"), Node("b2", "B"), Node("c1", "C")]
    edges = [Edge("a1", "b1", "R"), Edge("a1", "b2", "R"),
             Edge("b1", "c1", "S"), Edge("b2", "c1", "S")]
    graph = build_graph(nodes, edges)
    # tous les degrés valent 2 -> D = 2^-0.4 partout ; DWPC = 2^-0.2.
    mp = Metapath((Metaedge("A", "R", "B"), Metaedge("B", "S", "C")))
    feats = dwpc_features(graph, [mp], [("a1", "c1")], w=0.4)
    assert np.isclose(feats[0, 0], 2 ** -0.2, atol=1e-9)


def test_degree_weight_zero_degree():
    dw = degree_weight(np.array([0.0, 4.0]), 0.5)
    assert dw[0] == 0.0
    assert np.isclose(dw[1], 0.5)


def test_inverse_metaedge_transposes():
    nodes = [Node("a1", "A"), Node("b1", "B")]
    graph = build_graph(nodes, [Edge("a1", "b1", "R")])
    forward = Metapath((Metaedge("A", "R", "B"),))
    backward = Metapath((Metaedge("B", "R", "A", inverse=True),))
    f = dwpc_features(graph, [forward], [("a1", "b1")])[0, 0]
    b = dwpc_features(graph, [backward], [("b1", "a1")])[0, 0]
    assert np.isclose(f, b) and f > 0
