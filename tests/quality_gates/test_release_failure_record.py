from __future__ import annotations

import importlib.util
import os
import re
import subprocess
from pathlib import Path

RUNTIME_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "public"
    / "release"
    / "scripts"
    / "publish_release_runtime.py"
)


def _load_runtime():
    spec = importlib.util.spec_from_file_location("publish_release_failure_record_under_test", RUNTIME_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
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
