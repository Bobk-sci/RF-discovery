"""Segmentation -> masque FIDÈLE (base commune aux deux modes de sortie).

Le masque d'analyse est délibérément FIDÈLE : seuillage sur la carte DAB puis
retrait des micro-débris sous le plancher de bruit. AUCUNE fermeture ni lissage
cosmétique — les prolongements et les gaps authentiques sont préservés pour le
Sholl / YOLO en aval.

Le rendu FIGURE (embellissement) est fait séparément dans rendering.py à partir
de ce même masque.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from skimage.measure import label

from .calibration import CalibrationResult
from .morph_compat import remove_small_objects, remove_small_holes


@dataclass
class SegmentationResult:
    """Résultat de segmentation partagé par les deux modes."""

    analysis_mask: np.ndarray   # bool (H, W) — masque fidèle
    dab_map: np.ndarray         # float (H, W) — densité DAB
    threshold: float
    n_objects: int


def segment_astrocytes(
    dab_map: np.ndarray,
    calib: CalibrationResult,
) -> SegmentationResult:
    """Construit le masque d'analyse fidèle à partir de la carte DAB calibrée."""
    # Seuillage au seuil auto-estimé (le plus exigeant Otsu / MAD).
    raw = dab_map >= calib.threshold

    # Nettoyage MINIMAL : uniquement les micro-débris épars sous la taille
    # minimale dérivée de l'aire. Pas de fermeture, pas de dilatation.
    cleaned = remove_small_objects(raw, min_size=calib.min_object_size)

    # Bouche seulement les trous minuscules (bruit de seuillage interne au soma),
    # sans modifier le contour ni relier des prolongements séparés.
    hole_area = max(4, calib.min_object_size // 4)
    cleaned = remove_small_holes(cleaned, area_threshold=hole_area)

    n = int(label(cleaned).max())
    return SegmentationResult(
        analysis_mask=cleaned,
        dab_map=dab_map,
        threshold=calib.threshold,
        n_objects=n,
    )
