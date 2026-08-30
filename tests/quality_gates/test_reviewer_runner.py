"""End-to-end contract for the repo-owned file-backed runner selector."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import yaml

from tests.quality_gates.reviewer_capability_support import (
    EMPTY_NON_CLAIMS_SHA256,
    ready_capability,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/shared/scripts/run_reviewer_worker.py"
RESULT_SCHEMA = ROOT / "skills/shared/references/bounded-review-result.schema.json"


def _executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _common(tmp_path: Path) -> dict[str, Path]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    prompt = tmp_path / "prompt.md"
    prompt.write_text("return the typed result\n", encoding="utf-8")
    schema = tmp_path / "schema.json"
    schema.write_text(RESULT_SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    capability = tmp_path / "capability.json"
    capability.write_text(json.dumps(ready_capability("attempt-1")), encoding="utf-8")
    return {
        "workspace": workspace,
        "prompt": prompt,
        "schema": schema,
        "capability": capability,
        "ledger": tmp_path / "delivery.json",
        "output": tmp_path / "result.json",
        "receipt": tmp_path / "receipt.json",
        "report": tmp_path / "report.yaml",
    }


def _object_schemas(node: object) -> list[dict[str, object]]:
    if isinstance(node, dict):
        found = [node] if node.get("type") == "object" else []
        for value in node.values():
            found.extend(_object_schemas(value))
        return found
    if isinstance(node, list):
        found: list[dict[str, object]] = []
        for value in node:
            found.extend(_object_schemas(value))
        return found
    return []


def test_bounded_review_schema_is_provider_strict_for_every_object() -> None:
    schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
    objects = _object_schemas(schema)
    assert objects
    assert all(item.get("additionalProperties") is False for item in objects)


def test_file_backed_runner_binds_receipt_ledger_and_report(tmp_path: Path) -> None:
    files = _common(tmp_path)
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nreviewer_runner:\n  mode: file-backed-worker\n  backend: codex_exec\n  timeout_seconds: 900\n",
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _executable(
        bin_dir / "codex",
        """#!/bin/sh
out=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then out="$2"; shift 2; continue; fi
  shift
done
printf '%s\n' '{"kind":"charness.bounded_review.v1","lens":"runner test","verdict":"pass","findings":[],"counterweight_triage":[],"next_move":"test","non_claims":["test"],"capability_non_claims":[],"capability_non_claims_sha256":"__EMPTY_NON_CLAIMS_SHA256__","packet_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","reviewed_input_identity_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}' > "$out"
""",
    )
    script = (bin_dir / "codex").read_text(encoding="utf-8").replace("__EMPTY_NON_CLAIMS_SHA256__", EMPTY_NON_CLAIMS_SHA256)
    (bin_dir / "codex").write_text(script, encoding="utf-8")
    (bin_dir / "codex").chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    command = [
        sys.executable,
        str(SCRIPT),
        "--repo-root",
        str(tmp_path),
        "--backend",
        "codex_exec",
        "--prompt-file",
        str(files["prompt"]),
        "--schema-file",
        str(files["schema"]),
        "--capability-file",
        str(files["capability"]),
        "--scope",
        "scope-1",
        "--packet-identity",
        "a" * 64,
        "--reviewed-input-identity",
        "a" * 64,
        "--attempt-id",
        "attempt-1",
        "--parent-receipt-identity",
        "parent-1",
        "--boundary-fingerprint",
        "boundary-1",
        "--ledger-file",
        str(files["ledger"]),
        "--output-file",
        str(files["output"]),
        "--receipt-file",
        str(files["receipt"]),
        "--report-file",
        str(files["report"]),
    ]
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 0, result.stderr
    assert report["approval_eligible"] is True
    assert report["execution_mode"] == "file-backed-worker"
    assert yaml.safe_load(files["report"].read_text(encoding="utf-8"))["approval_eligible"] is True
    ledger = json.loads(files["ledger"].read_text(encoding="utf-8"))
    assert [event["state"] for event in ledger["attempts"][0]["history"]][:2] == [
        "spawn-accepted",
        "running",
    ]


def test_file_backed_runner_resolves_relative_artifacts_once_from_repo_root(tmp_path: Path) -> None:
    files = _common(tmp_path)
    unrelated = tmp_path / "unrelated-cwd"
    unrelated.mkdir()
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nreviewer_runner:\n  mode: file-backed-worker\n  backend: codex_exec\n  timeout_seconds: 900\n",
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _executable(
        bin_dir / "codex",
        """#!/bin/sh
out=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then out="$2"; shift 2; continue; fi
  shift
done
cat >/dev/null
printf '%s\\n' '{"kind":"charness.bounded_review.v1","lens":"runner path test","verdict":"pass","findings":[],"counterweight_triage":[],"next_move":"test","non_claims":["test"],"capability_non_claims":[],"capability_non_claims_sha256":"__EMPTY_NON_CLAIMS_SHA256__","packet_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","reviewed_input_identity_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}' > "$out"
        """,
    )
    script = (bin_dir / "codex").read_text(encoding="utf-8").replace("__EMPTY_NON_CLAIMS_SHA256__", EMPTY_NON_CLAIMS_SHA256)
    (bin_dir / "codex").write_text(script, encoding="utf-8")
    (bin_dir / "codex").chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    command = [
        sys.executable,
        str(SCRIPT),
        "--repo-root", str(tmp_path),
        "--backend", "codex_exec",
        "--prompt-file", "prompt.md",
        "--schema-file", "schema.json",
        "--capability-file", "capability.json",
        "--scope", "scope-1",
        "--packet-identity", "a" * 64,
        "--reviewed-input-identity", "a" * 64,
        "--attempt-id", "attempt-1",
        "--parent-receipt-identity", "parent-1",
        "--boundary-fingerprint", "boundary-1",
        "--ledger-file", "delivery.json",
        "--output-file", "result.json",
        "--receipt-file", "receipt.json",
        "--report-file", "report.yaml",
    ]
    result = subprocess.run(command, cwd=unrelated, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert all(path.exists() for path in files.values())
    assert not (unrelated / "result.json").exists()
    assert not (unrelated / "receipt.json").exists()
    assert not (unrelated / "report.yaml").exists()
    receipt = json.loads(files["receipt"].read_text(encoding="utf-8"))
    report = yaml.safe_load(files["report"].read_text(encoding="utf-8"))
    assert receipt["output_file"] == str(files["output"].resolve())
    assert receipt["stdout_file"] == str((tmp_path / "result.json.stdout").resolve())
    assert receipt["stderr_file"] == str((tmp_path / "result.json.stderr").resolve())
    assert report["receipt_path"] == str(files["receipt"].resolve())


def test_file_backed_runner_rejects_caller_backend_override(tmp_path: Path) -> None:
    files = _common(tmp_path)
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nreviewer_runner:\n  mode: file-backed-worker\n  backend: codex_exec\n  timeout_seconds: 900\n",
        encoding="utf-8",
    )
    command = [
        sys.executable,
        str(SCRIPT),
        "--repo-root", str(tmp_path),
        "--backend", "claude_p",
        "--prompt-file", str(files["prompt"]),
        "--schema-file", str(files["schema"]),
        "--capability-file", str(files["capability"]),
        "--scope", "scope-1",
        "--packet-identity", "packet-1",
        "--reviewed-input-identity", "a" * 64,
        "--attempt-id", "attempt-1",
        "--parent-receipt-identity", "parent-1",
        "--boundary-fingerprint", "boundary-1",
        "--ledger-file", str(files["ledger"]),
        "--output-file", str(files["output"]),
        "--receipt-file", str(files["receipt"]),
        "--report-file", str(files["report"]),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "runner-invalid"
    assert "authoritative" in payload["error"]


def test_file_backed_runner_does_not_turn_explicit_zero_timeout_into_adapter_default(tmp_path: Path) -> None:
    files = _common(tmp_path)
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nreviewer_runner:\n  mode: file-backed-worker\n  backend: codex_exec\n  timeout_seconds: 900\n",
        encoding="utf-8",
    )
    command = [
        sys.executable,
        str(SCRIPT),
        "--repo-root", str(tmp_path),
        "--backend", "codex_exec",
        "--prompt-file", str(files["prompt"]),
        "--schema-file", str(files["schema"]),
        "--capability-file", str(files["capability"]),
        "--scope", "scope-1",
        "--packet-identity", "packet-1",
        "--reviewed-input-identity", "a" * 64,
        "--attempt-id", "attempt-1",
        "--parent-receipt-identity", "parent-1",
        "--boundary-fingerprint", "boundary-1",
        "--ledger-file", str(files["ledger"]),
        "--output-file", str(files["output"]),
        "--receipt-file", str(files["receipt"]),
        "--report-file", str(files["report"]),
        "--timeout-seconds", "0",
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "runner-invalid"
    assert "timeout_seconds" in payload["error"]


def test_file_backed_runner_refuses_typed_subagent_mode(tmp_path: Path) -> None:
    files = _common(tmp_path)
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nreviewer_runner:\n  mode: typed-subagent\n  backend: codex_exec\n", encoding="utf-8"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--prompt-file",
            str(files["prompt"]),
            "--capability-file",
            str(files["capability"]),
            "--scope",
            "scope-1",
            "--packet-identity",
            "packet-1",
            "--reviewed-input-identity",
            "a" * 64,
            "--attempt-id",
            "attempt-1",
            "--parent-receipt-identity",
            "parent-1",
            "--boundary-fingerprint",
            "boundary-1",
            "--ledger-file",
            str(files["ledger"]),
            "--output-file",
            str(files["output"]),
            "--receipt-file",
            str(files["receipt"]),
            "--report-file",
            str(files["report"]),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 2
    assert payload["execution_mode"] == "typed-subagent"
    assert payload["approval_eligible"] is False
