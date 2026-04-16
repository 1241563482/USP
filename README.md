# USP (Universal Superionic Prediction)

A Python package for high-throughput screening and prediction of superionic materials. It integrates the Materials Project database, the MACE universal force field for structure relaxation, and a pre-fitted SVM classifier for superionicity.

## Features

- **Structure download**: query the Materials Project by element list and save structures in VASP or ASE-extended XYZ format.
- **Structure relaxation**: perform geometry optimization (BFGS) with the MACE-MP universal force field.
- **Superionic classification**: screen binary compounds with a built-in SVM decision plane using electronegativity, chemical hardness, and atomic mass descriptors.
- **API key management**: read or persist your Materials Project API key in `~/.bashrc` automatically.
- **Modular design**: pluggable `StructureProvider`, `Optimizer`, and `DFTCalculator` interfaces.

## Installation

```bash
python -m pip install -e .
```

> **Note**: `mace-torch` is required for structure relaxation. Install it with `pip install mace-torch` if you plan to use the `--relax` or full workflow features.

## API Key Management

USP can read the Materials Project API key from the `MP_API_KEY` environment variable or from `~/.bashrc`.

```bash
# Check if a key is already stored
usp --mp-api-key

# Store a new key in ~/.bashrc
usp --mp-api-key <YOUR_KEY>
```

Once stored, normal workflow commands will pick it up automatically.

## Usage

### 1. Download structures from the Materials Project

```bash
# Download Li/In entries as VASP POSCARs (default)
usp --mp Li In --mp-api-key <YOUR_KEY>

# Download as ASE-extended XYZ files
usp --mp Li In --mp-api-key <YOUR_KEY> --format xyz

# Save to a custom directory
usp --mp Li In --mp-api-key <YOUR_KEY> --output-dir structures
```

Files are named `序号-化学式-mpid.vasp` (or `.xyz`), e.g. `1-LiIn-mp-1234.vasp`.

### 2. Relax a structure with MACE

```bash
# CPU with default float64 (recommended for geometry optimization)
usp --relax structure.xyz

# GPU with float32
usp --relax structure.xyz --mace-device cuda --mace-dtype float32
```

The relaxed structure is written to `opt.xyz`.

### 3. Screen structures for superionicity

```bash
usp --predict candidates.xyz
```

Each frame in the input XYZ is classified by a hard-coded SVM boundary. Two files are produced in the current directory:

- `superionic.xyz`
- `non_superionic.xyz`

If `atoms.info` is empty, the classifier automatically populates it with elemental electronegativity (`chi`), chemical hardness (`eta`), and atomic masses from the internal database, where **A is always the element with the smaller atomic number**.

### 4. Full screening workflow

```bash
usp --input candidates.csv
```

This runs the end-to-end pipeline: read identifiers → fetch structures → MACE relaxation → DFT stub.

## Extensibility

Subclass `StructureProvider`, `Optimizer`, or `DFTCalculator` to swap backends.

See the docstrings in `usp/` for details.
