"""Library helpers for inventory_ci_local_gate_parity.py."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Callable

DEFAULT_WORKFLOW_GLOB = ".github/workflows/*.yml"
DEFAULT_CANONICAL_GATE_PATTERNS = (
    r"\bnpm\s+run\s+verify\b",
    r"\bnpm\s+run\s+lint\s*&&\s*npm\s+run\s+test\b",
    r"\bmake\s+verify\b",
    r"\bbash\s+scripts/run-quality\.sh\b",
    r"\bbash\s+scripts/run-verify\.(?:mjs|sh)\b",
    r"\bnode\s+scripts/run-verify\.mjs\b",
    r"\bcharness\s+verify\b",
)
DEFAULT_CI_ONLY_MARKER = "CI-only"
GATE_POLICY_MARKER_PREFIX = "# charness:gate-policy "
SCHEDULED_DEEPER_CHECK_POLICY = "scheduled-deeper-check"
KNOWN_GATE_POLICIES = frozenset({SCHEDULED_DEEPER_CHECK_POLICY})
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


def iter_workflow_files(repo_root: Path, glob_pattern: str) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return sorted(p for p in repo_root.glob(glob_pattern) if p.is_file())
    visible = {repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel}
    return sorted(p for p in repo_root.glob(glob_pattern) if p.is_file() and p in visible)


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
    if gate_policy == SCHEDULED_DEEPER_CHECK_POLICY:
        return {
            "workflow": str(path),
            "gate_policy": gate_policy,
            "exempt": True,
            "jobs": [],
            "jobs_without_canonical_gate": [],
        }
    findings: dict[str, Any] = {"workflow": str(path), "jobs": [], "jobs_without_canonical_gate": []}
    data = workflow["data"]
    if not isinstance(data, dict):
        return findings
    jobs_block = data.get("jobs") or {}
    if not isinstance(jobs_block, dict):
        return findings
    marker_re = re.compile(re.escape(ci_only_marker), re.IGNORECASE)
    for job_id, job in jobs_block.items():
        if not isinstance(job, dict):
            continue
        steps_raw = job.get("steps") or []
        if not isinstance(steps_raw, list):
            continue
        steps = [step for step in steps_raw if isinstance(step, dict)]
        if not steps or all(not isinstance(step.get("run"), str) for step in steps):
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
    exempt_workflows: list[dict[str, Any]] = []
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
    return {
        "workflows_scanned": len(report),
        "workflows": report,
        "parity_issues": parity_issues,
        "jobs_without_canonical_gate": misses,
        "exempt_workflows": exempt_workflows,
    }
