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

from .repo_shapes import install_committed_repo
from .support import run_script

WRITE_RECORD = "skills/public/gather/scripts/write_record.py"


def _bootstrap_gather_repo(tmp_path: Path) -> Path:
    repo = install_committed_repo(tmp_path / "repo", {".gitignore": "\n"}, message="init")
    (repo / "charness-artifacts" / "gather").mkdir(parents=True)
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
    # Real content, via `--content-file`. This test used to inherit an empty stdin, so
    # it wrote a 0-BYTE record and asserted success — pinning sweep row S19
    # (`write_record.py` reported `{"status": "updated"}` over an empty asset) inside
    # the very test that exists to protect the prior canonical file.
    content_file = tmp_path / "new-asset.md"
    content_file.write_text("# New asset\n\nThe gathered source text.\n", encoding="utf-8")

    result = run_script(
        WRITE_RECORD,
        "--repo-root",
        str(repo),
        "--slug",
        "new-asset",
        "--date",
        "2026-05-09",
        "--content-file",
        str(content_file),
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


def test_write_record_refuses_empty_content_instead_of_erasing_the_pointer(tmp_path: Path) -> None:
    """Sweep row S19, parent-reproduced. Empty content wrote a 0-byte dated record AND
    overwrote `latest.md` with 0 bytes, reporting `{"status": "updated",
    "wrote_record": true}` and exit 0.

    The destructive half is the pointer: a previously good gathered asset is replaced
    by nothing while the report says the write worked. Empty stdin is not exotic — a
    fetch that produced nothing, a failed pipe, a truncated download. Whitespace-only
    is the same case, because a record of three newlines is not a knowledge asset."""
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"
    prior = gather_dir / "2026-05-09-prior-asset.md"
    prior.write_text("# Prior canonical record\n\nReal gathered text.\n", encoding="utf-8")
    pointer = gather_dir / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha256_bytes(prior)

    whitespace = tmp_path / "whitespace.md"
    whitespace.write_text("   \n\n\t\n", encoding="utf-8")
    for label, content_file in (("empty", tmp_path / "empty.md"), ("whitespace-only", whitespace)):
        content_file.touch(exist_ok=True)
        result = run_script(
            WRITE_RECORD, "--repo-root", str(repo), "--slug", f"{label}-record",
            "--date", "2026-05-10", "--content-file", str(content_file), "--execute",
            cwd=Path.cwd(), env={**os.environ},
        )
        assert result.returncode == 1, label
        assert "refusing to write an empty gather record" in result.stderr, label
        assert not (gather_dir / f"2026-05-10-{label}-record.md").exists(), label
        assert _sha256_bytes(prior) == prior_sha, f"prior canonical mutated by the {label} run"
        assert os.readlink(pointer) == prior.name, label

    # The dry-run path reads content too (it reports `content_bytes`), so it must
    # refuse the same input the executing run would rather than plan a write.
    planned = run_script(
        WRITE_RECORD, "--repo-root", str(repo), "--slug", "empty-plan",
        "--date", "2026-05-11", "--content-file", str(tmp_path / "empty.md"),
        cwd=Path.cwd(), env={**os.environ},
    )
    assert planned.returncode == 1
    assert "refusing to write an empty gather record" in planned.stderr


def test_write_record_refuses_a_content_file_that_is_not_a_file(tmp_path: Path) -> None:
    """An ABSENT `--content-file` is not empty content, and it is not a crash either.

    The emptiness refusal above reads the file to judge it. Reaching that read with a
    path that does not exist (a fetch step that never ran, a typo'd path) or that is a
    directory raises inside the reader; the writer has to refuse it on the same
    channel as every other refusal, before either the record or the `latest.md`
    pointer is touched. Both the executing and the dry-run arm read content, so both
    must refuse the same input.
    """
    repo = _bootstrap_gather_repo(tmp_path)
    gather_dir = repo / "charness-artifacts" / "gather"
    prior = gather_dir / "2026-05-09-prior-asset.md"
    prior.write_text("# Prior canonical record\n\nReal gathered text.\n", encoding="utf-8")
    pointer = gather_dir / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha256_bytes(prior)

    a_directory = tmp_path / "content-dir"
    a_directory.mkdir()
    cases = (("absent", tmp_path / "never-written.md"), ("directory", a_directory))
    for label, content_file in cases:
        for arm, extra in (("execute", ["--execute"]), ("dry-run", [])):
            result = run_script(
                WRITE_RECORD, "--repo-root", str(repo), "--slug", f"{label}-{arm}",
                "--date", "2026-05-13", "--content-file", str(content_file), *extra,
                cwd=Path.cwd(), env={**os.environ},
            )
            assert result.returncode == 1, f"{label}/{arm}"
            assert "does not exist or is not a file" in result.stderr, f"{label}/{arm}"
            assert str(content_file) in result.stderr, f"{label}/{arm}"
            assert not (gather_dir / f"2026-05-13-{label}-{arm}.md").exists(), f"{label}/{arm}"

    assert _sha256_bytes(prior) == prior_sha, "prior canonical mutated by a refused run"
    assert os.readlink(pointer) == prior.name
