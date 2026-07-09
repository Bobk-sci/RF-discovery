"""Auto-calibrage PAR IMAGE.

Chaque image estime, à partir de ses propres statistiques :
    - son point blanc I0 (percentile haut de luminosité = illumination de fond) ;
    - une carte de densité DAB (déconvolution de couleur sur image normalisée
      au point blanc, c.-à-d. en densité optique) ;
    - une carte de PROMINENCE = densité DAB moins son fond local (passe-haut
      gaussien). Le neuropile diffus est basse fréquence -> soustrait ~0 ; les
      somas compacts et les prolongements fins survivent. C'est cette carte, à
      fond aplati, qui est seuillée -> le seuillage reste robuste même quand le
      neuropile est lui-même fortement marqué ;
    - une échelle d'affichage robuste (percentile haut de la prominence) ;
    - ses seuils (Otsu sur la prominence + plancher robuste médiane + k·MAD) ;
    - une taille minimale d'objet dérivée de l'aire de l'image.

La LOGIQUE est identique d'une image à l'autre — seules les valeurs numériques
s'adaptent (le sigma du fond local est dérivé de la taille de l'image). Toutes
les valeurs sont retournées pour être journalisées.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional

import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.color import rgb2hed
from skimage.filters import threshold_otsu

# Paramètres de la LOGIQUE (identiques pour toutes les images ; non réglés
# image par image). Seules les VALEURS estimées ci-dessous s'adaptent.
WHITE_PERCENTILE = 99.0        # point blanc = percentile haut de luminosité
SCALE_PERCENTILE = 99.5        # échelle d'affichage = percentile haut prominence
MAD_K = 3.0                    # plancher robuste : médiane + k·MAD (fond)
MIN_SIZE_AREA_FRAC = 6e-5      # taille min d'objet = frac. de l'aire image
MIN_SIZE_FLOOR = 24            # taille min d'objet, plancher absolu (px)
# Fond local : sigma du passe-haut, dérivé de la taille de l'image.
# Doit être >> largeur des prolongements et >~ taille des somas, mais assez
# petit pour capturer le neuropile diffus comme "fond local".
BG_SIGMA_FRAC = 0.025
BG_SIGMA_MIN = 12.0
BG_SIGMA_MAX = 40.0
EPS = 1e-6


@dataclass
class CalibrationResult:
    """Valeurs auto-estimées pour une image (journalisées telles quelles)."""

    height: int
    width: int
    # point blanc par canal + luminance
    white_point_rgb: tuple
    white_luminance: float
    # fond local (soustraction du neuropile diffus)
    background_sigma: float
    # statistiques de la carte de prominence (signal seuillé)
    signal_scale: float            # échelle d'affichage (normalisation)
    signal_median: float
    signal_mad: float
    signal_p99: float
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


def local_prominence(dab: np.ndarray, sigma: float) -> np.ndarray:
    """Densité DAB moins son fond local (passe-haut gaussien), rectifiée >= 0.

    Supprime le neuropile diffus (basse fréquence) tout en conservant les
    structures compactes (somas) et fines (prolongements) des astrocytes.
    """
    background = gaussian_filter(dab, sigma=sigma, mode="reflect")
    prom = np.clip(dab - background, 0.0, None)
    return prom.astype(np.float32)


def _auto_background_sigma(h: int, w: int) -> float:
    return float(np.clip(BG_SIGMA_FRAC * min(h, w), BG_SIGMA_MIN, BG_SIGMA_MAX))


def calibrate_image(
    rgb: np.ndarray,
    background_sigma: Optional[float] = None,
) -> tuple[CalibrationResult, np.ndarray]:
    """Estime toutes les valeurs de calibrage d'une image.

    Retourne (CalibrationResult, carte_de_prominence). La carte de prominence
    (densité DAB à fond local soustrait) est celle qui sera seuillée par la
    segmentation ; elle est réutilisée pour éviter de la recalculer.
    """
    h, w = rgb.shape[:2]

    # --- Point blanc : percentile haut par canal (illumination de fond) -------
    white_rgb = np.percentile(
        rgb.reshape(-1, 3), WHITE_PERCENTILE, axis=0
    ).astype(np.float32)
    white_rgb = np.maximum(white_rgb, EPS)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    white_lum = float(np.percentile(lum, WHITE_PERCENTILE))

    # --- Densité DAB (OD) puis PROMINENCE (fond diffus soustrait) -------------
    dab = dab_density_map(rgb, white_rgb)
    if background_sigma is None:
        background_sigma = _auto_background_sigma(h, w)
    signal = local_prominence(dab, background_sigma)

    # --- Statistiques robustes de la carte de prominence ----------------------
    sig_median = float(np.median(signal))
    sig_mad = float(np.median(np.abs(signal - sig_median))) + EPS
    sig_p99 = float(np.percentile(signal, 99.0))
    sig_scale = float(np.percentile(signal, SCALE_PERCENTILE)) + EPS

    # --- Seuils candidats -----------------------------------------------------
    # Otsu, calculé sur les pixels non nuls : la prominence est majoritairement
    # nulle (fond aplati) ; inclure ce pic de zéros écrase Otsu vers 0. On
    # cherche donc la vallée signal/fond parmi les pixels porteurs de structure.
    positive = signal[signal > EPS]
    try:
        if positive.size >= 64 and np.ptp(positive) > EPS:
            t_otsu = float(threshold_otsu(positive))
        else:
            t_otsu = sig_median + MAD_K * 1.4826 * sig_mad
    except (ValueError, RuntimeError):
        t_otsu = sig_median + MAD_K * 1.4826 * sig_mad
    # Plancher robuste : le fond (prominence ~0) est modélisé par (médiane, MAD).
    t_mad = sig_median + MAD_K * 1.4826 * sig_mad

    # Seuil retenu : le plus exigeant des deux -> zéro résidu de neuropile.
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
        background_sigma=float(background_sigma),
        signal_scale=sig_scale,
        signal_median=sig_median,
        signal_mad=sig_mad,
        signal_p99=sig_p99,
        threshold_otsu=t_otsu,
        threshold_mad=t_mad,
        threshold=threshold,
        threshold_source=source,
        min_object_size=min_size,
    )
    return result, signal
