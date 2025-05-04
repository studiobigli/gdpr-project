from src.obfuscator import obfuscate
import boto3
import io
import os


def lambda_handler(event, context):
    try:
        i_filepath = [event["bucket"], event["key"]]
        columns = event["fields"]
        s3 = boto3.client("s3")
        byte_stream = io.BytesIO()

        s3.download_fileobj(
            Bucket=os.environ["INGESTION_BUCKET"],
            Key=os.environ["INGESTION_KEY"],
            Fileobj=byte_stream,
        )
        byte_stream.seek(0)

        result = obfuscate(columns, byte_stream)

        o_key = i_filepath[1].rsplit(".", 1)
        o_key[0] += "-obfuscated."
        o_key = "".join(o_key)

        s3.put_object(Bucket=os.environ["OBFUSCATED_BUCKET"], Body=result, Key=o_key)

        return {
            "response": 200,
            "bucket": os.environ["OBFUSCATED_BUCKET"],
            "key": o_key,
        }

    except Exception as e:
        return {"response": 500, "error": e}
