from src.obfuscator import obfuscate
import boto3
import json
import io
import os


def lambda_handler(event, context):
    try:
        metadata_filepath = []
        i_filepath = []
        
        metadata_filepath.append(os.environ["INGESTION_BUCKET"])
        i_filepath.append(os.environ["INGESTION_BUCKET"])

        if event["Records"][0]["s3"]["object"]["key"]:
            metadata_filepath.append(event["Records"][0]["s3"]["object"]["key"])
        else:
            metadata_filepath.append(os.environ["INGESTION_KEY"])

        s3 = boto3.client("s3")

        try:
            metadata_file = s3.get_object(
                Bucket=metadata_filepath[0], Key=metadata_filepath[1]
            )
            metadata = json.loads(metadata_file["Body"].read().decode("utf-8"))
        except Exception as e:
            print(e)
            print(f"Error getting metadata file {key} from bucket {bucket}.")
            raise e

        columns = metadata["fields"]
        i_filepath.append(metadata["key"])
        byte_stream = io.BytesIO()
        try:
            s3.download_fileobj(
                Bucket=os.environ["INGESTION_BUCKET"],
                Key=os.environ["INGESTION_KEY"],
                Fileobj=byte_stream,
            )
            byte_stream.seek(0)
        except Exception as e:
            print(e)
            print(
                "Error getting CSV file {key} from bucket {bucket}. Make sure they exist and your metadata file refers to the correct key."
            )
            raise e

        result = obfuscate(columns, byte_stream)

        o_key = i_filepath[1].rsplit(".", 1)
        o_key[0] += "-obfuscated."
        o_key = "".join(o_key)

        s3.put_object(Bucket=os.environ["OBFUSCATED_BUCKET"], Body=result, Key=o_key)

        try:
            s3.delete_object(Bucket=metadata_filepath[0], Key=metadata_filepath[1])
            print(f"Deleted {metadata_filepath[1]}")
        except Exception as e:
            print(e)
            print(
                f"Error deleting metadata file {metadata_filepath[1]} from bucket {metadata_filepath[0]}."
            )
            raise e

        try:
            s3.delete_object(Bucket=i_filepath[0], Key=i_filepath[1])
            print(f"Deleted {i_filepath[1]}")
        except Exception as e:
            print(e)
            print(
                f"Error deleting CSV file {i_filepath[1]} from bucket {i_filepath[0]}."
            )
            raise e

        return {
            "response": 200,
            "bucket": os.environ["OBFUSCATED_BUCKET"],
            "key": o_key,
        }

    except Exception as e:
        return {"response": 500, "error": e}
