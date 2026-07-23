"""Normalisation SemMedDB → nœuds/arêtes typés (§ M3).

Mappe les types sémantiques UMLS vers les types de nœuds, filtre les prédicats hors de
l'ensemble retenu (config/metapaths.yaml), rejette les prédications négatives (``NEG_*``)
et les hubs sémantiques vides. Agrège les arêtes multi-articles (n_papers, first/last year).
Pour les gènes, l'identifiant Entrez encodé dans le CUI (``C…|1017``) est préféré afin de
maximiser la jointure avec les nœuds PubTator (qui utilisent l'Entrez).
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml

from collect.semmeddb import Predication
from normalize.records import AggEdge, AggNode

__all__ = ["AggEdge", "AggNode", "SemMedConfig", "build_nodes_edges", "normalize_cui"]


@dataclass
class SemMedConfig:
    semtype_map: dict[str, str]
    exposure_cuis: set[str]
    predicates: set[str]
    empty_hubs: set[str]

    @classmethod
    def load(cls, semtypes_path: str | Path, metapaths_path: str | Path) -> SemMedConfig:
        st = yaml.safe_load(Path(semtypes_path).read_text(encoding="utf-8"))
        mp = yaml.safe_load(Path(metapaths_path).read_text(encoding="utf-8"))
        return cls(
            semtype_map=dict(st.get("semtype_map", {})),
            exposure_cuis=set(st.get("exposure_cuis", []) or []),
            predicates=set(mp.get("predicates", [])),
            empty_hubs=set(mp.get("empty_hub_nodes", [])),
        )


def _node_type(cui_token0: str, semtype: str, cfg: SemMedConfig) -> str | None:
    if cui_token0 in cfg.exposure_cuis:
        return "Exposure"
    return cfg.semtype_map.get(semtype.lower())


def normalize_cui(cui: str, node_type: str) -> str:
    """Identifiant normalisé : Entrez pour les gènes si présent, sinon le CUI."""
    tokens = [t.strip() for t in cui.split("|") if t.strip()]
    if not tokens:
        return cui.strip()
    if node_type == "Gene":
        for tok in tokens:
            if tok.isdigit():
                return tok
    return tokens[0]


def build_nodes_edges(
    preds: Iterable[Predication], year_map: Mapping[str, int], cfg: SemMedConfig
) -> tuple[list[AggNode], list[AggEdge]]:
    """Transforme un flux de prédications en nœuds/arêtes agrégés et filtrés."""
    nodes: dict[str, AggNode] = {}
    edges: dict[tuple[str, str, str], AggEdge] = {}
    for p in preds:
        if p.predicate.startswith("NEG_") or p.predicate not in cfg.predicates:
            continue
        s_type = _node_type(p.subject_cui.split("|")[0].strip(), p.subject_semtype, cfg)
        o_type = _node_type(p.object_cui.split("|")[0].strip(), p.object_semtype, cfg)
        if s_type is None or o_type is None:
            continue
        s_id = normalize_cui(p.subject_cui, s_type)
        o_id = normalize_cui(p.object_cui, o_type)
        if s_id == o_id or s_id in cfg.empty_hubs or o_id in cfg.empty_hubs:
            continue
        year = int(year_map.get(p.pmid, 0))
        _upsert_node(nodes, s_id, s_type, p.subject_name, year)
        _upsert_node(nodes, o_id, o_type, p.object_name, year)
        _upsert_edge(edges, s_id, o_id, p.predicate, p.pmid, year)
    return list(nodes.values()), list(edges.values())


def _upsert_node(nodes: dict, node_id: str, node_type: str, name: str, year: int) -> None:
    existing = nodes.get(node_id)
    if existing is None:
        nodes[node_id] = AggNode(node_id, node_type, name, year or 0)
    elif year and (existing.first_year == 0 or year < existing.first_year):
        existing.first_year = year


def _upsert_edge(edges: dict, s: str, o: str, pred: str, pmid: str, year: int) -> None:
    key = (s, pred, o)
    e = edges.get(key)
    if e is None:
        edges[key] = AggEdge(s, o, pred, 1, year or 0, year or 0, [pmid] if pmid else [])
        return
    e.n_papers += 1
    if pmid and pmid not in e.pmids:
        e.pmids.append(pmid)
    if year:
        e.first_year = year if e.first_year == 0 else min(e.first_year, year)
        e.last_year = max(e.last_year, year)
