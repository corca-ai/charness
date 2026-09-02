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
    __file__, "scripts.adapters.adapter_version_verdict"
)
_scaffold_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.scaffold_artifact_lib")
_resolve_artifact_path = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.resolve_artifact_path")
_scaffold_artifact_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.scaffold_artifact_lib")
_followup_routing = SKILL_RUNTIME.load_local_skill_module(__file__, "debug_followup_routing")

# Single-source the artifact word budget from the validator (the one authority
# for MAX_ARTIFACT_WORDS) so the scaffold surfaces the exact ceiling the gate
# enforces. If the validator module cannot load, degrade to no budget rather
# than break the scaffold — the field is additive guidance, never load-bearing.
try:
    _debug_validator = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.gates.validate_debug_artifact")
    _MAX_ARTIFACT_WORDS: int | None = int(_debug_validator.MAX_ARTIFACT_WORDS)
except Exception:
    _debug_validator = None
    _MAX_ARTIFACT_WORDS = None


# The recurring overflow in real captures is ## Sibling Search (a rich structural
# scan that enumerates many siblings). The budget guidance routes the run to the
# abstraction rule that keeps it tight, instead of writing long then trim-looping.
SIZE_GUIDANCE = (
    "Write the whole artifact within max_words; the budget charges words, so rewrapping buys nothing. The usual overflow is "
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


def render_template(*, title: str, date_text: str, evidence_mode: bool = False) -> str:
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
    if evidence_mode:
        lines.extend(
            [
                "## Evidence Disposition",
                "",
                "- Report Identity: TODO source:id#sha256:<64 lowercase hex>",
                "- Reported Findings: TODO non-negative integer",
                "- Dispositioned Findings: TODO finding IDs",
                "- Missing Findings: none",
                "- Evidence Digest: TODO sha256:<64 lowercase hex>",
                "- Report Source: TODO repo-relative report or fixture path",
                "- Report Source SHA256: TODO 64 lowercase hex",
                "",
                "## Adversarial Verification",
                "",
                "<!-- Replace every TODO with a typed claim and a receipt from the execution harness. -->",
                "- Finding: TODO-F1 | source: TODO | expected: TODO | stimulus: TODO | disposition: TODO | observed: TODO | proof: TODO | handoff: TODO | next move: TODO | receipt: TODO repo-relative receipt.json | receipt sha256: TODO",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def validator_command(
    repo_root: Path, write_artifact_path: str | None = None, *, evidence_mode: bool = False
) -> str:
    """The command that validates THIS artifact, scoped to it when the path is known.

    Unscoped, this emitted `--repo-root .`, which for a corpus validator means the whole
    historical debug directory. Reported from a consumer repo: a fresh, valid artifact
    validated clean and the command still exited 1, because unrelated older records carry
    legacy-schema debt. The operator cannot tell from the exit code whether the thing they
    just wrote is malformed or whether the corpus was already red, and the repo's own
    changed-scope gate disagreed with the command the skill emitted.

    `--paths` was already modeled and already exposed; `retro`, `ideation` and `critique`
    already pass their write path. Debug was the family that did not.

    The path stays OPTIONAL rather than required: a caller with no chosen write path
    (there is one, in the refusal preview) gets the corpus command, which is the honest
    answer when there is no single artifact to name. A default of None is what keeps that
    caller from having to invent a path to ask the question.
    """
    return _scaffold_lib.validator_command(
        repo_root=repo_root,
        script_file=__file__,
        script_names=VALIDATOR_SCRIPT_NAMES,
        artifact_path=write_artifact_path,
        evidence_mode=evidence_mode,
    )


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


def invocation_subject_key(*, title: str | None, subject: str | None) -> str | None:
    """WHICH investigation this invocation is for — `debug`'s own subject key.

    `None` when the author declared neither `--subject` nor `--title`, and that is the whole
    fix: an undeclared run is a NEW investigation, so it must not resolve onto an open record
    whoever opened it. Falling back to the default title looked equivalent and was not — a
    bounded round found that `slugify("Debug Review")` is `debug-review`, that this repo holds
    twenty `<date>-debug-review.md` records, and that a brand-new undeclared run therefore
    MATCHED an unrelated open one and reported `continue-existing-artifact`. The generic
    default was not a key that matches no investigation; it was the most common real one.

    An author continuing investigation X declares `--subject <X's slug>`.
    """
    declared = subject or title
    return _scaffold_artifact_lib.slugify(declared) if declared else None


def payload_for(
    repo_root: Path,
    *,
    title: str | None,
    subject: str | None = None,
    evidence_mode: bool = False,
) -> dict[str, object]:
    # GUARDED AT THE READ SITE. Every scaffold in this family reads its write TARGET out
    # of the adapter, so an unhonored declaration does not degrade the answer -- it
    # relocates the artifact. Measured on the real CLI at `0bcb6b227`: a repo declaring
    # `output_dir: docs/mine-debug` under `version: 9` got back `artifact_path: charness-artifacts/debug/latest.md`, exit 0, and the scaffold
    # would have written there.
    #
    # `payload_for` rather than `main()`, and here the importer claim is MEASURED rather
    # than assumed: `plan_debug_run` calls this function directly, so a refusal at the
    # entrypoint would have covered the CLI and left that caller on charness defaults.
    # (The same sentence was refuted for quality, critique and handoff, whose only
    # importers are tests -- see those files.)
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="debug-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    artifact_date = dt.date.today()
    date_text = artifact_date.isoformat()
    resolved_title = default_title(title)
    subject_key = invocation_subject_key(title=title, subject=subject)
    size_budget = _scaffold_lib.size_budget(
        _debug_validator, _MAX_ARTIFACT_WORDS, adapter, guidance=SIZE_GUIDANCE
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
    # Two independent reasons to leave the current pointer's record alone, and they are
    # different questions: the first asks whether that investigation is FINISHED, the
    # second whether it is MINE. The finished-arm shipped first and answers neither half
    # of the reported defect, because the record it would have destroyed was open.
    current_target_path = str(payload["write_artifact_path"])
    current_target_subject = _scaffold_artifact_lib.record_subject_slug(current_target_path)
    # NOT "is it a mismatch" — "is it confirmed mine". An unreadable target subject (a
    # regular-file `latest.md`, a legacy `debug-<date>-<slug>.md` name) and an undeclared
    # invocation are both states in which nobody established that this record is this
    # author's, and comparing against `mismatch` wrote in place for both.
    subject_facts = _scaffold_artifact_lib.subject_identity_facts(
        invocation_subject_key=subject_key,
        target_subject_key=current_target_subject,
    )
    subject_unconfirmed = _scaffold_artifact_lib.diverts_from_target(
        repo_root, write_path=current_target_path, facts=subject_facts
    )
    if _resolution(current_write_path) == "resolved" or subject_unconfirmed:
        record_payload = _followup_routing.resolved_followup_record_payload(
            repo_root,
            adapter=adapter,
            # The DECLARED subject names the fresh record when there is one: an author who
            # said `--subject X` and was routed off someone else's record should land on a
            # file named for X, not on the generic default title.
            resolved_title=subject or resolved_title,
            artifact_date=artifact_date,
            current_pointer_target_path=payload.get("current_pointer_target_path")
            if isinstance(payload.get("current_pointer_target_path"), str)
            else None,
            # Only when the divert was about SUBJECT. In the finished-investigation arm the
            # whole point is a fresh record, so reusing one by name is the wrong answer even
            # when the name matches.
            reuse_subject_key=subject_key if subject_unconfirmed else None,
            scaffold_artifact_lib=_scaffold_artifact_lib,
            resolve_artifact_path=_resolve_artifact_path,
            resolution=_resolution,
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
        # Only when something was actually declined. `diverts_from_target` is already the
        # at-stake test, so the remaining condition is that the payload moved off that path;
        # the resolved-followup arm reaches this branch for a different reason.
        if subject_unconfirmed and str(payload["write_artifact_path"]) != current_target_path:
            payload.update(
                _scaffold_artifact_lib.subject_refusal_facts(
                    refused_path=current_target_path,
                    refused_subject_key=current_target_subject,
                    reason=str(subject_facts["write_artifact_subject_match"]),
                )
            )
    payload.update(
        {
            "date": date_text,
            "title": resolved_title,
            "artifact_role": "current_pointer",
            "current_pointer_symlink_target": _current_pointer_symlink_target(repo_root, str(payload["artifact_path"])),
            "template": render_template(title=resolved_title, date_text=date_text, evidence_mode=evidence_mode),
        }
    )
    if size_budget is not None:
        payload["size_budget"] = size_budget
    # LAST, because the resolved-followup branch above replaces `write_artifact_path` through
    # a fixed key list. Facts computed before that swap describe the wrong file.
    _scaffold_artifact_lib.with_write_target_facts(repo_root, payload)
    # AFTER the swap, for the same reason and one the records-only sibling already states:
    # the command NAMES the artifact path, so computing it before the path is final points
    # the validator at a file nothing writes. Unscoped this was swap-insensitive by
    # accident -- it named no path at all.
    payload["validator_command"] = validator_command(
        repo_root, str(payload["write_artifact_path"]), evidence_mode=evidence_mode
    )
    payload["evidence_mode"] = evidence_mode
    payload.update(
        _scaffold_artifact_lib.final_subject_facts(
            invocation_subject_key=subject_key,
            target_subject_key=_scaffold_artifact_lib.record_subject_slug(str(payload["write_artifact_path"])),
            chosen=str(payload["write_artifact_path"]) != current_target_path,
        )
    )
    return payload


def main() -> int:
    return _scaffold_lib.emit_payload_main(
        payload_for, artifact_label="debug", supports_evidence_mode=True
    )


if __name__ == "__main__":
    raise SystemExit(main())
