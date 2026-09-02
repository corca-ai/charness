from __future__ import annotations

import hashlib
from pathlib import Path

COMPACT_AGENTS_TEMPLATE = """# Agents

Start with [docs/index.md](./docs/index.md), then read only the owner page needed for the current request.

Keep this file short. Put durable procedures and repository-specific decisions in the docs they own.

When work is independent, inspect the live host tools and use a host spawn for short interactive work or `charness task run` for bounded isolated Codex work; neither is a fallback. Use the host's fast tier for bounded sidecars unless the repository or user chose otherwise, and keep that choice across compaction.

Preserve authored changes, use the repository's documented commands, and update the owning docs when behavior changes.
"""


def render_agents_template() -> str:
    """Return the small greenfield root contract."""

    return COMPACT_AGENTS_TEMPLATE


def _digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_host_docs(
    repo_root: Path,
    *,
    execute: bool,
    compact: bool = False,
) -> dict[str, object]:
    """Plan or apply the AGENTS/CLAUDE compatibility boundary.

    Existing AGENTS.md content is preserved by default. Replacing it is an
    explicit `--compact` operation so setup can repair an overgrown root file
    without silently discarding authored instructions.
    """

    agents = repo_root / "AGENTS.md"
    claude = repo_root / "CLAUDE.md"
    result: dict[str, object] = {
        "status": "planned",
        "execute": execute,
        "compact": compact,
        "actions": [],
        "blocked": [],
        "agents_path": "AGENTS.md",
        "claude_path": "CLAUDE.md",
    }
    if _real_file_conflict(claude):
        result["status"] = "blocked"
        result["blocked"].append(
            {
                "path": "CLAUDE.md",
                "reason": "real CLAUDE.md content requires a user merge decision",
            }
        )
        return result

    if not agents.exists() and not agents.is_symlink():
        content = render_agents_template()
        result["actions"].append(
            {
                "action": "write_agents",
                "path": "AGENTS.md",
                "after_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
        )
        if execute:
            agents.write_text(content, encoding="utf-8")
    elif not agents.is_file():
        result["status"] = "blocked"
        result["blocked"].append(
            {"path": "AGENTS.md", "reason": "AGENTS.md is not a regular file"}
        )
        return result
    elif compact and agents.is_symlink():
        result["status"] = "blocked"
        result["blocked"].append(
            {
                "path": "AGENTS.md",
                "reason": "--compact will not replace an AGENTS.md symlink",
            }
        )
        return result
    elif compact:
        content = render_agents_template()
        result["actions"].append(
            {
                "action": "replace_agents_with_compact_template",
                "path": "AGENTS.md",
                "before_sha256": _digest(agents),
                "after_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
        )
        if execute:
            agents.write_text(content, encoding="utf-8")
    else:
        result["actions"].append({"action": "keep_agents", "path": "AGENTS.md"})

    if not claude.exists() and not claude.is_symlink():
        result["actions"].append(
            {"action": "create_claude_symlink", "path": "CLAUDE.md", "target": "AGENTS.md"}
        )
        if execute:
            claude.symlink_to("AGENTS.md")
    elif claude.is_symlink() and claude.readlink() == Path("AGENTS.md"):
        result["actions"].append(
            {"action": "keep_claude_symlink", "path": "CLAUDE.md", "target": "AGENTS.md"}
        )
    elif claude.is_symlink():
        result["status"] = "blocked"
        result["blocked"].append(
            {"path": "CLAUDE.md", "reason": "CLAUDE.md symlink target is not AGENTS.md"}
        )
        return result
    result["status"] = "completed" if execute else "planned"
    return result


def _real_file_conflict(path: Path) -> bool:
    return path.exists() and path.is_file() and not path.is_symlink()
