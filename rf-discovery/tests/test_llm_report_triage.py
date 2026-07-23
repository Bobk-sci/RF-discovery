"""LLM périphérique (dégradation propre), digest, triage supervisé (M7, M9)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from llm.client import LLMClient, LLMUnavailable, parse_json
from llm.explain import explain_top
from report.digest import build_digest
from report.issue import failure_issue, weekly_issue
from score.rank import Candidate
from triage.classify import TriageClassifier, keyword_baseline_f1

CFG = Path(__file__).resolve().parents[1] / "config" / "llm.yaml"


def _cand(rank: int) -> Candidate:
    return Candidate(f"EXP{rank}", f"PHEN{rank}", "mp", 1.0, 3.0, 0.001, 0.2, 1.5, 0.4, rank)


def test_llm_unavailable_without_keys(monkeypatch):
    for var in ("GROQ_API_KEY", "CEREBRAS_API_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    client = LLMClient.from_config(CFG)
    assert client.available() == []
    try:
        client.complete("x")
        raise AssertionError("devait lever LLMUnavailable")
    except LLMUnavailable:
        pass


def test_digest_degrades_without_explanations():
    cands = [_cand(i) for i in range(1, 4)]
    md = build_digest(cands, run_date=date(2025, 1, 6),
                      gate={"auroc": 0.72, "passes_gate": True})
    assert "tableau brut" in md
    assert "AUROC=0.720" in md
    assert md.strip().count("|") > 0  # tableau markdown présent
    # les explications sont vides quand le LLM est indisponible -> pas d'échec.
    assert explain_top(LLMClient(providers=[]), cands) == {}


def test_issue_payloads():
    wk = weekly_issue(date(2025, 1, 6), "# digest")
    assert "weekly-digest" in wk.labels
    fail = failure_issue(date(2025, 1, 6), "boom", "trace")
    assert "pipeline-failure" in fail.labels and "boom" in fail.body


def test_parse_json_robust():
    assert parse_json('{"a": 1}') == {"a": 1}
    assert parse_json("not json") is None


def test_triage_beats_keyword_baseline():
    pos = [f"radiofrequency exposure oxidative stress developing brain case {i}" for i in range(10)]
    pos += [f"microwave SAR neuronal calcium influx hippocampus study {i}" for i in range(10)]
    neg = [f"quarterly telecom market revenue and pricing report {i}" for i in range(10)]
    neg += [f"medieval european agricultural history overview {i}" for i in range(10)]
    texts = pos + neg
    labels = [1] * 20 + [0] * 20
    clf_f1 = TriageClassifier.default(seed=0).cross_val_f1(texts, labels)
    base_f1 = keyword_baseline_f1(texts, labels, ["radiofrequency"])
    assert clf_f1 > 0.7
    assert clf_f1 >= base_f1
