from src.example_local import _call_csv_generator, _call_obfuscator

import pytest

test_good_data = "id,First Name,Last Name,Age\n1,aaa,aaa,20\n"
test_good_columns = ["id", "First Name", "Last Name", "Age"]


class TestCallCSVGenerator:
    def test_function_raises_exception_if_not_csv_extension(self, dummy_file):
        bad_file = str(dummy_file[0]).replace("csv", "xls")
        dummy_file[0].write_text(test_good_data)

        with pytest.raises(Exception) as e:
            _call_csv_generator(bad_file)
        assert "Target file is not .csv extension" in str(e.value)

    def test_function_returns_file_data_on_success(self, dummy_file, capsys):
        _call_csv_generator(str(dummy_file[0]))
        capture = capsys.readouterr()
        check = capture.out.split("\n")
        assert f'File at "{str(dummy_file[0])}" generated in' in check[0]

        check_float = 0.0
        for x in check[0].split(" "):
            try:
                check_float = float(x)
            except ValueError:
                continue

        assert check_float > 0.0
        assert "File creation date:" in check[1]
        assert "File last modified:" in check[2]
        assert "File size" == check[3].rsplit(":", 1)[0]
        assert int(check[3].rsplit(":", 1)[1]) >= 1_000_000


class TestCallObfuscator:
    def test_function_aborts_on_invalid_filepath(self, dummy_file):
        bad_file = str(dummy_file[0]).replace("csv", "xls")
        dummy_file[0].write_text(test_good_data)

        with pytest.raises(Exception) as e:
            _call_obfuscator(test_good_columns, bad_file)
        assert f"File is unreadable" in str(e.value)

    def test_function_returns_file_data_on_success(self, dummy_file, capsys):
        dummy_file[0].write_text(test_good_data)

        _call_obfuscator(test_good_columns, str(dummy_file[0]))
        capture = capsys.readouterr()
        check = capture.out.split("\n")
        while "Obfuscated file" not in check[0]:
            check.pop(0)

        check_f = str(dummy_file[0]).rsplit(".", 1)
        check_f = check_f[0] + "-obfuscated." + check_f[1]
        assert f'Obfuscated file at "{check_f}" generated in' in check[0]

        check_float = 0.0
        for x in check[0].split(" "):
            try:
                check_float = float(x)
            except ValueError:
                continue

        assert check_float > 0.0

        assert "Obfuscated file creation date:" in check[1]
        assert "Obfuscated file last modified:" in check[2]
        assert "Obfuscated file size" == check[3].rsplit(":", 1)[0]
        assert int(check[3].rsplit(":", 1)[1]) >= 0


