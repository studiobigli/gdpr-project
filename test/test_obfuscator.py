from src.obfuscator import filepath_validity, is_csv, column_validity


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


class TestFunctionIsCSV:
    def test_function_returns_false_on_invalid_file_extension(self):
        arguments = [
            "../dummydata.xls",
            "../dummydata.txt",
            "../dummydata.zip",
            "../dummydata.json",
        ]

        for arg in arguments:
            assert is_csv(arg) is False

    def test_function_returns_false_on_invalid_csv_data(self, tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        p = d / "testdata.csv"
        p.write_text("id;firstname;lastname;age\n1;aaa;aaa;20\n2;bbb;bbb;21\n")
        assert is_csv(str(p)) is False

        p.write_text("id,firstname,lastname\n1,aaa,aaa,20")
        assert is_csv(str(p)) is False

    def test_function_returns_true_if_data_valid(self, tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        p = d / "testdata.csv"
        p.write_text("id,firstname,lastname,age\n1,aaa,aaa,20\n2,bbb,bbb,21\n")
        assert is_csv(str(p)) is True

        p.write_text("id,First Name, Last Name, Age\n1,Adam,Ant,20\n")
        assert is_csv(str(p)) is True

        p.write_text("id,first,last,age\n1,,,20\n")
        assert is_csv(str(p)) is True


class TestFunctionColumnValidity:
    def test_function_returns_false_and_empty_list_if_input_columns_doesnt_match_data(
        self, tmp_path
    ):
        p = tmp_path / "dummydata.csv"
        p.write_text("id,First Name,Last Name,Age\n1,aaa,aaa,20\n")
        columns = ["id", "firstname", "lastname", "age"]
        assert column_validity(columns, p) == [False, []]

    def test_function_returns_true_and_column_indexes_if_input_matches(self, tmp_path):
        p = tmp_path / "dummydata.csv"
        p.write_text("id,First Name,Last Name,Age\n1,aaa,aaa,20\n")
        columns = ["id", "First Name", "Last Name", "Age"]
        assert column_validity(columns, p) == [True, [0, 1, 2, 3]]
