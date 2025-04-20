from src.obfuscator import (
    _filepath_validity,
    _is_csv,
    _column_validity,
    _alter_data,
    obfuscate,
)

import pytest

test_good_data = "id,First Name,Last Name,Age\n1,aaa,aaa,20\n"
test_good_columns = ["id", "First Name", "Last Name", "Age"]


@pytest.fixture(scope="function")
def dummy_file(tmp_path, filename="dummydata.csv"):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / filename
    return [p, tmp_path, d, filename]


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
            assert _filepath_validity(arg) is False

    def test_function_returns_true_if_filepath_is_readable(self, dummy_file):
        dummy_file[0].write_text("content", encoding="utf-8")
        assert _filepath_validity(str(dummy_file[0])) is True
        assert dummy_file[0].read_text(encoding="utf-8") == "content"
        assert len(list(dummy_file[1].iterdir())) == 1

    def test_function_returns_error_if_filepath_is_unreadable(self, dummy_file):
        bad_file = str(dummy_file[0]).replace("csv", "xls")
        dummy_file[0].write_text(test_good_data)

        with pytest.raises(Exception):
            _filepath_validity(bad_file)


class TestFunctionIsCSV:
    def test_function_returns_false_on_invalid_file_extension(self):
        arguments = [
            "../dummydata.xls",
            "../dummydata.txt",
            "../dummydata.zip",
            "../dummydata.json",
        ]

        for arg in arguments:
            assert _is_csv(arg) is False

    def test_function_returns_false_on_invalid_csv_data(self, dummy_file):
        dummy_file[0].write_text(
            "id;firstname;lastname;age\n1;aaa;aaa;20\n2;bbb;bbb;21\n"
        )
        assert _is_csv(str(dummy_file[0])) is False

        dummy_file[0].write_text("id,firstname,lastname\n1,aaa,aaa,20")
        assert _is_csv(str(dummy_file[0])) is False

    def test_function_returns_true_if_data_valid(self, dummy_file):
        dummy_file[0].write_text(
            "id,firstname,lastname,age\n1,aaa,aaa,20\n2,bbb,bbb,21\n"
        )
        assert _is_csv(str(dummy_file[0])) is True

        dummy_file[0].write_text("id,First Name, Last Name, Age\n1,Adam,Ant,20\n")
        assert _is_csv(str(dummy_file[0])) is True

        dummy_file[0].write_text("id,first,last,age\n1,,,20\n")
        assert _is_csv(str(dummy_file[0])) is True


class TestFunctionColumnValidity:
    def test_function_returns_false_and_empty_list_if_input_columns_doesnt_match_data(
        self, dummy_file
    ):
        dummy_file[0].write_text(test_good_data)
        columns = ["id", "firstname", "lastname", "age"]
        assert _column_validity(columns, dummy_file[0]) == [False, []]

    def test_function_returns_true_and_column_indexes_if_input_matches(
        self, dummy_file
    ):
        dummy_file[0].write_text(test_good_data)
        assert _column_validity(test_good_columns, dummy_file[0]) == [
            True,
            [0, 1, 2, 3],
        ]


class TestFunctionAlterData:
    def test_function_creates_target_file_with_expected_path(self, dummy_file):
        dummy_file[0].write_text(test_good_data)
        target_path = _alter_data(test_good_columns, str(dummy_file[0]))
        target_path_check = target_path.rsplit("/", 1)
        assert target_path_check[1] == "dummydata-obfuscated.csv"

    def test_function_replaces_data_with_obfuscated_string(self, dummy_file):
        columns = [0, 1, 2, 3]

        for column in range(4):
            dummy_file[0].write_text(test_good_data)
            target_path = _alter_data([column], str(dummy_file[0]))
            with open(target_path, "r") as targetf:

                for x in range(2):
                    if x == 0:
                        targetf.readline()
                        continue
                    line = targetf.readline().split(",")
                    line[-1] = line[-1].replace("\n", "")
                    assert line[column] == "***"

    def test_function_doesnt_remove_line_break_when_obfuscating(self, dummy_file):
        dummy_file[0].write_text(test_good_data)
        target_path = _alter_data([3], str(dummy_file[0]))
        with open(target_path, "r") as targetf:
            for x in range(2):
                if x == 0:
                    targetf.readline()
                    continue
                line = targetf.readline()
                assert line[-1::] == "\n"


class TestObfuscate:
    def test_function_returns_false_if_filepath_invalid(self):
        assert obfuscate(test_good_columns, 90210) is False

    def test_function_returns_false_if_not_csv_extension(self, tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        p = d / "dummydata.xls"
        p.write_text(test_good_data)
        assert obfuscate(test_good_columns, str(p)) is False

    def test_function_returns_false_if_column_names_invalid(self, dummy_file):
        bad_columns = ["id", "firstname", "lastname", "Age"]
        dummy_file[0].write_text(test_good_data)
        assert obfuscate(bad_columns, str(dummy_file[0])) is False

    def test_function_returns_successfully_with_target_filepath(self, dummy_file):
        dummy_file[0].write_text(test_good_data)
        result = obfuscate(test_good_columns, str(dummy_file[0]))

        path_check = str(dummy_file[0]).rsplit(".", 1)
        path_check[1] = "-obfuscated." + path_check[1]
        path_check = "".join(path_check)

        assert result[0] == path_check
        assert (
            result[1]
            == f'Task Completed. Obfuscated data can be found in the file at "{path_check}"'
        )
