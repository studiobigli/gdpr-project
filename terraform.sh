#!/bin/bash

PROJ_DIR="$(pwd)"
ZIP_NAME="awslayer_obfuscator.zip"
MODULE_SOURCE="./src/obfuscator.py"
TMP_DIR="${PROJ_DIR}/tmp/"

MODULE_DIR="${TMP_DIR}/layer_obfuscator/python/obfuscator"

mkdir -p ${MODULE_DIR}

echo "from .obfuscator import obfuscate" >${MODULE_DIR}/__init__.py

cp ${MODULE_SOURCE} ${MODULE_DIR}/

#cd ${TMP_DIR}/layer_obfuscator/

#zip -r ../${ZIP_NAME} .

#cd ${TMP_DIR}
#rm -rf ./layer_obfuscator
