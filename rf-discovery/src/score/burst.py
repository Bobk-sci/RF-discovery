"""Détection de rafales de Kleinberg (2002) — automate à deux états (§7.4).

Priorise les termes en accélération : un terme dont la fréquence relative passe en
régime « rafale » sur les périodes récentes reçoit un score élevé. Modèle discret à
deux états (base ``p0`` ; rafale ``s·p0``), coût de transition ``gamma``, décodage Viterbi.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np

_EPS = 1e-9


def _state_probs(r: np.ndarray, d: np.ndarray, s: float) -> tuple[float, float]:
    total_r, total_d = float(r.sum()), float(d.sum())
    p0 = total_r / total_d if total_d > 0 else 0.0
    p0 = min(max(p0, _EPS), 1 - _EPS)
    p1 = min(max(p0 * s, _EPS), 1 - _EPS)
    return p0, p1


def burst_states(r: Sequence[float], d: Sequence[float], s: float = 2.0, gamma: float = 1.0
                 ) -> list[int]:
    """Séquence d'états (0=base, 1=rafale) minimisant coût d'ajustement + transitions."""
    r_arr = np.asarray(r, dtype=np.float64)
    d_arr = np.asarray(d, dtype=np.float64)
    n = len(r_arr)
    if n == 0:
        return []
    probs = _state_probs(r_arr, d_arr, s)

    def sigma(i: int, t: int) -> float:
        p = probs[i]
        return -(r_arr[t] * np.log(p) + (d_arr[t] - r_arr[t]) * np.log(1 - p))

    cost = np.full((2, n), np.inf)
    back = np.zeros((2, n), dtype=int)
    for i in (0, 1):
        cost[i, 0] = sigma(i, 0) + (gamma if i == 1 else 0.0)
    for t in range(1, n):
        for j in (0, 1):
            options = [(cost[i, t - 1] + gamma * max(0, j - i), i) for i in (0, 1)]
            best_cost, best_prev = min(options)
            cost[j, t] = best_cost + sigma(j, t)
            back[j, t] = best_prev
    states = [0] * n
    states[-1] = 0 if cost[0, -1] <= cost[1, -1] else 1
    for t in range(n - 1, 0, -1):
        states[t - 1] = int(back[states[t], t])
    return states


def burst_score(r: Sequence[float], d: Sequence[float], s: float = 2.0, gamma: float = 1.0,
                recent: int = 3) -> float:
    """Score scalaire pondéré vers les périodes récentes (rafale récente = priorité)."""
    states = burst_states(r, d, s, gamma)
    if not states:
        return 0.0
    n = len(states)
    weights = np.array([(t + 1) / n for t in range(n)])
    weighted = float(np.dot(states, weights) / weights.sum())
    tail = float(np.mean(states[-recent:])) if n >= 1 else 0.0
    return 0.5 * weighted + 0.5 * tail
