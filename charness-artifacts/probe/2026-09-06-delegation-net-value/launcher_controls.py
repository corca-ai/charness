"""One-off final-consumer checks for the neutral transport, never model cells."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import launch


class LauncherChecks(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="goal805-launch-controls-", dir="/tmp")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.work = self.root / "work"
        self.work.mkdir()
        for name in launch.SEED_FILES:
            target = self.work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(launch.SEED / name, target)
        self.assertTrue(launch.inject_task(self.work, launch.HERE / "initial-task.md"))
        self.initial = launch.protected_inventory(self.work)

    def test_inventory_rejects_addition_deletion_and_file_kind(self):
        self.assertTrue(launch.phase_checks(self.work, 1, self.initial)["source_and_test_inventory_unchanged"])
        for name in ("src/helper.py", "tests/test_new.py"):
            path = self.work / name
            path.write_text("pass\n")
            self.assertFalse(launch.phase_checks(self.work, 1, self.initial)["source_and_test_inventory_unchanged"])
            path.unlink()
        original = self.work / "tests/test_catalog.py"
        original.unlink()
        checks = launch.phase_checks(self.work, 1, self.initial)
        self.assertFalse(checks["baseline_tests_unchanged"])
        self.assertFalse(checks["source_and_test_inventory_unchanged"])
        original.symlink_to(launch.SEED / "tests/test_catalog.py")
        checks = launch.phase_checks(self.work, 1, self.initial)
        self.assertFalse(checks["baseline_tests_unchanged"])
        self.assertIn("tests/test_catalog.py", checks["escaping_symlinks"])

    def test_checkpoint_notes_and_interpreter_cache_are_allowed(self):
        (self.work / "checkpoint.md").write_text("Next action: consult current task.\n")
        (self.work / "src/__pycache__").mkdir()
        (self.work / "src/__pycache__/catalog.pyc").write_bytes(b"runtime cache")
        self.assertTrue(launch.phase_checks(self.work, 1, self.initial)["source_and_test_inventory_unchanged"])

    def test_missing_task_is_a_failed_check_then_replaced_by_stimulus(self):
        (self.work / ".task/current.md").unlink()
        self.assertFalse(launch.phase_checks(self.work, 1, self.initial)["task_channel_unchanged"])
        self.assertTrue(launch.inject_task(self.work, launch.HERE / "revised-task.md"))
        self.assertTrue(launch.phase_checks(self.work, 2, self.initial)["task_channel_unchanged"])

    def test_unsafe_task_replacement_refuses_without_following_link(self):
        target = self.work / ".task/current.md"
        target.unlink()
        outside = self.root / "outside.txt"
        outside.write_text("retain")
        target.symlink_to(outside)
        self.assertFalse(launch.inject_task(self.work, launch.HERE / "revised-task.md"))
        self.assertEqual(outside.read_text(), "retain")

    def test_real_isolation_hides_observer_and_host_roots(self):
        command = launch.isolated_command(self.work, None)
        for path in (launch.HERE / "oracle.py", self.root):
            result = subprocess.run(command + ["/usr/bin/test", "!", "-e", str(path)], check=False)
            self.assertEqual(result.returncode, 0)
        result = subprocess.run(command + ["/usr/bin/test", "-f", "/tmp/work/src/catalog.py"], check=False)
        self.assertEqual(result.returncode, 0)

    def test_timeout_is_retained(self):
        result = launch.run_process([sys.executable, "-c", "import time; time.sleep(3)"], "", 0.05,
                                    self.root / "timeout.log")
        self.assertTrue(result["timeout"])
        self.assertNotEqual(result["exit_code"], 0)

    def test_missing_test_does_not_abort_scheduled_second_phase(self):
        # Restrict only the outer directory requirement for this disposable control.
        arm = Path(tempfile.mkdtemp(prefix="goal805-transport-arm-", dir="/tmp"))
        arm.rmdir()
        self.addCleanup(lambda: shutil.rmtree(arm) if arm.exists() else None)
        calls = []

        def fake_process(command, prompt, seconds, output):
            calls.append(seconds)
            output.write_text("fake transport control; no model\n")
            if len(calls) == 1:
                (arm / "work/tests/test_catalog.py").unlink()
            return {"exit_code": 0, "timeout": False, "wall_seconds": 0.0}

        # This is a transport-state test, not a bypass exposed to producer cells.
        actual_read = Path.read_text

        def read_manifest(path, *args, **kwargs):
            if path == launch.HERE / "frozen-inputs.json":
                return (arm / "inputs.json").read_text()
            return actual_read(path, *args, **kwargs)

        actual_is_file = Path.is_file
        def is_file(path):
            return path == launch.HERE / "frozen-inputs.json" or actual_is_file(path)

        with patch.object(sys, "argv", ["launch.py", "cell", "--root", str(arm)]), \
             patch.object(launch, "run_process", fake_process), \
             patch.object(Path, "read_text", read_manifest), \
             patch.object(Path, "is_file", is_file):
            self.assertEqual(launch.main(), 0)
        observations = json.loads((arm / "observations.json").read_text())
        self.assertEqual(calls, [900, 1800])
        self.assertFalse(observations["phase1"]["baseline_tests_unchanged"])
        self.assertFalse(observations["phase2"]["baseline_tests_unchanged"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LauncherChecks)
    # Transport test needs both evidence files to be named before this output exists.
    original_digest = launch.digest
    original_is_file = Path.is_file
    target = launch.HERE / "launcher-control-observations.json"
    def fixture_digest(path):
        return "control-in-progress" if path == target and not target.exists() else original_digest(path)
    with patch.object(launch, "digest", fixture_digest), \
         patch.object(Path, "is_file", lambda path: path == target or original_is_file(path)):
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    payload = {"successful": result.wasSuccessful(), "tests": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "sources": {name: hashlib.sha256((launch.HERE / name).read_bytes()).hexdigest()
                           for name in ("launch.py", "launcher_controls.py")}}
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(rendered)
    print(rendered)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
