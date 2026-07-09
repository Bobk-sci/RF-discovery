"""MODE FIGURE : rendu esthétique (embellissement) — livrable de publication.

Part du MÊME masque de segmentation que le mode analyse, mais applique :
    - une fermeture morphologique douce (reconnecte les prolongements) ;
    - un retrait des micro-débris et des spurs (fragments épars, poils 1 px) ;
    - un feathering du canal ALPHA uniquement (anti-aliasing des bords) ;
    - un léger rehaussement de contraste LOCAL, sur le signal conservé seulement.

Le masque final est appliqué sur l'image ORIGINALE : on conserve le brun DAB et
la texture interne des astrocytes (la sortie n'est PAS un masque binaire).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.morphology import disk
from skimage.exposure import equalize_adapthist

from .calibration import CalibrationResult
from .morph_compat import binary_closing, remove_small_objects

WHITE = np.array([1.0, 1.0, 1.0], dtype=np.float32)


@dataclass
class FigureRender:
    """Sorties du mode figure + paramètres d'embellissement (journalisables)."""

    rgba_transparent: np.ndarray   # float (H, W, 4) — fond transparent
    rgb_white: np.ndarray          # float (H, W, 3) — fond blanc pur
    figure_mask: np.ndarray        # bool (H, W) — masque après embellissement
    alpha: np.ndarray              # float (H, W) — alpha feathering [0,1]
    close_radius: int
    feather_sigma: float
    local_contrast: bool


def _auto_close_radius(calib: CalibrationResult) -> int:
    """Rayon de fermeture doux, dérivé de l'échelle de l'image."""
    scale = 0.5 * (calib.height + calib.width)
    return int(np.clip(round(0.0015 * scale), 1, 4))


def render_figure(
    rgb: np.ndarray,
    analysis_mask: np.ndarray,
    calib: CalibrationResult,
    close_radius: Optional[int] = None,
    feather_sigma: float = 1.0,
    local_contrast: bool = True,
) -> FigureRender:
    """Produit les rendus figure (transparent + fond blanc) à partir du masque."""
    if close_radius is None:
        close_radius = _auto_close_radius(calib)

    # --- Embellissement du masque --------------------------------------------
    # Fermeture douce : reconnecte les prolongements fragmentés / gaps.
    # C'est une opération ADDITIVE : le rendu figure est un SUR-ensemble du
    # masque fidèle -> l'embellissement ne peut jamais amputer de structure
    # (invariant vérifiable dans le panneau QC).
    fig_mask = binary_closing(analysis_mask, disk(close_radius))
    # Suppression des spurs / micro-débris épars : filtre par TAILLE, qui retire
    # les fragments isolés sans éroder les prolongements fins des astrocytes.
    fig_mask = remove_small_objects(fig_mask, min_size=calib.min_object_size)
    # On garantit le sur-ensemble même si un débris jouxtait un astrocyte.
    fig_mask = fig_mask | analysis_mask

    # --- Signal : image originale (+ rehaussement local optionnel) ------------
    signal_rgb = rgb.astype(np.float32)
    if local_contrast:
        signal_rgb = _local_contrast_on_signal(signal_rgb, fig_mask)

    # --- Feathering du canal ALPHA UNIQUEMENT ---------------------------------
    # Léger flou (~feather_sigma px) sur l'alpha seul -> bords adoucis,
    # non en escalier ; les pixels du signal ne sont jamais floutés.
    alpha_hard = fig_mask.astype(np.float32)
    alpha = gaussian_filter(alpha_hard, sigma=feather_sigma)
    alpha = np.clip(alpha, 0.0, 1.0)
    # On borne l'alpha au cœur du masque à 1 pour ne pas ternir le signal plein.
    alpha = np.maximum(alpha, alpha_hard)

    # --- Composition ----------------------------------------------------------
    rgba_transparent = np.dstack([signal_rgb, alpha]).astype(np.float32)

    a = alpha[..., None]
    rgb_white = (signal_rgb * a + WHITE[None, None, :] * (1.0 - a)).astype(np.float32)

    return FigureRender(
        rgba_transparent=rgba_transparent,
        rgb_white=rgb_white,
        figure_mask=fig_mask,
        alpha=alpha,
        close_radius=int(close_radius),
        feather_sigma=float(feather_sigma),
        local_contrast=bool(local_contrast),
    )


def _local_contrast_on_signal(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """CLAHE léger appliqué UNIQUEMENT dans la région du signal.

    Le fond n'est jamais touché : on ne recompose le résultat CLAHE que là où le
    masque est vrai, pour faire ressortir les prolongements fins sans salir le
    fond.
    """
    if not mask.any():
        return rgb
    enhanced = equalize_adapthist(np.clip(rgb, 0, 1), clip_limit=0.01)
    enhanced = enhanced.astype(np.float32)
    out = rgb.copy()
    m = mask[..., None]
    out = np.where(m, enhanced, out)
    return out.astype(np.float32)
