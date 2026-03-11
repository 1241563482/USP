import pytest
from usp import __version__
from usp.input import read_csv, read_json
from usp.api import MaterialsProjectClient, StructureProvider
from usp.optimizer import Optimizer, MACEOptimizer
from usp.dft import DFTCalculator, DummyDFTCalculator
from usp.workflow import run_workflow
from pymatgen.core import Structure


def test_version():
    assert __version__ == "0.1.0"


def test_input_parsers(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id\nmp-1\n")
    data = read_csv(str(csv_file))
    assert data[0]["id"] == "mp-1"

    json_file = tmp_path / "data.json"
    json_file.write_text("[{\"id\": \"mp-2\"}]")
    data = read_json(str(json_file))
    assert data[0]["id"] == "mp-2"


def test_base_classes():
    with pytest.raises(TypeError):
        Optimizer()
    with pytest.raises(TypeError):
        DFTCalculator()
    with pytest.raises(TypeError):
        StructureProvider()


def test_dummy_components(tmp_path):
    provider = MaterialsProjectClient(api_key="TEST")
    # monkeypatch get_structure to avoid network
    provider.get_structure = lambda x: Structure([[0,0,0],[1,1,1],[2,2,2]], ["H","H","H"])
    optimizer = MACEOptimizer()
    dft_calc = DummyDFTCalculator()
    input_file = tmp_path / "in.csv"
    input_file.write_text("id\nmp-1\n")
    results = run_workflow(str(input_file), provider, optimizer, dft_calc)
    assert results[0]["id"] == "mp-1"
    assert results[0]["result"]["energy"] is None


def test_provider_element_search(monkeypatch):
    provider = MaterialsProjectClient(api_key="TEST")
    # fake returned documents from whichever backend is used; force the
    # pymatgen branch by clearing _mpapi so tests don't require mp_api
    provider._mpapi = None
    fake_docs = [
        {"material_id": "mp-1", "structure": "S1"},
        {"material_id": "mp-2", "structure": "S2"},
    ]
    monkeypatch.setattr(provider._mpr, "query", lambda crit, props: fake_docs)
    entries = provider.get_structures_by_elements(["Li", "In"])
    assert entries == [("mp-1", "S1"), ("mp-2", "S2")]


def test_provider_element_search_with_mpapi(monkeypatch):
    # verify the mp_api code path if someone happens to have the package
    provider = MaterialsProjectClient(api_key="TEST")
    # inject a fake _mpapi object with the minimal interface
    class FakeDoc:
        def __init__(self, mid, struct):
            self.material_id = mid
            self.structure = struct
    fake_docs = [FakeDoc("mp-3", "S3")]
    provider._mpapi = type("X", (), {})()
    provider._mpapi.materials = type("Y", (), {})()
    provider._mpapi.materials.summary = type("Z", (), {})()
    provider._mpapi.materials.summary.search = lambda **kwargs: fake_docs
    entries = provider.get_structures_by_elements(["Fe", "O"])
    assert entries == [("mp-3", "S3")]


def test_cli_mp_search(monkeypatch, tmp_path):
    # dummy provider returns a real pymatgen Structure so CIF writing works
    class DummyProv:
        def __init__(self, api_key):
            assert api_key == "TEST"
        def download_structures_by_elements(self, elements, out_dir="."):
            # ensure elements passed correctly and write a trivial cif
            assert elements == ["Li", "In"]
            from pymatgen.core import Structure
            from pymatgen.io.cif import CifWriter
            struct = Structure([[0, 0, 0]], ["H"])
            CifWriter(struct).write_file(f"{out_dir}/mp-1.cif")
            return ["mp-1"]
    monkeypatch.setattr("usp.main.MaterialsProjectClient", DummyProv)
    monkeypatch.setattr("usp.main.MACEOptimizer", lambda: None)
    monkeypatch.setattr("usp.main.DummyDFTCalculator", lambda: None)
    monkeypatch.setenv("MP_API_KEY", "TEST")

    outdir = tmp_path / "out"
    monkeypatch.setattr("sys.argv", ["usp", "--mp", "Li", "In", "--mp-api-key", "TEST", "--output-dir", str(outdir)])
    from usp.main import main
    main()
    # verify the CIF file was created
    assert (outdir / "mp-1.cif").exists()
