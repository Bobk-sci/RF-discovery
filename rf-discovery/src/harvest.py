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
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from collect import europepmc, pubtator
from collect.pubtator import Annotation, Relation
from graph.schema import connect
from graph.store import insert_papers, upsert
from normalize.dedupe import dedupe, load_seen, save_seen
from normalize.entities import agg_edges_from_relations, agg_nodes_from_annotations

ROOT = Path(__file__).resolve().parents[1]
_PUBTATOR_BATCH = 100


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
    anns: list[Annotation] = []
    rels: list[Relation] = []
    for i in range(0, len(pmids), _PUBTATOR_BATCH):
        batch = pmids[i:i + _PUBTATOR_BATCH]
        a, r = pubtator.fetch_annotations(batch, fetcher=fetcher, cache_dir=cache_dir)
        anns.extend(a)
        rels.extend(r)
    return anns, rels


def harvest(
    db_path: str | Path,
    *,
    domains_path: str | Path | None = None,
    seen_path: str | Path | None = None,
    page_size: int = 100,
    epmc_fetcher=None,
    pubtator_fetcher=None,
    cache_dir: str = "data/cache",
) -> HarvestResult:
    """Collecte tous les domaines et met à jour le graphe DuckDB."""
    domains, rf_terms = _load_domains(domains_path or ROOT / "config" / "domains.yaml")
    seen_path = seen_path or ROOT / "data" / "seen.json"
    seen = load_seen(seen_path)
    all_papers: list = []
    all_anns: list[Annotation] = []
    all_rels: list[Relation] = []
    year_map: dict[str, int] = {}
    per_domain: dict[str, int] = {}
    for dom in domains:
        query = europepmc.build_query(dom["query"], rf_terms, dom.get("rf_terms_allowed", False))
        papers = europepmc.search(query, domain=dom["name"], page_size=page_size,
                                  fetcher=epmc_fetcher, cache_dir=cache_dir)
        fresh, seen = dedupe(papers, seen)
        per_domain[dom["name"]] = len(fresh)
        pmids = [p.pmid for p in fresh if p.pmid]
        for p in fresh:
            all_papers.append(p)
            if p.pmid:
                year_map[p.pmid] = p.year
        anns, rels = _fetch_pubtator(pmids, pubtator_fetcher, cache_dir)
        all_anns.extend(anns)
        all_rels.extend(rels)
    save_seen(seen_path, seen)
    nodes = agg_nodes_from_annotations(all_anns, year_map)
    edges = agg_edges_from_relations(all_rels, {n.node_id for n in nodes}, year_map)
    con = connect(db_path)
    insert_papers(con, all_papers)
    upsert(con, nodes, edges)
    con.close()
    return HarvestResult(len(all_papers), len(nodes), len(edges), per_domain)


def main() -> None:
    ap = argparse.ArgumentParser(description="Collecte littérature → graphe DuckDB")
    ap.add_argument("--db", default=str(ROOT / "data" / "graph.duckdb"))
    ap.add_argument("--domains", default=None)
    ap.add_argument("--page-size", type=int, default=100)
    args = ap.parse_args()
    result = harvest(args.db, domains_path=args.domains, page_size=args.page_size)
    print(json.dumps(result.__dict__, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
