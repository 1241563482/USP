"""Command-line entry point for the workflow."""

import argparse
import os
import re
import logging
from typing import Optional

from .api import MaterialsProjectClient
from .optimizer import MACEOptimizer
from .dft import DummyDFTCalculator
from .workflow import run_workflow
from .classifier import SuperionicClassifier


logger = logging.getLogger(__name__)
BASHRC_PATH = os.path.expanduser("~/.bashrc")


def _read_mp_api_key_from_bashrc() -> Optional[str]:
    """Read MP_API_KEY from ~/.bashrc if it exists."""
    if not os.path.isfile(BASHRC_PATH):
        return None
    with open(BASHRC_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'^(?:export\s+)?MP_API_KEY\s*=\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return None


def _write_mp_api_key_to_bashrc(key: str) -> None:
    """Write or update MP_API_KEY in ~/.bashrc."""
    if os.path.isfile(BASHRC_PATH):
        with open(BASHRC_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []

    new_line = f'export MP_API_KEY="{key}"\n'
    updated = False

    for i, line in enumerate(lines):
        if re.match(r'^(?:export\s+)?MP_API_KEY\s*=', line.strip()):
            lines[i] = new_line
            updated = True
            break

    if not updated:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(new_line)

    with open(BASHRC_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(description="Run USP workflow.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--input", help="Path to input CSV/JSON file")
    group.add_argument("--mp", nargs="+",
                       help="List of element symbols to download from Materials Project")
    group.add_argument("--relax", help="Path to input file for MACE relaxation")
    group.add_argument("--predict", help="Path to input XYZ file for superionic classification")
    parser.add_argument("--mp-api-key", nargs='?', const=None, default=argparse.SUPPRESS,
                        help="Materials Project API key. "
                             "Use 'usp --mp-api-key' to check existing key from ~/.bashrc. "
                             "Use 'usp --mp-api-key <KEY>' to set it.")
    parser.add_argument("--output-dir", default=".",
                        help="Directory to write output files when using --mp")
    parser.add_argument("--format", default="vasp", choices=["vasp", "xyz"],
                        help="Output format for downloaded structures (default: vasp)")
    parser.add_argument("--mace-device", default="cpu",
                        help="Device for MACE calculator (cpu or cuda)")
    parser.add_argument("--mace-dtype", default="float64",
                        help="Data type for MACE calculator (float32 or float64)")
    args = parser.parse_args()

    # Handle API key management mode
    if hasattr(args, "mp_api_key"):
        if args.mp_api_key is not None:
            # Setting mode: usp --mp-api-key xxx
            _write_mp_api_key_to_bashrc(args.mp_api_key)
            print("ok")
            return
        else:
            # Checking mode: usp --mp-api-key
            key = _read_mp_api_key_from_bashrc()
            if key:
                print("ok")
            else:
                print("MP_API_KEY not found. You can set it via: usp --mp-api-key <YOUR_KEY>")
            return

    # Relaxation mode: no MP key required
    if args.relax:
        optimizer = MACEOptimizer(device=args.mace_device, dtype=args.mace_dtype)
        optimizer.relax_file(args.relax, output_path="opt.xyz")
        return

    # Prediction mode: no MP key required
    if args.predict:
        SuperionicClassifier.predict_from_xyz(args.predict)
        return

    # Normal workflow: require either --input or --mp
    if not args.input and not args.mp:
        parser.error("One of --input, --mp, --relax, or --predict is required")

    mp_api_key = os.environ.get("MP_API_KEY") or _read_mp_api_key_from_bashrc()
    if not mp_api_key:
        parser.error("Materials Project API key must be provided via --mp-api-key or MP_API_KEY env var")

    provider = MaterialsProjectClient(api_key=mp_api_key)
    optimizer = MACEOptimizer(device=args.mace_device, dtype=args.mace_dtype)
    dft_calc = DummyDFTCalculator()

    if args.mp:
        ids = provider.download_structures_by_elements(args.mp, out_dir=args.output_dir, fmt=args.format)
        for mid in ids:
            print(f"downloaded {mid}")
        return

    # normal workflow using an input file
    results = run_workflow(args.input, provider, optimizer, dft_calc)
    for r in results:
        logger.info(f"Processed {r['id']}: {r['result']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
