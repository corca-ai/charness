#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

IDEATION_ARTIFACT_PREFIX = "charness-artifacts/ideation/"
STRUCTURED_QUESTIONS_HEADING = "## Structured Questions"
STRUCTURED_URGENCY = frozenset({"must-resolve", "probe-in-impl", "defer"})
STRUCTURED_ACTIONS = frozenset({"spec", "impl", "hold"})
STRUCTURED_REQUIRED_FIELDS = ("urgency", "depends-on", "action", "note")


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
            "ideation artifact changed-path discovery failed; "
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
        return sorted((repo_root / IDEATION_ARTIFACT_PREFIX).glob("*.md"))
    candidates: list[Path] = []
    for relpath in paths:
        if relpath.startswith(IDEATION_ARTIFACT_PREFIX) and relpath.endswith(".md"):
            path = repo_root / relpath
            if path.is_file():
                candidates.append(path)
    return sorted(candidates)


def _structured_questions_lines(text: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == STRUCTURED_QUESTIONS_HEADING)
    except StopIteration:
        return []
    section: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        section.append(line)
    return [line for line in section if line.strip().startswith("- ")]


def _parse_structured_question(raw: str) -> dict[str, str]:
    body = raw.strip().lstrip("- ").strip()
    parts = [chunk.strip() for chunk in body.split("|") if chunk.strip()]
    if not parts:
        return {}
    fields: dict[str, str] = {}
    head = parts[0]
    if ":" not in head:
        fields["id"] = head
        rest = parts[1:]
    else:
        rest = parts
    for chunk in rest:
        if ":" not in chunk:
            continue
        key, _, value = chunk.partition(":")
        fields[key.strip().lower()] = value.strip()
    return fields


def validate_structured_questions(path: Path, text: str) -> None:
    bullets = _structured_questions_lines(text)
    if not bullets:
        return
    seen_ids: set[str] = set()
    for index, raw in enumerate(bullets, start=1):
        question = _parse_structured_question(raw)
        question_id = question.get("id", f"<line {index}>")
        for field in STRUCTURED_REQUIRED_FIELDS:
            if not question.get(field):
                raise ValidationError(
                    f"{path}: `## Structured Questions` entry {question_id} missing required field `{field}`"
                )
        if "id" in question:
            if question["id"] in seen_ids:
                raise ValidationError(
                    f"{path}: `## Structured Questions` duplicate id `{question['id']}`"
                )
            seen_ids.add(question["id"])
        if question["urgency"] not in STRUCTURED_URGENCY:
            raise ValidationError(
                f"{path}: `## Structured Questions` entry {question_id} has unknown urgency "
                f"`{question['urgency']}`; allowed: {sorted(STRUCTURED_URGENCY)}"
            )
        if question["action"] not in STRUCTURED_ACTIONS:
            raise ValidationError(
                f"{path}: `## Structured Questions` entry {question_id} has unknown action "
                f"`{question['action']}`; allowed: {sorted(STRUCTURED_ACTIONS)}"
            )


def validate_ideation_artifact(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    validate_structured_questions(path, text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to changed paths.")
    parser.add_argument("--all", action="store_true", help="Validate every checked ideation artifact.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = [] if args.all else args.paths if args.paths is not None else changed_paths(repo_root)
    artifacts = candidate_paths(repo_root, paths, all_artifacts=args.all)
    for artifact in artifacts:
        validate_ideation_artifact(artifact)
    print(f"Validated {len(artifacts)} ideation artifact(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
