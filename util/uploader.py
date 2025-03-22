import boto3
import base64
import uuid
import logging
from util.config import get_config
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Uploader:
    client = boto3.resource(
        "s3",
        endpoint_url=get_config("S3_ENDPOINT"),
        aws_access_key_id=get_config("S3_ACCESS_TOKEN"),
        aws_secret_access_key=get_config("S3_SECRET_TOKEN"),
    )

    @classmethod
    def upload_file(cls, bucket_name, file_path, file_name=False, content_type="application/octet-stream"):
        try:
            if not file_name:
                file_name = f"{uuid.uuid4().hex}"

            with open(file_path, "rb") as file:
                file_data = file.read()

            bucket = cls.client.Bucket(bucket_name)
            bucket.put_object(
                Key=file_name, Body=file_data, ContentType=content_type, ACL="public-read"
            )

            public_url = f"{get_config('S3_PUBLIC_ENDPOINT')}/{file_name}"
            logger.info(f"File {file_name} uploaded successfully to {bucket_name}. URL: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise e

    @classmethod
    def upload_base64(cls, bucket_name, base64_string, content_type="application/octet-stream"):
        try:
            file_name = f"{uuid.uuid4().hex}"
            file_data = base64.b64decode(base64_string)

            bucket = cls.client.Bucket(bucket_name)
            bucket.put_object(
                Key=file_name, Body=file_data, ContentType=content_type, ACL="public-read"
            )

            public_url = f"{get_config('S3_PUBLIC_ENDPOINT')}/{file_name}"
            logger.info(f"File {file_name} uploaded successfully to {bucket_name}. URL: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Base64 upload failed: {e}")
            raise e
