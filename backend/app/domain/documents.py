import uuid


def new_doc_id() -> str:
    return str(uuid.uuid4())


def originals_object_key(doc_uuid: str, ext: str, page_no: int | None = None) -> str:
    normalized_ext = ext.lower().lstrip(".")
    if page_no is None:
        return f"originals/{doc_uuid}.{normalized_ext}"
    return f"originals/{doc_uuid}/pages/{page_no}.{normalized_ext}"


def ocr_text_object_key(doc_uuid: str, page_no: int) -> str:
    return f"ocr/{doc_uuid}/pages/{page_no}.txt"
