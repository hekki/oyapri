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

    def upload_image(self, key: str, body: BinaryIO, content_type: str) -> None:
        self._client.upload_fileobj(
            body,
            self._bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )

    def upload_text(self, key: str, text: str) -> None:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=text.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
        )

    def download_bytes(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def list_keys(self, prefix: str) -> list[str]:
        keys: list[str] = []
        continuation_token: str | None = None
        while True:
            params = {"Bucket": self._bucket, "Prefix": prefix}
            if continuation_token:
                params["ContinuationToken"] = continuation_token
            response = self._client.list_objects_v2(**params)
            for item in response.get("Contents", []):
                key = item.get("Key")
                if key:
                    keys.append(key)
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")
        return keys
