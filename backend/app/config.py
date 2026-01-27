import os


class Settings:
    def __init__(self) -> None:
        self.s3_endpoint = os.environ.get("S3_ENDPOINT", "")
        self.s3_region = os.environ.get("S3_REGION", "ap-northeast-1")
        self.s3_bucket = os.environ.get("S3_BUCKET", "")
        self.s3_access_key_id = os.environ.get("S3_ACCESS_KEY_ID", "")
        self.s3_secret_access_key = os.environ.get("S3_SECRET_ACCESS_KEY", "")
        self.s3_force_path_style = os.environ.get("S3_FORCE_PATH_STYLE", "true").lower() == "true"


def get_settings() -> Settings:
    return Settings()
