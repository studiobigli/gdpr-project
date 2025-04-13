import os
import csv
import string

# Obfuscator module
# Requires an input of a string containing the source filename.
# Requires a list of strings containing column names whose data requires obfuscation.
# Returns a byte-stream object suitable for handling however the user chooses.

def filepath_validity(filepath):
    if not isinstance(filepath, str) or not filepath:
        print(f'Filepath \"{filepath}\" is invalid')
        return False

    if os.access(filepath, os.R_OK):
        print(f'Filepath \"{filepath}\" is readable...')
        return True

def is_csv(filepath):
    if filepath.rsplit(".", 1)[1] != "csv":
        print(f'File is not .csv')
        return False    
    
    try:
        with open(filepath, newline='\n') as file:
            check = file.read(8192)

            if not all([x in string.printable or x.isprintable() for x in check]):
                return False
            
            dialect = csv.Sniffer().sniff(check)
            return True
    
    except csv.Error:
        print(f'File does not appear to contain correct .csv data')
        return False


def column_validity(columns, filepath):
    with open(filepath, "r", newline='') as file:
        check = file.readline().split(",")
    
    print(f'{check=}')
    for x in columns:
        if x not in check:
            print(f'Column {x} not in CSV file, aborting.')
            return [False, []]
    
    column_idx = [idx for idx,x in enumerate(check) if x in columns]

    return [True, column_idx]

def alter_data(column_idx, filepath):
    

    target_path = filepath.rsplit(".", 1)
    target_path[0] += "-obfuscated."
    target_path = target_path.join()
    print(f'Writing to {target_path}...')

    with open(filepath, "r") as sourcef:
        with open(target_path, "w") as targetf:
            for line in sourcef:
                source_line = sourcef.readline().split(",")
            
                for idx, x in enumerate(source_line):
                    if idx in column_idx:
                        x = "***"

                targetf.write(source_line)

def obfuscate(columns, filepath):
    if not filepath_validity(filepath):
        return False

    if not is_csv(filepath):
        return False

    columns = column_validity(columns, filepath)
    if columns[0] is False:
        return False

    alter_data(columns[1], filepath)
    return True

if __name__ == "__main__":
    columns = ["first_name", "last_name"]
    filepath = "../dummydata.csv"
    print(obfuscate(columns, filepath))
