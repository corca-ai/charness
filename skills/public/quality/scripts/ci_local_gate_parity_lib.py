"""Library helpers for inventory_ci_local_gate_parity.py."""

from __future__ import annotations

import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_inventory_lib import (  # noqa: E402
    GitFileListingError,
    VisibleRepoFilesSnapshot,
    visible_repo_files,
)

# GitHub Actions accepts BOTH extensions, and the gate saw only one: the same
# workflow saved as `ci.yaml` scanned 0 files and exited 0 where `ci.yml` raised a
# parity issue and exited 1 (S30, reproduced 2026-08-01 with that exact pair). A
# single glob cannot express the alternation portably across `Path.glob`, so the
# scope is a TUPLE and `--workflow-glob` stays repeatable for callers who narrow it.
DEFAULT_WORKFLOW_GLOBS = (".github/workflows/*.yml", ".github/workflows/*.yaml")
#: Back-compat for out-of-repo callers that read the single-glob name. It is ONE
#: entry, not the scope: a caller defaulting to it re-creates the S30 blind spot,
#: which is exactly what round 1 found `inventory_ci_recoverable_gates.py` doing.
#: No in-repo caller reads it now; kept only so an external import does not break.
DEFAULT_WORKFLOW_GLOB = DEFAULT_WORKFLOW_GLOBS[0]
_SHELL_COMMAND_PREFIX = (
    r"(?m)(?:^|(?:&&|\|\||[;|])\s*)\s*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=(?:\"[^\"]*\"|'[^']*'|\S+)\s+)*"
)
DEFAULT_CANONICAL_GATE_PATTERNS = (
    r"\bnpm\s+run\s+verify\b",
    r"\bnpm\s+run\s+lint\s*&&\s*npm\s+run\s+test\b",
    r"\bmake\s+verify\b",
    _SHELL_COMMAND_PREFIX + r"bash\s+(?:\./)?scripts/run-quality\.sh(?=$|\s|[;&|])",
    _SHELL_COMMAND_PREFIX + r"\./scripts/run-quality\.sh(?=$|\s|[;&|])",
    r"\bbash\s+scripts/run-verify\.(?:mjs|sh)\b",
    r"\bnode\s+scripts/run-verify\.mjs\b",
)
DEFAULT_CI_ONLY_MARKER = "CI-only"
GATE_POLICY_MARKER_PREFIX = "# charness:gate-policy "
SCHEDULED_DEEPER_CHECK_POLICY = "scheduled-deeper-check"
LOCAL_GATE_SUBSET_MIRROR_POLICY = "local-gate-subset-mirror"
KNOWN_GATE_POLICIES = frozenset({SCHEDULED_DEEPER_CHECK_POLICY, LOCAL_GATE_SUBSET_MIRROR_POLICY})
SETUP_SHAPES = tuple(
    re.compile(p)
    for p in (
        r"^actions/checkout(@|$)",
        r"^actions/setup-",
        r"^actions/cache(@|/|$)",
        r"^actions/upload-artifact(@|$)",
        r"^actions/download-artifact(@|$)",
        r"^denoland/setup-deno(@|$)",
        r"^astral-sh/setup-uv(@|$)",
    )
)
SETUP_RUN_PATTERNS = tuple(
    re.compile(p)
    for p in (
        r"\bnpm\s+(?:ci|install)\b",
        r"\byarn\s+install\b",
        r"\bpnpm\s+(?:install|i)\b",
        r"\bpip\s+install\b",
        r"\buv\s+sync\b",
        r"\bapt(?:-get)?\s+install\b",
        r"\bbrew\s+install\b",
        r"\bgo\s+mod\s+download\b",
        r"\bcargo\s+fetch\b",
    )
)
_STEP_KEY_PREFIXES = (
    "run", "uses", "name", "id", "env", "with", "if", "shell",
    "timeout-minutes", "continue-on-error", "working-directory",
)


class WorkflowListingError(SystemExit):
    pass


def iter_workflow_files(
    repo_root: Path,
    glob_pattern: str | Sequence[str],
    *,
    require_git: bool = False,
    snapshot: VisibleRepoFilesSnapshot | None = None,
) -> list[Path]:
    """Workflow files under one glob or several, de-duplicated and ordered.

    Accepts a bare string so existing callers keep working; the default scope is
    now several globs because GitHub Actions accepts both `.yml` and `.yaml` and
    reading only one silently emptied the denominator (S30).
    """
    patterns = [glob_pattern] if isinstance(glob_pattern, str) else list(glob_pattern)
    # `visible_repo_files` owns "which files does git list" for this skill package.
    # This module used to hand-roll the same subprocess block; restructuring it for
    # the multi-glob scope made that a NEW duplicate family, which is the dup
    # ratchet doing its job — the fix is to adopt the owner, not to re-baseline.
    try:
        visible = visible_repo_files(
            repo_root,
            require_git=require_git,
            context="CI/local gate parity workflow listing",
            snapshot=snapshot,
        )
    except GitFileListingError as error:
        # Re-raised as this module's SystemExit subclass so the CLI still fails
        # closed with a clean exit rather than a traceback.
        raise WorkflowListingError(str(error)) from error
    candidates = {p for pattern in patterns for p in repo_root.glob(pattern) if p.is_file()}
    if visible is None:
        return sorted(candidates)
    return sorted(candidates & visible)


def add_workflow_glob_arg(parser: Any) -> None:
    """The repeatable `--workflow-glob` option, declared once for both CLIs.

    Both parity entrypoints grew the identical block when the default scope became
    a tuple; one owner keeps the next extension from landing in only one of them.
    """
    parser.add_argument(
        "--workflow-glob",
        action="append",
        default=None,
        help=(
            "glob for CI workflow files, repeatable (default: "
            f"{', '.join(DEFAULT_WORKFLOW_GLOBS)}). A glob NAMED here that matches "
            "nothing is a refusal where the caller asserted a scope; the discovered "
            "default matching nothing stays a pass."
        ),
    )


def resolve_workflow_globs(named: list[str] | None) -> tuple[str, ...]:
    """Caller-named globs, else the discovered default scope."""
    return tuple(named) if named else DEFAULT_WORKFLOW_GLOBS


def classify_step(step: dict[str, Any]) -> str:
    raw_run = step.get("run")
    raw_uses = step.get("uses")
    if isinstance(raw_uses, str):
        for pattern in SETUP_SHAPES:
            if pattern.search(raw_uses):
                return "setup"
    if isinstance(raw_run, str):
        if any(pattern.search(raw_run) for pattern in SETUP_RUN_PATTERNS):
            return "setup"
    return "parity-issue"


def step_text_for_marker(step: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("name", "run", "if"):
        value = step.get(key)
        if isinstance(value, str):
            parts.append(value)
    comment = step.get("__leading_comment")
    if isinstance(comment, str):
        parts.append(comment)
    return "\n".join(parts)


def _find_step_starts(lines: list[str]) -> list[int]:
    starts: list[int] = []
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped.startswith("- "):
            continue
        rest = stripped[2:].lstrip()
        if any(rest.startswith(prefix + ":") for prefix in _STEP_KEY_PREFIXES):
            starts.append(idx)
    return starts


def steps_with_leading_comments(raw_text: str, parsed_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach `__leading_comment` to each step using a lexical pass."""
    if not parsed_steps:
        return []
    lines = raw_text.splitlines()
    step_starts = _find_step_starts(lines)
    if len(step_starts) != len(parsed_steps):
        # Lexical/parsed views disagree — refuse to guess; fall back to
        # name/run/if text only for marker exemption.
        return [dict(step) for step in parsed_steps]
    enriched: list[dict[str, Any]] = []
    for step, start_idx in zip(parsed_steps, step_starts):
        comment_lines: list[str] = []
        cursor = start_idx - 1
        while cursor >= 0 and lines[cursor].strip().startswith("#"):
            comment_lines.insert(0, lines[cursor].strip().lstrip("#").strip())
            cursor -= 1
        if comment_lines:
            step = {**step, "__leading_comment": "\n".join(comment_lines)}
        enriched.append(step)
    return enriched


def parse_workflow(path: Path, yaml_loader: Callable[[Path], Any]) -> dict[str, Any]:
    raw_text = path.read_text(encoding="utf-8")
    payload = yaml_loader(path) or {}
    return {"text": raw_text, "data": payload}


def find_canonical_gate_index(
    steps: list[dict[str, Any]], gate_patterns: tuple[re.Pattern[str], ...]
) -> int | None:
    """Return the LAST step index that invokes the canonical local gate."""
    last_match: int | None = None
    for idx, step in enumerate(steps):
        run_value = step.get("run")
        if not isinstance(run_value, str):
            continue
        if any(pattern.search(run_value) for pattern in gate_patterns):
            last_match = idx
    return last_match


def _classify_subsequent(step: dict[str, Any], marker_re: re.Pattern[str]) -> str:
    if marker_re.search(step_text_for_marker(step)):
        return "ci-only-violation"
    return classify_step(step)


def read_gate_policy(raw_text: str, workflow_label: str | None = None) -> str | None:
    """Return the declared gate-policy keyword from the top of a workflow file.

    Recognized marker: a top-of-file YAML comment of the exact form
    `# charness:gate-policy <policy>` placed before any non-comment content.
    Returns the policy keyword (e.g. `scheduled-deeper-check`) or `None` if
    no marker is present, an unknown keyword is declared, or the marker
    appears after real YAML content begins. Emits a stderr warning when the
    marker prefix is present but the keyword is unrecognized so a typo
    fails loud instead of silently falling back to standard parity
    enforcement. `workflow_label` (typically the path) is interpolated into
    the warning when supplied.
    """
    import sys
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(GATE_POLICY_MARKER_PREFIX):
            keyword = stripped[len(GATE_POLICY_MARKER_PREFIX):].strip()
            if keyword in KNOWN_GATE_POLICIES:
                return keyword
            label = workflow_label or "<workflow>"
            sys.stderr.write(
                f"warning: {label} declares unknown gate-policy "
                f"{keyword!r}; falling back to standard parity enforcement. "
                f"Known policies: {sorted(KNOWN_GATE_POLICIES)}.\n"
            )
            return None
        if not stripped.startswith("#"):
            return None
    return None


def evaluate_workflow(
    path: Path,
    workflow: dict[str, Any],
    gate_patterns: tuple[re.Pattern[str], ...],
    ci_only_marker: str,
) -> dict[str, Any]:
    raw_text = workflow["text"]
    gate_policy = read_gate_policy(raw_text, workflow_label=str(path))
    # Every KNOWN policy keyword names an exempt category: scheduled
    # deeper-checks (periodic analyses, not per-commit gates) and
    # local-gate-subset mirrors (every quality step verbatim re-runs a
    # validator the canonical local gate already enforces, so CI cannot be
    # the first place a required failure appears). Unknown keywords already
    # warned in read_gate_policy and fall through to standard enforcement.
    if gate_policy in KNOWN_GATE_POLICIES:
        return {
            "workflow": str(path),
            "gate_policy": gate_policy,
            "exempt": True,
            "jobs": [],
            "jobs_without_canonical_gate": [],
            # Present-but-empty, not absent: `payload["workflows"]` must not carry
            # two schemas, and in this repo EVERY workflow takes this branch.
            "jobs_gate_match_unestablished": [],
        }
    findings: dict[str, Any] = {
        "workflow": str(path),
        "jobs": [],
        "jobs_without_canonical_gate": [],
        # Jobs whose canonical-gate match this reader CANNOT ESTABLISH, in either
        # composite shape: every step is a `uses:`, or the job itself is a
        # `jobs.<id>.uses:` reusable-workflow call with no `steps` key at all. The
        # gate may well run inside; this reader cannot open either one. Both used
        # to `continue` silently, so such a job was indistinguishable from a job
        # that passed (S26). Round 1 caught the job-level shape still escaping the
        # first cut of this repair — and caught the comment that had declared the
        # escape correct.
        "jobs_gate_match_unestablished": [],
    }
    data = workflow["data"]
    if not isinstance(data, dict):
        return findings
    jobs_block = data.get("jobs") or {}
    if not isinstance(jobs_block, dict):
        return findings
    marker_re = re.compile(re.escape(ci_only_marker), re.IGNORECASE)
    for job_id, job in jobs_block.items():
        if not isinstance(job, dict):
            # A truthy non-mapping job is unreadable, not absent.
            if job:
                findings["jobs_gate_match_unestablished"].append(job_id)
            continue
        steps_raw = job.get("steps") or []
        if not isinstance(steps_raw, list):
            # A `steps:` key this reader could not parse (e.g. a YAML flow sequence,
            # which the repo's hand-rolled loader returns as a string) is exactly
            # "could not establish", not "nothing here" — round 2 caught it still
            # landing in no bucket at all.
            findings["jobs_gate_match_unestablished"].append(job_id)
            continue
        steps = [step for step in steps_raw if isinstance(step, dict)]
        if steps_raw and not steps:
            # Steps were declared but none of them is a readable mapping.
            findings["jobs_gate_match_unestablished"].append(job_id)
            continue
        if not steps:
            # A job with no steps but a job-level `uses:` is a reusable-workflow
            # call — it runs an entire workflow this reader cannot open, which is
            # how repos factor a whole gate graph. Silently skipping it was the
            # same defect as S26 in its more common shape. A job with neither
            # steps nor `uses:` genuinely runs nothing and stays a plain skip.
            if isinstance(job.get("uses"), str):
                findings["jobs_gate_match_unestablished"].append(job_id)
            continue
        if all(not isinstance(step.get("run"), str) for step in steps):
            findings["jobs_gate_match_unestablished"].append(job_id)
            continue
        steps = steps_with_leading_comments(workflow["text"], steps)
        gate_index = find_canonical_gate_index(steps, gate_patterns)
        if gate_index is None:
            findings["jobs_without_canonical_gate"].append(job_id)
            continue
        subsequent = [
            {
                "name": step.get("name"),
                "run": step.get("run"),
                "uses": step.get("uses"),
                "if": step.get("if"),
                "classification": _classify_subsequent(step, marker_re),
            }
            for step in steps[gate_index + 1:]
        ]
        findings["jobs"].append({
            "job_id": job_id,
            "canonical_gate_step": {
                "name": steps[gate_index].get("name"),
                "run": steps[gate_index].get("run"),
            },
            "subsequent": subsequent,
        })
    return findings


def render_report(report: list[dict[str, Any]]) -> dict[str, Any]:
    parity_issues: list[dict[str, Any]] = []
    misses: list[dict[str, Any]] = []
    unseen_jobs: list[dict[str, Any]] = []
    exempt_workflows: list[dict[str, Any]] = []
    jobs_evaluated = 0
    for workflow in report:
        if workflow.get("exempt"):
            exempt_workflows.append({
                "workflow": workflow["workflow"],
                "gate_policy": workflow.get("gate_policy"),
            })
            continue
        for job in workflow.get("jobs", []):
            for entry in job.get("subsequent", []):
                if entry.get("classification") not in {"parity-issue", "ci-only-violation"}:
                    continue
                parity_issues.append({
                    "workflow": workflow["workflow"],
                    "job": job["job_id"],
                    "name": entry.get("name"),
                    "run": entry.get("run"),
                    "uses": entry.get("uses"),
                    "classification": entry.get("classification"),
                })
        without_gate = workflow.get("jobs_without_canonical_gate") or []
        if without_gate:
            misses.append({"workflow": workflow["workflow"], "jobs": list(without_gate)})
        unseen = workflow.get("jobs_gate_match_unestablished") or []
        if unseen:
            unseen_jobs.append({"workflow": workflow["workflow"], "jobs": list(unseen)})
        jobs_evaluated += len(workflow.get("jobs", [])) + len(without_gate)
    return {
        # Always present, so a consumer switching on `status` sees a VALUE rather
        # than a missing key. Without it the refusal payload (`named-scope-empty`)
        # and a clean run differed by key presence, and a consumer switching on
        # content read the refusal as a pass — this slice's own thesis, one level up.
        "status": "evaluated" if jobs_evaluated else "nothing-evaluated",
        "workflows_scanned": len(report),
        # `scanned` counts files READ; `evaluated` counts files NOT exempted —
        # which is weaker than "judged", since an unparseable workflow or one with
        # no `jobs:` mapping counts here while contributing no job. `jobs_evaluated`
        # is the honest denominator and is what the refusal keys on. Both exist
        # because they diverged silently: in charness's own repo both workflows
        # carry a `# charness:gate-policy` exemption marker, so the gate reported
        # green over ZERO evaluated jobs and nothing in the payload said so (S31's
        # consequence). A denominator that reached zero is now a value, not a gap.
        "workflows_not_exempt": len(report) - len(exempt_workflows),
        "jobs_evaluated": jobs_evaluated,
        "workflows": report,
        "parity_issues": parity_issues,
        "jobs_without_canonical_gate": misses,
        # Not a pass and not a violation: the canonical gate may run inside the
        # composite action or reusable workflow, which this reader cannot open, so
        # the match is UNESTABLISHED for these jobs (S26).
        "jobs_gate_match_unestablished": unseen_jobs,
        "exempt_workflows": exempt_workflows,
    }
