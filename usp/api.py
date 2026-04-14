"""Structure provider abstractions and Materials Project client."""

from abc import ABC, abstractmethod
from typing import Any

from pymatgen.core import Structure
from pymatgen.ext.matproj import MPRester

# optional import of the newer Materials Project API client
try:
    from mp_api.client import MPRester as MPAPIClient
except ImportError:  # pragma: no cover - optional dependency
    MPAPIClient = None


class StructureProvider(ABC):
    """Base class for obtaining structures from a source.

    Concrete providers must implement :meth:`get_structure`.  Implementations may
    also offer additional convenience helpers; one such helper is
    :meth:`get_structures_by_elements` which, by default, raises
    :class:`NotImplementedError`.
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
    """Fetch structures from the Materials Project API.

    The class wraps :class:`~pymatgen.ext.matproj.MPRester` and exposes a simple
    interface that the rest of the workflow code can consume.  In addition to
    fetching a single structure by ID, we also support querying by a list of
    elements which is useful for the ``--mp`` command‑line option.
    """

    def __init__(self, api_key: str):
        self._mpr = MPRester(api_key)
        # if the mp-api client is available we keep an instance around for
        # queries; tests may monkeypatch ``self._mpapi`` as needed.
        if MPAPIClient is not None:
            self._mpapi = MPAPIClient(api_key)
        else:
            self._mpapi = None

    def get_structure(self, identifier: Any) -> Structure:
        # identifier may be MP-ID (e.g. "mp-1234") or formula
        return self._mpr.get_structure_by_material_id(str(identifier))

    def get_structures_by_elements(self, elements: list[str]) -> list[tuple[str, Structure]]:
        """Return ``(mp_id, structure)`` tuples for all materials containing any
        of the specified elements.

        Parameters
        ----------
        elements
            List of element symbols (e.g. ``["Li", "In"]``) to search for.

        Notes
        -----
        This is a thin wrapper around :meth:`~pymatgen.ext.matproj.MPRester.query`.
        The returned list may be large depending on the element set, so callers
        should be prepared to handle many entries.
        """
        # pymatgen query syntax; only request the fields we need
        # prefer the new mp-api search interface if available
        if self._mpapi is not None:
            # ``chemsys`` expects a dash-separated string, e.g. "Li-In" for
            # elements requested.  The API returns objects with attributes rather
            # than dicts.
            chemsys = "-".join(elements)
            docs = self._mpapi.materials.summary.search(chemsys=chemsys)
            return [(doc.material_id, doc.structure) for doc in docs]

        raise RuntimeError(
            "Element-based search requires the 'mp-api' package, which is not available. "
            "Please install it: pip install mp-api"
        )

    def download_structures_by_elements(self, elements: list[str], out_dir: str = ".") -> list[str]:
        """Search and write CIFs for matching materials.

        The API key held by the client is reused; callers do not need to supply it
        again.  The output directory is created if necessary, and the list of
        downloaded material IDs is returned.
        """
        from pathlib import Path
        from pymatgen.io.cif import CifWriter

        Path(out_dir).mkdir(parents=True, exist_ok=True)
        entries = self.get_structures_by_elements(elements)
        ids: list[str] = []
        for mid, struct in entries:
            CifWriter(struct).write_file(Path(out_dir) / f"{mid}.cif")
            ids.append(mid)
        return ids
