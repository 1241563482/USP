"""Command-line entry point for the workflow."""

import argparse
import os
import logging

from .api import MaterialsProjectClient
from .optimizer import MACEOptimizer
from .dft import DummyDFTCalculator
from .workflow import run_workflow


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run USP workflow.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Path to input CSV/JSON file")
    group.add_argument("--mp", nargs="+",
                       help="List of element symbols to download from Materials Project")
    parser.add_argument("--mp-api-key", default=os.environ.get("MP_API_KEY"),
                        help="Materials Project API key (or set MP_API_KEY env var)")
    parser.add_argument("--output-dir", default=".",
                        help="Directory to write CIF files when using --mp")
    args = parser.parse_args()

    if not args.mp_api_key:
        parser.error("Materials Project API key must be provided via --mp-api-key or MP_API_KEY")

    provider = MaterialsProjectClient(api_key=args.mp_api_key)
    optimizer = MACEOptimizer()
    dft_calc = DummyDFTCalculator()

    if args.mp:
        # element-based download mode; fetch structures and optionally write
        # them to disk.  ``output_dir`` defaults to current working directory.
        ids = provider.download_structures_by_elements(args.mp, out_dir=args.output_dir)
        # report what was done, even though the CIFs are written to files
        for mid in ids:
            print(f"downloaded {mid} -> {args.output_dir}/{mid}.cif")
        return

    # normal workflow using an input file
    results = run_workflow(args.input, provider, optimizer, dft_calc)
    for r in results:
        logger.info(f"Processed {r['id']}: {r['result']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
