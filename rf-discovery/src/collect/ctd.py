"""Collecte CTD — Comparative Toxicogenomics Database (§4, source gratuite).

CTD fournit des relations **curées manuellement** avec leurs références PubMed :
chimique↔gène, gène↔maladie, chimique↔maladie, et surtout **gène→voie biologique**
(Reactome/KEGG) — le maillon que PubTator ne fournit pas et qui casse les métachemins.

Usage académique libre (citer CTD ; une licence est requise pour un usage commercial).
Les fichiers sont téléchargés **en flux** vers ``data/cache/ctd/`` (un rerun ne
retélécharge pas) puis lus **ligne à ligne** : jamais tout le fichier en mémoire.

Format CTD : lignes de commentaires ``#``, dont la dernière contient les noms de colonnes
séparés par des tabulations ; puis les lignes de données.
"""
from __future__ import annotations

import gzip
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import IO

BASE_URL = "https://ctdbase.org/reports"

# Fichiers utilisés. Les trois premiers portent des PMIDs (donc datables) ;
# genes_pathways est la charpente mécanistique (sans date).
FILES = {
    "chem_gene": "CTD_chem_gene_ixns.tsv.gz",
    "gene_disease": "CTD_genes_diseases.tsv.gz",
    "chem_disease": "CTD_chemicals_diseases.tsv.gz",
    "gene_pathway": "CTD_genes_pathways.tsv.gz",
}


def download(name: str, cache_dir: str | Path = "data/cache/ctd",
             base_url: str = BASE_URL, chunk: int = 1 << 20) -> Path:
    """Télécharge un dump CTD en flux (ignoré s'il est déjà en cache)."""
    filename = FILES.get(name, name)
    target = Path(cache_dir) / filename
    if target.exists() and target.stat().st_size > 0:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    import requests  # import tardif : le module reste importable hors réseau

    tmp = target.with_suffix(target.suffix + ".part")
    with requests.get(f"{base_url}/{filename}", stream=True, timeout=300) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as fh:
            for block in resp.iter_content(chunk_size=chunk):
                fh.write(block)
    tmp.rename(target)
    return target


def _open(path: str | Path) -> IO[str]:
    p = Path(path)
    if p.suffix == ".gz":
        return gzip.open(p, "rt", encoding="utf-8", errors="replace")
    return open(p, encoding="utf-8", errors="replace")


def iter_rows(path: str | Path, limit: int | None = None,
              prefilter: Callable[[str], bool] | None = None) -> Iterator[dict[str, str]]:
    """Rend chaque ligne de données en dict {colonne: valeur} (lecture en flux).

    ``prefilter`` s'applique à la **ligne brute** : les fichiers CTD comptent des dizaines
    de millions de lignes dont la grande majorité sera écartée (associations inférées).
    Filtrer avant de construire le dict évite des millions d'allocations inutiles.
    """
    header: list[str] = []
    yielded = 0
    with _open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#"):
                candidate = line.lstrip("#").strip()
                if "\t" in candidate:      # la dernière ligne # tabulée = l'en-tête
                    header = candidate.split("\t")
                continue
            if not line or not header:
                continue
            if prefilter is not None and not prefilter(line):
                continue
            values = line.split("\t")
            if len(values) < len(header):
                values += [""] * (len(header) - len(values))
            yield dict(zip(header, values, strict=False))
            yielded += 1
            if limit is not None and yielded >= limit:
                return


def has_direct_evidence(line: str) -> bool:
    """Pré-filtre : ne garder que les lignes portant une preuve directe curée."""
    return "marker/mechanism" in line or "therapeutic" in line
