from obfuscator import obfuscate
from botocore.exceptions import ClientError
import boto3
import io
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event, context):
    try:
        metadata_filepath = []
        i_filepath = []

        metadata_filepath.append(os.environ["INGESTION_BUCKET"])
        i_filepath.append(os.environ["INGESTION_BUCKET"])
        metadata_filepath.append(event["Records"][0]["s3"]["object"]["key"])

        s3 = boto3.client("s3")

        try:
            logging.info(f"Fetching metadata file {metadata_filepath[1]}")
            metadata_file = s3.get_object(
                Bucket=metadata_filepath[0], Key=metadata_filepath[1]
            )
            metadata = json.loads(metadata_file["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logging.error(e)
                logging.error(f"No Such Key {metadata_filepath[1]}")
            raise e

        columns = metadata["fields"]
        logging.info(f"Obfuscating columns: {columns}")
        i_filepath.append(metadata["key"])
        byte_stream = io.BytesIO()

        try:
            logging.info(f"Fetching file {i_filepath[1]}")
            s3.download_fileobj(
                Bucket=i_filepath[0],
                Key=i_filepath[1],
                Fileobj=byte_stream,
            )
            byte_stream.seek(0)
        except ClientError as e:
            if (
                e.response['Error']['Code'] == 'NoSuchKey' or
                e.response['Error']['Code'] == '404'
            ):
                logging.error(e)
                logging.error(f"No Such Key {i_filepath[1]}")
            raise e

        result = obfuscate(columns, byte_stream)

        o_key = i_filepath[1].rsplit(".", 1)
        o_key[0] += "-obfuscated."
        o_key = "".join(o_key)

        s3.put_object(
            Bucket=os.environ["OBFUSCATED_BUCKET"],
            Body=result,
            Key=o_key
        )
        logging.info(f"Obfuscated file generated: {o_key}")

        s3.delete_object(Bucket=metadata_filepath[0], Key=metadata_filepath[1])
        logging.info(f"Deleted {metadata_filepath[1]}")

        s3.delete_object(Bucket=i_filepath[0], Key=i_filepath[1])
        logging.info(f"Deleted {i_filepath[1]}")

        return {
            "response": 200,
            "bucket": os.environ["OBFUSCATED_BUCKET"],
            "key": o_key,
        }

    except Exception as e:
        logging.error(e)
        return {"response": 500, "error": e}
