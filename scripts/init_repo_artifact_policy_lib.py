from __future__ import annotations

from pathlib import Path

REQUIRED_SNIPPETS = (
    "charness-artifacts/",
    "repo state",
    "canonical content",
    "no-op",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _repo_uses_charness_artifacts(repo_root: Path) -> bool:
    if (repo_root / "charness-artifacts").exists():
        return True
    agents_dir = repo_root / ".agents"
    return agents_dir.is_dir() and any(
        "charness-artifacts/" in _read_text(adapter_path)
        for adapter_path in agents_dir.glob("*adapter*.yaml")
    )


def detect_charness_artifact_policy(
    repo_root: Path,
    agents_text: str,
) -> tuple[dict[str, object], list[dict[str, str]]]:
    uses_artifacts = _repo_uses_charness_artifacts(repo_root)
    lowered = agents_text.lower()
    missing_required = [
        snippet for snippet in REQUIRED_SNIPPETS if uses_artifacts and snippet not in lowered
    ]
    findings = []
    if uses_artifacts and missing_required:
        findings.append(
            {
                "type": "charness_artifacts_commit_policy_drift",
                "message": (
                    "Repo uses Charness durable artifacts but AGENTS.md does not say meaningful "
                    "charness-artifacts/ changes are repo state and that current-pointer helpers "
                    "should no-op when canonical content has not changed."
                ),
                "recommended_action": "add_charness_artifacts_repo_state_policy_to_agents",
            }
        )
    return {
        "uses_charness_artifacts": uses_artifacts,
        "missing_required_snippets": missing_required,
    }, findings
