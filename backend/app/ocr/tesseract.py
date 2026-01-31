from io import BytesIO

import pkgutil
from importlib.util import find_spec

if not hasattr(pkgutil, "find_loader"):
    def _find_loader(name: str):  # type: ignore[override]
        spec = find_spec(name)
        return spec.loader if spec else None

    pkgutil.find_loader = _find_loader  # type: ignore[attr-defined]

import pytesseract
from PIL import Image


class TesseractOCR:
    def __init__(self, lang: str = "jpn") -> None:
        self._lang = lang

    def extract_text(self, image_bytes: bytes) -> str:
        image = Image.open(BytesIO(image_bytes))
        return pytesseract.image_to_string(image, lang=self._lang)
