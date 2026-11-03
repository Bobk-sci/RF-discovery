"""Filtrage local d'un corpus complet téléchargé en vrac (PubMed baseline, OpenAlex).

**Pourquoi ce module.** Interroger une API, c'est demander à un moteur de recherche de
deviner ce qu'on cherche : la requête PubMed de ce dépôt a rendu zéro notice pendant des
semaines sans le dire, parce qu'elle était écrite dans la syntaxe d'Europe PMC. Filtrer
soi-même un corpus complet supprime ce risque : on lit **toutes** les notices et c'est la
taxonomie du dépôt — le même comptage de mots-clés que partout ailleurs — qui décide.

Deux formats, deux usages :

``pubmed``
    Les fichiers ``*.xml.gz`` du *baseline* PubMed (ftp.ncbi.nlm.nih.gov/pubmed/baseline/).
    Notices complètes, avec résumé et descripteurs MeSH : elles produisent directement des
    fiches, exactement comme une collecte en ligne. C'est le format à privilégier.

``openalex``
    Les fichiers ``*.gz`` du *snapshot* OpenAlex (s3://openalex/data/jsonl/works/). OpenAlex
    ne publie pas le résumé en clair mais sous forme d'index inversé : le reconstruire
    donnerait un texte dont la ponctuation n'est plus celle de l'original. Ce format ne
    produit donc **aucune fiche** — il écrit une liste de PMID/DOI candidats, que
    ``collect_library`` résout ensuite auprès de PubMed / Europe PMC, qui font foi.

La lecture est incrémentale : un fichier d'archive est parcouru article par article, jamais
chargé entier en mémoire. Un poste de 16 Go traite le baseline complet sans difficulté.
"""
from __future__ import annotations

import argparse
import gzip
import json
import logging
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path

from collect.europepmc import Paper
from collect.pubmed import parse_pubmed_xml
from library.classify import Taxonomy, load_taxonomy

log = logging.getLogger("baseline")

_ENTETE = '<?xml version="1.0"?><PubmedArticleSet>'
_PIED = "</PubmedArticleSet>"
_PMID_URL = re.compile(r"/(\d{4,9})/?$")


def _lots(chemin: Path, taille: int = 500) -> Iterator[str]:
    """Découpe un fichier baseline en paquets de notices, sans tout charger en mémoire.

    Chaque paquet est un ``PubmedArticleSet`` autonome, confié au parseur déjà utilisé
    par la collecte en ligne : une seule logique de lecture, donc aucune divergence
    possible entre les deux chemins.
    """
    with gzip.open(chemin, "rb") as flux:
        morceaux: list[str] = []
        for _, element in ET.iterparse(flux, events=("end",)):
            if element.tag != "PubmedArticle":
                continue
            morceaux.append(ET.tostring(element, encoding="unicode"))
            element.clear()
            if len(morceaux) >= taille:
                yield _ENTETE + "".join(morceaux) + _PIED
                morceaux = []
        if morceaux:
            yield _ENTETE + "".join(morceaux) + _PIED


def lire_pubmed(chemin: Path, *, lot: int = 500) -> Iterator[Paper]:
    """Notices d'un fichier baseline, une par une."""
    for xml_text in _lots(chemin, lot):
        yield from parse_pubmed_xml(xml_text, domain="rf")


def _identifiants(rec: dict) -> tuple[str, str]:
    """(PMID, DOI) d'une notice OpenAlex du snapshot ; les deux arrivent en URL."""
    ids = rec.get("ids") or {}
    brut = str(ids.get("pmid") or "")
    trouve = _PMID_URL.search(brut) if brut else None
    pmid = trouve.group(1) if trouve else (brut if brut.isdigit() else "")
    doi = str(ids.get("doi") or rec.get("doi") or "").lower()
    doi = doi.removeprefix("https://doi.org/").removeprefix("http://doi.org/")
    return pmid, doi


def _texte_openalex(rec: dict) -> str:
    """Titre seul : le résumé d'OpenAlex est un index inversé, on ne le reconstruit pas."""
    return str(rec.get("title") or rec.get("display_name") or "")


def scanner_openalex(chemin: Path, tax: Taxonomy) -> Iterator[tuple[str, str]]:
    """Identifiants des notices dont le titre porte un terme d'exposition RF."""
    motifs = [re.compile(rf"\b{re.escape(t.lower())}\b") for t in tax.rf_terms]
    with gzip.open(chemin, "rt", encoding="utf-8", errors="replace") as flux:
        for ligne in flux:
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                rec = json.loads(ligne)
            except json.JSONDecodeError:
                continue
            titre = _texte_openalex(rec).lower()
            if not titre or not any(m.search(titre) for m in motifs):
                continue
            pmid, doi = _identifiants(rec)
            if pmid or doi:
                yield pmid, doi


def _fichiers(dossier: Path, motif: str) -> list[Path]:
    return sorted(p for p in dossier.rglob(motif) if p.is_file())


def parcourir_pubmed(dossier: Path, out: Path, tax: Taxonomy, *,
                     limite: int = 0) -> dict[str, int]:
    """Filtre tout un baseline et écrit les fiches retenues (import paresseux du CLI)."""
    from collect_library import file_papers

    fichiers = _fichiers(dossier, "*.xml.gz")
    total = {"fichiers": len(fichiers), "notices": 0, "retenues": 0, "ecartees": 0}
    for rang, chemin in enumerate(fichiers, 1):
        lot: list[Paper] = []
        for paper in lire_pubmed(chemin):
            total["notices"] += 1
            lot.append(paper)
            if len(lot) >= 2000:
                _vider(lot, out, tax, total, file_papers)
        _vider(lot, out, tax, total, file_papers)
        log.info("[%d/%d] %s : %d notices lues, %d retenues",
                 rang, len(fichiers), chemin.name, total["notices"], total["retenues"])
        if limite and total["notices"] >= limite:
            break
    return total


def _vider(lot: list[Paper], out: Path, tax: Taxonomy, total: dict[str, int],
           file_papers) -> None:
    """Classe un paquet de notices et remet le tampon à zéro."""
    if not lot:
        return
    counts, ecrits = file_papers(out, lot, tax)
    total["retenues"] += len(ecrits)
    total["ecartees"] += counts.get("_ecartes", 0)
    lot.clear()


def parcourir_openalex(dossier: Path, tax: Taxonomy,
                       sortie: Path) -> dict[str, int | str]:
    """Écrit les identifiants candidats du snapshot OpenAlex, sans créer de fiche."""
    fichiers = _fichiers(dossier, "*.gz")
    pmids: dict[str, None] = {}
    dois: dict[str, None] = {}
    for rang, chemin in enumerate(fichiers, 1):
        for pmid, doi in scanner_openalex(chemin, tax):
            (pmids if pmid else dois).setdefault(pmid or doi, None)
        log.info("[%d/%d] %s : %d PMID, %d DOI",
                 rang, len(fichiers), chemin.name, len(pmids), len(dois))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps({"pmids": list(pmids), "dois": list(dois)},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    return {"fichiers": len(fichiers), "pmids": len(pmids), "dois": len(dois),
            "sortie": str(sortie)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dump", required=True, help="dossier contenant l'archive décompressée")
    ap.add_argument("--format", default="pubmed", choices=["pubmed", "openalex"])
    ap.add_argument("--taxonomy", default="config/taxonomy.yaml")
    ap.add_argument("--out", default="articles")
    ap.add_argument("--candidats", default="data/candidats_openalex.json")
    ap.add_argument("--limite", type=int, default=0, help="arrêt après N notices (essai)")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    tax = load_taxonomy(args.taxonomy)
    dossier = Path(args.dump)
    bilan: dict[str, int | str]
    if args.format == "pubmed":
        bilan = dict(parcourir_pubmed(dossier, Path(args.out), tax, limite=args.limite))
    else:
        bilan = parcourir_openalex(dossier, tax, Path(args.candidats))
    print(json.dumps(bilan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
