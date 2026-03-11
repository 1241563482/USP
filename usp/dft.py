"""DFT calculation interface and stub implementation."""

from abc import ABC, abstractmethod
from pymatgen.core import Structure
import logging


logger = logging.getLogger(__name__)


class DFTCalculator(ABC):
    """Abstract base class representing a DFT calculator."""

    @abstractmethod
    def run(self, structure: Structure) -> dict:
        """Perform a DFT calculation on the given structure.

        Returns a dict containing results (energy, forces, etc.).
        """
        pass


class DummyDFTCalculator(DFTCalculator):
    """Simple dummy implementation that does nothing."""

    def run(self, structure: Structure) -> dict:
        logger.info("Running dummy DFT calculation (no-op)")
        return {"energy": None}
