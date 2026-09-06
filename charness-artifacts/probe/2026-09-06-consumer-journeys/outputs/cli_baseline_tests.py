import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


SEED_ROOT = Path(__file__).resolve().parents[1]
REPOCTL = SEED_ROOT / "repoctl"


class RepoctlTests(unittest.TestCase):
    def run_cli(self, root, *args):
        return subprocess.run(
            [str(REPOCTL), *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_repoctl_is_executable(self):
        self.assertTrue(os.stat(REPOCTL).st_mode & stat.S_IXUSR)

    def test_help_is_read_only_and_subcommand_help_is_available(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for args in (
                ("--help",),
                ("refresh", "--help"),
                ("doctor", "--help"),
                ("version", "--help"),
            ):
                result = self.run_cli(root, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage: repoctl", result.stdout)
            self.assertFalse((root / ".state/cache.json").exists())

    def test_version_is_a_cheap_read_only_probe_with_json_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_cli(root, "--json", "version")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(result.stdout),
                {"command": "version", "status": "ok", "version": "1.0.0"},
            )
            self.assertFalse((root / ".state").exists())

    def test_doctor_reports_status_without_creating_or_rewriting_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = self.run_cli(root, "doctor", "--json")
            self.assertEqual(missing.returncode, 1)
            self.assertEqual(json.loads(missing.stdout)["status"], "missing")
            self.assertFalse((root / ".state").exists())

            cache = root / ".state/cache.json"
            cache.parent.mkdir()
            cache.write_text('{"items": []}\n', encoding="utf-8")
            before = cache.stat().st_mtime_ns
            ready = self.run_cli(root, "doctor")
            self.assertEqual(ready.returncode, 0)
            self.assertEqual(ready.stdout, "cache: ready\n")
            self.assertEqual(cache.stat().st_mtime_ns, before)

            cache.write_text("not json\n", encoding="utf-8")
            invalid = self.run_cli(root, "doctor", "--json")
            self.assertEqual(invalid.returncode, 1)
            self.assertEqual(json.loads(invalid.stdout)["status"], "invalid")

    def test_refresh_and_dry_run_support_json_positions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            payload = {"items": ["one", "two"], "enabled": True}
            source.write_text(json.dumps(payload), encoding="utf-8")

            dry_run = self.run_cli(
                root, "refresh", "--dry-run", "--json", str(source)
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertEqual(
                json.loads(dry_run.stdout),
                {
                    "cache": ".state/cache.json",
                    "command": "refresh",
                    "dry_run": True,
                    "source": str(source),
                    "status": "would_refresh",
                },
            )
            self.assertFalse((root / ".state/cache.json").exists())

            refresh = self.run_cli(root, "--json", "refresh", str(source))
            self.assertEqual(refresh.returncode, 0, refresh.stderr)
            result = json.loads(refresh.stdout)
            self.assertEqual(result["status"], "refreshed")
            self.assertFalse(result["dry_run"])
            self.assertEqual(
                json.loads((root / ".state/cache.json").read_text()), payload
            )
            self.assertEqual(
                (root / ".state/cache.json").read_text(encoding="utf-8"),
                '{\n  "enabled": true,\n  "items": [\n    "one",\n    "two"\n  ]\n}\n',
            )

            after_source = self.run_cli(root, "refresh", str(source), "--json")
            self.assertEqual(after_source.returncode, 0, after_source.stderr)
            self.assertEqual(json.loads(after_source.stdout)["status"], "refreshed")

            before_dry_run = (root / ".state/cache.json").read_bytes()
            dry_run_existing = self.run_cli(
                root, "refresh", str(source), "--dry-run", "--json"
            )
            self.assertEqual(dry_run_existing.returncode, 0, dry_run_existing.stderr)
            self.assertEqual((root / ".state/cache.json").read_bytes(), before_dry_run)

    def test_parser_refuses_invalid_shapes_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text('{"before": true}\n', encoding="utf-8")

            invalid_calls = (
                ("refresh", "--unknown", str(source)),
                ("--json", "refresh", str(source), "--json"),
                ("refresh", "--json"),
                ("refresh", "--looks-like-a-source.json"),
                ("refresh", str(source), "--unknown"),
                ("--json",),
            )
            for args in invalid_calls:
                with self.subTest(args=args):
                    result = self.run_cli(root, *args)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("repoctl: error:", result.stderr)
                    self.assertFalse((root / ".state/cache.json").exists())

    def test_legacy_refresh_invocation_still_writes_same_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            payload = {"z": 1, "a": ["value"]}
            source.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SEED_ROOT / "scripts/refresh_cache.py"), str(source)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (root / ".state/cache.json").read_text(encoding="utf-8"),
                '{\n  "a": [\n    "value"\n  ],\n  "z": 1\n}\n',
            )


if __name__ == "__main__":
    unittest.main()
