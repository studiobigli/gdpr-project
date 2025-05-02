import os
import csv
import string
import io


def _filepath_validity(i_filepath):
    if not isinstance(i_filepath, str) or not i_filepath:
        print(
            f'Input filepath "{i_filepath}" is invalid, is of type {type(i_filepath)}'
        )
        return False

    if os.access(i_filepath, os.R_OK) is True:
        print(f'Input filepath "{i_filepath}" is readable...')
        return True
    else:
        print(os.access(i_filepath, os.R_OK))
        raise Exception("File is unreadable")


def _is_csv(i_filepath):
    print(f"Checking {i_filepath}...")
    if i_filepath.rsplit(".", 1)[1] != "csv":
        print(f'File "{i_filepath}" is not .csv')
        return False

    try:
        with open(i_filepath, newline="\n") as file:
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


def _column_validity(columns, i_filepath):
    with open(i_filepath, "r") as file:
        check = file.readline().split(",")
        check[-1] = check[-1].replace("\n", "")

    for x in columns:
        if x not in check:
            print(f"Column {x} not in CSV file, aborting.")
            return [False, []]

    column_idx = [idx for idx, x in enumerate(check) if x in columns]

    return [True, column_idx]


def _alter_data(column_idx, i_filepath):
    with open(i_filepath, "r") as sourcef:
        doc_length = sourcef.readlines()

    with open(i_filepath, "r") as sourcef:
        with io.BytesIO() as targetf:
            for line in range(len(doc_length)):
                if line == 0:
                    targetf.write(bytes(sourcef.readline(), "utf-8"))
                    continue
                source_line = sourcef.readline().split(",")
                source_line[-1].replace("\n", "")

                for idx, x in enumerate(source_line):
                    if idx in column_idx:
                        if source_line[idx] is source_line[-1]:
                            source_line[idx] = "***\n"
                        else:
                            source_line[idx] = "***"
                    # if source_line[-1] == "***":
                    # source_line[-1] = "***\n"

                targetf.write(bytes(",".join(source_line), "utf-8"))

            targetf.seek(0)
            return targetf.getvalue()


def obfuscate(columns, i_filepath):
    """
    Takes the data from a CSV file and a list of column names and replaces the
    data under those columns with the string '***'. The data is then stored in
    another CSV file, with '-obfuscated' appended to the filename before the
    file extension.

    Parameters:
    columns (list of str): A list containing the names of columns whose data
    should be obfuscated.
    i_filepath (str): A string containing the filepath of the CSV file to be
    processed.
    o_filepath (str): A string containing the intended destination of the obfuscated CSV file.

    Returns: (CHANGE)
    list of str: First string is the i_filepath of the CSV with the obfuscated
    data. Second string is a confirmation of this i_filepath location.
    """

    if not _filepath_validity(i_filepath):
        return False

    if not _is_csv(i_filepath):
        return False

    columns = _column_validity(columns, i_filepath)
    if columns[0] is False:
        return False

    endfile = _alter_data(columns[1], i_filepath)
    # return [
    #    endfile,
    #    f'Task Completed. Obfuscated data can be found in the file at "{endfile}"',
    # ]

    return endfile
