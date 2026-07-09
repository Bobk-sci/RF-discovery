"""Génère une image DAB synthétique (astrocytes bruns + bruit de neuropile).

Sert de jeu de test reproductible pour valider le pipeline de bout en bout en
l'absence de lames réelles. NON destiné à la quantification.
"""
from __future__ import annotations

import numpy as np

from .imageio_utils import write_rgb, PathLike

DAB_BROWN = np.array([0.35, 0.22, 0.10], dtype=np.float32)   # brun DAB
BG_WHITE = np.array([0.95, 0.94, 0.92], dtype=np.float32)    # fond clair


def _star_astrocyte(canvas: np.ndarray, cy: int, cx: int,
                    rng: np.random.Generator, soma_r: float, n_proc: int,
                    reach: float) -> None:
    """Dessine un astrocyte étoilé (soma + prolongements fins) en densité."""
    h, w = canvas.shape
    yy, xx = np.mgrid[0:h, 0:w]
    # soma (gaussien)
    d2 = (yy - cy) ** 2 + (xx - cx) ** 2
    canvas += 0.9 * np.exp(-d2 / (2 * soma_r ** 2))
    # prolongements : segments bruités
    for _ in range(n_proc):
        ang = rng.uniform(0, 2 * np.pi)
        length = reach * rng.uniform(0.5, 1.0)
        steps = int(length)
        y, x = float(cy), float(cx)
        dy, dx = np.sin(ang), np.cos(ang)
        width = rng.uniform(0.8, 1.6)
        for s in range(steps):
            ang += rng.normal(0, 0.15)
            dy, dx = np.sin(ang), np.cos(ang)
            y += dy
            x += dx
            iy, ix = int(round(y)), int(round(x))
            if 0 <= iy < h and 0 <= ix < w:
                amp = 0.6 * (1 - s / max(steps, 1))
                rr = int(np.ceil(width))
                y0, y1 = max(0, iy - rr), min(h, iy + rr + 1)
                x0, x1 = max(0, ix - rr), min(w, ix + rr + 1)
                sub = canvas[y0:y1, x0:x1]
                ly, lx = np.mgrid[y0:y1, x0:x1]
                sub += amp * np.exp(
                    -((ly - iy) ** 2 + (lx - ix) ** 2) / (2 * width ** 2)
                )


def make_demo_image(path: PathLike, size: int = 640, seed: int = 7) -> np.ndarray:
    """Crée et écrit une image DAB synthétique. Retourne le tableau RGB."""
    rng = np.random.default_rng(seed)
    density = np.zeros((size, size), dtype=np.float32)

    # quelques astrocytes bien formés
    centers = [(0.30, 0.30), (0.68, 0.35), (0.45, 0.70), (0.78, 0.72)]
    for fy, fx in centers:
        _star_astrocyte(
            density, int(fy * size), int(fx * size), rng,
            soma_r=rng.uniform(6, 9), n_proc=rng.integers(7, 11),
            reach=rng.uniform(45, 70),
        )

    # bruit de fond diffus (neuropile) : doit être éliminé par le calibrage
    neuropile = rng.gamma(1.2, 0.03, size=(size, size)).astype(np.float32)
    neuropile += 0.05 * rng.random((size, size)).astype(np.float32)
    density += neuropile

    # fragments épars (débris) : doivent être supprimés (taille min)
    for _ in range(60):
        y = rng.integers(0, size)
        x = rng.integers(0, size)
        density[max(0, y - 1):y + 1, max(0, x - 1):x + 1] += rng.uniform(0.2, 0.5)

    density = np.clip(density, 0, 1.5)

    # densité -> RGB par loi de Beer-Lambert (fond clair, marquage brun)
    od = density[..., None] * (-np.log(np.clip(DAB_BROWN, 1e-3, 1)))[None, None, :]
    rgb = BG_WHITE[None, None, :] * np.exp(-od)
    # légère variation d'illumination (teste le point blanc par image)
    ramp = np.linspace(0.97, 1.03, size).astype(np.float32)
    rgb *= ramp[None, :, None]
    rgb = np.clip(rgb, 0, 1).astype(np.float32)

    write_rgb(path, rgb)
    return rgb
