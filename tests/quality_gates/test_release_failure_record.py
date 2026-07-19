from __future__ import annotations

import importlib.util
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
    records = sorted(record_dir.glob("*.yaml"))
    assert len(records) == runtime.FAILURE_RECORD_RETENTION
    assert not any(path.name.startswith("v0-") for path in records)


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
