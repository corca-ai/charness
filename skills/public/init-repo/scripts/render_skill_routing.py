#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

CURATED_HINTS = {
    "announcement": "release-note style summary or chat-ready human update",
    "create-cli": "new or upgraded repo-owned CLI, bootstrap script, or command runner",
    "create-skill": "new or updated charness skill, support skill, profile, preset, or integration",
    "debug": "bug, error, regression, or unexpected behavior investigation",
    "find-skills": "unclear skill choice, named support/helper, or hidden capability lookup",
    "gather": "external source fetch (Slack thread, Notion page, Google Docs, GitHub content, arbitrary URL)",
    "handoff": "next-session pickup, baton pass, or handoff artifact refresh",
    "hitl": "bounded human review loop or deliberate human judgment checkpoint",
    "ideation": "early product, system, workflow, API, or agent concept shaping",
    "impl": "code, config, test, or operator-facing artifact implementation",
    "init-repo": "new or partially initialized repo operating surface",
    "narrative": "source-of-truth docs and current repo story alignment",
    "premortem": "before-the-fact failure review for a non-trivial decision",
    "quality": "repo quality posture, gates, test confidence, security, or operability review",
    "release": "cut, bump, or verify a release surface",
    "retro": "retrospective after a meaningful work unit or missed issue",
    "spec": "turn a concept or design into a living implementation contract",
}

ORDER = tuple(CURATED_HINTS)
COMPACT_ORDER = ("find-skills", "gather", "debug", "impl", "quality", "handoff", "init-repo")
VALID_MODES = ("compact", "expanded")


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
_init_repo_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "init_repo_adapter")


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


def _resolve_mode(repo_root: Path, cli_mode: str | None) -> tuple[str, str]:
    if cli_mode is not None:
        return cli_mode, "cli"

    adapter_data, _adapter_path, _warnings = _init_repo_adapter_module.load_init_repo_adapter(repo_root)
    adapter_mode = adapter_data.get("skill_routing_mode")
    if adapter_mode is None:
        return "compact", "default"
    if not isinstance(adapter_mode, str) or adapter_mode not in VALID_MODES:
        raise SystemExit(
            "init-repo adapter `skill_routing_mode` must be one of: "
            + ", ".join(f"`{mode}`" for mode in VALID_MODES)
        )
    return adapter_mode, "adapter"


def _render_expanded_skill_routing(public_skill_ids: list[str]) -> tuple[str, list[str]]:
    installed = set(public_skill_ids)
    lines = [
        "## Skill Routing",
        "",
        "When one of these shows up in a request, prefer the named skill first:",
        "",
    ]
    listed_skill_ids: list[str] = []
    for skill_id in ORDER:
        if skill_id in installed:
            lines.append(f"- {CURATED_HINTS[skill_id]} -> `{skill_id}`")
            listed_skill_ids.append(skill_id)
    unknown = sorted(installed - set(ORDER))
    for skill_id in unknown:
        lines.append(f"- task matching the `{skill_id}` skill description -> `{skill_id}`")
        listed_skill_ids.append(skill_id)
    return "\n".join(lines) + "\n", listed_skill_ids


def _render_compact_skill_routing(public_skill_ids: list[str]) -> tuple[str, list[str]]:
    installed = set(public_skill_ids)
    lines = [
        "## Skill Routing",
        "",
        "Prefer installed charness public skills before improvising a repo-local workflow.",
        "",
        "Keep this block intentionally non-exhaustive so `AGENTS.md` stays stable as the installed charness skill catalog changes.",
        "",
    ]
    if "find-skills" in installed:
        lines.extend(
            [
                "When the right skill is unclear, or you need the current installed/trusted capability list, use `find-skills` first.",
                "",
            ]
        )
    lines.extend(
        [
            "Use these high-signal routes first:",
            "",
        ]
    )

    listed_skill_ids: list[str] = []
    for skill_id in COMPACT_ORDER:
        if skill_id in installed:
            lines.append(f"- {CURATED_HINTS[skill_id]} -> `{skill_id}`")
            listed_skill_ids.append(skill_id)

    if "find-skills" not in installed:
        lines.extend(
            [
                "",
                "If no bullet matches exactly, prefer the closest installed public skill before inventing repo-local workflow.",
            ]
        )
    return "\n".join(lines) + "\n", listed_skill_ids


def render_skill_routing(public_skill_ids: list[str], *, mode: str) -> tuple[str, list[str]]:
    if mode == "expanded":
        return _render_expanded_skill_routing(public_skill_ids)
    if mode == "compact":
        return _render_compact_skill_routing(public_skill_ids)
    raise ValueError(f"unknown skill routing mode: {mode}")


def build_payload(repo_root: Path) -> dict[str, object]:
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
    mode, mode_source = _resolve_mode(repo_root, None)
    markdown, listed_skill_ids = render_skill_routing(public_skill_ids, mode=mode)
    return {
        "public_skills": public_skill_ids,
        "support_skills": support_skill_ids,
        "available_modes": list(VALID_MODES),
        "agents_path": "AGENTS.md",
        "agents_has_skill_routing": has_skill_routing,
        "recommended_action": action,
        "skill_routing_mode": mode,
        "skill_routing_mode_source": mode_source,
        "listed_skill_ids": listed_skill_ids,
        "markdown": markdown,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--mode", choices=VALID_MODES)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
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
    mode, mode_source = _resolve_mode(repo_root, args.mode)
    markdown, listed_skill_ids = render_skill_routing(public_skill_ids, mode=mode)
    payload = {
        "public_skills": public_skill_ids,
        "support_skills": support_skill_ids,
        "available_modes": list(VALID_MODES),
        "agents_path": "AGENTS.md",
        "agents_has_skill_routing": has_skill_routing,
        "recommended_action": action,
        "skill_routing_mode": mode,
        "skill_routing_mode_source": mode_source,
        "listed_skill_ids": listed_skill_ids,
        "markdown": markdown,
    }
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(str(payload["markdown"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
