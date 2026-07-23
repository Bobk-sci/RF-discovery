"""Déduplication des articles (§ M1).

Clé de dédup : PMID, sinon DOI, sinon titre normalisé. L'état persistant ``seen.json``
garantit qu'un rerun n'ajoute aucune ligne (critère d'acceptation M1).
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path

from collect.europepmc import Paper

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]")


def normalize_title(title: str) -> str:
    t = _PUNCT.sub(" ", title.lower())
    return _WS.sub(" ", t).strip()


def paper_key(paper: Paper) -> str:
    if paper.pmid:
        return f"pmid:{paper.pmid}"
    if paper.doi:
        return f"doi:{paper.doi.lower()}"
    return f"title:{normalize_title(paper.title)}"


def load_seen(path: str | Path) -> set[str]:
    p = Path(path)
    if p.exists():
        return set(json.loads(p.read_text(encoding="utf-8")))
    return set()


def save_seen(path: str | Path, seen: Iterable[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sorted(seen), ensure_ascii=False), encoding="utf-8")


def dedupe(papers: Iterable[Paper], seen: set[str]) -> tuple[list[Paper], set[str]]:
    """Renvoie les articles inédits et l'ensemble ``seen`` mis à jour (idempotent)."""
    fresh: list[Paper] = []
    updated = set(seen)
    batch: set[str] = set()
    for paper in papers:
        key = paper_key(paper)
        if key in updated or key in batch:
            continue
        batch.add(key)
        fresh.append(paper)
    updated |= batch
    return fresh, updated
