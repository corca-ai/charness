from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/public/critique/scripts/record_round_findings.py"
PLUGIN_SCRIPT = ROOT / "plugins/charness/skills/critique/scripts/record_round_findings.py"
WORKER_FIXTURE = ROOT / "charness-artifacts/critique/workers/2026-08-25-consumer-boundary-r2"
FIXTURE_BOUNDARY_SHA256 = "26c0810296d4912caa89e4fbe8d23d54986e932a1098c4fe76e48879081604c3"


def load_recorder_module():
    spec = importlib.util.spec_from_file_location("record_round_findings_inprocess", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_recorder(
    repo: Path, *args: str, input_text: str | None = None, script: Path = SCRIPT
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(script), "--repo-root", str(repo), *args],
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def seed_snapshot(repo: Path, window_id: str) -> Path:
    path = repo / ".charness" / "reviewer-boundary" / "snapshot.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"head": "abc", "window": {"id": window_id}}), encoding="utf-8")
    return path


def seed_worker_fixture(repo: Path, boundary_sha256: str) -> Path:
    worker_dir = repo / "charness-artifacts/critique/workers/2026-08-25-consumer-boundary-r2"
    shutil.copytree(WORKER_FIXTURE, worker_dir, dirs_exist_ok=True)
    for artifact in worker_dir.rglob("*"):
        if not artifact.is_file():
            continue
        text = artifact.read_text(encoding="utf-8")
        text = text.replace(str(ROOT), str(repo))
        text = text.replace("/home/hwidong/codes/charness", str(repo))
        text = text.replace(FIXTURE_BOUNDARY_SHA256, boundary_sha256)
        if artifact.name == "report.yaml":
            text = text.replace(
                "parent_receipt_identity: 2026-08-25-consumer-boundary-r2-parent\nprovenance:",
                "parent_receipt_identity: 2026-08-25-consumer-boundary-r2-parent\n"
                "producer_run_id: 2026-08-25-consumer-boundary-r2-run\nprovenance:",
            )
        artifact.write_text(text, encoding="utf-8")
    receipt_file = worker_dir / "receipt.json"
    receipt_payload = json.loads(receipt_file.read_text(encoding="utf-8"))
    envelope_payload = {
        "schema_version": "charness.capability_envelope.v1",
        "task_kind": "read",
        "requested_capabilities": receipt_payload["requested_capabilities"],
        "effective_capabilities": receipt_payload["effective_capabilities"],
        "preflight": receipt_payload["preflight"],
        "capability_non_claims": receipt_payload["capability_non_claims"],
    }
    current_hash = receipt_payload["capability_envelope_sha256"]
    refreshed_hash = hashlib.sha256(
        json.dumps(
            envelope_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    if current_hash != refreshed_hash:
        for artifact in worker_dir.rglob("*"):
            if artifact.is_file():
                text = artifact.read_text(encoding="utf-8")
                artifact.write_text(text.replace(current_hash, refreshed_hash), encoding="utf-8")
    return worker_dir / "report.yaml"


def test_records_typed_worker_findings_with_explicit_provenance(tmp_path: Path) -> None:
    window_id = "w-20260820T110000Z-round-1"
    snapshot = seed_snapshot(tmp_path, window_id)
    report = seed_worker_fixture(tmp_path, hashlib.sha256(snapshot.read_bytes()).hexdigest())
    result_file = report.with_name("result.json")

    result = run_recorder(
        tmp_path,
        "--round",
        "1",
        "--window-id",
        window_id,
        "--boundary-snapshot",
        str(snapshot),
        "--worker-report",
        str(report.relative_to(tmp_path)),
        "--recorded-date",
        "2026-08-20",
    )

    assert result.returncode == 0, result.stderr
    receipt = yaml.safe_load(result.stdout)
    assert receipt["path"] == f"charness-artifacts/critique/rounds/2026-08-20-{window_id}.md"
    record = tmp_path / receipt["path"]
    text = record.read_text(encoding="utf-8")
    assert f"Boundary window id: `{window_id}`" in text
    assert "## Reviewer Provenance" in text
    assert "Typed verdict: `block`" in text
    assert "Reviewer execution identity: `attempt_id=2026-08-25-consumer-boundary-r2" in text
    assert json.loads(result_file.read_text(encoding="utf-8")) == json.loads(
        text.split("## Findings Returned\n\n", 1)[1]
    )
    assert "## Goal Evidence Lineage" in text
    assert receipt["goal_lineage"]["disposition"] == "not-goal-bound"
    assert receipt["boundary_snapshot_sha256"] == hashlib.sha256(snapshot.read_bytes()).hexdigest()
    assert receipt["findings_sha256"] == hashlib.sha256(result_file.read_bytes()).hexdigest()
    assert receipt["worker_report"] == report.relative_to(tmp_path).as_posix()
    assert receipt["worker_result"] == result_file.relative_to(tmp_path).as_posix()


def test_refuses_raw_same_context_findings_file(tmp_path: Path) -> None:
    window_id = "w-raw-rejected"
    snapshot = seed_snapshot(tmp_path, window_id)
    findings = tmp_path / "findings.md"
    findings.write_text("same-context text\n", encoding="utf-8")

    result = run_recorder(
        tmp_path,
        "--round",
        "1",
        "--window-id",
        window_id,
        "--boundary-snapshot",
        str(snapshot),
        "--worker-report",
        str(tmp_path / "missing-report.yaml"),
        "--findings-file",
        str(findings),
    )

    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr
    assert not (tmp_path / "charness-artifacts").exists()


def test_exported_plugin_recorder_accepts_the_same_bound_worker_result(tmp_path: Path) -> None:
    window_id = "w-plugin"
    snapshot = seed_snapshot(tmp_path, window_id)
    report = seed_worker_fixture(tmp_path, hashlib.sha256(snapshot.read_bytes()).hexdigest())

    result = run_recorder(
        tmp_path,
        "--round",
        "1",
        "--window-id",
        window_id,
        "--boundary-snapshot",
        str(snapshot),
        "--worker-report",
        str(report),
        "--recorded-date",
        "2026-08-20",
        script=PLUGIN_SCRIPT,
    )

    assert result.returncode == 0, result.stdout
    receipt = yaml.safe_load(result.stdout)
    assert receipt["review_verdict"] == "block"


def test_refuses_delivered_report_without_explicit_producer_identity(tmp_path: Path) -> None:
    window_id = "w-missing-producer"
    snapshot = seed_snapshot(tmp_path, window_id)
    report = seed_worker_fixture(tmp_path, hashlib.sha256(snapshot.read_bytes()).hexdigest())
    report.write_text(
        report.read_text(encoding="utf-8").replace(
            "producer_run_id: 2026-08-25-consumer-boundary-r2-run\n", ""
        ),
        encoding="utf-8",
    )

    result = run_recorder(
        tmp_path,
        "--round",
        "1",
        "--window-id",
        window_id,
        "--boundary-snapshot",
        str(snapshot),
        "--worker-report",
        str(report),
    )

    assert result.returncode == 2
    assert "producer_run_id" in yaml.safe_load(result.stdout)["error"]
    assert not (tmp_path / "charness-artifacts/critique/rounds").exists()


def test_refuses_snapshot_from_another_round(tmp_path: Path) -> None:
    snapshot = seed_snapshot(tmp_path, "w-round-1")
    result = run_recorder(
        tmp_path,
        "--round",
        "2",
        "--window-id",
        "w-round-2",
        "--boundary-snapshot",
        str(snapshot),
        "--worker-report",
        str(tmp_path / "missing-report.yaml"),
    )

    assert result.returncode == 2
    assert "window id mismatch" in yaml.safe_load(result.stdout)["error"]
    assert not (tmp_path / "charness-artifacts").exists()


def test_refuses_overwrite_of_prior_round_record(tmp_path: Path) -> None:
    window_id = "w-round-1"
    snapshot = seed_snapshot(tmp_path, window_id)
    report = seed_worker_fixture(tmp_path, hashlib.sha256(snapshot.read_bytes()).hexdigest())
    args = (
        "--round",
        "1",
        "--window-id",
        window_id,
        "--boundary-snapshot",
        str(snapshot),
        "--worker-report",
        str(report),
        "--recorded-date",
        "2026-08-20",
    )
    first = run_recorder(tmp_path, *args)
    second = run_recorder(tmp_path, *args)

    assert first.returncode == 0
    assert second.returncode == 2
    assert "refusing overwrite" in yaml.safe_load(second.stdout)["error"]
    assert '"verdict":"block"' in (
        tmp_path / "charness-artifacts/critique/rounds/2026-08-20-w-round-1.md"
    ).read_text(encoding="utf-8")


def test_skill_contract_requires_immediate_round_record_and_next_round_read() -> None:
    text = (ROOT / "skills/public/critique/SKILL.md").read_text(encoding="utf-8")
    assert "record_round_findings.py" in text
    assert "--window-id <id>" in text
    assert "--boundary-snapshot <path>" in text
    assert "--worker-report <path>" in text
    assert "typed worker result" in text
    assert "round `n+1`" in text
    assert "reads as prior evidence" in text


def test_inprocess_recorder_covers_rejection_boundaries(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_recorder_module()
    window_id = "w-inprocess"
    snapshot = seed_snapshot(tmp_path, window_id)
    report = seed_worker_fixture(tmp_path, hashlib.sha256(snapshot.read_bytes()).hexdigest())

    receipt = module.record_round(
        tmp_path,
        round_number=1,
        window_id=window_id,
        snapshot=str(snapshot),
        worker_report=str(report),
        recorded_date="2026-08-20",
    )
    assert receipt["window_id"] == window_id

    relative_snapshot = snapshot.relative_to(tmp_path).as_posix()
    assert module._read_snapshot(tmp_path, relative_snapshot, window_id)[0] == relative_snapshot

    with pytest.raises(module.RoundFindingsError, match="path must stay under repo root"):
        module._repo_relative(tmp_path, Path("/tmp/outside-round-record"))
    with pytest.raises(module.RoundFindingsError, match="snapshot not found"):
        module._read_snapshot(tmp_path, "missing.json", window_id)

    malformed = tmp_path / "malformed.json"
    malformed.write_bytes(b"not-json")
    with pytest.raises(module.RoundFindingsError, match="snapshot is unreadable"):
        module._read_snapshot(tmp_path, str(malformed), window_id)

    with pytest.raises(module.RoundFindingsError, match="worker report is unreadable or unsafe"):
        module._read_worker_report(tmp_path, "/tmp/round-outside-worker-report.yaml")

    with pytest.raises(module.RoundFindingsError, match="window id may contain"):
        module._record_path(tmp_path, "2026-08-20", "bad/id")
    with pytest.raises(module.RoundFindingsError, match="ISO-8601"):
        module._record_path(tmp_path, "not-a-date", window_id)
    with pytest.raises(module.RoundFindingsError, match="positive integer"):
        module.record_round(
            tmp_path,
            round_number=0,
            window_id=window_id,
            snapshot=str(snapshot),
            worker_report=str(report),
            recorded_date="2026-08-20",
        )

    original_write_text = Path.write_text

    def fail_write(self, *args, **kwargs):
        if self.name == "2026-08-21-w-write-error.md":
            raise OSError("simulated write failure")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_write)
    write_snapshot = tmp_path / "write-snapshot.json"
    write_snapshot.write_text(
        json.dumps({"head": "abc", "window": {"id": "w-write-error"}}),
        encoding="utf-8",
    )
    write_report = seed_worker_fixture(
        tmp_path, hashlib.sha256(write_snapshot.read_bytes()).hexdigest()
    )
    with pytest.raises(module.RoundFindingsError, match="could not write round record"):
        module.record_round(
            tmp_path,
            round_number=2,
            window_id="w-write-error",
            snapshot=str(write_snapshot),
            worker_report=str(write_report),
            recorded_date="2026-08-21",
        )

    class HelperPath:
        def __init__(self, value):
            self.value = value

        def resolve(self):
            return self

        @property
        def parents(self):
            return [self]

        def __truediv__(self, _other):
            return self

        def is_file(self):
            return True

    monkeypatch.setattr(module, "Path", HelperPath)
    monkeypatch.setattr(
        module.importlib.util,
        "spec_from_file_location",
        lambda *_args, **_kwargs: SimpleNamespace(loader=None),
    )
    module._emit_yaml({"fallback": True})
    assert '"fallback": true' in capsys.readouterr().out
