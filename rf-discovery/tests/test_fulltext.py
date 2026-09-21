"""Texte intégral Europe PMC : conversion JATS et écriture des annexes (aucun réseau)."""
from __future__ import annotations

from pathlib import Path

from fetch_fulltext import fetch_all, fetch_one, xml_vers_markdown

FIX = Path(__file__).resolve().parent / "fixtures"
XML = (FIX / "epmc_fulltext.xml").read_text(encoding="utf-8")


def test_conversion_garde_les_sections_et_ecarte_le_reste():
    md = xml_vers_markdown(XML)
    assert "## Introduction" in md and "## Materials and Methods" in md
    assert "Radiofrequency exposure has been studied in rodent models." in md
    assert "SAR 1.5 W/kg" in md
    # Figures, tableaux et bibliographie n'apportent rien à une lecture ou à une recherche.
    assert "Figure caption" not in md and "Table caption" not in md
    assert "référence à ne pas recopier" not in md


def test_xml_vide_ou_illisible_ne_leve_pas():
    assert xml_vers_markdown("") == ""
    assert xml_vers_markdown("<pas du xml") == ""
    assert xml_vers_markdown("<article><front/></article>") == ""   # pas de <body>


def test_article_hors_acces_libre_rend_une_chaine_vide():
    """Europe PMC renvoie une réponse vide : on compte, on ne contourne pas."""
    assert fetch_one("PMC1", fetcher=lambda _u, _p: "") == ""

    def refuse(_u, _p):
        raise RuntimeError("404")

    assert fetch_one("PMC1", fetcher=refuse) == ""


def test_fetch_all_ecrit_une_annexe_par_article(tmp_path):
    records = [
        {"pmid": "1", "pmcid": "PMC1", "titre": "T", "auteurs": ["Durand A"],
         "journal": "J", "annee": 2019, "doi": "10.1/x"},
        {"pmid": "2", "pmcid": "", "titre": "Sans PMC"},
        {"pmid": "3", "pmcid": "PMC3", "titre": "Non libre"},
    ]
    counts = fetch_all(records, tmp_path, sleep=lambda _s: None,
                       fetcher=lambda url, _p: XML if "PMC1/" in url else "")
    assert counts == {"deja_present": 0, "recuperes": 1, "sans_pmcid": 1,
                      "non_disponible": 1}
    texte = (tmp_path / "1.md").read_text(encoding="utf-8")
    assert texte.startswith("# T") and "Durand A" in texte
    assert "Europe PMC" in texte and "## Introduction" in texte
    assert not (tmp_path / "3.md").exists()

    # Deuxième passage : rien n'est re-téléchargé.
    again = fetch_all(records, tmp_path, sleep=lambda _s: None,
                      fetcher=lambda url, _p: XML if "PMC1/" in url else "")
    assert again["deja_present"] == 1 and again["recuperes"] == 0
