# USP (Universal Superionic Prediction)

This Python package provides a framework for constructing workflows targeting ionic materials. The pipeline reads an input file, fetches structures (e.g. from the Materials Project), relaxes them via a generic force field (currently MACE), and finally runs a self-consistent DFT calculation.

## Features

- **Input parsing**: flexible readers for CSV/JSON of candidate identifiers.
- **Structure providers**: default implementation uses Materials Project API via `pymatgen`.
- **Optimizers**: abstract interface; a stub `MACEOptimizer` is provided.
- **DFT calculators**: pluggable backends; interface defined for future integrations.
- **Workflow orchestration**: end-to-end driver script and console entry point.

## Installation

```bash
python -m pip install -e .
```

## Usage

Either supply an input file listing Materials Project IDs or formulas, or
ask USP to pull all entries containing specified elements directly from the
Materials Project server.  When using ``--mp`` you can also specify an
output directory for the downloaded CIF files with ``--output-dir``.

```bash
usp --input candidates.csv                      # normal workflow
usp --mp Li In --mp-api-key <YOUR_KEY>           # download Li/In entries
usp --mp Li In --mp-api-key <YOUR_KEY> \
    --output-dir cif_files                       # save CIFs in subfolder
```

You only need to provide the API key once per invocation; the key may be set
in your shell environment instead of passed on the command line:

```bash
export MP_API_KEY=<YOUR_KEY>
usp --mp Li In            # will pick up key automatically
```

## Extensibility

Subclass `StructureProvider`, `Optimizer`, or `DFTCalculator` to swap components.

See the docstrings in the source modules for details.
