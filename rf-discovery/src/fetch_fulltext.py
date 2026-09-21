"""Texte intégral des articles libres, depuis Europe PMC — pour l'analyse, pas pour citer.

    python -m fetch_fulltext --out articles/_textes

Plusieurs éditeurs (MDPI, Wiley, Elsevier) répondent 403 au téléchargement de leur PDF par
un script, même pour des articles sous licence libre. Europe PMC, lui, sert le texte
intégral en XML pour les articles du sous-ensemble en accès ouvert, via un point d'accès
documenté et ouvert aux programmes :

    https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML

Pour lire dans Obsidian ou faire travailler un modèle local, ce texte vaut mieux qu'un
PDF : il est structuré, sans colonnes ni en-têtes de page, et se cherche. Les fichiers
produits vont dans un dossier préfixé ``_`` : ce sont des annexes, jamais des fiches.

Ce module ne récupère que ce qu'Europe PMC accepte de donner. Un article hors du
sous-ensemble libre renvoie une réponse vide : il est compté, pas contourné.
"""
from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from collect.cache import get_text
from export_refs import collect_records

ROOT = Path(__file__).resolve().parents[1]
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
log = logging.getLogger("fulltext")
_SAUTE = {"ref-list", "back", "fn-group", "table-wrap", "fig"}


def _texte(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def xml_vers_markdown(xml_text: str) -> str:
    """Corps de l'article en Markdown : titres de sections et paragraphes, rien d'autre.

    Références, figures et tableaux sont écartés : ils encombrent sans rien apporter à une
    lecture ou à une recherche sémantique, et les références restent dans le fichier RIS.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return ""
    body = root.find(".//body")
    if body is None:
        return ""
    lignes: list[str] = []
    for section in body.iter():
        if section.tag not in {"sec", "p"} or _parent_saute(body, section):
            continue
        if section.tag == "sec":
            titre = section.find("title")
            if titre is not None and _texte(titre):
                lignes += ["", f"## {_texte(titre)}", ""]
        elif _texte(section):
            lignes.append(_texte(section))
    return "\n".join(lignes).strip()


def _parent_saute(body: ET.Element, cible: ET.Element) -> bool:
    for ignore in _SAUTE:
        for bloc in body.iter(ignore):
            if cible in bloc.iter():
                return True
    return False


def fetch_one(pmcid: str, *, fetcher=None, cache_dir: str = "data/cache/fulltext") -> str:
    """Texte intégral d'un article, ou chaîne vide s'il n'est pas en accès libre."""
    fetch = fetcher or (lambda u, p: get_text(u, p, cache_dir=cache_dir))
    try:
        return xml_vers_markdown(fetch(f"{EPMC}/{pmcid}/fullTextXML", {}) or "")
    except Exception as exc:
        log.debug("texte intégral %s : %s", pmcid, exc)
        return ""


def _entete(meta: dict[str, Any]) -> str:
    auteurs = ", ".join(meta.get("auteurs") or [])
    return (f"# {meta.get('titre', '')}\n\n"
            f"*{auteurs}* — {meta.get('journal', '')} {meta.get('annee', '')}\n\n"
            f"PMID {meta.get('pmid', '')} · [{meta.get('doi', '')}]"
            f"(https://doi.org/{meta.get('doi', '')})\n\n"
            "> Texte intégral récupéré d'Europe PMC (sous-ensemble en accès ouvert).\n")


def fetch_all(records: list[dict[str, Any]], out: Path, *, limit: int | None = None,
              pause_s: float = 0.5, fetcher=None, sleep=time.sleep,
              pas_avancement: int = 25) -> dict[str, int]:
    """Écrit un fichier par article dont Europe PMC fournit le texte intégral.

    L'avancement est journalisé régulièrement : sur un millier d'articles, une commande
    muette pendant vingt minutes est indiscernable d'une commande bloquée.
    """
    out.mkdir(parents=True, exist_ok=True)
    counts = {"deja_present": 0, "recuperes": 0, "sans_pmcid": 0, "non_disponible": 0}
    eligibles = [m for m in records[:limit] if str(m.get("pmcid") or "").strip()]
    counts["sans_pmcid"] = len(records[:limit]) - len(eligibles)
    log.info("%d articles, dont %d avec un PMCID à interroger", len(records[:limit]),
             len(eligibles))
    for rang, meta in enumerate(eligibles, start=1):
        pmcid = str(meta["pmcid"]).strip()
        cible = out / f"{meta.get('pmid') or pmcid}.md"
        if cible.exists():
            counts["deja_present"] += 1
            continue
        corps = fetch_one(pmcid, fetcher=fetcher)
        if not corps:
            counts["non_disponible"] += 1
        else:
            cible.write_text(_entete(meta) + "\n" + corps + "\n", encoding="utf-8")
            counts["recuperes"] += 1
        if rang % pas_avancement == 0:
            log.info("  %d/%d traités — %d textes récupérés", rang, len(eligibles),
                     counts["recuperes"] + counts["deja_present"])
        sleep(pause_s)
    return counts


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description="Texte intégral des articles en accès libre")
    ap.add_argument("--articles", default=str(ROOT / "articles"))
    ap.add_argument("--out", default=str(ROOT / "articles" / "_textes"))
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    records = collect_records(Path(args.articles))
    counts = fetch_all(records, Path(args.out), limit=args.limit)
    print(json.dumps({"articles": len(records), **counts}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
