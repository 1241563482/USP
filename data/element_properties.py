"""Elemental electronegativities (chi) and chemical hardnesses (eta) at 0 GPa.

Reference: Electronegativity and chemical hardness of elements under pressure, PNAS 2022 Vol. 119 No. 10 e2117416119

https://doi.org/10.1073/pnas.2117416119

"""

from ase.data import chemical_symbols

# fmt: off
_ELECTRONEGATIVITY_0GPA = [
    0.00,  # not used (index 0)
    4.32,  # H
    6.14,  # He
    0.06,  # Li
    1.42,  # Be
    1.60,  # B
    3.69,  # C
    4.38,  # N
    4.80,  # O
    7.31,  # F
    5.55,  # Ne
    -0.03, # Na
    0.78,  # Mg
    0.35,  # Al
    2.05,  # Si
    2.69,  # P
    3.31,  # S
    5.37,  # Cl
    4.58,  # Ar
    -0.99, # K
    0.04,  # Ca
    0.36,  # Sc
    0.55,  # Ti
    0.73,  # V
    0.91,  # Cr
    -0.21, # Mn
    1.35,  # Fe
    1.50,  # Co
    1.70,  # Ni
    1.31,  # Cu
    1.00,  # Zn
    0.15,  # Ga
    1.69,  # Ge
    2.49,  # As
    3.09,  # Se
    4.73,  # Br
    3.40,  # Kr
    -0.79, # Rb
    -0.18, # Sr
    0.28,  # Y
    0.56,  # Zr
    0.79,  # Nb
    0.90,  # Mo
    0.61,  # Tc
    0.92,  # Ru
    0.75,  # Rh
    1.72,  # Pd
    1.31,  # Ag
    0.83,  # Cd
    -0.22, # In
    1.27,  # Sn
    1.95,  # Sb
    2.58,  # Te
    3.82,  # I
    2.60,  # Xe
    -1.35, # Cs
    -0.36, # Ba
    0.08,  # La
    0.02,  # Ce
    0.11,  # Pr
    0.18,  # Nd
    0.30,  # Pm
    0.34,  # Sm
    0.34,  # Eu
    0.32,  # Gd
    0.27,  # Tb
    0.27,  # Dy
    0.15,  # Ho
    0.08,  # Er
    0.01,  # Tm
    -0.19, # Yb
    -0.24, # Lu
    0.37,  # Hf
    1.14,  # Ta
    1.62,  # W
    1.07,  # Re
    1.95,  # Os
    2.36,  # Ir
    2.83,  # Pt
    3.01,  # Au
    1.94,  # Hg
    0.07,  # Tl
    0.86,  # Pb
    1.22,  # Bi
    2.05,  # Po
    2.98,  # At
    1.86,  # Rn
    -0.86, # Fr
    -0.52, # Ra
    0.06,  # Ac
    0.49,  # Th
    -0.07, # Pa
    0.11,  # U
    -0.16, # Np
    -0.49, # Pu
    -0.35, # Am
    -0.21, # Cm
]

_CHEMICAL_HARDNESS_0GPA = [
    0.00,  # not used (index 0)
    6.21,  # H
    8.80,  # He
    2.23,  # Li
    4.59,  # Be
    3.80,  # B
    4.68,  # C
    7.06,  # N
    5.55,  # O
    6.14,  # F
    9.06,  # Ne
    2.06,  # Na
    3.98,  # Mg
    2.60,  # Al
    3.28,  # Si
    4.73,  # P
    3.83,  # S
    4.47,  # Cl
    7.74,  # Ar
    2.27,  # K
    3.19,  # Ca
    3.17,  # Sc
    2.93,  # Ti
    3.23,  # V
    3.37,  # Cr
    3.95,  # Mn
    3.62,  # Fe
    3.33,  # Co
    3.34,  # Ni
    3.82,  # Cu
    5.79,  # Zn
    3.00,  # Ga
    3.27,  # Ge
    4.53,  # As
    3.86,  # Se
    4.22,  # Br
    7.67,  # Kr
    1.90,  # Rb
    3.11,  # Sr
    3.14,  # Y
    2.87,  # Zr
    3.27,  # Nb
    3.51,  # Mo
    3.68,  # Tc
    3.70,  # Ru
    3.88,  # Rh
    4.07,  # Pd
    3.58,  # Ag
    5.40,  # Cd
    3.09,  # In
    3.09,  # Sn
    3.96,  # Sb
    3.62,  # Te
    3.78,  # I
    6.78,  # Xe
    1.80,  # Cs
    2.75,  # Ba
    2.35,  # La
    2.32,  # Ce
    2.55,  # Pr
    2.66,  # Nd
    2.55,  # Pm
    3.00,  # Sm
    3.04,  # Eu
    3.21,  # Gd
    3.17,  # Tb
    3.26,  # Dy
    3.32,  # Ho
    3.29,  # Er
    3.09,  # Tm
    3.46,  # Yb
    3.25,  # Lu
    3.77,  # Hf
    3.12,  # Ta
    3.58,  # W
    3.72,  # Re
    3.67,  # Os
    3.80,  # Ir
    3.51,  # Pt
    3.58,  # Au
    5.78,  # Hg
    3.09,  # Tl
    3.44,  # Pb
    3.33,  # Bi
    3.60,  # Po
    3.56,  # At
    6.05,  # Rn
    1.80,  # Fr
    3.02,  # Ra
    2.84,  # Ac
    2.77,  # Th
    3.14,  # Pa
    3.01,  # U
    3.11,  # Np
    3.46,  # Pu
    3.28,  # Am
    3.32,  # Cm
]
# fmt: on

_SYMBOLS = chemical_symbols[: len(_ELECTRONEGATIVITY_0GPA)]

CHI_0GPA: dict[str, float] = {
    sym: val for sym, val in zip(_SYMBOLS, _ELECTRONEGATIVITY_0GPA) if sym
}
"""Electronegativities (chi) at 0 GPa keyed by element symbol."""

ETA_0GPA: dict[str, float] = {
    sym: val for sym, val in zip(_SYMBOLS, _CHEMICAL_HARDNESS_0GPA) if sym
}
"""Chemical hardnesses (eta) at 0 GPa keyed by element symbol."""


def get_element_number(symbol: str) -> int | None:
    """Return the atomic number for an element symbol, or None if unknown."""
    try:
        return chemical_symbols.index(symbol)
    except ValueError:
        return None


def chi_eta_at_0GPa(symbol: str) -> tuple[float, float]:
    """Return (chi, eta) at 0 GPa for the given element symbol.

    Raises
    ------
    KeyError
        If the element symbol is not present in the dataset.
    """
    return CHI_0GPA[symbol], ETA_0GPA[symbol]


if __name__ == "__main__":
    print(chi_eta_at_0GPa("H"))
