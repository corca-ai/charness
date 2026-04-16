#!/usr/bin/env python3

from __future__ import annotations

import argparse
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


def render_skill_routing(public_skill_ids: list[str]) -> str:
    installed = set(public_skill_ids)
    lines = [
        "## Skill Routing",
        "",
        "When one of these shows up in a request, prefer the named skill first:",
        "",
    ]
    for skill_id in ORDER:
        if skill_id in installed:
            lines.append(f"- {CURATED_HINTS[skill_id]} -> `{skill_id}`")
    unknown = sorted(installed - set(ORDER))
    for skill_id in unknown:
        lines.append(f"- task matching the `{skill_id}` skill description -> `{skill_id}`")
    return "\n".join(lines) + "\n"


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
    return {
        "public_skills": public_skill_ids,
        "support_skills": support_skill_ids,
        "agents_path": "AGENTS.md",
        "agents_has_skill_routing": has_skill_routing,
        "recommended_action": action,
        "markdown": render_skill_routing(public_skill_ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.repo_root.resolve())
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(str(payload["markdown"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
