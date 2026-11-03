"""Filtrage local d'un corpus en vrac : lecture incrémentale, aucune référence fabriquée.

Les archives sont construites à la volée depuis les fixtures : aucun accès réseau, aucun
téléchargement. Un test garde explicitement la règle qui interdit de reconstruire le
résumé d'OpenAlex.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from import_baseline import (
    lire_pubmed,
    parcourir_openalex,
    parcourir_pubmed,
    scanner_openalex,
)
from library.classify import load_taxonomy

FIX = Path(__file__).resolve().parent / "fixtures"
TAX = load_taxonomy(Path(__file__).resolve().parents[1] / "config" / "taxonomy.yaml")


def _baseline(dossier: Path, nom: str = "pubmed26n0001.xml.gz") -> Path:
    """Fabrique un fichier baseline gzippé à partir de la fixture efetch."""
    chemin = dossier / nom
    chemin.write_bytes(gzip.compress((FIX / "pubmed_efetch.xml").read_bytes()))
    return chemin


def _snapshot(dossier: Path, lignes: list[dict], nom: str = "part_0000.gz") -> Path:
    chemin = dossier / nom
    corps = "\n".join(json.dumps(x, ensure_ascii=False) for x in lignes)
    chemin.write_bytes(gzip.compress(corps.encode("utf-8")))
    return chemin


def test_lecture_incrementale_rend_les_memes_notices(tmp_path):
    chemin = _baseline(tmp_path)
    papers = list(lire_pubmed(chemin, lot=1))      # lot=1 force le découpage
    assert papers, "le baseline doit rendre au moins une notice"
    assert all(p.pmid for p in papers)
    # Titre et résumé viennent du parseur déjà utilisé en ligne : rien n'est reconstruit.
    assert all(p.title for p in papers)


def test_decoupage_en_lots_ne_perd_aucune_notice(tmp_path):
    chemin = _baseline(tmp_path)
    assert [p.pmid for p in lire_pubmed(chemin, lot=1)] == \
           [p.pmid for p in lire_pubmed(chemin, lot=500)]


def test_parcours_pubmed_ecrit_des_fiches(tmp_path):
    dump = tmp_path / "dump"
    dump.mkdir()
    _baseline(dump)
    out = tmp_path / "articles"
    bilan = parcourir_pubmed(dump, out, TAX)
    assert bilan["fichiers"] == 1
    assert bilan["notices"] >= 1
    assert bilan["retenues"] + bilan["ecartees"] == bilan["notices"]


def test_openalex_ne_retient_que_les_titres_portant_un_terme_rf(tmp_path):
    chemin = _snapshot(tmp_path, [
        {"title": "Radiofrequency exposure and hippocampal neurogenesis",
         "ids": {"pmid": "https://pubmed.ncbi.nlm.nih.gov/31234567"}},
        {"title": "Effects of microwave radiation on the rat cerebellum",
         "ids": {"doi": "https://doi.org/10.1000/ONLY-A-DOI.2021"}},
        # `rf_terms` ne contient pas « microwave » seul mais des locutions : la chimie
        # assistée par micro-ondes ne doit pas entrer, et c'est ce qui tient le filtre.
        {"title": "Microwave-assisted synthesis of fused heterocycles",
         "ids": {"doi": "https://doi.org/10.1000/CHEM.2021"}},
        {"title": "Predicting rainfall with satellite imagery", "ids": {"pmid": "1"}},
    ])
    trouves = list(scanner_openalex(chemin, TAX))
    retenus = {p or d for p, d in trouves}
    assert retenus == {"31234567", "10.1000/only-a-doi.2021"}
    assert len(trouves) == 2


def test_openalex_ne_fabrique_aucune_fiche(tmp_path):
    dump = tmp_path / "dump"
    dump.mkdir()
    _snapshot(dump, [{"title": "5G radiofrequency exposure in rats",
                      "abstract_inverted_index": {"Exposure": [0], "to": [1]},
                      "ids": {"pmid": "https://pubmed.ncbi.nlm.nih.gov/42000001"}}])
    sortie = tmp_path / "candidats.json"
    bilan = parcourir_openalex(dump, TAX, sortie)
    assert bilan["pmids"] == 1
    donnees = json.loads(sortie.read_text(encoding="utf-8"))
    assert donnees["pmids"] == ["42000001"]
    # Aucune fiche, et surtout aucun résumé reconstruit depuis l'index inversé.
    assert not list(tmp_path.glob("articles/**/*.md"))
    assert "Exposure" not in sortie.read_text(encoding="utf-8")


def test_dossier_vide_ne_fabrique_rien(tmp_path):
    vide = tmp_path / "vide"
    vide.mkdir()
    assert parcourir_pubmed(vide, tmp_path / "articles", TAX)["notices"] == 0
    assert parcourir_openalex(vide, TAX, tmp_path / "c.json")["pmids"] == 0
