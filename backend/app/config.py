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
        self.ai_engine_api_base = os.environ.get("AI_ENGINE_API_BASE", "https://api.ai.sakura.ad.jp/v1")
        self.ai_engine_api_token = os.environ.get("AI_ENGINE_API_TOKEN", "")
        self.ai_engine_embeddings_model = os.environ.get("AI_ENGINE_EMBEDDINGS_MODEL", "multilingual-e5-large")
        self.ai_engine_embeddings_prefix = os.environ.get("AI_ENGINE_EMBEDDINGS_PREFIX", "passage: ")
        self.ai_engine_query_prefix = os.environ.get("AI_ENGINE_QUERY_PREFIX", "query: ")
        self.ai_engine_chat_model = os.environ.get("AI_ENGINE_CHAT_MODEL", "")
        self.chunk_size = int(os.environ.get("CHUNK_SIZE", "250"))
        self.chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", "50"))
        self.embedding_max_tokens = int(os.environ.get("EMBEDDING_MAX_TOKENS", "512"))
        self.embedding_chars_per_token = float(os.environ.get("EMBEDDING_CHARS_PER_TOKEN", "0.5"))


def get_settings() -> Settings:
    return Settings()
