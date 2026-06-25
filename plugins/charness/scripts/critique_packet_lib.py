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

PACKET_KIND = "charness.critique_prepare_packet"
PACKET_VERSION = 1
PRODUCER_TIMEOUT_SECONDS = 60
DEFAULT_REVIEWER_TIER = "high-leverage"


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


def build_packet(
    *,
    adapter: dict[str, Any],
    repo_root: Path,
    prepared_for: str,
    changed_ref: str | None = None,
    packet_kind: str = PACKET_KIND,
    include_reviewer_tier: bool = True,
    changed_ref_env_var: str = "CHARNESS_CRITIQUE_CHANGED_REF",
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
    all_ok = all(section["ok"] for section in sections)
    packet: dict[str, Any] = {
        "kind": packet_kind,
        "version": PACKET_VERSION,
        "repo": data.get("repo") or repo_root.name,
        "generated_at": _now_iso(),
        "prepared_for": prepared_for,
        "changed_ref": changed_ref,
        "adapter_path": _relative_adapter_path(adapter.get("path"), repo_root),
        "sections": sections,
        "section_count": len(sections),
        "ok": all_ok,
    }
    if include_reviewer_tier:
        packet["reviewer_tier_evidence"] = reviewer_tier_evidence(data)
    return packet


def reviewer_tier_evidence(adapter_data: dict[str, Any]) -> dict[str, object]:
    reviewer_tiers = adapter_data.get("reviewer_tiers", {}) or {}
    requested_fields = reviewer_tiers.get(DEFAULT_REVIEWER_TIER, {}) or {}
    return {
        "requested_tier": DEFAULT_REVIEWER_TIER,
        "requested_spawn_fields": dict(requested_fields),
        "host_exposure_state": "pending-parent-spawn",
        "application_state": "unverified-by-packet",
        "instruction": (
            "Review artifacts must record requested_fields_sent, metadata-hidden, "
            "host-defaulted, unsupported, or applied only when host-confirmed."
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


def render_markdown(packet: dict[str, Any]) -> str:
    lines: list[str] = []
    title = "Critique Prepare Packet"
    if packet.get("kind") == "charness.retro_prepare_packet":
        title = "Retro Prepare Packet"
    lines.append(f"# {title} — {packet['repo']}")
    lines.append("")
    lines.append(f"- **Kind**: `{packet['kind']}` (v{packet['version']})")
    lines.append(f"- **Generated**: {packet['generated_at']}")
    lines.append(f"- **Prepared for**: {packet['prepared_for']}")
    if packet.get("changed_ref"):
        lines.append(f"- **Changed ref**: `{packet['changed_ref']}`")
    if packet.get("adapter_path"):
        lines.append(f"- **Adapter**: `{packet['adapter_path']}`")
    lines.append(f"- **Sections**: {packet['section_count']}")
    lines.append(f"- **Overall ok**: {packet['ok']}")
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
        lines.append(f"- **Section ok**: {section['ok']}")
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
    return [
        "## Reviewer Tier Evidence",
        "",
        f"- **Requested tier**: `{evidence.get('requested_tier', '')}`",
        f"- **Requested spawn fields**: `{rendered_fields}`",
        f"- **Host exposure state**: `{evidence.get('host_exposure_state', '')}`",
        f"- **Application state**: `{evidence.get('application_state', '')}`",
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
