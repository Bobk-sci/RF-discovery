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
from skimage.filters import threshold_otsu, threshold_multiotsu

from .structure import auto_scales, structureness

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
    # fond local (soustraction optionnelle du halo diffus avant détection forme)
    background_sigma: float
    # détection de STRUCTURE (tubeness) : plus grande échelle de prolongement
    ridge_scale_max: float
    # statistiques de la carte de prominence (signal seuillé)
    signal_scale: float            # échelle d'affichage (normalisation)
    signal_median: float
    signal_mad: float
    signal_p99: float
    # seuils candidats et seuil retenu
    threshold_otsu: float
    threshold_mad: float
    threshold: float               # seuil HAUT (germes = astrocyte certain)
    threshold_low: float           # seuil BAS (croissance par hystérésis)
    threshold_source: str          # "multiotsu" (3 classes) ou "otsu" (repli)
    sensitivity: float             # facteur utilisateur appliqué aux seuils
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
    sensitivity: float = 1.0,
) -> tuple[CalibrationResult, np.ndarray, np.ndarray]:
    """Estime toutes les valeurs de calibrage d'une image.

    Retourne (CalibrationResult, carte_de_structure, densité_DAB). La carte de
    structure (tubeness) est celle qui sera seuillée ; la densité DAB est
    réutilisée par la segmentation pour ancrer les astrocytes sur leurs somas.
    """
    h, w = rgb.shape[:2]

    # --- Point blanc : percentile haut par canal (illumination de fond) -------
    white_rgb = np.percentile(
        rgb.reshape(-1, 3), WHITE_PERCENTILE, axis=0
    ).astype(np.float32)
    white_rgb = np.maximum(white_rgb, EPS)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    white_lum = float(np.percentile(lum, WHITE_PERCENTILE))

    # --- Densité DAB (OD) -----------------------------------------------------
    dab = dab_density_map(rgb, white_rgb)
    # Soustraction OPTIONNELLE du halo diffus (utile si le fond est très marqué) ;
    # par défaut on ne s'appuie pas sur l'intensité mais sur la structure.
    if background_sigma is not None and background_sigma > 0:
        dab = local_prominence(dab, background_sigma)
    else:
        background_sigma = 0.0

    # --- Carte de STRUCTURE (morphologie, pas intensité) ----------------------
    # Filtre tubulaire multi-échelle : ne répond qu'aux prolongements fins et aux
    # somas compacts des astrocytes ; le fond diffus est éliminé par construction.
    scales = auto_scales(h, w)
    signal = structureness(dab, scales)

    # --- Statistiques robustes de la carte de prominence ----------------------
    sig_median = float(np.median(signal))
    sig_mad = float(np.median(np.abs(signal - sig_median))) + EPS
    sig_p99 = float(np.percentile(signal, 99.0))
    sig_scale = float(np.percentile(signal, SCALE_PERCENTILE)) + EPS

    # --- Seuils candidats -----------------------------------------------------
    # On seuille sur les pixels non nuls : la prominence est majoritairement
    # nulle (fond aplati) ; inclure ce pic de zéros écrase les seuils vers 0.
    positive = signal[signal > EPS]
    # Plancher robuste : le fond (prominence ~0) est modélisé par (médiane, MAD).
    t_mad = sig_median + MAD_K * 1.4826 * sig_mad
    t_otsu = t_mad  # valeur de repli

    # Seuillage SÉLECTIF à 3 classes (multi-Otsu) : fond / neuropile faible /
    # astrocyte sombre. On retient la borne HAUTE (t2) -> ne garde que la classe
    # la plus dense (astrocytes), en rejetant le maillage de neuropile. C'est le
    # discriminant clé : astrocytes et neuropile ont la même finesse mais des
    # DENSITÉS différentes. Repli sur Otsu 2 classes si multi-Otsu échoue.
    source = "multiotsu"
    t2 = t1 = None
    if positive.size >= 256 and np.ptp(positive) > EPS:
        try:
            ts = threshold_multiotsu(positive, classes=3)
            t1, t2 = float(ts[0]), float(ts[1])
        except (ValueError, RuntimeError):
            t1 = t2 = None
    if t2 is None:  # repli Otsu 2 classes
        try:
            t2 = float(threshold_otsu(positive)) if positive.size >= 64 else t_mad
        except (ValueError, RuntimeError):
            t2 = t_mad
        t1 = 0.5 * t2
        source = "otsu"
    t_otsu = t2

    # Seuil HAUT = borne astrocyte, jamais sous le plancher de bruit.
    threshold = max(t2, t_mad)
    # Seuil BAS (hystérésis) : croissance des germes vers les prolongements fins,
    # entre le neuropile (t1) et l'astrocyte (t2) -> complète les astrocytes sans
    # envahir le maillage faible.
    t_low = max(t_mad, 0.5 * (t1 + t2))
    t_low = min(t_low, threshold)

    # Sensibilité (auto=1.0). >1 : plus sélectif (astrocytes plus nets, moins de
    # maillage) ; <1 : plus permissif. Règle utilisateur, appliquée aux 2 seuils.
    threshold *= sensitivity
    t_low = min(t_low * sensitivity, threshold)

    # --- Taille minimale d'objet (dérivée de l'aire) --------------------------
    min_size = max(MIN_SIZE_FLOOR, int(round(MIN_SIZE_AREA_FRAC * h * w)))

    result = CalibrationResult(
        height=h,
        width=w,
        white_point_rgb=tuple(float(v) for v in white_rgb),
        white_luminance=white_lum,
        background_sigma=float(background_sigma),
        ridge_scale_max=float(scales.max()),
        signal_scale=sig_scale,
        signal_median=sig_median,
        signal_mad=sig_mad,
        signal_p99=sig_p99,
        threshold_otsu=t_otsu,
        threshold_mad=t_mad,
        threshold=threshold,
        threshold_low=t_low,
        threshold_source=source,
        sensitivity=float(sensitivity),
        min_object_size=min_size,
    )
    return result, signal, dab
