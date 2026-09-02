#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import tarfile
import tempfile
from pathlib import Path
from types import SimpleNamespace

try:
    from scripts.core.subprocess_guard import run_monitored_phase, run_process
except ModuleNotFoundError:  # executed directly from scripts/
    from scripts.core.subprocess_guard import run_monitored_phase, run_process


class ValidationError(Exception):
    pass


def run_git(repo_root: Path, *args: str, text: bool = True):  # noqa: ANN201
    result = run_process(["git", *args], cwd=repo_root, timeout_seconds=None)
    if text:
        return result
    return SimpleNamespace(
        args=result.args,
        returncode=result.returncode,
        stdout=result.stdout.encode("utf-8", errors="surrogateescape"),
        stderr=result.stderr.encode("utf-8", errors="surrogateescape"),
    )


def ensure_git_commit(repo_root: Path, ref: str) -> None:
    result = run_git(repo_root, "rev-parse", "--verify", f"{ref}^{{commit}}")
    if result.returncode != 0:
        raise ValidationError(
            f"could not resolve git ref `{ref}` in `{repo_root}`:\nSTDERR:\n{result.stderr}"
        )


def extract_snapshot(repo_root: Path, ref: str, snapshot_root: Path) -> None:
    archive_path = snapshot_root.parent / "snapshot.tar"
    archive_path.unlink(missing_ok=True)
    snapshot_root.parent.mkdir(parents=True, exist_ok=True)
    archive = run_process(
        ["git", "archive", "--format=tar", "--output", str(archive_path), ref],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if archive.returncode != 0:
        raise ValidationError(
            f"could not archive git ref `{ref}` in `{repo_root}`:\nSTDERR:\n{archive.stderr}"
        )
    snapshot_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, mode="r:") as tar:
        tar.extractall(snapshot_root)


def validate_snapshot(snapshot_root: Path):  # noqa: ANN201
    script_path = snapshot_root / "scripts" / "plugin_export" / "validate_packaging.py"
    if not script_path.is_file():
        raise ValidationError(f"snapshot is missing `{script_path.relative_to(snapshot_root)}`")
    # No `--validate-export`. That flag requires the materialized plugin export to exist in
    # the snapshot, and `plugins/` stopped being tracked on 2026-08-29: it is generated
    # by `sync_root_plugin_manifests.py` on `charness init`/`update` and at the release
    # version bump, so a committed tree legitimately has none. (An earlier spelling of
    # this comment also claimed `.githooks/pre-push` runs the sync; it does not -- the
    # hook runs the close-keyword guard, the push classifier, and `run-quality.sh`, and
    # none of them regenerate the mirror.) Asking a commit to carry generated output was the
    # premise this flag encoded, and it is the premise that changed.
    #
    # What survives is the part that was never about the export: the committed manifests
    # and marketplace records still have to be well-formed and agree with each other,
    # and a malformed one reaches consumers exactly the way it always did.
    return run_monitored_phase(
        [
            sys.executable,
            str(script_path),
            "--repo-root",
            str(snapshot_root),
        ],
        cwd=snapshot_root,
        phase="packaging-snapshot-validation",
        timeout_seconds=None,
        capture=True,
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
