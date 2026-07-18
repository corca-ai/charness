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

Silent when no workflow files match the glob (e.g., a repo with no
`.github/workflows/`). Local gate fatter than CI is correct (no parity
issue surfaces); the helper is asymmetric on purpose.
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
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_lib"
)
load_yaml_file = _adapter_lib.load_yaml_file

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_local_gate_parity_lib as plib  # noqa: E402
from summary_output_lib import add_output_args, emit_selected  # noqa: E402


def _print_text_summary(rendered: dict[str, Any]) -> None:
    print(
        f"CI/local gate parity inventory: {rendered['workflows_scanned']} "
        f"workflow(s) scanned; "
        f"{len(rendered['parity_issues'])} parity-issue step(s); "
        f"{len(rendered['jobs_without_canonical_gate'])} workflow(s) "
        f"with no canonical gate match."
    )
    for issue in rendered["parity_issues"]:
        run_text = issue.get("run") or issue.get("uses") or "<unknown>"
        suffix = f" (named {issue['name']!r})" if issue.get("name") else ""
        print(
            f"  parity-issue {issue['workflow']}::{issue['job']}: {run_text!r}"
            f"{suffix}"
        )
    for advisory in rendered["jobs_without_canonical_gate"]:
        jobs = ", ".join(advisory["jobs"])
        print(
            f"  no-canonical-gate {advisory['workflow']}: jobs [{jobs}] — "
            "pass --canonical-gate-pattern to anchor on this repo's gate."
        )
    for entry in rendered.get("exempt_workflows") or []:
        print(
            f"  exempt {entry['workflow']}: gate-policy={entry['gate_policy']}"
        )
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
        "workflows_scanned": rendered.get("workflows_scanned", 0),
        "parity_issue_count": len(parity_issues) if isinstance(parity_issues, list) else 0,
        "jobs_without_canonical_gate_count": len(missing) if isinstance(missing, list) else 0,
        "exempt_workflow_count": len(exempt) if isinstance(exempt, list) else 0,
        "parity_issues_sample": parity_issues[:sample_limit] if isinstance(parity_issues, list) else [],
        "jobs_without_canonical_gate_sample": missing[:sample_limit] if isinstance(missing, list) else [],
        "exempt_workflows_sample": exempt[:sample_limit] if isinstance(exempt, list) else [],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root for the CI/local gate parity inventory")
    parser.add_argument(
        "--workflow-glob",
        default=plib.DEFAULT_WORKFLOW_GLOB,
        help=f"glob for CI workflow files (default: {plib.DEFAULT_WORKFLOW_GLOB})",
    )
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
    parser.add_argument("--require-git-file-listing", action="store_true", help="Fail when git ls-files is unavailable for workflow discovery")
    add_output_args(
        parser,
        summary_help="Emit compact YAML parity counts and bounded triage samples",
        detail_help="Emit the full CI/local gate parity inventory as YAML",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    root = args.repo_root.resolve()
    workflow_files = plib.iter_workflow_files(
        root,
        args.workflow_glob,
        require_git=args.require_git_file_listing,
    )
    raw_patterns = tuple(args.canonical_gate_pattern or plib.DEFAULT_CANONICAL_GATE_PATTERNS)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
