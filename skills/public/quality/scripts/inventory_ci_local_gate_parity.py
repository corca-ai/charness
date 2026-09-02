#!/usr/bin/env python3

"""Inventory parity between a canonical local gate and CI workflow steps.

Reports `run:` steps that follow the canonical local gate inside the same
GitHub Actions job. A non-empty `parity_issues` set means CI enforces
required quality gates that the local/pre-push gate does not run, which is
the CI/local parity failure mode.

Classification per subsequent step:

- `ci-only-violation` — step run line, name, or its preceding YAML
  comment contains the forbidden CI-only marker (default `CI-only`,
  case-insensitive).
- `setup`       — step uses common provisioning shapes
  (actions/checkout, actions/setup-*, actions/cache,
  actions/upload-artifact, actions/download-artifact, npm ci,
  pip install, etc.).
- `parity-issue` — anything else: the most likely "required gate appended
  outside the local gate graph" shape from the issue body.

Scope rules, because a denominator that reached zero used to read as a pass:
the DISCOVERED default globs (`.github/workflows/*.yml` and `*.yaml` — Actions
accepts both) matching nothing stays a clean exit that SAYS it evaluated
nothing; a `--workflow-glob` the caller NAMED that matches nothing is a refusal
with a payload. A job whose canonical-gate match cannot be established — every
step a `uses:`, or the job itself a reusable-workflow call — is neither a pass
nor a violation and has its own bucket plus its own opt-in refusal flag.

Local gate fatter than CI is correct (no parity issue surfaces); the helper is
asymmetric on purpose.
"""

from __future__ import annotations

import argparse
import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
_quality_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.quality_adapter_lib"
)
_quality_universes = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.quality_universes_lib"
)
load_yaml_file = _adapter_lib.load_yaml_file

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_local_gate_parity_lib as plib  # noqa: E402
from git_inventory_lib import capture_visible_repo_files  # noqa: E402
from summary_output_lib import add_output_args, emit_selected  # noqa: E402


def _print_text_summary(rendered: dict[str, Any]) -> None:
    print(
        f"CI/local gate parity inventory: {rendered['workflows_scanned']} "
        f"workflow(s) scanned, {rendered.get('workflows_not_exempt', 0)} not exempt "
        f"({rendered.get('jobs_evaluated', 0)} job(s)); "
        f"{len(rendered['parity_issues'])} parity-issue step(s); "
        f"{len(rendered['jobs_without_canonical_gate'])} workflow(s) "
        f"with no canonical gate match."
    )
    if not rendered.get("jobs_evaluated"):
        # Without this line a fully exempt or fully unreadable scope printed the
        # same sentence as a repo whose every job was checked and passed.
        print(
            "  NOTE: zero jobs were evaluated, so this run establishes NOTHING about "
            "CI/local parity. A green here is the absence of a measurement, not a "
            "passing one. Pass --require-evaluated-scope to make that a refusal."
        )
    for issue in rendered["parity_issues"]:
        run_text = issue.get("run") or issue.get("uses") or "<unknown>"
        suffix = f" (named {issue['name']!r})" if issue.get("name") else ""
        print(f"  parity-issue {issue['workflow']}::{issue['job']}: {run_text!r}{suffix}")
    for advisory in rendered["jobs_without_canonical_gate"]:
        jobs = ", ".join(advisory["jobs"])
        print(
            f"  no-canonical-gate {advisory['workflow']}: jobs [{jobs}] — "
            "pass --canonical-gate-pattern to anchor on this repo's gate."
        )
    for advisory in rendered.get("jobs_gate_match_unestablished") or []:
        jobs = ", ".join(advisory["jobs"])
        print(
            f"  gate-match-unestablished {advisory['workflow']}: jobs [{jobs}] have no "
            "`run:` step this reader can see (every step is a `uses:`, or the job "
            "itself is a reusable-workflow call), so the canonical gate may run "
            "inside something it cannot open. Not a pass and not a violation."
        )
    for entry in rendered.get("exempt_workflows") or []:
        print(f"  exempt {entry['workflow']}: gate-policy={entry['gate_policy']}")
    if rendered["parity_issues"]:
        print(
            "  resolve each parity-issue by adding the step to the canonical "
            "local/pre-push gate, moving it to an explicit local release or "
            "update gate, or removing the CI-only split. CI-only quality gates "
            "are not an acceptable waiver. See "
            "skills/public/quality/references/maintainer-local-enforcement.md."
        )


def summarize(rendered: dict[str, Any], *, sample_limit: int = 10) -> dict[str, Any]:
    """Return bounded triage data without hiding the aggregate parity state."""
    parity_issues = rendered.get("parity_issues", [])
    missing = rendered.get("jobs_without_canonical_gate", [])
    exempt = rendered.get("exempt_workflows", [])
    return {
        "summary_note": "summary is triage output; use --detail for full workflow and step evidence",
        "status": rendered.get("status"),
        "workflows_scanned": rendered.get("workflows_scanned", 0),
        "workflows_not_exempt": rendered.get("workflows_not_exempt", 0),
        "jobs_evaluated": rendered.get("jobs_evaluated", 0),
        # JOB counts, not workflow counts: round 2 caught both of these summing
        # per-workflow entries under a `jobs_*` name, so a workflow with seven
        # unreadable jobs summarized as 1 — the denominator defect one register down.
        "jobs_gate_match_unestablished_count": sum(
            len(entry.get("jobs") or [])
            for entry in rendered.get("jobs_gate_match_unestablished") or []
        ),
        "parity_issue_count": len(parity_issues) if isinstance(parity_issues, list) else 0,
        "jobs_without_canonical_gate_count": (
            sum(len(entry.get("jobs") or []) for entry in missing)
            if isinstance(missing, list)
            else 0
        ),
        "workflows_without_canonical_gate_count": len(missing) if isinstance(missing, list) else 0,
        "exempt_workflow_count": len(exempt) if isinstance(exempt, list) else 0,
        "parity_issues_sample": parity_issues[:sample_limit]
        if isinstance(parity_issues, list)
        else [],
        "jobs_without_canonical_gate_sample": missing[:sample_limit]
        if isinstance(missing, list)
        else [],
        "exempt_workflows_sample": exempt[:sample_limit] if isinstance(exempt, list) else [],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root for the CI/local gate parity inventory",
    )
    plib.add_workflow_glob_arg(parser)
    parser.add_argument(
        "--canonical-gate-pattern",
        action="append",
        default=None,
        help="regex matching the canonical local gate `run:` line (repeatable)",
    )
    parser.add_argument(
        "--ci-only-marker",
        default=plib.DEFAULT_CI_ONLY_MARKER,
        help=f"case-insensitive marker (default: {plib.DEFAULT_CI_ONLY_MARKER!r})",
    )
    parser.add_argument(
        "--require-empty-parity-issues",
        action="store_true",
        help="exit 1 when any subsequent step is classified as parity-issue",
    )
    parser.add_argument(
        "--require-canonical-gate-match",
        action="store_true",
        help="exit 1 when a workflow has run-steps but no canonical-gate match",
    )
    parser.add_argument(
        "--require-established-gate-match",
        action="store_true",
        help=(
            "exit 1 when a job's canonical-gate match could not be ESTABLISHED at all "
            "(every step is a `uses:`, or the job is a reusable-workflow call). Separate "
            "from --require-canonical-gate-match because a composite-action wrapper is an "
            "honest CI shape, and the only escapes from a folded-in refusal would be "
            "dropping the real teeth or misusing a gate-policy marker"
        ),
    )
    parser.add_argument(
        "--require-evaluated-scope",
        action="store_true",
        help=(
            "exit 1 when zero jobs were evaluated (every workflow exempt, unreadable, or "
            "absent), so a green cannot be cited as CI/local parity proof"
        ),
    )
    parser.add_argument(
        "--require-git-file-listing",
        action="store_true",
        help="Fail when git ls-files is unavailable for workflow discovery",
    )
    add_output_args(
        parser,
        summary_help="Emit compact YAML parity counts and bounded triage samples",
        detail_help="Emit the full CI/local gate parity inventory as YAML",
    )
    return parser


def _resolve_gate_universe(root: Path, args):
    if args.canonical_gate_pattern:
        return _quality_universes.Universe(tuple(args.canonical_gate_pattern), True, "adapter")
    adapter = _quality_adapter_lib.load_quality_adapter(root)
    return _quality_universes.resolve_universe(
        adapter,
        "ci_gate_patterns",
        default=_quality_universes.DEFAULT_UNIVERSES["ci_gate_patterns"],
    )


def _identity_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return payload


def _refuse_empty_gate_universe(args, universe) -> bool:
    if universe.patterns:
        return False
    reason = _quality_universes.refuse_if_declared_and_empty(
        universe, [], "inventory-ci-local-gate-parity"
    )
    if not reason:
        return False
    refusal = {
        "status": "declared-universe-empty",
        "ci_gate_patterns": [],
        "reason": reason,
    }
    if not emit_selected(refusal, args, summarize=_identity_summary):
        print(f"CI/local gate parity inventory: {reason}", file=sys.stderr)
    return True


def main() -> int:
    args = _build_parser().parse_args()
    root = args.repo_root.resolve()
    try:
        snapshot = capture_visible_repo_files(
            root,
            require_git=args.require_git_file_listing,
            context="CI/local gate parity workflow listing",
        )
    except plib.GitFileListingError as error:
        raise plib.WorkflowListingError(str(error)) from error
    named_globs = args.workflow_glob
    globs = plib.resolve_workflow_globs(named_globs)
    workflow_files = plib.iter_workflow_files(
        root,
        globs,
        require_git=args.require_git_file_listing,
        snapshot=snapshot,
    )
    if named_globs and not workflow_files:
        # The caller named this scope; resolving to nothing is a failed assertion,
        # not an empty repo. The DISCOVERED default matching nothing stays a pass
        # (`test_empty_scope_refusals.py`'s rule), and says so in the text summary.
        # The refusal carries a PAYLOAD as well as a nonzero exit: round 1 caught
        # the first cut writing only to stderr, which left a `--json` consumer
        # unable to tell "refused" from "crashed".
        refusal = {
            "status": "named-scope-empty",
            "named_workflow_globs": list(globs),
            "workflows_scanned": 0,
            "workflows_not_exempt": 0,
            "jobs_evaluated": 0,
            "workflows": [],
            "parity_issues": [],
            "jobs_without_canonical_gate": [],
            "jobs_gate_match_unestablished": [],
            "exempt_workflows": [],
            "reason": (
                f"named --workflow-glob {', '.join(globs)} matched no workflow file under "
                f"{root}; refusing rather than reporting parity over an empty scope. Remedy: "
                "correct the glob, or drop --workflow-glob to use the discovered default."
            ),
        }

        def _summarize_refusal(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
            # Summary mode has its own key set; handing it the raw refusal made a
            # consumer keyed on `parity_issue_count` raise, which is the very
            # "cannot tell refused from crashed" failure this payload exists to fix.
            summarized = summarize(payload)
            summarized["status"] = payload["status"]
            summarized["reason"] = payload["reason"]
            summarized["named_workflow_globs"] = payload["named_workflow_globs"]
            return summarized

        if not emit_selected(refusal, args, summarize=_summarize_refusal):
            print(f"CI/local gate parity inventory: {refusal['reason']}", file=sys.stderr)
        return 1
    gate_universe = _resolve_gate_universe(root, args)
    raw_patterns = gate_universe.patterns
    if _refuse_empty_gate_universe(args, gate_universe):
        return 1
    gate_patterns: tuple[re.Pattern[str], ...] = tuple(re.compile(p) for p in raw_patterns)
    report: list[dict[str, Any]] = []
    for path in workflow_files:
        workflow = plib.parse_workflow(path, load_yaml_file)
        report.append(plib.evaluate_workflow(path, workflow, gate_patterns, args.ci_only_marker))
    rendered = plib.render_report(report)
    if not emit_selected(rendered, args, summarize=summarize):
        _print_text_summary(rendered)
    if args.require_empty_parity_issues and rendered["parity_issues"]:
        return 1
    if args.require_canonical_gate_match and rendered["jobs_without_canonical_gate"]:
        return 1
    if gate_universe.declared and rendered["jobs_without_canonical_gate"]:
        return 1
    if args.require_established_gate_match and rendered.get("jobs_gate_match_unestablished"):
        return 1
    if args.require_evaluated_scope and not rendered.get("jobs_evaluated"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
