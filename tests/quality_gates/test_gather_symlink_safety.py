"""Regression tests for corca-ai/charness#138 — gather latest symlink can
overwrite prior canonical asset.

These tests pin the contract that running the scripted gather writer with
`latest.md` already resolved as a symlink does NOT mutate the prior
canonical asset. Instead the writer creates a fresh dated record and
atomically refreshes the pointer.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

from .support import init_git_repo, run_script

WRITE_RECORD = "skills/public/gather/scripts/write_record.py"


def _bootstrap_gather_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    gather_dir = repo / "charness-artifacts" / "gather"
    gather_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore")
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    return repo


def _sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_write_record_does_not_mutate_prior_canonical_when_pointer_is_symlink(
    tmp_path: Path,
) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"
    prior_canonical = gather_dir / "2026-05-09-prior-asset.md"
    prior_canonical.write_text(
        "# Prior canonical record\n\nDo not overwrite this file.\n",
        encoding="utf-8",
    )
    pointer = gather_dir / "latest.md"
    pointer.symlink_to(prior_canonical.name)
    prior_sha = _sha256_bytes(prior_canonical)

    result = run_script(
        WRITE_RECORD,
        "--repo-root",
        str(repo),
        "--slug",
        "new-asset",
        "--date",
        "2026-05-09",
        "--execute",
        cwd=Path.cwd(),
        env={**os.environ},
    )
    assert result.returncode == 0, result.stdout + result.stderr

    new_canonical = gather_dir / "2026-05-09-new-asset.md"
    assert new_canonical.is_file(), result.stdout
    assert _sha256_bytes(prior_canonical) == prior_sha, "prior canonical mutated"
    assert pointer.is_symlink()
    target = os.readlink(pointer)
    assert target == new_canonical.name, target


def test_write_record_blocks_when_dated_path_exists(tmp_path: Path) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"
    existing = gather_dir / "2026-05-09-already-here.md"
    existing.write_text("# already here\n", encoding="utf-8")

    proc = subprocess.run(
        [
            "python3",
            WRITE_RECORD,
            "--repo-root",
            str(repo),
            "--slug",
            "already-here",
            "--date",
            "2026-05-09",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        input="duplicate content\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1, proc.stdout
    assert "dated record already exists" in proc.stdout


def test_write_record_dry_run_does_not_write(tmp_path: Path) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"
    prior = gather_dir / "2026-05-09-prior.md"
    prior.write_text("# prior\n", encoding="utf-8")
    (gather_dir / "latest.md").symlink_to(prior.name)
    prior_sha = _sha256_bytes(prior)

    proc = subprocess.run(
        [
            "python3",
            WRITE_RECORD,
            "--repo-root",
            str(repo),
            "--slug",
            "dry-run",
            "--date",
            "2026-05-09",
        ],
        cwd=Path(__file__).resolve().parents[2],
        input="dry run\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "planned" in proc.stdout
    assert not (gather_dir / "2026-05-09-dry-run.md").exists()
    assert _sha256_bytes(prior) == prior_sha


def test_write_record_creates_fresh_pointer_when_absent(tmp_path: Path) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"

    proc = subprocess.run(
        [
            "python3",
            WRITE_RECORD,
            "--repo-root",
            str(repo),
            "--slug",
            "fresh",
            "--date",
            "2026-05-09",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        input="fresh content\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout
    record = gather_dir / "2026-05-09-fresh.md"
    pointer = gather_dir / "latest.md"
    assert record.is_file()
    assert pointer.exists()


def test_write_record_rejects_invalid_date(tmp_path: Path) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    proc = subprocess.run(
        [
            "python3",
            WRITE_RECORD,
            "--repo-root",
            str(repo),
            "--slug",
            "ok",
            "--date",
            "../../etc",
        ],
        cwd=Path(__file__).resolve().parents[2],
        input="x\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "ISO YYYY-MM-DD" in proc.stderr


def test_write_record_blocks_when_pointer_symlink_targets_outside_output_dir(
    tmp_path: Path,
) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"
    outside = repo / "outside-target.md"
    outside.write_text("# outside\n", encoding="utf-8")
    pointer = gather_dir / "latest.md"
    pointer.symlink_to("../../outside-target.md")

    proc = subprocess.run(
        [
            "python3",
            WRITE_RECORD,
            "--repo-root",
            str(repo),
            "--slug",
            "new",
            "--date",
            "2026-05-09",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        input="x\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1, proc.stdout
    assert "outside output_dir" in proc.stdout


def test_write_record_handles_dangling_symlink_pointer(tmp_path: Path) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"
    pointer = gather_dir / "latest.md"
    # symlink to a record that doesn't exist (dangling)
    pointer.symlink_to("2026-01-01-missing.md")

    proc = subprocess.run(
        [
            "python3",
            WRITE_RECORD,
            "--repo-root",
            str(repo),
            "--slug",
            "fresh-after-dangling",
            "--date",
            "2026-05-09",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        input="content\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert pointer.is_symlink()
    target = os.readlink(pointer)
    assert target == "2026-05-09-fresh-after-dangling.md", target


def test_write_record_rejects_invalid_slug(tmp_path: Path) -> None:
    repo = _bootstrap_gather_repo(tmp_path)
    proc = subprocess.run(
        [
            "python3",
            WRITE_RECORD,
            "--repo-root",
            str(repo),
            "--slug",
            "Has Spaces",
        ],
        cwd=Path(__file__).resolve().parents[2],
        input="x\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "lowercase letters, digits, and hyphens" in proc.stderr
