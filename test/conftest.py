import pytest

@pytest.fixture(scope="function")
def dummy_file(tmp_path, filename="dummydata.csv"):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / filename
    return [p, tmp_path, d, filename]
