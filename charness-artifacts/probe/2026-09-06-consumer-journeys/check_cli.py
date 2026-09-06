"""Frozen Goal 798 external-command checks; never installed in producer repos."""

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(os.environ["CHARNESS_CONSUMER_ROOT"]).resolve()


class CliAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="goal798-cli-check-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "consumer"
        # Runtime cache left by producer verification is not a test precondition.
        # Each case below explicitly establishes absent or populated cache state.
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".state"))
        self.source = self.root / "input.json"
        self.source.write_text('{"items": [1, 2], "ready": true}\n')
        self.cache = self.root / ".state/cache.json"

    def snapshot(self):
        return {
            str(p.relative_to(self.root)): (
                p.read_bytes() if p.is_file() else None,
                stat.S_IMODE(p.stat().st_mode),
                p.stat().st_mtime_ns,
            )
            for p in self.root.rglob("*")
        }

    def command(self, *args, legacy=None):
        argv = [str(self.root / "repoctl")] if legacy is None else [sys.executable, legacy]
        return subprocess.run(
            argv + list(args), cwd=self.root, text=True, capture_output=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=15, check=False,
        )

    def readonly(self, args, *, success=True, structured=False):
        before = self.snapshot()
        result = self.command(*args)
        self.assertEqual(self.snapshot(), before, result.stdout + result.stderr)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        if structured:
            self.assertIsInstance(json.loads(result.stdout), dict)
        return result

    def test_help_and_version_readonly(self):
        for args in [("--help",), ("refresh", "--help"), ("doctor", "--help"),
                     ("version", "--help"), ("version",)]:
            with self.subTest(args=args):
                self.assertTrue(self.readonly(args).stdout.strip())

    def test_doctor_has_observable_state_and_is_readonly(self):
        missing = self.readonly(("doctor",), success=False)
        self.cache.parent.mkdir()
        self.cache.write_text('{"ready": true}\n')
        ready = self.readonly(("doctor",), success=False)
        self.assertTrue(missing.stdout.strip() or missing.stderr.strip())
        self.assertNotEqual((missing.returncode, missing.stdout, missing.stderr),
                            (ready.returncode, ready.stdout, ready.stderr))

    def test_dry_run_never_writes(self):
        for existing in [False, True]:
            if existing:
                self.cache.parent.mkdir()
                self.cache.write_text('{"old": true}\n')
            self.readonly(("refresh", "--dry-run", "input.json"))

    def test_structured_output_in_each_option_position(self):
        for args in [("--json", "version"), ("version", "--json"),
                     ("--json", "doctor"), ("doctor", "--json"),
                     ("--json", "refresh", "--dry-run", "input.json"),
                     ("refresh", "--json", "--dry-run", "input.json"),
                     ("refresh", "--dry-run", "input.json", "--json")]:
            with self.subTest(args=args):
                self.readonly(args, success="doctor" not in args, structured=True)

    def test_refresh_writes_only_the_existing_cache(self):
        before = self.snapshot()
        result = self.command("refresh", "input.json", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsInstance(json.loads(result.stdout), dict)
        self.assertEqual(json.loads(self.cache.read_text()), json.loads(self.source.read_text()))
        after = self.snapshot()
        self.assertEqual(set(after) - set(before), {".state", ".state/cache.json"})
        self.assertTrue(all(after[path] == content for path, content in before.items()))

    def test_refresh_replaces_an_existing_cache(self):
        self.cache.parent.mkdir()
        self.cache.write_text('{"stale": true}\n')
        before = self.snapshot()
        result = self.command("refresh", "input.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(self.cache.read_text()), json.loads(self.source.read_text()))
        after = self.snapshot()
        self.assertEqual(set(after), set(before))
        self.assertTrue(all(after[path] == content for path, content in before.items()
                            if path not in {".state", ".state/cache.json"}))

    def test_malformed_inputs_refused_before_write(self):
        (self.root / "--looks-like-a-source.json").write_text('{"danger": true}\n')
        (self.root / "invalid.json").write_text("not json\n")
        cases = [
            ("--unknown",), ("refresh", "--unknown", "input.json"), ("refresh",),
            ("refresh", "--dry-run"), ("refresh", "--looks-like-a-source.json"),
            ("refresh", "--", "--looks-like-a-source.json"),
            ("refresh", "input.json", "extra"),
            ("--json", "refresh", "input.json", "--json"),
            ("refresh", "--dry-run", "--dry-run", "input.json"),
            ("refresh", "invalid.json"), ("refresh", "missing.json"),
        ]
        for args in cases:
            with self.subTest(args=args):
                result = self.readonly(args, success=False)
                self.assertNotEqual(result.returncode, 0)

    def test_legacy_scripts_still_work(self):
        result = self.command("input.json", legacy="scripts/refresh_cache.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(self.cache.read_text()), json.loads(self.source.read_text()))
        before = self.snapshot()
        result = self.command(legacy="scripts/check_cache.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
