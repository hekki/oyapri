import unittest

from app.worker.ingest import _split_by_chars
from app.worker.ingest import _cap_chunks_by_max_chars


class TestChunkSplitter(unittest.TestCase):
    def test_split_by_chars_with_overlap(self) -> None:
        text = "abcdefghij"
        chunks = _split_by_chars(text, size=4, overlap=2)
        self.assertEqual(chunks, ["abcd", "cdef", "efgh", "ghij"])

    def test_split_by_chars_no_overlap(self) -> None:
        text = "abcdef"
        chunks = _split_by_chars(text, size=3, overlap=0)
        self.assertEqual(chunks, ["abc", "def"])

    def test_cap_chunks_by_max_chars(self) -> None:
        chunks = [(1, "abcdef")]
        capped = _cap_chunks_by_max_chars(chunks, max_chars=2)
        self.assertEqual(capped, [(1, "ab"), (1, "cd"), (1, "ef")])
