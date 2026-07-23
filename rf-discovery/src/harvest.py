"""Collecte de la littérature → graphe DuckDB (chef d'orchestre, M1–M3).

Pour chaque domaine de ``config/domains.yaml`` : interroge Europe PMC (PMIDs + résumés),
déduplique via ``seen.json``, récupère les entités/relations PubTator3 (par lots), normalise
et écrit nœuds/arêtes/articles dans DuckDB. Règle §3 respectée en amont : un domaine-pont
(``rf_terms_allowed: false``) est interrogé SANS aucun terme RF.

Réseau injectable (``epmc_fetcher``/``pubtator_fetcher``) : les tests utilisent des fixtures,
jamais le réseau. En production (Actions, ou machine avec réseau ouvert), les fetchers par
défaut passent par le cache disque + backoff de ``collect.cache``.
"""
from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from collect import europepmc, pubtator
from collect.pubtator import Annotation, Relation
from graph.schema import connect
from graph.store import insert_papers, upsert
from normalize.dedupe import dedupe, load_seen, save_seen
from normalize.entities import (
    agg_edges_from_relations,
    agg_nodes_from_annotations,
    cooccurrence_edges,
)
from normalize.records import AggEdge, AggNode

ROOT = Path(__file__).resolve().parents[1]
_PUBTATOR_BATCH = 100
_EXPOSURE_ID = "RF_EMF"
# Prédicat de l'arête Exposure -> entité, selon le type de la cible (métaedges §7.1).
_EXPOSURE_PRED = {"Gene": "AFFECTS", "Chemical": "AUGMENTS", "Pathway": "DISRUPTS",
                  "Phenotype": "CAUSES", "Disease": "CAUSES", "CellType": "AFFECTS",
                  "BrainRegion": "AFFECTS"}


@dataclass
class HarvestResult:
    n_papers: int
    n_nodes: int
    n_edges: int
    per_domain: dict[str, int] = field(default_factory=dict)


def _load_domains(path: str | Path) -> tuple[list[dict], list[str]]:
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return cfg.get("domains", []), cfg.get("rf_terms", [])


def _fetch_pubtator(pmids, fetcher, cache_dir) -> tuple[list[Annotation], list[Relation]]:
    """PubTator3 n'accepte que des PMID numériques ; un lot en échec est ignoré, pas fatal."""
    numeric = [p for p in pmids if p.isdigit()]
    anns: list[Annotation] = []
    rels: list[Relation] = []
    for i in range(0, len(numeric), _PUBTATOR_BATCH):
        batch = numeric[i:i + _PUBTATOR_BATCH]
        try:
            a, r = pubtator.fetch_annotations(batch, fetcher=fetcher, cache_dir=cache_dir)
        except Exception as exc:  # un lot problématique ne doit pas tuer la collecte
            logging.warning("lot PubTator ignoré (%d PMIDs) : %s", len(batch), exc)
            continue
        anns.extend(a)
        rels.extend(r)
    return anns, rels


def _inject_exposure(
    nodes: list[AggNode], rf_years: dict[str, int]
) -> tuple[list[AggNode], list[AggEdge]]:
    """Injecte un nœud Exposure ``RF_EMF`` relié aux entités des articles RF (modèle Swanson).

    Les articles-source (interrogés AVEC termes RF) définissent le voisinage de l'exposition :
    leurs entités deviennent les cibles directes de ``RF_EMF``, ouvrant les métachemins
    Exposure → Gene/Chemical → … → Phénotype/Maladie que le DWPC exploite.
    """
    type_by_id = {n.node_id: n.node_type for n in nodes}
    linked = {eid: yr for eid, yr in rf_years.items() if eid in type_by_id}
    if not linked:
        return [], []
    first = min(linked.values())
    exp_node = AggNode(_EXPOSURE_ID, "Exposure", "Radiofrequency EMF exposure", first)
    edges = [AggEdge(_EXPOSURE_ID, eid, _EXPOSURE_PRED.get(type_by_id[eid], "AFFECTS"),
                     1, yr, yr, []) for eid, yr in linked.items()]
    return [exp_node], edges


def harvest(
    db_path: str | Path,
    *,
    domains_path: str | Path | None = None,
    seen_path: str | Path | None = None,
    page_size: int = 1000,
    max_results: int = 1000,
    epmc_fetcher=None,
    pubtator_fetcher=None,
    cache_dir: str = "data/cache",
) -> HarvestResult:
    """Collecte tous les domaines (paginée) et met à jour le graphe DuckDB."""
    domains, rf_terms = _load_domains(domains_path or ROOT / "config" / "domains.yaml")
    seen_path = seen_path or ROOT / "data" / "seen.json"
    seen = load_seen(seen_path)
    all_papers: list = []
    all_anns: list[Annotation] = []
    all_rels: list[Relation] = []
    year_map: dict[str, int] = {}
    rf_years: dict[str, int] = {}   # entités vues dans les domaines-source RF -> année
    per_domain: dict[str, int] = {}
    for dom in domains:
        try:
            query = europepmc.build_query(dom["query"], rf_terms,
                                          dom.get("rf_terms_allowed", False))
            papers = europepmc.search(query, domain=dom["name"], page_size=page_size,
                                      max_results=max_results, fetcher=epmc_fetcher,
                                      cache_dir=cache_dir)
            fresh, seen = dedupe(papers, seen)
        except Exception as exc:  # un domaine en échec n'annule pas les autres
            logging.warning("domaine %s ignoré : %s", dom["name"], exc)
            per_domain[dom["name"]] = 0
            continue
        per_domain[dom["name"]] = len(fresh)
        pmids = [p.pmid for p in fresh if p.pmid]
        for p in fresh:
            all_papers.append(p)
            if p.pmid:
                year_map[p.pmid] = p.year
        anns, rels = _fetch_pubtator(pmids, pubtator_fetcher, cache_dir)
        all_anns.extend(anns)
        all_rels.extend(rels)
        if dom.get("rf_terms_allowed", False):   # entités co-mentionnées avec l'exposition RF
            for a in anns:
                yr = year_map.get(a.pmid, a.year) or 0
                if yr and (a.concept_id not in rf_years or yr < rf_years[a.concept_id]):
                    rf_years[a.concept_id] = yr
    save_seen(seen_path, seen)
    nodes = agg_nodes_from_annotations(all_anns, year_map)
    edges = agg_edges_from_relations(all_rels, {n.node_id for n in nodes}, year_map)
    # PubTator donne peu de relations explicites -> on reconstruit les maillons manquants
    # par co-occurrence d'entités dans un même article (modèle Swanson).
    edges += cooccurrence_edges(all_anns, year_map)
    exp_nodes, exp_edges = _inject_exposure(nodes, rf_years)
    con = connect(db_path)
    insert_papers(con, all_papers)
    upsert(con, nodes + exp_nodes, edges + exp_edges)
    n_nodes = (con.execute("SELECT count(*) FROM nodes").fetchone() or (0,))[0]  # dédupliqué
    n_edges = (con.execute("SELECT count(*) FROM edges").fetchone() or (0,))[0]
    con.close()
    return HarvestResult(len(all_papers), int(n_nodes), int(n_edges), per_domain)


def main() -> None:
    ap = argparse.ArgumentParser(description="Collecte littérature → graphe DuckDB")
    ap.add_argument("--db", default=str(ROOT / "data" / "graph.duckdb"))
    ap.add_argument("--domains", default=None)
    ap.add_argument("--page-size", type=int, default=1000)
    ap.add_argument("--max-results", type=int, default=1000,
                    help="articles max par domaine (pagination Europe PMC)")
    args = ap.parse_args()
    result = harvest(args.db, domains_path=args.domains, page_size=args.page_size,
                     max_results=args.max_results)
    print(json.dumps(result.__dict__, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
