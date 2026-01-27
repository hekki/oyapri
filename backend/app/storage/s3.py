from typing import BinaryIO

import boto3
from botocore.config import Config

from app.config import Settings


class S3Storage:
    def __init__(self, settings: Settings) -> None:
        client_config = Config(s3={"addressing_style": "path" if settings.s3_force_path_style else "virtual"})
        self._client = boto3.client(
            "s3",
            region_name=settings.s3_region,
            endpoint_url=settings.s3_endpoint or None,
            aws_access_key_id=settings.s3_access_key_id or None,
            aws_secret_access_key=settings.s3_secret_access_key or None,
            config=client_config,
        )
        self._bucket = settings.s3_bucket

    def upload_pdf(self, key: str, body: BinaryIO) -> None:
        self._client.upload_fileobj(
            body,
            self._bucket,
            key,
            ExtraArgs={"ContentType": "application/pdf"},
        )
