#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
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

SECTIONS = (
    "## Problem",
    "## Correct Behavior",
    "## Observed Facts",
    "## Reproduction",
    "## Candidate Causes",
    "## Hypothesis",
    "## Verification",
    "## Root Cause",
    "## Invariant Proof",
    "## Detection Gap",
    "## Sibling Search",
    "## Seam Risk",
    "## Interrupt Decision",
    "## Prevention",
)
VALIDATOR_SCRIPT_NAMES = ("validate_debug_artifact.py", "validate-debug-artifact.py")


def default_title(title: str | None) -> str:
    return title if title else "Debug Review"


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {title}", f"Date: {date_text}", ""]
    for heading in SECTIONS:
        if heading == "## Candidate Causes":
            lines.extend([heading, "", "- TODO", "- TODO", "- TODO", ""])
            continue
        if heading == "## Invariant Proof":
            lines.extend(
                [
                    heading,
                    "",
                    "- Invariant: n/a - not a workflow-boundary propagation bug",
                    "- Producer Proof: n/a",
                    "- Final-Consumer Proof: n/a",
                    "- Interface-Shape Sibling Scan: n/a",
                    "- Non-Claims: n/a",
                    "",
                ]
            )
            continue
        if heading == "## Detection Gap":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO surface | what did not fire | smallest change to fire it",
                    "",
                ]
            )
            continue
        if heading == "## Sibling Search":
            lines.extend(
                [
                    heading,
                    "",
                    "- Mental model: TODO",
                    "- TODO axis: TODO location | decision: TODO | proof: TODO",
                    "- cross-file: TODO name a sibling outside the subject file"
                    " (or replace this line with `no cross-file sibling: <reason>`)",
                    "",
                ]
            )
            continue
        if heading == "## Seam Risk":
            lines.extend(
                [
                    heading,
                    "",
                    "- Interrupt ID: TODO",
                    "- Risk Class: none",
                    "- Seam: none",
                    "- Disproving Observation: none",
                    "- What Local Reasoning Cannot Prove: none",
                    "- Generalization Pressure: none",
                    "",
                ]
            )
            continue
        if heading == "## Interrupt Decision":
            lines.extend(
                [
                    heading,
                    "",
                    "- Critique Required: no",
                    "- Next Step: impl",
                    "- Handoff Artifact: none",
                    "",
                ]
            )
            continue
        lines.extend([heading, "", "TODO", ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path) -> str:
    return _scaffold_lib.validator_command(repo_root=repo_root, script_file=__file__, script_names=VALIDATOR_SCRIPT_NAMES)


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    output_dir = Path(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    return _scaffold_lib.current_pointer_payload(
        repo_root=repo_root,
        output_dir=output_dir,
        date_text=date_text,
        title=resolved_title,
        template=render_template(title=resolved_title, date_text=date_text),
        validator_command=validator_command(repo_root),
    )


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="debug")


if __name__ == "__main__":
    raise SystemExit(main())
