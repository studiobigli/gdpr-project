#!/bin/bash

if [[ $# -eq 0 ]]; then
  echo 'Bucket prefix missing. Make sure this matches the prefix in your .tfvars file'
  exit 0
fi

set -e

source venv/bin/activate

mkdir -p $(pwd)/tmp/examples/
PYTHONPATH=$(pwd):$(pwd)/src python src/fake_csv.py $(pwd)/tmp/examples/dummydata.csv
touch $(pwd)/tmp/examples/dummydata-fields.json
cat <<EOF >$(pwd)/tmp/examples/dummydata-fields.json
{
  "key":"dummydata.csv",
  "fields": [
    "First Name",
    "Last Name",
    "Street Address",
    "City",
    "Postcode",
    "Date of Birth",
    "Phone Number",
    "Language"
    ]
}
EOF

echo "showing dummydata-fields.json: "
echo ""
cat $(pwd)/tmp/examples/dummydata-fields.json
echo ""
echo "showing first ten entries of dummydata.csv: "
echo ""
head -n 11 $(pwd)/tmp/examples/dummydata.csv
echo ""

echo "Sending dummydata-fields.json to s3://$1-ingestion/..."
aws s3 cp $(pwd)/tmp/examples/dummydata-fields.json s3://$1-ingestion/dummydata-fields.json
echo ""

echo "Sending dummydata.csv to s3://$1-ingestion/..."
aws s3 cp $(pwd)/tmp/examples/dummydata.csv s3://$1-ingestion/dummydata.csv
echo ""

echo "Waiting 10 seconds for file to process..."
sleep 10

echo "Showing file listings of s3://$1-obfuscated/...:"
echo ""
aws s3 ls s3://$1-obfuscated/
echo ""
echo "Grabbing dummydata-obfuscated.csv from s3://$1-obfuscated/..."
aws s3 cp s3://$1-obfuscated/dummydata-obfuscated.csv $(pwd)/tmp/examples/dummydata-obfuscated.csv
echo ""
echo "showing first ten entries of dummydata-obfuscated.csv: "
echo ""
head -n 11 $(pwd)/tmp/examples/dummydata-obfuscated.csv
echo ""
echo "Removing dummydata-obfuscated.csv from s3://$1-obfuscated/"
aws s3 rm s3://$1-obfuscated/dummydata-obfuscated.csv
