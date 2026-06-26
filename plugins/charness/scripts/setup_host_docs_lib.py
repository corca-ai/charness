from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def _read_template(name: str) -> str:
    return (Path(__file__).resolve().parent / "templates" / name).read_text(
        encoding="utf-8"
    )


COMMIT_DISCIPLINE = _read_template("agents_commit_discipline.txt")
COMPACT_SUBAGENT_DELEGATION = _read_template("agents_subagent_delegation.txt")


def render_agents_template(*, skill_routing_markdown: str) -> str:
    body = [
        "# Agents",
        "",
        skill_routing_markdown.strip(),
        "",
        COMMIT_DISCIPLINE.strip(),
        "",
        COMPACT_SUBAGENT_DELEGATION.strip(),
        "",
    ]
    return "\n".join(part for part in body if part) + "\n"


def normalize_host_docs(
    repo_root: Path,
    *,
    skill_routing_payload: Callable[[Path], dict[str, Any]],
    execute: bool,
) -> dict[str, Any]:
    agents = repo_root / "AGENTS.md"
    claude = repo_root / "CLAUDE.md"
    payload = skill_routing_payload(repo_root)
    result: dict[str, Any] = {
        "status": "planned",
        "execute": execute,
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
        content = render_agents_template(skill_routing_markdown=str(payload.get("markdown", "")))
        result["actions"].append({"action": "write_agents", "path": "AGENTS.md"})
        if execute:
            agents.write_text(content, encoding="utf-8")
    elif not agents.is_file():
        result["status"] = "blocked"
        result["blocked"].append({"path": "AGENTS.md", "reason": "AGENTS.md is not a regular file"})
        return result
    else:
        result["actions"].append({"action": "keep_agents", "path": "AGENTS.md"})
    if not claude.exists() and not claude.is_symlink():
        result["actions"].append({"action": "create_claude_symlink", "path": "CLAUDE.md", "target": "AGENTS.md"})
        if execute:
            claude.symlink_to("AGENTS.md")
    elif claude.is_symlink() and claude.readlink() == Path("AGENTS.md"):
        result["actions"].append({"action": "keep_claude_symlink", "path": "CLAUDE.md", "target": "AGENTS.md"})
    elif claude.is_symlink():
        result["status"] = "blocked"
        result["blocked"].append({"path": "CLAUDE.md", "reason": "CLAUDE.md symlink target is not AGENTS.md"})
        return result
    result["status"] = "completed" if execute else "planned"
    return result


def _real_file_conflict(path: Path) -> bool:
    return path.exists() and path.is_file() and not path.is_symlink()
