"""High-level workflow orchestration."""

from pathlib import Path
from typing import List, Dict
from pymatgen.core import Structure

from .input import read_csv, read_json
from .api import StructureProvider
from .optimizer import Optimizer
from .dft import DFTCalculator


def _parse_input(path: str) -> List[Dict]:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return read_csv(path)
    elif suffix == ".json":
        return read_json(path)
    else:
        raise ValueError("Unsupported input format")


def run_workflow(input_file: str,
                 provider: StructureProvider,
                 optimizer: Optimizer,
                 dft_calc: DFTCalculator):
    """Run the full screening workflow.

    - Read candidate identifiers from the input file.
    - Fetch structure via provider.
    - Optimize structure via optimizer.
    - Run DFT calculation and collect results.
    """
    records = _parse_input(input_file)
    results = []
    for rec in records:
        identifier = rec.get("id") or rec.get("mp_id")
        if identifier is None:
            raise ValueError("Record missing 'id' or 'mp_id'")
        struct: Structure = provider.get_structure(identifier)
        struct = optimizer.optimize(struct)
        res = dft_calc.run(struct)
        results.append({"id": identifier, "result": res})
    return results
