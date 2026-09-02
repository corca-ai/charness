#!/usr/bin/env python3
"""Inventory managed mutation outputs and explicitly prune old unmanaged files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import time
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

_quality_adapter = import_repo_module(__file__, "scripts.adapters.quality_adapter_lib")
load_quality_adapter_strict = _quality_adapter.load_quality_adapter_strict
_mutation_sampling = import_repo_module(__file__, "scripts.mutation.mutation_sampling_lib")
DEFAULT_SAMPLE_COVERAGE_JSON = _mutation_sampling.DEFAULT_SAMPLE_COVERAGE_JSON
_mutation_changed_files = import_repo_module(
    __file__, "scripts.mutation.mutation_changed_files_lib"
)
changed_line_coverage_marker_path = _mutation_changed_files.changed_line_coverage_marker_path

DEFAULT_REPORT_ROOT = Path("reports/mutation")
DEFAULT_MANAGED_NAMES = {
    ".mutation-coverage",
    ".mutation-coveragerc",
    "baseline-abort.json",
    "cosmic-ray-dump.jsonl",
    "cosmic-ray-sample-probe.sqlite",
    "cosmic-ray-sample-probe.toml",
    "cosmic-ray.sqlite",
    "exec-timeout.json",
    "release-changed-line-coverage.json",
    "release-changed-line-coverage.json.fingerprint",
    "release-changed-line-coverage.json.changed-line.fingerprint",
    "run.log",
    "sample-coverage.json",
    "sample.json",
    "sample.md",
    "stryker-js.json",
    "stryker-js.html",
    "stryker-js.log",
    "summary.md",
    "test-coverage.json",
    "test-coverage.json.fingerprint",
    "test-coverage.json.changed-line.fingerprint",
}


def _resolved(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def managed_paths(repo_root: Path) -> set[Path]:
    report_root = repo_root / DEFAULT_REPORT_ROOT
    paths = {report_root / name for name in DEFAULT_MANAGED_NAMES}
    adapter = load_quality_adapter_strict(repo_root)
    if adapter.get("valid") is not True:
        messages = "; ".join(str(item) for item in adapter.get("errors", []))
        raise SystemExit(f"mutation-report-retention: invalid quality adapter: {messages}")
    data = adapter.get("data") or {}
    mutation = data.get("mutation_testing") or {}
    for value in (mutation.get("report_paths") or {}).values():
        if isinstance(value, str) and value.strip():
            paths.add(_resolved(repo_root, value).resolve())
    changed_line = data.get("changed_line_mutation_gate") or {}
    coverage_json = changed_line.get("coverage_json")
    if isinstance(coverage_json, str) and coverage_json.strip():
        coverage = _resolved(repo_root, coverage_json).resolve()
        paths.add(coverage)
        paths.add(coverage.with_name(f"{coverage.name}.fingerprint"))
        paths.add(changed_line_coverage_marker_path(coverage).resolve())
    sample = (repo_root / DEFAULT_SAMPLE_COVERAGE_JSON).resolve()
    paths.add(sample)
    return {path.resolve() for path in paths}


def inventory(repo_root: Path, *, older_than_days: int) -> dict[str, object]:
    lexical_report_root = repo_root / DEFAULT_REPORT_ROOT
    if lexical_report_root.is_symlink():
        raise SystemExit("mutation-report-retention: report root must not be a symlink")
    report_root = lexical_report_root.resolve()
    if report_root.exists() and not report_root.is_dir():
        raise SystemExit("mutation-report-retention: report root must be a directory")
    managed = managed_paths(repo_root)
    cutoff = time.time() - older_than_days * 86400
    records: list[dict[str, object]] = []
    if report_root.is_dir():
        for path in sorted(report_root.iterdir(), key=lambda item: item.name):
            try:
                info = path.lstat()
            except OSError:
                continue
            is_managed = path.resolve() in managed
            candidate = (
                path.is_file()
                and not path.is_symlink()
                and not is_managed
                and info.st_mtime < cutoff
            )
            records.append(
                {
                    "path": path.relative_to(repo_root).as_posix(),
                    "bytes": info.st_size if path.is_file() else None,
                    "mtime_ns": info.st_mtime_ns,
                    "managed": is_managed,
                    "kind": "symlink"
                    if path.is_symlink()
                    else "directory"
                    if path.is_dir()
                    else "file",
                    "prune_candidate": candidate,
                }
            )
    candidates = [
        {key: record[key] for key in ("path", "bytes", "mtime_ns")}
        for record in records
        if record["prune_candidate"]
    ]
    root_info = report_root.stat() if report_root.is_dir() else None
    candidate_set_sha256 = hashlib.sha256(
        json.dumps(
            {
                "report_root_exists": root_info is not None,
                "report_root_device": root_info.st_dev if root_info else None,
                "report_root_inode": root_info.st_ino if root_info else None,
                "candidates": candidates,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return {
        "kind": "charness.mutation-report-retention",
        "schema_version": 1,
        "report_root": DEFAULT_REPORT_ROOT.as_posix(),
        "older_than_days": older_than_days,
        "report_root_exists": root_info is not None,
        "report_root_device": root_info.st_dev if root_info else None,
        "report_root_inode": root_info.st_ino if root_info else None,
        "records": records,
        "candidate_count": sum(bool(record["prune_candidate"]) for record in records),
        "candidate_bytes": sum(
            int(record["bytes"] or 0) for record in records if record["prune_candidate"]
        ),
        "candidate_set_sha256": candidate_set_sha256,
    }


def execute_prune(
    repo_root: Path,
    payload: dict[str, object],
    *,
    confirmed_candidate_set_sha256: str,
) -> list[str]:
    expected = str(payload["candidate_set_sha256"])
    if confirmed_candidate_set_sha256 != expected:
        raise SystemExit(
            "mutation-report-retention: candidate-set confirmation mismatch; "
            f"rerun the dry-run and pass --confirm-candidate-set-sha256 {expected}"
        )
    if not any(record["prune_candidate"] for record in payload["records"]):
        return []
    report_root = repo_root / DEFAULT_REPORT_ROOT
    open_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        root_fd = os.open(report_root, open_flags)
    except OSError as exc:
        raise SystemExit("mutation-report-retention: report root changed after inventory") from exc
    try:
        root_info = os.fstat(root_fd)
        if (
            root_info.st_dev != payload["report_root_device"]
            or root_info.st_ino != payload["report_root_inode"]
        ):
            raise SystemExit("mutation-report-retention: report root changed after inventory")
        current_managed = managed_paths(repo_root)
        candidates: list[dict[str, object]] = []
        for record in payload["records"]:
            if not record["prune_candidate"]:
                continue
            path = repo_root / str(record["path"])
            if path.parent != report_root:
                raise SystemExit(
                    f"mutation-report-retention: candidate escaped report root: {path}"
                )
            _validate_candidate(root_fd, path.name, path, record, current_managed)
            candidates.append(record)
        removed: list[str] = []
        for record in candidates:
            path = repo_root / str(record["path"])
            _validate_candidate(root_fd, path.name, path, record, current_managed)
            os.unlink(path.name, dir_fd=root_fd)
            removed.append(str(record["path"]))
        return removed
    finally:
        os.close(root_fd)


def _validate_candidate(
    root_fd: int,
    name: str,
    path: Path,
    record: dict[str, object],
    current_managed: set[Path],
) -> None:
    try:
        current = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
    except OSError as exc:
        raise SystemExit(
            f"mutation-report-retention: candidate changed after inventory: {path}"
        ) from exc
    if (
        not stat.S_ISREG(current.st_mode)
        or current.st_size != record["bytes"]
        or current.st_mtime_ns != record["mtime_ns"]
    ):
        raise SystemExit(f"mutation-report-retention: candidate changed after inventory: {path}")
    if path.resolve() in current_managed:
        raise SystemExit(
            f"mutation-report-retention: candidate became managed after inventory: {path}"
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--older-than-days", type=int, default=30)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-candidate-set-sha256")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.older_than_days < 0:
        raise SystemExit("--older-than-days must be greater than or equal to 0")
    repo_root = args.repo_root.resolve()
    payload = inventory(repo_root, older_than_days=args.older_than_days)
    payload["executed"] = args.execute
    if args.execute and not args.confirm_candidate_set_sha256:
        raise SystemExit(
            "--execute requires --confirm-candidate-set-sha256 from the current dry-run"
        )
    payload["removed"] = (
        execute_prune(
            repo_root,
            payload,
            confirmed_candidate_set_sha256=args.confirm_candidate_set_sha256,
        )
        if args.execute
        else []
    )
    emit_yaml(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
