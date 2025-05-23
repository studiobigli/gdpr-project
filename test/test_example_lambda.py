from moto import mock_aws
from src.example_lambda import lambda_handler
import boto3
import pytest
import os
import json


@pytest.fixture(scope="function")
def dummy_s3():
    ingestion_bucket = "test-ingestion"
    obfuscated_bucket = "test-obfuscated"
    test_good_data = "id,First Name,Last Name,Age\n1,aaa,aaa,20\n2,bbb,bbb,302"
    test_key = "dummy.csv"
    test_metadata_key = "dummy-fields.json"
    test_metadata = '{"key": "dummy.csv","fields": ["First Name", "Age"]}'

    os.environ["INGESTION_BUCKET"] = ingestion_bucket
    os.environ["OBFUSCATED_BUCKET"] = obfuscated_bucket
    os.environ["INGESTION_KEY"] = test_key

    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(
            Bucket=ingestion_bucket,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3.put_object(
            Bucket=ingestion_bucket, Body=test_good_data, Key=test_key
        )
        s3.put_object(
            Bucket=ingestion_bucket, Body=test_metadata, Key=test_metadata_key
        )
        s3.create_bucket(
            Bucket=obfuscated_bucket,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        yield s3


class TestFunctionLambdaHandler:
    def test_function_creates_obfuscated_csv_in_target_bucket(self, dummy_s3):
        with open("test/event.json", "r") as event_file:
            test_event = json.load(event_file)

        response = lambda_handler(test_event, {})
        check = dummy_s3.list_objects(Bucket="test-obfuscated")

        assert response["response"] == 200
        assert check["Contents"][0]["Key"] == response["key"]

    def test_function_responds_500_if_error(self, dummy_s3):
        test_event = {
            "bucket": "test-ingestion",
            "fields": ["id", "First Name", "Last Name", "Age"],
        }

        response = lambda_handler(test_event, {})

        assert response["response"] == 500

    def test_function_returns_500_if_metadata_file_missing(self, dummy_s3):
        with open("test/event.json", "r") as event_file:
            test_event = json.load(event_file)

        dummy_s3.delete_object(
            Bucket="test-ingestion",
            Key="dummy-fields.json"
        )

        result = lambda_handler(test_event, {})

        assert "NoSuchKey" in str(result["error"])
        assert result["response"] == 500

    def test_function_returns_500_if_csv_file_missing(self, dummy_s3):
        expected = (
            'An error occurred (404) when calling ' +
            'the HeadObject operation: Not Found'
        )

        with open("test/event.json", "r") as event_file:
            test_event = json.load(event_file)

        dummy_s3.delete_object(Bucket="test-ingestion", Key="dummy.csv")
        result = lambda_handler(test_event, {})

        assert expected in str(result["error"])
        assert result["response"] == 500


class TestOutputData:
    def test_obfuscated_file_contains_correct_data(self, dummy_s3):
        check_data = (
                "id,First Name,Last Name,Age" +
                "\n1,***,aaa,***\n2,***,bbb,***\n"
        )
        with open("test/event.json", "r") as event_file:
            test_event = json.load(event_file)

        lambda_handler(test_event, {})

        obj = dummy_s3.get_object(
            Bucket="test-obfuscated",
            Key="dummy-obfuscated.csv"
        )

        assert obj["Body"].read().decode("utf-8") == check_data
