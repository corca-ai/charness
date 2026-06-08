#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import runpy
import sys
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

# The critique validator (scripts/validate_critique_artifacts.py) is opt-in but
# enforces real schemas when their sections appear: `## Structured Findings`
# enums/follow-ups, `## Reviewer Tier Evidence` fields/host-exposure-state, and a
# fresh-eye satisfaction status that must cite a signal when it is blocked. The
# scaffold emits all three so the dogfood validation exercises them, with the
# fresh-eye line deliberately free of the literal "blocked" token (which would
# otherwise demand a host/tool signal).


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


def allowed_enums() -> dict[str, object]:
    """The validator's allowed enum sets, surfaced for programmatic consumers."""
    return {
        "structured_findings": {
            "bin": list(ALLOWED_BINS),
            "evidence": list(ALLOWED_EVIDENCE),
            "action": list(ALLOWED_ACTIONS),
        },
        "reviewer_tier_host_exposure_state": list(ALLOWED_HOST_EXPOSURE_STATES),
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
            "TODO record the reviewer verdict and the concrete signal behind it.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def validator_command(repo_root: Path, write_artifact_path: str) -> str:
    # Prefer the repo-local validator when the working repo owns one so the cited
    # check == the broad gate; fall back to the installed-plugin copy only for a
    # consumer repo that ships no validator of its own. Repo-local-first kills the
    # installed-vs-repo version-skew class (an installed validator looser than the
    # repo's must not shadow it).
    for script_name in ("validate_critique_artifacts.py", "validate-critique-artifacts.py"):
        repo_local = repo_root / "scripts" / script_name
        if repo_local.is_file():
            return f"python3 scripts/{script_name} --repo-root . --paths {write_artifact_path}"
    for ancestor in Path(__file__).resolve().parents:
        for script_name in ("validate_critique_artifacts.py", "validate-critique-artifacts.py"):
            candidate = ancestor / "scripts" / script_name
            if candidate.is_file():
                return f"python3 {candidate} --repo-root . --paths {write_artifact_path}"
    raise FileNotFoundError("validate_critique_artifacts.py not found in installed Charness layout")


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to scaffold the critique artifact into")
    parser.add_argument("--title", help="Title for the scaffolded critique artifact")
    parser.add_argument("--json", action="store_true", help="Emit the payload as JSON instead of the rendered template")
    args = parser.parse_args()

    payload = payload_for(args.repo_root.resolve(), title=args.title)
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(payload["template"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
