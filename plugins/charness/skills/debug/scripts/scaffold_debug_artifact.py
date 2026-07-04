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

# Single-source the artifact line budget from the validator (the one authority
# for MAX_ARTIFACT_LINES) so the scaffold surfaces the exact ceiling the gate
# enforces. If the validator module cannot load, degrade to no budget rather
# than break the scaffold — the field is additive guidance, never load-bearing.
try:
    _debug_validator = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.validate_debug_artifact")
    _MAX_ARTIFACT_LINES: int | None = int(_debug_validator.MAX_ARTIFACT_LINES)
except Exception:
    _MAX_ARTIFACT_LINES = None

# The recurring overflow in real captures is ## Sibling Search (a rich structural
# scan that enumerates many siblings). The budget guidance routes the run to the
# abstraction rule that keeps it tight, instead of writing long then trim-looping.
SIZE_GUIDANCE = (
    "Write the whole artifact within max_lines. The usual overflow is "
    "## Sibling Search — abstract it to the mental-model + axis lines rather "
    "than enumerating every sibling verbatim (references/sibling-search.md)."
)

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
        if heading == "## Reproduction":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO smallest reproduction (input/path/env that still fails),"
                    " or `n/a — could not reproduce: <why; gathered stronger observation instead>`",
                    "",
                ]
            )
            continue
        if heading == "## Hypothesis":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO falsifiable claim: <what observably changes if true>"
                    " | disconfirmer: <cheapest check run to refute it before the fix>",
                    "",
                ]
            )
            continue
        if heading == "## Verification":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO result: confirmed | disconfirmed | still-candidate"
                    " — evidence from the disconfirmer/reproduction above",
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
                    "- Resolution: open",
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
    size_budget = (
        {"max_lines": _MAX_ARTIFACT_LINES, "guidance": SIZE_GUIDANCE}
        if _MAX_ARTIFACT_LINES is not None
        else None
    )
    return _scaffold_lib.current_pointer_payload(
        repo_root=repo_root,
        output_dir=output_dir,
        date_text=date_text,
        title=resolved_title,
        template=render_template(title=resolved_title, date_text=date_text),
        validator_command=validator_command(repo_root),
        size_budget=size_budget,
    )


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="debug")


if __name__ == "__main__":
    raise SystemExit(main())
