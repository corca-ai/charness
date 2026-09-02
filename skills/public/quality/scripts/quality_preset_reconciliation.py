"""Typed preset-lineage reconciliation for quality declarations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

COMMAND_FIELDS = (
    "preflight_commands",
    "gate_commands",
    "review_commands",
    "security_commands",
)
PRESETS_DIR = Path("presets")


def preset_contract(
    repo_root: Path, preset: object, repo_module: Callable[[str], Any]
) -> dict[str, Any]:
    """Load one repo-owned, machine-readable preset adoption contract."""
    validator = repo_module("scripts.validate_presets")
    if not isinstance(preset, str) or not validator.re.fullmatch(validator.PRESET_NAME_RE, preset):
        return {"state": "unavailable", "reason": "preset id must be a simple filename"}
    canonical_repo_root = repo_root.resolve()
    path = repo_root / PRESETS_DIR / f"{preset}.md"
    if not path.is_file():
        return {"state": "metadata-only", "reason": "no local machine-readable preset prescription"}
    try:
        resolved_path = path.resolve()
    except OSError:
        return {
            "state": "unavailable",
            "reason": f"could not resolve {path.relative_to(repo_root)}",
        }
    if not resolved_path.is_relative_to(canonical_repo_root / PRESETS_DIR):
        return {
            "state": "unavailable",
            "reason": f"{path.relative_to(repo_root)} must resolve inside presets/",
        }
    try:
        data = validator.validate_preset(path)
    except (OSError, ValueError, TypeError, validator.ValidationError) as exc:
        return {
            "state": "unavailable",
            "reason": f"{path.relative_to(repo_root)} is not a valid preset: {exc}",
        }
    reconciliation = data.get("reconciliation") if isinstance(data, dict) else None
    if reconciliation is None:
        return {
            "state": "metadata-only",
            "reason": "preset declares no reconciliation prescription",
        }
    if not isinstance(reconciliation, dict):
        return {"state": "unavailable", "reason": "reconciliation must be a mapping"}
    required = reconciliation.get("required_adapter_commands")
    if (
        not isinstance(required, list)
        or not required
        or not all(isinstance(item, str) and item.strip() for item in required)
    ):
        return {
            "state": "unavailable",
            "reason": "reconciliation.required_adapter_commands must be a non-empty string list",
        }
    return {"state": "prescribed", "required_adapter_commands": list(required)}


def preset_rows(
    repo_root: Path, raw: dict[str, Any], repo_module: Callable[[str], Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Reconcile explicit prescriptions against exact declared commands."""
    detected = set(repo_module("scripts.quality_bootstrap_detect").detect_preset_lineage(repo_root))
    declared_commands = {
        command
        for field in COMMAND_FIELDS
        for command in (raw.get(field) if isinstance(raw.get(field), list) else [])
        if isinstance(command, str) and command.strip()
    }
    rows: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for preset in raw.get("preset_lineage") if isinstance(raw.get("preset_lineage"), list) else []:
        contract = preset_contract(repo_root, preset, repo_module)
        row: dict[str, Any] = {
            "preset": preset,
            "declaration_state": "declared",
            "repo_signal_detected": preset in detected,
        }
        if contract["state"] == "metadata-only":
            row.update(
                {
                    "reconciliation_state": "metadata-only",
                    "reconciliation_reason": contract["reason"],
                }
            )
        elif contract["state"] == "unavailable":
            row.update(
                {"reconciliation_state": "unavailable", "reconciliation_reason": contract["reason"]}
            )
            gaps.append(
                {
                    "kind": "preset_reconciliation_unavailable",
                    "detail": f"{preset}: {contract['reason']}",
                }
            )
        else:
            required = contract["required_adapter_commands"]
            missing = [command for command in required if command not in declared_commands]
            row.update(
                {
                    "required_adapter_commands": required,
                    "missing_adapter_commands": missing,
                    "reconciliation_state": "missing" if missing else "reconciled",
                }
            )
            gaps.extend(
                {
                    "kind": "preset_requirement_missing",
                    "detail": f"{preset}: declare adapter command: {command}",
                }
                for command in missing
            )
        rows.append(row)
    return rows, gaps
