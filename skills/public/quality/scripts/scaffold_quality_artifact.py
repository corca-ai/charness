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
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)
_scaffold_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.scaffold_artifact_lib")
_resolve_quality_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_quality_artifact")

#: What a subject-mismatch redirect replaces on the current-pointer payload. The record
#: resolver owns these five; everything else on the payload (template, budget, validator
#: command) is the invocation's and must survive the swap.
_REDIRECTED_RECORD_KEYS = (
    "write_artifact_path",
    "write_artifact_role",
    "record_artifact_path",
    "update_current_pointer_after_write",
    "refresh_current_pointer_command",
    "refresh_current_pointer_argv",
)

# Mirrors REQUIRED_SECTIONS in scripts/validate_quality_artifact.py. The scaffold
# emits a skeleton that passes that validator out of the box so an author fills
# slots instead of rediscovering the contract by trial-and-error.

# Single-source the artifact word budget from the validator (the one authority
# for MAX_ARTIFACT_WORDS) so the scaffold surfaces the exact ceiling the gate
# enforces, without a second literal that can drift. If the validator module
# cannot load, degrade to no budget rather than break the scaffold — the field is
# additive guidance, never load-bearing.
try:
    _quality_validator = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.validate_quality_artifact")
    _MAX_ARTIFACT_WORDS: int | None = int(_quality_validator.MAX_ARTIFACT_WORDS)
except Exception:
    _quality_validator = None
    _MAX_ARTIFACT_WORDS = None


# Budget guidance routes the run to write-to-fit instead of writing long then
# trim-looping. It names the judgment-heavy sections that run largest in the real
# artifact (## Advisory, ## Recommended Next Quality Moves, ## Delegated Review)
# plus the structural rule for enumerate-prone sections, rather than asserting an
# unproven "usual overflow" section the one captured artifact does not support.
SIZE_GUIDANCE = (
    "Write the whole artifact within max_words; the budget charges words, so rewrapping buys nothing. The judgment-heavy sections "
    "(## Advisory, ## Recommended Next Quality Moves, ## Delegated Review) run "
    "largest — keep each finding to its evidence, and cite the inventory command "
    "rather than pasting every gate or command entry verbatim."
)
SECTIONS = (
    "## Scope",
    "## Surface Contract Review",
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
    # Validator note: the first line must be exactly "# Quality Review". Keep
    # caller-provided titles as metadata below the required Date line; the
    # Runtime Signals/Advisory/Delegated Review/Recommended/History blocks below
    # carry the literal tokens validate_quality_artifact.py asserts on.
    # Fill-time guard comments surface the conditional rules that only fire
    # AFTER the TODO slots are filled, so authors do not rediscover them one
    # failed validator run at a time. Fill the slots in place; rewriting
    # sections from scratch is what reintroduces the conditional violations.
    lines = [
        "# Quality Review",
        f"Date: {date_text}",
        f"Title: {title}",
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
                    " rendered by `render_runtime_summary.py`; TODO profile (or state timing capture is missing)."
                    " <!-- reproduction-source -->",
                    "- runtime hot spots: TODO top gate timings (latest / median vs budget).",
                    "- coverage gate: TODO run-quality pass/fail.",
                    "- evaluator depth: TODO consumer-owned evaluator or deterministic-gates-only, and why.",
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
                    "<!-- fill guard: an executed status must substantiate itself — name the review"
                    " channel that ran (reviewer, bounded subagent, critique angle, counterweight),"
                    " the disposition it returned (findings, verdict, what it confirmed or refuted),"
                    " or the path of the record it wrote; the standing slow-gate lens bullet alone"
                    " does not count, and an executed status that also says no reviewer ran is"
                    " refused. Guard comments are stripped before these rules read the section -->",
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
        if heading == "## Surface Contract Review":
            lines.extend(
                [
                    heading,
                    "",
                    "- semantic coverage: `not-in-scope` — no user-visible or cross-boundary surface is in scope for this review.",
                    "- surface: no semantic surface in scope",
                    "- owner: quality reviewer owns this scope declaration; no product owner is claimed.",
                    "- projections: not assessed because no semantic surface is in scope",
                    "- state scope: not assessed because no semantic surface is in scope",
                    "- transitions: not assessed because no semantic surface is in scope",
                    "- proof boundary: scoped quality command only; no semantic behavior claim",
                    "- unexamined axes: surface, owner, projection, state scope, transitions, proof boundary",
                    "",
                ]
            )
            continue
        lines.extend([heading, "", "TODO", ""])
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path) -> str:
    return _scaffold_lib.validator_command(repo_root=repo_root, script_file=__file__, script_names=VALIDATOR_SCRIPT_NAMES)


def invocation_subject_key(*, title: str | None, subject: str | None, date_text: str) -> str | None:
    """WHICH review this invocation is — `quality`'s own subject key: its slug AND its date.

    The date channel is this family's, and only this family's: a quality review written today
    over yesterday's dated record destroys a finished review, while `debug` continuing
    yesterday's open investigation in place is designed behavior. `validate_quality_artifact`
    already refuses that disagreement AFTER the artifact is written; the same channel here
    means the producer never hands the destructive path back in the first place.

    Never `None`, unlike `debug`'s. The two families differ because their default slugs differ
    in kind: `debug`'s `debug-review` names twenty real records with nothing to tell them
    apart, while `quality`'s `quality-review@<today>` names exactly one thing — today's review
    — because the date channel is always known whether or not the author declared anything.
    An undeclared `quality` run is not ambiguous about which review it is.
    """
    return _scaffold_lib.compose_subject_key(_scaffold_lib.slugify(subject or default_title(title)), date_text)


def target_subject_key(write_path: str) -> str | None:
    """The subject of the record the path NAMES, in this family's two channels.

    `None` — not a dated record — is UNKNOWN, and unknown does not write in place. The earlier
    version reasoned that an undated `latest.md` is "a pointer whose body is a copy of the
    record it stands for" and let the write through; that is an unproven premise about consumer
    repos, and the repo's own history records the opposite (a `latest.md` regular file holding
    the previous review is exactly the layout `inventory_current_pointer_layouts` enumerates as
    `regular_current_pointer`).
    """
    slug, date_text = _scaffold_lib.record_subject_channels(write_path)
    return _scaffold_lib.compose_subject_key(slug, date_text)


def payload_for(repo_root: Path, *, title: str | None, subject: str | None = None) -> dict[str, object]:
    # GUARDED AT THE READ SITE. Every scaffold in this family reads its write TARGET out
    # of the adapter, so an unhonored declaration does not degrade the answer -- it
    # relocates the artifact. Measured on the real CLI at `0bcb6b227`: a repo declaring
    # `output_dir: docs/mine-quality` under `version: 9` got back `artifact_path: charness-artifacts/quality/latest.md`, exit 0, and the scaffold
    # would have written there.
    #
    # `payload_for` rather than `main()`: the target is resolved HERE, so the refusal is a
    # property of this function rather than of whatever calls it. A round-1 bounded review
    # over rows 6-13 REFUTED the sentence this comment used to carry ("this module's
    # `payload_for` is imported elsewhere; a refusal at the entrypoint would cover one
    # caller") -- verified false for quality, critique and handoff, whose only importers
    # are tests. It is true only for retro (`plan_retro_run`) and debug (`plan_debug_run`).
    # This slice had ALREADY struck the same unmeasured harm claim once, for rows 1-5.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="quality-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    output_dir = Path(adapter["data"]["output_dir"])
    artifact_date = dt.date.today()
    date_text = artifact_date.isoformat()
    resolved_title = default_title(title)
    subject_key = invocation_subject_key(title=title, subject=subject, date_text=date_text)
    size_budget = _scaffold_lib.size_budget(
        _quality_validator, _MAX_ARTIFACT_WORDS, adapter, guidance=SIZE_GUIDANCE
    )
    payload = _scaffold_lib.current_pointer_payload(
        repo_root=repo_root,
        output_dir=output_dir,
        date_text=date_text,
        title=resolved_title,
        template=render_template(title=resolved_title, date_text=date_text),
        validator_command=validator_command(repo_root),
        size_budget=size_budget,
    )
    pointer_target_path = str(payload["write_artifact_path"])
    pointer_target_subject = target_subject_key(pointer_target_path)
    if _scaffold_lib.diverts_from_target(
        repo_root,
        write_path=pointer_target_path,
        facts=_scaffold_lib.subject_identity_facts(
            invocation_subject_key=subject_key,
            target_subject_key=pointer_target_subject,
        ),
    ):
        # Routed onto this review's OWN dated record, with the pointer refresh that follows
        # the write, rather than onto the record the pointer currently names. The resolver
        # already owns that shape for `--intent record`; rebuilding it here would be a second
        # copy of the rule the current-pointer consolidation exists to prevent.
        record = _resolve_quality_artifact.payload_for(
            repo_root,
            slug=_scaffold_lib.slugify(subject or default_title(title)),
            intent="record",
            artifact_date=artifact_date,
        )
        # The redirect target is a DATED path the resolver computes without asking whether
        # anything is at it. Round 2 found the consequence: with a stale pointer and today's
        # review already written, the family whose contract is "must never overwrite a finished
        # review" routed straight onto that finished review and reported the stale pointer as
        # the thing it had protected. A destination that already holds a record is not a
        # destination; the author names one.
        if (repo_root / str(record["write_artifact_path"])).exists():
            raise SystemExit(
                f"quality: the current pointer names `{pointer_target_path}`, which is not this "
                f"review ({subject_key}), and this review's own record "
                f"`{record['write_artifact_path']}` already exists. Append to that record, or "
                f"rerun with --subject <distinct review slug>."
            )
        payload.update({key: record[key] for key in _REDIRECTED_RECORD_KEYS})
        # No existence condition: `diverts_from_target` already reached this branch only for a
        # target that holds a record OR positively names another subject, and the second case
        # is the dangling pointer — declined, nothing there, and still worth reporting.
        if pointer_target_path != str(payload["write_artifact_path"]):
            payload.update(
                _scaffold_lib.subject_refusal_facts(
                    refused_path=pointer_target_path,
                    refused_subject_key=pointer_target_subject,
                    reason=str(
                        _scaffold_lib.subject_identity_facts(
                            invocation_subject_key=subject_key,
                            target_subject_key=pointer_target_subject,
                        )["write_artifact_subject_match"]
                    ),
                )
            )
        _scaffold_lib.with_write_target_facts(repo_root, payload)
    payload.update(
        _scaffold_lib.final_subject_facts(
            invocation_subject_key=subject_key,
            target_subject_key=target_subject_key(str(payload["write_artifact_path"])),
            chosen=str(payload["write_artifact_path"]) != pointer_target_path,
        )
    )
    return payload


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="quality")


if __name__ == "__main__":
    raise SystemExit(main())
