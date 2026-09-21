"""Dossier de lecture à partir d'une note de question.

    python -m rapport_question --note "_Notes/neurodeveloppement-age-exposition.md"

Smart Connections classe ; ce module **tabule**. Il lit une note de question, retient les
articles qu'elle désigne — les wikilinks que vous y avez collés depuis Smart Connections,
ou à défaut une sélection par mots-clés — et produit un dossier : la liste chronologique,
la répartition par modèle d'étude, et le tableau de relevé à remplir en lisant.

Ce dossier **n'interprète rien**. Il ne résume aucun article, ne conclut rien, n'invente
aucun chiffre : il ne contient que ce qui est déjà dans les fiches (année, revue, PMID,
classement) et la place pour ce que vous relèverez vous-même. Une synthèse rédigée
demande un lecteur — ou la commande `/synthese` de Claude Code, qui cite ses sources.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from library.organize import iter_fiches, read_article, read_front_matter

ROOT = Path(__file__).resolve().parents[1]
_LIEN = re.compile(r"\[\[([^\]|#]+)")
_VIDES = {"les", "des", "une", "dans", "pour", "avec", "sur", "par", "que", "qui", "aux",
          "est", "sont", "the", "and", "for", "with", "from", "that", "this", "during",
          "between", "whether", "their", "were", "have", "been", "after", "only"}


def mots_significatifs(texte: str) -> set[str]:
    mots = re.findall(r"[a-zà-ÿ0-9]{3,}", texte.lower())
    return {m for m in mots if m not in _VIDES}


def liens_de_la_note(texte: str) -> list[str]:
    """Noms de fiches cités en wikilinks dans la note."""
    return [nom.strip() for nom in _LIEN.findall(texte)]


def _score(chemin: Path, mots: set[str]) -> float:
    paper = read_article(chemin)
    corpus = mots_significatifs(f"{paper.title} {paper.abstract}")
    return len(mots & corpus) / max(len(mots), 1)


def selectionner(out: Path, note: str, limite: int = 20) -> tuple[list[Path], str]:
    """Fiches du dossier : celles que la note désigne, sinon les plus proches par mots."""
    par_nom = {p.stem: p for p in iter_fiches(out)}
    cites = [par_nom[n] for n in liens_de_la_note(note) if n in par_nom]
    if cites:
        return cites, "liens de la note"
    mots = mots_significatifs(note)
    classes = sorted(par_nom.values(), key=lambda p: -_score(p, mots))
    return classes[:limite], "sélection par mots-clés (approximative)"


def _ligne_tableau(meta: dict[str, Any], nom: str) -> str:
    pmid = str(meta.get("pmid") or "")
    lien = f"[{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)" if pmid.isdigit() else "—"
    return (f"| {meta.get('annee') or 's.d.'} | [[{nom}]] | "
            f"{meta.get('modele', '?')} / {meta.get('theme', '?')} | "
            f"{str(meta.get('journal') or '—')[:34]} | {lien} |")


def rendre(question: str, fiches: list[Path], origine: str, titre: str) -> str:
    """Texte du dossier : inventaire et tableau de relevé, rien d'interprété."""
    metas = [(read_front_matter(p), p.stem) for p in fiches]
    metas = [(m, n) for m, n in metas if m]
    metas.sort(key=lambda e: int(e[0].get("annee") or 0))
    modeles: dict[str, int] = {}
    for meta, _ in metas:
        cle = str(meta.get("modele") or "?")
        modeles[cle] = modeles.get(cle, 0) + 1
    repartition = ", ".join(f"{n} {c}" for c, n in sorted(modeles.items(), key=lambda kv: -kv[1]))
    annees = [int(m.get("annee") or 0) for m, _ in metas if m.get("annee")]
    sans_resume = sum(1 for p in fiches if not read_article(p).abstract)

    return "\n".join([
        f"# Dossier — {titre}", "",
        f"**{len(metas)} articles** · {repartition}"
        + (f" · publications {min(annees)}–{max(annees)}" if annees else ""),
        f"*Source de la sélection : {origine}.*", "",
        "## Question", "", question.strip(), "",
        "## Articles", "",
        "| Année | Fiche | Modèle / thème | Revue | PMID |",
        "| --- | --- | --- | --- | --- |",
        *[_ligne_tableau(m, n) for m, n in metas], "",
        "## À relever en lisant", "",
        "| PMID | Fréquence | SAR | Durée | Âge exposition | Âge test | Sexe | n | Effet |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        *[f"| {m.get('pmid') or '—'} | | | | | | | | |" for m, _ in metas], "",
        "## Ce que ce dossier ne dit pas", "",
        "Il n'interprète aucun résultat et ne résume aucun article : les résumés sont",
        "dans les fiches, recopiés mot pour mot. Les colonnes ci-dessus sont vides parce",
        "que ces paramètres ne figurent pas toujours dans un résumé — plusieurs demandent",
        "le texte intégral.", "",
        f"{sans_resume} fiche(s) de ce dossier n'ont pas de résumé fourni par la source."
        if sans_resume else "", "",
    ]) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Dossier de lecture d'une note de question")
    ap.add_argument("--note", required=True)
    ap.add_argument("--articles", default=str(ROOT / "articles"))
    ap.add_argument("--limite", type=int, default=20)
    args = ap.parse_args()

    note = Path(args.note)
    texte = note.read_text(encoding="utf-8")
    fiches, origine = selectionner(Path(args.articles), texte, args.limite)
    dossier = note.with_name(f"{note.stem} — dossier.md")
    dossier.write_text(rendre(texte, fiches, origine, note.stem), encoding="utf-8")
    print(json.dumps({"articles": len(fiches), "origine": origine,
                      "dossier": str(dossier)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
