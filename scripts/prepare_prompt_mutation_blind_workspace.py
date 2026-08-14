#!/usr/bin/env python3
"""Prepare a capture-facing prompt-mutation workspace with no source history.

Given a source snapshot commit, export only its tree into a new standalone git
repository, then create one neutral parentless commit. The captured run can
still use ordinary git commands, but it cannot inspect the source repo's parent
history, refs, remotes, reflog, or mutation manifest by walking `.git`.

This is an advisory preparation helper for prompt-mutation experiments; it does
not run captures and does not gate commits.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from prompt_mutant_lib import (
    NEUTRAL_COMMIT_MESSAGE,
    neutral_commit_env,
    resolve_baseline_committer_date,
    resolve_baseline_sha,
    resolve_baseline_tree_sha,
    scrub_git_env,
)

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)


class BlindWorkspaceError(RuntimeError):
    pass


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, input_bytes: bytes | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        env=scrub_git_env(env),
        input=input_bytes,
        capture_output=True,
        text=input_bytes is None,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr if isinstance(result.stderr, str) else result.stderr.decode("utf-8", errors="replace")
        raise BlindWorkspaceError(f"{' '.join(cmd)} failed (rc={result.returncode}): {stderr.strip()}")
    stdout = result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
    return stdout.strip()


def _safe_rmtree(path: Path) -> None:
    if path.exists() or path.is_symlink():
        shutil.rmtree(path)


def _ensure_output_dir(path: Path, *, force: bool) -> None:
    if path.exists() and any(path.iterdir()):
        if not force:
            raise BlindWorkspaceError(f"output dir is not empty: {path} (use --force to replace it)")
        _safe_rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _metadata_outside_workspace(metadata_out: Path, workspace: Path) -> bool:
    metadata_parent = metadata_out.resolve().parent
    workspace_resolved = workspace.resolve()
    try:
        return os.path.commonpath([str(metadata_parent), str(workspace_resolved)]) != str(workspace_resolved)
    except ValueError:
        return True


def _archive_tree(repo_root: Path, snapshot_sha: str, output_dir: Path) -> None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "archive", "--format=tar", snapshot_sha],
        capture_output=True,
        env=scrub_git_env(),
        check=False,
    )
    if result.returncode != 0:
        raise BlindWorkspaceError(
            f"git archive failed (rc={result.returncode}): {result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        archive.extractall(output_dir)


def _commit_blind_tree(workspace: Path, commit_date: str) -> str:
    _run(["git", "init", "-q"], cwd=workspace)
    _run(["git", "add", "-A"], cwd=workspace)
    _run(
        ["git", "commit", "--allow-empty", "-q", "-m", NEUTRAL_COMMIT_MESSAGE],
        cwd=workspace,
        env=neutral_commit_env(commit_date),
    )
    return _run(["git", "rev-parse", "HEAD"], cwd=workspace)


def prepare_workspace(repo_root: Path, snapshot_ref: str, output_dir: Path, *, force: bool = False) -> dict:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    snapshot_sha = resolve_baseline_sha(repo_root, snapshot_ref)
    tree_sha = resolve_baseline_tree_sha(repo_root, snapshot_sha)
    commit_date = resolve_baseline_committer_date(repo_root, snapshot_sha)

    _ensure_output_dir(output_dir, force=force)
    _archive_tree(repo_root, snapshot_sha, output_dir)
    workspace_head_sha = _commit_blind_tree(output_dir, commit_date)
    visible_history_count = int(_run(["git", "rev-list", "--count", "HEAD"], cwd=output_dir))
    parent_list = _run(["git", "show", "-s", "--format=%P", "HEAD"], cwd=output_dir)
    remotes = _run(["git", "remote", "-v"], cwd=output_dir)
    return {
        "workspace": str(output_dir),
        "workspace_head_sha": workspace_head_sha,
        "source_snapshot_sha": snapshot_sha,
        "source_tree_sha": tree_sha,
        "visible_history_commit_count": visible_history_count,
        "workspace_head_parents": parent_list.split() if parent_list else [],
        "workspace_remote_count": len([line for line in remotes.splitlines() if line.strip()]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Export a prompt-mutation snapshot into a standalone one-commit git repo for blind captures. "
            "Advisory preparation helper; writes no metadata inside the capture workspace."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--snapshot-ref", required=True, help="Capture-facing parentless snapshot SHA/ref to export.")
    parser.add_argument("--out-dir", type=Path, required=True, help="Standalone blind git repo to create.")
    parser.add_argument("--metadata-out", type=Path, help="Optional JSON metadata path; must be outside --out-dir.")
    parser.add_argument("--force", action="store_true", help="Replace an existing non-empty --out-dir.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.metadata_out and not _metadata_outside_workspace(args.metadata_out, args.out_dir):
            raise BlindWorkspaceError("--metadata-out must live outside --out-dir so the captured run cannot read it")
        report = prepare_workspace(args.repo_root, args.snapshot_ref, args.out_dir, force=args.force)
        if args.metadata_out:
            # `--metadata-out` is a persisted JSON artifact, not command output:
            # it keeps its storage format.
            args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
            args.metadata_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        emit_yaml(report)
        return 0
    except BlindWorkspaceError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
