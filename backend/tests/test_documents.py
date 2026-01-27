import unittest

from app.domain.documents import new_doc_id, originals_object_key


class TestDocuments(unittest.TestCase):
    def test_new_doc_id_is_uuid(self) -> None:
        doc_id = new_doc_id()
        self.assertEqual(len(doc_id), 36)
        self.assertEqual(doc_id.count("-"), 4)

    def test_originals_object_key(self) -> None:
        doc_id = "abc"
        self.assertEqual(originals_object_key(doc_id), "originals/abc.pdf")


if __name__ == "__main__":
    unittest.main()
