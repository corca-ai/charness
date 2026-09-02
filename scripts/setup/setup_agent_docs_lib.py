from __future__ import annotations

from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.setup.setup_operating_surface_lib import (  # noqa: E402
    detect_operating_surface_ownership,  # noqa: E402
)

RETRO_ADAPTER_RELATIVE_PATH = Path(".agents/retro-adapter.yaml")
RETRO_SUMMARY_RELATIVE_PATH = Path("charness-artifacts/retro/recent-lessons.md")
RECOMMENDATION_PRIORITY_ORDER = {
    "review_required": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "advisory": 4,
}

# Setup reports only findings it can own. Artifact commit wording, skill
# detailed routing prose, session hooks, and review delegation belong to the
# workflow that uses them; copying those contracts into every consumer AGENTS.md
# was a source of drift and false setup work. The compact template's one-line
# parallel cue is intentionally not a host-specific delegation contract.
FINDING_RECOMMENDATION_PRIORITIES: dict[str, str] = {}
RECOMMENDATION_FINDING_TYPES: set[str] = set()


def _file_state(path: Path) -> dict[str, object]:
    if not path.exists() and not path.is_symlink():
        return {"exists": False, "kind": "missing"}
    if path.is_symlink():
        return {"exists": True, "kind": "symlink", "target": str(path.readlink())}
    if path.is_file():
        return {"exists": True, "kind": "file", "size": path.stat().st_size}
    return {"exists": True, "kind": "other"}


def _text_present(path: Path) -> bool:
    return path.is_file() and path.read_text(encoding="utf-8", errors="replace").strip() != ""


def _case_insensitive_path(repo_root: Path, relative_path: Path) -> Path:
    current = repo_root
    for part in relative_path.parts:
        exact = current / part
        if exact.exists() or exact.is_symlink():
            current = exact
            continue
        if not current.is_dir():
            return exact
        matches = sorted(child for child in current.iterdir() if child.name.lower() == part.lower())
        current = matches[0] if matches else exact
    return current


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _retro_memory_state(repo_root: Path, agents_text: str) -> dict[str, object]:
    """Expose the opt-in retro seam without making setup its policy owner."""

    adapter_exists = (repo_root / RETRO_ADAPTER_RELATIVE_PATH).is_file()
    summary_exists = (repo_root / RETRO_SUMMARY_RELATIVE_PATH).is_file()
    return {
        "enabled": adapter_exists or summary_exists,
        "adapter_exists": adapter_exists,
        "summary_exists": summary_exists,
        "agents_mentions_summary": RETRO_SUMMARY_RELATIVE_PATH.as_posix() in agents_text,
        "policy_owner": "retro",
    }


def _recommendation(
    *,
    rec_id: str,
    target: str,
    kind: str,
    priority: str,
    confidence: str,
    enforcement_tier: str,
    evidence: list[str],
    suggested_action: str,
) -> dict[str, object]:
    return {
        "id": rec_id,
        "target": target,
        "kind": kind,
        "priority": priority,
        "confidence": confidence,
        "enforcement_tier": enforcement_tier,
        "evidence": evidence,
        "suggested_action": suggested_action,
        "acknowledgement": {"status": "unacknowledged"},
    }


def finding_recommendation(finding: dict[str, str], *, priority: str = "advisory") -> dict[str, object]:
    return _recommendation(
        rec_id=finding["type"],
        target="AGENTS.md",
        kind="policy_sync",
        priority=priority,
        confidence="medium",
        enforcement_tier="NON_AUTOMATABLE",
        evidence=[finding["message"]],
        suggested_action=finding["recommended_action"],
    )


def is_acknowledged(item_id: str, acknowledged: set[str]) -> bool:
    return item_id in acknowledged


def sort_recommendations(recommendations: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        recommendations,
        key=lambda item: (
            RECOMMENDATION_PRIORITY_ORDER.get(str(item.get("priority")), 99),
            str(item.get("id")),
        ),
    )


def detect_agent_docs(repo_root: Path) -> dict[str, object]:
    """Inspect the host-doc boundary without prescribing workflow prose."""

    agents = _case_insensitive_path(repo_root, Path("AGENTS.md"))
    claude = _case_insensitive_path(repo_root, Path("CLAUDE.md"))
    agents_text = _read_text(agents)
    if not agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_agents_and_symlink"
    elif agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_symlink_only"
    elif claude.is_symlink() and claude.resolve() == agents.resolve():
        action = "leave_as_is"
    elif claude.is_file() and not agents.exists():
        action = "ask_to_promote_claude_into_agents"
    elif claude.is_file() and agents.exists():
        action = "ask_to_merge_and_replace_with_symlink"
    else:
        action = "inspect_manually"

    from scripts.setup.setup_adapter_inspect_lib import (
        detect_setup_adapter_normalization,
        detect_worktree_adapter_normalization,
    )

    worktree_adapter, worktree_findings, worktree_recommendations = (
        detect_worktree_adapter_normalization(repo_root)
    )
    setup_adapter, setup_recommendations = detect_setup_adapter_normalization(repo_root)
    ownership = detect_operating_surface_ownership(repo_root, agents_text=agents_text)
    findings = list(worktree_findings)
    recommendations = [*worktree_recommendations, *setup_recommendations]
    return {
        "agents": _file_state(agents),
        "claude": _file_state(claude),
        "recommended_action": action,
        "agents_has_text": _text_present(agents),
        "claude_has_text": _text_present(claude),
        "normalization": {
            "status": "needs_normalization" if findings or recommendations else "ok",
            "findings": findings,
            "recommendations": sort_recommendations(recommendations),
            "retro_memory": _retro_memory_state(repo_root, agents_text),
            "worktree_adapter": worktree_adapter,
            "setup_adapter": setup_adapter,
            "ownership": ownership,
        },
    }
