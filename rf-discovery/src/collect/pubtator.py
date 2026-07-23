"""Collecte PubTator3 (§4) — entités pré-annotées et normalisées, réseau injectable.

PubTator3 fournit gratuitement l'extraction d'entités (Gene, Disease, Chemical, Species…)
et des relations sur tout PubMed : aucun token de LLM pour cette tâche (§4, principe de coût).
Le parsing (BioC-JSON) est pur ; ``fetch_annotations`` prend un ``fetcher`` injectable.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from collect.cache import get_json

Fetcher = Callable[[str, dict[str, Any]], Any]
_BASE = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson"


@dataclass
class Annotation:
    pmid: str
    concept_id: str      # identifiant normalisé (ex. MESH:D000544, 348 pour Entrez)
    entity_type: str     # Gene|Disease|Chemical|Species|CellLine…
    text: str
    year: int = 0


@dataclass
class Relation:
    pmid: str
    subject_id: str
    predicate: str
    object_id: str
    year: int = 0


def parse_biocjson(doc: dict[str, Any]) -> tuple[list[Annotation], list[Relation]]:
    """Extrait annotations + relations d'un document BioC-JSON PubTator3."""
    pmid = str(doc.get("pmid") or doc.get("id") or "")
    year = int(doc.get("year") or 0)
    anns: list[Annotation] = []
    for passage in doc.get("passages", []):
        for a in passage.get("annotations", []):
            infon = a.get("infons", {})
            cid = infon.get("identifier") or infon.get("normalized_id")
            if not cid or cid in ("-", "None"):
                continue
            anns.append(Annotation(pmid, str(cid), str(infon.get("type", "")),
                                   str(a.get("text", "")), year))
    rels: list[Relation] = []
    for r in doc.get("relations", []):
        infon = r.get("infons", {})
        subj, obj = infon.get("subject") or infon.get("role1"), \
            infon.get("object") or infon.get("role2")
        pred = infon.get("type") or infon.get("predicate") or "ASSOCIATED_WITH"
        if subj and obj:
            rels.append(Relation(pmid, str(subj), str(pred).upper(), str(obj), year))
    return anns, rels


def fetch_annotations(
    pmids: Sequence[str], *, fetcher: Fetcher | None = None, cache_dir: str = "data/cache"
) -> tuple[list[Annotation], list[Relation]]:
    """Récupère et parse les annotations PubTator3 pour une liste de PMIDs."""
    fetch = fetcher or (lambda u, p: get_json(u, p, cache_dir=cache_dir))
    params = {"pmids": ",".join(pmids)}
    data = fetch(_BASE, params)
    docs = data if isinstance(data, list) else (data or {}).get("PubTator3", [data])
    anns: list[Annotation] = []
    rels: list[Relation] = []
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        a, r = parse_biocjson(doc)
        anns.extend(a)
        rels.extend(r)
    return anns, rels
