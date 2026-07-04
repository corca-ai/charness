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

# Mirrors REQUIRED_SECTIONS in scripts/validate_quality_artifact.py. The scaffold
# emits a skeleton that passes that validator out of the box so an author fills
# slots instead of rediscovering the contract by trial-and-error.

# Single-source the artifact line budget from the validator (the one authority
# for MAX_ARTIFACT_LINES) so the scaffold surfaces the exact ceiling the gate
# enforces, without a second literal that can drift. If the validator module
# cannot load, degrade to no budget rather than break the scaffold — the field is
# additive guidance, never load-bearing.
try:
    _quality_validator = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.validate_quality_artifact")
    _MAX_ARTIFACT_LINES: int | None = int(_quality_validator.MAX_ARTIFACT_LINES)
except Exception:
    _MAX_ARTIFACT_LINES = None

# Budget guidance routes the run to write-to-fit instead of writing long then
# trim-looping. It names the judgment-heavy sections that run largest in the real
# artifact (## Advisory, ## Recommended Next Quality Moves, ## Delegated Review)
# plus the structural rule for enumerate-prone sections, rather than asserting an
# unproven "usual overflow" section the one captured artifact does not support.
SIZE_GUIDANCE = (
    "Write the whole artifact within max_lines. The judgment-heavy sections "
    "(## Advisory, ## Recommended Next Quality Moves, ## Delegated Review) run "
    "largest — keep each finding to its evidence, and cite the inventory command "
    "rather than pasting every gate or command entry verbatim."
)
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
    "## Recommended Next Quality Moves",
    "## History",
)
VALIDATOR_SCRIPT_NAMES = ("validate_quality_artifact.py", "validate-quality-artifact.py")


def default_title(title: str | None) -> str:
    return title if title else "Quality Review"


def render_template(*, title: str, date_text: str) -> str:
    # Validator note: the first line must be exactly "# Quality Review"; the
    # Runtime Signals/Advisory/Delegated Review/Recommended/History blocks below
    # carry the literal tokens validate_quality_artifact.py asserts on.
    # Fill-time guard comments surface the conditional rules that only fire
    # AFTER the TODO slots are filled, so authors do not rediscover them one
    # failed validator run at a time. Fill the slots in place; rewriting
    # sections from scratch is what reintroduces the conditional violations.
    lines = [
        f"# {title}",
        f"Date: {date_text}",
        "",
        "<!-- fill guard: fill the TODO slots in place; the payload's"
        " validator_command reports every rule violation in one pass -->",
        "",
    ]
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
                    "- structural review result: TODO answer `structural_review_packet` from the planner because target-skill recommendations need judgment beyond heuristic output.",
                    "- prose review result: TODO trigger boundaries, progressive disclosure, helper ownership, dogfood pressure, and target-vs-ambient split because TODO evidence.",
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
        if heading == "## Recommended Next Quality Moves":
            lines.extend(
                [
                    heading,
                    "",
                    "- active TODO — capability_needed=TODO; next_center=TODO; transformation=TODO; proof_boundary=TODO; enforcement_posture=advisory.",
                    "- passive TODO — capability_needed=TODO; next_center=TODO; transformation=TODO; proof_boundary=TODO; enforcement_posture=no-gate because TODO it is not yet actionable.",
                    "<!-- fill guard: every bullet's FIRST line starts with `- active ` or"
                    " `- passive `, and a passive bullet's first line must carry ` because`"
                    " or ` until` before any wrap; apply move-card fields only to recommended"
                    " moves, not every finding; candidate-floor requires a north-star plus"
                    " floor-addition-restraint record -->",
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
        if heading == "## Scope":
            lines.extend(
                [
                    heading,
                    "",
                    "Target boundary: TODO target skill, repo-wide quality question, or explicit non-target.",
                    "",
                    "Ambient repo findings: TODO broad-gate failures and opportunistic repairs that are not target-skill quality findings.",
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
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="quality")


if __name__ == "__main__":
    raise SystemExit(main())
