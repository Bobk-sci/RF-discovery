"""Bibliothèque RF : collecter des articles réels et les ranger en sous-dossiers.

Sources interrogées (toutes gratuites, sans compte) :
  * **Europe PMC** — recherche plein texte, pagination ``cursorMark`` ;
  * **PubMed** (E-utilities NCBI) — couverture décalée, notices « ahead of print » ;
  * **EMF-Portal** — base spécialisée CEM ; on n'en tire que les identifiants
    (PMID/DOI), les métadonnées venant de PubMed/Europe PMC.

Rien n'est inventé : chaque fiche correspond à une notice réellement renvoyée par une
de ces sources, titre et résumé recopiés tels quels, PMID/DOI cliquables.

Exemples ::

    python -m collect_library --max-results 300
    python -m collect_library --sources europepmc,pubmed --max-results 1000
    python -m collect_library --emfportal-file page_emfportal.html
    python -m collect_library --reclasser        # relit taxonomy.yaml, ne collecte rien

Le classement est incrémental : ``data/seen_library.json`` mémorise ce qui est déjà
rangé, un rerun ne ramène que les nouveautés. ``index.csv`` et ``README.md`` sont
reconstruits depuis le disque, donc toujours complets.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from collect import emfportal, pubmed
from collect.europepmc import Paper
from collect.europepmc import search as epmc_search
from library.classify import (
    Taxonomy,
    build_query,
    classify_paper,
    is_off_topic,
    load_taxonomy,
)
from library.importer import papers_from_json
from library.organize import (
    article_path,
    prune_empty_dirs,
    read_article,
    scan_library,
    write_article,
    write_index,
    write_readme,
)
from normalize.dedupe import dedupe, load_seen, paper_key, save_seen

ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("library")


def collect(tax: Taxonomy, sources: list[str], max_results: int, *,
            emfportal_url: str, emfportal_files: list[str],
            email: str, api_key: str) -> list[Paper]:
    """Interroge les sources demandées et rend la liste brute des articles trouvés."""
    query = build_query(tax)
    papers: list[Paper] = []
    if "europepmc" in sources:
        found = epmc_search(query, domain="rf", max_results=max_results,
                            cache_dir="data/cache/library")
        log.info("Europe PMC : %d notices", len(found))
        papers += found
    if "pubmed" in sources:
        found = pubmed.search(query, max_results=max_results, domain="rf",
                              api_key=api_key, email=email)
        log.info("PubMed : %d notices", len(found))
        papers += found
    if "emfportal" in sources:
        texts = emfportal.read_files(emfportal_files) if emfportal_files else \
            emfportal.fetch_pages(" OR ".join(tax.rf_terms[:3]), url_template=emfportal_url)
        found = emfportal.resolve(texts, api_key=api_key, email=email,
                                  max_results=max_results,
                                  search_epmc=lambda q, max_results=40: epmc_search(
                                      q, max_results=max_results,
                                      cache_dir="data/cache/library"))
        log.info("EMF-Portal : %d notices résolues", len(found))
        papers += found
    return papers


def file_papers(out: Path, papers: list[Paper], tax: Taxonomy) -> dict[str, int]:
    """Classe et écrit chaque article ; compte les fiches par catégorie de 1er niveau."""
    axes = tuple(ax.name for ax in tax.axes)
    counts: dict[str, int] = {}
    for paper in papers:
        motif = is_off_topic(paper, tax)
        if motif:
            log.info("écarté (%s) : %s", motif, paper.title[:70])
            counts["_ecartes"] = counts.get("_ecartes", 0) + 1
            continue
        assignments = classify_paper(paper, tax)
        write_article(out, paper, assignments, axes)
        key = assignments[axes[0]].category if axes else "?"
        counts[key] = counts.get(key, 0) + 1
    return counts


def reclasser(out: Path, tax: Taxonomy) -> dict[str, int]:
    """Réapplique la taxonomie aux fiches déjà présentes (aucun accès réseau).

    Resserrer `exclusions`/`pertinence` doit aussi **sortir** du corpus les fiches
    devenues hors sujet : sinon la bibliothèque garderait une trace de réglages révolus.
    """
    axes = tuple(ax.name for ax in tax.axes)
    moved = removed = 0
    for path in sorted(out.rglob("*.md")):
        if path.name == "README.md":
            continue
        paper = read_article(path)
        motif = is_off_topic(paper, tax)
        if motif:
            log.info("sorti du corpus (%s) : %s", motif, paper.title[:70])
            path.unlink()
            removed += 1
            continue
        assignments = classify_paper(paper, tax)
        target = article_path(out, paper, assignments, axes)
        write_article(out, paper, assignments, axes)
        if target.resolve() != path.resolve():
            path.unlink()
            moved += 1
    prune_empty_dirs(out)
    return {"fiches_deplacees": moved, "fiches_sorties": removed}


def memoire_depuis_bibliotheque(out: Path) -> set[str]:
    """Clés de déduplication reconstruites depuis les fiches réellement rangées.

    Invariant : « déjà vu » = « déjà rangé ». Sans cela, un article écarté par un réglage
    trop strict resterait marqué comme vu et ne reviendrait jamais, même une fois le
    réglage corrigé. Le coût est nul : les sources renvoient de toute façon ces notices.
    """
    return {paper_key(read_article(p)) for p in out.rglob("*.md") if p.name != "README.md"}


def _finalise(out: Path, tax: Taxonomy, query: str) -> int:
    records = scan_library(out)
    axes = tuple(ax.name for ax in tax.axes)
    write_index(out, records, axes)
    write_readme(out, records, tax, query)
    return len(records)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description="Collecte et classement d'articles RF")
    ap.add_argument("--taxonomy", default=str(ROOT / "config" / "taxonomy.yaml"))
    ap.add_argument("--out", default=str(ROOT / "articles"))
    ap.add_argument("--seen", default=str(ROOT / "data" / "seen_library.json"))
    ap.add_argument("--sources", default="europepmc,pubmed",
                    help="europepmc,pubmed,emfportal (séparées par des virgules)")
    ap.add_argument("--max-results", type=int, default=300, help="plafond par source")
    ap.add_argument("--emfportal-url", default=emfportal.DEFAULT_URL,
                    help="gabarit d'URL de recherche EMF-Portal ({query} = les termes)")
    ap.add_argument("--emfportal-file", action="append", default=[],
                    help="page/export EMF-Portal enregistré localement (répétable)")
    ap.add_argument("--import-json", action="append", default=[],
                    help="export JSON de notices déjà récupérées (répétable, hors ligne)")
    ap.add_argument("--import-source", default="import",
                    help="provenance réelle des exports importés (pubmed, europepmc…)")
    ap.add_argument("--reclasser", action="store_true",
                    help="reclasse les fiches existantes sans rien collecter")
    ap.add_argument("--tout", action="store_true",
                    help="ignore seen_library.json (re-collecte tout le corpus)")
    args = ap.parse_args()

    tax = load_taxonomy(args.taxonomy)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.reclasser:
        result = reclasser(out, tax)
        # La mémoire suit le corpus : ce qui vient d'être écarté redeviendra collectable
        # si la taxonomie se rouvre un jour.
        save_seen(args.seen, memoire_depuis_bibliotheque(out))
        result["articles"] = _finalise(out, tax, build_query(tax))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    papers: list[Paper] = []
    for path in args.import_json:
        imported = papers_from_json(path, source=args.import_source)
        log.info("import %s : %d notices", path, len(imported))
        papers += imported
    sources = [] if args.import_json else \
        [s.strip() for s in args.sources.split(",") if s.strip()]
    papers += collect(tax, sources, args.max_results,
                      emfportal_url=args.emfportal_url,
                      emfportal_files=args.emfportal_file,
                      email=os.environ.get("CONTACT_EMAIL", ""),
                      api_key=os.environ.get("NCBI_API_KEY", ""))
    seen = set() if args.tout else load_seen(args.seen)
    fresh, updated = dedupe(papers, seen)
    counts = file_papers(out, fresh, tax)
    save_seen(args.seen, updated)
    print(json.dumps({"trouves": len(papers), "nouveaux": len(fresh),
                      "par_modele": counts, "articles": _finalise(out, tax, build_query(tax))},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
