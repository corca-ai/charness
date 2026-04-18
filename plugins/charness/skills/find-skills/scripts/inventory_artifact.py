from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _section_lines(entries: list[dict[str, Any]], *, formatter) -> list[str]:
    if not entries:
        return ["- none"]
    return [formatter(entry) for entry in entries]


def _count_by_layer(entries: list[dict[str, Any]], layer: str) -> int:
    return sum(1 for entry in entries if entry.get("layer") == layer)


def render_markdown(snapshot: dict[str, Any]) -> str:
    generated_at = snapshot["generated_at"]
    date_value = generated_at[:10]
    inventory = snapshot["inventory"]
    support_skills = inventory["support_skills"]
    lines = [
        "# Find Skills Inventory",
        f"Date: {date_value}",
        f"Updated: {generated_at}",
        "",
        "## Summary",
        f"- public skills: {len(inventory['public_skills'])}",
        f"- support skills: {_count_by_layer(support_skills, 'support skill')}",
        f"- synced support skills: {_count_by_layer(support_skills, 'synced support skill')}",
        f"- support capabilities: {len(inventory['support_capabilities'])}",
        f"- integrations: {len(inventory['integrations'])}",
        f"- trusted skills: {len(inventory['trusted_skills'])}",
        "",
        "## Public Skills",
        * _section_lines(
            inventory["public_skills"],
            formatter=lambda entry: f"- `{entry['id']}`: {entry['summary']}",
        ),
        "",
        "## Support Skills",
        * _section_lines(
            support_skills,
            formatter=lambda entry: f"- `{entry['id']}` ({entry['layer']}): {entry['summary']}",
        ),
        "",
        "## Support Capabilities",
        * _section_lines(
            inventory["support_capabilities"],
            formatter=lambda entry: (
                f"- `{entry['id']}`: {entry['summary']}"
                + (
                    f" Supports `{', '.join(entry['supports_public_skills'])}`."
                    if entry.get("supports_public_skills")
                    else ""
                )
            ),
        ),
        "",
        "## Integrations",
        * _section_lines(
            inventory["integrations"],
            formatter=lambda entry: (
                f"- `{entry['id']}` ({entry['kind']}, {entry['support_state']}): access modes "
                f"`{', '.join(entry['access_modes'])}`"
            ),
        ),
        "",
        "## Trusted Skills",
        * _section_lines(
            inventory["trusted_skills"],
            formatter=lambda entry: f"- `{entry['id']}`: {entry['summary']}",
        ),
        "",
    ]
    return "\n".join(lines)


def _load_existing_snapshot(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if not isinstance(payload.get("inventory"), dict):
        return None
    if not isinstance(payload.get("generated_at"), str):
        return None
    return payload


def persist_inventory(
    *,
    repo_root: Path,
    output_dir: Path,
    inventory: dict[str, Any],
) -> dict[str, Any]:
    markdown_path = output_dir / "latest.md"
    json_path = output_dir / "latest.json"
    existing = _load_existing_snapshot(json_path)

    if existing is not None and existing.get("inventory") == inventory and markdown_path.is_file():
        generated_at = existing["generated_at"]
        updated = False
        snapshot = existing
    else:
        generated_at = _utc_now()
        snapshot = {
            "schema_version": 1,
            "artifact_kind": "find-skills-inventory",
            "generated_at": generated_at,
            "repo": repo_root.name,
            "inventory": inventory,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(snapshot).rstrip() + "\n", encoding="utf-8")
        json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        updated = True

    return {
        "markdown_path": str(markdown_path.relative_to(repo_root)),
        "json_path": str(json_path.relative_to(repo_root)),
        "generated_at": generated_at,
        "updated": updated,
    }
