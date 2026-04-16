"""Optimizer interface and MACE implementation."""

from abc import ABC, abstractmethod
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
import logging
import warnings
import os

warnings.filterwarnings("ignore", message=".*TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD.*")
warnings.filterwarnings("ignore", message=".*cuequivariance.*is not available.*")

logger = logging.getLogger(__name__)


class Optimizer(ABC):
    """Abstract optimizer that relaxes a structure."""

    @abstractmethod
    def optimize(self, structure: Structure) -> Structure:
        """Return a relaxed pymatgen Structure."""
        pass


class MACEOptimizer(Optimizer):
    """MACE universal force-field optimizer.

    Supports both pymatgen Structure optimization (used by the workflow)
    and direct ASE XYZ file relaxation.
    """

    def __init__(self, model_path: str = None, device: str = "cpu", dtype: str = "float64"):
        self.model_path = model_path
        self.device = device
        self.dtype = dtype

    def optimize(self, structure: Structure) -> Structure:
        """Relax a pymatgen Structure and return the relaxed Structure."""
        atoms = AseAtomsAdaptor().get_atoms(structure)
        relaxed = self._relax_atoms(atoms)
        return AseAtomsAdaptor().get_structure(relaxed)

    def relax_file(self, input_path: str, output_path: str = "opt.xyz") -> None:
        """Read an XYZ file, relax with MACE, and write the result to XYZ."""
        try:
            from ase.io import read, write
        except ImportError as exc:
            raise RuntimeError(
                "ASE is required for MACE relaxation. Please install: pip install ase"
            ) from exc

        atoms_to_relax = read(input_path, ":")
        out = []
        for atoms in atoms_to_relax:
            relaxed = self._relax_atoms(atoms)
            out.append(relaxed)
        write(output_path, out)
        logger.info(f"Relaxed structures saved to {output_path}")

    def _relax_atoms(self, atoms):
        """Internal helper: run ASE geometry optimization on ASE Atoms."""
        try:
            from mace.calculators import mace_mp
        except ImportError as exc:
            raise RuntimeError(
                "MACE is required for relaxation. Please install: pip install mace-torch"
            ) from exc

        try:
            from ase.optimize import BFGS
        except ImportError as exc:
            raise RuntimeError(
                "ASE is required for MACE relaxation. Please install: pip install ase"
            ) from exc


        calc = mace_mp(model=self.model_path, device=self.device, dtype=self.dtype)
        atoms.calc = calc
        dyn = BFGS(atoms, logfile="-")
        dyn.run(fmax=0.001)
        energy = atoms.get_potential_energy()
        logger.info(f"MACE relaxation converged, final energy: {energy:.4f} eV")

        return atoms
