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
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from collect.cache import get_json
from export_refs import collect_records

ROOT = Path(__file__).resolve().parents[1]
UNPAYWALL = "https://api.unpaywall.org/v2"
# Le code HTTP est la seule information exploitable dans le message d'une exception
# `requests` : 403 vient d'un éditeur qui refuse les scripts, 404 d'un lien mort.
_CODE_HTTP = re.compile(r"\b([45]\d{2})\b")
log = logging.getLogger("pdfs")


def oa_pdf_urls(doi: str, email: str, *, fetcher=None,
                cache_dir: str = "data/cache/unpaywall") -> list[str]:
    """URLs de PDF en accès libre pour ce DOI, **dépôts d'abord**.

    Les dépôts (PMC, archives institutionnelles) servent les fichiers à un script sans
    difficulté ; les sites d'éditeurs renvoient souvent 403 à tout ce qui n'est pas un
    navigateur, même pour un article sous licence libre. On essaie donc les dépôts en
    premier et on garde les éditeurs en secours.
    """
    fetch = fetcher or (lambda u, p: get_json(u, p, cache_dir=cache_dir))
    try:
        data = fetch(f"{UNPAYWALL}/{doi}", {"email": email}) or {}
    except Exception as exc:            # DOI inconnu, réseau : on passe au suivant
        log.debug("Unpaywall %s : %s", doi, exc)
        return []
    locations = [loc for loc in (data.get("oa_locations") or []) if isinstance(loc, dict)]
    best = data.get("best_oa_location")
    if isinstance(best, dict) and best not in locations:
        locations.append(best)
    depots = [loc for loc in locations if loc.get("host_type") == "repository"]
    autres = [loc for loc in locations if loc.get("host_type") != "repository"]
    urls: list[str] = []
    for loc in depots + autres:
        url = str(loc.get("url_for_pdf") or "")
        if url and url not in urls:
            urls.append(url)
    return urls


def _headers(email: str) -> dict[str, str]:
    """En-têtes d'un client honnête mais complet.

    ``User-Agent: rf-library/1.0`` seul, sans ``Accept``, ressemble à un robot anonyme :
    plusieurs éditeurs répondent 403. On s'identifie donc avec un contact — la convention
    du « polite pool » de Crossref — et on annonce ce qu'on accepte. Aucune tentative de
    se faire passer pour un navigateur, aucun contournement d'authentification.
    """
    contact = f"; mailto:{email}" if email else ""
    return {
        "User-Agent": f"rf-library/1.0 (+https://github.com/Bobk-sci/RF-discovery{contact})",
        "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
        "Accept-Language": "en,fr;q=0.8",
    }


def download(url: str, target: Path, *, timeout: int = 60, email: str = "") -> bool:
    """Écrit le PDF ; refuse tout ce qui n'en est pas un (page de péage, HTML d'erreur)."""
    import requests

    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout, allow_redirects=True,
                      headers=_headers(email)) as resp:
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
              url_resolver=None, downloader=None, sleep=time.sleep,
              journal: list[dict[str, Any]] | None = None) -> dict[str, int]:
    """Parcourt la bibliothèque et récupère ce qui est légalement téléchargeable.

    ``journal``, s'il est fourni, reçoit une entrée par article non obtenu : le DOI, la
    classe retenue et, pour chaque source essayée, le code HTTP et le message. Sans ce
    relevé, le compteur ``echecs`` est un nombre sans cause, donc sans action possible.
    """
    resolve = url_resolver or (lambda doi: oa_pdf_urls(doi, email))
    grab = downloader or (lambda url, target: download(url, target, email=email))
    counts = {"deja_present": 0, "telecharges": 0, "sans_acces_libre": 0,
              "sans_doi": 0, "refus_editeur": 0, "echecs": 0}
    for meta in records[:limit]:
        target = out / _name(meta)
        if target.exists():
            counts["deja_present"] += 1
            continue
        doi = str(meta.get("doi") or "").strip()
        if not doi:
            counts["sans_doi"] += 1
            continue
        urls = resolve(doi)
        if not urls:
            counts["sans_acces_libre"] += 1
            continue
        _essayer(urls, target, doi, grab, counts, journal)
        sleep(pause_s)
    return counts


def _motif(exc: Exception) -> tuple[str, str]:
    """(code HTTP si présent, sinon type d'erreur ; message abrégé)."""
    texte = str(exc)
    trouve = _CODE_HTTP.search(texte)
    return (trouve.group(1) if trouve else type(exc).__name__), texte[:140]


def _essayer(urls: list[str], target: Path, doi: str, grab, counts: dict[str, int],
             journal: list[dict[str, Any]] | None = None) -> None:
    """Essaie chaque source jusqu'à obtenir le PDF ; retient la cause de chaque échec."""
    refus = False
    sources: list[dict[str, str]] = []
    for url in urls:
        try:
            if grab(url, target):
                counts["telecharges"] += 1
                return
        except Exception as exc:
            # 403 = l'éditeur refuse les scripts, pas un article payant. Zotero, qui
            # agit depuis un navigateur, y arrive généralement. Tout le reste — délai
            # dépassé, lien mort, coupure — est un échec technique, et se dit autrement.
            code, message = _motif(exc)
            refus = refus or code == "403"
            sources.append({"url": url, "code": code, "message": message})
            log.info("%s pour %s : %s",
                     "refus de l'éditeur" if code == "403" else f"échec {code}",
                     doi, message[:80])
    classe = "refus_editeur" if refus else "echecs"
    counts[classe] += 1
    if journal is not None:
        journal.append({"doi": doi, "classe": classe, "sources": sources})


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
    journal: list[dict[str, Any]] = []
    counts = fetch_all(records, out, args.email, limit=args.limit, journal=journal)
    print(json.dumps({"articles": len(records), **counts}, indent=2, ensure_ascii=False))
    if counts["refus_editeur"]:
        print(f"\n{counts['refus_editeur']} articles en accès libre dont l'éditeur refuse "
              "les scripts (403). Ils ne sont pas payants : dans Zotero, « Trouver le PDF "
              "disponible » les récupère depuis un navigateur.")
    _rapport(journal, out, counts)


def _rapport(journal: list[dict[str, Any]], out: Path, counts: dict[str, int]) -> None:
    """Écrit le relevé des échecs et en affiche les causes, par fréquence."""
    if not journal:
        return
    chemin = out / "rapport-echecs.json"
    chemin.write_text(json.dumps(journal, indent=1, ensure_ascii=False), encoding="utf-8")
    causes = Counter(s["code"] for e in journal if e["classe"] == "echecs"
                     for s in e["sources"])
    if causes:
        print(f"\n{counts['echecs']} échecs techniques, par cause :")
        for code, n in causes.most_common(8):
            print(f"  {n:>5}  {code}")
    print(f"\nRelevé détaillé : {chemin}")


if __name__ == "__main__":
    main()
