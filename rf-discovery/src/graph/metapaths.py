"""Énumération des métachemins sur le métagraphe (§7.1).

Un métachemin est une séquence de métaedges typés reliant un ``source_type`` à un
``target_type``. Chaque métaedge du métagraphe est disponible dans les deux sens
(l'inverse est marqué ``inverse=True`` ; sa matrice est la transposée, cf. dwpc.py).
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Metaedge:
    src: str
    predicate: str
    dst: str
    inverse: bool = False

    def label(self) -> str:
        arrow = "<-" if self.inverse else "->"
        return f"{self.src} {arrow}{self.predicate}{arrow[::-1]} {self.dst}"


@dataclass(frozen=True)
class Metapath:
    edges: tuple[Metaedge, ...]

    @property
    def source_type(self) -> str:
        return self.edges[0].src

    @property
    def target_type(self) -> str:
        return self.edges[-1].dst

    def label(self) -> str:
        parts = [self.edges[0].src]
        for e in self.edges:
            arrow = "<--" if e.inverse else "-->"
            parts.append(f"{arrow[:2]}{e.predicate}{arrow[-1]} {e.dst}")
        return " ".join(parts)


@dataclass
class MetaGraph:
    node_types: set[str]
    metaedges: list[Metaedge]
    source_types: set[str]
    target_types: set[str]
    min_len: int
    max_len: int

    @classmethod
    def from_config(cls, path: str | Path) -> MetaGraph:
        cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        base = [Metaedge(s, p, d) for s, p, d in cfg["metaedges"]]
        both: list[Metaedge] = []
        for me in base:
            both.append(me)
            if me.src != me.dst:
                both.append(Metaedge(me.dst, me.predicate, me.src, inverse=True))
        return cls(
            node_types=set(cfg["node_types"]),
            metaedges=both,
            source_types=set(cfg["source_types"]),
            target_types=set(cfg["target_types"]),
            min_len=int(cfg["min_len"]),
            max_len=int(cfg["max_len"]),
        )

    def out_edges(self, node_type: str) -> list[Metaedge]:
        return [me for me in self.metaedges if me.src == node_type]


def enumerate_metapaths(mg: MetaGraph) -> list[Metapath]:
    """DFS bornée en longueur ; interdit la répétition d'un type de nœud (pas de cycle)."""
    results: list[Metapath] = []

    def walk(current: str, path: list[Metaedge], visited_types: set[str]) -> None:
        if len(path) >= mg.min_len and current in mg.target_types:
            results.append(Metapath(tuple(path)))
        if len(path) >= mg.max_len:
            return
        for me in mg.out_edges(current):
            if me.dst in visited_types:
                continue
            walk(me.dst, [*path, me], visited_types | {me.dst})

    for src in sorted(mg.source_types):
        walk(src, [], {src})
    return _dedupe(results)


def _dedupe(paths: Sequence[Metapath]) -> list[Metapath]:
    seen: set[str] = set()
    out: list[Metapath] = []
    for p in paths:
        lab = p.label()
        if lab not in seen:
            seen.add(lab)
            out.append(p)
    return out
