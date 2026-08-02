from __future__ import annotations

import importlib.util
import re
import runpy
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
_load_local = runpy.run_path(
    str(Path(__file__).resolve().parent / "issue_local_import.py")
)["sibling_loader"](__file__)
_strip_code_fences = _load_local("issue_markdown_lib").strip_code_fences
_observer = _load_local("issue_critique_observer")


def min_blocked_signal_length() -> int | None:
    """The floor a `Critique: blocked <signal>` signal must clear, or ``None``
    when the shared helper is not resolvable.

    Read live from the owning library rather than restated, so the author-facing
    shape describer cannot drift from the gate the way it did when the floor
    moved. Returns ``None`` instead of raising: a describer that cannot reach the
    helper should omit the number, never invent one or crash.
    """
    try:
        return int(_load_shared_helper().MIN_SKIP_DETAIL_LENGTH)
    except Exception:
        return None


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


def _observer_disposition(repo_root: Path, check: dict[str, Any]) -> dict[str, Any] | None:
    """Read the CITED artifact's own `Fresh-eye satisfaction:` record.

    The floor's presence check asks whether a critique exists. This asks the
    question that check is a proxy for: did anyone other than the closing agent
    read it? The two are not the same, and only the first was ever asked at the
    close boundary.

    Returns ``None`` when no evidence file resolved (the blocked-skip path and
    the missing-critique path both land there, and each is already reported by
    its own arm).
    """
    path = _resolved_evidence_path(check)
    if path is None:
        return None
    candidate = path if path.is_absolute() else repo_root / path
    try:
        # `errors="replace"`, matching the binding library that already read this
        # same file: it reads with errors ignored, so a bad byte binds cleanly and
        # would then have raised UnicodeDecodeError here — a traceback out of the
        # close command instead of the typed `unreadable` disposition designed
        # right below.
        text = candidate.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        # A cited artifact that cannot be READ is not a delegated one. Reported as
        # its own disposition rather than silently treated as absent, so an
        # unreadable path never reads like a consumer repo that simply has no
        # such convention.
        return {"value": None, "disposition": "unreadable", "path": str(path), "reason": str(error)}
    # The `blocked` valve is held to the SAME signal floor as its in-body sibling
    # `Critique: blocked <signal>`, read live from the owning library rather than
    # restated, so the two escape hatches cannot drift apart in cost.
    minimum = min_blocked_signal_length()
    disposition = _observer.observer_disposition(
        text,
        strip_code_fences=_strip_code_fences,
        **({"min_blocked_signal": minimum} if minimum is not None else {}),
    )
    return {
        **disposition,
        "path": str(path),
        # Grandfathering rides on the REPORT, not on the classification, so a
        # grandfathered close is visibly grandfathered instead of silently clean.
        "predates_typed_contract": _observer.predates_typed_contract(candidate, text),
    }


def _observer_advisories(checks: list[dict[str, Any]]) -> list[str]:
    """REVIEW-severity advisory for every close whose critique records that no
    distinct observer read it, on the paths that are NOT refused.

    `blocked` is the degradation valve a subagent-blocked host must keep, so it
    passes everywhere with an advisory: it is a positive record that no fresh eye
    ran, in any repo, and it is the one disposition that is neither a refusal nor
    a clean delegation.

    `absent` gets NO advisory on either arm, and the asymmetry is deliberate.
    Under the delegation contract it is refused, so the refusal already carries
    the message. Outside the contract the field is a convention the repo never
    adopted, so a line here would fire on every close in that repo forever — an
    advisory that always fires is the token-theater the floor-addition restraint
    names, and it trains the reader to skip the word REVIEW before the `blocked`
    case that matters.
    """
    lines: list[str] = []
    for entry in checks:
        observer = entry.get("fresh_eye_observer") or {}
        if observer.get("disposition") != "blocked":
            continue
        refs = ", ".join(f"#{number}" for number in entry["numbers"])
        # The valve carries two different facts and they need different advice.
        # Telling an operator to "confirm the host genuinely could not spawn one"
        # when the USER declined the standing delegation request asks them to
        # verify a machine failure that never happened — a deliberate "no"
        # laundered into an incapacity, at an irreversible public boundary.
        if observer.get("blocked_kind") == "delegation-declined":
            tail = (
                "the user DECLINED the standing bounded-review delegation request, so no fresh eye "
                "was authorized. This is a recorded user decision, not a host failure: confirm the "
                "decision still stands before treating this issue as resolved"
            )
        else:
            tail = (
                "Confirm the host genuinely could not spawn one before treating this issue as resolved"
            )
        lines.append(
            f"REVIEW: the resolution critique cited for {refs} records "
            f"`Fresh-eye satisfaction: {observer.get('value')}` — the artifact itself says no "
            f"distinct observer read this resolution. {tail} (advisory only, never blocks)."
        )
    return lines


#: Every disposition that blocks a close — but ONLY in a repo that adopted the
#: delegation contract. `absent` is here because nothing orders the artifact
#: validator before the GitHub mutation: `close-with-comment` performs no commit,
#: so the authoring-side floor that requires the line cannot be relied on to have
#: run, and omitting the line would otherwise be the cheapest bypass of all.
REFUSED_DISPOSITIONS = ("undelegated", "unreadable", "blocked-unsubstantiated", "absent")


def _refusal_reason(number: int, observer: dict[str, Any]) -> str:
    """One operator-facing sentence per refusal disposition.

    Each names the specific defect and the honest way out, because the generic
    "add `Critique: <path>`" message sends the author to fix the one thing that
    is not wrong on these paths.
    """
    records = f"records `Fresh-eye satisfaction: {observer.get('value')}`"
    detail = {
        "unreadable": (
            f"could not be read at {observer.get('path')}: {observer.get('reason')}"
        ),
        "absent": (
            "carries no `Fresh-eye satisfaction:` line, so who read this resolution is "
            "unrecorded at an irreversible public boundary. This repo's own critique contract "
            "requires that line; nothing runs that authoring floor before the close, so omitting "
            "it cannot be treated as already-caught. Record `parent-delegated` / "
            "`nested-delegated`, or `blocked <host-signal>`."
        ),
        "blocked-unsubstantiated": (
            f"{records} — it claims the host-blocked valve without naming what blocked it. The "
            "valve exists so a host that genuinely cannot spawn a reviewer can still close; a "
            "bare `blocked` is the word without the fact, and it is the cheapest possible way to "
            "defeat this floor. Name the concrete host signal."
        ),
    }.get(
        observer["disposition"],
        (
            f"{records}, which is neither a completed delegation "
            f"({' / '.join(_observer.DELEGATED_VALUES)}) nor the "
            f"`{_observer.BLOCKED_VALUE} <host-signal>` valve. Closing an issue is irreversible "
            "and public; a review the closing agent wrote about its own work is not a distinct "
            "observer. Either run the bounded review and record it, or record the host signal "
            "that prevented it."
        ),
    )
    return f"the resolution critique cited for #{number} {detail}"


def _observer_refusals(repo_root: Path, checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The close-blocking arm: a critique that POSITIVELY records that no distinct
    observer read it, in a repo that adopted the delegation contract.

    Deliberately narrow, and the narrowness is the defence. `undelegated` means
    the artifact carries a real value that is neither a completed delegation nor
    the `blocked` valve — a self-authored review, in the artifact's own words. A
    host that cannot spawn is not stranded: it writes `blocked <host-signal>` and
    closes with an advisory. A repo without the contract is not held to it at all.
    """
    if not _observer.repo_requires_delegated_observer(repo_root):
        return []
    refusals: list[dict[str, Any]] = []
    for entry in checks:
        observer = entry.get("fresh_eye_observer") or {}
        # `predates_typed_contract` is a grandfather, not a pass: an artifact
        # written before the typed contract existed records its delegation in
        # prose — "three reviewers ran in separate agent contexts" — with no typed
        # token anywhere. Six checked-in artifacts are exactly that, and refusing
        # them applies a rule that did not exist when they were written: teeth
        # landing entirely on honest authors, the failure mode this floor was
        # already repaired once to avoid. The disposition is still REPORTED.
        if observer.get("disposition") not in REFUSED_DISPOSITIONS or observer.get(
            "predates_typed_contract"
        ):
            continue
        for number in entry["numbers"]:
            refusals.append({
                "number": number,
                "path": observer.get("path"),
                "disposition": observer["disposition"],
                "value": observer.get("value"),
                "reason": _refusal_reason(number, observer),
            })
    return refusals


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
                "fresh_eye_observer": _observer_disposition(repo_root, check),
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
