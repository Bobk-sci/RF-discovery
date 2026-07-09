"""Panneau de contrôle qualité (QC).

Montage d'un coup d'œil comprenant, notamment :
    (1) image originale ;
    (2) carte de densité DAB (OD) normalisée à l'échelle auto-estimée ;
    (3) seuil auto (Otsu / MAD) sur la carte DAB ;
    (4) masque ANALYSE fidèle (contour sur l'original) ;
    (5) masque FIGURE embelli (contour sur l'original) ;
    (6) rendu FIGURE sur fond blanc ;
    (7) rendu FIGURE transparent (sur damier pour visualiser l'alpha).

Les panneaux (6) et (7) sont placés à côté du masque fidèle pour vérifier que
l'embellissement n'a ni amputé ni inventé de structure.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.segmentation import find_boundaries

from .calibration import CalibrationResult
from .segmentation import SegmentationResult
from .rendering import FigureRender

PANEL = 320          # côté d'une vignette (px)
LABEL_H = 22         # hauteur de la barre de titre
PAD = 6
COLS = 4
BG = (245, 245, 247)


def _fit(img: np.ndarray) -> Image.Image:
    """Redimensionne un panneau RGB float en vignette PANEL x PANEL."""
    arr = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    pil = Image.fromarray(arr, mode="RGB")
    pil.thumbnail((PANEL, PANEL), Image.LANCZOS)
    canvas = Image.new("RGB", (PANEL, PANEL), BG)
    ox = (PANEL - pil.width) // 2
    oy = (PANEL - pil.height) // 2
    canvas.paste(pil, (ox, oy))
    return canvas


def _heat(gray: np.ndarray) -> np.ndarray:
    """Pseudo-colormap (magma-like) pour une carte scalaire [0,1]."""
    g = np.clip(gray, 0, 1)
    r = np.clip(1.6 * g - 0.2, 0, 1)
    gr = np.clip(1.4 * g - 0.4, 0, 1)
    b = np.clip(0.9 * (1 - np.abs(g - 0.35) * 2.0), 0, 1) * 0.7 + 0.3 * g
    return np.dstack([r, gr, b]).astype(np.float32)


def _overlay_boundary(rgb: np.ndarray, mask: np.ndarray,
                      color: Tuple[float, float, float]) -> np.ndarray:
    out = rgb.copy()
    if mask.any():
        b = find_boundaries(mask, mode="outer")
        out[b] = np.array(color, dtype=np.float32)
    return out


def _checkerboard(h: int, w: int, size: int = 12) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    check = ((yy // size) + (xx // size)) % 2
    light = np.float32(0.85)
    dark = np.float32(0.65)
    base = np.where(check == 0, light, dark).astype(np.float32)
    return np.dstack([base, base, base])


def _composite_over_checker(rgba: np.ndarray) -> np.ndarray:
    h, w = rgba.shape[:2]
    checker = _checkerboard(h, w)
    a = rgba[..., 3:4]
    return (rgba[..., :3] * a + checker * (1 - a)).astype(np.float32)


def build_qc_panel(
    rgb: np.ndarray,
    calib: CalibrationResult,
    seg: SegmentationResult,
    fig: FigureRender,
) -> Image.Image:
    """Assemble le montage QC (retourne une image PIL RGB)."""
    sig_norm = np.clip(seg.signal_map / max(calib.signal_scale, 1e-6), 0, 1)

    # aperçu du seuillage par hystérésis : contour du masque d'analyse (bas
    # relié aux germes) + germes hauts en surbrillance
    seeds = seg.signal_map >= calib.threshold
    thr_view = _heat(sig_norm)
    thr_view = _overlay_boundary(thr_view, seg.analysis_mask, (1.0, 1.0, 1.0))
    thr_view[seeds] = np.array([1.0, 0.3, 0.3], dtype=np.float32)

    panels: List[Tuple[str, np.ndarray]] = [
        ("1. Originale", rgb),
        (f"2. Prominence DAB (fond-s={calib.background_sigma:.0f}px)",
         _heat(sig_norm)),
        (f"3. Hysteresis [{calib.threshold_source}] {calib.threshold_low:.3f}->{calib.threshold:.3f}",
         thr_view),
        (f"4. Masque ANALYSE fidele (n={seg.n_objects})",
         _overlay_boundary(rgb, seg.analysis_mask, (0.10, 0.85, 0.20))),
        ("5. Masque FIGURE embelli",
         _overlay_boundary(rgb, fig.figure_mask, (1.0, 0.55, 0.0))),
        ("6. FIGURE fond blanc", fig.rgb_white),
        ("7. FIGURE transparent (damier)",
         _composite_over_checker(fig.rgba_transparent)),
        (f"8. Alpha feathering (s={fig.feather_sigma:g})",
         np.dstack([fig.alpha] * 3)),
    ]

    n = len(panels)
    rows = (n + COLS - 1) // COLS
    cell_w = PANEL + PAD
    cell_h = PANEL + LABEL_H + PAD
    W = COLS * cell_w + PAD
    H = rows * cell_h + PAD
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.load_default()
    except Exception:  # pragma: no cover
        font = None

    for i, (title, img) in enumerate(panels):
        r, c = divmod(i, COLS)
        x = PAD + c * cell_w
        y = PAD + r * cell_h
        draw.rectangle([x, y, x + PANEL, y + LABEL_H], fill=(30, 30, 40))
        draw.text((x + 4, y + 5), title, fill=(240, 240, 240), font=font)
        canvas.paste(_fit(img), (x, y + LABEL_H))

    return canvas
