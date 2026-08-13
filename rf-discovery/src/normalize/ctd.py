"""Normalisation CTD → nœuds/arêtes typés (§ M3).

Identifiants alignés sur ceux de PubTator pour que les deux substrats se **joignent** :
- chimiques et maladies : ``MESH:xxx`` (CTD donne le MeSH nu pour les chimiques),
- gènes : identifiant Entrez nu (comme PubTator),
- voies : ``REACT:...`` / ``KEGG:...`` tels quels.

Les relations chimique-gène, gène-maladie et chimique-maladie sont **datées** via les PMID
(cf. ``pmid_year``). Les associations gène→voie n'ont pas de date : ce sont des arêtes de
**charpente** (``first_year = 0``), toujours présentes, qui referment les métachemins.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping

from normalize.pmid_year import first_year
from normalize.records import AggEdge, AggNode

# Premier verbe d'InteractionActions -> prédicat du métagraphe.
_ACTION_PRED = {"increases": "STIMULATES", "decreases": "INHIBITS", "affects": "AFFECTS"}
# Organismes retenus par défaut (humain, souris, rat) : le reste est écarté.
DEFAULT_ORGANISMS = frozenset({"9606", "10090", "10116"})


def mesh(value: str) -> str:
    """Préfixe ``MESH:`` si absent (CTD donne ``D001151``, PubTator ``MESH:D001151``)."""
    v = value.strip()
    if not v:
        return ""
    return v if ":" in v else f"MESH:{v}"


def _pred_from_actions(actions: str) -> str:
    verb = actions.split("|")[0].split("^")[0].strip().lower()
    return _ACTION_PRED.get(verb, "AFFECTS")


class Accumulator:
    """Agrège nœuds et arêtes en dédupliquant (mêmes clés que le substrat PubTator)."""

    def __init__(self) -> None:
        self.nodes: dict[str, AggNode] = {}
        self.edges: dict[tuple[str, str, str], AggEdge] = {}

    def node(self, node_id: str, node_type: str, name: str, year: int = 0) -> None:
        existing = self.nodes.get(node_id)
        if existing is None:
            self.nodes[node_id] = AggNode(node_id, node_type, name, year)
        elif year and (existing.first_year == 0 or year < existing.first_year):
            existing.first_year = year

    def edge(self, source: str, predicate: str, target: str, year: int) -> None:
        if not source or not target or source == target:
            return
        key = (source, predicate, target)
        e = self.edges.get(key)
        if e is None:
            self.edges[key] = AggEdge(source, target, predicate, 1, year, year, [])
            return
        e.n_papers += 1
        if year:
            e.first_year = year if e.first_year == 0 else min(e.first_year, year)
            e.last_year = max(e.last_year, year)


def add_chem_gene(acc: Accumulator, rows: Iterable[Mapping[str, str]],
                  organisms: frozenset[str] = DEFAULT_ORGANISMS) -> int:
    """Chimique →(STIMULATES/INHIBITS/AFFECTS)→ Gène, daté par PMID."""
    kept = 0
    for r in rows:
        if organisms and r.get("OrganismID", "").strip() not in organisms:
            continue
        chem, gene = mesh(r.get("ChemicalID", "")), r.get("GeneID", "").strip()
        if not chem or not gene:
            continue
        year = first_year(r.get("PubMedIDs", ""))
        acc.node(chem, "Chemical", r.get("ChemicalName", ""), year)
        acc.node(gene, "Gene", r.get("GeneSymbol", ""), year)
        acc.edge(chem, _pred_from_actions(r.get("InteractionActions", "")), gene, year)
        kept += 1
    return kept


def add_gene_disease(acc: Accumulator, rows: Iterable[Mapping[str, str]]) -> int:
    """Gène →ASSOCIATED_WITH→ Maladie, restreint aux preuves **directes** (curées)."""
    kept = 0
    for r in rows:
        if not r.get("DirectEvidence", "").strip():
            continue
        gene, disease = r.get("GeneID", "").strip(), mesh(r.get("DiseaseID", ""))
        if not gene or not disease:
            continue
        year = first_year(r.get("PubMedIDs", ""))
        acc.node(gene, "Gene", r.get("GeneSymbol", ""), year)
        acc.node(disease, "Disease", r.get("DiseaseName", ""), year)
        acc.edge(gene, "ASSOCIATED_WITH", disease, year)
        kept += 1
    return kept


def add_chem_disease(acc: Accumulator, rows: Iterable[Mapping[str, str]]) -> int:
    """Chimique →CAUSES→ Maladie, restreint aux preuves **directes** (curées)."""
    kept = 0
    for r in rows:
        if not r.get("DirectEvidence", "").strip():
            continue
        chem, disease = mesh(r.get("ChemicalID", "")), mesh(r.get("DiseaseID", ""))
        if not chem or not disease:
            continue
        year = first_year(r.get("PubMedIDs", ""))
        acc.node(chem, "Chemical", r.get("ChemicalName", ""), year)
        acc.node(disease, "Disease", r.get("DiseaseName", ""), year)
        acc.edge(chem, "CAUSES", disease, year)
        kept += 1
    return kept


def add_gene_pathway(acc: Accumulator, rows: Iterable[Mapping[str, str]]) -> int:
    """Gène →PARTICIPATES_IN→ Voie : charpente mécanistique (sans date)."""
    kept = 0
    for r in rows:
        gene, pathway = r.get("GeneID", "").strip(), r.get("PathwayID", "").strip()
        if not gene or not pathway:
            continue
        acc.node(gene, "Gene", r.get("GeneSymbol", ""), 0)
        acc.node(pathway, "Pathway", r.get("PathwayName", ""), 0)
        acc.edge(gene, "PARTICIPATES_IN", pathway, 0)
        kept += 1
    return kept


def restrict_to_genes(acc: Accumulator, keep: Iterable[str]) -> None:
    """Ne garde que le voisinage des gènes d'intérêt (limite la taille du graphe).

    Une arête est conservée si l'une de ses extrémités est un gène retenu ; les nœuds
    devenus isolés sont supprimés.
    """
    keep_set = set(keep)
    if not keep_set:
        return
    kept_edges = {k: e for k, e in acc.edges.items()
                  if e.source_id in keep_set or e.target_id in keep_set}
    acc.edges = kept_edges
    used: set[str] = set()
    for e in kept_edges.values():
        used.update((e.source_id, e.target_id))
    acc.nodes = {nid: n for nid, n in acc.nodes.items() if nid in used}


def iter_limited(rows: Iterator[Mapping[str, str]], limit: int | None) -> Iterator:
    """Borne un flux de lignes (``None`` = pas de limite)."""
    if limit is None:
        yield from rows
        return
    for i, row in enumerate(rows):
        if i >= limit:
            return
        yield row
