"""End-to-end contract for the repo-owned file-backed runner selector."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import yaml

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
    schema.write_text(
        json.dumps(
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["kind", "reason"],
                "properties": {"kind": {"type": "string", "const": "review"}, "reason": {"type": "string"}},
            }
        ),
        encoding="utf-8",
    )
    return {
        "workspace": workspace,
        "prompt": prompt,
        "schema": schema,
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
printf '%s\n' '{"kind":"review","reason":"fresh"}' > "$out"
""",
    )
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
    ]
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 0, result.stderr
    assert report["approval_eligible"] is True
    assert report["execution_mode"] == "file-backed-worker"
    assert yaml.safe_load(files["report"].read_text(encoding="utf-8"))["approval_eligible"] is True


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
