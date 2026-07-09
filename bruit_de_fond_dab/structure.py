"""Détection de STRUCTURE (morphologie), pas d'intensité.

Un astrocyte se reconnaît à sa forme : un soma compact d'où rayonnent des
prolongements fins, allongés et ramifiés. Le bruit de fond (neuropile, halo brun
diffus, flou hors-plan) n'a pas cette structure filamenteuse cohérente.

On utilise donc un filtre de Hessienne multi-échelle (Sato / « tubeness »,
famille des filtres de traçage de neurites) qui répond fortement aux structures
tubulaires fines et FAIBLEMENT aux zones diffuses — quel que soit leur niveau de
brun. C'est un détecteur de FORME, indépendant d'un simple seuil de contraste.

Deux réponses complémentaires sont combinées :
    - `tubeness`  : prolongements fins et ramifiés (Sato multi-échelle) ;
    - `blobness`  : somas compacts (réponse de Hessienne à petite échelle).

Le fond diffus, n'étant ni tubulaire ni compact, est éliminé par construction.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.filters import sato
from skimage.feature import peak_local_max
from skimage.morphology import opening, dilation, disk

EPS = 1e-6


def auto_soma_radius(h: int, w: int) -> int:
    """Rayon typique d'un soma (px), dérivé de la taille de l'image."""
    return int(np.clip(round(0.009 * min(h, w)), 3, 18))


def detect_somata(dab: np.ndarray, soma_radius: int,
                  sensitivity: float = 1.0) -> np.ndarray:
    """Détecte les CORPS CELLULAIRES (blobs compacts denses).

    Étape clé : une ouverture morphologique par un disque de rayon `soma_radius`
    n'a de réponse QUE là où le disque « rentre » — c.-à-d. sur des blobs
    compacts (somas). Les structures fines (prolongements, fibres de fond) sont
    effacées : elles ne produisent aucun soma. C'est le marqueur qui distingue
    l'astrocyte du fond fibreux.

    On repère ensuite les somas comme des MAXIMA LOCAUX de la carte d'ouverture
    (un germe par corps cellulaire), au lieu d'un seuil global : la détection
    s'adapte au contraste propre de chaque cellule -> bien meilleur rappel sur
    les somas peu marqués, sans faire remonter les fibres (dont l'ouverture reste
    quasi nulle).
    """
    opened = opening(dab, disk(soma_radius))
    pos = opened[opened > EPS]
    if pos.size < 32 or np.ptp(pos) < EPS:
        return np.zeros(dab.shape, dtype=bool)
    # seuil de bruit robuste sur la carte d'ouverture (fibres ~ 0)
    med = float(np.median(opened))
    mad = float(np.median(np.abs(opened - med))) + EPS
    thr = (med + 2.0 * 1.4826 * mad) / max(sensitivity, EPS)
    thr = max(thr, float(np.percentile(pos, 50)) * 0.5)
    coords = peak_local_max(
        opened, min_distance=max(2, soma_radius),
        threshold_abs=thr, exclude_border=False,
    )
    seeds = np.zeros(dab.shape, dtype=bool)
    if coords.size:
        seeds[tuple(coords.T)] = True
        # petits disques -> recouvrent la structure de façon fiable
        seeds = dilation(seeds, disk(max(2, soma_radius // 2)))
    return seeds


def auto_scales(h: int, w: int) -> np.ndarray:
    """Échelles (largeurs de prolongement, en px) dérivées de la taille image."""
    kmax = int(np.clip(round(0.006 * min(h, w)), 3, 10))
    return np.arange(1, kmax + 1, dtype=np.float64)


def tubeness(dab: np.ndarray, scales: np.ndarray) -> np.ndarray:
    """Réponse tubulaire multi-échelle (prolongements fins) sur la densité DAB.

    `black_ridges=False` : on cherche des crêtes CLAIRES (forte densité DAB) sur
    un fond sombre. La réponse est indépendante de l'intensité absolue : un
    prolongement fin peu contrasté ressort autant qu'un prolongement dense.
    """
    resp = sato(dab.astype(np.float64), sigmas=scales, black_ridges=False)
    resp = np.nan_to_num(resp, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(resp, 0.0, None).astype(np.float32)


def structureness(dab: np.ndarray, scales: np.ndarray) -> np.ndarray:
    """Carte de STRUCTURE combinée (prolongements + somas), normalisée [0,1].

    - tubeness multi-échelle -> prolongements et branches ;
    - une petite composante « soma » : lissage local de la densité aux petites
      échelles, qui renforce les corps cellulaires compacts sans réintroduire le
      fond diffus (celui-ci reste basse amplitude après normalisation robuste).
    """
    tube = tubeness(dab, scales)
    tube /= (np.percentile(tube, 99.5) + EPS)

    # renfort soma : réponse tubulaire aux plus grandes échelles (corps compacts)
    soma_scales = scales[scales >= max(2.0, scales.mean())]
    if soma_scales.size:
        soma = tubeness(gaussian_filter(dab, 1.0), soma_scales)
        soma /= (np.percentile(soma, 99.5) + EPS)
    else:
        soma = np.zeros_like(tube)

    struct = np.maximum(tube, 0.85 * soma)
    return np.clip(struct, 0.0, 1.0).astype(np.float32)
