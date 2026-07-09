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

EPS = 1e-6


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
