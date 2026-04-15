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
    parser.add_argument("--mp-api-key", nargs='?', const=None, default=argparse.SUPPRESS,
                        help="Materials Project API key. "
                             "Use 'usp --mp-api-key' to check existing key from ~/.bashrc. "
                             "Use 'usp --mp-api-key <KEY>' to set it.")
    parser.add_argument("--output-dir", default=".",
                        help="Directory to write CIF files when using --mp")
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

    # Normal workflow: require either --input or --mp
    if not args.input and not args.mp:
        parser.error("One of --input or --mp is required")

    mp_api_key = os.environ.get("MP_API_KEY") or _read_mp_api_key_from_bashrc()
    if not mp_api_key:
        parser.error("Materials Project API key must be provided via --mp-api-key or MP_API_KEY env var")

    provider = MaterialsProjectClient(api_key=mp_api_key)
    optimizer = MACEOptimizer()
    dft_calc = DummyDFTCalculator()

    if args.mp:
        ids = provider.download_structures_by_elements(args.mp, out_dir=args.output_dir)
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
