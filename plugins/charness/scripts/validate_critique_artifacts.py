#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
is_valid_followup_tail = _artifact_validator.is_valid_followup_tail
run_validation_checks = _artifact_validator.run_validation_checks

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"
STRUCTURED_FINDINGS_HEADING = "## Structured Findings"
STRUCTURED_BINS = frozenset({"act-before-ship", "bundle-anyway", "over-worry", "valid-but-defer"})
STRUCTURED_EVIDENCE = frozenset({"strong", "moderate", "weak", "contested"})
STRUCTURED_ACTIONS = frozenset({"fix", "file-issue", "document", "defer"})
STRUCTURED_REQUIRED_FIELDS = ("bin", "evidence", "ref", "action", "note")
REVIEWER_TIER_HEADING = "## Reviewer Tier Evidence"
REVIEWER_TIER_REQUIRED_FIELDS = (
    "requested tier",
    "requested spawn fields",
    "host exposure state",
    "application state",
)
REVIEWER_TIER_HOST_STATES = frozenset(
    {
        "pending-parent-spawn",
        "requested_fields_sent",
        "metadata-hidden",
        "host-defaulted",
        "unsupported",
        "applied",
    }
)
PACKET_CONSUMED_RE = re.compile(r"(?im)^\s*packet consumed\s*:\s*(?P<path>\S+)")
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


def _structured_findings_lines(text: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == STRUCTURED_FINDINGS_HEADING)
    except StopIteration:
        return []
    section: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        section.append(line)
    return [line for line in section if line.strip().startswith("- ")]


def _parse_structured_finding(raw: str) -> dict[str, str]:
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


def _is_valid_followup_value(value: str) -> bool:
    """Same grammar as `debug` sibling follow-up: identifier or `deferred <anchor>`.

    Delegates to the shared `artifact_validator.is_valid_followup_tail` so the
    follow-up grammar lives in one place (the Closeout Schema Rule in
    `create-skill/references/portable-authoring.md` requires reusing it).
    """
    return is_valid_followup_tail(value.strip().lower())


def validate_structured_findings(path: Path, text: str) -> None:
    bullets = _structured_findings_lines(text)
    if not bullets:
        return
    seen_ids: set[str] = set()
    for index, raw in enumerate(bullets, start=1):
        finding = _parse_structured_finding(raw)
        finding_id = finding.get("id", f"<line {index}>")
        for field in STRUCTURED_REQUIRED_FIELDS:
            if not finding.get(field):
                raise ValidationError(
                    f"{path}: `## Structured Findings` entry {finding_id} missing required field `{field}`"
                )
        if "id" in finding:
            if finding["id"] in seen_ids:
                raise ValidationError(
                    f"{path}: `## Structured Findings` duplicate id `{finding['id']}`"
                )
            seen_ids.add(finding["id"])
        if finding["bin"] not in STRUCTURED_BINS:
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has unknown bin `{finding['bin']}`; "
                f"allowed: {sorted(STRUCTURED_BINS)}"
            )
        if finding["evidence"] not in STRUCTURED_EVIDENCE:
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has unknown evidence `{finding['evidence']}`; "
                f"allowed: {sorted(STRUCTURED_EVIDENCE)}"
            )
        if finding["action"] not in STRUCTURED_ACTIONS:
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has unknown action `{finding['action']}`; "
                f"allowed: {sorted(STRUCTURED_ACTIONS)}"
            )
        followup_value = finding.get("follow-up", "")
        if finding["action"] == "file-issue":
            if not _is_valid_followup_value(followup_value):
                raise ValidationError(
                    f"{path}: `## Structured Findings` entry {finding_id} has `action: file-issue` "
                    "but no parseable `follow-up:` field; record the issue URL or "
                    "`follow-up: deferred <handoff-anchor>` per "
                    "skills/public/critique/references/counterweight-triage.md."
                )
        elif followup_value and not _is_valid_followup_value(followup_value):
            raise ValidationError(
                f"{path}: `## Structured Findings` entry {finding_id} has malformed `follow-up:` value "
                "(bare `deferred` without an anchor)."
            )


def _section_field_map(text: str, heading: str) -> dict[str, str]:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return {}
    fields: dict[str, str] = {}
    for raw in lines[start + 1 :]:
        if raw.startswith("## "):
            break
        stripped = raw.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, _, value = stripped.lstrip("- ").partition(":")
        normalized_key = key.replace("*", "").strip().lower()
        fields[normalized_key] = value.strip().strip("`")
    return fields


def validate_reviewer_tier_evidence(path: Path, text: str) -> None:
    fields = _section_field_map(text, REVIEWER_TIER_HEADING)
    missing = [field for field in REVIEWER_TIER_REQUIRED_FIELDS if not fields.get(field)]
    if missing:
        raise ValidationError(f"{path}: reviewer tier evidence missing fields: {missing}")
    state = fields["host exposure state"]
    if state not in REVIEWER_TIER_HOST_STATES:
        raise ValidationError(
            f"{path}: reviewer tier host exposure state `{state}` must be one of "
            f"{sorted(REVIEWER_TIER_HOST_STATES)}"
        )
    if state == "applied" and not fields["application state"].lower().startswith("host-confirmed:"):
        raise ValidationError(
            f"{path}: reviewer tier evidence may use `applied` only with "
            "`Application state: host-confirmed: <signal>`"
        )


def validate_critique_artifact(
    path: Path, *, repo_has_delegation_contract: bool, require_tier_evidence: bool, collect_all: bool = False
) -> None:
    text = path.read_text(encoding="utf-8")
    status = fresh_eye_satisfaction_status(text)
    status_lowered = status.lower() if status is not None else ""

    def _check_forbidden_blocker_phrases() -> None:
        if not repo_has_delegation_contract:
            return
        for phrase in FORBIDDEN_SUBAGENT_BLOCKER_PHRASES:
            if phrase in status_lowered:
                raise ValidationError(
                    f"{path}: critique artifact must not treat missing explicit subagent delegation "
                    "as the canonical blocker; honor repo `Subagent Delegation` instructions, then cite "
                    "the concrete spawn-tool refusal, missing tool surface, or exhausted host budget if "
                    "delegation is still blocked"
                )

    def _check_blocked_signal_detail() -> None:
        if status_lowered and "blocked" in status_lowered and "parent-delegated" not in status_lowered:
            if not has_blocked_signal_detail(text):
                raise ValidationError(
                    f"{path}: blocked critique fresh-eye satisfaction must cite `host signal:` or `tool signal:`"
                )

    def _check_reviewer_tier_evidence() -> None:
        requires_tier_evidence = require_tier_evidence and (
            "parent-delegated" in status_lowered or PACKET_CONSUMED_RE.search(text)
        )
        if requires_tier_evidence or _section_field_map(text, REVIEWER_TIER_HEADING):
            validate_reviewer_tier_evidence(path, text)

    checks = (
        _check_forbidden_blocker_phrases,
        _check_blocked_signal_detail,
        lambda: validate_structured_findings(path, text),
        _check_reviewer_tier_evidence,
    )
    run_validation_checks(
        checks, collect_all=collect_all, artifact_label="critique artifact", error_cls=ValidationError
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to changed paths.")
    parser.add_argument("--all", action="store_true", help="Validate every checked critique artifact.")
    parser.add_argument(
        "--report-all",
        action="store_true",
        help="Report every rule violation per artifact in one pass instead of failing on the first.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    explicit_paths = args.paths is not None
    paths = [] if args.all else args.paths if explicit_paths else changed_paths(repo_root)
    artifacts = candidate_paths(repo_root, paths, all_artifacts=args.all)
    require_tier_paths = set(paths)
    repo_has_delegation_contract = has_repo_delegation_contract(repo_root)
    for artifact in artifacts:
        relpath = artifact.relative_to(repo_root).as_posix()
        validate_critique_artifact(
            artifact,
            repo_has_delegation_contract=repo_has_delegation_contract,
            require_tier_evidence=explicit_paths or relpath in require_tier_paths,
            collect_all=args.report_all,
        )
    print(f"Validated {len(artifacts)} critique artifact(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
