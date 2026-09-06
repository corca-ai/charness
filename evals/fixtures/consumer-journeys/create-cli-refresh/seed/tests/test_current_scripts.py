import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SEED_ROOT = Path(__file__).resolve().parents[1]
REFRESH = SEED_ROOT / "scripts" / "refresh_cache.py"
CHECK = SEED_ROOT / "scripts" / "check_cache.py"


class CurrentScriptTests(unittest.TestCase):
    def test_refresh_script_writes_parsed_json_for_existing_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            payload = {"items": ["one", "two"], "enabled": True}
            source.write_text(json.dumps(payload), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(REFRESH), str(source)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((root / ".state/cache.json").read_text()), payload)

    def test_check_script_reports_missing_then_ready_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = subprocess.run(
                [sys.executable, str(CHECK)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(missing.returncode, 1)
            self.assertEqual(missing.stdout, "missing\n")

            cache = root / ".state/cache.json"
            cache.parent.mkdir()
            cache.write_text('{"items": []}\n', encoding="utf-8")
            ready = subprocess.run(
                [sys.executable, str(CHECK)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(ready.returncode, 0)
            self.assertEqual(ready.stdout, "ready\n")


if __name__ == "__main__":
    unittest.main()
