from __future__ import annotations

import importlib.util
import re
import runpy
from pathlib import Path
from typing import Any

_CRITIQUE_LINE = re.compile(
    r"^\s*Critique(?:\s+(?P<target>[^:]+?))?\s*:\s*(?P<value>.+?)\s*$",
    re.MULTILINE,
)
_ISSUE_REF = re.compile(r"#(\d+)\b")
_CRITIQUE_BLOCKED = re.compile(r"^blocked\s+(.+)$", re.IGNORECASE)
CRITIQUE_REQUIRED_CLASSIFICATIONS = ("bug", "feature", "deferred-work")
_load_local = runpy.run_path(
    str(Path(__file__).resolve().parent / "issue_local_import.py")
)["sibling_loader"](__file__)
_strip_code_fences = _load_local("issue_markdown_lib").strip_code_fences
_OBSERVER_SUPPORT_SPEC = importlib.util.spec_from_file_location(
    "charness_issue_resolution_observer",
    Path(__file__).resolve().with_name("issue_resolution_observer.py"),
)
if _OBSERVER_SUPPORT_SPEC is None or _OBSERVER_SUPPORT_SPEC.loader is None:
    raise ImportError("issue resolution observer support is unavailable")
_OBSERVER_SUPPORT = importlib.util.module_from_spec(_OBSERVER_SUPPORT_SPEC)
_OBSERVER_SUPPORT_SPEC.loader.exec_module(_OBSERVER_SUPPORT)
_observer_disposition = _OBSERVER_SUPPORT._observer_disposition
_observer_advisories = _OBSERVER_SUPPORT._observer_advisories
REFUSED_DISPOSITIONS = _OBSERVER_SUPPORT.REFUSED_DISPOSITIONS
_observer_refusals = _OBSERVER_SUPPORT._observer_refusals
_resolved_evidence_path = _OBSERVER_SUPPORT._resolved_evidence_path
_load_shared_helper = _OBSERVER_SUPPORT._load_shared_helper


def min_blocked_signal_length() -> int | None:
    return _OBSERVER_SUPPORT._read_min_blocked_signal_length(_load_shared_helper)


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


def _check_value(
    helper: Any, repo_root: Path, value: str, target_numbers: list[int]
) -> dict[str, Any]:
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
        # `residual_tokens`, not `tokens`: binding stays per-ISSUE below, because
        # one critique line may name several issues and each must bind on its own,
        # while `tokens=` means "bind if ANY match". The stub floor is a per-FILE
        # question, so it can run here. Without it this gate accepted an evidence
        # file whose entire content was the issue citation itself -- the floor
        # lived in the shared library and this caller never reached it.
        residual_tokens=[str(number) for number in target_numbers],
    )


def _binding_failure(helper: Any, number: int, check: dict[str, Any]) -> dict[str, Any] | None:
    path = _resolved_evidence_path(check)
    if path is None:
        return None
    binds, reason = helper.evidence_binds_to_context(path, tokens=[str(number)])
    # The report `check()` produced says `binding_checked: false`, because this
    # wrapper binds out here instead of passing `tokens=` in. Left alone, a
    # correctly-bound issue close reports that it was never bound -- the field
    # added so a presence-only pass could not read as a bound one, saying the
    # opposite of the truth.
    check["binding_checked"] = True
    check.setdefault("binding_tokens", [])
    if str(number) not in check["binding_tokens"]:
        check["binding_tokens"].append(str(number))
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


def _skip_advisories(checks: list[dict[str, Any]]) -> list[str]:
    """REVIEW-severity advisory for each issue whose resolution critique was
    satisfied by a ``blocked <signal>`` host skip rather than a real critique.

    Rung-1 cannot judge whether a host block was genuine — the caller supplies
    both the enum head and the signal text, so the only surviving teeth are the
    detail-length floor and this line. Without it a skipped critique's top-level
    verdict (``ok: True``, ``status: carrier_verified``) is indistinguishable
    from an executed one, which is what let a 17-character excuse close a real
    issue on GitHub (B2). Advisory only: never affects ``ok`` or exit status.
    """
    lines: list[str] = []
    for entry in checks:
        skipped = entry["check"].get("skipped") or []
        for skip in skipped:
            if skip.get("name") != "resolution_critique":
                continue
            refs = ", ".join(f"#{number}" for number in entry["numbers"])
            lines.append(
                f"REVIEW: the resolution critique for {refs} was SKIPPED, not executed "
                f"— recorded host signal: {skip.get('reason', '')!r}. No fresh-eye review "
                "of this resolution exists; confirm the host genuinely could not spawn one "
                "before treating this issue as resolved (advisory only, never blocks)."
            )
    return lines


def check_resolution_critique(
    *,
    repo_root: Path,
    body: str,
    classification: str,
    numbers: list[int],
    repository: str | None = None,
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
        check = _check_value(helper, repo_root, line["value"], target_numbers)
        checks.append(
            {
                "target": line["target"],
                "numbers": target_numbers,
                "value": line["value"],
                "check": check,
                "fresh_eye_observer": _observer_disposition(
                    repo_root,
                    check,
                    expected_issue_numbers=target_numbers,
                    expected_repository=repository,
                ),
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
    review_advisory = _skip_advisories(checks) + _observer_advisories(checks)
    observer_refusals = _observer_refusals(repo_root, checks)
    if len(numbers) == 1 and checks:
        report = dict(checks[0]["check"])
        report["bindings"] = [{"number": numbers[0], "target": checks[0]["target"]}]
        report["binding_failures"] = binding_failures
        report["missing_issue_bindings"] = missing_issue_bindings
        report["review_advisory"] = review_advisory
        report["fresh_eye_observer"] = checks[0].get("fresh_eye_observer")
        # `observer_refusals` spans every check, so reporting only `checks[0]`'s
        # disposition could show `delegated` beside a refusal a second critique
        # line produced. The list is the honest record; the scalar stays for the
        # single-line case every real single-issue body actually has.
        report["fresh_eye_observers"] = [entry.get("fresh_eye_observer") for entry in checks]
        report["observer_refusals"] = observer_refusals
        report["ok"] = (
            bool(report.get("ok"))
            and not binding_failures
            and not missing_issue_bindings
            and not observer_refusals
        )
        return report

    return {
        "ok": not missing_issue_bindings and not binding_failures and not observer_refusals and all(
            entry["check"].get("ok", False) for entry in checks
        ),
        "kind": "issue-resolution",
        "required": ["resolution_critique"],
        "checks": checks,
        "binding_failures": binding_failures,
        "missing_issue_bindings": missing_issue_bindings,
        "observer_refusals": observer_refusals,
        "review_advisory": review_advisory,
    }
