"""Structure provider abstractions and Materials Project client."""

from abc import ABC, abstractmethod
from typing import Any
from pymatgen.core import Structure
from pymatgen.ext.matproj import MPRester

try:
    from mp_api.client import MPRester as MPAPIClient
except:
    raise ImportError(
        "The mp-api package is required, please install by pip install mp-api"
    )


class StructureProvider(ABC):
    """
    Base class for obtaining structures from a source.
    """

    @abstractmethod
    def get_structure(self, identifier: Any) -> Structure:
        """Return a pymatgen Structure for the given identifier."""
        pass

    def get_structures_by_elements(self, elements: list[str]) -> list:
        """Optional helper to fetch many materials by element list.

        Subclasses can override this if they support element-based queries.
        The default simply raises to signal it is unavailable.
        """
        raise NotImplementedError("element search not supported by provider")


class MaterialsProjectClient(StructureProvider):
    """
    Fetch structures from the Materials Project API.
    """

    def __init__(self, api_key: str):
        self._mpr = MPRester(api_key)
        self._mpapi = MPAPIClient(api_key)

    def get_structure(self, identifier: Any) -> Structure:
        # identifier may be MP-ID (e.g. "mp-1234") or formula
        return self._mpr.get_structure_by_material_id(str(identifier))

    def get_structures_by_elements(self, elements: list[str]) -> list[tuple[str, Structure]]:
        """
        Parameters
        ----------
        elements
            List of element symbols (e.g. ``["Li", "In"]``) to search for.
        """
        if self._mpapi is not None:
            chemsys = "-".join(elements)
            docs = self._mpapi.materials.summary.search(chemsys=chemsys)
            return [(doc.material_id, doc.structure) for doc in docs]
        else:
            raise RuntimeError("The mp-api package is required, please install by pip install mp-api")

    def download_structures_by_elements(self, elements: list[str], out_dir: str = ".") -> list[str]:
        """
        Search and write VASP POSCARs for matching materials.
        """
        from pathlib import Path
        from pymatgen.io.vasp import Poscar

        Path(out_dir).mkdir(parents=True, exist_ok=True)
        entries = self.get_structures_by_elements(elements)
        ids: list[str] = []
        for i, (mid, struct) in enumerate(entries, start=1):
            formula = struct.composition.reduced_formula
            filename = Path(out_dir) / f"{i}-{formula}-{mid}.vasp"
            Poscar(struct).write_file(filename)
            ids.append(mid)
        return ids
