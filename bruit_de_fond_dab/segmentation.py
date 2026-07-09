"""Segmentation -> masque FIDÈLE (base commune aux deux modes de sortie).

Le masque d'analyse est délibérément FIDÈLE : seuillage sur la carte de
prominence DAB (densité à fond local soustrait) puis retrait des micro-débris.
AUCUNE fermeture ni lissage cosmétique — les prolongements et les gaps
authentiques sont préservés pour le Sholl / YOLO en aval.

Le rendu FIGURE (embellissement) est fait séparément dans rendering.py à partir
de ce même masque.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from skimage.measure import label
from skimage.filters import apply_hysteresis_threshold

from .calibration import CalibrationResult
from .morph_compat import remove_small_objects, remove_small_holes


@dataclass
class SegmentationResult:
    """Résultat de segmentation partagé par les deux modes."""

    analysis_mask: np.ndarray   # bool (H, W) — masque fidèle
    signal_map: np.ndarray      # float (H, W) — prominence DAB (fond soustrait)
    threshold: float
    n_objects: int


def segment_astrocytes(
    signal_map: np.ndarray,
    calib: CalibrationResult,
) -> SegmentationResult:
    """Construit le masque d'analyse fidèle à partir de la carte calibrée."""
    # Seuillage par HYSTÉRÉSIS : les germes (>= seuil haut) sont des astrocytes
    # certains ; on les fait croître dans les pixels >= seuil bas UNIQUEMENT
    # s'ils y sont connectés. -> prolongements fins complets, et neuropile faible
    # isolé (sans germe) rejeté = fond propre. Reste FIDÈLE (aucune morphologie
    # cosmétique) : préserve les gaps authentiques pour le Sholl.
    if calib.threshold_low < calib.threshold:
        raw = apply_hysteresis_threshold(
            signal_map, calib.threshold_low, calib.threshold
        )
    else:  # cas dégénéré -> seuil unique
        raw = signal_map >= calib.threshold

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
        signal_map=signal_map,
        threshold=calib.threshold,
        n_objects=n,
    )
