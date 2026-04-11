#!/usr/bin/env python3
# ruff: noqa: T201

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _file_state(path: Path) -> dict[str, object]:
    if not path.exists() and not path.is_symlink():
        return {"exists": False, "kind": "missing"}
    if path.is_symlink():
        target = path.readlink()
        return {"exists": True, "kind": "symlink", "target": str(target)}
    if path.is_file():
        size = path.stat().st_size
        return {"exists": True, "kind": "file", "size": size}
    return {"exists": True, "kind": "other"}


def _text_present(path: Path) -> bool:
    return path.is_file() and path.read_text(encoding="utf-8", errors="replace").strip() != ""


def detect_agent_docs(repo_root: Path) -> dict[str, object]:
    agents = repo_root / "AGENTS.md"
    claude = repo_root / "CLAUDE.md"
    agents_state = _file_state(agents)
    claude_state = _file_state(claude)

    if not agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_agents_and_symlink"
    elif agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_symlink_only"
    elif claude.is_symlink() and claude.resolve() == agents.resolve():
        action = "leave_as_is"
    elif claude.is_file() and not agents.exists():
        action = "ask_to_promote_claude_into_agents"
    elif claude.is_file() and agents.exists():
        action = "ask_to_merge_and_replace_with_symlink"
    else:
        action = "inspect_manually"

    return {
        "agents": agents_state,
        "claude": claude_state,
        "recommended_action": action,
        "agents_has_text": _text_present(agents),
        "claude_has_text": _text_present(claude),
    }


def detect_repo_mode(repo_root: Path) -> str:
    core = [
        repo_root / "README.md",
        repo_root / "AGENTS.md",
        repo_root / "docs" / "roadmap.md",
        repo_root / "docs" / "operator-acceptance.md",
    ]
    present = sum(1 for path in core if path.exists())
    if present == 0:
        return "GREENFIELD"
    if present < len(core):
        return "PARTIAL"
    return "NORMALIZE"


def build_payload(repo_root: Path) -> dict[str, object]:
    return {
        "repo": repo_root.name,
        "repo_mode": detect_repo_mode(repo_root),
        "agent_docs": detect_agent_docs(repo_root),
        "surfaces": {
            "readme": _file_state(repo_root / "README.md"),
            "roadmap": _file_state(repo_root / "docs" / "roadmap.md"),
            "operator_acceptance": _file_state(repo_root / "docs" / "operator-acceptance.md"),
            "install": _file_state(repo_root / "INSTALL.md"),
            "uninstall": _file_state(repo_root / "UNINSTALL.md"),
            "handoff": _file_state(repo_root / "docs" / "handoff.md"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.repo_root.resolve())
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
