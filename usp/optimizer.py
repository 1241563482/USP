"""Optimizer interface and MACE stub."""

from abc import ABC, abstractmethod
from pymatgen.core import Structure
import logging


logger = logging.getLogger(__name__)


class Optimizer(ABC):
    """Abstract optimizer that relaxes a structure."""

    @abstractmethod
    def optimize(self, structure: Structure) -> Structure:
        """Return a relaxed pymatgen Structure."""
        pass


class MACEOptimizer(Optimizer):
    """Placeholder optimizer using the MACE force field.

    Actual MACE integration should replace the stub code.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path

    def optimize(self, structure: Structure) -> Structure:
        logger.info("Optimizing structure with MACE (stub)")
        # TODO: call MACE API or CLI to relax structure
        return structure
