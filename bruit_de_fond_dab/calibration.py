"""Auto-calibrage PAR IMAGE.

Chaque image estime, à partir de ses propres statistiques :
    - son point blanc I0 (percentile haut de luminosité = illumination de fond) ;
    - une carte de densité DAB (déconvolution de couleur sur image normalisée
      au point blanc, c.-à-d. en densité optique) ;
    - une échelle d'OD robuste (percentile haut de la carte DAB) ;
    - ses seuils (Otsu sur la carte DAB + plancher robuste médiane + k·MAD) ;
    - une taille minimale d'objet dérivée de l'aire de l'image.

La LOGIQUE est identique d'une image à l'autre — seules les valeurs numériques
s'adaptent. Toutes les valeurs sont retournées pour être journalisées.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Dict

import numpy as np
from skimage.color import rgb2hed
from skimage.filters import threshold_otsu

# Paramètres de la LOGIQUE (identiques pour toutes les images ; non réglés
# image par image). Seules les VALEURS estimées ci-dessous s'adaptent.
WHITE_PERCENTILE = 99.0        # point blanc = percentile haut de luminosité
DAB_SCALE_PERCENTILE = 99.5    # échelle d'OD = percentile haut de la carte DAB
MAD_K = 3.0                    # plancher robuste : médiane + k·MAD (fond)
MIN_SIZE_AREA_FRAC = 6e-5      # taille min d'objet = frac. de l'aire image
MIN_SIZE_FLOOR = 24            # taille min d'objet, plancher absolu (px)
EPS = 1e-6


@dataclass
class CalibrationResult:
    """Valeurs auto-estimées pour une image (journalisées telles quelles)."""

    height: int
    width: int
    # point blanc par canal + luminance
    white_point_rgb: tuple
    white_luminance: float
    # densité DAB
    dab_scale: float               # échelle d'OD (normalisation d'affichage)
    dab_median: float
    dab_mad: float
    dab_p99: float
    # seuils candidats et seuil retenu
    threshold_otsu: float
    threshold_mad: float
    threshold: float
    threshold_source: str          # "otsu", "mad" (celui qui domine)
    # nettoyage
    min_object_size: int

    def to_log_dict(self) -> Dict:
        d = asdict(self)
        d["white_point_rgb"] = [round(float(v), 5) for v in self.white_point_rgb]
        for k, v in d.items():
            if isinstance(v, float):
                d[k] = round(v, 6)
        return d


def dab_density_map(rgb: np.ndarray, white_point_rgb: np.ndarray) -> np.ndarray:
    """Carte de densité DAB à partir d'une image normalisée au point blanc.

    On divise par le point blanc (fond -> ~1, donc OD -> 0), puis on applique la
    déconvolution H-E-DAB de skimage. Le canal DAB est renvoyé (absorbance,
    croissant avec la quantité de marquage brun).
    """
    norm = rgb / np.maximum(white_point_rgb[None, None, :], EPS)
    norm = np.clip(norm, EPS, 1.0).astype(np.float32)
    hed = rgb2hed(norm)
    dab = hed[..., 2]
    # recale le zéro sur le mode du fond (percentile bas) pour que le fond ~ 0
    baseline = np.percentile(dab, 10.0)
    dab = np.maximum(dab - baseline, 0.0)
    return dab.astype(np.float32)


def calibrate_image(rgb: np.ndarray) -> tuple[CalibrationResult, np.ndarray]:
    """Estime toutes les valeurs de calibrage d'une image.

    Retourne (CalibrationResult, carte_DAB). La carte DAB est réutilisée par la
    segmentation pour éviter de la recalculer.
    """
    h, w = rgb.shape[:2]

    # --- Point blanc : percentile haut par canal (illumination de fond) -------
    white_rgb = np.percentile(
        rgb.reshape(-1, 3), WHITE_PERCENTILE, axis=0
    ).astype(np.float32)
    white_rgb = np.maximum(white_rgb, EPS)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    white_lum = float(np.percentile(lum, WHITE_PERCENTILE))

    # --- Carte de densité DAB (en OD, normalisée au point blanc) --------------
    dab = dab_density_map(rgb, white_rgb)

    # --- Statistiques robustes de la carte DAB --------------------------------
    dab_median = float(np.median(dab))
    dab_mad = float(np.median(np.abs(dab - dab_median))) + EPS
    dab_p99 = float(np.percentile(dab, 99.0))
    dab_scale = float(np.percentile(dab, DAB_SCALE_PERCENTILE)) + EPS

    # --- Seuils candidats -----------------------------------------------------
    # Otsu sur la carte DAB (sépare signal / fond sur cette image)
    try:
        t_otsu = float(threshold_otsu(dab))
    except (ValueError, RuntimeError):
        t_otsu = dab_median + MAD_K * dab_mad
    # Plancher robuste : le fond est modélisé par (médiane, MAD)
    t_mad = dab_median + MAD_K * 1.4826 * dab_mad

    # Le seuil retenu ne descend jamais sous le plancher de bruit robuste :
    # on garde le plus exigeant des deux -> zéro résidu de neuropile.
    if t_otsu >= t_mad:
        threshold, source = t_otsu, "otsu"
    else:
        threshold, source = t_mad, "mad"

    # --- Taille minimale d'objet (dérivée de l'aire) --------------------------
    min_size = max(MIN_SIZE_FLOOR, int(round(MIN_SIZE_AREA_FRAC * h * w)))

    result = CalibrationResult(
        height=h,
        width=w,
        white_point_rgb=tuple(float(v) for v in white_rgb),
        white_luminance=white_lum,
        dab_scale=dab_scale,
        dab_median=dab_median,
        dab_mad=dab_mad,
        dab_p99=dab_p99,
        threshold_otsu=t_otsu,
        threshold_mad=t_mad,
        threshold=threshold,
        threshold_source=source,
        min_object_size=min_size,
    )
    return result, dab
