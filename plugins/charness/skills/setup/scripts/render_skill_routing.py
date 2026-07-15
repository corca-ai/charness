#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_ROUTING = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.setup_skill_routing_lib"
)


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
    lines = [
        "## Skill Routing",
        "",
        "At session start, a pickup follows docs/handoff.md `## Workflow Trigger`; otherwise choose the durable workflow directly from installed skill metadata and model judgment. If hidden support/integration availability is unclear, run the read-only `charness catalog list --repo-root <repo>` inventory. Treat its facts only as inventory; if the command returns nonzero, report the command failure. When a request names an external URL or source, use `gather` before deciding; validation closeout or operator-reading tests go through `quality`.",
        "",
        "The SessionStart hook may inject this context when installed; this block is the fallback when it is absent.",
        "",
    ]
    listed_skill_ids = []
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
    semantically_complete = bool(
        has_skill_routing
        and _ROUTING.agents_skill_routing_semantically_complete(agents_text)
    )
    expected_lines = tuple(line for line in markdown.splitlines() if line.strip() and line != "## Skill Routing")
    missing_expected_snippets = [line for line in expected_lines if line not in agents_text] if has_skill_routing else []
    if matches_compact_block or semantically_complete:
        missing_expected_snippets = []
    if not agents.exists():
        action = "create_agents_with_skill_routing"
    elif matches_compact_block or semantically_complete:
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
        "skill_routing_semantically_complete": semantically_complete,
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
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose skill-routing markdown should be rendered")
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
