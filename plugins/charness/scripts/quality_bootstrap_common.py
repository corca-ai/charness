from __future__ import annotations

from typing import Any


def merge_unique(existing: list[str], inferred: list[str]) -> list[str]:
    merged = list(existing)
    for item in inferred:
        if item not in merged:
            merged.append(item)
    return merged


def classify_command_deferral(field: str, preset_lineage: list[str]) -> dict[str, Any]:
    if field == "gate_commands":
        families = ["repo-native test runner", "repo-native lint or typecheck gate"]
        if "python-quality" in preset_lineage:
            families = ["pytest or repo-native test runner", "ruff, mypy, or pyright"]
        elif "typescript-quality" in preset_lineage:
            families = ["vitest or jest", "eslint or tsc --noEmit"]
        elif "go-quality" in preset_lineage:
            families = ["go test ./...", "go vet ./..."]
        elif "specdown-quality" in preset_lineage:
            families = ["specdown smoke", "overlap or adapter-depth guard"]
        reason = "No repo-owned quality gate command was detected."
    elif field == "preflight_commands":
        families = ["maintainer setup validation", "repo doctor or setup sanity"]
        reason = "No repo-owned maintainer setup or doctor command was detected."
    else:
        families = ["secret scan", "dependency or supply-chain audit"]
        reason = "No repo-owned security helper was detected."
    return {"field": field, "status": "deferred", "reason": reason, "suggested_families": families}
