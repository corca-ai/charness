from __future__ import annotations

import sys
from pathlib import Path
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


def quality_resolver_path(repo_root: Path) -> Path:
    """The quality skill's `resolve_adapter.py` in the authoring or the exported layout."""
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "quality" / "scripts" / "resolve_adapter.py",
    )
    found = next((candidate for candidate in candidates if candidate.is_file()), None)
    if found is None:
        raise FileNotFoundError("quality resolve_adapter.py not found")
    return found


def load_adapter_validators(anchor_file: str | Path):
    """Import the quality skill's `adapter_validators` from the tree that ships `anchor_file`.

    The anchor's OWN checkout, not the analysed repo: a gate run with
    `CHARNESS_REPO_ROOT` pointing at a consumer still validates with the
    validators that ship beside it.
    """
    anchor = Path(anchor_file).resolve()
    repo_root = next(
        (p for p in anchor.parents if (p / "scripts" / "adapter_lib.py").is_file()),
        anchor.parents[2] if anchor.parent.name != "scripts" else anchor.parents[1],
    )
    for candidate in (
        repo_root / "skills" / "public" / "quality" / "scripts",
        repo_root / "skills" / "quality" / "scripts",
    ):
        if not (candidate / "adapter_validators.py").is_file():
            continue
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        import adapter_validators

        return adapter_validators
    raise FileNotFoundError("quality adapter_validators.py not found")
