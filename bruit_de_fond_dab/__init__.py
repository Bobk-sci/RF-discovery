"""Bruit-de-fond-DAB : détourage d'astrocytes DAB avec auto-calibrage par image.

Deux modes de sortie partagent le même masque de segmentation :
    - MODE ANALYSE : masque fidèle (Sholl / YOLO en aval)
    - MODE FIGURE  : rendu esthétique (publication)

L'auto-calibrage est réalisé image par image : point blanc, échelle d'OD et
seuils sont estimés à partir des statistiques propres à chaque image. La logique
de décision reste identique d'une image à l'autre ; seules les valeurs
numériques s'adaptent, et elles sont journalisées pour la traçabilité.
"""

from .calibration import CalibrationResult, calibrate_image
from .segmentation import SegmentationResult, segment_astrocytes
from .rendering import FigureRender, render_figure
from .pipeline import ProcessOutput, process_image, process_path

__all__ = [
    "CalibrationResult",
    "calibrate_image",
    "SegmentationResult",
    "segment_astrocytes",
    "FigureRender",
    "render_figure",
    "ProcessOutput",
    "process_image",
    "process_path",
]

__version__ = "0.1.0"
