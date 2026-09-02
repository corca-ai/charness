"""Announcement delivery boundary: the rung-1 presence floor (P5) and the
optional adapter-declared readback probe (rung-2 observer, P4) for
`delivery_kind: human-backend` -- the only announcement delivery kind that
writes to a system this repo does not control. `none` and `release-notes`
stay outside this floor.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import announcement_verification_lib as verification_lib
from scripts.announcement_verification_lib import (
    DELIVERY_VERIFICATION_STATUSES,
    STATUSES_REQUIRING_REASON,
    evaluate_delivery_kind_agreement,
    evaluate_delivery_verification,
    fail_delivery_kind_mismatch,
    fail_missing_delivery_verification,
    render_readback_probe_command,
    requires_delivery_kind_agreement,
    requires_delivery_verification,
    resolve_manual_disposition,
    run_readback_probe,
)
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
ANNOUNCEMENT_RECORD = load_script_module(
    "tests.portable_record_announcement_verification",
    ROOT / "skills/public/announcement/scripts/record_announcement.py",
)


def _shell_result(returncode: int, stdout: str = "", stderr: str = ""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


# --- rung-1 presence floor (library) --------------------------------------


def test_requires_delivery_verification_only_for_human_backend() -> None:
    assert requires_delivery_verification("human-backend") is True
    assert requires_delivery_verification("none") is False
    assert requires_delivery_verification("release-notes") is False


def test_rung1_floor_refuses_silent_or_untyped_record() -> None:
    assert evaluate_delivery_verification(None)["ok"] is False
    assert evaluate_delivery_verification({})["ok"] is False
    assert evaluate_delivery_verification({"status": "maybe"})["ok"] is False


def test_rung1_floor_passes_confirmation_and_typed_disposition_equally() -> None:
    for status in DELIVERY_VERIFICATION_STATUSES:
        record = {"channel": "human-observation", "status": status}
        assert evaluate_delivery_verification(record)["ok"] is True


def test_fail_missing_delivery_verification_names_typed_statuses() -> None:
    with pytest.raises(SystemExit) as excinfo:
        fail_missing_delivery_verification("human-backend")
    for status in DELIVERY_VERIFICATION_STATUSES:
        assert status in str(excinfo.value)


# --- manual disposition fallback (finding c) ------------------------------


def test_resolve_manual_disposition_returns_none_without_status() -> None:
    assert resolve_manual_disposition(status="", channel="", reason="") is None


def test_resolve_manual_disposition_defaults_channel_and_keeps_reason() -> None:
    record = resolve_manual_disposition(status="skipped", channel="", reason="no probe declared")
    assert record == {
        "channel": "human-observation",
        "status": "skipped",
        "reason": "no probe declared",
    }


@pytest.mark.parametrize("status", STATUSES_REQUIRING_REASON)
def test_resolve_manual_disposition_requires_reason_for_non_confirmed_statuses(status: str) -> None:
    with pytest.raises(SystemExit, match="requires a non-empty --verification-reason"):
        resolve_manual_disposition(status=status, channel="", reason="")
    # with a reason, it succeeds
    record = resolve_manual_disposition(status=status, channel="", reason="explicit reason")
    assert record["reason"] == "explicit reason"


def test_resolve_manual_disposition_confirmed_needs_no_reason() -> None:
    record = resolve_manual_disposition(status="confirmed", channel="", reason="")
    assert record == {"channel": "human-observation", "status": "confirmed"}


# --- delivery_kind self-attestation cross-check ---------------------------


def test_requires_delivery_kind_agreement_only_for_human_backend() -> None:
    assert requires_delivery_kind_agreement("human-backend") is True
    assert requires_delivery_kind_agreement("none") is False
    assert requires_delivery_kind_agreement("release-notes") is False
    assert requires_delivery_kind_agreement(None) is False


def test_evaluate_delivery_kind_agreement_falls_back_when_adapter_unresolved() -> None:
    check = evaluate_delivery_kind_agreement(
        recorded_kind="human-backend", adapter_delivery_kind=None, adapter_resolved=False
    )
    assert check == {"adapter_resolved": False, "trust": "cli-choices-validated"}


def test_evaluate_delivery_kind_agreement_reports_disagreement() -> None:
    check = evaluate_delivery_kind_agreement(
        recorded_kind="none", adapter_delivery_kind="human-backend", adapter_resolved=True
    )
    assert check == {
        "adapter_resolved": True,
        "adapter_delivery_kind": "human-backend",
        "agrees_with_recorded_kind": False,
    }


def test_fail_delivery_kind_mismatch_names_both_values() -> None:
    with pytest.raises(SystemExit) as excinfo:
        fail_delivery_kind_mismatch(recorded_kind="none", adapter_delivery_kind="human-backend")
    message = str(excinfo.value)
    assert "human-backend" in message
    assert "none" in message


# --- rung-2 observer: adapter-declared readback probe ---------------------


def test_render_readback_probe_command_substitutes_placeholders() -> None:
    rendered = render_readback_probe_command(
        "check {delivery_target} {delivery_handle}",
        delivery_target="#eng",
        delivery_handle="123.456",
    )
    assert rendered == "check #eng 123.456"


def test_run_readback_probe_confirms_on_zero_exit() -> None:
    calls: list[str] = []

    def fake_run_shell(command, *, cwd, check):
        calls.append(command)
        return _shell_result(0)

    record = run_readback_probe(
        probe_template="probe {delivery_target}",
        delivery_target="#eng",
        delivery_handle="",
        repo_root=Path("."),
        run_shell=fake_run_shell,
    )
    assert record == {
        "channel": "adapter-probe",
        "command": "probe #eng",
        "status": "confirmed",
        "returncode": 0,
    }
    assert calls == ["probe #eng"]


def test_run_readback_probe_records_not_confirmed_on_failure() -> None:
    def fake_run_shell(command, *, cwd, check):
        return _shell_result(1, stderr="message not found")

    record = run_readback_probe(
        probe_template="probe {delivery_handle}",
        delivery_target="",
        delivery_handle="ts-1",
        repo_root=Path("."),
        run_shell=fake_run_shell,
    )
    assert record["status"] == "not-confirmed"
    assert record["reason"] == "message not found"


# --- CLI floor: record_announcement.py -------------------------------------


def _run(monkeypatch, capsys, *args: str):
    import sys

    monkeypatch.setattr(sys, "argv", ["record_announcement.py", *args])
    returncode = 0
    stderr_suffix = ""
    try:
        returncode = ANNOUNCEMENT_RECORD.main() or 0
    except SystemExit as exc:
        if isinstance(exc.code, int):
            returncode = exc.code
        elif exc.code is None:
            returncode = 0
        else:
            returncode = 1
            stderr_suffix = f"{exc.code}\n"
    captured = capsys.readouterr()
    return SimpleNamespace(
        returncode=returncode, stdout=captured.out, stderr=captured.err + stderr_suffix
    )


def _record_args(repo: Path, artifact: Path, *extra: str) -> list[str]:
    return [
        "--repo-root",
        str(repo),
        "--head-commit",
        "abc123",
        "--artifact-path",
        str(artifact),
        *extra,
    ]


def _prepare_artifact(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "announcement" / "latest.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Announcement\n", encoding="utf-8")
    return repo, artifact


def _read_record(repo: Path) -> dict:
    return json.loads(
        (repo / ".charness" / "announcement" / "announcements.jsonl").read_text(encoding="utf-8")
    )


def test_human_backend_delivery_without_verification_refuses_naming_statuses(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo, artifact, "--delivery-kind", "human-backend", "--delivery-target", "#eng"
        ),
    )
    assert result.returncode != 0
    for status in DELIVERY_VERIFICATION_STATUSES:
        assert status in result.stderr
    assert not (repo / ".charness" / "announcement" / "announcements.jsonl").exists()


@pytest.mark.parametrize("status", DELIVERY_VERIFICATION_STATUSES)
def test_human_backend_delivery_accepts_each_typed_status(
    tmp_path: Path, monkeypatch, capsys, status: str
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--delivery-target",
            "#eng",
            "--verification-status",
            status,
            "--verification-reason",
            "manual check",
        ),
    )
    assert result.returncode == 0, result.stderr
    record = _read_record(repo)
    assert record["verification"]["status"] == status
    assert record["verification"]["reason"] == "manual check"


def test_human_backend_delivery_rejects_untyped_verification_status(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--verification-status",
            "looks-fine",
        ),
    )
    assert result.returncode != 0
    for status in DELIVERY_VERIFICATION_STATUSES:
        assert status in result.stderr


def test_adapter_declared_probe_runs_and_its_verdict_becomes_verification(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    calls: list[str] = []

    def fake_run_readback_probe(*, probe_template, delivery_target, delivery_handle, repo_root):
        calls.append(probe_template)
        return {
            "channel": "adapter-probe",
            "command": "rendered",
            "status": "confirmed",
            "returncode": 0,
        }

    monkeypatch.setattr(ANNOUNCEMENT_RECORD, "run_readback_probe", fake_run_readback_probe)
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--delivery-target",
            "#eng",
            "--delivery-handle",
            "ts-1",
            "--readback-probe-template",
            "check {delivery_target} {delivery_handle}",
        ),
    )
    assert result.returncode == 0, result.stderr
    assert calls == ["check {delivery_target} {delivery_handle}"]
    record = _read_record(repo)
    assert record["verification"] == {
        "channel": "adapter-probe",
        "command": "rendered",
        "status": "confirmed",
        "returncode": 0,
    }


def test_probe_seam_actually_shells_out_and_substitutes_placeholders(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    # No mocking: exercises the real subprocess default run_shell end to end,
    # proving placeholder substitution happens before the shell sees the command.
    repo, artifact = _prepare_artifact(tmp_path)
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--delivery-target",
            "T1",
            "--delivery-handle",
            "H1",
            "--readback-probe-template",
            'test "{delivery_target}" = "T1" -a "{delivery_handle}" = "H1"',
        ),
    )
    assert result.returncode == 0, result.stderr
    record = _read_record(repo)
    assert record["verification"]["status"] == "confirmed"
    assert record["verification"]["channel"] == "adapter-probe"
    assert "T1" in record["verification"]["command"]


def test_readback_probe_takes_priority_over_manual_status(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)

    def fake_run_readback_probe(*, probe_template, delivery_target, delivery_handle, repo_root):
        return {"channel": "adapter-probe", "status": "not-confirmed", "reason": "no readback"}

    monkeypatch.setattr(ANNOUNCEMENT_RECORD, "run_readback_probe", fake_run_readback_probe)
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--readback-probe-template",
            "check",
            "--verification-status",
            "confirmed",
        ),
    )
    assert result.returncode == 0, result.stderr
    record = _read_record(repo)
    assert record["verification"]["status"] == "not-confirmed"


def _write_adapter(repo: Path, delivery_kind: str) -> None:
    target = repo / ".agents" / "announcement-adapter.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"delivery_kind: {delivery_kind}\n", encoding="utf-8")


def test_cli_rejects_foreign_delivery_kind(tmp_path: Path, monkeypatch, capsys) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    result = _run(monkeypatch, capsys, *_record_args(repo, artifact, "--delivery-kind", "slack"))
    assert result.returncode == 2
    assert "invalid choice" in result.stderr
    assert not (repo / ".charness" / "announcement" / "announcements.jsonl").exists()


def test_cli_normalizes_delivery_kind_case(tmp_path: Path, monkeypatch, capsys) -> None:
    for raw, expected in (("Human-Backend", "human-backend"), ("NONE", "none")):
        repo, artifact = _prepare_artifact(tmp_path / raw)
        extra = ["--verification-status", "confirmed"] if expected == "human-backend" else []
        result = _run(
            monkeypatch, capsys, *_record_args(repo, artifact, "--delivery-kind", raw, *extra)
        )
        assert result.returncode == 0, result.stderr
        record = _read_record(repo)
        assert record["delivery_kind"] == expected


def test_cli_refuses_when_delivery_kind_disagrees_with_human_backend_adapter(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    _write_adapter(repo, "human-backend")
    result = _run(monkeypatch, capsys, *_record_args(repo, artifact, "--delivery-kind", "none"))
    assert result.returncode != 0
    assert "human-backend" in result.stderr
    assert "none" in result.stderr
    assert not (repo / ".charness" / "announcement" / "announcements.jsonl").exists()


def test_cli_accepts_matching_human_backend_adapter_and_records_agreement(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    _write_adapter(repo, "human-backend")
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--verification-status",
            "confirmed",
        ),
    )
    assert result.returncode == 0, result.stderr
    record = _read_record(repo)
    assert record["delivery_kind_check"] == {
        "adapter_resolved": True,
        "adapter_delivery_kind": "human-backend",
        "agrees_with_recorded_kind": True,
    }


def test_cli_does_not_enforce_agreement_when_adapter_kind_is_not_human_backend(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    _write_adapter(repo, "release-notes")
    # A legitimate draft-only finalization even though the adapter's declared
    # backend (release-notes) differs from this call's kind (none).
    result = _run(monkeypatch, capsys, *_record_args(repo, artifact, "--delivery-kind", "none"))
    assert result.returncode == 0, result.stderr
    record = _read_record(repo)
    assert record["delivery_kind_check"]["agrees_with_recorded_kind"] is False
    assert record["delivery_kind_check"]["adapter_delivery_kind"] == "release-notes"


def test_cli_falls_back_to_trust_when_adapter_cannot_be_resolved(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)

    def raising_load_announcement_adapter(repo_root):
        raise RuntimeError("simulated adapter resolution failure")

    monkeypatch.setattr(
        ANNOUNCEMENT_RECORD, "load_announcement_adapter", raising_load_announcement_adapter
    )
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo, artifact, "--delivery-kind", "human-backend", "--verification-status", "confirmed"
        ),
    )
    assert result.returncode == 0, result.stderr
    record = _read_record(repo)
    assert record["delivery_kind_check"] == {
        "adapter_resolved": False,
        "trust": "cli-choices-validated",
    }


@pytest.mark.parametrize("status", STATUSES_REQUIRING_REASON)
def test_cli_refuses_status_without_reason_and_accepts_with_reason(
    tmp_path: Path, monkeypatch, capsys, status: str
) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    refused = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo, artifact, "--delivery-kind", "human-backend", "--verification-status", status
        ),
    )
    assert refused.returncode != 0
    assert "--verification-reason" in refused.stderr
    assert not (repo / ".charness" / "announcement" / "announcements.jsonl").exists()

    accepted = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--verification-status",
            status,
            "--verification-reason",
            "explicit reason",
        ),
    )
    assert accepted.returncode == 0, accepted.stderr
    record = _read_record(repo)
    assert record["verification"]["reason"] == "explicit reason"


def test_draft_only_and_release_notes_do_not_require_verification(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    for delivery_kind in ("none", "release-notes"):
        repo, artifact = _prepare_artifact(tmp_path / delivery_kind)
        result = _run(
            monkeypatch, capsys, *_record_args(repo, artifact, "--delivery-kind", delivery_kind)
        )
        assert result.returncode == 0, result.stderr
        record = _read_record(repo)
        assert record["verification"] is None


def test_schema_round_trip_with_delivery_handle(tmp_path: Path, monkeypatch, capsys) -> None:
    repo, artifact = _prepare_artifact(tmp_path)
    result = _run(
        monkeypatch,
        capsys,
        *_record_args(
            repo,
            artifact,
            "--delivery-kind",
            "human-backend",
            "--delivery-target",
            "#eng",
            "--delivery-handle",
            "1700000000.123456",
            "--verification-status",
            "confirmed",
            "--verification-channel",
            "adapter-probe",
        ),
    )
    assert result.returncode == 0, result.stderr
    record = _read_record(repo)
    assert record["delivery_handle"] == "1700000000.123456"
    assert record["verification"] == {"channel": "adapter-probe", "status": "confirmed"}
    assert set(record) == {
        "recorded_at",
        "head_commit",
        "delivery_kind",
        "delivery_target",
        "delivery_handle",
        "artifact_path",
        "artifact_path_provenance",
        "commits",
        "verification",
        "delivery_kind_check",
    }


# --- _default_run_shell timeout handling -----------------------------------


def test_default_run_shell_returns_completed_process_on_timeout(
    tmp_path: Path, monkeypatch
) -> None:
    # PROBE_TIMEOUT_SECONDS is 120s -- too long to actually wait on. Return the
    # guard's timeout result directly, without ever sleeping; the guard owns the
    # timeout-as-result conversion and its stderr marker.
    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command,
            124,
            "partial out",
            "timed out after 120s while running `sleep 999`",
        )

    monkeypatch.setattr(verification_lib, "run_process", fake_run)
    result = verification_lib._default_run_shell("sleep 999", cwd=tmp_path)
    assert result.returncode == 124
    assert result.args == "sleep 999"
    assert result.stdout == "partial out"
    assert result.stderr == (
        f"timed out after {verification_lib.PROBE_TIMEOUT_SECONDS:g}s while running `sleep 999`"
    )


# --- record_announcement.py bootstrap shim ----------------------------------


def test_record_announcement_shim_not_found_raises_import_error(
    tmp_path: Path, monkeypatch
) -> None:
    # Mirrors tests/test_adapter_shim_inprocess_coverage.py's shim-not-found
    # forcing technique. record_announcement.py is a skill CLI, not one of the
    # named resolver scripts that test's filename allowlist discovers, so its
    # copy of the same canonical `raise ImportError` guard needs its own force.
    isolated = tmp_path / "deep" / "nest" / "record_announcement.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(ANNOUNCEMENT_RECORD, "__file__", str(isolated))
    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        ANNOUNCEMENT_RECORD._load_skill_runtime_bootstrap()
