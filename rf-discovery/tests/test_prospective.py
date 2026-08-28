"""Validation prospective : gel du graphe, effacement du lien, classement vs témoins."""
from __future__ import annotations

from pathlib import Path

import yaml

from graph.build import Edge, Node
from graph.metapaths import MetaGraph, enumerate_metapaths
from validate.prospective import freeze, rank_known_link, run_prospective

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "metapaths.yaml"


def test_freeze_keeps_scaffold_and_old_edges():
    edges = [Edge("a", "b", "AFFECTS", 2005), Edge("b", "c", "PARTICIPATES_IN", 0),
             Edge("a", "c", "CAUSES", 2020)]
    kept = freeze(edges, 2010)
    years = {e.first_year for e in kept}
    assert years == {2005, 0}      # l'arête de 2020 est écartée, la charpente reste


def _toy_graph():
    """Un composé vrai relié à la maladie par 3 gènes ; les témoins n'en ont aucun."""
    nodes = [Node("CHEM_TRUE", "Chemical"), Node("DIS", "Disease")]
    edges = []
    for i in range(3):
        nodes.append(Node(f"G{i}", "Gene"))
        edges.append(Edge("CHEM_TRUE", f"G{i}", "AFFECTS", 2005))
        edges.append(Edge(f"G{i}", "DIS", "ASSOCIATED_WITH", 2005))
    for j in range(20):                     # témoins de degré comparable, sans lien mécaniste
        nodes.append(Node(f"CHEM_CTRL{j}", "Chemical"))
        nodes.append(Node(f"GX{j}", "Gene"))
        edges.append(Edge(f"CHEM_CTRL{j}", f"GX{j}", "AFFECTS", 2005))
    edges.append(Edge("CHEM_TRUE", "DIS", "CAUSES", 2020))   # le lien à retrouver
    return nodes, edges


def test_true_link_outranks_controls_after_direct_edge_removed():
    nodes, edges = _toy_graph()
    metapaths = enumerate_metapaths(MetaGraph.from_config(CFG))
    res = rank_known_link(nodes, freeze(edges, 2010), metapaths,
                          "CHEM_TRUE", "DIS", "vrai lien", n_controls=20)
    assert res is not None and res.reachable
    assert res.rank == 1, "le couple mécanistiquement relié doit sortir en tête"
    assert res.percentile < 20


def test_unknown_entity_returns_none():
    nodes, edges = _toy_graph()
    metapaths = enumerate_metapaths(MetaGraph.from_config(CFG))
    assert rank_known_link(nodes, freeze(edges, 2010), metapaths,
                           "ABSENT", "DIS", "x", n_controls=5) is None


def test_run_prospective_skips_links_known_before_cutoff(tmp_path):
    nodes, edges = _toy_graph()
    cfg = {"n_controls": 20, "median_percentile_max": 20.0, "links": [
        {"chemical": "CHEM_TRUE", "disease": "DIS", "label": "prospectif", "recognised": 2020},
        {"chemical": "CHEM_TRUE", "disease": "DIS", "label": "deja connu", "recognised": 2001},
    ]}
    path = tmp_path / "known.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    out = run_prospective(nodes, edges, CFG, path, cutoff=2010)
    assert out["n_tested"] == 1          # le couple déjà connu au gel est écarté
    assert out["links"][0]["label"] == "prospectif"
    assert out["passes"] is True
