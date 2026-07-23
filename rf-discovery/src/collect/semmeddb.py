"""Lecture des dumps SemMedDB (§4) — substrat du graphe, licence UMLS gratuite.

NLM distribue SemMedDB en dumps MySQL (``INSERT INTO `PREDICATION` VALUES (...),(...);``).
On les lit en **flux** (fichier ``.sql`` ou ``.sql.gz``), sans MySQL, sans réseau : un
scanner tolérant aux guillemets échappés et aux virgules dans les chaînes extrait les
tuples. Un fallback TSV (colonnes dans l'ordre PREDICATION, sans en-tête) est accepté.

Table PREDICATION (VER43), colonnes dans l'ordre :
  PREDICATION_ID, SENTENCE_ID, PMID, PREDICATE, SUBJECT_CUI, SUBJECT_NAME,
  SUBJECT_SEMTYPE, SUBJECT_NOVELTY, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE, OBJECT_NOVELTY
"""
from __future__ import annotations

import csv
import gzip
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import IO


@dataclass(frozen=True)
class Predication:
    pmid: str
    predicate: str
    subject_cui: str
    subject_name: str
    subject_semtype: str
    object_cui: str
    object_name: str
    object_semtype: str


def _open(path: str | Path) -> IO[str]:
    p = Path(path)
    if p.suffix == ".gz":
        return gzip.open(p, "rt", encoding="utf-8", errors="replace")
    return open(p, encoding="utf-8", errors="replace")


def parse_value_tuples(segment: str) -> Iterator[list[str | None]]:
    """Scanne la portion après ``VALUES`` et rend chaque tuple comme liste de champs.

    Gère les chaînes ``'…'`` avec guillemets échappés (``\\'`` et ``''``), les virgules
    internes, et ``NULL`` -> ``None``.
    """
    field: list[str] = []
    row: list[str | None] = []
    in_str = False
    quoted = False
    depth = 0
    i, n = 0, len(segment)
    while i < n:
        ch = segment[i]
        if in_str:
            if ch == "\\" and i + 1 < n:
                field.append(segment[i + 1])
                i += 2
                continue
            if ch == "'" and i + 1 < n and segment[i + 1] == "'":
                field.append("'")
                i += 2
                continue
            if ch == "'":
                in_str = False
            else:
                field.append(ch)
        elif ch == "'":
            in_str, quoted = True, True
        elif ch == "(":
            depth, field, row, quoted = 1, [], [], False
        elif ch == "," and depth == 1:
            row.append(_finish_field(field, quoted))
            field, quoted = [], False
        elif ch == ")" and depth == 1:
            row.append(_finish_field(field, quoted))
            yield row
            depth = 0
        elif depth == 1:
            field.append(ch)  # champ non quoté (nombre, NULL)
        i += 1


def _finish_field(chars: list[str], quoted: bool) -> str | None:
    value = "".join(chars).strip()
    if not quoted and value.upper() == "NULL":
        return None
    return value if quoted else value


def iter_predications(path: str | Path, table: str = "PREDICATION") -> Iterator[Predication]:
    """Rend les prédications d'un dump SQL (streaming) ou d'un TSV sans en-tête."""
    p = Path(path)
    if p.suffix in (".tsv", ".csv"):
        yield from _iter_tsv(p)
        return
    marker = f"`{table}` VALUES"
    with _open(p) as fh:
        for line in fh:
            idx = line.find("VALUES")
            if marker not in line and "INSERT INTO" not in line:
                continue
            if idx < 0:
                continue
            for row in parse_value_tuples(line[idx + len("VALUES"):]):
                pred = _row_to_predication(row)
                if pred is not None:
                    yield pred


def _iter_tsv(path: Path) -> Iterator[Predication]:
    delim = "\t" if path.suffix == ".tsv" else ","
    with _open(path) as fh:
        for row in csv.reader(fh, delimiter=delim):
            pred = _row_to_predication(row)
            if pred is not None:
                yield pred


def _row_to_predication(row: list) -> Predication | None:
    if len(row) < 12:
        return None
    g = lambda x: "" if x is None else str(x)  # noqa: E731
    return Predication(
        pmid=g(row[2]), predicate=g(row[3]).upper(),
        subject_cui=g(row[4]), subject_name=g(row[5]), subject_semtype=g(row[6]),
        object_cui=g(row[8]), object_name=g(row[9]), object_semtype=g(row[10]),
    )


def parse_citations(path: str | Path, table: str = "CITATIONS") -> dict[str, int]:
    """Mappe PMID -> année de publication (PYEAR) depuis un dump CITATIONS."""
    year_map: dict[str, int] = {}
    marker = f"`{table}` VALUES"
    with _open(path) as fh:
        for line in fh:
            if marker not in line and "INSERT INTO" not in line:
                continue
            idx = line.find("VALUES")
            if idx < 0:
                continue
            for row in parse_value_tuples(line[idx + len("VALUES"):]):
                pmid, year = _citation_year(row)
                if pmid and year:
                    year_map[pmid] = year
    return year_map


def _citation_year(row: list) -> tuple[str, int]:
    if not row:
        return "", 0
    pmid = "" if row[0] is None else str(row[0])
    for field in reversed(row):  # PYEAR est en fin ; on prend la 1re année plausible
        s = "" if field is None else str(field).strip()
        if s.isdigit() and 1800 <= int(s) <= 2100:
            return pmid, int(s)
    return pmid, 0
