from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/public/critique/scripts/record_round_findings.py"


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
