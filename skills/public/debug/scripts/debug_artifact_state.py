#!/usr/bin/env python3
"""What the debug artifact surface currently SAYS, read once for the whole plan.

A cohesive split, not a spill (the length gate refused one file and forbids an `_extra_lib`
companion): `plan_debug_run` assembles a plan -- required reads, gate packets, next action,
envelope -- and this module answers the questions that plan is assembled FROM. Which record
the current pointer resolves to, whether it is open, whether this run continues it, what the
producer declined, and which prior incidents are worth reading.

`_continues_existing_artifact` living here is the point of the split rather than an accident
of size: the plan's `mode`, its `next_action.kind`, and its `required_reads` each used to
decide it privately from the same two fields, and two bounded rounds found the copies
disagreeing. One module owns the question; the plan asks it.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

MAX_PRIOR_INCIDENTS = 5


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
risk_interrupt_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.risk_interrupt_lib")
_scaffold_artifact_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.scaffold_artifact_lib")
declarations = SKILL_RUNTIME.load_local_skill_module(__file__, "debug_artifact_declarations")


def _artifact_summary(repo_root: Path, scaffold: dict[str, Any]) -> dict[str, Any]:
    artifact_rel = str(scaffold["artifact_path"])
    artifact_path = repo_root / artifact_rel
    # A SIXTH derivation of the pointer rule used to live here, reimplemented from the
    # published pointer keys rather than by resolving the symlink -- so the single-owner
    # guard, which greps for readlink-shaped spellings, structurally could not see it. The
    # pair below now comes from the owner, which also fixes what a bounded round found: this
    # summary paired a pointer-derived `write_path` with `write_role` copied from the
    # scaffold AFTER its resolved-followup swap, so in that branch it reported a finished
    # resolved record labelled `durable_record`.
    write_rel, write_role, _ = _scaffold_artifact_lib.current_pointer_write_path(
        repo_root, Path(artifact_rel)
    )
    write_path = repo_root / write_rel
    exists = artifact_path.is_file()
    write_exists = write_path.is_file()
    text = artifact_path.read_text(encoding="utf-8") if exists else ""
    line_count = len(text.splitlines()) if exists else 0
    # Resolution lifecycle: an existing current pointer is treated as an OPEN
    # investigation to continue UNLESS it explicitly declares `- Resolution: resolved`.
    # Default open (missing field) keeps same-investigation resume and legacy
    # behavior; only an explicit `resolved` (set at closeout) makes the planner
    # treat the pointer as a closed prior incident instead of a continuation, so a
    # closed artifact stops hijacking a fresh bug.
    resolution = "resolved" if (exists and (declarations.parse_field(text, "Resolution") or "").strip().lower() == "resolved") else "open"
    if exists and scaffold.get("current_pointer_is_symlink"):
        status = "current_pointer_target_exists"
    elif exists:
        status = "current_pointer_exists"
    else:
        status = "missing"
    summary: dict[str, Any] = {
        "path": artifact_rel,
        "exists": exists,
        "resolution": resolution,
        "line_count": line_count,
        "status": status,
        "role": scaffold["artifact_role"],
        "write_path": write_rel,
        "write_exists": write_exists,
        "write_role": write_role,
        "current_pointer_symlink_target": scaffold["current_pointer_symlink_target"],
    }
    summary.update(declarations.risk_summary(artifact_path, risk_interrupt_lib))
    return summary

def _title_for(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def _prior_incidents(repo_root: Path, output_dir: str, current_path: str) -> list[dict[str, Any]]:
    directory = repo_root / output_dir
    if not directory.is_dir():
        return []
    current_resolved = (repo_root / current_path).resolve()
    candidates: list[Path] = []
    for pattern in ("debug-*.md", "20*.md"):
        candidates.extend(directory.glob(pattern))
    unique = sorted(set(candidates), key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
    incidents = []
    for path in unique:
        if path.name == "latest.md" or path.resolve() == current_resolved:
            continue
        rel_path = str(path.relative_to(repo_root))
        incidents.append(
            {
                "path": rel_path,
                "title": _title_for(path),
                "mtime": path.stat().st_mtime,
            }
        )
        if len(incidents) >= MAX_PRIOR_INCIDENTS:
            break
    return incidents

def _refusal_keys(scaffold: dict[str, Any]) -> dict[str, Any]:
    """What the producer declined, for every arm that hands back an existing record's path.

    Round 2 found the refusal keys living only on the scaffold branch — the one branch whose
    path is fresh. The three arms that actually name an existing record (continue, and both
    risk arms) carried none, so a run following `next_action` saw an overwrite target with no
    sign that the producer had refused to hand it out.
    """
    if "refused_write_artifact_path" not in scaffold:
        return {}
    return {
        "refused_write_artifact_path": scaffold["refused_write_artifact_path"],
        "refused_write_artifact_subject_key": scaffold["refused_write_artifact_subject_key"],
        "refused_write_artifact_reason": scaffold["refused_write_artifact_reason"],
        "continue_refused_subject_command": _continue_refused_command(scaffold),
    }

def _continue_refused_command(scaffold: dict[str, Any]) -> str:
    return (
        "python3 $SKILL_DIR/scripts/plan_debug_run.py --repo-root . "
        f"--subject {scaffold['refused_write_artifact_subject_key']}"
    )

def _continues_existing_artifact(artifact: dict[str, Any], scaffold: dict[str, Any]) -> bool:
    """ONE answer to "does this run continue the record the current pointer names".

    The plan's `mode`, its `next_action.kind`, and its `required_reads` each decided this
    independently from the same two fields, which is fine while the rule is one line and wrong
    the moment it grows a third clause: the subject clause landed in `mode` first, and the
    other two kept naming the record the scaffold had declined.

    Only a DECLARED disagreement stops the continue arm. An undeclared invocation is ambiguity,
    and this planner's fail-safe for ambiguity is deliberate and tested — an unparseable or
    missing resolution continues rather than abandoning an open investigation. The scaffold
    still refuses to hand an undeclared run a template write path onto that record, which is
    where the destructive half of the reported defect lived; routing an author to READ and
    continue it is the pre-existing contract and not this slice's to invert.
    """
    if not artifact["exists"] or artifact["resolution"] == "resolved":
        return False
    if scaffold.get("invocation_subject_key") is None:
        # Undeclared: ambiguity, and the fail-safe applies whatever the scaffold's reason was.
        return True
    return scaffold.get("refused_write_artifact_reason") not in (
        _scaffold_artifact_lib.SUBJECT_MATCH_MISMATCH,
        # A DECLARED subject against a target whose own name carries no subject is not
        # ambiguity on the author's side -- they said which investigation this is, and the
        # record cannot confirm it is that one.
        _scaffold_artifact_lib.SUBJECT_MATCH_UNKNOWN,
    )
