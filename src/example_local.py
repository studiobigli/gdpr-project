from src.obfuscator import obfuscate
from src.fake_csv import fake_csv
from time import perf_counter

import os
import sys


"""
Sample program to demonstrate functionality of obfuscator.py

Import obfuscate function from obfuscator.py
Import fake_csv function from fake_csv.py

Pass a filepath to the variable filepath in the fake_csv function
Report file info of generated csv

Pass the output of fake_csv to obfuscate
Time how long the obfuscate function takes to complete
Report file info of resulting csv
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
    fake_csv(filepath)
    t = perf_counter() - start

    if os.path.isfile(filepath):
        print(f'File at "{filepath}" generated in {t:.6f} seconds')
        print(f"File creation date: {os.path.getctime(filepath)}")
        print(f"File last modified: {os.path.getmtime(filepath)}")
        print(f"File size: {os.path.getsize(filepath)}")
    

def _call_obfuscator(columns, filepath):
    start = perf_counter()
    result = obfuscate(columns, filepath)
    t = perf_counter() - start

    if os.path.isfile(result[0]):
        print(f'Obfuscated file at "{result[0]}" generated in {t:.6f} seconds')
        print(f"Obfuscated file creation date: {os.path.getctime(result[0])}")
        print(f"Obfuscated file last modified: {os.path.getmtime(result[0])}")
        print(f"Obfuscated file size: {os.path.getsize(result[0])}")
    else:
        raise Exception(f'File{result[0]} does not exist, aborting')
        #sys.exit(f"File {result[0]} does not exist, aborting")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    _call_csv_generator(filepath)
    _call_obfuscator(columns, filepath)
