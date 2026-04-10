#!/usr/bin/env python3

from __future__ import annotations

from typing import Any


def render_generated_wrapper(manifest: dict[str, Any]) -> str:
    tool_id = manifest["tool_id"]
    support = manifest["support_skill_source"]
    wrapper_id = support["wrapper_skill_id"]
    return "\n".join(
        [
            "---",
            f"name: {wrapper_id}",
            f'description: "Generated wrapper for the upstream {tool_id} support surface."',
            "---",
            "",
            f"# {wrapper_id}",
            "",
            f"This generated wrapper points at the upstream `{tool_id}` support guidance.",
            "",
            f"- upstream repo: `{manifest['upstream_repo']}`",
            f"- upstream path: `{support['path']}`",
            f"- sync strategy: `{support['sync_strategy']}`",
            "",
            "Regenerate this file through `scripts/sync_support.py` instead of editing it by hand.",
            "",
        ]
    )


def render_reference_note(manifest: dict[str, Any], *, support_state: str) -> str:
    support = manifest["support_skill_source"]
    lines = [
        f"# {manifest['tool_id']} Support Reference",
        "",
        "This generated reference records how `charness` consumes the upstream",
        "support surface without copying it into the local taxonomy.",
        "",
        f"- upstream repo: `{manifest['upstream_repo']}`",
        f"- upstream path: `{support['path']}`",
        f"- sync strategy: `{support['sync_strategy']}`",
        f"- support state: `{support_state}`",
    ]
    access_modes = manifest.get("access_modes", [])
    if access_modes:
        lines.append(f"- access modes: `{', '.join(access_modes)}`")

    requirements = manifest.get("capability_requirements", {})
    if isinstance(requirements, dict):
        grant_ids = requirements.get("grant_ids", [])
        env_vars = requirements.get("env_vars", [])
        scopes = requirements.get("permission_scopes", [])
        if grant_ids:
            lines.append(f"- grant ids: `{', '.join(grant_ids)}`")
        if env_vars:
            lines.append(f"- env vars: `{', '.join(env_vars)}`")
        if scopes:
            lines.append(f"- permission scopes: `{', '.join(scopes)}`")

    config_layers = manifest.get("config_layers", [])
    if config_layers:
        lines.extend(["", "## Config Layers", ""])
        lines.extend(f"- `{layer['layer_type']}`: {layer['summary']}" for layer in config_layers)

    notes = support.get("notes", [])
    if notes:
        lines.extend(["", "## Reuse Notes", ""])
        lines.extend(f"- {note}" for note in notes)

    host_notes = manifest.get("host_notes", [])
    if host_notes:
        lines.extend(["", "## Host Notes", ""])
        lines.extend(f"- {note}" for note in host_notes)

    lines.extend(
        [
            "",
            "Regenerate this file through `scripts/sync_support.py` instead of",
            "editing it by hand.",
            "",
        ]
    )
    return "\n".join(lines)
