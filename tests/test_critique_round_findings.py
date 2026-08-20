from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/public/critique/scripts/record_round_findings.py"


def load_recorder_module():
    spec = importlib.util.spec_from_file_location("record_round_findings_inprocess", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_recorder(
    repo: Path, *args: str, input_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(repo), *args],
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


def test_records_findings_with_snapshot_and_content_digests(tmp_path: Path) -> None:
    window_id = "w-20260820T110000Z-round-1"
    snapshot = seed_snapshot(tmp_path, window_id)
    findings = tmp_path / "findings.md"
    findings.write_text("Act Before Ship: the next round must read this.\n", encoding="utf-8")

    result = run_recorder(
        tmp_path,
        "--round",
        "1",
        "--window-id",
        window_id,
        "--boundary-snapshot",
        str(snapshot),
        "--findings-file",
        str(findings),
        "--recorded-date",
        "2026-08-20",
    )

    assert result.returncode == 0, result.stderr
    receipt = yaml.safe_load(result.stdout)
    assert receipt["path"] == f"charness-artifacts/critique/rounds/2026-08-20-{window_id}.md"
    record = tmp_path / receipt["path"]
    text = record.read_text(encoding="utf-8")
    assert f"Boundary window id: `{window_id}`" in text
    assert "Act Before Ship: the next round must read this." in text
    assert receipt["boundary_snapshot_sha256"] == hashlib.sha256(snapshot.read_bytes()).hexdigest()
    assert receipt["findings_sha256"] == hashlib.sha256(findings.read_bytes()).hexdigest()


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
        input_text="finding",
    )

    assert result.returncode == 2
    assert "window id mismatch" in yaml.safe_load(result.stdout)["error"]
    assert not (tmp_path / "charness-artifacts").exists()


def test_refuses_overwrite_of_prior_round_record(tmp_path: Path) -> None:
    window_id = "w-round-1"
    snapshot = seed_snapshot(tmp_path, window_id)
    args = (
        "--round",
        "1",
        "--window-id",
        window_id,
        "--boundary-snapshot",
        str(snapshot),
        "--recorded-date",
        "2026-08-20",
    )
    first = run_recorder(tmp_path, *args, input_text="first finding")
    second = run_recorder(tmp_path, *args, input_text="replacement finding")

    assert first.returncode == 0
    assert second.returncode == 2
    assert "refusing overwrite" in yaml.safe_load(second.stdout)["error"]
    assert "first finding" in (
        tmp_path / "charness-artifacts/critique/rounds/2026-08-20-w-round-1.md"
    ).read_text(encoding="utf-8")


def test_skill_contract_requires_immediate_round_record_and_next_round_read() -> None:
    text = (ROOT / "skills/public/critique/SKILL.md").read_text(encoding="utf-8")
    assert "record_round_findings.py" in text
    assert "--window-id <id>" in text
    assert "--boundary-snapshot <path>" in text
    assert "round `n+1`" in text
    assert "reads as prior evidence" in text


def test_inprocess_recorder_covers_rejection_boundaries(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_recorder_module()
    window_id = "w-inprocess"
    snapshot = seed_snapshot(tmp_path, window_id)
    findings = tmp_path / "findings.md"
    findings.write_text("finding\n", encoding="utf-8")

    receipt = module.record_round(
        tmp_path,
        round_number=1,
        window_id=window_id,
        snapshot=str(snapshot),
        findings=str(findings),
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

    findings_dir = tmp_path / "findings-dir"
    findings_dir.mkdir()
    with pytest.raises(module.RoundFindingsError, match="findings file is unreadable"):
        module._read_findings(str(findings_dir))
    empty = tmp_path / "empty.md"
    empty.write_bytes(b"\n")
    with pytest.raises(module.RoundFindingsError, match="must not be empty"):
        module._read_findings(str(empty))
    invalid_utf8 = tmp_path / "invalid.md"
    invalid_utf8.write_bytes(b"\xff")
    with pytest.raises(module.RoundFindingsError, match="must be UTF-8"):
        module._read_findings(str(invalid_utf8))

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
            findings=str(findings),
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
    with pytest.raises(module.RoundFindingsError, match="could not write round record"):
        module.record_round(
            tmp_path,
            round_number=2,
            window_id="w-write-error",
            snapshot=str(write_snapshot),
            findings=str(findings),
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
