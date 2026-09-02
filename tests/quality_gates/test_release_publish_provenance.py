"""Entrypoint provenance guard for the release publish path.

Separated from `test_release_publish_resilience.py` as its own concept rather
than spilled into a `_lib` companion (D33): resilience covers what a publish
does when a step fails mid-run, while this covers refusing a run that should
never have started.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from ..repo_copy import REPO_COPY_IGNORE

REPO_ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.boundary_contract(
    reason="prove the release entrypoint's installed-style foreign copy is rejected while the repo-local executable proceeds"
)


def _foreign_tree(tmp_path: Path) -> Path:
    """An installed-style charness tree whose lazily-imported library has drifted."""
    foreign = tmp_path / "foreign"
    (foreign / ".claude-plugin").mkdir(parents=True)
    (foreign / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "charness", "version": "0.0.1"}), encoding="utf-8"
    )
    shutil.copytree(REPO_ROOT / "scripts", foreign / "scripts", ignore=REPO_COPY_IGNORE)
    lessons = foreign / "scripts" / "lessons" / "recent_lessons_lib.py"
    lessons.write_text(lessons.read_text(encoding="utf-8") + "\n# drifted\n", encoding="utf-8")
    entry = foreign / "skills" / "release" / "scripts"
    entry.mkdir(parents=True)
    for script in (REPO_ROOT / "skills" / "public" / "release" / "scripts").glob("*.py"):
        shutil.copy2(script, entry / script.name)
    (foreign / "skill_runtime_bootstrap.py").write_text(
        (REPO_ROOT / "skill_runtime_bootstrap.py").read_text(encoding="utf-8"), encoding="utf-8"
    )
    return foreign


def test_publish_entrypoint_refuses_a_drifted_foreign_copy(tmp_path: Path) -> None:
    """Refuse BEFORE bump/sync/quality, not partway through.

    Two 2.11.2 publish attempts ran bump, manifest sync, and the full quality
    suite from an installed copy before dying on a stale lesson index the copy's
    own library had written. The entrypoint has enough information to refuse in
    milliseconds, and the drift is in a module imported lazily much later --
    which is why the guard scans the tree rather than the import anchors.
    """
    foreign = _foreign_tree(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(foreign / "skills" / "release" / "scripts" / "publish_release.py"),
            "--repo-root",
            str(REPO_ROOT),
            "--part",
            "patch",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2, (result.returncode, result.stdout[-2000:], result.stderr[-2000:])
    assert "helper provenance refusal" in result.stderr
    assert "scripts/lessons/recent_lessons_lib.py" in result.stderr
    assert "skills/public/release/scripts/publish_release.py" in result.stderr


def test_publish_entrypoint_allows_the_repo_local_copy(tmp_path: Path) -> None:
    """The guard must be invisible to the normal repo-local invocation."""
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release.py"),
            "--repo-root",
            str(REPO_ROOT),
            "--publish-current",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert "helper provenance refusal" not in result.stderr
    # It proceeds far enough to hit the real critique gate.
    assert "critique" in (result.stdout + result.stderr).lower()
