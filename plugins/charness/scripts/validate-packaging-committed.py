#!/usr/bin/env python3

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


class ValidationError(Exception):
    pass


def run_git(repo_root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=text,
    )


def ensure_git_commit(repo_root: Path, ref: str) -> None:
    result = run_git(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}")
    if result.returncode != 0:
        raise ValidationError(
            f"could not resolve git ref `{ref}` in `{repo_root}`:\nSTDERR:\n{result.stderr}"
        )


def extract_snapshot(repo_root: Path, ref: str, snapshot_root: Path) -> None:
    archive = run_git(repo_root, "archive", "--format=tar", ref, text=False)
    if archive.returncode != 0:
        stderr = archive.stderr.decode("utf-8", errors="replace")
        raise ValidationError(
            f"could not archive git ref `{ref}` in `{repo_root}`:\nSTDERR:\n{stderr}"
        )
    snapshot_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as tar:
        tar.extractall(snapshot_root)


def validate_snapshot(snapshot_root: Path) -> subprocess.CompletedProcess[str]:
    script_path = snapshot_root / "scripts" / "validate-packaging.py"
    if not script_path.is_file():
        raise ValidationError(f"snapshot is missing `{script_path.relative_to(snapshot_root)}`")
    return subprocess.run(
        ["python3", str(script_path), "--repo-root", str(snapshot_root)],
        cwd=snapshot_root,
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--ref", default="HEAD")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    ensure_git_commit(repo_root, args.ref)

    with tempfile.TemporaryDirectory(prefix="charness-validate-packaging-committed-") as tmpdir:
        snapshot_root = Path(tmpdir) / "snapshot"
        extract_snapshot(repo_root, args.ref, snapshot_root)
        result = validate_snapshot(snapshot_root)

    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
        return result.returncode

    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
