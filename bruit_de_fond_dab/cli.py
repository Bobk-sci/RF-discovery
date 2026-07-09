"""Interface en ligne de commande.

Exemples :
    python -m bruit_de_fond_dab.cli input.png -o out/
    python -m bruit_de_fond_dab.cli dossier_images/ -o out/ --no-local-contrast
    python -m bruit_de_fond_dab.cli --demo -o out/     # image synthétique de test
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import process_path, process_image


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bruit_de_fond_dab",
        description="Détourage d'astrocytes DAB avec auto-calibrage par image "
                    "(modes ANALYSE + FIGURE).",
    )
    p.add_argument("input", nargs="?",
                   help="image ou dossier d'images à traiter")
    p.add_argument("-o", "--out", default="out",
                   help="dossier de sortie (défaut: out/)")
    p.add_argument("--no-qc", action="store_true",
                   help="ne pas générer le panneau QC")
    p.add_argument("--no-local-contrast", action="store_true",
                   help="désactiver le rehaussement de contraste local (figure)")
    p.add_argument("--feather-sigma", type=float, default=1.0,
                   help="flou du canal alpha en px (défaut: 1.0)")
    p.add_argument("--close-radius", type=int, default=None,
                   help="rayon de fermeture figure (défaut: auto)")
    p.add_argument("--background-sigma", type=float, default=None,
                   help="sigma du fond local soustrait, en px (défaut: auto, "
                        "dérivé de la taille de l'image). Diminuer si les "
                        "astrocytes sont petits ; augmenter s'ils sont grands.")
    p.add_argument("--demo", action="store_true",
                   help="générer et traiter une image DAB synthétique de test")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    out_dir = Path(args.out)

    kwargs = dict(
        write_qc=not args.no_qc,
        local_contrast=not args.no_local_contrast,
        feather_sigma=args.feather_sigma,
        close_radius=args.close_radius,
        background_sigma=args.background_sigma,
    )

    if args.demo:
        from .synthetic import make_demo_image
        demo_path = out_dir / "demo_input.png"
        out_dir.mkdir(parents=True, exist_ok=True)
        make_demo_image(demo_path)
        outputs = [process_image(demo_path, out_dir, **kwargs)]
    elif args.input:
        outputs = process_path(args.input, out_dir, **kwargs)
    else:
        build_parser().print_help()
        return 2

    for o in outputs:
        c = o.calibration
        print(f"[{o.name}] blanc(lum)={c.white_luminance:.3f} "
              f"seuil[{c.threshold_source}]={c.threshold:.4f} "
              f"objets={o.segmentation.n_objects} -> {o.paths.get('qc', o.paths['analysis_mask'])}")
    print(f"Journal : {out_dir/'calibration_log.json'} / "
          f"{out_dir/'calibration_log.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
