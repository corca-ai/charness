#!/usr/bin/env python3
"""Packet and semantic-input helpers for the critique review command."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def _semantic_review_paths(packet: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return readable and deleted paths from the verified input identity.

    Packet sections are consumer-defined context; they do not establish that
    the explicitly reviewed artifact reached the worker.  The identity is the
    one source of truth for that artifact.  A deleted path has a bound
    pre-image, but no current path for a read-only worker to open.
    """
    identity = packet.get("reviewed_input_identity")
    if not isinstance(identity, dict):
        return [], []
    raw_paths = identity.get("reviewed_paths")
    raw_content = identity.get("reviewed_content")
    if not isinstance(raw_paths, list) or not isinstance(raw_content, list):
        return [], []
    paths = [path for path in raw_paths if isinstance(path, str) and path]
    deleted = {
        entry.get("path")
        for entry in raw_content
        if isinstance(entry, dict)
        and entry.get("disposition") == "deleted"
        and isinstance(entry.get("path"), str)
    }
    return [path for path in paths if path not in deleted], sorted(deleted)


def _semantic_input_refusal(
    support: Any, root: Path, packet: dict[str, Any], packet_path: Path
) -> None:
    """Refuse a packet whose identity gives the worker no readable input."""
    readable, deleted = _semantic_review_paths(packet)
    identity = packet.get("reviewed_input_identity")
    paths = identity.get("reviewed_paths") if isinstance(identity, dict) else None
    if not isinstance(paths, list) or not paths:
        raise support.RunReviewError(
            "empty-reviewed-paths",
            "packet reviewed input covers zero paths and carries no semantic review input",
            details={
                "packet_path": support.relative(root, packet_path),
                "scope_status": "empty-reviewed-input",
                "section_count": packet.get("section_count", 0),
                "usable": False,
                "remedy": "Provide at least one explicit or changed reviewed path and rerun",
            },
        )
    if not readable and deleted:
        raise support.RunReviewError(
            "deleted-reviewed-paths",
            "packet reviewed input contains only deleted paths and no readable semantic review input",
            details={
                "packet_path": support.relative(root, packet_path),
                "scope_status": "deleted-input-only",
                "section_count": packet.get("section_count", 0),
                "usable": False,
                "deleted_paths": deleted,
                "remedy": "Provide at least one readable reviewed path or a packet with bounded semantic content, then rerun",
            },
        )


def manifest_paths(support: Any, root: Path, manifest: str | None, explicit: list[str] | None) -> list[str]:
    values = list(explicit or [])
    if manifest is not None:
        path = support.repo_path(root, manifest, label="reviewed-paths-file", require_file=True)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            raise support.RunReviewError("path-invalid", f"reviewed-paths-file is unreadable: {path}") from exc
        values.extend(line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#"))
    # `allow_symlink`: the symlink policy for a DECLARED path is owned by
    # `reviewed_input_identity`, which binds a current pointer by link payload and
    # refuses every other symlink. Re-deciding it here refused inputs that owner
    # accepts.
    return sorted(
        {
            support.relative(root, support.repo_path(root, value, label="reviewed path", allow_symlink=True))
            for value in values
        }
    )


def prepare_packet(
    support: Any,
    root: Path,
    args: Any,
    attempt: str,
    reviewed_paths: list[str],
    adapter: dict[str, Any],
    prepare: Path,
) -> Path:
    data = adapter.get("data")
    output_dir = data.get("output_dir", "charness-artifacts/critique") if isinstance(data, dict) else "charness-artifacts/critique"
    output_root = support.repo_path(root, str(output_dir), label="critique output_dir")
    expected = output_root / f"{attempt}-packet.json"
    if expected.exists():
        raise support.RunReviewError("stale-artifact-refused", f"refusing to overwrite existing packet: {expected}")
    command = [
        sys.executable,
        str(prepare),
        "--repo-root", str(root),
        "--prepared-for", args.prepared_for,
        "--slug", attempt,
    ]
    for path in reviewed_paths:
        command.extend(["--reviewed-path", path])
    if args.commit is not None:
        command.extend(["--commit", args.commit])
    if args.changed_range is not None:
        command.extend(["--range", args.changed_range])
    code, stdout, stderr = support.run_command(command, root=root)
    payload = support.yaml_payload(stdout, label="prepare packet")
    packet_name = payload.get("json_path")
    binding = payload.get("reviewed_input_binding")
    usable = binding.get("usable") if isinstance(binding, dict) else None
    if not isinstance(packet_name, str):
        raise support.RunReviewError(
            "packet-invalid", "prepare packet did not return json_path",
            details={"prepare": payload, "stderr": stderr},
        )
    packet = support.repo_path(root, packet_name, label="prepared packet")
    if code != 0 or payload.get("ok") is not True or usable is False:
        binding_data = binding if isinstance(binding, dict) else {}
        reason_code = payload.get("reason_code") or binding_data.get("reason_code")
        if not isinstance(reason_code, str) or not reason_code:
            reason_code = "packet-invalid"
        error = payload.get("error") or binding_data.get("error")
        if not isinstance(error, str) or not error:
            error = "prepared packet is not usable"
        details = {"prepare": payload, "stderr": stderr}
        for field in ("adapter_path", "scope_status", "section_count", "usable", "remedy", "warning"):
            if field in binding_data:
                details[field] = binding_data[field]
            elif field in payload:
                details[field] = payload[field]
        raise support.RunReviewError(reason_code, error, details=details)
    return packet


def read_packet(
    support: Any, root: Path, path_value: str, verifier: Path
) -> tuple[Path, dict[str, Any], str, str, dict[str, Any]]:
    packet = support.repo_path(root, path_value, label="packet-file", require_file=True)
    raw = packet.read_bytes()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise support.RunReviewError("packet-invalid", f"packet-file is not valid JSON: {packet}") from exc
    if not isinstance(payload, dict) or payload.get("kind") != "charness.critique_prepare_packet":
        raise support.RunReviewError("packet-invalid", "packet-file is not a critique prepare packet")
    sections = payload.get("sections")
    section_count = payload.get("section_count")
    if (
        section_count == 0
        or payload.get("scope_status") == "adapter-no-sections"
        or not isinstance(sections, list)
        or not sections
    ):
        raise support.RunReviewError(
            "adapter-no-sections",
            "packet-file declares no packet sections and carries no semantic review input",
            details={
                "packet_path": support.relative(root, packet),
                "scope_status": "adapter-no-sections",
                "section_count": 0,
                "usable": False,
                "remedy": "Provide a packet with at least one declared packet_sections entry and rerun",
            },
        )
    has_content = any(
        isinstance(section, dict)
        and isinstance(section.get("content"), str)
        and bool(section["content"].strip())
        for section in sections
    )
    if not has_content or payload.get("scope_status") == "producer-empty" or payload.get("ok") is not True:
        reason_code = payload.get("reason_code")
        if not isinstance(reason_code, str) or not reason_code:
            reason_code = "producer-empty" if not has_content else "packet-invalid"
        error = payload.get("error")
        if not isinstance(error, str) or not error:
            error = (
                "packet-file sections produced no content"
                if not has_content
                else "packet-file is not usable"
            )
        details = {
            "packet_path": support.relative(root, packet),
            "packet": payload,
            "scope_status": "producer-empty" if not has_content else payload.get("scope_status"),
            "usable": False,
        }
        if isinstance(payload.get("remedy"), str):
            details["remedy"] = payload["remedy"]
        elif not has_content:
            details["remedy"] = "Repair the declared packet producer(s) so at least one section emits semantic review content, then rerun"
        raise support.RunReviewError(reason_code, error, details=details)
    _semantic_input_refusal(support, root, payload, packet)
    identity = payload.get("reviewed_input_identity")
    identity_sha = identity.get("identity_sha256") if isinstance(identity, dict) else None
    if not isinstance(identity_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", identity_sha):
        raise support.RunReviewError("packet-invalid", "packet-file has no valid reviewed input identity")
    packet_sha = hashlib.sha256(raw).hexdigest()
    command = [
        sys.executable, str(verifier), "--repo-root", str(root),
        "--packet-path", support.relative(root, packet),
        "--packet-sha256", packet_sha,
        "--identity-sha256", identity_sha,
    ]
    code, stdout, stderr = support.run_command(command, root=root)
    verification = support.yaml_payload(stdout, label="packet verifier")
    if code != 0 or verification.get("status") != "current":
        raise support.RunReviewError(
            "packet-stale", "packet or reviewed input is not current",
            details={"verification": verification, "stderr": stderr},
        )
    return packet, payload, packet_sha, identity_sha, verification


def default_capability(root: Path) -> dict[str, Any]:
    return {
        "schema_version": "charness.capability_envelope.v1",
        "task_kind": "read",
        "requested_capabilities": {
            "filesystem": {"read_roots": [str(root)], "write_policy": "deny-all", "write_roots": []},
            "external_reads": [],
            "external_effects": {"policy": "deny-all", "entries": []},
        },
        "effective_capabilities": {
            "filesystem": {"write": "denied", "observation": "host"},
            "external_reads": {"state": "unproved", "observation": "host", "entries": []},
            "external_effects": {"state": "denied", "observation": "host"},
            "host_selection_source": "charness-derived-read-only-default",
            "sandbox": {"label": "read-only", "source": "charness-derived"},
            "configuration_identity": "charness-run-review-v1",
        },
        "preflight": [],
        "capability_non_claims": [],
    }


def write_prompt(
    path: Path,
    packet: dict[str, Any],
    *,
    scope: str,
    lens: str,
    packet_sha: str,
    input_sha: str,
    goal_lineage: dict[str, Any] | None = None,
) -> None:
    readable_paths, deleted_paths = _semantic_review_paths(packet)
    semantic_lines = [
        "Every explicitly declared `--reviewed-path` and every auto-bound path below is semantic review input.",
        "The packet owns identity and provenance; the hash-bound paths own the semantic bytes.",
        "Open each readable path from the repository root using read-only access before judging.",
    ]
    semantic_lines.extend(f"- `{path}`" for path in readable_paths)
    if deleted_paths:
        semantic_lines.append(
            "Deleted reviewed paths are bound to their pre-image and have no current bytes to open:"
        )
        semantic_lines.extend(f"- `{path}` (deleted)" for path in deleted_paths)
    semantic_lines.append(
        "Do not infer reviewed content from hashes or unrelated packet sections, and do not silently truncate large files."
    )
    lineage_lines = (
        "Goal evidence lineage (copy exactly):",
        json.dumps(goal_lineage, ensure_ascii=False, indent=2, sort_keys=True),
    ) if goal_lineage is not None else ()
    path.write_text(
        "\n".join(
            (
                "You are a bounded read-only fresh-eye reviewer.",
                f"Scope: {scope}",
                f"Lens: {lens}",
                f"Packet identity (copy exactly): {packet_sha}",
                f"Reviewed input identity (copy exactly): {input_sha}",
                *lineage_lines,
                "Return only JSON matching the supplied bounded-review result schema.",
                "Do not edit the workspace, and do not treat partial progress as approval.",
                *semantic_lines,
                "The packet below is the authoritative review input:",
                json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True),
                "",
            )
        ),
        encoding="utf-8",
    )


def run_paths(run_dir: Path, packet: Path) -> dict[str, Path]:
    names = {
        "run_dir": run_dir,
        "packet": packet,
        "schema": "bounded-review-result.schema.json",
        "capability": "capability.json",
        "prompt": "review-prompt.md",
        "plan": "run-plan.json",
        "ledger": "delivery.json",
        "output": "result.json",
        "receipt": "receipt.json",
        "report": "worker-report.yaml",
        "runner_stdout": "runner.stdout",
        "runner_stderr": "runner.stderr",
        "backend_stdout": "backend.stdout",
        "backend_stderr": "backend.stderr",
        "summary": "lifecycle.yaml",
    }
    return {key: value if isinstance(value, Path) else run_dir / value for key, value in names.items()}
