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
_resolve_artifact_path = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.resolve_artifact_path")
_scaffold_artifact_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.scaffold_artifact_lib")

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


def _append_placeholder_section(lines: list[str], heading: str) -> None:
    lines.extend((heading, "", "TODO", ""))


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
        _append_placeholder_section(lines, heading)
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path) -> str:
    return _scaffold_lib.validator_command(repo_root=repo_root, script_file=__file__, script_names=VALIDATOR_SCRIPT_NAMES)


def _resolution(path: Path) -> str:
    if not path.is_file():
        return "open"
    prefix = "- Resolution:"
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return "resolved" if stripped[len(prefix) :].strip().lower() == "resolved" else "open"
    return "open"


def _current_pointer_symlink_target(repo_root: Path, artifact_path: str) -> str | None:
    """From the single owner, not a private copy.

    This was a FIFTH implementation of the pointer rule. It existed because
    `published_pointer_state` filters this key out, so a bounded review's answer to "is the
    fourth copy the last one" was no -- the owner's own key filtering was what forced the
    copy to stay.
    """
    state = _scaffold_artifact_lib.current_pointer_state(repo_root, Path(artifact_path))
    target = state["current_pointer_symlink_target"]
    return str(target) if isinstance(target, str) else None


def _resolved_followup_record_payload(
    repo_root: Path,
    *,
    adapter: dict[str, object],
    resolved_title: str,
    artifact_date: dt.date,
    current_pointer_target_path: str | None,
) -> dict[str, object]:
    def _record_payload_for(title_text: str) -> dict[str, object]:
        return _resolve_artifact_path.payload_for(
            repo_root,
            "debug",
            title_text,
            intent="record",
            artifact_date=artifact_date,
            adapter=adapter,
        )

    current_target = current_pointer_target_path or ""
    candidate = _record_payload_for(resolved_title)
    candidate_path = str(candidate["write_artifact_path"])
    if candidate_path != current_target and not (repo_root / candidate_path).exists():
        return candidate
    for suffix in ("followup", "followup-2", "followup-3", "followup-4"):
        candidate = _record_payload_for(f"{resolved_title} {suffix}")
        candidate_path = str(candidate["write_artifact_path"])
        if candidate_path != current_target and not (repo_root / candidate_path).exists():
            return candidate
    raise SystemExit(
        "resolved current debug artifact needs a fresh dated follow-up record, but every deterministic "
        "default slug for today already exists; rerun scaffold_debug_artifact.py with --title <specific follow-up title>"
    )


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    artifact_date = dt.date.today()
    date_text = artifact_date.isoformat()
    resolved_title = default_title(title)
    size_budget = (
        {"max_lines": _MAX_ARTIFACT_LINES, "guidance": SIZE_GUIDANCE}
        if _MAX_ARTIFACT_LINES is not None
        else None
    )
    payload = _resolve_artifact_path.payload_for(
        repo_root,
        "debug",
        resolved_title,
        intent="current",
        artifact_date=dt.date.today(),
        adapter=adapter,
    )
    current_write_path = repo_root / str(payload["write_artifact_path"])
    if _resolution(current_write_path) == "resolved":
        record_payload = _resolved_followup_record_payload(
            repo_root,
            adapter=adapter,
            resolved_title=resolved_title,
            artifact_date=artifact_date,
            current_pointer_target_path=payload.get("current_pointer_target_path")
            if isinstance(payload.get("current_pointer_target_path"), str)
            else None,
        )
        for key in (
            "intent",
            "record_artifact_path",
            "write_artifact_path",
            "write_artifact_role",
            "update_current_pointer_after_write",
            "refresh_current_pointer_argv",
            "refresh_current_pointer_command",
            "frontmatter",
        ):
            payload[key] = record_payload[key]
    payload.update(
        {
            "date": date_text,
            "title": resolved_title,
            "artifact_role": "current_pointer",
            "current_pointer_symlink_target": _current_pointer_symlink_target(repo_root, str(payload["artifact_path"])),
            "template": render_template(title=resolved_title, date_text=date_text),
            "validator_command": validator_command(repo_root),
        }
    )
    if size_budget is not None:
        payload["size_budget"] = size_budget
    # LAST, because the resolved-followup branch above replaces `write_artifact_path` through
    # a fixed key list. Facts computed before that swap describe the wrong file.
    _scaffold_artifact_lib.with_write_target_facts(repo_root, payload)
    return payload


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="debug")


if __name__ == "__main__":
    raise SystemExit(main())
