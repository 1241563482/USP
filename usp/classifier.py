"""Superionic material classifier based on a pre-fitted SVM decision plane."""

from pathlib import Path
from ase.io import read, write


class SuperionicClassifier:
    """Binary classifier for superionic materials.

    The decision boundary is a hard-coded SVM hyper-plane:

        coef[0] * X + coef[1] * Y + coef[2] * Z + intercept = 0

    A positive decision value corresponds to the superionic class.
    """

    COEF = (
        0.03564779496537085,
        0.6567081317833354,
        -0.024798282957561923,
    )
    INTERCEPT = -2.2849193847913725

    @staticmethod
    def _check_info(info: dict) -> None:
        required_keys = ["chi_A", "chi_B", "eta_A", "eta_B", "m_A", "m_B"]
        missing = [k for k in required_keys if k not in info]
        if missing:
            raise ValueError(
                f"Missing required keys in atoms.info: {missing}. "
                f"Available keys: {list(info.keys())}"
            )

    @classmethod
    def decision_function(cls, X: float, Y: float, Z: float) -> float:
        """Return the raw SVM decision value.

        Parameters
        ----------
        X, Y, Z
            The three numerical descriptors used to train the SVM.
        """
        return (
            cls.COEF[0] * X
            + cls.COEF[1] * Y
            + cls.COEF[2] * Z
            + cls.INTERCEPT
        )

    @classmethod
    def predict(cls, X: float, Y: float, Z: float) -> bool:
        """Predict whether a material is superionic.

        Return True when the decision value is positive.
        """
        return cls.decision_function(X, Y, Z) > 0

    @classmethod
    def predict_from_atoms(cls, atoms) -> bool:
        """Predict superionicity from an ASE Atoms object.

        If ``atoms.info`` does not contain the required keys, they are
        automatically populated from the internal database
        (:mod:`data.data`) and ASE atomic masses.  A is always the
        element with the **smaller atomic number**.
        """
        try:
            from ase.data import atomic_masses, chemical_symbols
        except ImportError as exc:
            raise RuntimeError(
                "ASE is required for classification. Please install: pip install ase"
            ) from exc

        from data.element_properties import CHI_0GPA, ETA_0GPA

        symbols = list(set(atoms.get_chemical_symbols()))
        if len(symbols) != 2:
            raise ValueError(
                f"Only binary compounds are supported, got {len(symbols)} elements: {symbols}"
            )

        # Order by atomic number: A = smaller Z, B = larger Z
        z_nums = [chemical_symbols.index(s) for s in symbols]
        (z_A, sym_A), (z_B, sym_B) = sorted(
            zip(z_nums, symbols), key=lambda pair: pair[0]
        )

        info = atoms.info if atoms.info is not None else {}

        def _get(key: str, fallback: float) -> float:
            return float(info.get(key, fallback))

        chi_A = _get("chi_A", CHI_0GPA[sym_A])
        chi_B = _get("chi_B", CHI_0GPA[sym_B])
        eta_A = _get("eta_A", ETA_0GPA[sym_A])
        eta_B = _get("eta_B", ETA_0GPA[sym_B])
        m_A = _get("m_A", atomic_masses[z_A])
        m_B = _get("m_B", atomic_masses[z_B])

        # Write back to atoms.info if it was originally empty
        if not info:
            atoms.info = {
                "chi_A": chi_A,
                "chi_B": chi_B,
                "eta_A": eta_A,
                "eta_B": eta_B,
                "m_A": m_A,
                "m_B": m_B,
            }

        X = (abs(chi_A - chi_B) * m_A / m_B) ** 2
        Y = 1.0 / abs(eta_A - eta_B)
        Z = (m_B / m_A) ** 0.5
        return cls.predict(X, Y, Z)

    @classmethod
    def predict_from_xyz(cls, xyz_path: str | Path) -> None:
        """Read an XYZ file and predict superionicity for each frame.

        Frames are written to ``superionic.xyz`` or ``non_superionic.xyz``
        depending on the prediction.
        """
        superionic = []
        non_superionic = []
        for atoms in read(str(xyz_path), ":"):
            if cls.predict_from_atoms(atoms):
                superionic.append(atoms)
            else:
                non_superionic.append(atoms)

        write("superionic.xyz", superionic)
        write("non_superionic.xyz", non_superionic)
