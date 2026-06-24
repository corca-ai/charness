#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

SKILL_RUNTIME_PATH = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
if SKILL_RUNTIME_PATH is None:
    raise ImportError("skill_runtime_bootstrap.py not found")
sys_path_root = str(SKILL_RUNTIME_PATH.parent)
if sys_path_root not in sys.path:
    sys.path.insert(0, sys_path_root)
import skill_runtime_bootstrap as SKILL_RUNTIME  # noqa: E402

_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter
_scaffold_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.scaffold_artifact_lib")

VALIDATOR_SCRIPT_NAMES = ("validate_retro_artifact.py", "validate-retro-artifact.py")

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
    lines.extend(["## Persisted", "", "Persisted: yes: TODO path", ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path, write_artifact_path: str) -> str:
    return _scaffold_lib.validator_command(
        repo_root=repo_root,
        script_file=__file__,
        script_names=VALIDATOR_SCRIPT_NAMES,
        artifact_path=write_artifact_path,
    )


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
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="retro")


if __name__ == "__main__":
    raise SystemExit(main())
