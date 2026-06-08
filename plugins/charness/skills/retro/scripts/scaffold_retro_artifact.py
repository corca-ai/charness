#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
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

# The retro validator (scripts/validate_retro_artifact.py) is opt-in: it only
# enforces the `## Sibling Search` follow-up grammar. The scaffold emits the
# canonical retro sections plus a `## Sibling Search` bullet carrying a valid
# `follow-up:` so the part the validator actually checks passes unedited and an
# author sees the exact format the follow-up rule demands.


def default_title(title: str | None) -> str:
    return title if title else "Session Retro"


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "retro"


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {title}", f"Date: {date_text}", ""]
    lines.extend(["## Mode", "", "session", ""])
    lines.extend(["## Context", "", "TODO what happened and why this retro.", ""])
    lines.extend(["## Evidence Summary", "", "- TODO concrete evidence (paths, line counts, command output).", ""])
    lines.extend(["## Waste", "", "TODO what created rework or wasted effort.", ""])
    lines.extend(["## Critical Decisions", "", "- TODO the decision that shaped the next move.", ""])
    lines.extend(
        [
            "## Expert Counterfactuals",
            "",
            "- TODO a named-expert or direct counterfactual lens that would have changed the next move.",
            "",
        ]
    )
    lines.extend(
        [
            "## Sibling Search",
            "",
            "- TODO axis: TODO location | decision: valid follow-up outside the slice"
            " | proof: TODO | follow-up: deferred TODO-handoff-anchor",
            "",
        ]
    )
    lines.extend(["## Next Improvements", "", "- workflow: TODO", "- capability: TODO", "- memory: TODO", ""])
    lines.extend(["## Persisted", "", "yes: TODO path", ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path, write_artifact_path: str) -> str:
    # Prefer the repo-local validator when the working repo owns one so the cited
    # check == the broad gate; fall back to the installed-plugin copy only for a
    # consumer repo that ships no validator of its own. Repo-local-first kills the
    # installed-vs-repo version-skew class (an installed validator looser than the
    # repo's must not shadow it).
    for script_name in ("validate_retro_artifact.py", "validate-retro-artifact.py"):
        repo_local = repo_root / "scripts" / script_name
        if repo_local.is_file():
            return f"python3 scripts/{script_name} --repo-root . --paths {write_artifact_path}"
    for ancestor in Path(__file__).resolve().parents:
        for script_name in ("validate_retro_artifact.py", "validate-retro-artifact.py"):
            candidate = ancestor / "scripts" / script_name
            if candidate.is_file():
                return f"python3 {candidate} --repo-root . --paths {write_artifact_path}"
    raise FileNotFoundError("validate_retro_artifact.py not found in installed Charness layout")


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    output_dir = str(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    write_artifact_path = f"{output_dir}/{date_text}-{_slug(resolved_title)}.md"
    return {
        "artifact_path": write_artifact_path,
        "artifact_role": "record",
        "write_artifact_path": write_artifact_path,
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": validator_command(repo_root, write_artifact_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to scaffold the retro artifact into")
    parser.add_argument("--title", help="Title for the scaffolded retro artifact")
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
