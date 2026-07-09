"""Entrées/sorties images robustes (lecture RGB float, écriture PNG RGBA)."""
from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image

PathLike = Union[str, Path]


def read_rgb(path: PathLike) -> np.ndarray:
    """Lit une image en RGB float32 dans [0, 1].

    Les images en niveaux de gris sont dupliquées sur 3 canaux ; l'alpha
    éventuel est aplati sur fond blanc (l'illumination de fond est claire).
    """
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img).convert("RGB")
    else:
        img = img.convert("RGB")
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return arr


def write_rgba(path: PathLike, rgba: np.ndarray) -> None:
    """Écrit un tableau RGBA float [0,1] (ou uint8) en PNG."""
    arr = _to_uint8(rgba)
    Image.fromarray(arr, mode="RGBA").save(str(path))


def write_rgb(path: PathLike, rgb: np.ndarray) -> None:
    """Écrit un tableau RGB float [0,1] (ou uint8)."""
    arr = _to_uint8(rgb)
    Image.fromarray(arr, mode="RGB").save(str(path))


def _to_uint8(arr: np.ndarray) -> np.ndarray:
    if arr.dtype == np.uint8:
        return arr
    return (np.clip(arr, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
