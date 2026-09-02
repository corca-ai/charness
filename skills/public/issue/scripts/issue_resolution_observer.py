"""Fresh-eye evidence policy for issue-resolution closeout checks."""

from __future__ import annotations

import importlib.util
import re
import runpy
import sys
from pathlib import Path
from typing import Any


def _load_critique_shape():
    """Load the package-owned reviewer-tier shape used by critique producers."""
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "critique_reviewer_evidence.py"
        if not candidate.is_file():
            continue
        if str(ancestor) not in sys.path:
            sys.path.insert(0, str(ancestor))
        spec = importlib.util.spec_from_file_location("charness_critique_shape", candidate)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/critique_reviewer_evidence.py not found")


def _load_shared_helper():
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "gates" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    raise ImportError("scripts/gates/check_prescribed_skill_executed_lib.py not found")


_load_local = runpy.run_path(
    str(Path(__file__).resolve().parent / "issue_local_import.py")
)["sibling_loader"](__file__)
_strip_code_fences = _load_local("issue_markdown_lib").strip_code_fences
_observer = _load_local("issue_critique_observer")
_critique_shape = _load_critique_shape()

_TYPED_TIER_FIELDS = _critique_shape.TYPED_REVIEWER_TIER_FIELDS
_EXECUTION_MODE_FIELD = _critique_shape.REVIEWER_EXECUTION_MODE_FIELD
_TYPED_EXECUTION_MODE = _critique_shape.TYPED_SUBAGENT_EXECUTION_MODE
_TYPED_HOST_STATES = {
    "pending-parent-spawn",
    "requested_fields_sent",
    "metadata-hidden",
    "host-defaulted",
    "unsupported",
    "applied",
}
_TYPED_DELIVERY_STATES = {
    "findings-received",
    "pending-parent-spawn",
    "spawn-accepted-no-delivery",
    "host-channel-unreadable",
    "host-capacity-blocked",
    "timed-out",
    "non-delivery-unknown",
    "findings-recovered-from-transcript",
}
REFUSED_DISPOSITIONS = (
    "undelegated",
    "carrier-unverified",
    "round-cap-unreviewed",
    "delegation-unverified",
    "delegation-contradicted",
    "outside-repo",
    "unreadable",
    "blocked-unsubstantiated",
    "absent",
)


def _read_min_blocked_signal_length(loader: Any) -> int | None:
    try:
        return int(loader().MIN_SKIP_DETAIL_LENGTH)
    except Exception:
        return None


def min_blocked_signal_length() -> int | None:
    return _read_min_blocked_signal_length(_load_shared_helper)


def _resolved_evidence_path(check: dict[str, Any]) -> Path | None:
    for entry in check.get("satisfied", []):
        if entry.get("name") == "resolution_critique" and entry.get("via") == "evidence":
            return Path(str(entry.get("path", "")))
    return None


def _typed_delegation_error(text: str) -> str | None:
    fields = _observer._section_fields(text, "Reviewer Tier Evidence")
    missing = [field for field in _TYPED_TIER_FIELDS if not fields.get(field)]
    if missing:
        return f"typed-subagent reviewer evidence is missing fields: {missing}"
    stubs = [
        field
        for field in _TYPED_TIER_FIELDS
        if re.match(r"^(todo|tbd)\b", fields[field].strip().lower())
    ]
    if stubs:
        return f"typed-subagent reviewer evidence contains placeholders: {stubs}"
    if fields[_EXECUTION_MODE_FIELD].strip().lower() != _TYPED_EXECUTION_MODE:
        return (
            "typed-subagent reviewer evidence execution mode is not "
            f"{_TYPED_EXECUTION_MODE}: {fields[_EXECUTION_MODE_FIELD]!r}"
        )
    host_state = fields["host exposure state"].strip().lower()
    if host_state not in _TYPED_HOST_STATES:
        return f"typed-subagent reviewer host exposure state is invalid: {host_state!r}"
    delivery_state = fields["delivery state"].strip().lower()
    if delivery_state not in _TYPED_DELIVERY_STATES:
        return f"typed-subagent reviewer delivery state is invalid: {delivery_state!r}"
    if host_state == "applied" and not fields["application state"].lower().startswith("host-confirmed:"):
        return "typed-subagent reviewer application state claims applied without host-confirmed evidence"
    return None


def _observer_disposition(
    repo_root: Path,
    check: dict[str, Any],
    *,
    expected_issue_numbers: list[int] | None = None,
    expected_repository: str | None = None,
) -> dict[str, Any] | None:
    path = _resolved_evidence_path(check)
    if path is None:
        return None
    candidate = path if path.is_absolute() else repo_root / path
    try:
        candidate = candidate.resolve()
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return {
            "value": None,
            "disposition": "outside-repo",
            "path": str(path),
            "reason": "cited critique resolves outside the consuming repository",
        }
    try:
        text = candidate.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        return {"value": None, "disposition": "unreadable", "path": str(path), "reason": str(error)}
    minimum = min_blocked_signal_length()
    disposition = _observer.observer_disposition(
        text,
        strip_code_fences=_strip_code_fences,
        **({"min_blocked_signal": minimum} if minimum is not None else {}),
    )
    result = {
        **disposition,
        "path": str(path),
        "predates_typed_contract": _observer.predates_typed_contract(
            candidate, text, repo_root=repo_root
        ),
    }
    if (
        result.get("disposition") == "delegated"
        and _observer.WORKER_DELIVERED_VALUE in str(result.get("value", "")).lower()
    ):
        result.update(
            _observer._worker_carrier_disposition(
                repo_root,
                text,
                required_issue_numbers=expected_issue_numbers,
                required_repository=expected_repository,
            )
        )
    elif result.get("disposition") == "delegated":
        tier_error = None if result.get("predates_typed_contract") else _typed_delegation_error(text)
        if tier_error:
            result["disposition"] = "delegation-unverified"
            result["tier_reason"] = tier_error
            return result
        tier = _observer._section_fields(text, "Reviewer Tier Evidence")
        host_state = tier.get("host exposure state", "").strip().lower()
        delivery_state = tier.get("delivery state", "").strip().lower()
        if host_state.startswith("pending-parent-spawn") or (
            delivery_state and not delivery_state.startswith("findings-received")
        ):
            result["disposition"] = "delegation-contradicted"
            result["contradiction"] = {
                "host_exposure_state": host_state,
                "delivery_state": delivery_state,
            }
    return result


def _observer_advisories(checks: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for entry in checks:
        observer = entry.get("fresh_eye_observer") or {}
        if observer.get("disposition") != "blocked":
            continue
        refs = ", ".join(f"#{number}" for number in entry["numbers"])
        if observer.get("blocked_kind") == "delegation-declined":
            tail = (
                "the user DECLINED the standing bounded-review delegation request, so no fresh eye "
                "was authorized. This is a recorded user decision, not a host failure: confirm the "
                "decision still stands before treating this issue as resolved"
            )
        else:
            tail = "Confirm the host genuinely could not spawn one before treating this issue as resolved"
        lines.append(
            f"REVIEW: the resolution critique cited for {refs} records "
            f"`Fresh-eye satisfaction: {observer.get('value')}` — the artifact itself says no "
            f"distinct observer read this resolution. {tail} (advisory only, never blocks)."
        )
    return lines


def _refusal_reason(number: int, observer: dict[str, Any]) -> str:
    records = f"records `Fresh-eye satisfaction: {observer.get('value')}`"
    detail = {
        "unreadable": f"could not be read at {observer.get('path')}: {observer.get('reason')}",
        "outside-repo": (
            f"is outside the consuming repository at {observer.get('path')}: {observer.get('reason')}. "
            "A closeout cannot cite foreign or symlink-escaped evidence."
        ),
        "absent": (
            "carries no `Fresh-eye satisfaction:` line, so who read this resolution is unrecorded at "
            "an irreversible public boundary. Record `parent-delegated` / `nested-delegated`, or "
            "`blocked <host-signal>`."
        ),
        "blocked-unsubstantiated": (
            f"{records} — it claims the host-blocked valve without naming what blocked it. "
            "Name the concrete host signal."
        ),
        "carrier-unverified": (
            f"claims a file-backed worker delivery, but the durable report carrier could not prove "
            f"approval: {observer.get('carrier_reason')}. A process exit, output file, or prose line "
            "is not a fresh-eye approval; repair the report/receipt/ledger and packet-input joins."
        ),
        "delegation-unverified": (
            f"claims a completed typed-subagent review, but its Reviewer Tier Evidence is incomplete "
            f"or invalid: {observer.get('tier_reason')}. Record the actual host-boundary states."
        ),
        "round-cap-unreviewed": (
            f"records `{observer.get('value')}`, which is an explicit non-approval under the bounded "
            "review round cap. A capped repair is not a fresh-eye approval."
        ),
        "delegation-contradicted": (
            f"claims a completed typed-subagent review, but its host exposure is "
            f"`{observer.get('contradiction', {}).get('host_exposure_state')}` and delivery is "
            f"`{observer.get('contradiction', {}).get('delivery_state')}`."
        ),
    }.get(
        observer["disposition"],
        (
            f"{records}, which is neither a completed delegation ({' / '.join(_observer.DELEGATED_VALUES)}) "
            f"nor the `{_observer.BLOCKED_VALUE} <host-signal>` valve. A review the closing agent "
            "wrote about its own work is not a distinct observer. Run bounded review and record it, "
            "or record the host signal that prevented it."
        ),
    )
    return f"the resolution critique cited for #{number} {detail}"


def _observer_refusals(repo_root: Path, checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contract_required = _observer.repo_requires_delegated_observer(repo_root)
    unconditional_refusals = {"carrier-unverified", "outside-repo", "round-cap-unreviewed"}
    refusals: list[dict[str, Any]] = []
    for entry in checks:
        observer = entry.get("fresh_eye_observer") or {}
        disposition = observer.get("disposition")
        if disposition not in REFUSED_DISPOSITIONS:
            continue
        if disposition not in unconditional_refusals and not contract_required:
            continue
        if disposition not in unconditional_refusals and observer.get("predates_typed_contract"):
            continue
        for number in entry["numbers"]:
            refusals.append(
                {
                    "number": number,
                    "path": observer.get("path"),
                    "disposition": disposition,
                    "value": observer.get("value"),
                    "reason": _refusal_reason(number, observer),
                }
            )
    return refusals
