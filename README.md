
# GDPR Obfuscator library for Python Project

A simple Python library that takes a byte stream of a CSV file a list of column names of which whose data will be obfuscated with a string of "***". The library returns the data as a byte stream ready for further data manipulation by the user.

The library has been tested as an imported module for a local Python script, as well as deployed as a layer for use by an AWS Lambda.

## Getting Started
### Prerequisites

It is required to have the following installed and configured as per your use case:

- Python >=3.12
- Terraform
- AWS CLI (supply credentials with aws configure)
- An AWS account, with privileges to create IAM roles, policies, S3 buckets, Lambdas, layers, Cloudwatch

### Installation

Open a terminal and clone the repo with the following command:
```
https://github.com/studiobigli/gdpr-project.git
```

A Makefile can be called to create the virtual environment and install dependencies with (from the root folder of the project):
```
make all
```

This will run the unit testing, check for security vulnerabilities in the code and any dependencies, and check for any issues with PEP8 compliance using Flake8.

For deploying the AWS Infrastructure with Terraform, you are required to replace values in the included terraform/example.tfbackend and terraform/example.tfvars files. 
In example.tfvars, choose a suitable prefix for your S3 buckets (I suggest a random string containing numbers and lower case letters). You should also choose whichever AWS region is best suited for you (for example, eu-west-1)
In example.tfbackend, choose a suitable name for your backend S3 which will store your terraform.tfstate file.

When the above is completed, you can deploy the AWS Infrastructure with:
```
terraform init -backend-config=example.tfbackend
```
```
terraform plan -var-file=example.tfvars
```
```
terraform apply -var-file=example.tfvars -auto-approve
```

### Obfuscator.py

The main purpose of this project was to create a Python module that can assist with obfuscating data from imported CSV files. The module can be ported over to other projects with ease, and requires no dependencies outside of a base Python 3.12 installation. 

To use in your scripts, import the obfuscate function:

```
from obfuscator import obfuscate
```
```
Takes CSV data from a byte stream and alters matching columns from an input list,
    replacing them with "***" strings, before returning the altered byte stream.

Parameters:
    columns (list of str): A list containing the names of columns whose data
    should be obfuscated.
    i_data (byte stream): A byte stream containing the binary data of the CSV file to be
    processed.

    Returns:
    endfile (byte stream): A byte stream containing the obfuscated CSV data
    ready for the calling python script to handle as the user sees fit.

```
### Included scripts

This repo contains a variety of scripts to demonstrate the practical use of the library, including:

**fake_csv.py**: a python script to generate a 1MB CSV file with randomized yet relevant information.

**example_local.py**: a python script that takes a CSV file location. It reads the data into memory and allows the user to choose from a checkbox list which columns are to be obfuscated. The data and the list is sent to the obfuscator library to be processed, and the returned byte stream is converted into another csv file; the name of the input file is used and appended with "-obfuscated" to separate them.

**example_lambda.py**: a python script to be deployed as an AWS lambda. It is triggered when a metadata json file is uploaded to an ingestion S3 bucket. The lambda reads this json data, determines the location of a CSV file to be processed and the columns to be obfuscated. It passes the CSV as a byte stream to the library, which obfuscates the relevant columns and returns the byte stream to the lambda, which in turn converts the byte stream back to a CSV file which is placed in another S3 bucket, ready for download.

**generate_example.sh**: a Bash script designed to demonstrate the **example_lambda.py** functionality as part of the included **Terraform** deployment. It uses **fake_csv.py** to generate a CSV file, creating a .json with metadata required by the Lambda script, and uploads the two files to the ingestion bucket. After ten seconds, the Bash script will display the contents of the obfuscated data S3 bucket, before moving the obfuscated CSV file from the bucket to the users computer. It displays the first ten rows of both the unprocessed and the obfuscated CSV files to allow for immediate comparison.

generate_example.sh needs to be invoked with the prefix used in the example.tfvars file as handled during installation, for example:

```
./generate_example.sh prefixhere
```

### Context And Goals

The project brief is included in [**gdpr_obfuscator.md**](gdpr_obfuscator.md).

As per the project brief, I believe my work reaches the requirements for Minimum Viable Product:
- Contains a module 'obfuscator' -- when calls with the function 'obfuscate' it takes a byte stream containing a CSV file and a list of columns to be obfuscated; obfuscates the relevant data and returns the manipulated byte stream.
- Handles CSV files up to 1MB with a runtime of less than 1 minute (typically less than 5 seconds).
- The module is written in Python.
- All of the Python code is PEP-8 compliant and tested for security vulnerabilities (demonstrated with Flake8, bandit and pip-audit).
- The module is fully unit tested, and most of the example scripts / extension tasks are significantly unit tested.
- Does not exceed the memory limits for Python Lambda dependencies (demonstrated deployed as a Layer with a live AWS Lambda example)
- The code includes documentation (README.md, docstrings for callable functions, logging/print statements/error handling).

Outside of the requirements, I aimed to prevent situations where the CSV data could remain accessible outside of the intended process, such as aiming to keep all data in memory rather than stored in temporary / duplicate files.

### Extension tasks

I would like to continue working on the project and provide further examples of my understanding in how such a library could be handled.

- Create a web interface to allow the uploading of a CSV file, reading the available columns and allowing the user to choose which to obfuscate, obfuscating this data and returning the process CSV file to the user for immediate download.
- Demonstrate the library's use outside of local scripts and AWS lambdas
- Fully unit test all example scripts.
- ~~Create a script that generates CSV data using Faker library~~ (completed)






