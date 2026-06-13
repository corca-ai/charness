"""Closeout-telemetry emitter (spec achieve-efficiency-improvements, direction E1).

E1 persists the objective operational-waste signals the closeout already computes
into a durable sibling stream. The record must REUSE C's gate_runtime verdict and
B's over-slice run (no recomputation drift), keep all fields present (empty/zero,
never absent), and the emitter must never block closeout — suppressed under
CHARNESS_QUALITY_MODE and the disable knob, writing only under the gitignored
.charness/ tree.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from scripts import slice_closeout_advisories as adv
from scripts import slice_closeout_telemetry as tel


def _churn(commits: int, artifact_only: int) -> dict:
    ratio = round(artifact_only / commits, 3) if commits else 0.0
    return {
        "base": tel.SLICE_CHURN_BASE,
        "commits": commits,
        "artifact_only_commits": artifact_only,
        "artifact_only_ratio": ratio,
    }


def test_default_path_is_usage_episode_sibling() -> None:
    # Sibling of the usage-episode stream, under the already-gitignored tree.
    assert tel.CLOSEOUT_TELEMETRY_DEFAULT_PATH.parent == Path(".charness/usage-episodes")
    assert tel.CLOSEOUT_TELEMETRY_DEFAULT_PATH.name == "closeout_telemetry.jsonl"


def test_record_reuses_gate_runtime_verdict_object(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(adv, "over_slice_run", lambda repo_root: (0, 3))
    monkeypatch.setattr(tel, "_slice_churn", lambda repo_root: _churn(1, 0))
    verdict = {
        "budget_seconds": 120.0,
        "over_budget": [
            {"phase": "verify", "command": "pytest", "elapsed_seconds": 200.0,
             "budget_seconds": 120.0, "over_budget": True}
        ],
    }
    payload = {"status": "completed", "gate_runtime_advisory": verdict}
    record = tel.build_closeout_telemetry_record(tmp_path, payload)
    # Reused straight off the payload — not a second, drifting computation.
    assert record["gate_runtime"] is verdict
    assert record["event_type"] == "closeout_telemetry"
    assert record["status"] == "completed"


def test_record_reuses_over_slice_run_no_drift(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(adv, "over_slice_run", lambda repo_root: (4, 3))
    monkeypatch.setattr(tel, "_slice_churn", lambda repo_root: _churn(4, 4))
    record = tel.build_closeout_telemetry_record(tmp_path, {"status": "completed"})
    assert record["over_slice"] == {"trailing_artifact_only_run": 4, "threshold": 3, "over": True}
    assert record["slice_churn"]["artifact_only_ratio"] == 1.0


def test_clean_slice_records_fields_empty_not_absent(monkeypatch, tmp_path) -> None:
    # Negative: a fast, under-budget, non-churning slice records zero/empty, not absent.
    monkeypatch.setattr(adv, "over_slice_run", lambda repo_root: (0, 3))
    monkeypatch.setattr(tel, "_slice_churn", lambda repo_root: _churn(1, 0))
    record = tel.build_closeout_telemetry_record(tmp_path, {"status": "completed"})
    for field in ("gate_runtime", "over_slice", "slice_churn"):
        assert field in record
    assert record["gate_runtime"] == {"budget_seconds": None, "over_budget": []}
    assert record["over_slice"]["over"] is False
    assert record["slice_churn"]["artifact_only_commits"] == 0


def test_emit_appends_record_to_sibling_path(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("CHARNESS_QUALITY_MODE", raising=False)
    monkeypatch.delenv("CHARNESS_CLOSEOUT_TELEMETRY", raising=False)
    monkeypatch.setattr(adv, "over_slice_run", lambda repo_root: (0, 3))
    monkeypatch.setattr(tel, "_slice_churn", lambda repo_root: _churn(0, 0))
    payload = {"status": "completed", "gate_runtime_advisory": {"budget_seconds": 120.0, "over_budget": []}}

    result = tel.emit_closeout_telemetry_for_slice(tmp_path, payload)
    assert result["emitted"] is True
    records = tmp_path / tel.CLOSEOUT_TELEMETRY_DEFAULT_PATH
    assert records.is_file()
    first = records.read_text(encoding="utf-8").splitlines()
    assert len(first) == 1
    assert json.loads(first[0])["event_type"] == "closeout_telemetry"

    # A second closeout appends, never overwrites.
    tel.emit_closeout_telemetry_for_slice(tmp_path, payload)
    assert len(records.read_text(encoding="utf-8").splitlines()) == 2


def test_quality_mode_suppresses_emission(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CHARNESS_QUALITY_MODE", "1")
    result = tel.emit_closeout_telemetry_for_slice(tmp_path, {"status": "completed"})
    assert result == {"status": "readonly_quality_run", "emitted": False, "quality_mode": "1"}
    assert not (tmp_path / tel.CLOSEOUT_TELEMETRY_DEFAULT_PATH).exists()


def test_disable_env_suppresses_emission(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("CHARNESS_QUALITY_MODE", raising=False)
    monkeypatch.setenv("CHARNESS_CLOSEOUT_TELEMETRY", "off")
    result = tel.emit_closeout_telemetry_for_slice(tmp_path, {"status": "completed"})
    assert result == {"status": "disabled", "emitted": False}
    assert not (tmp_path / tel.CLOSEOUT_TELEMETRY_DEFAULT_PATH).exists()


def test_resolve_max_mb_valid_floor_and_garbage(monkeypatch) -> None:
    monkeypatch.setenv("CHARNESS_CLOSEOUT_TELEMETRY_MAX_MB", "7")
    assert tel._resolve_max_mb() == 7
    monkeypatch.setenv("CHARNESS_CLOSEOUT_TELEMETRY_MAX_MB", "0")  # max(1, 0) floor
    assert tel._resolve_max_mb() == 1
    monkeypatch.setenv("CHARNESS_CLOSEOUT_TELEMETRY_MAX_MB", "nope")  # ValueError branch
    assert tel._resolve_max_mb() == tel.DEFAULT_TELEMETRY_MAX_MB
    monkeypatch.delenv("CHARNESS_CLOSEOUT_TELEMETRY_MAX_MB", raising=False)
    assert tel._resolve_max_mb() == tel.DEFAULT_TELEMETRY_MAX_MB


def test_portable_path_outside_repo_falls_back_to_str(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    inside = repo / "y.jsonl"
    assert tel._portable_path(repo, inside) == "y.jsonl"
    outside = (tmp_path / "outside" / "x.jsonl").resolve()  # relative_to raises ValueError
    assert tel._portable_path(repo, outside) == str(outside)


def _git_fake(*, rev_rc: int = 0, log_rc: int = 0, show_rc: int = 0,
              log_stdout: str = "sha1\nsha2\n", show_stdout: str = ""):
    def fake_run(cmd, **_kw):
        if "rev-parse" in cmd:
            return SimpleNamespace(returncode=rev_rc, stdout="")
        if "log" in cmd:
            return SimpleNamespace(returncode=log_rc, stdout=log_stdout)
        if "show" in cmd:
            return SimpleNamespace(returncode=show_rc, stdout=show_stdout)
        return SimpleNamespace(returncode=0, stdout="")
    return fake_run


def test_slice_commit_path_lists_empty_when_base_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(tel.subprocess, "run", _git_fake(rev_rc=1))
    assert tel._slice_commit_path_lists(tmp_path) == []


def test_slice_commit_path_lists_empty_when_log_fails(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(tel.subprocess, "run", _git_fake(log_rc=1))
    assert tel._slice_commit_path_lists(tmp_path) == []


def test_slice_commit_path_lists_breaks_when_show_fails(monkeypatch, tmp_path) -> None:
    # rev-parse ok, log returns shas, show fails -> break before appending.
    monkeypatch.setattr(tel.subprocess, "run", _git_fake(show_rc=1))
    assert tel._slice_commit_path_lists(tmp_path) == []


def test_slice_churn_over_real_helper(monkeypatch, tmp_path) -> None:
    # Happy path: two commits, both charness-artifacts/-only -> ratio 1.0.
    monkeypatch.setattr(
        tel.subprocess, "run",
        _git_fake(show_stdout="charness-artifacts/x.md\n"),
    )
    churn = tel._slice_churn(tmp_path)
    assert churn["commits"] == 2
    assert churn["artifact_only_commits"] == 2
    assert churn["artifact_only_ratio"] == 1.0
    assert churn["base"] == tel.SLICE_CHURN_BASE


def test_emit_invalid_records_path(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("CHARNESS_QUALITY_MODE", raising=False)
    monkeypatch.delenv("CHARNESS_CLOSEOUT_TELEMETRY", raising=False)
    # An absolute default path resolves outside repo_root -> relative_to raises.
    outside = (tmp_path / "outside" / "telemetry.jsonl").resolve()
    monkeypatch.setattr(tel, "CLOSEOUT_TELEMETRY_DEFAULT_PATH", outside)
    result = tel.emit_closeout_telemetry_for_slice(tmp_path / "repo", {"status": "completed"})
    assert result["status"] == "invalid_records_path"
    assert result["emitted"] is False


def test_emit_failed_when_record_build_raises(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("CHARNESS_QUALITY_MODE", raising=False)
    monkeypatch.delenv("CHARNESS_CLOSEOUT_TELEMETRY", raising=False)

    def boom(_repo_root, _payload):
        raise RuntimeError("boom")

    monkeypatch.setattr(tel, "build_closeout_telemetry_record", boom)
    result = tel.emit_closeout_telemetry_for_slice(tmp_path, {"status": "completed"})
    assert result["status"] == "emit_failed"
    assert result["emitted"] is False
    assert "RuntimeError" in result["error"]
