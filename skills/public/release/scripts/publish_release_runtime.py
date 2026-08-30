from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, TextIO, TypeVar

from scripts.yaml_output import render_yaml as _render_yaml

T = TypeVar("T")
FAILURE_RECORD_RETENTION = 20


def record_runtime(payload: dict[str, Any], label: str, start: float) -> None:
    payload.setdefault("release_runtime", []).append(
        {"label": label, "elapsed_seconds": round(time.perf_counter() - start, 3)}
    )


def timed(payload: dict[str, Any], label: str, callback: Callable[[], T]) -> T:
    start = time.perf_counter()
    try:
        return callback()
    finally:
        record_runtime(payload, label, start)


def print_failure_payload(
    payload: dict[str, Any],
    error: BaseException,
    *,
    repo_root: Path,
    render_yaml: Callable[[Any], str] | None = None,
    stream: TextIO = sys.stderr,
) -> None:
    visible_keys = (
        "package_id",
        "previous_version",
        "target_version",
        "tag_name",
        "remote",
        "branch",
        "expected_release_url",
        "fresh_checkout_probe_status",
        "public_release_verification",
        "release_runtime",
        "precommit_rollback",
        "issue_closeout_draft_validation",
        "resume_head_release_content_close_refs",
    )
    renderer = render_yaml or _render_yaml
    failure_payload = {key: payload[key] for key in visible_keys if key in payload}
    durable_payload = dict(failure_payload)
    durable_payload["release_failure"] = {
        "status": "failed",
        "error_type": type(error).__name__,
        "error_sha256": hashlib.sha256(str(error).encode()).hexdigest(),
        "detail": "raw exception text omitted from durable local state",
    }
    record = persist_failure_payload(repo_root, durable_payload, render_yaml=renderer)
    failure_payload["release_failure"] = {
        "status": "failed",
        "error": _compact_error(error),
    }
    if record["status"] != "persisted":
        failure_payload["release_failure"]["error_detail"] = _bounded_error(error)
    failure_payload["release_failure_record"] = record
    print("BEGIN publish_release_failure_payload", file=stream)
    # `_render_yaml`, NOT the injectable `renderer`. The two renderers are deliberately
    # independent: `renderer` reaches the DURABLE record, whose write failure is caught
    # and reported back as `release_failure_record.status`. Routing the terminal print
    # through it too means a renderer that raises takes down the one output whose entire
    # job is surfacing a release failure -- the operator gets a traceback and no payload
    # at all. Before the 2026-08-14 YAML migration this line was a hardcoded
    # `json.dumps`, independent for exactly this reason; the migration coupled them.
    print(_render_yaml(failure_payload), end="", file=stream)
    print("END publish_release_failure_payload", file=stream)


def _compact_error(error: BaseException, *, limit: int = 240) -> str:
    summary = next((line.strip() for line in str(error).splitlines() if line.strip()), type(error).__name__)
    return summary if len(summary) <= limit else summary[: limit - 1] + "…"


def _bounded_error(error: BaseException, *, limit: int = 4000) -> str:
    detail = str(error)
    return detail if len(detail) <= limit else "…" + detail[-(limit - 1) :]


def _record_creation_order_ns(path: Path) -> int:
    """Return a creation-order key (epoch nanoseconds) for a persisted record.

    The filename embeds the wall-clock ``time.time_ns()`` stamp taken when the
    record was written, which is far higher resolution than filesystem mtime.
    Coarse-granularity filesystems (ext2/ext3, or ext4 with 128-byte inodes)
    collapse every same-second write to one identical ``st_mtime_ns``, so mtime
    alone cannot order a burst of records and retention would evict an arbitrary
    one instead of the oldest. Prefer the embedded stamp and fall back to mtime
    for any foreign file; the caller breaks any remaining ties on ``path.name``.
    """
    match = re.search(r"-(\d+)\.yaml$", path.name)
    if match is not None:
        return int(match.group(1))
    return path.stat().st_mtime_ns


def _git_common_dir_via_git(repo_root: Path) -> Path:
    git_common = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    common_dir = Path(git_common)
    if not common_dir.is_absolute():
        common_dir = repo_root / common_dir
    return common_dir.resolve()


def _discover_git_dir(repo_root: Path) -> Path | None:
    marker = repo_root / ".git"
    if marker.is_file():
        for line in marker.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("gitdir:"):
                git_dir = Path(stripped.split(":", 1)[1].strip())
                if not git_dir.is_absolute():
                    git_dir = repo_root / git_dir
                return git_dir
        return None
    if marker.is_dir() and (marker / "HEAD").is_file():
        return marker
    return None


def git_common_dir(repo_root: Path) -> Path:
    """Git's common dir, from checkout files when discovery is local.

    ``persist_failure_payload`` only needs the administration root. Ordinary
    checkouts already have it on disk; ``rev-parse`` is the fallback for
    environment-redirected or unreadable layouts.
    """
    if any(os.environ.get(name) for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")):
        return _git_common_dir_via_git(repo_root)
    try:
        git_dir = _discover_git_dir(repo_root)
        if git_dir is not None:
            commondir = git_dir / "commondir"
            if commondir.is_file():
                raw = commondir.read_text(encoding="utf-8").splitlines()[0].strip()
                common = Path(raw)
                if not common.is_absolute():
                    common = git_dir / common
                resolved = common.resolve()
                if resolved.is_dir():
                    return resolved
            elif git_dir.is_dir():
                return git_dir.resolve()
    except OSError:
        pass
    return _git_common_dir_via_git(repo_root)


def persist_failure_payload(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    render_yaml: Callable[[Any], str],
) -> dict[str, Any]:
    """Persist structured recovery evidence without dirtying the release worktree."""
    temporary_path: Path | None = None
    try:
        record_dir = git_common_dir(repo_root) / "charness-release-failures"
        record_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        record_dir.chmod(0o700)
        tag = re.sub(r"[^A-Za-z0-9._-]+", "-", str(payload.get("tag_name", "release")))
        record_path = record_dir / f"{tag}-{time.time_ns()}.yaml"
        rendered = render_yaml(payload)
        temporary_path = record_path.with_suffix(".yaml.tmp")
        descriptor = os.open(temporary_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(rendered)
        os.replace(temporary_path, record_path)
        temporary_path = None
        records = sorted(
            record_dir.glob("*.yaml"),
            key=lambda path: (_record_creation_order_ns(path), path.name),
            reverse=True,
        )
        for stale_record in records[FAILURE_RECORD_RETENTION:]:
            # missing_ok: a concurrent eviction (two release runs sharing one git
            # common dir) may have already removed this record; that must not flip
            # an already-persisted record's status to failed.
            stale_record.unlink(missing_ok=True)
        return {
            "status": "persisted",
            "path": str(record_path),
            "retention_limit": FAILURE_RECORD_RETENTION,
        }
    except Exception as exc:  # persistence must never replace the release failure
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        return {"status": "failed", "error": _compact_error(exc)}
