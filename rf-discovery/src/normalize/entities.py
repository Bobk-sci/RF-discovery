"""Normalisation des entités PubTator/SemMedDB en nœuds et arêtes du graphe (§ M2–M3).

Mappe les types PubTator vers les types de nœuds du métagraphe et les prédicats bruts
vers l'ensemble SemMedDB retenu. Agrège les arêtes multi-articles (n_papers, first/last year).
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from collect.pubtator import Annotation, Relation
from graph.build import Edge, Node
from normalize.records import AggEdge, AggNode

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


def agg_nodes_from_annotations(
    anns: Iterable[Annotation], year_map: Mapping[str, int] | None = None
) -> list[AggNode]:
    """Nœuds agrégés (nom, première année) à partir des annotations PubTator."""
    year_map = year_map or {}
    nodes: dict[str, AggNode] = {}
    for a in anns:
        ntype = map_type(a.entity_type)
        if ntype is None:
            continue
        year = int(year_map.get(a.pmid, a.year) or 0)
        existing = nodes.get(a.concept_id)
        if existing is None:
            nodes[a.concept_id] = AggNode(a.concept_id, ntype, a.text, year)
        elif year and (existing.first_year == 0 or year < existing.first_year):
            existing.first_year = year
    return list(nodes.values())


def agg_edges_from_relations(
    rels: Sequence[Relation], valid_ids: Iterable[str],
    year_map: Mapping[str, int] | None = None,
) -> list[AggEdge]:
    """Arêtes agrégées PubTator (n_papers, first/last year, pmids), prédicats mappés."""
    year_map = year_map or {}
    valid = set(valid_ids)
    edges: dict[tuple[str, str, str], AggEdge] = {}
    for r in rels:
        pred = map_predicate(r.predicate)
        if pred is None or r.subject_id not in valid or r.object_id not in valid:
            continue
        if r.subject_id == r.object_id:
            continue
        year = int(year_map.get(r.pmid, r.year) or 0)
        key = (r.subject_id, pred, r.object_id)
        e = edges.get(key)
        if e is None:
            edges[key] = AggEdge(r.subject_id, r.object_id, pred, 1, year, year,
                                 [r.pmid] if r.pmid else [])
            continue
        e.n_papers += 1
        if r.pmid and r.pmid not in e.pmids:
            e.pmids.append(r.pmid)
        if year:
            e.first_year = year if e.first_year == 0 else min(e.first_year, year)
            e.last_year = max(e.last_year, year)
    return list(edges.values())


# Prédicat d'une arête de co-occurrence selon la paire de types (direction canonique),
# aligné sur les métaedges §7.1. PubTator n'annote que Gene/Chemical/Disease/CellType.
_COOC_PRED = {
    ("Chemical", "Gene"): "AFFECTS", ("Chemical", "Disease"): "CAUSES",
    ("Gene", "Disease"): "ASSOCIATED_WITH", ("CellType", "Disease"): "ASSOCIATED_WITH",
}


def _cooc_direction(ta: str, ia: str, tb: str, ib: str) -> tuple[str, str, str] | None:
    if (ta, tb) in _COOC_PRED:
        return _COOC_PRED[(ta, tb)], ia, ib
    if (tb, ta) in _COOC_PRED:
        return _COOC_PRED[(tb, ta)], ib, ia
    return None


def cooccurrence_edges(
    anns: Iterable[Annotation], year_map: Mapping[str, int] | None = None,
    max_entities: int = 30,
) -> list[AggEdge]:
    """Arêtes de co-occurrence (modèle Swanson) : entités co-citées dans un même article.

    Reconstruit les maillons que PubTator ne fournit pas explicitement. Les articles à plus
    de ``max_entities`` entités sont ignorés (bruit/explosion combinatoire).
    """
    year_map = year_map or {}
    by_pmid: dict[str, dict[str, str]] = {}
    for a in anns:
        nt = map_type(a.entity_type)
        if nt is not None:
            by_pmid.setdefault(a.pmid, {})[a.concept_id] = nt
    edges: dict[tuple[str, str, str], AggEdge] = {}
    for pmid, ents in by_pmid.items():
        if len(ents) > max_entities:
            continue
        year = int(year_map.get(pmid, 0) or 0)
        items = list(ents.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                direction = _cooc_direction(items[i][1], items[i][0],
                                            items[j][1], items[j][0])
                if direction is None:
                    continue
                _accumulate(edges, direction, pmid, year)
    return list(edges.values())


def _accumulate(edges: dict, direction: tuple[str, str, str], pmid: str, year: int) -> None:
    pred, s, o = direction
    key = (s, pred, o)
    e = edges.get(key)
    if e is None:
        edges[key] = AggEdge(s, o, pred, 1, year, year, [pmid] if pmid else [])
        return
    e.n_papers += 1
    if year:
        e.first_year = year if e.first_year == 0 else min(e.first_year, year)
        e.last_year = max(e.last_year, year)
