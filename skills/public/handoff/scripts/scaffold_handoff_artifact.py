#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import runpy
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
_scaffold_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.scaffold_artifact_lib")

# Mirrors REQUIRED_SECTIONS in scripts/validate_handoff_artifact.py. The handoff
# validator enforces an EXACT H2 set, a `# ... Handoff` title, a content-line
# ceiling (blank lines, the required headings, and `## References` are not
# counted), non-empty sections, and a markdown link under `## References`, so the
# scaffold emits a skeleton that passes that validator out of the box.
SECTIONS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
)
VALIDATOR_SCRIPT_NAMES = ("validate_handoff_artifact.py", "validate-handoff-artifact.py")


def default_title(title: str | None) -> str:
    return title if title else "Session Handoff"


def _heading_title(title: str) -> str:
    # The validator requires "handoff" in the title line; guard a custom --title
    # so a subject like "Auth Migration" still yields a passing `# ... Handoff`.
    return title if "handoff" in title.lower() else f"{title} Handoff"


# One body per section, as DATA. The if-chain this replaces said the same four
# lines five times, which read as five decisions and was one. `## Current State`
# and `## Next Session` carry an owner because the stub itself has to VALIDATE:
# the failure hint points authors at this scaffold, and a scaffold whose output
# fails the gate teaches that the gate is noise.
SECTION_BODIES = {
    "## Workflow Trigger": "- TODO name the pickup workflow the next session invokes"
    " (e.g. `charness:handoff`) and the one-line condition that triggers it.",
    "## Current State": "- TODO one state fact that changes the next action, with the"
    " [artifact](docs/handoff.md) or command that owns it.",
    "## Next Session": "- TODO the smallest next action, carrying its owner:"
    " [target file](docs/handoff.md), a command, or an issue id.",
    "## Discuss": "- TODO open decisions for the next operator, or `none` when there are none.",
    "## References": "- [TODO pickup doc](docs/handoff.md)",
}


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {_heading_title(title)}", f"Date: {date_text}", ""]
    for heading in SECTIONS:
        lines.extend([heading, "", SECTION_BODIES.get(heading, "- TODO"), ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path) -> str:
    return _scaffold_lib.validator_command(repo_root=repo_root, script_file=__file__, script_names=VALIDATOR_SCRIPT_NAMES)


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    artifact_path = str(adapter["artifact_path"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    return _scaffold_lib.with_write_target_facts(repo_root, {
        "artifact_path": artifact_path,
        "artifact_role": "rolling",
        "write_artifact_path": artifact_path,
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": validator_command(repo_root),
    })


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="handoff")


if __name__ == "__main__":
    raise SystemExit(main())
