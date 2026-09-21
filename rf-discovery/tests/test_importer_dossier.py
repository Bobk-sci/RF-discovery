"""Intégration d'un dossier de PDF existant : on cherche par titre, on n'invente jamais."""
from __future__ import annotations

from pathlib import Path

from collect.europepmc import Paper
from importer_dossier import chercher, importer_dossier, similarite, titre_depuis_nom
from library.classify import load_taxonomy
from library.organize import iter_fiches, read_front_matter
from library.refs import to_ris

TAX = load_taxonomy(Path(__file__).resolve().parents[1] / "config" / "taxonomy.yaml")
AXES = tuple(ax.name for ax in TAX.axes)

TROUVE = Paper(
    pmid="6925593", doi="10.1080/x",
    title="Effect of 2,450 MHz microwave radiation on the development of the rat brain",
    abstract="Pregnant rats were exposed in vivo; offspring brain weight was measured.",
    year=1982, journal="J Microw Power",
    extra={"authors": ["Smialowicz RJ"], "mesh": ["Animals", "Rats", "Pregnancy"]})


def test_titre_depuis_nom_nettoie_numero_et_copie():
    assert titre_depuis_nom(Path("100_Effect of 2,450 MHz microwave radiation.pdf")) == \
        "Effect of 2,450 MHz microwave radiation"
    assert titre_depuis_nom(Path("2_Intl J - Tüfekci - An Evaluation (1).pdf")) == \
        "Intl J - Tüfekci - An Evaluation"


def test_similarite_tolere_une_troncature():
    complet = "Effect of 2,450 MHz microwave radiation on the development of the rat brain"
    assert similarite(complet, complet) == 1.0
    assert similarite("Effect of 2,450 MHz microwave radiation", complet) > 0.9
    assert similarite("Mobile phone use and glioma risk", complet) < 0.3


def test_chercher_refuse_une_correspondance_trop_lointaine():
    autre = Paper(pmid="1", doi="", title="Something entirely different about sleep",
                  abstract="", year=2020, journal="")
    assert chercher("Effect of 2,450 MHz microwave radiation on the rat brain",
                    search=lambda q, **kw: [autre]) is None
    assert chercher(TROUVE.title, search=lambda q, **kw: [autre, TROUVE]) is TROUVE


def test_import_cree_la_fiche_et_retient_le_pdf(tmp_path):
    dossier = tmp_path / "raw"
    dossier.mkdir()
    pdf = dossier / ("100_Effect of 2,450 MHz microwave radiation on the "
                     "development of the rat brain.pdf")
    pdf.write_bytes(b"%PDF-1.4")
    out = tmp_path / "articles"

    res = importer_dossier(dossier, out, TAX, search=lambda q, **kw: [TROUVE])
    assert res["pdf"] == 1 and res["importes"] == 1 and res["non_resolus"] == []

    fiche = next(iter_fiches(out))
    meta = read_front_matter(fiche)
    assert meta["pmid"] == "6925593"                      # métadonnées de la SOURCE
    assert meta["auteurs"] == ["Smialowicz RJ"]
    assert meta["pdf_local"] == str(pdf.resolve())
    assert "in_vivo" in str(fiche)                        # classé comme les autres
    # Le PDF apporté par l'utilisateur part dans le RIS : Zotero l'attachera.
    meta["fichier"] = str(fiche.relative_to(out))
    assert "L1  - file:///" in to_ris([meta], AXES)


def test_un_pdf_sans_notice_correspondante_est_signale_pas_fabrique(tmp_path):
    dossier = tmp_path / "raw"
    dossier.mkdir()
    (dossier / "Article1.pdf").write_bytes(b"%PDF")
    out = tmp_path / "articles"

    res = importer_dossier(dossier, out, TAX, search=lambda q, **kw: [])
    assert res["non_resolus"] == ["Article1.pdf"] and res["importes"] == 0
    assert list(iter_fiches(out)) == []      # aucune fiche inventée depuis le nom


def test_article_deja_present_est_saute(tmp_path):
    from normalize.dedupe import normalize_title

    dossier = tmp_path / "raw"
    dossier.mkdir()
    (dossier / f"1_{TROUVE.title}.pdf").write_bytes(b"%PDF")
    res = importer_dossier(dossier, tmp_path / "articles", TAX,
                           deja={normalize_title(TROUVE.title)},
                           search=lambda q, **kw: [TROUVE])
    assert res["deja_presents"] == 1 and res["importes"] == 0
