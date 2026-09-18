"""Classement déterministe d'un article dans les axes de ``config/taxonomy.yaml``.

Principe : pour chaque catégorie, on compte les mots-clés présents dans le titre et le
résumé **de l'article réel** ; le titre pèse ``title_boost`` fois plus. La catégorie la
mieux notée gagne, l'ordre de déclaration départage les ex æquo. Sous ``min_score``, on
tombe dans la catégorie par défaut de l'axe : mieux vaut ``non_classe`` qu'un rangement
arbitraire.

Aucun modèle de langue n'intervient : le résultat est identique d'un run à l'autre et
chaque décision est traçable (les mots-clés déclencheurs sont conservés).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Category:
    name: str
    keywords: tuple[str, ...]
    # Descripteurs qui tranchent à eux seuls : un type de publication « Review » attribué
    # par PubMed est plus sûr que n'importe quel comptage de mots du résumé.
    decisifs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Exclusion:
    """Terme qui écarte une notice, éventuellement annulé par une marque d'exposition.

    L'annulation est attachée à l'exclusion, pas globale : « mobile phone » doit sauver
    une étude de provocation mesurée par IRM, sans pour autant sauver un article sur
    l'addiction au téléphone.
    """

    terme: str
    sauf_si: tuple[str, ...] = ()


@dataclass(frozen=True)
class Axis:
    name: str
    default: str
    categories: tuple[Category, ...]


@dataclass(frozen=True)
class Taxonomy:
    axes: tuple[Axis, ...]
    rf_terms: tuple[str, ...]
    filtres: str = ""
    annee_min: int = 0
    title_boost: float = 2.5
    meta_boost: float = 2.0
    min_score: float = 1.0
    max_secondaires: int = 3
    exclusions: tuple[Exclusion, ...] = ()
    pertinence: tuple[str, ...] = ()


@dataclass
class Assignment:
    """Décision pour un axe : catégorie retenue, score, catégories suivantes, preuves."""

    axis: str
    category: str
    score: float
    secondaires: list[str] = field(default_factory=list)
    matched: list[str] = field(default_factory=list)


def _exclusion(entry: object) -> Exclusion:
    """Accepte ``"terme"`` ou ``{terme: …, sauf_si: [...]}`` dans la taxonomie."""
    if isinstance(entry, dict):
        return Exclusion(str(entry.get("terme", "")),
                         tuple(str(t) for t in entry.get("sauf_si", [])))
    return Exclusion(str(entry))


def load_taxonomy(path: str | Path) -> Taxonomy:
    """Lit la taxonomie YAML (axes, mots-clés, réglages de scoring)."""
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    rech = cfg.get("recherche", {}) or {}
    clas = cfg.get("classement", {}) or {}
    axes = tuple(
        Axis(
            name=str(ax["name"]),
            default=str(ax.get("default", "non_classe")),
            categories=tuple(
                Category(str(c["name"]),
                         tuple(str(k) for k in c.get("keywords", [])),
                         tuple(str(k) for k in c.get("decisifs", [])))
                for c in ax.get("categories", [])
            ),
        )
        for ax in cfg.get("axes", [])
    )
    return Taxonomy(
        axes=axes,
        rf_terms=tuple(str(t) for t in rech.get("rf_terms", [])),
        filtres=str(rech.get("filtres", "")),
        annee_min=int(rech.get("annee_min", 0) or 0),
        title_boost=float(clas.get("title_boost", 2.5)),
        meta_boost=float(clas.get("meta_boost", 2.0)),
        min_score=float(clas.get("min_score", 1.0)),
        max_secondaires=int(clas.get("max_secondaires", 3)),
        exclusions=tuple(_exclusion(e) for e in rech.get("exclusions", [])),
        pertinence=tuple(str(t) for t in rech.get("pertinence", [])),
    )


@lru_cache(maxsize=4096)
def _pattern(keyword: str) -> re.Pattern[str]:
    """Mot-clé -> regex tolérante aux tirets/espaces, bornée aux limites de mots.

    Sans bornes, « rat » se déclencherait sur « generated » et « SAR » sur « sarcoma ».
    """
    body = r"[\s\-]+".join(re.escape(part) for part in keyword.split())
    return re.compile(rf"(?<![\w-]){body}(?![\w-])", re.IGNORECASE)


def meta_text(paper_extra: dict[str, object] | None) -> str:
    """Descripteurs fournis par la source (MeSH, type de publication, mots-clés d'auteur).

    « Animals », « Rats », « In Vitro Techniques », « Review » sont des indications bien
    plus sûres que les mots du résumé : ils sont attribués par les indexeurs de PubMed.
    """
    parts: list[str] = []
    for key in ("mesh", "types", "keywords"):
        value = (paper_extra or {}).get(key) or []
        if isinstance(value, (list, tuple)):
            parts += [str(v) for v in value]
        elif value:
            parts.append(str(value))
    return " ; ".join(parts)


_DECISIF = 1000.0      # domine tout comptage de mots-clés, sans le remplacer


def _score(category: Category, title: str, abstract: str, meta: str,
           tax: Taxonomy) -> tuple[float, list[str]]:
    total, hits = 0.0, []
    # Un descripteur décisif vaut dans les MeSH **ou** dans le titre : quand les auteurs
    # écrivent « in vivo » dans leur titre, ils tranchent mieux qu'un descripteur
    # « Cell Line, Tumor » posé sur une tumeur greffée chez le rat.
    # Le bonus décisif ne compte qu'UNE fois : « Cell Line » et « Cell Line, Tumor »
    # désignent le même fait, les cumuler écraserait à tort un indice contraire.
    decisifs = [kw for kw in category.decisifs
                if any(f and _pattern(kw).search(f) for f in (meta, title))]
    if decisifs:
        total += _DECISIF
        hits += [f"{kw} (descripteur décisif)" for kw in decisifs]
    for kw in category.keywords:
        pat = _pattern(kw)
        weights = [(tax.title_boost, title), (tax.meta_boost, meta), (1.0, abstract)]
        found = [w for w, field in weights if field and pat.search(field)]
        if not found:
            continue
        total += max(found)          # une seule fois par mot-clé, au poids du champ le plus fort
        hits.append(kw)
    return total, hits


def classify_axis(axis: Axis, title: str, abstract: str, tax: Taxonomy,
                  meta: str = "") -> Assignment:
    """Classe un texte sur un axe ; renvoie aussi les catégories suivantes et les preuves."""
    scored = [(c, *_score(c, title, abstract, meta, tax)) for c in axis.categories]
    ranked = sorted(
        ((c, s, h) for c, s, h in scored if s >= tax.min_score),
        key=lambda t: (-t[1], axis.categories.index(t[0])),
    )
    if not ranked:
        return Assignment(axis.name, axis.default, 0.0)
    best, score, hits = ranked[0]
    return Assignment(
        axis=axis.name,
        category=best.name,
        score=round(score, 2),
        secondaires=[c.name for c, _, _ in ranked[1:1 + tax.max_secondaires]],
        matched=hits,
    )


def classify(title: str, abstract: str, tax: Taxonomy,
             meta: str = "") -> dict[str, Assignment]:
    """Classe un article sur tous les axes : {nom d'axe: décision}."""
    return {ax.name: classify_axis(ax, title or "", abstract or "", tax, meta)
            for ax in tax.axes}


def classify_paper(paper, tax: Taxonomy) -> dict[str, Assignment]:
    """Classe un ``Paper`` en exploitant aussi ses descripteurs MeSH."""
    return classify(paper.title, paper.abstract, tax, meta_text(getattr(paper, "extra", {})))


def is_off_topic(paper, tax: Taxonomy) -> str:
    """Motif d'exclusion du corpus, ou chaîne vide.

    Deux garde-fous, appris sur des notices réelles :

    * **exclusions** — « specific absorption rate » ramène de la méthodologie IRM, sans
      rapport avec l'exposition environnementale ;
    * **pertinence** — une requête trop large ramène du hors-sujet complet (l'abréviation
      « GSM » désigne aussi la *géosmine* en traitement de l'eau). On exige donc qu'un
      terme d'exposition RF figure réellement dans la notice.

    Mieux vaut écarter en le disant que ranger de force dans une catégorie.
    """
    meta = meta_text(getattr(paper, "extra", {}))
    titre_meta = f"{paper.title} {meta}"
    corpus = f"{titre_meta} {paper.abstract}"
    for excl in tax.exclusions:
        if not _pattern(excl.terme).search(titre_meta):
            continue
        # Une étude d'exposition qui se sert de l'IRM comme outil de mesure n'est pas un
        # article de méthodologie IRM : ses marques propres annulent cette exclusion-là.
        if any(_pattern(t).search(corpus) for t in excl.sauf_si):
            continue
        return excl.terme
    terms = tax.pertinence or tax.rf_terms
    if terms and not any(_pattern(t).search(corpus) for t in terms):
        return "aucun terme d'exposition RF"
    return ""


def build_query(tax: Taxonomy, extra: str = "") -> str:
    """Requête Europe PMC du corpus RF (termes de la taxonomie + filtres)."""
    rf = " OR ".join(f'"{t}"' for t in tax.rf_terms)
    parts = [f"({rf})"]
    if tax.annee_min:
        parts.append(f"(FIRST_PDATE:[{tax.annee_min}-01-01 TO 3000-12-31])")
    if tax.filtres:
        parts.append(f"({tax.filtres})")
    if extra:
        parts.append(f"({extra})")
    return " AND ".join(parts)
