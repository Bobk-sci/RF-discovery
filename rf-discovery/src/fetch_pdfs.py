"""Télécharge les PDF **en accès libre** des articles de la bibliothèque.

    python -m fetch_pdfs --email vous@exemple.fr --out pdf

Ce que fait ce module, et ce qu'il ne fait pas :

* il demande à **Unpaywall** (API publique et gratuite, une adresse courriel suffit) s'il
  existe une version légalement gratuite de l'article, puis télécharge ce PDF-là ;
* il ne contourne aucun péage : un article sous abonnement n'est pas téléchargé, il est
  compté dans ``sans_acces_libre``. Passer outre violerait les conditions d'utilisation
  des éditeurs — et pour ces articles-là, l'accès institutionnel (via Zotero et le proxy
  de votre bibliothèque) est la bonne voie.

Les PDF ne sont pas versionnés : ``pdf/`` est ignoré par git (volume, et droits d'auteur
variables selon les licences). Le chemin local part dans l'export RIS pour que Zotero ou
EndNote attache chaque fichier à sa référence.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from collect.cache import get_json
from export_refs import collect_records

ROOT = Path(__file__).resolve().parents[1]
UNPAYWALL = "https://api.unpaywall.org/v2"
log = logging.getLogger("pdfs")


def oa_pdf_url(doi: str, email: str, *, fetcher=None,
               cache_dir: str = "data/cache/unpaywall") -> str:
    """URL du PDF en accès libre pour ce DOI, ou chaîne vide s'il n'y en a pas."""
    fetch = fetcher or (lambda u, p: get_json(u, p, cache_dir=cache_dir))
    try:
        data = fetch(f"{UNPAYWALL}/{doi}", {"email": email}) or {}
    except Exception as exc:            # DOI inconnu, réseau : on passe au suivant
        log.debug("Unpaywall %s : %s", doi, exc)
        return ""
    best = data.get("best_oa_location") or {}
    url = best.get("url_for_pdf") or ""
    if not url:
        for loc in data.get("oa_locations") or []:
            if isinstance(loc, dict) and loc.get("url_for_pdf"):
                url = loc["url_for_pdf"]
                break
    return str(url or "")


def download(url: str, target: Path, *, timeout: int = 60) -> bool:
    """Écrit le PDF ; refuse tout ce qui n'en est pas un (page de péage, HTML d'erreur)."""
    import requests

    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout,
                      headers={"User-Agent": "rf-library/1.0"}) as resp:
        resp.raise_for_status()
        if "pdf" not in resp.headers.get("Content-Type", "").lower():
            return False
        tmp = target.with_suffix(".part")
        with open(tmp, "wb") as fh:
            for block in resp.iter_content(chunk_size=1 << 16):
                fh.write(block)
        tmp.rename(target)
    return True


def _name(meta: dict[str, Any]) -> str:
    return f"{meta.get('pmid') or str(meta.get('doi', '')).replace('/', '_')}.pdf"


def fetch_all(records: list[dict[str, Any]], out: Path, email: str, *,
              limit: int | None = None, pause_s: float = 1.0,
              url_resolver=None, downloader=None, sleep=time.sleep) -> dict[str, int]:
    """Parcourt la bibliothèque et récupère ce qui est légalement téléchargeable."""
    resolve = url_resolver or (lambda doi: oa_pdf_url(doi, email))
    grab = downloader or download
    counts = {"deja_present": 0, "telecharges": 0, "sans_acces_libre": 0,
              "sans_doi": 0, "echecs": 0}
    for meta in records[:limit]:
        target = out / _name(meta)
        if target.exists():
            counts["deja_present"] += 1
            continue
        doi = str(meta.get("doi") or "").strip()
        if not doi:
            counts["sans_doi"] += 1
            continue
        url = resolve(doi)
        if not url:
            counts["sans_acces_libre"] += 1
            continue
        try:
            counts["telecharges" if grab(url, target) else "echecs"] += 1
        except Exception as exc:
            log.warning("téléchargement %s : %s", doi, exc)
            counts["echecs"] += 1
        sleep(pause_s)
    return counts


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description="PDF en accès libre de la bibliothèque")
    ap.add_argument("--articles", default=str(ROOT / "articles"))
    ap.add_argument("--out", default=str(ROOT / "pdf"))
    ap.add_argument("--email", default=os.environ.get("CONTACT_EMAIL", ""),
                    help="exigé par Unpaywall (identification de l'appelant)")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if not args.email:
        raise SystemExit("Unpaywall exige une adresse : --email ou CONTACT_EMAIL")

    records = collect_records(Path(args.articles))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    counts = fetch_all(records, out, args.email, limit=args.limit)
    print(json.dumps({"articles": len(records), **counts}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
