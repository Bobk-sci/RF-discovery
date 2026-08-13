"""Validation par time-slicing — gate bloquant (§9).

Graphe construit sur les seules arêtes ``first_year <= cutoff``. Positifs = arêtes
apparues dans ``(cutoff, end]`` entre types candidats (source→cible) absentes du graphe
d'entraînement. Négatifs = non-arêtes appariées en degré (ratio 1:neg_ratio). Les features
sont les DWPC par métachemin ; on entraîne une régression logistique et on reporte
AUROC/AUPRC/precision@k en validation croisée (scores hors-échantillon, non optimistes).

Gate : AUROC < 0.65 sur le hold-out ⇒ ne pas construire les étages supérieurs.
"""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

from graph.build import Edge, Graph, Node, build_graph
from graph.dwpc import dwpc_features
from graph.metapaths import MetaGraph, Metapath, enumerate_metapaths
from validate.metrics import evaluate

GATE_HARD_FLOOR = 0.65
GATE_TARGET = 0.70


def _load_meta(path: str | Path) -> tuple[MetaGraph, list[str]]:
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return MetaGraph.from_config(path), list(cfg.get("empty_hub_nodes", []))


def _degree_matched_negatives(
    graph: Graph, positives: list[tuple[int, int]], forbidden: set[tuple[int, int]],
    tgt_rows: np.ndarray, neg_ratio: int, rng: np.random.Generator,
) -> list[tuple[int, int]]:
    """Pour chaque positif, tire ``neg_ratio`` négatifs de même source, cible de degré voisin."""
    deg = graph.degree
    order = tgt_rows[np.argsort(deg[tgt_rows])]
    pos_in_order = {int(t): i for i, t in enumerate(order)}
    negatives: list[tuple[int, int]] = []
    for a, c in positives:
        centre = pos_in_order.get(c, len(order) // 2)
        lo, hi = max(0, centre - 50), min(len(order), centre + 50)
        window = order[lo:hi]
        picked = 0
        for cand in rng.permutation(window):
            cand = int(cand)
            if cand == c or (a, cand) in forbidden or (a, cand) in negatives:
                continue
            negatives.append((a, cand))
            picked += 1
            if picked >= neg_ratio:
                break
    return negatives


def build_dataset(
    nodes: Sequence[Node], edges: Sequence[Edge], metapaths_path: str | Path,
    *, cutoff: int, end: int, neg_ratio: int = 10, seed: int = 0, buffer_years: int = 0,
) -> tuple[Graph, list[Metapath], list[tuple[str, str]], np.ndarray]:
    mg, hubs = _load_meta(metapaths_path)
    metapaths = enumerate_metapaths(mg)
    train_edges = [e for e in edges if e.first_year <= cutoff]
    graph = build_graph(nodes, train_edges, exclude_nodes=hubs)
    ntype = {n.node_id: n.node_type for n in nodes}
    src_t, tgt_t = mg.source_types, mg.target_types
    existing = {(graph.index[e.source_id], graph.index[e.target_id])
                for e in train_edges
                if e.source_id in graph.index and e.target_id in graph.index}
    pos_idx: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for e in edges:
        if not (cutoff + buffer_years < e.first_year <= end):
            continue
        if ntype.get(e.source_id) not in src_t or ntype.get(e.target_id) not in tgt_t:
            continue
        if e.source_id not in graph.index or e.target_id not in graph.index:
            continue
        pair = (graph.index[e.source_id], graph.index[e.target_id])
        if pair in existing or pair in seen:
            continue
        seen.add(pair)
        pos_idx.append(pair)
    rng = np.random.default_rng(seed)
    tgt_rows = np.concatenate([graph.rows_of_type(t) for t in sorted(tgt_t)])
    forbidden = existing | seen
    neg_idx = _degree_matched_negatives(graph, pos_idx, forbidden, tgt_rows, neg_ratio, rng)
    all_idx = pos_idx + neg_idx
    labels = np.array([1] * len(pos_idx) + [0] * len(neg_idx), dtype=int)
    pairs = [(graph.node_ids[a], graph.node_ids[c]) for a, c in all_idx]
    return graph, metapaths, pairs, labels


def run_timeslice(
    nodes: Sequence[Node], edges: Sequence[Edge], metapaths_path: str | Path,
    *, cutoff: int = 2018, end: int = 2025, neg_ratio: int = 10, seed: int = 0,
    w: float = 0.4, n_splits: int = 5, buffer_years: int = 0,
) -> dict:
    """Exécute la validation et renvoie métriques + statut du gate.

    ``buffer_years`` laisse une zone morte entre la fin de l'entraînement et le début de la
    fenêtre de test : indispensable quand les années proviennent d'une estimation (PMID),
    pour qu'une erreur d'un an ne fasse pas basculer une arête du mauvais côté.
    """
    graph, metapaths, pairs, labels = build_dataset(
        nodes, edges, metapaths_path, cutoff=cutoff, end=end, neg_ratio=neg_ratio, seed=seed,
        buffer_years=buffer_years,
    )
    if labels.sum() == 0 or labels.sum() == len(labels):
        return {"error": "classes dégénérées", "n_positive": int(labels.sum()),
                "passes_gate": False, "n": int(len(labels))}
    feats = dwpc_features(graph, metapaths, pairs, w)
    x = StandardScaler().fit_transform(np.log1p(feats))
    clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed)
    n_splits = min(n_splits, int(labels.sum()), int((labels == 0).sum()))
    cv = StratifiedKFold(n_splits=max(2, n_splits), shuffle=True, random_state=seed)
    proba = cross_val_predict(clf, x, labels, cv=cv, method="predict_proba")[:, 1]
    metrics = evaluate(labels, proba, ks=(50,))
    metrics["passes_gate"] = bool(metrics["auroc"] >= GATE_HARD_FLOOR)
    metrics["meets_target"] = bool(metrics["auroc"] >= GATE_TARGET)
    metrics["n_metapaths"] = len(metapaths)
    return metrics
