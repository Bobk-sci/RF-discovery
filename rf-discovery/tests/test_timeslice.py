"""Le gate time-slice : sur le graphe synthétique structuré, AUROC > 0.65 (M6, §9)."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from synthetic import generate
from validate.metrics import evaluate, precision_at_k
from validate.timeslice import GATE_HARD_FLOOR, run_timeslice

CFG = Path(__file__).resolve().parents[1] / "config" / "metapaths.yaml"


def test_gate_passes_on_structured_graph():
    sg = generate(seed=0)
    metrics = run_timeslice(sg.nodes, sg.edges, CFG, seed=0)
    assert metrics["n_positive"] > 5, "il faut des positifs futurs"
    assert metrics["auroc"] >= GATE_HARD_FLOOR, f"AUROC={metrics['auroc']:.3f} sous le gate"
    assert metrics["passes_gate"] is True


def test_metrics_helpers():
    y = np.array([1, 0, 1, 0])
    s = np.array([0.9, 0.1, 0.8, 0.2])
    assert precision_at_k(y, s, 2) == 1.0
    out = evaluate(y, s, ks=(2,))
    assert out["auroc"] == 1.0
    assert out["precision_at_2"] == 1.0
