"""Critique prepare packet: envelope assembly + section execution.

Schema lives in `skills/public/critique/references/prepare-packet.md`.

The runner is intentionally thin: read adapter, run/inline each declared
section, fold into one envelope, render markdown. Producer correctness
stays the producer's responsibility; this module owns shape only.
"""

from __future__ import annotations

import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKET_KIND = "charness.critique_prepare_packet"
PACKET_VERSION = 1
PRODUCER_TIMEOUT_SECONDS = 60


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_command(command: str, *, repo_root: Path) -> tuple[str, list[str], bool]:
    try:
        result = subprocess.run(
            shlex.split(command),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=PRODUCER_TIMEOUT_SECONDS,
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


def execute_section(section: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    section_id = section.get("id", "")
    title = section.get("title", section_id)
    kind = section.get("content_kind", "")
    if kind == "script":
        command = section.get("command", "")
        producer = command
        content, errors, ok = _run_command(command, repo_root=repo_root)
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
) -> dict[str, Any]:
    data = adapter.get("data", {}) or {}
    sections_decl = data.get("packet_sections", []) or []
    sections = [execute_section(section, repo_root=repo_root) for section in sections_decl]
    all_ok = all(section["ok"] for section in sections)
    return {
        "kind": PACKET_KIND,
        "version": PACKET_VERSION,
        "repo": data.get("repo") or repo_root.name,
        "generated_at": _now_iso(),
        "prepared_for": prepared_for,
        "adapter_path": adapter.get("path"),
        "sections": sections,
        "section_count": len(sections),
        "ok": all_ok,
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Critique Prepare Packet — {packet['repo']}")
    lines.append("")
    lines.append(f"- **Kind**: `{packet['kind']}` (v{packet['version']})")
    lines.append(f"- **Generated**: {packet['generated_at']}")
    lines.append(f"- **Prepared for**: {packet['prepared_for']}")
    if packet.get("adapter_path"):
        lines.append(f"- **Adapter**: `{packet['adapter_path']}`")
    lines.append(f"- **Sections**: {packet['section_count']}")
    lines.append(f"- **Overall ok**: {packet['ok']}")
    lines.append("")
    if not packet["sections"]:
        lines.append(
            "_No `packet_sections` declared in the adapter. The prepare contract is "
            "opt-in; declare ≥1 section in `.agents/critique-adapter.yaml` to "
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


def write_packet(
    packet: dict[str, Any], *, output_dir: Path, slug: str
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{slug}-packet.json"
    md_path = output_dir / f"{slug}-packet.md"
    json_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return json_path, md_path
