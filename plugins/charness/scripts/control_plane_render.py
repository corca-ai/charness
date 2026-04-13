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
            f"This generated wrapper helps `charness` users consume the upstream `{tool_id}` support surface.",
            "",
            f"- upstream repo: `{manifest['upstream_repo']}`",
            f"- upstream context path: `{support['path']}`",
            "- local materialization: cache-backed repo symlink",
            "",
            "Regenerate this file through `scripts/sync_support.py` instead of editing it by hand.",
            "",
        ]
    )
