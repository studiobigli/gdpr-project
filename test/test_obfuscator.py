from src.obfuscator import (
    _is_csv,
    _column_validity,
    _alter_data,
    obfuscate,
)

import pytest
import shutil
import io

test_good_data = "id,First Name,Last Name,Age\n1,aaa,aaa,20\n2,bbb,bbb,302"
test_good_columns = ["id", "First Name", "Last Name", "Age"]

class Bytestream(io.BytesIO):
    def __init__(self, i_filepath):
        io.BytesIO.__init__(self)
        self.buf = io.BytesIO()
        with open(i_filepath, 'rb') as sourcef:
            shutil.copyfileobj(sourcef, self.buf)
        self.buf.seek(0)


class TestFunctionIsCSV:
    def test_function_returns_false_on_invalid_csv_data(self, dummy_file):
        dummy_file[0].write_text(
            "id;firstname;lastname;age\n1;aaa;aaa;20\n2;bbb;bbb;21\n"
        )
        stream = Bytestream(str(dummy_file[0]))
        assert _is_csv(stream.buf) is False
        stream.close()

        dummy_file[0].write_text("id,firstname,lastname\n1,aaa,aaa,20")
        stream = Bytestream(str(dummy_file[0]))
        assert _is_csv(stream.buf) is False
        stream.close()

    def test_function_returns_true_if_data_valid(self, dummy_file):
        dummy_file[0].write_text(
            "id,firstname,lastname,age\n1,aaa,aaa,20\n2,bbb,bbb,21\n"
        )
        stream = Bytestream(str(dummy_file[0]))
        assert _is_csv(stream.buf) is True
        stream.close()

        dummy_file[0].write_text("id,First Name, Last Name, Age\n1,Adam,Ant,20\n")
        stream = Bytestream(str(dummy_file[0]))
        assert _is_csv(stream.buf) is True
        stream.close()

        dummy_file[0].write_text("id,first,last,age\n1,,,20\n")
        stream = Bytestream(str(dummy_file[0]))
        assert _is_csv(stream.buf) is True
        stream.close()

class TestFunctionColumnValidity:
    def test_function_returns_false_and_empty_list_if_input_columns_doesnt_match_data(
        self, dummy_file
    ):
        dummy_file[0].write_text(test_good_data)
        columns = ["id", "firstname", "lastname", "age"]
        stream = Bytestream(str(dummy_file[0]))
        assert _column_validity(columns, stream.buf) == [False, []]
        stream.close()

    def test_function_returns_true_and_column_indexes_if_input_matches(
        self, dummy_file
    ):
        dummy_file[0].write_text(test_good_data)
        stream = Bytestream(str(dummy_file[0]))
        assert _column_validity(test_good_columns, stream.buf) == [
            True,
            [0, 1, 2, 3],
        ]
        stream.close()


class TestFunctionAlterData:
    def test_function_creates_readable_byte_stream(self, dummy_file):
        dummy_file[0].write_text(test_good_data)
        stream = Bytestream(str(dummy_file[0]))
        result = _alter_data(test_good_columns, stream.buf)
        stream.close()

        assert isinstance(result, bytes)
        assert result.decode("utf-8") == test_good_data

    def test_function_replaces_data_with_obfuscated_string(
        self, dummy_file, dummy_output_file
    ):
        columns = [0, 1, 2, 3]

        for column in range(4):
            dummy_file[0].write_text(test_good_data)
            stream = Bytestream(str(dummy_file[0]))
            result = _alter_data([column], stream.buf)
            with open(str(dummy_output_file[0]), "wb") as output_f:
                output_f.write(result)

            with open(str(dummy_output_file[0]), "r") as targetf:

                for x in range(2):
                    if x == 0:
                        targetf.readline()
                        continue
                    line = targetf.readline().split(",")
                    line[-1] = line[-1].replace("\n", "")
                    assert line[column] == "***"


class TestObfuscate:
    def test_function_returns_false_if_column_names_invalid(self, dummy_file):
        bad_columns = ["id", "firstname", "lastname", "Age"]
        dummy_file[0].write_text(test_good_data)
        stream = Bytestream(str(dummy_file[0]))
        assert obfuscate(bad_columns, stream.buf) is False
        stream.close()
