from __future__ import annotations

from typing import Any


def runtime_visibility_findings(adapter_data: dict[str, Any], budgets: dict[str, int]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not budgets:
        findings.append(
            {
                "type": "runtime_visibility_missing_budgets",
                "severity": "weak",
                "message": (
                    "quality adapter has no effective runtime budget for the selected profile; "
                    "runtime reviews cannot budget standing-gate cost centers."
                ),
                "recommended_action": (
                    "Add budgets for dominant standing-gate phases once structured runtime samples exist."
                ),
            }
        )
    if not adapter_data.get("startup_probes"):
        findings.append(
            {
                "type": "runtime_visibility_missing_startup_probes",
                "severity": "weak",
                "message": (
                    "quality adapter has no startup_probes; repeated CLI or process startup cost "
                    "will remain invisible to quality review."
                ),
                "recommended_action": "Add at least one standing startup probe for agent-facing CLI or adapter startup.",
            }
        )
    return findings
