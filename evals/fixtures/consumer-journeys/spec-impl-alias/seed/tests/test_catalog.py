import unittest

from src.catalog import Catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog({"books": ["novel"], "music": ["jazz"]})

    def test_resolves_existing_canonical_keys(self):
        self.assertEqual(self.catalog.resolve("books"), ["novel"])
        self.assertEqual(self.catalog.resolve("music"), ["jazz"])

    def test_unknown_key_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.catalog.resolve("missing")


if __name__ == "__main__":
    unittest.main()
