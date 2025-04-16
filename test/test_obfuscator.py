#from pytest import tmp_path
from src.obfuscator import filepath_validity

class TestFunctionFilepathValidity:
    def test_function_returns_false_if_input_is_not_string(self):
        arguments = [
                        int(20),
                        float(20.5),
                        complex(1j),
                        list(("list", "of", "strs")),
                        tuple(("tuple", "strs")),
                        range(5),
                        dict(path="./testfile.csv", format="csv"),
                        set(("set", "strs")),
                        frozenset(("set", "strs")),
                        bool(5),
                        bytes(5),
                        bytearray(5),
                        memoryview(bytes(5)),
                    ]

        for arg in arguments:
            assert filepath_validity(arg) is False

    def test_function_returns_true_if_filepath_is_readable(self, tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        p = d / "hello.txt"
        p.write_text("content", encoding="utf-8")

        assert filepath_validity(str(p)) is True
        assert p.read_text(encoding="utf-8") == "content"
        assert len(list(tmp_path.iterdir())) == 1
