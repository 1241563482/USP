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


    def check_info(self, info: dict) -> bool:
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
    def predict_from_xyz(cls, xyz_path: str | Path) -> bool:
        """Read an XYZ file and predict superionicity for a binary compound.

        The XYZ file must be written by ASE with the following entries in
        ``atoms.info``:

            * chi_A, chi_B  - electronegativity
            * eta_A, eta_B  - chemical pressure
            * m_A, m_B      - effective atom mass, eg 12 for Carbon

        A and B are ordered such that A comes before B in the periodic table
        (e.g. for In-Li, A = Li, B = In).
        """

        superionic = []
        non_superionic = []
        for atoms in read(str(xyz_path), ":"):
            info = atoms.info
            cls.check_info(info)

            chi_A = float(info["chi_A"])
            chi_B = float(info["chi_B"])
            eta_A = float(info["eta_A"])
            eta_B = float(info["eta_B"])
            m_A = float(info["m_A"])
            m_B = float(info["m_B"])

            X = (abs(chi_A - chi_B) * m_A / m_B) ** 2
            Y = 1.0 / abs(eta_A - eta_B)
            Z = (m_B / m_A) ** 0.5
            if cls.predict(X, Y, Z):
                superionic.append(atoms)
            else:
                non_superionic.append(atoms)
        
        write("superionic.xyz", superionic)
        write("non_superionic.xyz", non_superionic)
