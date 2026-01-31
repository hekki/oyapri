import os


class Settings:
    def __init__(self) -> None:
        self.s3_endpoint = os.environ.get("S3_ENDPOINT", "")
        self.s3_region = os.environ.get("S3_REGION", "ap-northeast-1")
        self.s3_bucket = os.environ.get("S3_BUCKET", "")
        self.s3_access_key_id = os.environ.get("S3_ACCESS_KEY_ID", "")
        self.s3_secret_access_key = os.environ.get("S3_SECRET_ACCESS_KEY", "")
        self.s3_force_path_style = os.environ.get("S3_FORCE_PATH_STYLE", "true").lower() == "true"
        self.mysql_host = os.environ.get("MYSQL_HOST", "")
        self.mysql_port = int(os.environ.get("MYSQL_PORT", "4000"))
        self.mysql_user = os.environ.get("MYSQL_USER", "")
        self.mysql_password = os.environ.get("MYSQL_PASSWORD", "")
        self.mysql_database = os.environ.get("MYSQL_DATABASE", "")
        self.mysql_ca_path = os.environ.get("MYSQL_CA_PATH", "")
        self.simplemq_endpoint = os.environ.get("SIMPLEMQ_ENDPOINT", "")
        self.simplemq_queue_name = os.environ.get("SIMPLEMQ_QUEUE_NAME", "")
        self.simplemq_api_token = os.environ.get("SIMPLEMQ_API_TOKEN", "")
        self.ocr_lang = os.environ.get("OCR_LANG", "jpn")


def get_settings() -> Settings:
    return Settings()
