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
_scaffold_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.scaffold_artifact_lib")

# The critique validator (scripts/validate_critique_artifacts.py) is opt-in but
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
# (scripts/validate_critique_artifacts.py: STRUCTURED_BINS / STRUCTURED_EVIDENCE /
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
# Boundary-ownership verdict enum the validator's presence floor enforces once an
# artifact is dated on/after its enforce-from date. MUST stay equal to the
# validator's BOUNDARY_VERDICT_VALUES (drift test pins the equality). See
# skills/shared/references/boundary-ownership-brief.md.
ALLOWED_BOUNDARY_VERDICTS = ("single-surface", "owned-correctly", "moved-to-owner", "escalated-to-issue-spec")
VALIDATOR_SCRIPT_NAMES = ("validate_critique_artifacts.py", "validate-critique-artifacts.py")


def allowed_enums() -> dict[str, object]:
    """The validator's allowed enum sets, surfaced for programmatic consumers."""
    return {
        "structured_findings": {
            "bin": list(ALLOWED_BINS),
            "evidence": list(ALLOWED_EVIDENCE),
            "action": list(ALLOWED_ACTIONS),
        },
        "reviewer_tier_host_exposure_state": list(ALLOWED_HOST_EXPOSURE_STATES),
        "boundary_ownership": {"verdict": list(ALLOWED_BOUNDARY_VERDICTS)},
        "couplings": [
            "action: file-issue requires a parseable follow-up: (issue URL or 'deferred <handoff-anchor>')",
            "Host exposure state: applied requires Application state: host-confirmed: <signal>",
        ],
    }


def default_title(title: str | None) -> str:
    return title if title else "Critique Review"


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "critique"


def render_template(*, title: str, date_text: str) -> str:
    lines = [f"# {title}", f"Date: {date_text}", ""]
    lines.extend(["## Decision Under Review", "", "TODO the change or decision under critique, in one or two lines.", ""])
    lines.extend(["## Failure Angles", "", "- TODO a distinct failure angle and why it could bite.", ""])
    lines.extend(["## Counterweight Pass", "", "- TODO separate the real blockers from over-worry.", ""])
    bins_legend = " | ".join(ALLOWED_BINS)
    evidence_legend = " | ".join(ALLOWED_EVIDENCE)
    actions_legend = " | ".join(ALLOWED_ACTIONS)
    host_states_legend = " | ".join(ALLOWED_HOST_EXPOSURE_STATES)
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
            "- Requested tier: TODO the fresh-eye reviewer tier requested.",
            "- Requested spawn fields: TODO the fields sent to the host spawn surface.",
            "- Host exposure state: pending-parent-spawn",
            "- Application state: TODO the host signal once the reviewer runs.",
            "",
        ]
    )
    lines.extend(
        [
            "## Fresh-Eye Satisfaction",
            "",
            # Deliberately NOT a typed value (see the module comment above): the
            # validator requires this line to OPEN with `parent-delegated` /
            # `nested-delegated` / a signal-bearing typed value once dated
            # on/after its enforce-from date, and it also rejects a typed value
            # whose remainder still carries an unedited `todo`. Pre-filling a
            # real typed token here (even with a trailing TODO) would let every
            # unedited scaffold silently claim a review happened; this text
            # cannot satisfy the floor until the author replaces it with a real
            # typed value after the reviewer actually runs. Stays free of the
            # literal "blocked" token for the same reason as the module comment.
            "TODO: replace with `parent-delegated`, `nested-delegated`, or a citation of "
            "the concrete signal that stopped delegation — after the reviewer actually runs.",
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


def validator_command(repo_root: Path, write_artifact_path: str) -> str:
    return _scaffold_lib.validator_command(
        repo_root=repo_root,
        script_file=__file__,
        script_names=VALIDATOR_SCRIPT_NAMES,
        artifact_path=write_artifact_path,
    )


def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    output_dir = str(adapter["data"]["output_dir"])
    date_text = dt.date.today().isoformat()
    resolved_title = default_title(title)
    write_artifact_path = f"{output_dir}/{date_text}-{_slug(resolved_title)}.md"
    return {
        "artifact_path": write_artifact_path,
        "artifact_role": "record",
        "write_artifact_path": write_artifact_path,
        "date": date_text,
        "title": resolved_title,
        "template": render_template(title=resolved_title, date_text=date_text),
        "validator_command": validator_command(repo_root, write_artifact_path),
        "allowed_enums": allowed_enums(),
    }


def main() -> int:
    return _scaffold_lib.emit_payload_main(payload_for, artifact_label="critique")


if __name__ == "__main__":
    raise SystemExit(main())
