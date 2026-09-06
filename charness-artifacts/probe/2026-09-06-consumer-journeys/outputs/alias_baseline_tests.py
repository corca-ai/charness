import unittest

from src.catalog import Catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.mapping = {"books": ["novel"], "music": ["jazz"]}
        self.catalog = Catalog(self.mapping)

    def test_resolves_existing_canonical_keys(self):
        self.assertEqual(self.catalog.resolve("books"), ["novel"])
        self.assertEqual(self.catalog.resolve("music"), ["jazz"])

    def test_unknown_key_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.catalog.resolve("missing")

    def test_empty_alias_list_preserves_canonical_behavior(self):
        catalog = Catalog(self.mapping, aliases=[])

        self.assertEqual(catalog.resolve("books"), ["novel"])
        with self.assertRaises(KeyError):
            catalog.resolve("reading")

    def test_resolves_alias_to_canonical_value(self):
        catalog = Catalog(
            self.mapping,
            aliases=[("reading", "books"), ("listening", "music")],
        )

        self.assertEqual(catalog.resolve("reading"), ["novel"])
        self.assertEqual(catalog.resolve("listening"), ["jazz"])

    def test_canonical_lookup_remains_available_with_aliases(self):
        catalog = Catalog(self.mapping, aliases=[("reading", "books")])

        self.assertEqual(catalog.resolve("books"), ["novel"])
        self.assertEqual(catalog.resolve("reading"), ["novel"])

    def assert_alias_error(self, aliases, expected_message):
        with self.assertRaises(ValueError) as context:
            Catalog(self.mapping, aliases=aliases)
        self.assertEqual(str(context.exception), expected_message)

    def test_rejects_alias_colliding_with_canonical_key(self):
        for alias in ("books", "music"):
            with self.subTest(alias=alias):
                self.assert_alias_error(
                    [(alias, alias)],
                    f"alias {alias!r} collides with canonical key",
                )

    def test_rejects_alias_with_unknown_target(self):
        cases = (
            (
                [("novels", "missing")],
                "alias 'novels' targets unknown canonical key 'missing'",
            ),
            (
                [("reading", "short"), ("short", "books")],
                "alias 'reading' targets unknown canonical key 'short'",
            ),
        )
        for aliases, expected_message in cases:
            with self.subTest(aliases=aliases):
                self.assert_alias_error(aliases, expected_message)

    def test_rejects_duplicate_alias_with_same_target(self):
        self.assert_alias_error(
            [("reading", "books"), ("reading", "books")],
            "duplicate alias 'reading'",
        )

    def test_rejects_duplicate_alias_with_different_target(self):
        self.assert_alias_error(
            [("reading", "books"), ("reading", "music")],
            "duplicate alias 'reading'",
        )

    def test_reports_first_invalid_alias_pair_in_input_order(self):
        cases = (
            (
                [("first", "missing"), ("books", "books")],
                "alias 'first' targets unknown canonical key 'missing'",
            ),
            (
                [("books", "missing"), ("later", "missing")],
                "alias 'books' collides with canonical key",
            ),
            (
                [("first", "books"), ("first", "missing")],
                "duplicate alias 'first'",
            ),
        )
        for aliases, expected_message in cases:
            with self.subTest(aliases=aliases):
                self.assert_alias_error(aliases, expected_message)

    def test_unknown_key_with_aliases_raises_key_error(self):
        catalog = Catalog(self.mapping, aliases=[("reading", "books")])

        with self.assertRaises(KeyError):
            catalog.resolve("missing")


if __name__ == "__main__":
    unittest.main()
