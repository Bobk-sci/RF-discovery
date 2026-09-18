"""Bibliothèque RF : classement déterministe, rangement, sources PubMed/EMF-Portal.

Aucun accès réseau : fixtures et fetchers injectés. Un test garde explicitement la
règle « aucune référence inventée » : ce qui manque à la source reste vide.
"""
from __future__ import annotations

from pathlib import Path

from collect import emfportal, pubmed
from collect.europepmc import Paper
from collect_library import collect, file_papers, reclasser
from library.classify import (
    build_query,
    classify,
    classify_paper,
    is_off_topic,
    load_taxonomy,
    meta_text,
)
from library.importer import papers_from_json
from library.organize import (
    article_path,
    read_article,
    render_article,
    scan_library,
    write_article,
    write_index,
    write_readme,
)

FIX = Path(__file__).resolve().parent / "fixtures"
TAXONOMY = Path(__file__).resolve().parents[1] / "config" / "taxonomy.yaml"
TAX = load_taxonomy(TAXONOMY)
AXES = tuple(ax.name for ax in TAX.axes)

INVIVO = Paper(
    pmid="31234567", doi="10.1000/fixture.2019.01",
    title="Prenatal 900 MHz exposure and hippocampal neurogenesis in rats",
    abstract="Pregnant Wistar rats were exposed in vivo. Oxidative stress increased.",
    year=2019, journal="Journal of Fixture Neuroscience", source="pubmed")
INVITRO = Paper(
    pmid="30000002", doi="",
    title="DNA damage in SH-SY5Y cell culture after 1800 MHz exposure",
    abstract="Comet assay on cultured cells; micronucleus frequency measured in vitro.",
    year=2018, journal="Fixture In Vitro", source="europepmc")


def test_classement_deux_axes_et_determinisme():
    first, second = classify(INVIVO.title, INVIVO.abstract, TAX), \
        classify(INVIVO.title, INVIVO.abstract, TAX)
    assert first["modele"].category == "in_vivo"
    assert first["theme"].category == "neurodeveloppement"
    assert {k: v.category for k, v in first.items()} == {k: v.category
                                                        for k, v in second.items()}
    assert "prenatal" in [m.lower() for m in first["theme"].matched]


def test_in_vitro_et_theme_genotoxicite():
    out = classify(INVITRO.title, INVITRO.abstract, TAX)
    assert out["modele"].category == "in_vitro"
    assert out["theme"].category == "genotoxicite_epigenetique"


def test_hors_sujet_tombe_dans_les_categories_par_defaut():
    out = classify("A survey of medieval pottery kilns", "Ceramic shards were counted.", TAX)
    assert out["modele"].category == "non_classe" and out["theme"].category == "general"
    assert out["modele"].score == 0.0


def test_mot_cle_borne_aux_limites_de_mots():
    """« rat » ne doit pas se déclencher sur « generated », ni « SAR » sur « sarcoma »."""
    out = classify("Data generated from sarcoma registries", "Nothing relevant here.", TAX)
    assert out["modele"].category == "non_classe"


def test_le_titre_pese_plus_que_le_resume():
    titre = classify("In vitro study", "", TAX)["modele"]
    resume = classify("Study", "in vitro", TAX)["modele"]
    assert titre.score > resume.score


def test_arborescence_et_index(tmp_path):
    for paper in (INVIVO, INVITRO):
        write_article(tmp_path, paper, classify(paper.title, paper.abstract, TAX), AXES)
    path = article_path(tmp_path, INVIVO, classify(INVIVO.title, INVIVO.abstract, TAX), AXES)
    assert path.relative_to(tmp_path).parts[:2] == ("in_vivo", "neurodeveloppement")
    assert path.name.startswith("2019_31234567_")
    records = scan_library(tmp_path)
    assert len(records) == 2
    index = write_index(tmp_path, records, AXES)
    lines = index.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("pmid,doi,annee,modele,theme")
    assert any("31234567" in ln and "in_vivo" in ln for ln in lines[1:])
    readme = write_readme(tmp_path, records, TAX, "requête")
    assert "2 articles" in readme.read_text(encoding="utf-8")


def test_rerun_idempotent(tmp_path):
    assignments = classify(INVIVO.title, INVIVO.abstract, TAX)
    write_article(tmp_path, INVIVO, assignments, AXES)
    write_article(tmp_path, INVIVO, assignments, AXES)
    assert len(list(tmp_path.rglob("*.md"))) == 1


def test_aucune_reference_inventee(tmp_path):
    """Champs absents de la source : vides. Jamais de résumé ou de DOI fabriqué."""
    nu = Paper(pmid="28000001", doi="", title="A note without abstract or DOI",
               abstract="", year=0, journal="", source="pubmed")
    texte = render_article(nu, classify(nu.title, nu.abstract, TAX), AXES)
    assert "doi: ''" in texte
    assert "_Résumé non fourni par la source._" in texte
    assert "https://pubmed.ncbi.nlm.nih.gov/28000001/" in texte
    sans_id = Paper(pmid="", doi="", title="Anonyme", abstract="", year=0, journal="")
    assert "Référence d'origine" not in render_article(
        sans_id, classify("Anonyme", "", TAX), AXES)


def test_fiche_relue_conserve_le_texte_dorigine(tmp_path):
    path = write_article(tmp_path, INVIVO, classify(INVIVO.title, INVIVO.abstract, TAX), AXES)
    relu = read_article(path)
    assert relu.abstract == INVIVO.abstract and relu.title == INVIVO.title
    assert relu.pmid == "31234567" and relu.year == 2019


def test_reclassement_deplace_les_fiches(tmp_path, monkeypatch):
    write_article(tmp_path, INVITRO, classify(INVITRO.title, INVITRO.abstract, TAX), AXES)
    taxo = tmp_path / "taxo.yaml"
    taxo.write_text(TAXONOMY.read_text(encoding="utf-8").replace(
        "      - name: in_vitro", "      - name: cellules"), encoding="utf-8")
    out = reclasser(tmp_path, load_taxonomy(taxo))
    assert out["fiches_deplacees"] == 1
    assert not (tmp_path / "in_vitro").exists()
    assert list((tmp_path / "cellules").rglob("*.md"))


def test_parse_pubmed_xml():
    papers = pubmed.parse_pubmed_xml(
        (FIX / "pubmed_efetch.xml").read_text(encoding="utf-8"))
    assert [p.pmid for p in papers] == ["31234567", "28000001"]
    assert papers[0].doi == "10.1000/fixture.2019.01" and papers[0].year == 2019
    assert papers[0].abstract.startswith("BACKGROUND: Pregnant Wistar rats")
    assert papers[1].year == 2017 and papers[1].doi == "" and papers[1].abstract == ""


def test_pubmed_search_pagine_et_recupere(tmp_path):
    xml = (FIX / "pubmed_efetch.xml").read_text(encoding="utf-8")
    calls: list[dict] = []

    def fake_json(url, params):
        calls.append(params)
        start = int(params["retstart"])
        ids = ["31234567", "28000001"][start:start + int(params["retmax"])]
        return {"esearchresult": {"idlist": ids}}

    papers = pubmed.search("rf", max_results=2, fetcher_json=fake_json,
                           fetcher_text=lambda u, p: xml)
    assert [p.pmid for p in papers] == ["31234567", "28000001"]
    assert calls and calls[0]["db"] == "pubmed"


def test_pubmed_xml_illisible_ne_leve_pas():
    assert pubmed.parse_pubmed_xml("<pas du xml") == []


def test_emfportal_extrait_les_identifiants():
    pmids, dois = emfportal.extract_ids(
        (FIX / "emfportal_results.html").read_text(encoding="utf-8"))
    assert pmids == ["28000001", "31234567"]      # liens d'abord, puis « PMID: »
    assert "12345" not in pmids                   # un numéro de page n'est pas un PMID
    assert dois == ["10.1000/only-a-doi.2021"]


def test_emfportal_resout_via_pubmed_et_epmc():
    xml = (FIX / "pubmed_efetch.xml").read_text(encoding="utf-8")
    epmc = [Paper(pmid="", doi="10.1000/only-a-doi.2021", title="Study indexed by DOI only",
                  abstract="", year=2021, journal="Fixture", source="europepmc")]
    papers = emfportal.resolve(
        emfportal.read_files([FIX / "emfportal_results.html"]),
        fetcher_text=lambda u, p: xml,
        search_epmc=lambda q, max_results=40: epmc if "only-a-doi" in q else [])
    assert {p.pmid for p in papers} >= {"31234567", "28000001"}
    assert any(p.doi == "10.1000/only-a-doi.2021" for p in papers)
    assert all(p.extra.get("via") == "emf-portal" for p in papers)


def test_emfportal_indisponible_ne_fabrique_rien():
    def boom(url, params):
        raise RuntimeError("portail injoignable")

    assert emfportal.fetch_pages("rf", fetcher_text=boom) == []
    assert emfportal.resolve([], fetcher_text=boom) == []


def test_requete_contient_les_termes_rf_et_les_filtres():
    query = build_query(TAX)
    assert '"specific absorption rate"' in query and "HAS_ABSTRACT:Y" in query
    assert "FIRST_PDATE" in query


def test_les_mesh_orientent_le_classement():
    """Un résumé vague mais des MeSH « Animals/Rats » : l'article est bien in vivo."""
    vague = Paper(pmid="1", doi="", title="Exposure study", abstract="Effects were assessed.",
                  year=2020, journal="",
                  extra={"mesh": ["Animals", "Rats", "Brain"], "types": ["Journal Article"]})
    assert classify_paper(vague, TAX)["modele"].category == "in_vivo"
    assert "Animals" in meta_text(vague.extra)


def test_le_type_de_publication_designe_une_revue():
    revue = Paper(pmid="2", doi="", title="Exposure and the brain", abstract="We summarise.",
                  year=2020, journal="", extra={"types": ["Review", "Journal Article"]})
    assert classify_paper(revue, TAX)["modele"].category == "revue"


def test_methodologie_irm_ecartee_du_corpus(tmp_path):
    irm = Paper(pmid="3", doi="", title="Radiofrequency coil design for 7T imaging",
                abstract="Specific absorption rate was simulated.", year=2021, journal="",
                extra={"mesh": ["Magnetic Resonance Imaging"]})
    assert is_off_topic(irm, TAX) == "radiofrequency coil"
    assert is_off_topic(INVIVO, TAX) == ""
    counts = file_papers(tmp_path, [irm, INVIVO], TAX)
    assert counts["_ecartes"] == 1 and counts["in_vivo"] == 1
    assert len(list(tmp_path.rglob("*.md"))) == 1


def test_lignee_cellulaire_prime_sur_le_mesh_animals():
    """PubMed pose « Animals/Mice » sur une étude de cellules NIH 3T3 : in vitro quand même."""
    cellules = Paper(pmid="5", doi="", title="Apoptotic effect of 1800 MHz radiation",
                     abstract="Cells were exposed.", year=2015, journal="",
                     extra={"mesh": ["Animals", "Mice", "NIH 3T3 Cells", "Apoptosis"]})
    assert classify_paper(cellules, TAX)["modele"].category == "in_vitro"


def test_in_vivo_dans_le_titre_prime_sur_la_lignee_greffee():
    """Tumeur greffée : MeSH « Cell Line, Tumor » mais les auteurs écrivent « in vivo »."""
    greffe = Paper(pmid="6", doi="",
                   title="Effects of radiofrequency fields on in vivo C6 brain tumors in rats",
                   abstract="Wistar rats bearing tumors were exposed.", year=2013, journal="",
                   extra={"mesh": ["Animals", "Rats, Wistar", "Cell Line, Tumor"]})
    assert classify_paper(greffe, TAX)["modele"].category == "in_vivo"


def test_bonus_decisif_compte_une_seule_fois():
    """« Cell Line » et « Cell Line, Tumor » décrivent le même fait : pas de cumul."""
    une = Paper(pmid="7", doi="", title="Exposure", abstract="", year=2020, journal="",
                extra={"mesh": ["Cell Line"]})
    deux = Paper(pmid="8", doi="", title="Exposure", abstract="", year=2020, journal="",
                 extra={"mesh": ["Cell Line", "Cell Line, Tumor", "Cells, Cultured"]})
    ecart = classify_paper(deux, TAX)["modele"].score - classify_paper(une, TAX)["modele"].score
    assert 0 <= ecart < 100          # écart dû aux mots-clés seuls, pas à un bonus cumulé


def test_filtre_de_pertinence_ecarte_le_hors_sujet():
    """Constaté sur PubMed : « GSM » ramène des articles sur la géosmine."""
    geosmine = Paper(pmid="9", doi="", title="Identification of geosmin (GSM) in water",
                     abstract="Purge and trap gas chromatography was used.",
                     year=2024, journal="")
    assert is_off_topic(geosmine, TAX) == "aucun terme d'exposition RF"


def test_annulation_protege_une_etude_dexposition():
    """Une étude de provocation qui mesure par IRM ne doit pas tomber dans l'exclusion IRM."""
    provocation = Paper(pmid="10", doi="",
                        title="Mobile phone exposure and cerebral blood flow",
                        abstract="A double-blind sham exposure protocol was used.",
                        year=2019, journal="", extra={"mesh": ["Magnetic Resonance Imaging"]})
    assert is_off_topic(provocation, TAX) == ""
    methode = Paper(pmid="11", doi="", title="Open birdcage coil for head imaging at 7T",
                    abstract="The specific absorption rate was simulated.", year=2021,
                    journal="", extra={"mesh": ["Magnetic Resonance Imaging"]})
    assert is_off_topic(methode, TAX) == "Magnetic Resonance Imaging"


def test_import_json_et_notices_incompletes(tmp_path):
    papers = papers_from_json(FIX / "library_import.json")
    assert [p.pmid for p in papers] == ["40000001", "40000002", ""]   # rien n'est jeté
    assert papers[0].year == 2022 and papers[0].journal == "Fixture Journal of Imports"
    assert papers[0].extra["mesh"] == ["Animals", "Rats", "Brain", "Pregnancy"]
    counts = file_papers(tmp_path, papers, TAX)
    assert counts["_ecartes"] == 2            # la notice IRM et celle qui est vide
    assert counts.get("in_vivo") == 1


def test_descripteurs_survivent_a_la_relecture(tmp_path):
    riche = Paper(pmid="4", doi="", title="Exposure study", abstract="Effects.", year=2020,
                  journal="", extra={"mesh": ["Animals", "Rats"], "types": ["Review"],
                                     "keywords": ["SAR"]})
    path = write_article(tmp_path, riche, classify_paper(riche, TAX), AXES)
    relu = read_article(path)
    assert relu.extra["mesh"] == ["Animals", "Rats"] and relu.extra["types"] == ["Review"]
    assert classify_paper(relu, TAX)["modele"].category == "revue"


def test_collect_agrege_les_sources(monkeypatch, tmp_path):
    monkeypatch.setattr("collect_library.epmc_search",
                        lambda *a, **k: [INVITRO])
    monkeypatch.setattr(pubmed, "search", lambda *a, **k: [INVIVO])
    papers = collect(TAX, ["europepmc", "pubmed"], 10, emfportal_url="",
                     emfportal_files=[], email="", api_key="")
    assert {p.pmid for p in papers} == {"30000002", "31234567"}
    counts = file_papers(tmp_path, papers, TAX)
    assert counts == {"in_vivo": 1, "in_vitro": 1}
