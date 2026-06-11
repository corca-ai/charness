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

# Mirrors REQUIRED_SECTIONS in scripts/validate_quality_artifact.py. The scaffold
# emits a skeleton that passes that validator out of the box so an author fills
# slots instead of rediscovering the contract by trial-and-error.
SECTIONS = (
    "## Scope",
    "## Current Gates",
    "## Runtime Signals",
    "## Healthy",
    "## Weak",
    "## Missing",
    "## Deferred",
    "## Advisory",
    "## Delegated Review",
    "## Commands Run",
    "## Recommended Next Gates",
    "## History",
)
VALIDATOR_SCRIPT_NAMES = ("validate_quality_artifact.py", "validate-quality-artifact.py")


def default_title(title: str | None) -> str:
    return title if title else "Quality Review"


def render_template(*, title: str, date_text: str) -> str:
    # Validator note: the first line must be exactly "# Quality Review"; the
    # Runtime Signals/Advisory/Delegated Review/Recommended/History blocks below
    # carry the literal tokens validate_quality_artifact.py asserts on.
    lines = [f"# {title}", f"Date: {date_text}", ""]
    for heading in SECTIONS:
        if heading == "## Runtime Signals":
            lines.extend(
                [
                    heading,
                    "",
                    "- runtime source: structured metrics from `.charness/quality/runtime-signals.json`"
                    " rendered by `render_runtime_summary.py`; TODO profile (or state timing capture is missing).",
                    "- runtime hot spots: TODO top gate timings (latest / median vs budget).",
                    "- coverage gate: TODO run-quality pass/fail.",
                    "- evaluator depth: TODO live Cautilus run or deterministic-gates-only, and why.",
                    "",
                ]
            )
            continue
        if heading == "## Advisory":
            lines.extend(
                [
                    heading,
                    "",
                    "- TODO advisory bullet — cite `inventory`/command:/artifact: evidence"
                    " (or write `none found by inventory` with a `command:`).",
                    "",
                ]
            )
            continue
        if heading == "## Delegated Review":
            lines.extend(
                [
                    heading,
                    "",
                    "- Delegated Review: not_applicable — TODO record executed with the reviewer verdict,"
                    " or blocked with a concrete `host signal:`/`tool signal:`.",
                    "- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):"
                    " TODO whether re-delegated (required when status is executed and slow-gate scope).",
                    "",
                ]
            )
            continue
        if heading == "## Recommended Next Gates":
            lines.extend(
                [
                    heading,
                    "",
                    "- active TODO — name the exact gate/seam/command family to implement now.",
                    "- passive TODO — describe the watch item, because TODO it is not yet actionable.",
                    "",
                ]
            )
            continue
        if heading == "## History":
            lines.extend(
                [
                    heading,
                    "",
                    "- [TODO prior review](history/TODO-quality-review.md)",
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
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="quality")


if __name__ == "__main__":
    raise SystemExit(main())
