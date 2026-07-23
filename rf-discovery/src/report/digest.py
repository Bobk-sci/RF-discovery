"""Rédaction du digest hebdomadaire en markdown pur (§8, §12).

Dégradation propre : sans explication LLM, le digest tombe en tableau brut des candidats
scorés. Aucun HTML.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

from llm.explain import Explanation
from score.rank import Candidate


def _table(candidates: Sequence[Candidate], top: int) -> str:
    header = ("| # | source | cible | z | p | DWPC | novelty_z | embed | métachemin |\n"
              "|---|--------|-------|---|---|------|-----------|-------|------------|")
    rows = [
        f"| {c.composite_rank} | {c.a_id} | {c.c_id} | {c.z_score:.2f} | {c.p_value:.2g} "
        f"| {c.dwpc:.3g} | {c.novelty_z:.2f} | {c.embed_score:.2f} | {c.metapath} |"
        for c in list(candidates)[:top]
    ]
    return "\n".join([header, *rows])


def build_digest(
    candidates: Sequence[Candidate],
    *,
    run_date: date | None = None,
    explanations: Mapping[tuple[str, str], Explanation] | None = None,
    top: int = 20,
    gate: Mapping[str, object] | None = None,
) -> str:
    """Construit le digest markdown. ``explanations`` optionnel (dégradation si absent)."""
    run_date = run_date or date.today()
    lines = [f"# Digest RF-Discovery — {run_date.isoformat()}", ""]
    if gate is not None:
        auroc = gate.get("auroc")
        status = "✅ franchi" if gate.get("passes_gate") else "⛔ NON franchi"
        auroc_txt = f"{auroc:.3f}" if isinstance(auroc, (int, float)) else "n/a"
        lines += [f"**Gate time-slice** : AUROC={auroc_txt} ({status}).", ""]
    lines += [f"{len(candidates)} candidats scorés ; top {top} ci-dessous.", "",
              "## Candidats classés", "", _table(candidates, top), ""]
    if explanations:
        lines += ["## Explications (LLM, périphérique)", ""]
        for c in list(candidates)[:top]:
            exp = explanations.get((c.a_id, c.c_id))
            if exp is None:
                continue
            lines += [f"### {c.composite_rank}. {c.a_id} → {c.c_id}",
                      f"- **Mécanisme** : {exp.mechanism}",
                      f"- **Expérience test** : {exp.experiment}",
                      f"- **Faiblesse** : {exp.weakness}", ""]
    else:
        lines += ["_Explications LLM indisponibles ce run — tableau brut ci-dessus._", ""]
    lines += ["---", "_Moteur déterministe ; le LLM n'entre jamais dans le scoring._"]
    return "\n".join(lines)
