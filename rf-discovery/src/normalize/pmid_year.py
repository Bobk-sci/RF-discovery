"""Estimation de l'année de publication à partir du PMID.

Les PMID sont attribués de façon quasi chronologique : on interpole linéairement entre
des points d'ancrage (PMID observé en début d'année). CTD référence ses relations par
PMID sans donner l'année ; cette estimation permet de dater les arêtes pour le
time-slicing sans aucun appel réseau.

**Limite assumée** : précision de l'ordre de ±1 an, et quelques articles anciens indexés
tardivement reçoivent un PMID élevé. La validation (§9) compense en laissant une **année
tampon** entre la fin de l'entraînement et le début de la fenêtre de test, afin qu'une
erreur d'un an ne fasse pas basculer une arête du mauvais côté du découpage.
"""
from __future__ import annotations

import bisect

# (PMID approximatif en début d'année, année). Ancres approximatives, ordre croissant.
_ANCHORS: list[tuple[int, int]] = [
    (1, 1975), (1_900_000, 1990), (7_500_000, 1995), (10_600_000, 2000),
    (15_600_000, 2005), (19_800_000, 2010), (23_000_000, 2013), (25_300_000, 2015),
    (26_700_000, 2016), (28_000_000, 2017), (29_200_000, 2018), (30_500_000, 2019),
    (31_800_000, 2020), (33_300_000, 2021), (34_800_000, 2022), (36_400_000, 2023),
    (38_000_000, 2024), (39_500_000, 2025),
]
_PMIDS = [a[0] for a in _ANCHORS]
_YEARS = [a[1] for a in _ANCHORS]


def year_from_pmid(pmid: str | int) -> int:
    """Année estimée pour un PMID (0 si non exploitable)."""
    try:
        value = int(str(pmid).strip())
    except (TypeError, ValueError):
        return 0
    if value <= 0:
        return 0
    if value >= _PMIDS[-1]:
        return _YEARS[-1]
    idx = bisect.bisect_right(_PMIDS, value) - 1
    if idx < 0:
        return _YEARS[0]
    if idx >= len(_PMIDS) - 1:
        return _YEARS[-1]
    lo_pmid, lo_year = _PMIDS[idx], _YEARS[idx]
    hi_pmid, hi_year = _PMIDS[idx + 1], _YEARS[idx + 1]
    span = hi_pmid - lo_pmid
    frac = (value - lo_pmid) / span if span else 0.0
    return int(round(lo_year + frac * (hi_year - lo_year)))


def first_year(pmids: str, sep: str = "|") -> int:
    """Année la plus ancienne d'une liste de PMID (champ CTD ``PubMedIDs``)."""
    years = [year_from_pmid(p) for p in pmids.split(sep) if p.strip()]
    positive = [y for y in years if y > 0]
    return min(positive) if positive else 0
