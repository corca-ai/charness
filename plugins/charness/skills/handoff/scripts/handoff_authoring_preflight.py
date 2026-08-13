#!/usr/bin/env python3
"""Pre-edit handoff checks as one cohesive authoring boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Any

HANDOFF_AUTHORING_ACTIONS = frozenset({"refresh_handoff", "repair_or_prune_handoff"})
PREFLIGHT = "scripts/check_doc_authoring_preflight.py"
PREFLIGHT_DEPENDENCIES = (PREFLIGHT, "scripts/doc_authoring_rules.py")


def _item(why: str, command: str) -> dict[str, Any]:
    return {
        "path": PREFLIGHT,
        "why": why,
        "kind": "preflight",
        "base": "repo",
        "command": command,
    }


def required_reads(repo_root: Path, artifact_path: str) -> list[dict[str, Any]]:
    """Return rules-first, target-second checks when the repo can run them.

    Rules mode forecasts the contract. Target mode reports deterministic
    findings already present in the current artifact. Semantic proof-receipt
    ownership remains agent judgment in the handoff skill's phase barrier.
    """
    if any(not (repo_root / required).is_file() for required in PREFLIGHT_DEPENDENCIES):
        return []
    surface = "handoff" if artifact_path.endswith("handoff.md") else None
    rules_command = f"python3 {PREFLIGHT} --repo-root ."
    if surface:
        rules_command += f" --as-surface {surface}"
    reads = [
        _item("deterministic rules for this surface BEFORE writing into it", rules_command)
    ]
    if (repo_root / artifact_path).is_file():
        reads.append(
            _item(
                "deterministic findings already present in the current handoff BEFORE rewriting it",
                f"python3 {PREFLIGHT} --repo-root . --path {artifact_path}",
            )
        )
    return reads
