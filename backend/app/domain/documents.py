import uuid


def new_doc_id() -> str:
    return str(uuid.uuid4())


def originals_object_key(doc_uuid: str) -> str:
    return f"originals/{doc_uuid}.pdf"
