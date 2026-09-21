"""Compte rendu de collecte et dossier de question : inventaire, jamais interprétation."""
from __future__ import annotations

from pathlib import Path

from collect.europepmc import Paper
from library.classify import classify_paper, load_taxonomy
from library.digest import rendre as rendre_veille
from library.digest import write_digest
from library.organize import write_article
from rapport_question import liens_de_la_note, rendre, selectionner

TAX = load_taxonomy(Path(__file__).resolve().parents[1] / "config" / "taxonomy.yaml")
AXES = tuple(ax.name for ax in TAX.axes)

A = Paper(pmid="31234567", doi="10.1/a",
          title="Prenatal 900 MHz exposure and hippocampal neurogenesis in rats",
          abstract="Pregnant Wistar rats were exposed in vivo. Oxidative stress increased.",
          year=2019, journal="Brain Research", extra={"authors": ["Durand A", "Roy P", "Sy K"]})
B = Paper(pmid="30000002", doi="",
          title="DNA damage in SH-SY5Y cell culture after 1800 MHz exposure",
          abstract="Comet assay on cultured cells; micronucleus frequency measured in vitro.",
          year=2018, journal="Mutation Research", extra={"authors": ["Blanc M"]})


def _bibliotheque(tmp_path):
    return [write_article(tmp_path, p, classify_paper(p, TAX), AXES) for p in (A, B)]


def test_compte_rendu_de_collecte_groupe_par_categorie(tmp_path):
    fiches = _bibliotheque(tmp_path)
    texte = rendre_veille(fiches, tmp_path, {"_ecartes": 3}, "2026-09-21")
    assert "2 nouveaux articles" in texte and "3 notices écartées" in texte
    assert "## in_vivo / neurodeveloppement (1)" in texte
    assert "[[2019_31234567_" in texte and "Durand A et al." in texte
    assert "ne résume aucun article" in texte


def test_compte_rendu_vide_le_dit(tmp_path):
    chemin = write_digest(tmp_path, [], {}, jour="2026-09-28")
    texte = chemin.read_text(encoding="utf-8")
    assert "0 nouveaux articles" in texte and "Rien de nouveau" in texte


def test_les_liens_de_la_note_font_la_selection(tmp_path):
    fiches = _bibliotheque(tmp_path)
    note = f"Ma question.\n\n- [[{fiches[0].stem}]] — à lire\n"
    choisies, origine = selectionner(tmp_path, note)
    assert choisies == [fiches[0]] and origine == "liens de la note"


def test_sans_lien_la_selection_se_fait_par_mots(tmp_path):
    _bibliotheque(tmp_path)
    note = "Comet assay micronucleus cultured cells genotoxicity in vitro"
    choisies, origine = selectionner(tmp_path, note, limite=1)
    assert "30000002" in choisies[0].stem and "approximative" in origine


def test_liens_de_la_note_ignore_alias_et_ancres():
    assert liens_de_la_note("[[fiche-a|Alias]] et [[fiche-b#section]]") == \
        ["fiche-a", "fiche-b"]


def test_le_dossier_inventorie_sans_conclure(tmp_path):
    fiches = _bibliotheque(tmp_path)
    texte = rendre("Ma question de départ.", fiches, "liens de la note", "ma-note")
    assert "**2 articles**" in texte and "publications 2018–2019" in texte
    assert "1 in_vivo" in texte and "1 in_vitro" in texte
    assert "| 2018 |" in texte and "pubmed.ncbi.nlm.nih.gov/30000002" in texte
    assert "Ma question de départ." in texte
    # Tableau de relevé : une ligne par article, colonnes vides à remplir en lisant.
    assert "| Fréquence | SAR | Durée |" in texte
    assert "n'interprète aucun résultat" in texte
