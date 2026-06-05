#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
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
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter

# Mirrors REQUIRED_SECTIONS in scripts/validate_handoff_artifact.py. The handoff
# validator enforces an EXACT H2 set, a `# ... Handoff` title, a <=70 line
# ceiling, non-empty sections, and a markdown link under `## References`, so the
# scaffold emits a skeleton that passes that validator out of the box.
SECTIONS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
)


def default_title(title: str | None) -> str:
    return title if title else "Session Handoff"


def _heading_title(title: str) -> str:
    # The validator requires "handoff" in the title line; guard a custom --title
    # so a subject like "Auth Migration" still yields a passing `# ... Handoff`.
    return title if "handoff" in title.lower() else f"{title} Handoff"


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {_heading_title(title)}", f"Date: {date_text}", ""]
    for heading in SECTIONS:
        if heading == "## Workflow Trigger":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO name the pickup workflow the next session invokes (e.g. `charness:handoff`)"
                    " and the one-line condition that triggers it.",
                    "",
                ]
            )
            continue
        if heading == "## Next Session":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO the smallest next action, with its target file or command.",
                    "",
                ]
            )
            continue
        if heading == "## Discuss":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO open decisions for the next operator, or `none` when there are none.",
                    "",
                ]
            )
            continue
        if heading == "## References":
            lines.extend(
                [
                    heading,
                    "",
                    "- [TODO pickup doc](docs/handoff.md)",
                    "",
                ]
            )
            continue
        lines.extend([heading, "", "- TODO", ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path) -> str:
    for ancestor in Path(__file__).resolve().parents:
        for script_name in ("validate_handoff_artifact.py", "validate-handoff-artifact.py"):
            candidate = ancestor / "scripts" / script_name
            if candidate.is_file():
                return f"python3 {candidate} --repo-root ."
    for script_name in ("validate_handoff_artifact.py", "validate-handoff-artifact.py"):
        repo_local = repo_root / "scripts" / script_name
        if repo_local.is_file():
            return f"python3 scripts/{script_name} --repo-root ."
    raise FileNotFoundError("validate_handoff_artifact.py not found in installed Charness layout")


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    artifact_path = str(adapter["artifact_path"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    return {
        "artifact_path": artifact_path,
        "artifact_role": "rolling",
        "write_artifact_path": artifact_path,
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": validator_command(repo_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to scaffold the handoff artifact into")
    parser.add_argument("--title", help="Title for the scaffolded handoff artifact")
    parser.add_argument("--json", action="store_true", help="Emit the payload as JSON instead of the rendered template")
    args = parser.parse_args()

    payload = payload_for(args.repo_root.resolve(), title=args.title)
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(payload["template"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
