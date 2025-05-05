#!/bin/bash

PROJ_DIR="$(pwd)"
PYTHONPATH="${PROJ_DIR}"
ZIP_NAME="awslayer_obfuscator.zip"
MODULE_SOURCE="./src/obfuscator.py"
TMP_DIR="${PROJ_DIR}/tmp/"

MODULE_DIR="${TMP_DIR}/layer_obfuscator/python/obfuscator"

source ${PROJ_DIR}/venv/bin/activate

mkdir -p ${MODULE_DIR}
python src/fake_csv.py ${TMP_DIR}/dummydata.csv

echo "from .obfuscator import obfuscate" >${MODULE_DIR}/__init__.py

cp ${MODULE_SOURCE} ${MODULE_DIR}/
