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


def _diffuse_neuropile(size: int, rng: np.random.Generator,
                       level: float) -> np.ndarray:
    """Fond de neuropile diffus, basse fréquence + texture fibreuse fine.

    `level` module l'intensité globale du marquage de fond. Cas `heavy` : le
    neuropile est fortement et inégalement marqué (comme sur une lame réelle),
    ce qui piège un simple seuillage global.
    """
    from scipy.ndimage import gaussian_filter
    # composante basse fréquence (patches de neuropile)
    low = gaussian_filter(rng.random((size, size)).astype(np.float32), sigma=size * 0.06)
    low = (low - low.min()) / (np.ptp(low) + 1e-6)
    # texture fibreuse fine
    fine = gaussian_filter(rng.random((size, size)).astype(np.float32), sigma=1.5)
    fine = (fine - fine.min()) / (np.ptp(fine) + 1e-6)
    neuropile = level * (0.7 * low + 0.3 * fine)
    return neuropile.astype(np.float32)


def _faint_mesh(size: int, rng: np.random.Generator, n_fibres: int,
                amp: float) -> np.ndarray:
    """Maillage fibreux FAIBLE (neuropile hors-plan) à rejeter.

    Mêmes structures fines que les astrocytes mais nettement moins DENSES
    (amplitude basse) : seul un seuillage sélectif par l'intensité les écarte.
    """
    density = np.zeros((size, size), dtype=np.float32)
    for _ in range(n_fibres):
        y, x = rng.uniform(0, size), rng.uniform(0, size)
        ang = rng.uniform(0, 2 * np.pi)
        steps = int(rng.uniform(20, 60))
        width = rng.uniform(0.8, 1.4)
        for _ in range(steps):
            ang += rng.normal(0, 0.25)
            y += np.sin(ang); x += np.cos(ang)
            iy, ix = int(round(y)), int(round(x))
            if 0 <= iy < size and 0 <= ix < size:
                density[iy, ix] += amp * rng.uniform(0.5, 1.0)
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(density, sigma=width).astype(np.float32)


def make_dense_mesh_image(path: PathLike, size: int = 900, seed: int = 3,
                          n_astro: int = 28) -> np.ndarray:
    """Image type lame réelle : nombreux astrocytes SOMBRES sur maillage FAIBLE.

    Reproduit le cas où un seuil trop permissif capture tout le maillage (mask
    envahissant, astrocytes non définis). Retourne le tableau RGB.
    """
    rng = np.random.default_rng(seed)
    density = np.zeros((size, size), dtype=np.float32)

    # maillage faible envahissant (à REJETER)
    density += _faint_mesh(size, rng, n_fibres=140, amp=0.16)

    # astrocytes sombres, denses, bien contrastés (à GARDER)
    for _ in range(n_astro):
        cy = int(rng.uniform(0.05, 0.95) * size)
        cx = int(rng.uniform(0.05, 0.95) * size)
        _star_astrocyte(
            density, cy, cx, rng,
            soma_r=rng.uniform(4, 7), n_proc=rng.integers(6, 10),
            reach=rng.uniform(30, 55),
        )

    density = np.clip(density, 0, 1.5)
    od = density[..., None] * (-np.log(np.clip(DAB_BROWN, 1e-3, 1)))[None, None, :]
    rgb = BG_WHITE[None, None, :] * np.exp(-od)
    rgb = np.clip(rgb, 0, 1).astype(np.float32)
    write_rgb(path, rgb)
    return rgb


def make_demo_image(path: PathLike, size: int = 640, seed: int = 7,
                    heavy: bool = False) -> np.ndarray:
    """Crée et écrit une image DAB synthétique. Retourne le tableau RGB.

    `heavy=True` ajoute un neuropile de fond fortement marqué (lame dense) pour
    valider la soustraction de fond local.
    """
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
    if heavy:
        density += _diffuse_neuropile(size, rng, level=0.55)
    else:
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
