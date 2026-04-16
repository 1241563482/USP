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


def test_dummy_components(monkeypatch, tmp_path):
    provider = MaterialsProjectClient(api_key="TESTTESTTESTTESTTESTTESTTESTTEST")
    # monkeypatch get_structure to avoid network
    provider.get_structure = lambda x: Structure([[1,0,0],[0,1,0],[0,0,1]], ["H","H","H"], [[0,0,0],[0,0,0],[0,0,0]])
    # avoid requiring mace/ase in the test environment
    monkeypatch.setattr("usp.optimizer.MACEOptimizer._relax_atoms", lambda self, atoms: atoms)
    optimizer = MACEOptimizer()
    dft_calc = DummyDFTCalculator()
    input_file = tmp_path / "in.csv"
    input_file.write_text("id\nmp-1\n")
    results = run_workflow(str(input_file), provider, optimizer, dft_calc)
    assert results[0]["id"] == "mp-1"
    assert results[0]["result"]["energy"] is None


def test_provider_element_search_requires_mpapi(monkeypatch):
    # when _mpapi is unavailable, element search should raise RuntimeError
    provider = MaterialsProjectClient(api_key="TESTTESTTESTTESTTESTTESTTESTTEST")
    provider._mpapi = None
    with pytest.raises(RuntimeError, match="mp-api"):
        provider.get_structures_by_elements(["Li", "In"])


def test_provider_element_search_with_mpapi(monkeypatch):
    # verify the mp_api code path if someone happens to have the package
    provider = MaterialsProjectClient(api_key="TESTTESTTESTTESTTESTTESTTESTTEST")
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
            assert api_key == "TESTTESTTESTTESTTESTTESTTESTTEST"
        def download_structures_by_elements(self, elements, out_dir=".", fmt="vasp"):
            # ensure elements passed correctly and write a trivial file
            assert elements == ["Li", "In"]
            import os
            from pymatgen.core import Structure
            from pymatgen.io.vasp import Poscar
            os.makedirs(out_dir, exist_ok=True)
            struct = Structure([[1, 0, 0], [0, 1, 0], [0, 0, 1]], ["H"], [[0, 0, 0]])
            Poscar(struct).write_file(f"{out_dir}/mp-1.vasp")
            return ["mp-1"]
    monkeypatch.setattr("usp.main.MaterialsProjectClient", DummyProv)
    monkeypatch.setattr("usp.main.MACEOptimizer", lambda *args, **kwargs: None)
    monkeypatch.setattr("usp.main.DummyDFTCalculator", lambda *args, **kwargs: None)
    monkeypatch.setattr("usp.main._read_mp_api_key_from_bashrc", lambda: "TESTTESTTESTTESTTESTTESTTESTTEST")

    outdir = tmp_path / "out"
    monkeypatch.setattr("sys.argv", ["usp", "--mp", "Li", "In", "--output-dir", str(outdir)])
    from usp.main import main
    main()
    # verify the VASP file was created
    assert (outdir / "mp-1.vasp").exists()


def test_cli_mp_api_key_check_found(monkeypatch, capsys):
    monkeypatch.setattr("usp.main._read_mp_api_key_from_bashrc", lambda: "TEST_KEY")
    monkeypatch.setattr("sys.argv", ["usp", "--mp-api-key"])
    from usp.main import main
    main()
    captured = capsys.readouterr()
    assert "ok" in captured.out


def test_cli_mp_api_key_check_not_found(monkeypatch, capsys):
    monkeypatch.setattr("usp.main._read_mp_api_key_from_bashrc", lambda: None)
    monkeypatch.setattr("sys.argv", ["usp", "--mp-api-key"])
    from usp.main import main
    main()
    captured = capsys.readouterr()
    assert "usp --mp-api-key <YOUR_KEY>" in captured.out


def test_cli_mp_api_key_set(monkeypatch, capsys, tmp_path):
    fake_bashrc = tmp_path / ".bashrc"
    monkeypatch.setattr("usp.main.BASHRC_PATH", str(fake_bashrc))
    monkeypatch.setattr("sys.argv", ["usp", "--mp-api-key", "NEW_KEY"])
    from usp.main import main
    main()
    captured = capsys.readouterr()
    assert "ok" in captured.out
    content = fake_bashrc.read_text()
    assert 'export MP_API_KEY="NEW_KEY"' in content


def test_cli_mp_api_key_set_replace(monkeypatch, capsys, tmp_path):
    fake_bashrc = tmp_path / ".bashrc"
    fake_bashrc.write_text('export MP_API_KEY="OLD_KEY"\n')
    monkeypatch.setattr("usp.main.BASHRC_PATH", str(fake_bashrc))
    monkeypatch.setattr("sys.argv", ["usp", "--mp-api-key", "NEW_KEY"])
    from usp.main import main
    main()
    content = fake_bashrc.read_text()
    assert 'export MP_API_KEY="NEW_KEY"' in content
    assert "OLD_KEY" not in content
