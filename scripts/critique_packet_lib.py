"""Critique prepare packet: envelope assembly + section execution.

Schema lives in `skills/public/critique/references/prepare-packet.md`.

The runner is intentionally thin: read adapter, run/inline each declared
section, fold into one envelope, render markdown. Producer correctness
stays the producer's responsibility; this module owns shape only.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module
from scripts.critique_adapter_lib import adapter_has_sections

PACKET_KIND = "charness.critique_prepare_packet"
PACKET_VERSION = 1
PRODUCER_TIMEOUT_SECONDS = 60
DEFAULT_REVIEWER_TIER = "high-leverage"
_reviewed_input_identity = import_repo_module(__file__, "scripts.reviewed_input_identity")
build_reviewed_input_identity = _reviewed_input_identity.build_reviewed_input_identity
packet_file_sha256 = _reviewed_input_identity.packet_file_sha256
SUBSTRATE_WORKING_TREE = _reviewed_input_identity.SUBSTRATE_WORKING_TREE
SUBSTRATE_COMMITTED_REF = _reviewed_input_identity.SUBSTRATE_COMMITTED_REF
ReviewedInputError = _reviewed_input_identity.ReviewedInputError
_reviewer_shape = import_repo_module(__file__, "scripts.critique_reviewer_evidence")
DEFAULT_REVIEWER_EXECUTION_MODE = _reviewer_shape.DEFAULT_REVIEWER_EXECUTION_MODE
REVIEWER_EXECUTION_MODE_VALUES = _reviewer_shape.REVIEWER_EXECUTION_MODE_VALUES


def changed_ref_targets(
    *, changed_ref: str | None, commit: str | None, changed_range: str | None
) -> list[str]:
    """Return the explicitly supplied ref aliases in stable CLI order."""

    return [value for value in (changed_ref, commit, changed_range) if value]


def parse_changed_ref(parser: Any, *, changed_ref: str | None, commit: str | None, changed_range: str | None) -> str | None:
    """Resolve the three CLI aliases and report mutually-exclusive use once."""

    targets = changed_ref_targets(
        changed_ref=changed_ref, commit=commit, changed_range=changed_range
    )
    if len(targets) > 1:
        parser.error("use only one of --changed-ref, --commit, or --range")
    return targets[0] if targets else None


def substrate_refusal(*, substrate_mode: str, changed_ref: str | None) -> dict[str, object] | None:
    """Return a typed refusal when substrate and ref declarations disagree."""

    if substrate_mode == SUBSTRATE_WORKING_TREE and changed_ref:
        return {
            "ok": False,
            "status": "refused",
            "reason_code": "substrate-ref-mismatch",
            "error": "working-tree substrate cannot declare --changed-ref",
            "substrate_mode": substrate_mode,
        }
    if substrate_mode == SUBSTRATE_COMMITTED_REF and not changed_ref:
        return {
            "ok": False,
            "status": "refused",
            "reason_code": "substrate-ref-missing",
            "error": "committed-ref substrate requires --changed-ref",
            "substrate_mode": substrate_mode,
        }
    return None


def packet_result_payload(
    packet: dict[str, Any], *, repo_root: Path, json_path: Path, md_path: Path
) -> dict[str, object]:
    """Build the stable CLI result shared by critique and retro packet runners."""

    result: dict[str, object] = {
        "ok": packet["ok"],
        "section_count": packet["section_count"],
        "json_path": str(json_path.relative_to(repo_root)),
        "md_path": str(md_path.relative_to(repo_root)),
        "changed_ref": packet["changed_ref"],
        "adapter_path": packet["adapter_path"],
    }
    for field in ("scope_status", "reason_code", "usable", "warning", "remedy"):
        if field in packet:
            result[field] = packet[field]
    return result


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_command(
    command: str,
    *,
    repo_root: Path,
    changed_ref: str | None = None,
    changed_ref_env_var: str = "CHARNESS_CRITIQUE_CHANGED_REF",
) -> tuple[str, list[str], bool]:
    env = os.environ.copy()
    if changed_ref:
        env[changed_ref_env_var] = changed_ref
    else:
        env.pop(changed_ref_env_var, None)
    try:
        result = subprocess.run(
            shlex.split(command),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=PRODUCER_TIMEOUT_SECONDS,
            env=env,
        )
    except FileNotFoundError as exc:
        return "", [f"command not found: {exc}"], False
    except subprocess.TimeoutExpired:
        return "", [f"command timed out after {PRODUCER_TIMEOUT_SECONDS}s"], False
    if result.returncode != 0:
        errors = [f"exit code {result.returncode}"]
        if result.stderr.strip():
            errors.append(result.stderr.strip())
        return result.stdout, errors, False
    return result.stdout, [], True


def _resolve_static(section: dict[str, Any], *, repo_root: Path) -> tuple[str, list[str], bool]:
    if "content" in section:
        return section["content"], [], True
    rel = section.get("content_path", "")
    if not rel:
        return "", ["static section missing content/content_path"], False
    candidate = (repo_root / rel).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return "", [f"content_path `{rel}` resolves outside repo root"], False
    if not candidate.is_file():
        return "", [f"content_path `{rel}` does not point at a file"], False
    return candidate.read_text(encoding="utf-8"), [], True


def execute_section(
    section: dict[str, Any],
    *,
    repo_root: Path,
    changed_ref: str | None = None,
    changed_ref_env_var: str = "CHARNESS_CRITIQUE_CHANGED_REF",
) -> dict[str, Any]:
    section_id = section.get("id", "")
    title = section.get("title", section_id)
    kind = section.get("content_kind", "")
    if kind == "script":
        command = section.get("command", "")
        producer = command
        content, errors, ok = _run_command(
            command,
            repo_root=repo_root,
            changed_ref=changed_ref,
            changed_ref_env_var=changed_ref_env_var,
        )
    else:
        if "content" in section:
            producer = "static-config (inline)"
        else:
            producer = f"static-config (content_path: {section.get('content_path', '')})"
        content, errors, ok = _resolve_static(section, repo_root=repo_root)

    return {
        "id": section_id,
        "title": title,
        "content_kind": kind,
        "producer": producer,
        "content": content,
        "ok": ok,
        "errors": errors,
    }


def _section_has_content(section: dict[str, Any]) -> bool:
    content = section.get("content")
    return isinstance(content, str) and bool(content.strip())


def _scope_metadata(
    *, adapter: dict[str, Any], repo_root: Path, sections: list[dict[str, Any]]
) -> dict[str, object]:
    """Classify whether the packet has a declared and populated review scope."""

    if not adapter_has_sections(adapter):
        adapter_path = _relative_adapter_path(adapter.get("path"), repo_root)
        adapter_name = adapter_path or ".agents/critique-adapter.yaml"
        return {
            "scope_status": "adapter-no-sections",
            "reason_code": "adapter-no-sections",
            "usable": False,
            "warning": (
                f"critique adapter `{adapter_name}` declares no packet_sections; "
                "the packet carries no semantic review input"
            ),
            "remedy": (
                f"Declare at least one packet_sections entry in `{adapter_name}` "
                "and rerun"
            ),
        }

    if not any(_section_has_content(section) for section in sections):
        return {
            "scope_status": "producer-empty",
            "reason_code": "producer-empty",
            "usable": False,
            "warning": (
                "declared packet sections produced no content; this is a producer "
                "failure, not a passing empty review"
            ),
            "remedy": (
                "Repair the declared packet producer(s) so at least one section "
                "emits semantic review content, then rerun"
            ),
        }

    return {"scope_status": "populated"}


def build_packet(
    *,
    adapter: dict[str, Any],
    repo_root: Path,
    prepared_for: str,
    changed_ref: str | None = None,
    substrate_mode: str | None = None,
    packet_kind: str = PACKET_KIND,
    include_reviewer_tier: bool = True,
    include_reviewed_input_identity: bool = True,
    changed_ref_env_var: str = "CHARNESS_CRITIQUE_CHANGED_REF",
    reviewed_paths: list[str] | None = None,
    excluded_reviewed_paths: list[str] | None = None,
    excluded_reviewed_prefixes: list[str] | None = None,
) -> dict[str, Any]:
    data = adapter.get("data", {}) or {}
    sections_decl = data.get("packet_sections", []) or []
    sections = [
        execute_section(
            section,
            repo_root=repo_root,
            changed_ref=changed_ref,
            changed_ref_env_var=changed_ref_env_var,
        )
        for section in sections_decl
    ]
    if packet_kind == PACKET_KIND:
        scope_metadata = _scope_metadata(
            adapter=adapter, repo_root=repo_root, sections=sections
        )
        all_ok = (
            scope_metadata.get("scope_status") == "populated"
            and all(section["ok"] for section in sections)
        )
    else:
        # The shared builder also serves retro packets, whose adapter has a
        # separate opt-in contract and must retain its historical empty-list
        # behavior.
        scope_metadata = {}
        all_ok = all(section["ok"] for section in sections)
    packet: dict[str, Any] = {
        "kind": packet_kind,
        "version": PACKET_VERSION,
        "repo": data.get("repo") or repo_root.name,
        "generated_at": _now_iso(),
        "prepared_for": prepared_for,
        "changed_ref": changed_ref,
        "substrate_mode": substrate_mode
        or (SUBSTRATE_COMMITTED_REF if changed_ref else SUBSTRATE_WORKING_TREE),
        "adapter_path": _relative_adapter_path(adapter.get("path"), repo_root),
        "sections": sections,
        "section_count": len(sections),
        "ok": all_ok,
        **scope_metadata,
    }
    if include_reviewer_tier:
        packet["reviewer_tier_evidence"] = reviewer_tier_evidence(data)
    if include_reviewed_input_identity:
        packet["reviewed_input_identity"] = build_reviewed_input_identity(
            repo_root=repo_root,
            reviewed_paths=reviewed_paths,
            changed_ref=changed_ref,
            substrate_mode=packet["substrate_mode"],
            excluded_paths=excluded_reviewed_paths,
            excluded_prefixes=excluded_reviewed_prefixes,
        )
    return packet


def reviewer_tier_evidence(adapter_data: dict[str, Any]) -> dict[str, object]:
    reviewer_tiers = adapter_data.get("reviewer_tiers", {}) or {}
    requested_fields = reviewer_tiers.get(DEFAULT_REVIEWER_TIER, {}) or {}
    runner = adapter_data.get("reviewer_runner")
    if not isinstance(runner, dict):
        runner = {
            "mode": DEFAULT_REVIEWER_EXECUTION_MODE,
            "backend": "host-defaulted",
            "timeout_seconds": 900,
        }
    execution_mode = runner.get("mode", DEFAULT_REVIEWER_EXECUTION_MODE)
    if execution_mode not in REVIEWER_EXECUTION_MODE_VALUES:
        execution_mode = DEFAULT_REVIEWER_EXECUTION_MODE
    return {
        "requested_tier": DEFAULT_REVIEWER_TIER,
        "requested_spawn_fields": dict(requested_fields),
        "host_exposure_state": "pending-parent-spawn",
        "application_state": "unverified-by-packet",
        "reviewer_runner": runner,
        "execution_mode": execution_mode,
        "instruction": (
            "Review artifacts must record requested_fields_sent, metadata-hidden, "
            "host-defaulted, unsupported, or applied only when host-confirmed. "
            "Consume the worker receipt and delivery ledger; do not infer approval "
            "from a file or exit code."
        ),
    }


def _relative_adapter_path(adapter_path: object, repo_root: Path) -> str | None:
    if not isinstance(adapter_path, str) or not adapter_path:
        return None
    path = Path(adapter_path)
    resolved = path if path.is_absolute() else repo_root / path
    try:
        return resolved.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def render_markdown(packet: dict[str, Any], verification_command: str | None = None) -> str:
    lines: list[str] = []
    title = "Critique Prepare Packet"
    if packet.get("kind") == "charness.retro_prepare_packet":
        title = "Retro Prepare Packet"
    lines.append(f"# {title} — {packet['repo']}")
    lines.append("")
    lines.append(f"- **Kind**: `{packet['kind']}` (v{packet['version']})")
    lines.append(f"- **Generated**: {packet['generated_at']}")
    lines.append(f"- **Prepared for**: {packet['prepared_for']}")
    # Historical v1 packets did not carry this envelope field; their existing
    # Markdown remains the deterministic rendering of that older JSON shape.
    if "substrate_mode" in packet:
        lines.append(f"- **Substrate mode**: `{packet.get('substrate_mode', '')}`")
    if packet.get("changed_ref"):
        lines.append(f"- **Changed ref**: `{packet['changed_ref']}`")
    if packet.get("adapter_path"):
        lines.append(f"- **Adapter**: `{packet['adapter_path']}`")
    if "reviewed_input_identity" in packet:
        identity = packet["reviewed_input_identity"]
        identity = identity if isinstance(identity, dict) else {}
        reviewed_paths = identity.get("reviewed_paths", [])
        excluded_paths = identity.get("auto_excluded_paths", [])
        reviewed_paths = reviewed_paths if isinstance(reviewed_paths, list) else []
        excluded_paths = excluded_paths if isinstance(excluded_paths, list) else []
        lines.append(f"- **Reviewed input identity**: `{identity.get('identity_sha256', '')}`")
        lines.append(f"- **Reviewed paths**: {len(reviewed_paths)}")
        lines.extend(f"  - `{path}`" for path in reviewed_paths if isinstance(path, str))
        lines.append(f"- **Auto-excluded paths**: {len(excluded_paths)}")
        lines.extend(f"  - `{path}`" for path in excluded_paths if isinstance(path, str))
        if verification_command:
            lines.append("")
            lines.append("## Verify Packet")
            lines.append("")
            lines.append("Run this exact command from the repository root:")
            lines.append("")
            lines.append("```sh")
            lines.append(verification_command)
            lines.append("```")
            lines.append("")
            lines.append(
                "Raw sha256sum is not the contract; the verifier owns the "
                "domain-separated packet identity check."
            )
    lines.append(f"- **Sections**: {packet['section_count']}")
    lines.append(f"- **Shape validation ok**: {packet['ok']}")
    lines.append("- **Release approval**: not claimed")
    lines.append("")
    lines.append(
        "_This packet reports deterministic prepare-packet shape validation only; "
        "it is not a release-readiness or reviewer-verdict approval._"
    )
    lines.append("")
    if "reviewer_tier_evidence" in packet:
        lines.extend(render_reviewer_tier_evidence(packet.get("reviewer_tier_evidence")))
    lines.append("")
    if not packet["sections"]:
        adapter_name = ".agents/critique-adapter.yaml"
        if packet.get("kind") == "charness.retro_prepare_packet":
            adapter_name = ".agents/retro-adapter.yaml"
        lines.append(
            "_No `packet_sections` declared in the adapter. The prepare contract is "
            f"opt-in; declare >=1 section in `{adapter_name}` to "
            "populate this packet._"
        )
        lines.append("")
        return "\n".join(lines)
    lines.append("Read this packet first. Then judge what the deterministic surface "
                 "leaves uncovered before broad repo sampling.")
    lines.append("")
    for section in packet["sections"]:
        lines.append(f"## {section['title']}")
        lines.append("")
        lines.append(f"- **Section id**: `{section['id']}`")
        lines.append(f"- **Content kind**: `{section['content_kind']}`")
        lines.append(f"- **Producer**: `{section['producer']}`")
        lines.append(f"- **Section shape validation ok**: {section['ok']}")
        if section["errors"]:
            lines.append("- **Errors**:")
            for err in section["errors"]:
                lines.append(f"  - {err}")
        lines.append("")
        lines.append("```text")
        body = section["content"].rstrip("\n")
        lines.append(body if body else "(empty)")
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def render_reviewer_tier_evidence(raw: object) -> list[str]:
    evidence = raw if isinstance(raw, dict) else {}
    fields = evidence.get("requested_spawn_fields", {})
    if isinstance(fields, dict) and fields:
        rendered_fields = ", ".join(f"{key}={value}" for key, value in sorted(fields.items()))
    else:
        rendered_fields = "none"
    runner = evidence.get("reviewer_runner", {})
    if isinstance(runner, dict):
        runner_text = ", ".join(f"{key}={value}" for key, value in sorted(runner.items()))
    else:
        runner_text = "missing"
    return [
        "## Reviewer Tier Evidence",
        "",
        f"- **Requested tier**: `{evidence.get('requested_tier', '')}`",
        f"- **Requested spawn fields**: `{rendered_fields}`",
        f"- **Host exposure state**: `{evidence.get('host_exposure_state', '')}`",
        f"- **Application state**: `{evidence.get('application_state', '')}`",
        f"- **Execution mode**: `{evidence.get('execution_mode', '')}`",
        f"- **Reviewer runner**: `{runner_text}`",
        f"- **Instruction**: {evidence.get('instruction', '')}",
    ]


def write_packet(
    packet: dict[str, Any], *, output_dir: Path, slug: str
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{slug}-packet.json"
    md_path = output_dir / f"{slug}-packet.md"
    json_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return json_path, md_path
