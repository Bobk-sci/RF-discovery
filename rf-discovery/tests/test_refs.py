"""Export RIS/BibTeX et récupération des PDF en accès libre (aucun réseau : injections)."""
from __future__ import annotations

from pathlib import Path

from collect.europepmc import Paper
from export_refs import collect_records
from fetch_pdfs import fetch_all, oa_pdf_url
from library.classify import classify_paper, load_taxonomy
from library.organize import write_article
from library.refs import to_bibtex, to_ris

TAXONOMY = Path(__file__).resolve().parents[1] / "config" / "taxonomy.yaml"
TAX = load_taxonomy(TAXONOMY)
AXES = tuple(ax.name for ax in TAX.axes)

ARTICLE = Paper(
    pmid="31234567", doi="10.1000/fixture.2019.01",
    title="Prenatal 900 MHz exposure and hippocampal neurogenesis in rats",
    abstract="Pregnant Wistar rats were exposed in vivo. Oxidative stress increased.",
    year=2019, journal="Journal of Fixture Neuroscience", source="pubmed",
    extra={"authors": ["Durand A", "Nowak K"], "mesh": ["Animals", "Rats"],
           "types": ["Journal Article"], "volume": "12", "pages": "45-53",
           "keywords": ["neurodevelopment"]})


def _library(tmp_path) -> list[dict]:
    write_article(tmp_path, ARTICLE, classify_paper(ARTICLE, TAX), AXES)
    return collect_records(tmp_path)


def test_ris_porte_auteurs_identifiants_et_classement(tmp_path):
    ris = to_ris(_library(tmp_path), AXES)
    assert "TY  - JOUR" in ris and ris.rstrip().endswith("ER  -")
    assert "AU  - Durand A" in ris and "AU  - Nowak K" in ris
    assert "DO  - 10.1000/fixture.2019.01" in ris and "AN  - 31234567" in ris
    assert "KW  - modele:in_vivo" in ris and "KW  - theme:neurodeveloppement" in ris
    assert "AB  - Pregnant Wistar rats" in ris
    assert "VL  - 12" in ris and "SP  - 45-53" in ris


def test_ris_omet_les_champs_absents(tmp_path):
    nu = Paper(pmid="1", doi="", title="Sans rien", abstract="", year=0, journal="")
    ris = to_ris([{"titre": nu.title, "pmid": "1"}], AXES)
    assert "DO  -" not in ris and "AB  -" not in ris and "AU  -" not in ris


def test_ris_attache_le_pdf_present(tmp_path):
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / "31234567.pdf").write_bytes(b"%PDF-1.4")
    records = _library(tmp_path)
    assert "L1  - " in to_ris(records, AXES, pdf_dir)
    assert "L1  - " not in to_ris(records, AXES, tmp_path / "vide")


def test_bibtex_cle_unique_et_champs(tmp_path):
    records = _library(tmp_path) * 2          # deux fois le même auteur/année
    bib = to_bibtex(records, AXES)
    assert bib.count("@article{") == 2
    assert "@article{durand2019,\n" in bib and "@article{durand2019a,\n" in bib
    assert "author = {Durand A and Nowak K}" in bib
    assert "keywords = {modele:in_vivo, theme:neurodeveloppement" in bib


def test_unpaywall_rend_le_pdf_libre_sinon_vide():
    dispo = {"best_oa_location": {"url_for_pdf": "https://ex.org/a.pdf"}}
    assert oa_pdf_url("10.1/x", "a@b.c", fetcher=lambda u, p: dispo) == "https://ex.org/a.pdf"
    ferme = {"best_oa_location": None, "oa_locations": []}
    assert oa_pdf_url("10.1/x", "a@b.c", fetcher=lambda u, p: ferme) == ""


def test_unpaywall_replie_sur_une_autre_localisation():
    data = {"best_oa_location": {}, "oa_locations": [{"url": "x"},
                                                    {"url_for_pdf": "https://ex.org/b.pdf"}]}
    assert oa_pdf_url("10.1/x", "a@b.c", fetcher=lambda u, p: data).endswith("b.pdf")


def test_unpaywall_indisponible_ne_leve_pas():
    def boom(_u, _p):
        raise RuntimeError("réseau")

    assert oa_pdf_url("10.1/x", "a@b.c", fetcher=boom) == ""


def test_fetch_all_compte_chaque_situation(tmp_path):
    records = [
        {"pmid": "1", "doi": "10.1/libre"},
        {"pmid": "2", "doi": "10.1/ferme"},
        {"pmid": "3", "doi": ""},
        {"pmid": "4", "doi": "10.1/deja"},
    ]
    (tmp_path / "4.pdf").write_bytes(b"%PDF")
    counts = fetch_all(
        records, tmp_path, "a@b.c",
        url_resolver=lambda doi: "https://ex.org/x.pdf" if doi.endswith("libre") else "",
        downloader=lambda url, target: bool(target.write_bytes(b"%PDF") or True),
        sleep=lambda _s: None)
    assert counts == {"deja_present": 1, "telecharges": 1, "sans_acces_libre": 1,
                      "sans_doi": 1, "echecs": 0}
    assert (tmp_path / "1.pdf").exists()


def test_un_peage_ne_produit_pas_de_fichier(tmp_path):
    """Une page HTML renvoyée à la place d'un PDF est un échec, pas une fiche muette."""
    counts = fetch_all([{"pmid": "9", "doi": "10.1/x"}], tmp_path, "a@b.c",
                       url_resolver=lambda _d: "https://ex.org/paywall",
                       downloader=lambda _u, _t: False, sleep=lambda _s: None)
    assert counts["echecs"] == 1 and not (tmp_path / "9.pdf").exists()
