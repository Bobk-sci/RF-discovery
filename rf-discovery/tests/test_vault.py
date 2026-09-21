"""Coffre Obsidian : étiquettes dans les fiches et cartes de lecture."""
from __future__ import annotations

from pathlib import Path

from collect.europepmc import Paper
from library.classify import classify_paper, load_taxonomy
from library.organize import iter_fiches, read_front_matter, scan_library, write_article
from library.vault import CARTES, write_maps

TAX = load_taxonomy(Path(__file__).resolve().parents[1] / "config" / "taxonomy.yaml")
AXES = tuple(ax.name for ax in TAX.axes)

INVIVO = Paper(
    pmid="31234567", doi="10.1/x",
    title="Prenatal 900 MHz exposure and hippocampal neurogenesis in rats",
    abstract="Pregnant Wistar rats were exposed in vivo. Oxidative stress increased.",
    year=2019, journal="J", extra={"authors": ["Durand A", "Nowak K", "Roy P"]})
INVITRO = Paper(
    pmid="30000002", doi="",
    title="DNA damage in SH-SY5Y cell culture after 1800 MHz exposure",
    abstract="Comet assay on cultured cells; micronucleus frequency measured in vitro.",
    year=2018, journal="J", extra={"authors": ["Blanc M"]})


def _remplir(tmp_path):
    for paper in (INVIVO, INVITRO):
        write_article(tmp_path, paper, classify_paper(paper, TAX), AXES)
    return scan_library(tmp_path)


def test_les_fiches_portent_des_etiquettes_obsidian(tmp_path):
    path = write_article(tmp_path, INVIVO, classify_paper(INVIVO, TAX), AXES)
    tags = read_front_matter(path)["tags"]
    assert "rf" in tags and "modele/in_vivo" in tags
    assert "theme/neurodeveloppement" in tags and "annee/2019" in tags


def test_cartes_de_lecture(tmp_path):
    records = _remplir(tmp_path)
    assert write_maps(tmp_path, records, AXES) == 3      # deux catégories + accueil
    accueil = (tmp_path / CARTES / "Accueil.md").read_text(encoding="utf-8")
    assert "[[in_vivo]]" in accueil and "[[in_vitro]]" in accueil
    carte = (tmp_path / CARTES / "in_vivo.md").read_text(encoding="utf-8")
    assert "[[2019_31234567_" in carte              # wikilink vers la fiche
    assert "Durand A et al." in carte               # signature lisible
    assert "## neurodeveloppement (1)" in carte


def test_les_cartes_ne_sont_pas_prises_pour_des_articles(tmp_path):
    records = _remplir(tmp_path)
    write_maps(tmp_path, records, AXES)
    assert len(list(iter_fiches(tmp_path))) == 2
    assert len(scan_library(tmp_path)) == 2
