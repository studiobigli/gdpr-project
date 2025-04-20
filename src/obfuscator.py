import os
import csv
import string


def _filepath_validity(filepath):
    if not isinstance(filepath, str) or not filepath:
        print(f'Filepath "{filepath}" is invalid, is of type {type(filepath)}')
        return False

    if os.access(filepath, os.R_OK) is True:
        print(f'Filepath "{filepath}" is readable...')
        return True
    else:
        print(os.access(filepath, os.R_OK))
        raise Exception("File is unreadable")


def _is_csv(filepath):
    print(f"Checking {filepath}...")
    if filepath.rsplit(".", 1)[1] != "csv":
        print(f'File "{filepath}" is not .csv')
        return False

    try:
        with open(filepath, newline="\n") as file:
            check = file.read(8192)

            dialect = csv.Sniffer().sniff(check)

            # Consider checking more details of the CSV dialect to prevent issues
            if dialect.delimiter != ",":
                print("Dialect delimiter incorrect")
                return False

            return True

    except csv.Error:
        print(f"File does not appear to contain correct .csv data")
        return False


def _column_validity(columns, filepath):
    with open(filepath, "r") as file:
        check = file.readline().split(",")
        check[-1] = check[-1].replace("\n", "")

    for x in columns:
        if x not in check:
            print(f"Column {x} not in CSV file, aborting.")
            return [False, []]

    column_idx = [idx for idx, x in enumerate(check) if x in columns]

    return [True, column_idx]


def _alter_data(column_idx, filepath):

    target_path = filepath.rsplit(".", 1)
    target_path[0] += "-obfuscated."
    target_path = "".join(target_path)
    print(f'Writing to "{target_path}"...')

    with open(filepath, "r") as sourcef:
        doc_length = sourcef.readlines()

    with open(filepath, "r") as sourcef:
        with open(target_path, "w") as targetf:

            for line in range(len(doc_length)):
                if line == 0:
                    targetf.write(sourcef.readline())
                    continue
                source_line = sourcef.readline().split(",")
                source_line[-1].replace("\n", "")

                for idx, x in enumerate(source_line):
                    if idx in column_idx:
                        source_line[idx] = "***"

                targetf.write(",".join(source_line) + "\n")

    return target_path


def obfuscate(columns, filepath):
    """
    Takes the data from a CSV file and a list of column names and replaces the
    data under those columns with the string '***'. The data is then stored in
    another CSV file, with '-obfuscated' appended to the filename before the
    file extension.

    Parameters:
    columns (list of str): A list containing the names of columns whose data
    should be obfuscated.
    filepath (str): A string containing the filepath of the CSV file to be
    processed.

    Returns:
    list of str: First string is the filepath of the CSV with the obfuscated
    data. Second string is a confirmation of this filepath location.
    """

    if not _filepath_validity(filepath):
        return False

    if not _is_csv(filepath):
        return False

    columns = _column_validity(columns, filepath)
    if columns[0] is False:
        return False

    endfile = _alter_data(columns[1], filepath)
    return [
        endfile,
        f'Task Completed. Obfuscated data can be found in the file at "{endfile}"',
    ]
