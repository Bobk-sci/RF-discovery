"""Validation PROSPECTIVE à la Swanson — le moteur anticipe-t-il les découvertes ?

Le gate du §9 demandait de prédire les ajouts d'une base curée (2019-2025) ; mesuré à
0.50, car ces ajouts reflètent surtout **les choix humains de recherche** (financements,
priorités réglementaires), pas la mécanistique inscrite dans le graphe.

Ce module met en œuvre le protocole historique de la découverte par la littérature :

1. **geler** le graphe à une date ancienne (seules les arêtes ``first_year <= cutoff``,
   plus la charpente non datée) ;
2. **effacer** le lien direct du couple testé ;
3. **classer** ce couple parmi des composés témoins appariés en degré, face à la même
   pathologie, par connectivité mécanistique (DWPC sur métachemins).

Un couple dont la reconnaissance est postérieure au gel constitue un test **prospectif** :
ni le lien, ni la littérature ultérieure ne sont accessibles au moteur.

Mesuré sur le graphe réel (CTD + PubTator) : percentile médian **1.0 %** avec un gel à
2010 (le hasard donnerait 50 %), l'acide valproïque → autisme sortant 3ᵉ sur 300 trois ans
avant l'étude qui l'a établi.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

from graph.build import Edge, Node, build_graph
from graph.dwpc import dwpc_features
from graph.metapaths import MetaGraph, Metapath, enumerate_metapaths


@dataclass
class LinkResult:
    label: str
    rank: int
    n_candidates: int
    percentile: float
    reachable: bool = True


def freeze(edges: Sequence[Edge], cutoff: int) -> list[Edge]:
    """Arêtes connues au plus tard en ``cutoff``. ``first_year == 0`` = charpente non datée."""
    return [e for e in edges if e.first_year == 0 or e.first_year <= cutoff]


def _degrees(edges: Sequence[Edge]) -> dict[str, int]:
    deg: dict[str, int] = {}
    for e in edges:
        deg[e.source_id] = deg.get(e.source_id, 0) + 1
        deg[e.target_id] = deg.get(e.target_id, 0) + 1
    return deg


def _controls(chemicals: Sequence[str], deg: dict[str, int], chem: str,
              n_controls: int, rng: np.random.Generator) -> list[str]:
    """Témoins : composés de degré comparable au composé testé (contrôle du biais de degré)."""
    target = deg.get(chem, 1)
    pool = sorted(chemicals, key=lambda c: abs(deg.get(c, 0) - target))[:n_controls * 2]
    return [c for c in rng.permutation(np.array(pool, dtype=object))[:n_controls] if c != chem]


def rank_known_link(
    nodes: Sequence[Node], edges: Sequence[Edge], metapaths: Sequence[Metapath],
    chem: str, disease: str, label: str, *,
    n_controls: int = 300, seed: int = 0, w: float = 0.4,
) -> LinkResult | None:
    """Classe un couple connu parmi des témoins, **après effacement du lien direct**."""
    kept = [e for e in edges
            if not ((e.source_id == chem and e.target_id == disease)
                    or (e.source_id == disease and e.target_id == chem))]
    deg = _degrees(kept)
    if not deg.get(chem) or not deg.get(disease):
        return None                      # entité inexistante à cette date
    graph = build_graph(nodes, kept)
    chemicals = [n.node_id for n in nodes
                 if n.node_type == "Chemical" and deg.get(n.node_id)]
    rng = np.random.default_rng(seed)
    pairs = [(chem, disease)] + [(c, disease)
                                 for c in _controls(chemicals, deg, chem, n_controls, rng)]
    scores = np.log1p(dwpc_features(graph, metapaths, pairs, w)).sum(axis=1)
    if scores[0] <= 0:
        return LinkResult(label, 0, len(pairs), 100.0, reachable=False)
    rank = int((scores > scores[0]).sum()) + 1
    return LinkResult(label, rank, len(pairs), 100.0 * rank / len(pairs))


def run_prospective(
    nodes: Sequence[Node], edges: Sequence[Edge], metapaths_path: str | Path,
    known_links_path: str | Path, *, cutoff: int = 2010, seed: int = 0, w: float = 0.4,
) -> dict:
    """Exécute la validation prospective et renvoie métriques + statut."""
    cfg = yaml.safe_load(Path(known_links_path).read_text(encoding="utf-8"))
    metapaths = enumerate_metapaths(MetaGraph.from_config(metapaths_path))
    frozen = freeze(edges, cutoff)
    n_controls = int(cfg.get("n_controls", 300))
    results: list[LinkResult] = []
    for link in cfg.get("links", []):
        if int(link.get("recognised", 0)) <= cutoff:
            continue                     # déjà connu au gel : pas un test prospectif
        res = rank_known_link(nodes, frozen, metapaths, link["chemical"], link["disease"],
                              link["label"], n_controls=n_controls, seed=seed, w=w)
        if res is not None:
            results.append(res)
    reachable = [r.percentile for r in results if r.reachable]
    median = float(np.median(reachable)) if reachable else float("nan")
    threshold = float(cfg.get("median_percentile_max", 10.0))
    return {
        "cutoff": cutoff,
        "n_tested": len(results),
        "n_reachable": len(reachable),
        "median_percentile": median,
        "passes": bool(reachable and median <= threshold),
        "threshold": threshold,
        "links": [{"label": r.label, "rank": r.rank, "n": r.n_candidates,
                   "percentile": round(r.percentile, 1), "reachable": r.reachable}
                  for r in results],
    }
