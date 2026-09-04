#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
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
_reviewer_shape = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.review.critique_reviewer_evidence"
)

# The critique validator (scripts/review/validate_critique_artifacts.py) is opt-in but
# enforces real schemas when their sections appear: `## Structured Findings`
# enums/follow-ups, `## Reviewer Tier Evidence` fields/host-exposure-state, and
# (once dated on/after their enforce-from dates) a `Fresh-eye satisfaction:` line
# that must open with a typed value AND a `## Boundary Ownership` `Verdict:` line
# that must open with a typed boundary verdict. The scaffold emits all of these
# so the dogfood validation exercises them, but both the fresh-eye line and the
# boundary `Verdict:` are deliberately NOT typed values by default — those floors
# exist to stop an unedited artifact from silently claiming a review or a
# "no cross-surface concern" happened (a same-observer rubber stamp); a scaffold
# that pre-fills a real typed token would hand every author exactly that loophole
# for free. The fresh-eye line also stays free of the literal "blocked" token
# (which would otherwise demand a host/tool signal).


# Allowed enum values the critique validator enforces, surfaced at author time so
# substituting a value picks from the valid set instead of inventing one that only
# fails at validate-time. These MUST stay equal to the validator's frozensets
# (scripts/review/validate_critique_artifacts.py: STRUCTURED_BINS / STRUCTURED_EVIDENCE /
# STRUCTURED_ACTIONS / REVIEWER_TIER_HOST_STATES); a drift test pins the equality so
# this legend cannot silently diverge from the enforced contract.
ALLOWED_BINS = ("act-before-ship", "bundle-anyway", "over-worry", "valid-but-defer")
ALLOWED_EVIDENCE = ("strong", "moderate", "weak", "contested")
ALLOWED_ACTIONS = ("fix", "file-issue", "document", "defer")
ALLOWED_HOST_EXPOSURE_STATES = (
    "pending-parent-spawn",
    "requested_fields_sent",
    "metadata-hidden",
    "host-defaulted",
    "unsupported",
    "applied",
)
# Delivery-state enum the validator enforces once an artifact is dated on/after
# its enforce-from date. A reviewer that ran cleanly is not a reviewer whose
# findings arrived; the spawn call shape selects the delivery channel, and the
# losing one strands a complete review where the parent cannot read it. MUST
# stay equal to the validator's DELIVERY_STATE_VALUES (drift test pins the
# equality). See the `Result Delivery` section of
# skills/shared/references/fresh-eye-subagent-review.md.
ALLOWED_DELIVERY_STATES = (
    "findings-received",
    "findings-recovered-from-transcript",
    "spawn-accepted-no-delivery",
    "pending-parent-spawn",
)
ALLOWED_EXECUTION_MODES = tuple(_reviewer_shape.REVIEWER_EXECUTION_MODE_VALUES)
DEFAULT_EXECUTION_MODE = _reviewer_shape.DEFAULT_REVIEWER_EXECUTION_MODE
# Boundary-ownership verdict enum the validator's presence floor enforces once an
# artifact is dated on/after its enforce-from date. MUST stay equal to the
# validator's BOUNDARY_VERDICT_VALUES (drift test pins the equality). See
# skills/shared/references/boundary-ownership-brief.md.
ALLOWED_BOUNDARY_VERDICTS = ("single-surface", "owned-correctly", "moved-to-owner", "escalated-to-issue-spec")
# Verification-scope values are validated when the scaffolded section is present.
ALLOWED_FAILURE_CLASSIFICATIONS = ("scope-too-broad", "verifier-defect", "subject-defect", "none")
ALLOWED_RETRY_DISPOSITIONS = ("first-attempt", "retry-new-identity", "stop-no-progress", "non-claim")
VALIDATOR_SCRIPT_NAMES = (
    "validate_critique_artifacts.py",
    "validate-critique-artifacts.py",
)


def allowed_enums() -> dict[str, object]:
    """The validator's allowed enum sets, surfaced for programmatic consumers."""
    return {
        "structured_findings": {
            "bin": list(ALLOWED_BINS),
            "evidence": list(ALLOWED_EVIDENCE),
            "action": list(ALLOWED_ACTIONS),
        },
        "reviewer_tier_host_exposure_state": list(ALLOWED_HOST_EXPOSURE_STATES),
        "reviewer_delivery_state": list(ALLOWED_DELIVERY_STATES),
        "reviewer_execution_mode": list(ALLOWED_EXECUTION_MODES),
        "boundary_ownership": {"verdict": list(ALLOWED_BOUNDARY_VERDICTS)},
        "verification_scope": {
            "failure_classification": list(ALLOWED_FAILURE_CLASSIFICATIONS),
            "retry_disposition": list(ALLOWED_RETRY_DISPOSITIONS),
        },
        "couplings": [
            "action: file-issue requires a parseable follow-up: (issue URL or 'deferred <handoff-anchor>')",
            "Host exposure state: applied requires Application state: host-confirmed: <signal>",
            "Delivery state: spawn-accepted-no-delivery and findings-recovered-from-transcript each require a trailing channel or host signal",
        ],
    }


def default_title(title: str | None) -> str:
    return title if title else "Critique Review"


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "critique"


def render_template(*, title: str, date_text: str, evidence_mode: bool = False) -> str:
    lines = [f"# {title}", f"Date: {date_text}", ""]
    lines.extend(["## Decision Under Review", "", "TODO the change or decision under critique, in one or two lines.", ""])
    lines.extend(
        [
            "## Verification Scope Decision",
            "",
            "- Claim under test: TODO the smallest claim that must be established.",
            "- Changed surfaces: TODO the changed paths and required final consumers.",
            "- Minimum sufficient proof: TODO the cheapest proof that reaches those consumers.",
            "- Deliberately omitted checks: TODO what is omitted and why it is not required here.",
            "- Verifier contract: TODO the gate/validator identity and whether it changed or is suspect.",
            "- Failure classification: TODO scope-too-broad | verifier-defect | subject-defect | none",
            "- Negative control: TODO command | expected refusal | observed result | receipt, or none with rationale.",
            "- Subject identity: TODO sha256:<64 lowercase hex>",
            "- Verifier identity: TODO sha256:<64 lowercase hex>",
            "- Input identity: TODO sha256:<64 lowercase hex>",
            "- Failure identity: TODO stable:<lowercase-slug>",
            "- Evidence identity: TODO sha256:<64 lowercase hex> or none",
            "- Retry disposition: TODO first-attempt | retry-new-identity | stop-no-progress | non-claim",
            "- Retry key: TODO output from verification_retry.py",
            "",
        ]
    )
    lines.extend(["## Failure Angles", "", "- TODO a distinct failure angle and why it could bite.", ""])
    lines.extend(["## Counterweight Pass", "", "- TODO separate the real blockers from over-worry.", ""])
    bins_legend = " | ".join(ALLOWED_BINS)
    evidence_legend = " | ".join(ALLOWED_EVIDENCE)
    actions_legend = " | ".join(ALLOWED_ACTIONS)
    host_states_legend = " | ".join(ALLOWED_HOST_EXPOSURE_STATES)
    delivery_states_legend = " | ".join(ALLOWED_DELIVERY_STATES)
    execution_modes_legend = " | ".join(ALLOWED_EXECUTION_MODES)
    lines.extend(
        [
            "## Structured Findings",
            "",
            "<!-- allowed enums (substitute only these) — "
            f"bin: {bins_legend}; "
            f"evidence: {evidence_legend}; "
            f"action: {actions_legend}. "
            "action: file-issue also needs a follow-up: (issue URL or 'deferred ' "
            "plus a handoff anchor). -->",
            "- F1 | bin: act-before-ship | evidence: moderate | ref: TODO path-or-line"
            " | action: fix | note: TODO the blocker to fix before shipping",
            "- F2 | bin: over-worry | evidence: weak | ref: TODO path-or-line"
            " | action: defer | note: TODO the concern raised but not folded",
            "",
        ]
    )
    lines.extend(
        [
            "## Reviewer Tier Evidence",
            "",
            f"<!-- allowed Host exposure state: {host_states_legend}. Use applied "
            "only with Application state: host-confirmed: plus a concrete signal. -->",
            # Every one of these bullets must be replaced after the reviewer runs,
            # and the validator refuses each unedited default. Say so HERE: the
            # fresh-eye and boundary placeholders below both read "replace with",
            # and this block used to read as a descriptive hint instead — so an
            # author filled the two surfaces marked replace-me, submitted, and was
            # refused on a third they were never told about. That is one
            # guaranteed extra validator round-trip per critique, forever, which
            # is the closeout-authoring-churn class this repo names.
            "<!-- Every bullet below is a placeholder: a value still opening TODO/TBD is "
            "refused, and a pending-parent-spawn Host exposure or Delivery state is refused "
            "alongside a worker-delivered/parent-delegated/nested-delegated Fresh-Eye Satisfaction (it would "
            "claim a completed delegation over a record saying nothing was spawned). Write "
            "n/a when the host genuinely exposes no such control. -->",
            "- Requested tier: TODO replace with the fresh-eye reviewer tier requested (or n/a).",
            "- Requested spawn fields: TODO replace with the fields sent to the host spawn surface (or n/a).",
            "- Host exposure state: pending-parent-spawn",
            "- Application state: TODO replace with the host signal once the reviewer runs (or n/a).",
            f"<!-- allowed Delivery state: {delivery_states_legend}. Boundary "
            "cleanliness is a separate claim and does not imply delivery. -->",
            "- Delivery state: pending-parent-spawn",
            f"<!-- allowed Execution mode: {execution_modes_legend}. This defaults to "
            "the Charness-owned file-backed worker; use typed-subagent only when the "
            "adapter explicitly selects that branch. -->",
            f"- Execution mode: {DEFAULT_EXECUTION_MODE}",
            "<!-- If Fresh-Eye Satisfaction is `worker-delivered`, also record the "
            "durable combined report carrier below. Approval is owned by that report, "
            "not by this artifact's prose. -->",
            "- Worker report: TODO tracked path under charness-artifacts/critique/workers/<attempt>/worker-report.yaml (not .charness/)",
            "- Worker report identity: TODO lowercase SHA-256 of the report carrier",
            "- Worker report approval: TODO approval_eligible: true after report validation",
            "- Worker report delivery: TODO findings-received after parent delivery",
            "- Worker report packet identity: TODO lowercase SHA-256 from the report",
            "- Worker report input identity: TODO lowercase SHA-256 from the report",
            "- Worker report parent receipt identity: TODO non-empty receipt identity from the report",
            "- Worker report findings identity: TODO lowercase SHA-256 of the result",
            "",
        ]
    )
    lines.extend(
        [
            "## Fresh-Eye Satisfaction",
            "",
            # Deliberately NOT a typed value (see the module comment above): the
            # validator requires this line to OPEN with `worker-delivered` /
            # `parent-delegated` / `nested-delegated` / a signal-bearing value / or the explicit
            # a signal-bearing value once dated on/after its enforce-from date,
            # and it also rejects a typed value
            # whose remainder still carries an unedited `todo`. Pre-filling a
            # real typed token here (even with a trailing TODO) would let every
            # unedited scaffold silently claim a review happened; this text
            # cannot satisfy the floor until the author replaces it with a real
            # typed value after the reviewer actually runs. Stays free of the
            # literal "blocked" token for the same reason as the module comment.
            "TODO: replace with `worker-delivered`, `parent-delegated`, `nested-delegated`, "
            "a citation of the concrete host/tool signal after the reviewer runs.",
            "",
        ]
    )
    lines.extend(
        [
            "## Reviewed Input Identity",
            "",
            # The `Packet consumed:` line is what TURNS THIS FLOOR ON, and the
            # scaffold never named it — so an author had no way to learn the
            # trigger from the surface that enforces it, and the floor was
            # silently off for artifacts that did declare a packet another way.
            # Named here, not pre-filled: emitting it unconditionally would demand
            # binding fields from every scaffolded critique, most of which consume
            # no packet.
            "<!-- Packet-bound critiques replace this comment with `- Packet consumed: <packet-path>` "
            "plus three bullets copied from prepare_packet.py after the reviewed packet is final: "
            "Packet path, exact Packet SHA256, and Identity SHA256. That `Packet consumed:` line is "
            "what turns the binding floor on. Leave this section comment-only when no packet was consumed. -->",
            "",
        ]
    )
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
    verdict_legend = " | ".join(ALLOWED_BOUNDARY_VERDICTS)
    lines.extend(
        [
            "## Boundary Ownership",
            "",
            f"<!-- allowed Verdict (substitute only these): {verdict_legend}. Run the "
            "producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->",
            "- Producer: TODO who produces this fact or state.",
            "- Consumer: TODO the final consumer.",
            "- Owning surface: TODO the surface that should own the change (a repo-defined label).",
            # Deliberately NOT a typed verdict (same rationale as the Fresh-Eye
            # Satisfaction placeholder above): the validator requires the
            # `Verdict:` value to OPEN with one of the typed tokens once dated
            # on/after its enforce-from date, and rejects a typed value whose
            # remainder still carries an unedited `todo`. Pre-filling a real
            # verdict here (e.g. `single-surface`) would let every unedited
            # scaffold silently claim "no cross-surface concern" for free — the
            # same rubber stamp the fresh-eye floor stops. The author replaces
            # this with a real verdict after running the brief.
            f"- Verdict: TODO replace with one of {verdict_legend} after running the "
            "producer/consumer brief.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path, write_artifact_path: str, *, evidence_mode: bool = False) -> str:
    return _scaffold_lib.validator_command(
        repo_root=repo_root,
        script_file=__file__,
        script_names=VALIDATOR_SCRIPT_NAMES,
        artifact_path=write_artifact_path,
        evidence_mode=evidence_mode,
    )


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
    # `output_dir: docs/mine-critique` under `version: 9` got back `artifact_path: charness-artifacts/critique/<date>-probe.md`, exit 0, and the scaffold
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
        load_adapter, repo_root, adapter_name="critique-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    output_dir = str(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    # `critique`'s subject is the decision under review, and its one machine-readable channel
    # is the slug. A declared `--subject` NAMES the record: deriving the path from the title
    # while keying on the subject produced two files for one decision.
    return _scaffold_lib.subject_scoped_record_payload(
        repo_root,
        output_dir=output_dir,
        date_text=date_text,
        title=resolved_title,
        record_slug=_slug(subject or resolved_title),
        template=render_template(title=resolved_title, date_text=date_text, evidence_mode=evidence_mode),
        validator_command_for=lambda path: validator_command(repo_root, path, evidence_mode=evidence_mode),
        remedy="Rerun scaffold_critique_artifact.py with --title <specific decision under review>.",
        extra={"allowed_enums": allowed_enums(), "evidence_mode": evidence_mode},
    )


def main() -> int:
    return _scaffold_lib.emit_payload_main(
        payload_for, artifact_label="critique", supports_evidence_mode=True
    )


if __name__ == "__main__":
    raise SystemExit(main())
