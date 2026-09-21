"""Exporte la bibliothèque vers RIS et BibTeX — import direct dans EndNote ou Zotero.

    python -m export_refs                      # articles/bibliotheque-rf.{ris,bib}
    python -m export_refs --pdf-dir pdf        # attache les PDF déjà téléchargés

Le classement part en mots-clés (`modele:in_vivo`, `theme:neurodeveloppement`) : Zotero
en fait des étiquettes, EndNote des « keywords », sur lesquels on retrouve l'arborescence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from library.classify import load_taxonomy
from library.organize import README_NAME, read_article, read_front_matter
from library.refs import to_bibtex, to_ris

ROOT = Path(__file__).resolve().parents[1]


def collect_records(out: Path) -> list[dict[str, Any]]:
    """Fiches du disque, en-tête + résumé d'origine, triées (export reproductible)."""
    records = []
    for path in sorted(out.rglob("*.md")):
        if path.name == README_NAME:
            continue
        meta = read_front_matter(path)
        if not meta:
            continue
        meta["resume"] = read_article(path).abstract
        meta["fichier"] = str(path.relative_to(out))
        records.append(meta)
    return records


def main() -> None:
    ap = argparse.ArgumentParser(description="Export RIS / BibTeX de la bibliothèque")
    ap.add_argument("--articles", default=str(ROOT / "articles"))
    ap.add_argument("--taxonomy", default=str(ROOT / "config" / "taxonomy.yaml"))
    ap.add_argument("--pdf-dir", default=None,
                    help="dossier des PDF à rattacher aux références (accès libre)")
    args = ap.parse_args()

    out = Path(args.articles)
    tax = load_taxonomy(args.taxonomy)
    axes = tuple(ax.name for ax in tax.axes)
    records = collect_records(out)
    pdf_dir = Path(args.pdf_dir).resolve() if args.pdf_dir else None

    ris = out / "bibliotheque-rf.ris"
    bib = out / "bibliotheque-rf.bib"
    ris.write_text(to_ris(records, axes, pdf_dir), encoding="utf-8")
    bib.write_text(to_bibtex(records, axes), encoding="utf-8")
    avec_auteurs = sum(1 for r in records if r.get("auteurs"))
    print(json.dumps({"references": len(records), "avec_auteurs": avec_auteurs,
                      "ris": str(ris), "bibtex": str(bib)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
