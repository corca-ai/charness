"""Frozen Goal 798 black-box checks; run outside the producing consumer context."""

import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(os.environ["CHARNESS_CONSUMER_ROOT"]).resolve()
spec = importlib.util.spec_from_file_location("consumer_catalog", ROOT / "src/catalog.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Catalog = module.Catalog


class AliasAcceptance(unittest.TestCase):
    def test_canonical_compatibility(self):
        catalog = Catalog({"red": 17, "blue": 23})
        self.assertEqual(catalog.resolve("red"), 17)
        self.assertEqual(catalog.resolve("blue"), 23)
        with self.assertRaises(KeyError):
            catalog.resolve("missing")

    def test_aliases_and_canonical_names_coexist(self):
        catalog = Catalog({"red": 17, "blue": 23}, aliases=[("r", "red"), ("b", "blue")])
        for key, value in [("r", 17), ("red", 17), ("b", 23), ("blue", 23)]:
            self.assertEqual(catalog.resolve(key), value)
        with self.assertRaises(KeyError):
            catalog.resolve("missing")

    def test_invalid_definitions_rejected(self):
        cases = [
            [("red", "blue")],
            [("a", "missing")],
            [("a", "red"), ("a", "red")],
            [("a", "red"), ("a", "blue")],
            [("a", "red"), ("b", "a")],
        ]
        for aliases in cases:
            with self.subTest(aliases=aliases), self.assertRaises(ValueError):
                Catalog({"red": 17, "blue": 23}, aliases=aliases)

    def test_first_invalid_pair_is_reported(self):
        with self.assertRaises(ValueError) as caught:
            Catalog({"red": 17}, aliases=[("first_bad", "missing"), ("red", "missing")])
        self.assertIn("first_bad", str(caught.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
