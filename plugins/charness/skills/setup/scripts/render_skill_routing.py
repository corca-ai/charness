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
        if (plugin_public / "setup" / "SKILL.md").is_file():
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
        "At session startup in this repo, call the shared/public charness skill `find-skills` once before broader exploration.",
        "",
        "Use its capability inventory as the default map of installed public skills, support skills, synced support surfaces, and integrations.",
        "",
        "When a request names a workflow or capability noun such as worktree, browser automation, specdown, or validation, run `find-skills --recommend-for-task \"<task>\"` before ad hoc shell or tool use.",
        "",
        "After that bootstrap pass, choose the durable work skill that best matches the request from the installed charness surface.",
        "",
        "External URLs or source links that should become working context for this repo route through `gather` before summarizing, implementing, or deciding from them.",
        "",
        "Validation-shaped closeout or operator reading test requests go through `quality` validation recommendations before HITL or same-agent manual review.",
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
    markdown, listed_skill_ids = _render_skill_routing(public_skill_ids)
    has_skill_routing = "## Skill Routing" in agents_text
    matches_compact_block = bool(markdown and markdown in agents_text)
    expected_lines = tuple(line for line in markdown.splitlines() if line.strip() and line != "## Skill Routing")
    missing_expected_snippets = [line for line in expected_lines if line not in agents_text] if has_skill_routing else []
    if not agents.exists():
        action = "create_agents_with_skill_routing"
    elif matches_compact_block:
        action = "leave_as_is"
    elif has_skill_routing:
        action = "review_existing_skill_routing"
    else:
        action = "add_skill_routing_block"
    return {
        "public_skills": public_skill_ids,
        "support_skills": support_skill_ids,
        "available_modes": ["compact"],
        "agents_path": "AGENTS.md",
        "agents_has_skill_routing": has_skill_routing,
        "skill_routing_matches_compact_block": matches_compact_block,
        "missing_expected_snippets": missing_expected_snippets,
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
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root path")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload instead of markdown")
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
