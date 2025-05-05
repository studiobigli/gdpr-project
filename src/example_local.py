from obfuscator import obfuscate
from src.fake_csv import fake_csv
from time import perf_counter

import io
import os
import sys
import inquirer
import shutil

"""
Sample program to demonstrate functionality of obfuscator.py

To run, ensure PYTHONPATH is set to the project directory. Then:

    python src/example_local.py FILE_PATH OBFUSCATED_PATH

FILE_PATH referring to your preferred destination for sample CSV and
OBFUSCATED_PATH for preffered destination for obfuscated CSV files.
"""

i_filepath = ""
o_filepath = ""

columns = [
    "First Name",
    "Last Name",
    "Street Address",
    "City",
    "Postcode",
    "Phone Number",
    "Date of Birth",
]


def _call_csv_generator(i_filepath):
    start = perf_counter()
    data_f = fake_csv(i_filepath)
    t = perf_counter() - start

    if os.path.isfile(data_f):
        print(f'File at "{data_f}" generated in {t:.6f} seconds')
        print(f"File creation date: {os.path.getctime(data_f)}")
        print(f"File last modified: {os.path.getmtime(data_f)}")
        print(f"File size: {os.path.getsize(data_f)}\n")

    return data_f


def _create_byte_stream(i_filepath):
    buf = io.BytesIO()
    with open(i_filepath, "rb") as sourcef:
        shutil.copyfileobj(sourcef, buf)
    buf.seek(0)
    return buf


def _call_obfuscator(columns, i_filepath, i_byte_stream, o_filepath=""):
    start = perf_counter()
    result = obfuscate(columns, i_byte_stream)
    if not o_filepath:
        o_filepath = i_filepath.rsplit(".", 1)
        o_filepath[0] += "-obfuscated."
        o_filepath = "".join(o_filepath)

    print(f'Writing to "{o_filepath}"...')

    with open(o_filepath, "wb") as output_f:
        output_f.write(result)

    t = perf_counter() - start

    if os.path.isfile(o_filepath):
        print(
            'Obfuscated file at "{}" generated in {:.6f} seconds'
            .format(o_filepath, t)
        )
        print(f"Obfuscated file creation date: {os.path.getctime(o_filepath)}")
        print(f"Obfuscated file last modified: {os.path.getmtime(o_filepath)}")
        print(f"Obfuscated file size: {os.path.getsize(o_filepath)}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        i_filepath = sys.argv[1]
        o_filepath = sys.argv[2]

    data_f = _call_csv_generator(i_filepath)

    data_columns = []
    with open(data_f, "r") as f:
        check = f.readline().split(",")
        check[-1] = check[-1].replace("\n", "")

        questions = [
            inquirer.Checkbox(
                "columns",
                message="Which columns do you wish to obfuscate?",
                choices=check,
                carousel=True,
            )
        ]
        columns = inquirer.prompt(questions)["columns"]
        if not columns:
            print("No columns selected, aborting...")
            sys.exit()

        byte_stream = _create_byte_stream(data_f)

        _call_obfuscator(columns, i_filepath, byte_stream, o_filepath)
