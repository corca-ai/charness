from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .git_fixture_support import init_git_repo
from .seeding_support import load_module

RUNTIME_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "public"
    / "release"
    / "scripts"
    / "publish_release_runtime.py"
)


def _load_runtime():
    return load_module("publish_release_failure_record_under_test", RUNTIME_PATH)


def _seed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_git_repo(repo)
    return repo


def _render_yaml(_payload) -> str:
    return "status: failed\n"


def _retained_tags(record_dir: Path) -> set[str]:
    # Record names are ``{tag}-{time_ns}.yaml``; split on the LAST hyphen so tags
    # that themselves contain hyphens (e.g. ``v1.0.0-rc1``) extract intact.
    return {path.name.rsplit("-", 1)[0] for path in record_dir.glob("*.yaml")}


def test_failure_record_retention_removes_oldest_record(tmp_path: Path) -> None:
    runtime = _load_runtime()
    repo = _seed_repo(tmp_path)

    for index in range(runtime.FAILURE_RECORD_RETENTION + 1):
        result = runtime.persist_failure_payload(
            repo,
            {"tag_name": f"v{index}"},
            render_yaml=_render_yaml,
        )
        assert result["status"] == "persisted"

    record_dir = repo / ".git" / "charness-release-failures"
    # The loop writes v0 (oldest) .. vN (newest); retention keeps the newest N and
    # must drop exactly v0. On coarse-mtime filesystems (ext2/ext3, ext4 with
    # 128-byte inodes) every same-second write shares one st_mtime_ns, so this
    # assertion pins the exact retained set rather than trusting mtime order.
    assert _retained_tags(record_dir) == {f"v{index}" for index in range(1, runtime.FAILURE_RECORD_RETENTION + 1)}


def test_failure_record_retention_evicts_by_creation_stamp_not_mtime(tmp_path: Path) -> None:
    runtime = _load_runtime()
    repo = _seed_repo(tmp_path)

    for index in range(runtime.FAILURE_RECORD_RETENTION):
        result = runtime.persist_failure_payload(
            repo,
            {"tag_name": f"v{index}"},
            render_yaml=_render_yaml,
        )
        assert result["status"] == "persisted"

    record_dir = repo / ".git" / "charness-release-failures"
    # Make filesystem mtime ADVERSARIAL to true creation order: the oldest-created
    # record (v0) is stamped with the newest mtime. A retention that trusts mtime
    # would keep v0 and evict a newer record; eviction must instead honor the
    # embedded creation stamp. This pins the fix deterministically on any
    # filesystem, including nanosecond-granularity ones where the natural flake
    # never reproduces.
    embedded_ns = lambda path: int(re.search(r"-(\d+)\.yaml$", path.name).group(1))  # noqa: E731
    by_creation = sorted(record_dir.glob("*.yaml"), key=embedded_ns)
    base_seconds = 2_000_000_000  # well past every real record mtime in this test
    for offset, path in enumerate(by_creation):
        stamp_ns = (base_seconds + (len(by_creation) - offset)) * 1_000_000_000
        os.utime(path, ns=(stamp_ns, stamp_ns))

    result = runtime.persist_failure_payload(
        repo,
        {"tag_name": f"v{runtime.FAILURE_RECORD_RETENTION}"},
        render_yaml=_render_yaml,
    )
    assert result["status"] == "persisted"

    assert _retained_tags(record_dir) == {f"v{index}" for index in range(1, runtime.FAILURE_RECORD_RETENTION + 1)}


def test_failure_record_retention_tolerates_concurrent_eviction(tmp_path: Path, monkeypatch) -> None:
    runtime = _load_runtime()
    repo = _seed_repo(tmp_path)

    for index in range(runtime.FAILURE_RECORD_RETENTION):
        assert runtime.persist_failure_payload(repo, {"tag_name": f"v{index}"}, render_yaml=_render_yaml)["status"] == "persisted"

    record_dir = repo / ".git" / "charness-release-failures"
    real_key = runtime._record_creation_order_ns
    raced = {"done": False}

    def racing_key(path):
        # Simulate a competing release run (sharing one git common dir) that removes
        # the oldest record after this call globbed+sorted it but before it unlinks —
        # the classic TOCTOU on the shared directory. persist must still persist.
        key = real_key(path)
        if not raced["done"]:
            raced["done"] = True
            min(record_dir.glob("*.yaml"), key=real_key).unlink()
        return key

    monkeypatch.setattr(runtime, "_record_creation_order_ns", racing_key)

    result = runtime.persist_failure_payload(
        repo,
        {"tag_name": f"v{runtime.FAILURE_RECORD_RETENTION}"},
        render_yaml=_render_yaml,
    )

    assert result["status"] == "persisted"


def test_failure_record_does_not_launch_git_in_an_ordinary_checkout(
    tmp_path: Path, monkeypatch
) -> None:
    runtime = _load_runtime()
    repo = _seed_repo(tmp_path)
    git_launches: list[tuple[str, ...]] = []
    original = subprocess.run

    def wrapped(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            git_launches.append(tuple(str(part) for part in argv[1:]))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", wrapped)
    result = runtime.persist_failure_payload(
        repo,
        {"tag_name": "v1"},
        render_yaml=_render_yaml,
    )
    assert result["status"] == "persisted"
    assert git_launches == []
    assert (repo / ".git" / "charness-release-failures").is_dir()


def test_failed_atomic_replace_removes_temporary_record(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runtime = _load_runtime()
    repo = _seed_repo(tmp_path)

    def fail_replace(_source, _target):
        raise OSError("replace unavailable")

    monkeypatch.setattr(runtime.os, "replace", fail_replace)

    result = runtime.persist_failure_payload(
        repo,
        {"tag_name": "v1"},
        render_yaml=_render_yaml,
    )

    record_dir = repo / ".git" / "charness-release-failures"
    assert result["status"] == "failed"
    assert "replace unavailable" in result["error"]
    assert not list(record_dir.glob("*.tmp"))
    assert not list(record_dir.glob("*.yaml"))
