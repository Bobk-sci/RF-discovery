"""Enveloppes morphologiques tolérantes aux versions de scikit-image.

skimage 0.26 a renommé certains paramètres (`min_size`/`area_threshold` ->
`max_size`) et déprécié `binary_closing`/`binary_opening`. Ces enveloppes
préservent la sémantique historique quelle que soit la version installée.
"""
from __future__ import annotations

import numpy as np
from skimage import morphology as _m


def remove_small_objects(mask: np.ndarray, min_size: int) -> np.ndarray:
    """Supprime les objets d'aire < min_size (conserve aire >= min_size)."""
    try:  # skimage >= 0.26 : max_size retire les aires <= max_size
        return _m.remove_small_objects(mask, max_size=int(min_size) - 1)
    except TypeError:  # skimage < 0.26
        return _m.remove_small_objects(mask, min_size=int(min_size))


def remove_small_holes(mask: np.ndarray, area_threshold: int) -> np.ndarray:
    """Bouche les trous d'aire <= area_threshold."""
    try:
        return _m.remove_small_holes(mask, max_size=int(area_threshold))
    except TypeError:
        return _m.remove_small_holes(mask, area_threshold=int(area_threshold))


def binary_closing(mask: np.ndarray, footprint) -> np.ndarray:
    return _m.closing(mask, footprint)
