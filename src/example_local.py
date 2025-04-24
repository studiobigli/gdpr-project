from src.obfuscator import obfuscate
from src.fake_csv import fake_csv
from time import perf_counter

import os
import sys


"""
Sample program to demonstrate functionality of obfuscator.py

To run, ensure PYTHONPATH is set to the project directory. Then:

    python src/example_local.py FILEPATH

FILEPATH referring to your preferred destination for sample CSV and
obfuscated CSV files.
"""

filepath = ""
columns = [
    "First Name",
    "Last Name",
    "Street Address",
    "City",
    "Postcode",
    "Phone Number",
    "Date of Birth",
]


def _call_csv_generator(filepath):
    start = perf_counter()
    data_f = fake_csv(filepath)
    t = perf_counter() - start

    if os.path.isfile(data_f):
        print(f'File at "{data_f}" generated in {t:.6f} seconds')
        print(f"File creation date: {os.path.getctime(data_f)}")
        print(f"File last modified: {os.path.getmtime(data_f)}")
        print(f"File size: {os.path.getsize(data_f)}\n")

    return data_f


def _call_obfuscator(columns, filepath):
    start = perf_counter()
    result = obfuscate(columns, filepath)
    t = perf_counter() - start

    if os.path.isfile(result[0]):
        print(f'Obfuscated file at "{result[0]}" generated in {t:.6f} seconds')
        print(f"Obfuscated file creation date: {os.path.getctime(result[0])}")
        print(f"Obfuscated file last modified: {os.path.getmtime(result[0])}")
        print(f"Obfuscated file size: {os.path.getsize(result[0])}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    data_f = _call_csv_generator(filepath)
    _call_obfuscator(columns, data_f)
