from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_gitignore_scan_hygiene.py"


def _run_hygiene(repo: Path, *args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_gitignore_scan_hygiene_warns_on_repo_wide_rglob(tmp_path: Path) -> None:
    script = tmp_path / "scan.py"
    script.write_text(
        "from pathlib import Path\n"
        "def scan(repo_root: Path):\n"
        "    return [path for path in repo_root.rglob('*') if path.is_file()]\n",
        encoding="utf-8",
    )

    payload = _run_hygiene(tmp_path, "--path-glob", "*.py")

    assert payload["findings"] == [
        {
            "path": "scan.py",
            "line": 3,
            "call": "repo_root.rglob('*')",
            "reason": "repo-wide filesystem traversal without an obvious gitignore-aware file source",
            "recommendation": (
                "Prefer `git ls-files --cached --others --exclude-standard` or "
                "`scripts.repo_file_listing.iter_matching_repo_files` before scanning."
            ),
        }
    ]


def test_gitignore_scan_hygiene_accepts_git_aware_glob(tmp_path: Path) -> None:
    script = tmp_path / "scan.py"
    script.write_text(
        "import subprocess\n"
        "from pathlib import Path\n"
        "def scan(repo_root: Path):\n"
        "    subprocess.run(['git', 'ls-files', '--exclude-standard'], cwd=repo_root)\n"
        "    return list(repo_root.glob('**/*.py'))\n",
        encoding="utf-8",
    )

    payload = _run_hygiene(tmp_path, "--path-glob", "*.py")

    assert payload["findings"] == []


def test_gitignore_scan_hygiene_respects_gitignore_for_inventory_inputs(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / ".gitignore").write_text("ignored/\n", encoding="utf-8")
    ignored_dir = tmp_path / "ignored"
    ignored_dir.mkdir()
    (ignored_dir / "bad_scan.py").write_text(
        "from pathlib import Path\n"
        "def scan(repo_root: Path):\n"
        "    return list(repo_root.rglob('*'))\n",
        encoding="utf-8",
    )

    payload = _run_hygiene(tmp_path, "--path-glob", "**/*.py")

    assert payload["findings"] == []
