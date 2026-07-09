"""Tests de fumée du pipeline (bout en bout sur image synthétique)."""
from pathlib import Path

import numpy as np

from bruit_de_fond_dab.synthetic import make_demo_image
from bruit_de_fond_dab.pipeline import process_image
from bruit_de_fond_dab.calibration import calibrate_image
from bruit_de_fond_dab.segmentation import segment_astrocytes
from bruit_de_fond_dab.rendering import render_figure


def test_end_to_end(tmp_path: Path):
    demo = tmp_path / "demo.png"
    make_demo_image(demo, size=320)
    out = process_image(demo, tmp_path / "out")

    # les 4 astrocytes synthétiques sont retrouvés, débris/neuropile écartés
    assert 3 <= out.segmentation.n_objects <= 6

    # toutes les sorties existent
    for key in ("analysis_mask", "figure_transparent", "figure_white", "qc"):
        assert Path(out.paths[key]).exists()

    # journal écrit
    assert (tmp_path / "out" / "calibration_log.json").exists()
    assert (tmp_path / "out" / "calibration_log.csv").exists()


def test_calibration_is_per_image():
    """Deux images de statistiques différentes -> seuils différents,
    même LOGIQUE de décision (mêmes champs journalisés)."""
    a = make_demo_image(Path("/tmp/_a.png"), size=256, seed=1)
    b = np.clip(a * 0.6 + 0.2, 0, 1).astype(np.float32)  # image plus claire

    ca, _ = calibrate_image(a)
    cb, _ = calibrate_image(b)

    assert ca.to_log_dict().keys() == cb.to_log_dict().keys()
    assert ca.threshold != cb.threshold  # valeurs adaptées à chaque image
    assert ca.white_luminance != cb.white_luminance


def test_heavy_neuropile_is_suppressed():
    """Sur fond de neuropile FORTEMENT marqué, la soustraction de fond local
    doit quand même isoler les astrocytes sur un fond propre (pas de sortie
    quasi vide, pas de fond saturé)."""
    rgb = make_demo_image(Path("/tmp/_heavy.png"), size=512, seed=7, heavy=True)
    calib, signal = calibrate_image(rgb)
    seg = segment_astrocytes(signal, calib)

    # les astrocytes sont retrouvés (pas la sortie quasi vide du bug initial)
    assert seg.n_objects >= 3
    # le fond reste propre : la couverture du masque est faible (pas tout le champ)
    coverage = seg.analysis_mask.mean()
    assert 0.001 < coverage < 0.10
    # le seuil est fini et strictement positif
    assert calib.threshold > 0


def test_figure_and_analysis_diverge():
    """Le mode figure embellit (>= surface) ; le mode analyse reste fidèle."""
    rgb = make_demo_image(Path("/tmp/_c.png"), size=320, seed=3)
    calib, dab = calibrate_image(rgb)
    seg = segment_astrocytes(dab, calib)
    fig = render_figure(rgb, seg.analysis_mask, calib)

    # la fermeture ne peut qu'ajouter de la surface, jamais amputer le fidèle
    assert fig.figure_mask.sum() >= seg.analysis_mask.sum() * 0.98
    # l'alpha est bien dans [0, 1] et flouté (valeurs intermédiaires aux bords)
    assert fig.alpha.min() >= 0.0 and fig.alpha.max() <= 1.0
    assert ((fig.alpha > 0.05) & (fig.alpha < 0.95)).any()
