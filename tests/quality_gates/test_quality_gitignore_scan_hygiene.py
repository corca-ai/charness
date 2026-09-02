from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from tests.quality_gates.repo_shapes import install_committed_repo

from .support import ROOT, run_script

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_gitignore_scan_hygiene.py"


def _run_hygiene(repo: Path, *args: str) -> dict[str, object]:
    result = run_script(str(SCRIPT), "--repo-root", str(repo), "--detail", *args, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


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


def test_gitignore_scan_hygiene_flags_raw_scan_in_mixed_file(tmp_path: Path) -> None:
    script = tmp_path / "scan.py"
    script.write_text(
        "import subprocess\n"
        "from pathlib import Path\n"
        "def safe(repo_root: Path):\n"
        "    subprocess.run(['git', 'ls-files', '--exclude-standard'], cwd=repo_root)\n"
        "    return list(repo_root.glob('**/*.py'))\n"
        "def unsafe(repo_root: Path):\n"
        "    return list(repo_root.rglob('*'))\n",
        encoding="utf-8",
    )

    payload = _run_hygiene(tmp_path, "--path-glob", "*.py")

    assert [finding["call"] for finding in payload["findings"]] == ["repo_root.rglob('*')"]


def test_gitignore_scan_hygiene_require_empty_fails_on_findings(tmp_path: Path) -> None:
    script = tmp_path / "scan.py"
    script.write_text(
        "def scan(repo_root):\n    return list(repo_root.rglob('*'))\n", encoding="utf-8"
    )

    result = run_script(
        str(SCRIPT),
        "--repo-root",
        str(tmp_path),
        "--path-glob",
        "*.py",
        "--require-empty",
        cwd=ROOT,
    )

    assert result.returncode == 1
    assert "repo_root.rglob('*')" in result.stdout


def test_gitignore_scan_hygiene_refuses_empty_configured_scope(tmp_path: Path) -> None:
    (tmp_path / "scan.py").write_text("def scan(repo_root):\n    return []\n", encoding="utf-8")

    result = run_script(
        str(SCRIPT),
        "--repo-root",
        str(tmp_path),
        "--path-glob",
        "missing/*.py",
        cwd=ROOT,
    )

    assert result.returncode == 1
    assert "inventory-gitignore-scan-hygiene: refusing empty declared universe" in result.stderr
    assert "missing/*.py" in result.stderr


def test_gitignore_scan_hygiene_strict_listing_fails_closed_outside_git(tmp_path: Path) -> None:
    (tmp_path / "scan.py").write_text("def scan(repo_root):\n    return []\n", encoding="utf-8")

    result = run_script(
        str(SCRIPT),
        "--repo-root",
        str(tmp_path),
        "--path-glob",
        "*.py",
        "--require-git-file-listing",
        cwd=ROOT,
    )

    assert result.returncode == 1
    assert "gitignore scan hygiene file listing failed" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr


def test_gitignore_scan_hygiene_respects_gitignore_for_inventory_inputs(tmp_path: Path) -> None:
    install_committed_repo(tmp_path, {".gitignore": "ignored/\n"})
    (tmp_path / "scan.py").write_text("def scan(repo_root):\n    return []\n", encoding="utf-8")
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


def test_subagent_worktrees_are_ignored_so_a_live_agent_cannot_red_the_gates() -> None:
    """A host-created subagent worktree lands INSIDE this repo, at `.claude/worktrees/`.

    Measured 2026-08-14 while two worktree-isolated subagents were running: the
    directory is a live embedded git repo, so `git add -A` staged it as one (the
    staged-worktree gate refused the commit), and `collect_changed_paths` reported it
    as a changed path with no owning surface, which blocked
    `test_this_repo_is_currently_closeout_bundle_ready`,
    `test_this_repo_is_currently_bundle_ready`, and the critique prepare packet's
    reviewed-input identity for as long as the agents ran.

    One ignore line answers all of it, because the changed-path collector reads
    `git ls-files --others --exclude-standard`. This test exists because deleting that
    line turns nothing red until the next time someone happens to run an isolated
    subagent, and the failure then looks like a broken gate rather than a missing
    ignore.
    """
    probe = ROOT / ".claude" / "worktrees" / "agent-probe-not-created"
    result = subprocess.run(
        ["git", "check-ignore", str(probe)], cwd=ROOT, capture_output=True, text=True
    )

    assert result.returncode == 0, (
        "`.claude/worktrees/` is not gitignored; a worktree-isolated subagent will be "
        "staged as an embedded repo and will red the bundle preflights while it runs"
    )


def test_a_snapshot_backed_fallback_is_not_flagged(tmp_path: Path) -> None:
    """`rglob` guarded by the repo's own listing owner is not an ungoverned scan.

    `RepoFileSnapshot.list_files` delegates to `git_list_repo_files`, which this
    check already trusts -- but it reads the ENCLOSING FUNCTION's source text, and
    the class name is the only spelling that appears at the call sites. Three real
    call sites in `skills/public/quality/scripts/` list through the snapshot and
    keep `rglob` only for the branch where git listing is unavailable; without the
    marker they read as having no gitignore-aware source at all.
    """
    script = tmp_path / "scan.py"
    script.write_text(
        "from pathlib import Path\n"
        "from scripts.repo_file_listing import RepoFileSnapshot\n"
        "def scan(repo_root: Path):\n"
        "    listed = RepoFileSnapshot(repo_root).list_files(include_untracked=True)\n"
        "    if listed is None:\n"
        "        return sorted(repo_root.rglob('*.md'))\n"
        "    return sorted(path for path in listed if path.suffix == '.md')\n",
        encoding="utf-8",
    )

    payload = _run_hygiene(tmp_path, "--path-glob", "*.py")

    assert payload["findings"] == []


def test_gitignore_scan_hygiene_reads_consumer_scanner_universe(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nuniverses:\n  scanner_globs:\n    - src/**/*.py\n",
        encoding="utf-8",
    )
    (repo / "src" / "scan.py").write_text(
        "from pathlib import Path\n"
        "def scan(repo_root: Path):\n"
        "    return list(repo_root.rglob('*'))\n",
        encoding="utf-8",
    )

    payload = _run_hygiene(repo)

    assert payload["path_globs"] == ["src/**/*.py"]
    assert [finding["path"] for finding in payload["findings"]] == ["src/scan.py"]


def test_gitignore_scan_hygiene_refuses_empty_declared_scanner_universe(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nuniverses:\n  scanner_globs: []\n",
        encoding="utf-8",
    )

    result = run_script(str(SCRIPT), "--repo-root", str(repo), cwd=ROOT)

    assert result.returncode == 1
    assert "inventory-gitignore-scan-hygiene: refusing empty declared universe" in result.stderr
