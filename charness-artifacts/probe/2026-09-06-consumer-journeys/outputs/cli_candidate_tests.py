import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SEED_ROOT = Path(__file__).resolve().parents[1]
REPOCTL = SEED_ROOT / "repoctl"


def run_repoctl(root, *args):
    return subprocess.run(
        [str(REPOCTL), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


class RepoctlTests(unittest.TestCase):
    def test_help_and_subcommand_help_are_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for args, marker in (
                (("--help",), "refresh SOURCE"),
                (("refresh", "--help"), "--dry-run"),
                (("doctor", "--help"), "cache.json"),
                (("version", "--help"), "version"),
            ):
                result = run_repoctl(root, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(marker, result.stdout)
                self.assertEqual(result.stderr, "")
            self.assertFalse((root / ".state").exists())

    def test_doctor_reports_status_without_changing_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = run_repoctl(root, "doctor")
            self.assertEqual(missing.returncode, 1)
            self.assertEqual(missing.stdout, "missing\n")
            self.assertFalse((root / ".state").exists())

            cache = root / ".state/cache.json"
            cache.parent.mkdir()
            cache.write_text('{"items": []}\n', encoding="utf-8")
            before = cache.read_bytes()
            ready = run_repoctl(root, "doctor", "--json")
            self.assertEqual(ready.returncode, 0)
            self.assertEqual(
                json.loads(ready.stdout),
                {"cache": ".state/cache.json", "command": "doctor", "status": "ready"},
            )
            self.assertEqual(cache.read_bytes(), before)

            cache.write_text("not json\n", encoding="utf-8")
            invalid = run_repoctl(root, "--json", "doctor")
            self.assertEqual(invalid.returncode, 1)
            self.assertEqual(json.loads(invalid.stdout)["status"], "invalid")
            self.assertEqual(cache.read_text(encoding="utf-8"), "not json\n")

    def test_version_is_a_cheap_human_or_json_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            human = run_repoctl(root, "version")
            self.assertEqual(human.returncode, 0)
            self.assertEqual(human.stdout, "repoctl 1.0.0\n")

            machine = run_repoctl(root, "version", "--json")
            self.assertEqual(machine.returncode, 0)
            self.assertEqual(
                json.loads(machine.stdout),
                {"command": "version", "status": "ok", "version": "1.0.0"},
            )
            self.assertFalse((root / ".state").exists())

    def test_refresh_writes_only_the_legacy_cache_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            payload = {"z": 1, "items": ["one", "two"], "enabled": True}
            source.write_text(json.dumps(payload), encoding="utf-8")

            result = run_repoctl(root, "refresh", str(source))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "refreshed .state/cache.json\n")
            self.assertEqual(
                (root / ".state/cache.json").read_text(encoding="utf-8"),
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
            )
            self.assertEqual(
                sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()),
                [".state/cache.json", "source.json"],
            )

    def test_json_flag_is_order_independent_and_refresh_reports_a_stable_object(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text('{"items": [1]}\n', encoding="utf-8")

            before = {path.relative_to(root).as_posix() for path in root.rglob("*")}
            result = run_repoctl(root, "refresh", "--dry-run", str(source), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(result.stdout),
                {
                    "cache": ".state/cache.json",
                    "command": "refresh",
                    "dry_run": True,
                    "source": str(source),
                    "status": "would_refresh",
                },
            )
            self.assertEqual(
                {path.relative_to(root).as_posix() for path in root.rglob("*")}, before
            )
            self.assertFalse((root / ".state/cache.json").exists())

            result = run_repoctl(root, "--json", "refresh", str(source), "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "would_refresh")
            self.assertFalse((root / ".state/cache.json").exists())

    def test_refresh_json_success_and_dry_run_error_are_machine_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text('{"ok": true}\n', encoding="utf-8")
            result = run_repoctl(root, "refresh", str(source), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "refreshed")

            bad = root / "bad.json"
            bad.write_text("not json\n", encoding="utf-8")
            before = (root / ".state/cache.json").read_bytes()
            result = run_repoctl(root, "--json", "refresh", "--dry-run", str(bad))
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertTrue(payload["dry_run"])
            self.assertEqual((root / ".state/cache.json").read_bytes(), before)

    def test_parser_rejects_invalid_inputs_before_any_write(self):
        invalid_commands = (
            ("refresh", "--unknown", "source.json"),
            ("refresh", "--dry-run"),
            ("refresh", "--looks-like-a-source.json"),
            ("refresh", "--json", "source.json", "--json"),
            ("--json", "refresh", "source.json", "--json"),
            ("refresh", "source.json", "extra.json"),
            ("--unknown",),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for args in invalid_commands:
                result = run_repoctl(root, *args)
                self.assertEqual(result.returncode, 2, (args, result.stderr))
                self.assertEqual(result.stdout, "", args)
            self.assertFalse((root / ".state").exists())

    def test_legacy_refresh_invocation_remains_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            payload = {"legacy": ["still works"]}
            source.write_text(json.dumps(payload), encoding="utf-8")
            legacy = subprocess.run(
                ["python3", str(SEED_ROOT / "scripts/refresh_cache.py"), str(source)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(legacy.returncode, 0, legacy.stderr)
            self.assertEqual(json.loads((root / ".state/cache.json").read_text()), payload)


if __name__ == "__main__":
    unittest.main()
