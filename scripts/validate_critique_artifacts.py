#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"
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
SIGNAL_HEADINGS = ("host signal", "tool signal")
PLACEHOLDER_VALUES = {"", "todo", "tbd", "missing", "n/a", "na", "blocked"}


class ValidationError(Exception):
    pass


def _git_paths(repo_root: Path, args: list[str]) -> list[str]:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        message = (
            "critique artifact changed-path discovery failed; "
            f"command: {' '.join(command)}; exit_code: {result.returncode}"
        )
        if detail:
            message = f"{message}; output: {detail}"
        raise ValidationError(message)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_paths(repo_root: Path) -> list[str]:
    paths = set(_git_paths(repo_root, ["diff", "--name-only", "HEAD", "--"]))
    paths.update(_git_paths(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(paths)


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    if all_artifacts:
        return sorted((repo_root / CRITIQUE_ARTIFACT_PREFIX).glob("*.md"))
    candidates: list[Path] = []
    for relpath in paths:
        if relpath.startswith(CRITIQUE_ARTIFACT_PREFIX) and relpath.endswith(".md"):
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


def _substantive_signal(value: str) -> bool:
    signal_text = value.strip().strip("-*`._:;,#[](){}<>!/?\\|\"' ")
    normalized = " ".join(value.strip().lower().split())
    return (
        bool(signal_text)
        and any(character.isalnum() for character in signal_text)
        and normalized not in PLACEHOLDER_VALUES
        and not normalized.startswith("missing ")
    )


def has_blocked_signal_detail(text: str) -> bool:
    lines = text.splitlines()
    for raw in lines:
        lowered = raw.strip().lower().lstrip("-*").strip()
        for heading in SIGNAL_HEADINGS:
            marker = f"{heading}:"
            if lowered.startswith(marker) and _substantive_signal(lowered.removeprefix(marker)):
                return True
    for index, raw in enumerate(lines):
        lowered = raw.strip().lower().rstrip(":")
        if lowered.startswith("#"):
            lowered = lowered.lstrip("#").strip()
        if lowered not in SIGNAL_HEADINGS:
            continue
        for following in lines[index + 1 :]:
            stripped = following.strip()
            if stripped.startswith("## "):
                break
            if _substantive_signal(stripped):
                return True
    return False


def validate_critique_artifact(path: Path, *, repo_has_delegation_contract: bool) -> None:
    text = path.read_text(encoding="utf-8")
    status = fresh_eye_satisfaction_status(text)
    status_lowered = status.lower() if status is not None else ""
    if repo_has_delegation_contract:
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in status_lowered:
                raise ValidationError(
                    f"{path}: critique artifact must not treat missing explicit subagent delegation "
                    "as the canonical blocker; honor repo `Subagent Delegation` instructions, then cite "
                    "the concrete spawn-tool refusal, missing tool surface, or exhausted host budget if "
                    "delegation is still blocked"
                )
    if status_lowered and "blocked" in status_lowered and "parent-delegated" not in status_lowered:
        if not has_blocked_signal_detail(text):
            raise ValidationError(
                f"{path}: blocked critique fresh-eye satisfaction must cite `host signal:` or `tool signal:`"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to changed paths.")
    parser.add_argument("--all", action="store_true", help="Validate every checked critique artifact.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = [] if args.all else args.paths if args.paths is not None else changed_paths(repo_root)
    artifacts = candidate_paths(repo_root, paths, all_artifacts=args.all)
    repo_has_delegation_contract = has_repo_delegation_contract(repo_root)
    for artifact in artifacts:
        validate_critique_artifact(artifact, repo_has_delegation_contract=repo_has_delegation_contract)
    print(f"Validated {len(artifacts)} critique artifact(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
