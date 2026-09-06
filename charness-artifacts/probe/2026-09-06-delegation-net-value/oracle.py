"""Frozen observer, never mounted in producer environments."""

import argparse
from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys
import unittest


class Acceptance(unittest.TestCase):
    catalog = None

    def test_preserved_behavior(self):
        value = ["novel"]
        subject = self.catalog({"books": value})
        self.assertIs(subject.resolve("books"), value)
        self.assertEqual(subject.canonical_key("books"), "books")
        for method in (subject.resolve, subject.canonical_key):
            with self.assertRaises(KeyError):
                method("unknown")

    def test_direct_and_forward_chain(self):
        value = ["jazz"]
        subject = self.catalog(
            {"music": value, "empty": []},
            [("front", "middle"), ("direct", "music"), ("middle", "direct")],
        )
        for name in ("front", "middle", "direct", "music"):
            self.assertIs(subject.resolve(name), value)
            self.assertEqual(subject.canonical_key(name), "music")
        self.assertEqual(subject.canonical_key("empty"), "empty")
        for method in (subject.resolve, subject.canonical_key):
            with self.assertRaises(KeyError):
                method("unknown")

    def assert_invalid(self, aliases, name):
        with self.assertRaises(ValueError) as caught:
            self.catalog({"canonical": object()}, aliases)
        self.assertIn(name, str(caught.exception))

    def test_structural_precedence(self):
        self.assert_invalid(
            [("dangling_first", "missing"), ("duplicate_later", "canonical"),
             ("duplicate_later", "canonical")], "duplicate_later",
        )
        self.assert_invalid(
            [("dangling_first", "missing"), ("canonical", "missing")], "canonical",
        )
        self.assert_invalid(
            [("duplicate_first", "canonical"), ("duplicate_first", "canonical"),
             ("canonical", "missing")], "duplicate_first",
        )

    def test_cycles_and_dangling_report_initiator(self):
        self.assert_invalid([("self_cycle", "self_cycle")], "self_cycle")
        self.assert_invalid(
            [("entry_name", "cycle_a"), ("cycle_a", "cycle_b"),
             ("cycle_b", "cycle_a")], "entry_name",
        )
        self.assert_invalid(
            [("entry_name", "later"), ("later", "absent")], "entry_name",
        )
        self.assert_invalid(
            [("first_failure", "absent"), ("second_failure", "second_failure")],
            "first_failure",
        )

    def test_input_preservation_and_empty_aliases(self):
        mapping = {"canonical": ["value"]}
        aliases = [("alias", "canonical")]
        original_mapping = deepcopy(mapping)
        original_aliases = list(aliases)
        self.catalog(mapping, aliases)
        self.assertEqual(mapping, original_mapping)
        self.assertEqual(aliases, original_aliases)
        self.assertEqual(self.catalog(mapping, []).resolve("canonical"), ["value"])
        bad_aliases = [("bad", "absent")]
        with self.assertRaises(ValueError):
            self.catalog(mapping, bad_aliases)
        self.assertEqual(mapping, original_mapping)
        self.assertEqual(bad_aliases, [("bad", "absent")])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.root.resolve()))
    module = importlib.import_module("src.catalog")
    Acceptance.catalog = module.Catalog
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Acceptance)
    )
    print(json.dumps({"successful": result.wasSuccessful(), "tests": result.testsRun,
                      "failures": len(result.failures), "errors": len(result.errors)}))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
