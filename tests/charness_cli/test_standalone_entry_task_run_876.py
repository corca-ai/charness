"""Standalone installed entry resolves its payload for `task run` (#876).

A bare copy of the entry (no `packaging/` beside it, no source tree on
`sys.path`) used to fail every `task run` with
`ModuleNotFoundError: No module named 'scripts'`, because `_load_feature`
resolved the checkout via its `check` callback but never made it
importable nor retried the import. The spawn below runs a copied entry
outside any source tree and asserts the payload-level refusal surfaces
instead of the import error.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRY = REPO_ROOT / "charness"

_SPAWN_TIMEOUT_SECONDS = 120


def _standalone_copy(dest: Path) -> Path:
    """A bare installed copy: entry bytes only, no packaging beside it."""
    dest.mkdir(parents=True, exist_ok=True)
    copy = dest / "charness"
    copy.write_bytes(ENTRY.read_bytes())
    os.chmod(copy, 0o755)
    return copy


def _checkout_fixture(dest: Path) -> Path:
    """A checkout the explicit `--charness-checkout` resolution accepts."""
    (dest / "packaging").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / "packaging" / "charness.json",
        dest / "packaging" / "charness.json",
    )
    os.symlink(REPO_ROOT / "scripts", dest / "scripts")
    return dest


def _git_repo(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main", str(dest)], check=True, capture_output=True)
    (dest / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(dest), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=876@example.com",
            "-c",
            "user.name=e876",
            "-C",
            str(dest),
            "commit",
            "-m",
            "seed",
            "--no-gpg-sign",
        ],
        check=True,
        capture_output=True,
    )
    return dest


def test_standalone_copy_reaches_task_run_payload(tmp_path: Path) -> None:
    home = tmp_path / "home"
    cwd = tmp_path / "cwd"
    home.mkdir(parents=True)
    cwd.mkdir(parents=True)
    standalone = _standalone_copy(tmp_path / "bin")
    checkout = _checkout_fixture(tmp_path / "checkout")
    repo = _git_repo(tmp_path / "consumer")

    # --timeout-seconds 0 is refused by pure input validation, after the
    # payload import and before any executor probing: hermetic, no
    # executables needed, and unreachable when the import still fails.
    result = subprocess.run(
        [
            sys.executable,
            str(standalone),
            "task",
            "run",
            "--charness-checkout",
            str(checkout),
            "--repo-root",
            str(repo),
            "--path",
            str(tmp_path / "lane"),
            "--branch",
            "lane/standalone-probe",
            "--base",
            "HEAD",
            "--scope",
            "module.py",
            "--prompt",
            "inspect the module",
            "--effort",
            "medium",
            "--timeout-seconds",
            "0",
        ],
        env={
            # A repo-bearing PYTHONPATH would make `scripts` importable and
            # the retry path vacuous; drop it so the standalone shape holds.
            **{k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")},
            "HOME": str(home),
            "CHARNESS_NO_UPDATE_CHECK": "1",
            "CI": "",
        },
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_SPAWN_TIMEOUT_SECONDS,
    )

    combined = result.stdout + result.stderr
    assert "ModuleNotFoundError" not in combined, combined[-3000:]
    assert result.returncode != 0, combined[-3000:]
    assert "--timeout-seconds must be a positive integer" in combined
