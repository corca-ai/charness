#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

PREMORTEM_ARTIFACT_PREFIX = "charness-artifacts/premortem/"
FORBIDDEN_SUBAGENT_BLOCKER_PHRASES = (
    "did not explicitly allow subagents",
    "explicit subagent allowance",
    "only permits spawning subagents when",
    "only permits spawning subagents after",
    "current session delegation policy",
    "current developer instruction only permits",
)
DELEGATION_CONTRACT_MARKERS = (
    "subagent delegation",
    "repo-mandated bounded fresh-eye subagent reviews are already delegated",
)


class ValidationError(Exception):
    pass


def _git_paths(repo_root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_paths(repo_root: Path) -> list[str]:
    paths = set(_git_paths(repo_root, ["diff", "--name-only", "HEAD", "--"]))
    paths.update(_git_paths(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(paths)


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    if all_artifacts:
        return sorted((repo_root / PREMORTEM_ARTIFACT_PREFIX).glob("*.md"))
    candidates: list[Path] = []
    for relpath in paths:
        if relpath.startswith(PREMORTEM_ARTIFACT_PREFIX) and relpath.endswith(".md"):
            path = repo_root / relpath
            if path.is_file():
                candidates.append(path)
    return sorted(candidates)


def has_repo_delegation_contract(repo_root: Path) -> bool:
    agents_path = repo_root / "AGENTS.md"
    if not agents_path.is_file():
        return False
    text = agents_path.read_text(encoding="utf-8").lower()
    return all(marker in text for marker in DELEGATION_CONTRACT_MARKERS)


def fresh_eye_satisfaction_status(text: str) -> str | None:
    lines = text.splitlines()
    for index, raw in enumerate(lines):
        lowered = raw.strip().lower()
        if "fresh-eye satisfaction" not in lowered and "fresh-eye satisfaction" not in lowered.replace("_", "-"):
            continue
        if ":" in lowered:
            return lowered.split(":", 1)[1].strip()
        section_lines: list[str] = []
        for following in lines[index + 1 :]:
            stripped = following.strip()
            if stripped.startswith("## "):
                break
            if stripped:
                section_lines.append(stripped.lower())
                if len(section_lines) >= 3:
                    break
        return " ".join(section_lines)
    return None


def validate_premortem_artifact(path: Path, *, repo_has_delegation_contract: bool) -> None:
    text = path.read_text(encoding="utf-8")
    status = fresh_eye_satisfaction_status(text)
    status_lowered = status.lower() if status is not None else ""
    if repo_has_delegation_contract:
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in status_lowered:
                raise ValidationError(
                    f"{path}: premortem artifact must not treat missing explicit subagent delegation "
                    "as the canonical blocker; honor repo `Subagent Delegation` instructions, then cite "
                    "the concrete spawn-tool refusal, missing tool surface, or exhausted host budget if "
                    "delegation is still blocked"
                )
    if status_lowered and "blocked" in status_lowered and "parent-delegated" not in status_lowered:
        text_lowered = text.lower()
        if "host signal:" not in text_lowered and "tool signal:" not in text_lowered:
            raise ValidationError(
                f"{path}: blocked premortem fresh-eye satisfaction must cite `host signal:` or `tool signal:`"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to changed paths.")
    parser.add_argument("--all", action="store_true", help="Validate every checked premortem artifact.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = args.paths if args.paths is not None else changed_paths(repo_root)
    artifacts = candidate_paths(repo_root, paths, all_artifacts=args.all)
    repo_has_delegation_contract = has_repo_delegation_contract(repo_root)
    for artifact in artifacts:
        validate_premortem_artifact(artifact, repo_has_delegation_contract=repo_has_delegation_contract)
    print(f"Validated {len(artifacts)} premortem artifact(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
