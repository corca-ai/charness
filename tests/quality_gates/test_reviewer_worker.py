"""Process-facing tests for the portable typed review worker."""

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
SCRIPT = ROOT / "skills/shared/scripts/reviewer_worker.py"


def _executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Return a structured result.\n", encoding="utf-8")
    schema = tmp_path / "schema.json"
    schema.write_text(
        json.dumps(
            {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "kind",
                    "reason",
                    "packet_sha256",
                    "reviewed_input_identity_sha256",
                    "capability_non_claims",
                    "capability_non_claims_sha256",
                ],
                "properties": {
                    "kind": {"const": "review"},
                    "reason": {"type": "string"},
                    "packet_sha256": {"type": "string"},
                    "reviewed_input_identity_sha256": {"type": "string"},
                    "capability_non_claims": {"type": "array"},
                    "capability_non_claims_sha256": {"type": "string"},
                },
            }
        ),
        encoding="utf-8",
    )
    capability = tmp_path / "capability.json"
    capability.write_text(json.dumps(ready_capability("attempt-1")), encoding="utf-8")
    return workspace, prompt, schema, capability, tmp_path / "result.json", tmp_path / "receipt.json"


def _run(
    tmp_path: Path,
    backend: str,
    workspace: Path,
    prompt: Path,
    schema: Path,
    capability: Path,
    output: Path,
    receipt: Path,
    *,
    timeout: str = "2",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--backend",
            backend,
            "--workspace",
            str(workspace.relative_to(tmp_path)),
            "--prompt-file",
            str(prompt.relative_to(tmp_path)),
            "--schema-file",
            str(schema.relative_to(tmp_path)),
            "--capability-file",
            str(capability.relative_to(tmp_path)),
            "--output-file",
            str(output.relative_to(tmp_path)),
            "--receipt-file",
            str(receipt.relative_to(tmp_path)),
            "--attempt-id",
            "attempt-1",
            "--scope",
            "scope-1",
            "--packet-identity",
            "p" * 64,
            "--reviewed-input-identity",
            "i" * 64,
            "--parent-receipt-identity",
            "parent-1",
            "--boundary-fingerprint",
            "boundary-1",
            "--timeout-seconds",
            timeout,
            "--run-id",
            "test-run",
        ],
        cwd=tmp_path,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )


def test_codex_worker_publishes_only_schema_valid_fresh_output(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
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
printf '%s\n' '{"kind":"review","reason":"fresh","capability_non_claims":[],"capability_non_claims_sha256":"__EMPTY_NON_CLAIMS_SHA256__","packet_sha256":"pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp","reviewed_input_identity_sha256":"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"}' > "$out"
""",
    )
    script = (bin_dir / "codex").read_text(encoding="utf-8").replace("__EMPTY_NON_CLAIMS_SHA256__", EMPTY_NON_CLAIMS_SHA256)
    (bin_dir / "codex").write_text(script, encoding="utf-8")
    (bin_dir / "codex").chmod(0o755)
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt)
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "succeeded"
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "fresh"
    record = json.loads(receipt.read_text(encoding="utf-8"))
    assert record["status"] == "succeeded"
    assert record["output_fresh"] is True
    assert Path(record["output_file"]).is_absolute()
    assert record["attempt_id"] == "attempt-1"
    assert record["packet_identity"] == "p" * 64
    assert record["capability_status"] == "ready"
    assert record["capability_launch_envelope_sha256"] == record["capability_envelope_sha256"]
    assert record["capability_collection_envelope_sha256"] == record["capability_envelope_sha256"]
    assert record["effective_capabilities"]["filesystem"]["write"] == "denied"
    assert record["effective_capabilities"]["external_effects"]["state"] == "denied"


def test_transport_unestablished_is_typed_and_backend_is_not_started(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
    payload = json.loads(capability.read_text(encoding="utf-8"))
    payload["effective_capabilities"]["external_reads"]["state"] = "unproved"
    for entry in payload["effective_capabilities"]["external_reads"]["entries"]:
        entry["state"] = "unproved"
    payload["preflight"][0].update(
        {
            "status": "transport-unestablished",
            "reached_layer": "none",
            "observations": {"transport": {"status": "unestablished"}},
        }
    )
    capability.write_text(json.dumps(payload), encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    invoked = tmp_path / "backend-invoked"
    _executable(bin_dir / "codex", f"#!/bin/sh\ntouch {invoked}\n")
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt)
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 1
    record = json.loads(receipt.read_text(encoding="utf-8"))
    assert record["status"] == "transport-unestablished"
    assert record["capability_status"] == "transport-unestablished"
    assert not invoked.exists()
    assert not output.exists()


def test_capability_drift_between_launch_and_collection_is_refused(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _executable(
        bin_dir / "codex",
        f'''#!/bin/sh
out=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then out="$2"; shift 2; continue; fi
  shift
done
cat >/dev/null
printf '%s\\n' '{{"kind":"review","reason":"fresh","packet_sha256":"pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp","reviewed_input_identity_sha256":"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"}}' > "$out"
sed -i 's/fixture-config-1/fixture-config-2/' {capability}
''',
    )
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt)
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 1
    record = json.loads(receipt.read_text(encoding="utf-8"))
    assert record["status"] == "probe-invalid"
    assert "changed between launch and collection" in record["error"]
    assert not output.exists()


def test_colliding_artifact_paths_are_refused_before_backend_start(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, _receipt_path = _inputs(tmp_path)
    result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, output)
    assert result.returncode == 1
    record = json.loads(output.read_text(encoding="utf-8"))
    assert record["status"] == "input-invalid"
    assert "distinct files" in record["error"]


def test_preexisting_output_is_refused_and_gets_a_typed_receipt(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
    output.write_text('{"kind":"review","reason":"stale"}\n', encoding="utf-8")
    result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt)
    assert result.returncode == 1
    record = json.loads(receipt.read_text(encoding="utf-8"))
    assert record["status"] == "stale-artifact-refused"
    assert record["output_fresh"] is False
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "stale"


def test_schema_failure_does_not_publish_backend_output(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
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
printf '%s\n' '{"kind":"not-the-contract"}' > "$out"
""",
    )
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt)
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 1
    record = json.loads(receipt.read_text(encoding="utf-8"))
    assert record["status"] == "schema-invalid"
    assert not output.exists()


def test_result_identity_mismatch_is_schema_invalid_even_when_provider_schema_allows_it(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
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
printf '%s\n' '{"kind":"review","reason":"wrong packet","packet_sha256":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx","reviewed_input_identity_sha256":"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"}' > "$out"
""",
    )
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt)
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 1
    assert json.loads(receipt.read_text(encoding="utf-8"))["status"] == "schema-invalid"
    assert not output.exists()


def test_timeout_is_finite_and_typed_without_timeout_binary_fallback(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _executable(
        bin_dir / "codex",
        "#!/bin/sh\nsleep 1\n",
    )
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt, timeout="0.05")
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 1
    record = json.loads(receipt.read_text(encoding="utf-8"))
    assert record["status"] == "timed-out"
    assert record["timeout_seconds"] == 0.05
    assert not output.exists()


def test_timeout_terminates_backend_process_group(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    child_pid = tmp_path / "child.pid"
    _executable(
        bin_dir / "codex",
        "#!/bin/sh\n"
        "(sleep 30) &\n"
        f"child=$!\nprintf '%s\\n' \"$child\" > {child_pid}\n"
        "wait \"$child\"\n",
    )
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "codex_exec", workspace, prompt, schema, capability, output, receipt, timeout="0.05")
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 1
    assert json.loads(receipt.read_text(encoding="utf-8"))["status"] == "timed-out"
    child = int(child_pid.read_text(encoding="utf-8"))
    proc_stat = Path(f"/proc/{child}/stat")
    if proc_stat.exists():
        assert proc_stat.read_text(encoding="utf-8").split()[2] == "Z"


def test_claude_structured_output_is_normalized_and_schema_checked(tmp_path: Path) -> None:
    workspace, prompt, schema, capability, output, receipt = _inputs(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _executable(
        bin_dir / "claude",
        """#!/bin/sh
cat >/dev/null
printf '%s\n' '{"is_error":false,"structured_output":{"kind":"review","reason":"claude","capability_non_claims":[],"capability_non_claims_sha256":"__EMPTY_NON_CLAIMS_SHA256__","packet_sha256":"pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp","reviewed_input_identity_sha256":"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"}}'
        """,
    )
    script = (bin_dir / "claude").read_text(encoding="utf-8").replace("__EMPTY_NON_CLAIMS_SHA256__", EMPTY_NON_CLAIMS_SHA256)
    (bin_dir / "claude").write_text(script, encoding="utf-8")
    (bin_dir / "claude").chmod(0o755)
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:{old_path}"
    try:
        result = _run(tmp_path, "claude_p", workspace, prompt, schema, capability, output, receipt)
    finally:
        os.environ["PATH"] = old_path
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "claude"
