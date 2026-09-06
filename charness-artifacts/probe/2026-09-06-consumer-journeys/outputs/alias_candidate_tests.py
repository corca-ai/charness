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

    def test_resolves_alias_to_canonical_value(self):
        catalog = Catalog(
            {"books": ["novel"], "music": ["jazz"]},
            aliases=[("reading", "books"), ("listening", "music")],
        )

        self.assertEqual(catalog.resolve("reading"), ["novel"])
        self.assertEqual(catalog.resolve("listening"), ["jazz"])

    def test_canonical_lookup_with_aliases(self):
        catalog = Catalog(
            {"books": ["novel"]}, aliases=[("reading", "books")]
        )

        self.assertEqual(catalog.resolve("books"), ["novel"])
        self.assertEqual(catalog.resolve("reading"), ["novel"])

    def test_rejects_alias_canonical_collision(self):
        with self.assertRaisesRegex(
            ValueError, r"alias 'books' collides with canonical key"
        ):
            Catalog(
                {"books": ["novel"], "music": ["jazz"]},
                aliases=[("books", "music")],
            )

    def test_rejects_unknown_alias_target(self):
        with self.assertRaisesRegex(
            ValueError,
            r"alias 'reading' targets unknown canonical key 'archive'",
        ):
            Catalog({"books": ["novel"]}, aliases=[("reading", "archive")])

    def test_rejects_duplicate_alias_same_target(self):
        with self.assertRaisesRegex(ValueError, r"duplicate alias 'reading'"):
            Catalog(
                {"books": ["novel"]},
                aliases=[("reading", "books"), ("reading", "books")],
            )

    def test_rejects_duplicate_alias_different_target(self):
        with self.assertRaisesRegex(ValueError, r"duplicate alias 'reading'"):
            Catalog(
                {"books": ["novel"], "music": ["jazz"]},
                aliases=[("reading", "books"), ("reading", "music")],
            )

    def test_reports_first_invalid_pair_in_input_order(self):
        with self.assertRaisesRegex(
            ValueError,
            r"alias 'reading' targets unknown canonical key 'archive'",
        ):
            Catalog(
                {"books": ["novel"], "music": ["jazz"]},
                aliases=[("reading", "archive"), ("books", "music")],
            )

    def test_unknown_key_with_aliases_raises_key_error(self):
        catalog = Catalog(
            {"books": ["novel"]}, aliases=[("reading", "books")]
        )

        with self.assertRaises(KeyError):
            catalog.resolve("missing")


if __name__ == "__main__":
    unittest.main()
