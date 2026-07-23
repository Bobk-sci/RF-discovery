"""Normalisation des entités PubTator/SemMedDB en nœuds et arêtes du graphe (§ M2–M3).

Mappe les types PubTator vers les types de nœuds du métagraphe et les prédicats bruts
vers l'ensemble SemMedDB retenu. Agrège les arêtes multi-articles (n_papers, first/last year).
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from collect.pubtator import Annotation, Relation
from graph.build import Edge, Node

# PubTator/SemMedDB -> types de nœuds du métagraphe.
_TYPE_MAP = {
    "Gene": "Gene", "Chemical": "Chemical", "Disease": "Disease",
    "CellLine": "CellType", "CellType": "CellType", "Pathway": "Pathway",
    "Phenotype": "Phenotype", "Exposure": "Exposure", "BrainRegion": "BrainRegion",
}
# Prédicats bruts -> prédicats SemMedDB retenus (config/metapaths.yaml).
_PRED_MAP = {
    "ASSOCIATE": "ASSOCIATED_WITH", "ASSOCIATED_WITH": "ASSOCIATED_WITH",
    "CAUSE": "CAUSES", "CAUSES": "CAUSES", "TREAT": "AFFECTS", "AFFECT": "AFFECTS",
    "AFFECTS": "AFFECTS", "INHIBIT": "INHIBITS", "INHIBITS": "INHIBITS",
    "STIMULATE": "STIMULATES", "STIMULATES": "STIMULATES",
    "INTERACT": "INTERACTS_WITH", "INTERACTS_WITH": "INTERACTS_WITH",
    "PART_OF": "PART_OF", "PARTICIPATES_IN": "PARTICIPATES_IN",
    "PREDISPOSE": "PREDISPOSES", "PRODUCES": "PRODUCES", "DISRUPTS": "DISRUPTS",
    "AUGMENTS": "AUGMENTS",
}


def map_type(entity_type: str) -> str | None:
    return _TYPE_MAP.get(entity_type)


def map_predicate(predicate: str) -> str | None:
    return _PRED_MAP.get(predicate.upper())


def nodes_from_annotations(anns: Iterable[Annotation]) -> list[Node]:
    """Nœuds uniques (par concept_id) à partir des annotations, types mappés."""
    seen: dict[str, Node] = {}
    for a in anns:
        ntype = map_type(a.entity_type)
        if ntype is None or a.concept_id in seen:
            continue
        seen[a.concept_id] = Node(node_id=a.concept_id, node_type=ntype)
    return list(seen.values())


def edges_from_relations(rels: Sequence[Relation], known_nodes: Iterable[str]) -> list[Edge]:
    """Arêtes agrégées : first_year = plus ancienne mention ; prédicats mappés/filtrés."""
    valid = set(known_nodes)
    agg: dict[tuple[str, str, str], list[int]] = {}
    for r in rels:
        pred = map_predicate(r.predicate)
        if pred is None or r.subject_id not in valid or r.object_id not in valid:
            continue
        key = (r.subject_id, pred, r.object_id)
        agg.setdefault(key, []).append(r.year or 0)
    edges: list[Edge] = []
    for (s, pred, o), years in agg.items():
        positive = [y for y in years if y > 0]
        first = min(positive) if positive else 0
        edges.append(Edge(source_id=s, target_id=o, predicate=pred, first_year=first))
    return edges
