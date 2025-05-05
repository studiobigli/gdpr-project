import csv
import io


def _is_csv(i_data):
    print(f"Checking {i_data}...")

    try:
        check = i_data.read(8192)
        i_data.seek(0)
        check = check.decode("utf-8")
        dialect = csv.Sniffer().sniff(check)

        if dialect.delimiter != ",":
            print("Dialect delimiter incorrect")
            return False

        return True

    except csv.Error:
        print("File does not appear to contain correct .csv data")
        return False


def _column_validity(columns, i_data):
    print(i_data)
    i_data.seek(0)
    check = i_data.readline().decode("utf-8").split(",")
    check[-1] = check[-1].replace("\r\n", "").replace("\n", "")

    for x in columns:
        if x not in check:
            print(x, check)
            print(f"Column {x} not in CSV file, aborting.")
            return [False, []]

    column_idx = [idx for idx, x in enumerate(check) if x in columns]

    return [True, column_idx]


def _alter_data(column_idx, i_data):
    i_data.seek(0)
    doc_length = i_data.readlines()
    i_data.seek(0)

    with io.BytesIO() as targetf:
        for line in range(len(doc_length)):
            if line == 0:
                targetf.write(
                    bytes(i_data.readline().decode("utf-8"), "utf-8")
                )

            source_line = i_data.readline().decode("utf-8").split(",")
            source_line[-1].replace("\n", "")

            for idx, x in enumerate(source_line):
                if idx in column_idx:
                    if source_line[idx] is source_line[-1]:
                        source_line[idx] = "***\n"
                    else:
                        source_line[idx] = "***"

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

    Returns:
    endfile (byte stream): A byte stream containing the obfuscated CSV data
    ready for the calling python script to handle as the user sees fit.
    """

    if not _is_csv(i_filepath):
        return False

    columns = _column_validity(columns, i_filepath)
    if columns[0] is False:
        return False

    endfile = _alter_data(columns[1], i_filepath)

    return endfile
