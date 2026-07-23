"""Enregistrements agrégés neutres, partagés par les substrats SemMedDB et PubTator.

``AggNode``/``AggEdge`` sont la forme pivot avant persistance DuckDB : un nœud/arête typé
avec ses métadonnées agrégées (nom, années, n_papers, pmids). Les deux sources normalisent
vers ces mêmes types, ce qui permet la jointure sur les nœuds (§ M3).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from graph.build import Edge, Node


@dataclass
class AggNode:
    node_id: str
    node_type: str
    name: str
    first_year: int

    def to_graph_node(self) -> Node:
        return Node(node_id=self.node_id, node_type=self.node_type)


@dataclass
class AggEdge:
    source_id: str
    target_id: str
    predicate: str
    n_papers: int
    first_year: int
    last_year: int
    pmids: list[str] = field(default_factory=list)

    def to_graph_edge(self) -> Edge:
        return Edge(self.source_id, self.target_id, self.predicate, self.first_year)
