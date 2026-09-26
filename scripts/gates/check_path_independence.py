"""PATH-independence gate for the task_run lane surface (#825).

Re-executes the standing pytest runner over every
``tests/charness_cli/test_task_run*.py`` file with a minimal PATH
(``/usr/bin:/bin``). The lane surface must behave identically whether or
not ambient executables (codex, muse, or anything else) are installed:
input validation runs before PATH probing, and tests use self-made
executables. A failure here is the defect class that broke the mutation
baseline in #825, where refusal tests saw "not on PATH" instead of the
refusal under test.

The re-exec pins the current interpreter for the child runner so the only
variable is PATH, never the Python version.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import run_monitored_phase  # noqa: E402

MINIMAL_PATH = "/usr/bin:/bin"
TARGET_GLOB = "tests/charness_cli/test_task_run*.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    targets = sorted(str(path.relative_to(repo_root)) for path in repo_root.glob(TARGET_GLOB))
    if not targets:
        # Repos without the surface have nothing to check; the message keeps
        # the skip visible instead of silent.
        print("check-path-independence: no task_run test files; nothing to check")
        return 0
    print(
        f"check-path-independence: {len(targets)} task_run files under PATH={MINIMAL_PATH}",
        flush=True,
    )
    command = [
        sys.executable,
        "scripts/gates_support/run_standing_pytest.py",
        "--repo-root",
        str(repo_root),
        "--mode",
        "read-only",
    ]
    for target in targets:
        command.extend(["--pytest-target", target])
    env = dict(os.environ)
    env["PATH"] = MINIMAL_PATH
    env["CHARNESS_STANDING_PYTEST_PYTHON"] = sys.executable
    # A plain return (not exec) so coverage flushes in this process and every
    # line above stays measurable; the child exit code still decides.
    outcome = run_monitored_phase(
        command,
        cwd=repo_root,
        phase="path-independence",
        timeout_seconds=None,
        env=env,
        capture=False,
    )
    return outcome.returncode


if __name__ == "__main__":
    raise SystemExit(main())
