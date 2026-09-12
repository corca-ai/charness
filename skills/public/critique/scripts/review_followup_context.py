"""Bound and bind the inert context carried by a critique follow-up."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

MAX_CONTEXT_BYTES = 24 * 1024
MAX_FINDINGS = 64


def clip(value: object, limit: int) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 16)] + "…[truncated]"


def compact_findings(raw: object) -> tuple[list[dict[str, Any]], list[str], bool]:
    if not isinstance(raw, list):
        return [], [], False
    findings: list[dict[str, Any]] = []
    omitted: list[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        finding_id = item.get("id")
        stable_id = str(finding_id) if finding_id is not None else f"finding-{index + 1}"
        evidence = item.get("evidence")
        evidence_items = evidence if isinstance(evidence, list) else []
        findings.append(
            {
                "id": stable_id,
                "severity": clip(item.get("severity", "unknown"), 80),
                "summary": clip(item.get("summary", ""), 480),
                "action": clip(item.get("action", ""), 640),
                "evidence": [clip(entry, 520) for entry in evidence_items[:4]],
            }
        )
    if len(findings) > MAX_FINDINGS:
        omitted = [str(item.get("id")) for item in findings[MAX_FINDINGS:] if item.get("id")]
        findings = findings[:MAX_FINDINGS]
    return findings, omitted, False


def context_bytes(context: dict[str, Any]) -> bytes:
    return (json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _path_digest(paths: list[str]) -> str:
    encoded = json.dumps(sorted(set(paths)), ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _collapse_path_arrays(value: object, key: str = "") -> object:
    if isinstance(value, dict):
        return {
            name: (
                {"count": len(nested), "sha256": _path_digest(nested), "summarized": True}
                if name.endswith("paths")
                and isinstance(nested, list)
                and all(isinstance(item, str) for item in nested)
                else _collapse_path_arrays(nested, name)
            )
            for name, nested in value.items()
        }
    if isinstance(value, list) and key.endswith("paths") and all(isinstance(item, str) for item in value):
        return {"count": len(value), "sha256": _path_digest(value), "summarized": True}
    if isinstance(value, list):
        return [_collapse_path_arrays(item, key) for item in value]
    return value


def bound_context(
    context: dict[str, Any], error: Callable[..., Exception]
) -> dict[str, Any]:
    if len(context_bytes(context)) <= MAX_CONTEXT_BYTES:
        return context
    findings = context.get("prior_findings")
    if isinstance(findings, list):
        for finding in findings:
            if isinstance(finding, dict):
                finding["evidence"] = [str(item)[:220] for item in finding.get("evidence", [])[:1]]
                finding["action"] = clip(finding.get("action", ""), 300)
                finding["summary"] = clip(finding.get("summary", ""), 300)
    context["context_truncated"] = True
    if len(context_bytes(context)) <= MAX_CONTEXT_BYTES:
        return context
    context["prior_findings"] = [
        {key: value for key, value in finding.items() if key in {"id", "severity", "summary"}}
        for finding in findings or []
        if isinstance(finding, dict)
    ]
    for key in ("selected_paths", "prior_reviewed_paths", "comparison", "selection_receipt"):
        if key in context:
            context[key] = _collapse_path_arrays(context[key], key)
    if len(context_bytes(context)) <= MAX_CONTEXT_BYTES:
        return context
    context = {
        key: context[key]
        for key in (
            "kind",
            "source",
            "source_sha256",
            "prior_attempt_id",
            "prior_verdict",
            "prior_packet_path",
            "prior_packet_sha256",
            "prior_reviewed_input_identity_sha256",
            "selection",
            "selected_paths",
            "selection_receipt",
            "prior_findings",
            "approval_rule",
            "context_truncated",
        )
        if key in context
    }
    context["prior_findings"] = [
        {key: finding.get(key, "") for key in ("id", "severity", "summary")}
        for finding in context.get("prior_findings", [])
        if isinstance(finding, dict)
    ]
    context["selected_paths"] = _collapse_path_arrays(context.get("selected_paths", []), "selected_paths")
    context["selection_receipt"] = _collapse_path_arrays(
        context.get("selection_receipt", {}), "selection_receipt"
    )
    findings = context.get("prior_findings")
    if isinstance(findings, list):
        original_count = len(findings)
        for summary_limit in (160, 80, 40, 0):
            context["prior_findings"] = [
                {
                    "id": finding.get("id", ""),
                    "severity": finding.get("severity", ""),
                    "summary": clip(finding.get("summary", ""), summary_limit),
                }
                for finding in findings
                if isinstance(finding, dict)
            ]
            if len(context_bytes(context)) <= MAX_CONTEXT_BYTES:
                return context
        retained = context["prior_findings"]
        while retained and len(context_bytes(context)) > MAX_CONTEXT_BYTES:
            retained.pop()
        omitted = original_count - len(retained)
        if omitted:
            context["prior_findings_omitted"] = omitted
    if len(context_bytes(context)) > MAX_CONTEXT_BYTES:
        raise error(
            "follow-up-context-too-large",
            "follow-up context cannot be reduced under its hard byte bound",
            details={"size_bytes": len(context_bytes(context)), "max_bytes": MAX_CONTEXT_BYTES},
        )
    return context


def bind_final_identity(
    context: dict[str, Any], identity: dict[str, Any], error: Callable[..., Exception]
) -> dict[str, Any]:
    """Join selection context to the identity of the packet actually assembled."""
    context["final_reviewed_input_identity_sha256"] = identity.get("identity_sha256")
    context["final_selected_path_count"] = len(identity.get("reviewed_paths", []))
    context.pop("context_size_bytes", None)
    context["context_size_bytes"] = 0
    for _ in range(8):
        size = len(context_bytes(context))
        if context["context_size_bytes"] == size:
            break
        context["context_size_bytes"] = size
    final_size = len(context_bytes(context))
    if final_size > MAX_CONTEXT_BYTES or context["context_size_bytes"] != final_size:
        raise error(
            "follow-up-context-too-large",
            "final follow-up context exceeds its hard byte bound",
            details={"size_bytes": final_size, "max_bytes": MAX_CONTEXT_BYTES},
        )
    return context
