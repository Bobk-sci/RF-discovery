"""Générateur de graphe temporel synthétique (déterministe) pour tests et démo.

Structure latente : chaque nœud porte un « groupe ». Les arêtes pré-2018 relient
préférentiellement des nœuds de même groupe le long de la chaîne
``Exposure/Chemical → Gene → Pathway → Phenotype/Disease``. Les liens *futurs*
(directs ``CAUSES``, 2019–2025) apparaissent surtout entre nœuds de même groupe — donc
là où un métachemin fort préexiste. Le DWPC calculé sur le graphe pré-2018 doit ainsi
prédire les liens futurs : c'est le banc d'essai du gate (§9).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from graph.build import Edge, Node


@dataclass
class SyntheticGraph:
    nodes: list[Node]
    edges: list[Edge]
    groups: dict[str, int]


def _make_nodes(prefix: str, ntype: str, count: int, groups: dict[str, int],
                rng: np.random.Generator, n_groups: int) -> list[Node]:
    nodes = []
    for i in range(count):
        nid = f"{prefix}{i}"
        groups[nid] = int(rng.integers(n_groups))
        nodes.append(Node(node_id=nid, node_type=ntype))
    return nodes


def _link(src: list[Node], dst: list[Node], predicate: str, groups: dict[str, int],
          rng: np.random.Generator, p_same: float, p_diff: float,
          yr: tuple[int, int]) -> list[Edge]:
    edges = []
    for a in src:
        for b in dst:
            p = p_same if groups[a.node_id] == groups[b.node_id] else p_diff
            if rng.random() < p:
                year = int(rng.integers(yr[0], yr[1] + 1))
                edges.append(Edge(a.node_id, b.node_id, predicate, year))
    return edges


def generate(seed: int = 0, n_groups: int = 6, sizes: dict[str, int] | None = None
             ) -> SyntheticGraph:
    """Construit nœuds + arêtes (pré-2018 structurelles, futures directes 2019–2025)."""
    rng = np.random.default_rng(seed)
    sizes = sizes or {"EXP": 12, "CHEM": 18, "GENE": 40, "PATH": 20, "PHEN": 16, "DIS": 16}
    groups: dict[str, int] = {}
    exp = _make_nodes("EXP", "Exposure", sizes["EXP"], groups, rng, n_groups)
    chem = _make_nodes("CHEM", "Chemical", sizes["CHEM"], groups, rng, n_groups)
    gene = _make_nodes("GENE", "Gene", sizes["GENE"], groups, rng, n_groups)
    path = _make_nodes("PATH", "Pathway", sizes["PATH"], groups, rng, n_groups)
    phen = _make_nodes("PHEN", "Phenotype", sizes["PHEN"], groups, rng, n_groups)
    dis = _make_nodes("DIS", "Disease", sizes["DIS"], groups, rng, n_groups)
    nodes = exp + chem + gene + path + phen + dis

    past = (2005, 2018)
    edges: list[Edge] = []
    edges += _link(exp, gene, "AFFECTS", groups, rng, 0.55, 0.03, past)
    edges += _link(chem, gene, "AFFECTS", groups, rng, 0.55, 0.03, past)
    edges += _link(gene, path, "PARTICIPATES_IN", groups, rng, 0.55, 0.03, past)
    edges += _link(path, phen, "ASSOCIATED_WITH", groups, rng, 0.55, 0.03, past)
    edges += _link(path, dis, "ASSOCIATED_WITH", groups, rng, 0.55, 0.03, past)
    # Liens futurs directs (positifs du time-slice) : surtout intra-groupe.
    future = (2019, 2025)
    edges += _link(exp, phen, "CAUSES", groups, rng, 0.45, 0.02, future)
    edges += _link(chem, dis, "CAUSES", groups, rng, 0.45, 0.02, future)
    return SyntheticGraph(nodes=nodes, edges=edges, groups=groups)
