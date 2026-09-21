"""Intègre un dossier de PDF déjà constitué à la bibliothèque.

    python -m importer_dossier --dossier "C:\\biblio\\Biblio\\raw"

Beaucoup de gens ont déjà une collection de PDF nommés d'après leur titre. Ce module la
raccroche au corpus : pour chaque fichier, il cherche l'article **par son titre** dans
Europe PMC, récupère la notice réelle (auteurs, DOI, PMID, résumé, descripteurs), la classe
comme les autres et note le chemin du PDF local dans la fiche.

Aucune métadonnée n'est déduite du nom de fichier : celui-ci ne sert qu'à **chercher**.
Si aucune notice ne correspond assez bien, le fichier est signalé comme non résolu — la
bibliothèque ne contient pas de fiche fabriquée à partir d'un nom de fichier.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any

from collect.europepmc import Paper
from collect.europepmc import search as epmc_search
from library.classify import Taxonomy, classify_paper, is_off_topic, load_taxonomy
from library.organize import write_article
from normalize.dedupe import normalize_title

ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("importer")
_PREFIXE = re.compile(r"^[\d\W_]+")
_VIDES = {"the", "of", "on", "in", "a", "an", "and", "to", "for", "de", "la", "le"}


def titre_depuis_nom(path: Path) -> str:
    """Titre probable, tiré du nom de fichier : numéro de tête et suffixes retirés."""
    nom = _PREFIXE.sub("", path.stem)
    nom = re.sub(r"\s*\(\d+\)$", "", nom)          # « (1) » des copies
    return re.sub(r"[_\s]+", " ", nom).strip(" .")


def _mots(titre: str) -> set[str]:
    return {m for m in normalize_title(titre).split() if m not in _VIDES and len(m) > 2}


def similarite(a: str, b: str) -> float:
    """Recouvrement des mots significatifs (0 à 1) : robuste aux troncatures de nom."""
    ma, mb = _mots(a), _mots(b)
    if not ma or not mb:
        return 0.0
    return len(ma & mb) / min(len(ma), len(mb))


def chercher(titre: str, *, search=None, seuil: float = 0.7) -> Paper | None:
    """Notice Europe PMC dont le titre correspond, ou ``None`` si rien d'assez proche."""
    quete = search or (lambda q, **kw: epmc_search(q, cache_dir="data/cache/import", **kw))
    mots = " ".join(list(_mots(titre))[:12])
    try:
        candidats = quete(f'TITLE:"{titre}"', max_results=5) or quete(mots, max_results=10)
    except Exception as exc:
        log.warning("recherche « %s » : %s", titre[:60], exc)
        return None
    meilleur, score = None, 0.0
    for paper in candidats:
        s = similarite(titre, paper.title)
        if s > score:
            meilleur, score = paper, s
    return meilleur if score >= seuil else None


def importer_dossier(dossier: Path, out: Path, tax: Taxonomy, *, deja: set[str] | None = None,
                     search=None, limit: int | None = None) -> dict[str, Any]:
    """Crée une fiche par PDF résolu ; rend le compte et la liste des non résolus."""
    axes = tuple(ax.name for ax in tax.axes)
    connus = deja or set()
    compte: dict[str, int] = {"pdf": 0, "deja_presents": 0, "importes": 0, "ecartes": 0}
    non_resolus: list[str] = []
    for pdf in sorted(dossier.glob("*.pdf"))[:limit]:
        compte["pdf"] += 1
        titre = titre_depuis_nom(pdf)
        if normalize_title(titre) in connus:
            compte["deja_presents"] += 1
            continue
        paper = chercher(titre, search=search)
        if paper is None:
            non_resolus.append(pdf.name)
            continue
        paper.extra["pdf_local"] = str(pdf.resolve())
        motif = is_off_topic(paper, tax)
        if motif:
            log.info("écarté (%s) : %s", motif, paper.title[:70])
            compte["ecartes"] += 1
            continue
        write_article(out, paper, classify_paper(paper, tax), axes)
        compte["importes"] += 1
    return {**compte, "non_resolus": non_resolus}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description="Intègre un dossier de PDF à la bibliothèque")
    ap.add_argument("--dossier", required=True)
    ap.add_argument("--articles", default=str(ROOT / "articles"))
    ap.add_argument("--taxonomy", default=str(ROOT / "config" / "taxonomy.yaml"))
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    from export_refs import collect_records

    out = Path(args.articles)
    tax = load_taxonomy(args.taxonomy)
    deja = {normalize_title(str(r.get("titre", ""))) for r in collect_records(out)}
    resultat = importer_dossier(Path(args.dossier), out, tax, deja=deja, limit=args.limit)
    print(json.dumps(resultat, indent=2, ensure_ascii=False))
    print("\nRelancer ensuite : python -m collect_library --reclasser puis "
          "python -m export_refs --pdf-dir pdf")


if __name__ == "__main__":
    main()
