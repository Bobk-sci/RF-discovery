"""Métriques de la validation rétrospective (§9).

L'AUPRC prime sur l'AUROC vu le déséquilibre de classes (positifs rares).
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def precision_at_k(y_true: np.ndarray, scores: np.ndarray, k: int) -> float:
    """Précision parmi les ``k`` candidats les mieux scorés."""
    if k <= 0 or len(scores) == 0:
        return 0.0
    k = min(k, len(scores))
    top = np.argsort(scores)[::-1][:k]
    return float(np.mean(np.asarray(y_true)[top]))


def evaluate(y_true: np.ndarray, scores: np.ndarray, ks: tuple[int, ...] = (50,)) -> dict:
    """AUROC, AUPRC et precision@k. Robuste au cas dégénéré (une seule classe)."""
    y_true = np.asarray(y_true, dtype=int)
    scores = np.asarray(scores, dtype=float)
    single_class = len(np.unique(y_true)) < 2
    out: dict[str, float] = {
        "auroc": float("nan") if single_class else float(roc_auc_score(y_true, scores)),
        "auprc": float("nan")
        if single_class
        else float(average_precision_score(y_true, scores)),
        "n": int(len(y_true)),
        "n_positive": int(y_true.sum()),
    }
    for k in ks:
        out[f"precision_at_{k}"] = precision_at_k(y_true, scores, k)
    return out
