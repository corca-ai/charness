from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_shared_helper():
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/check_prescribed_skill_executed_lib.py not found")


_CRITIQUE_LINE = re.compile(
    r"^\s*Critique(?:\s+(?P<target>[^:]+?))?\s*:\s*(?P<value>.+?)\s*$",
    re.MULTILINE,
)
_ISSUE_REF = re.compile(r"#(\d+)\b")
_CRITIQUE_BLOCKED = re.compile(r"^blocked\s+(.+)$", re.IGNORECASE)
CRITIQUE_REQUIRED_CLASSIFICATIONS = ("bug", "feature", "deferred-work")


def _strip_code_fences(text: str) -> list[str]:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return lines


def _critique_lines(body: str) -> list[dict[str, Any]]:
    plain = "\n".join(_strip_code_fences(body))
    lines: list[dict[str, Any]] = []
    for match in _CRITIQUE_LINE.finditer(plain):
        target = (match.group("target") or "").strip()
        value = match.group("value").strip()
        lines.append(
            {
                "target": target or None,
                "value": value,
                "target_numbers": [int(raw) for raw in _ISSUE_REF.findall(target)],
            }
        )
    return lines


def _line_numbers(line: dict[str, Any], numbers: list[int]) -> list[int]:
    target_numbers = [number for number in line["target_numbers"] if number in numbers]
    if target_numbers:
        return target_numbers
    if line["target"] is None and len(numbers) == 1:
        return [numbers[0]]
    return []


def _check_value(helper: Any, repo_root: Path, value: str) -> dict[str, Any]:
    blocked_match = _CRITIQUE_BLOCKED.match(value)
    if blocked_match:
        signal = blocked_match.group(1).strip()
        return helper.check(
            repo_root=repo_root,
            required=["resolution_critique"],
            evidence={},
            skips={"resolution_critique": f"host-blocked-subagent: {signal}"},
            kind="issue-resolution",
        )
    return helper.check(
        repo_root=repo_root,
        required=["resolution_critique"],
        evidence={"resolution_critique": value},
        skips={},
        kind="issue-resolution",
    )


def _resolved_evidence_path(check: dict[str, Any]) -> Path | None:
    for entry in check.get("satisfied", []):
        if entry.get("name") == "resolution_critique" and entry.get("via") == "evidence":
            return Path(str(entry.get("path", "")))
    return None


def _binding_failure(helper: Any, number: int, check: dict[str, Any]) -> dict[str, Any] | None:
    path = _resolved_evidence_path(check)
    if path is None:
        return None
    binds, reason = helper.evidence_binds_to_context(path, tokens=[str(number)])
    if binds:
        return None
    return {"number": number, "path": str(path), "reason": reason}


def _missing_check(helper: Any, repo_root: Path) -> dict[str, Any]:
    return helper.check(
        repo_root=repo_root,
        required=["resolution_critique"],
        evidence={},
        skips={},
        kind="issue-resolution",
    )


def check_resolution_critique(
    *,
    repo_root: Path,
    body: str,
    classification: str,
    numbers: list[int],
) -> dict[str, Any]:
    """Validate issue-resolution critique evidence for each selected issue.

    Single-issue closeouts keep the historical ``Critique: <path>`` shorthand.
    Bundled closeouts must bind each issue through ``Critique #N: <path>`` or
    one explicit multi-issue line such as ``Critique #1 #2: <path>``.
    """
    helper = _load_shared_helper()
    if classification not in CRITIQUE_REQUIRED_CLASSIFICATIONS:
        return {"ok": True, "skipped_classification": classification}

    lines = _critique_lines(body)
    if not lines:
        return _missing_check(helper, repo_root)

    checks: list[dict[str, Any]] = []
    binding_failures: list[dict[str, Any]] = []
    bound_numbers: set[int] = set()
    for line in lines:
        target_numbers = _line_numbers(line, numbers)
        if not target_numbers:
            continue
        check = _check_value(helper, repo_root, line["value"])
        checks.append(
            {
                "target": line["target"],
                "numbers": target_numbers,
                "value": line["value"],
                "check": check,
            }
        )
        if not check.get("ok", False):
            continue
        for number in target_numbers:
            failure = _binding_failure(helper, number, check)
            if failure is not None:
                binding_failures.append(failure)
                continue
            bound_numbers.add(number)

    missing_issue_bindings = [number for number in numbers if number not in bound_numbers]
    if len(numbers) == 1 and checks:
        report = dict(checks[0]["check"])
        report["bindings"] = [{"number": numbers[0], "target": checks[0]["target"]}]
        report["binding_failures"] = binding_failures
        report["missing_issue_bindings"] = missing_issue_bindings
        report["ok"] = bool(report.get("ok")) and not binding_failures and not missing_issue_bindings
        return report

    return {
        "ok": not missing_issue_bindings and not binding_failures and all(
            entry["check"].get("ok", False) for entry in checks
        ),
        "kind": "issue-resolution",
        "required": ["resolution_critique"],
        "checks": checks,
        "binding_failures": binding_failures,
        "missing_issue_bindings": missing_issue_bindings,
    }
