"""Orchestration : calibrage -> segmentation -> (analyse + figure) -> QC + log.

`process_image` traite une image et écrit toutes les sorties dans un dossier :
    <stem>_analysis_mask.png      masque fidèle (MODE ANALYSE)
    <stem>_figure_transparent.png rendu esthetique, fond transparent
    <stem>_figure_white.png       rendu esthetique, fond blanc pur
    <stem>_qc.png                 panneau QC (8 vignettes)
    calibration_log.json          valeurs auto-estimees par image (append)
    calibration_log.csv           idem, en tableau

Les deux modes partent du MÊME masque de segmentation ; seule l'étape de rendu
final diffère. On ne mesure JAMAIS le Sholl sur le mode figure.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union

import numpy as np

from .imageio_utils import read_rgb, write_rgb, write_rgba, PathLike
from .calibration import calibrate_image, CalibrationResult
from .segmentation import segment_astrocytes, SegmentationResult
from .rendering import render_figure, FigureRender
from .qc import build_qc_panel

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


@dataclass
class ProcessOutput:
    name: str
    calibration: CalibrationResult
    segmentation: SegmentationResult
    figure: FigureRender
    paths: dict


def process_image(
    image_path: PathLike,
    out_dir: PathLike,
    *,
    write_qc: bool = True,
    local_contrast: bool = True,
    feather_sigma: float = 1.0,
    close_radius: Optional[int] = None,
    background_sigma: Optional[float] = None,
    sensitivity: float = 1.0,
    soma_anchor: bool = True,
) -> ProcessOutput:
    """Traite une image et écrit toutes ses sorties."""
    image_path = Path(image_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = image_path.stem

    rgb = read_rgb(image_path)

    # 1) Auto-calibrage PAR IMAGE
    calib, signal_map, dab = calibrate_image(
        rgb, background_sigma=background_sigma, sensitivity=sensitivity
    )

    # 2) Segmentation -> masque FIDÈLE (structure + ancrage soma)
    seg = segment_astrocytes(signal_map, calib, dab=dab, soma_anchor=soma_anchor)

    # 3) MODE FIGURE (embellissement séparé)
    fig = render_figure(
        rgb,
        seg.analysis_mask,
        calib,
        close_radius=close_radius,
        feather_sigma=feather_sigma,
        local_contrast=local_contrast,
    )

    # 4) Écriture des sorties
    paths = {}
    p_mask = out_dir / f"{stem}_analysis_mask.png"
    write_rgb(p_mask, np.dstack([seg.analysis_mask.astype(np.float32)] * 3))
    paths["analysis_mask"] = str(p_mask)

    p_tr = out_dir / f"{stem}_figure_transparent.png"
    write_rgba(p_tr, fig.rgba_transparent)
    paths["figure_transparent"] = str(p_tr)

    p_wh = out_dir / f"{stem}_figure_white.png"
    write_rgb(p_wh, fig.rgb_white)
    paths["figure_white"] = str(p_wh)

    if write_qc:
        p_qc = out_dir / f"{stem}_qc.png"
        build_qc_panel(rgb, calib, seg, fig).save(str(p_qc))
        paths["qc"] = str(p_qc)

    # 5) Journalisation des valeurs auto-estimées (traçabilité / repro)
    _append_log(out_dir, image_path.name, calib, seg, fig)

    return ProcessOutput(
        name=image_path.name,
        calibration=calib,
        segmentation=seg,
        figure=fig,
        paths=paths,
    )


def process_path(
    input_path: PathLike,
    out_dir: PathLike,
    **kwargs,
) -> List[ProcessOutput]:
    """Traite une image ou toutes les images d'un dossier."""
    input_path = Path(input_path)
    if input_path.is_dir():
        files = sorted(
            p for p in input_path.iterdir() if p.suffix.lower() in IMAGE_EXTS
        )
    else:
        files = [input_path]
    if not files:
        raise FileNotFoundError(f"Aucune image trouvée dans {input_path}")
    return [process_image(f, out_dir, **kwargs) for f in files]


def _log_row(name: str, calib: CalibrationResult,
             seg: SegmentationResult, fig: FigureRender) -> dict:
    row = {"image": name, "timestamp": datetime.now(timezone.utc).isoformat()}
    row.update(calib.to_log_dict())
    row["n_objects"] = seg.n_objects
    row["fig_close_radius"] = fig.close_radius
    row["fig_feather_sigma"] = fig.feather_sigma
    row["fig_local_contrast"] = fig.local_contrast
    return row


def _append_log(out_dir: Path, name: str, calib: CalibrationResult,
                seg: SegmentationResult, fig: FigureRender) -> None:
    row = _log_row(name, calib, seg, fig)

    # JSON (liste append)
    json_path = out_dir / "calibration_log.json"
    data = []
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text())
        except (json.JSONDecodeError, ValueError):
            data = []
    data.append(row)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # CSV (aplati : listes -> chaînes)
    csv_path = out_dir / "calibration_log.csv"
    flat = {k: (";".join(map(str, v)) if isinstance(v, list) else v)
            for k, v in row.items()}
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(flat)
