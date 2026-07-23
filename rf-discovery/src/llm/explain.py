"""Explication LLM d'un candidat DÉJÀ scoré (§8, usage 2).

Le LLM n'entre jamais dans le scoring : il reçoit un candidat classé et rend, en JSON
strict, un mécanisme plausible, l'expérience qui le testerait, et la faiblesse de
l'inférence. Tout échec se dégrade en ``None`` (le digest tombe en tableau brut).
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from llm.client import LLMClient, LLMUnavailable, parse_json
from score.rank import Candidate

_SCHEMA = {"mechanism": "str", "experiment": "str", "weakness": "str"}

_PROMPT = """Tu es un neurotoxicologue. Un moteur déterministe a proposé, SANS ton aide,
le lien mécanistique candidat ci-dessous (déjà scoré). N'invente pas de lien : explique
seulement celui-ci. Réponds en JSON strict avec les clés mechanism, experiment, weakness.

Candidat : {a} —(métachemin)—> {c}
Métachemin : {metapath}
z-score (vs null par permutation) : {z:.2f} ; p={p:.3g} ; DWPC={dwpc:.4g}
"""


@dataclass
class Explanation:
    a_id: str
    c_id: str
    mechanism: str
    experiment: str
    weakness: str


def explain_candidate(client: LLMClient, cand: Candidate) -> Explanation | None:
    """Explique un candidat ; ``None`` si le LLM est indisponible ou la sortie invalide."""
    prompt = _PROMPT.format(a=cand.a_id, c=cand.c_id, metapath=cand.metapath,
                            z=cand.z_score, p=cand.p_value, dwpc=cand.dwpc)
    try:
        raw = client.complete(prompt, schema=_SCHEMA)
    except LLMUnavailable:
        return None
    data = parse_json(raw)
    if not data or not all(k in data for k in _SCHEMA):
        return None
    return Explanation(cand.a_id, cand.c_id, str(data["mechanism"]),
                       str(data["experiment"]), str(data["weakness"]))


def explain_top(client: LLMClient, candidates: Sequence[Candidate], top: int = 20
                ) -> dict[tuple[str, str], Explanation]:
    """Explique les ``top`` meilleurs candidats ; renvoie un mapping (dégradation partielle OK)."""
    out: dict[tuple[str, str], Explanation] = {}
    for cand in list(candidates)[:top]:
        exp = explain_candidate(client, cand)
        if exp is not None:
            out[(cand.a_id, cand.c_id)] = exp
    return out
