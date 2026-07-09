"""Segmentation -> masque FIDÈLE (base commune aux deux modes de sortie).

Le masque d'analyse combine DEUX critères de FORME, pas d'intensité :
    1. STRUCTURE : seuillage par hystérésis de la carte de tubeness (prolongements
       fins et ramifiés) ;
    2. ANCRAGE SUR SOMA : on ne conserve que les structures CONNECTÉES à un corps
       cellulaire (soma) détecté, et dans un rayon plausible autour de lui.

C'est l'ancrage sur soma qui élimine le fond fibreux : les fibres de neuropile
sont filamenteuses mais n'ont PAS de soma -> elles sont rejetées. Un astrocyte =
un soma + ses branches connectées.

Aucune morphologie cosmétique (fermeture, lissage) : le masque reste FIDÈLE pour
le Sholl / YOLO. L'embellissement figure est fait séparément dans rendering.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.ndimage import distance_transform_edt
from skimage.measure import label
from skimage.filters import apply_hysteresis_threshold
from skimage.morphology import reconstruction

from .calibration import CalibrationResult
from .structure import detect_somata, auto_soma_radius
from .morph_compat import remove_small_objects, remove_small_holes

# Rayon max d'un astrocyte (fraction de la taille image) : borne la croissance
# depuis le soma pour ne pas fusionner tout un champ dense en un seul objet.
MAX_REACH_FRAC = 0.10


@dataclass
class SegmentationResult:
    """Résultat de segmentation partagé par les deux modes."""

    analysis_mask: np.ndarray   # bool (H, W) — masque fidèle
    signal_map: np.ndarray      # float (H, W) — carte de structure (tubeness)
    soma_mask: np.ndarray       # bool (H, W) — somas détectés (QC)
    threshold: float
    n_objects: int


def segment_astrocytes(
    signal_map: np.ndarray,
    calib: CalibrationResult,
    dab: Optional[np.ndarray] = None,
    soma_anchor: bool = True,
) -> SegmentationResult:
    """Construit le masque d'analyse fidèle (structure + ancrage soma)."""
    # 1) STRUCTURE : hystérésis sur la carte de tubeness.
    if calib.threshold_low < calib.threshold:
        struct = apply_hysteresis_threshold(
            signal_map, calib.threshold_low, calib.threshold
        )
    else:
        struct = signal_map >= calib.threshold
    struct = np.asarray(struct, dtype=bool)

    # 2) ANCRAGE SUR SOMA : ne conserver que les structures reliées à un soma,
    #    dans un rayon plausible. C'est ce qui supprime le fond fibreux.
    soma_mask = np.zeros_like(struct)
    if soma_anchor and dab is not None:
        radius = auto_soma_radius(calib.height, calib.width)
        somata = detect_somata(dab, radius, sensitivity=calib.sensitivity)
        # germes = somas qui coïncident avec de la structure
        seed = somata & struct
        if seed.any():
            soma_mask = somata
            # propage les germes dans la structure (composantes contenant un soma)
            grown = reconstruction(seed, struct, method="dilation").astype(bool)
            # borne l'extension à un rayon max autour des somas
            max_reach = MAX_REACH_FRAC * min(calib.height, calib.width)
            dist = distance_transform_edt(~seed)
            raw = grown & (dist <= max_reach)
        else:
            raw = struct  # aucun soma trouvé -> on garde la structure brute
    else:
        raw = struct

    # 3) Nettoyage MINIMAL : micro-débris + petits trous internes. Pas de
    #    fermeture ni dilatation -> gaps authentiques préservés.
    cleaned = remove_small_objects(raw, min_size=calib.min_object_size)
    hole_area = max(4, calib.min_object_size // 4)
    cleaned = remove_small_holes(cleaned, area_threshold=hole_area)

    n = int(label(cleaned).max())
    return SegmentationResult(
        analysis_mask=cleaned,
        signal_map=signal_map,
        soma_mask=soma_mask,
        threshold=calib.threshold,
        n_objects=n,
    )
