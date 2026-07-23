"""Énumération des métachemins et bornes de longueur (M4)."""
from __future__ import annotations

from pathlib import Path

from graph.metapaths import MetaGraph, enumerate_metapaths

CFG = Path(__file__).resolve().parents[1] / "config" / "metapaths.yaml"


def test_enumeration_respects_bounds_and_endpoints():
    mg = MetaGraph.from_config(CFG)
    paths = enumerate_metapaths(mg)
    assert paths, "au moins un métachemin attendu"
    for p in paths:
        assert mg.min_len <= len(p.edges) <= mg.max_len
        assert p.source_type in mg.source_types
        assert p.target_type in mg.target_types


def test_no_repeated_node_type():
    mg = MetaGraph.from_config(CFG)
    for p in enumerate_metapaths(mg):
        types = [p.edges[0].src] + [e.dst for e in p.edges]
        assert len(types) == len(set(types)), "un type de nœud ne doit pas se répéter"


def test_inverse_metaedges_present():
    mg = MetaGraph.from_config(CFG)
    assert any(e.inverse for e in mg.metaedges)
    assert any(not e.inverse for e in mg.metaedges)
