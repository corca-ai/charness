#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()


def _skill_roots() -> tuple[Path, Path | None]:
    script = Path(__file__).resolve()
    for ancestor in script.parents:
        source_public = ancestor / "skills" / "public"
        if source_public.is_dir():
            return source_public, ancestor / "skills" / "support"
        plugin_public = ancestor / "skills"
        if (plugin_public / "init-repo" / "SKILL.md").is_file():
            return plugin_public, ancestor / "support"
    return script.parents[1].parent, None


def _installed_skill_ids(root: Path | None) -> list[str]:
    if root is None or not root.is_dir():
        return []
    return sorted(path.parent.name for path in root.glob("*/SKILL.md"))


def _render_skill_routing(public_skill_ids: list[str]) -> tuple[str, list[str]]:
    installed = set(public_skill_ids)
    lines = [
        "## Skill Routing",
        "",
        "For task-oriented sessions in this repo, call the shared/public charness skill `find-skills` once at startup before broader exploration.",
        "",
        "Use its capability inventory as the default map of installed public skills, support skills, synced support surfaces, and integrations.",
        "",
        "After that bootstrap pass, choose the durable work skill that best matches the request from the installed charness surface.",
        "",
        "Keep this block short. Detailed routing belongs in installed skill metadata and `find-skills` output, not in a long checked-in catalog.",
        "",
    ]
    listed_skill_ids = ["find-skills"] if "find-skills" in installed else []
    return "\n".join(lines) + "\n", listed_skill_ids


def _build_payload(repo_root: Path) -> dict[str, object]:
    public_root, support_root = _skill_roots()
    public_skill_ids = _installed_skill_ids(public_root)
    support_skill_ids = _installed_skill_ids(support_root)
    agents = repo_root / "AGENTS.md"
    agents_text = agents.read_text(encoding="utf-8", errors="replace") if agents.is_file() else ""
    has_skill_routing = "## Skill Routing" in agents_text
    if not agents.exists():
        action = "create_agents_with_skill_routing"
    elif has_skill_routing:
        action = "leave_as_is"
    else:
        action = "add_skill_routing_block"
    markdown, listed_skill_ids = _render_skill_routing(public_skill_ids)
    return {
        "public_skills": public_skill_ids,
        "support_skills": support_skill_ids,
        "available_modes": ["compact"],
        "agents_path": "AGENTS.md",
        "agents_has_skill_routing": has_skill_routing,
        "recommended_action": action,
        "skill_routing_mode": "compact",
        "skill_routing_mode_source": "default",
        "listed_skill_ids": listed_skill_ids,
        "markdown": markdown,
    }


def build_payload(repo_root: Path) -> dict[str, object]:
    return _build_payload(repo_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    payload = _build_payload(repo_root)
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(str(payload["markdown"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
