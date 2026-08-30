#!/usr/bin/env python3
"""Classify the T-signal (durable improvement link) for the most recent commit.

Inspects ``git diff --name-status HEAD~1..HEAD`` plus the HEAD commit message
and applies a rule catalog to determine whether the slice produced a durable
improvement to memory, gates, conventions, skills, deferred decisions, debug
RCA, or closed a GitHub issue. One strongest-confidence rule wins; ties are
broken by ``rule_id`` alphabetical order for determinism.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

CONFIDENCE_RANK = {"low": 1, "medium": 2, "high": 3}

RETRO_LESSON_RE = re.compile(r"^charness-artifacts/retro/\d{4}-\d{2}-\d{2}-.*-session\.md$")
DEBUG_RCA_RE = re.compile(r"^charness-artifacts/debug/\d{4}-\d{2}-\d{2}-.*\.md$")
GATE_SCRIPT_RE = re.compile(r"^scripts/(check|validate)_[A-Za-z0-9_]+\.py$")
QUALITY_RUNNER_PATH = "scripts/run-quality.sh"
CONVENTION_DOC_PATHS = frozenset(
    {
        "docs/operating-contract.md",
        "docs/implementation-discipline.md",
        "docs/authoring-preflight.md",
        "docs/parallel-execution.md",
        "docs/validator-timing-layers.md",
        "docs/surface-driven-adapter-triggers.md",
        "docs/provenance-placement.md",
    }
)
SKILL_FILE_RE = re.compile(r"^skills/public/[^/]+/(SKILL\.md|references/.+)$")
DEFERRED_DECISIONS_PATH = "docs/deferred-decisions.md"
ISSUE_CLOSE_RE = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?)\s+#\d+\b", re.IGNORECASE)
DEFERRED_DECISION_HEADING_RE = re.compile(r"^## (D\d+)\b")


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def _commit_metadata_snapshot(repo_root: Path, head_sha: str | None) -> tuple[str, str | None, str] | None:
    target = head_sha or "HEAD"
    result = _run_git(repo_root, "log", "-1", "--format=%H%x00%P%x00%B%x00", target)
    if result.returncode != 0:
        return None
    fields = result.stdout.split("\0", 3)
    if len(fields) < 3:
        return None
    resolved_head, parents, message = fields[:3]
    if not resolved_head:
        return None
    parent_sha = parents.split(maxsplit=1)[0] if parents else None
    return resolved_head, parent_sha, message


def _missing_parent_reason(repo_root: Path) -> str:
    shallow_result = _run_git(repo_root, "rev-parse", "--is-shallow-repository")
    if shallow_result.returncode == 0 and shallow_result.stdout.strip() == "true":
        return "shallow_clone"
    return "no_parent"


def _parse_name_status(stdout: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0][:1]
        path = parts[-1]
        entries.append((status, path))
    return entries


def _diff_kind_for(status: str) -> str:
    if status == "A":
        return "added"
    if status == "D":
        return "removed"
    return "modified"


def _filter(entries: Iterable[tuple[str, str]], *, statuses: set[str] | None, predicate) -> list[tuple[str, str]]:
    matched: list[tuple[str, str]] = []
    for status, path in entries:
        if statuses is not None and status not in statuses:
            continue
        if predicate(path):
            matched.append((status, path))
    return matched


def _deferred_decision_ids(repo_root: Path, ref: str) -> set[str]:
    show_result = _run_git(repo_root, "show", f"{ref}:{DEFERRED_DECISIONS_PATH}")
    if show_result.returncode != 0:
        return set()
    ids: set[str] = set()
    for line in show_result.stdout.splitlines():
        match = DEFERRED_DECISION_HEADING_RE.match(line)
        if match:
            ids.add(match.group(1))
    return ids


def _deferred_decision_added(repo_root: Path, parent_sha: str, head_sha: str) -> bool:
    before = _deferred_decision_ids(repo_root, parent_sha)
    after = _deferred_decision_ids(repo_root, head_sha)
    return bool(after - before)


def _candidate(rule_id: str, t_status: str, confidence: str, diff_kind: str, paths: list[str], head_sha: str) -> dict:
    return {
        "rule_id": rule_id,
        "t_status": t_status,
        "confidence": confidence,
        "matched_paths": sorted(set(paths)),
        "commit_refs": [head_sha],
        "diff_kind": diff_kind,
    }


DIFF_RULES = (
    {
        "rule_id": "retro-lesson-path-added",
        "t_status": "memory_lesson_added",
        "confidence": "high",
        "diff_kind": "added",
        "statuses": {"A"},
        "predicate": RETRO_LESSON_RE.match,
    },
    {
        "rule_id": "debug-rca-path-added",
        "t_status": "debug_rca_added",
        "confidence": "high",
        "diff_kind": "added",
        "statuses": {"A"},
        "predicate": DEBUG_RCA_RE.match,
    },
    {
        "rule_id": "gate-script-added",
        "t_status": "gate_added",
        "confidence": "high",
        "diff_kind": "added",
        "statuses": {"A"},
        "predicate": GATE_SCRIPT_RE.match,
    },
    {
        "rule_id": "gate-script-modified",
        "t_status": "gate_modified",
        "confidence": "low",
        "diff_kind": "modified",
        "statuses": {"M"},
        "predicate": GATE_SCRIPT_RE.match,
    },
    {
        "rule_id": "quality-runner-modified",
        "t_status": "quality_runner_modified",
        "confidence": "medium",
        "diff_kind": None,
        "statuses": None,
        "predicate": lambda p: p == QUALITY_RUNNER_PATH,
    },
    {
        "rule_id": "convention-doc-modified",
        "t_status": "convention_modified",
        "confidence": "medium",
        "diff_kind": None,
        "statuses": None,
        "predicate": lambda p: p in CONVENTION_DOC_PATHS,
    },
    {
        "rule_id": "skill-or-reference-modified",
        "t_status": "skill_or_reference_modified",
        "confidence": "low",
        "diff_kind": None,
        "statuses": None,
        "predicate": SKILL_FILE_RE.match,
    },
)


def _diff_rule_candidate(rule: dict, entries: list[tuple[str, str]], head_sha: str) -> dict | None:
    matched = _filter(entries, statuses=rule["statuses"], predicate=rule["predicate"])
    if not matched:
        return None
    diff_kind = rule["diff_kind"] or _diff_kind_for(matched[0][0])
    return _candidate(
        rule["rule_id"],
        rule["t_status"],
        rule["confidence"],
        diff_kind,
        [path for _, path in matched],
        head_sha,
    )


def _collect_candidates(
    repo_root: Path,
    parent_sha: str,
    head_sha: str,
    entries: list[tuple[str, str]],
    head_message: str,
) -> list[dict]:
    candidates: list[dict] = []
    for rule in DIFF_RULES:
        candidate = _diff_rule_candidate(rule, entries, head_sha)
        if candidate is not None:
            candidates.append(candidate)

    if any(path == DEFERRED_DECISIONS_PATH for _, path in entries) and _deferred_decision_added(
        repo_root, parent_sha, head_sha
    ):
        candidates.append(
            _candidate(
                "deferred-decision-added",
                "deferred_decision_added",
                "medium",
                "modified",
                [DEFERRED_DECISIONS_PATH],
                head_sha,
            )
        )

    if ISSUE_CLOSE_RE.search(head_message):
        candidates.append(
            {
                "rule_id": "issue-closed",
                "t_status": "issue_closed",
                "confidence": "high",
                "matched_paths": ["<commit-message>"],
                "commit_refs": [head_sha],
                "diff_kind": "modified",
            }
        )

    return candidates


def _select_strongest(candidates: list[dict]) -> dict | None:
    # Spec-fixed tie-break: highest confidence first, then rule_id alphabetical for
    # determinism. Consequence: when a retro-lesson commit also says "Closes #N",
    # both rules fire at `high` and `issue-closed` sorts before
    # `retro-lesson-path-added`, so the diff-side signal loses to the
    # commit-message signal. Revisit only if reporting demands the substantive
    # rule win the trailer-style rule.
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda c: (-CONFIDENCE_RANK[c["confidence"]], c["rule_id"]),
    )[0]


def _empty_result(skipped_reason: str | None) -> dict:
    return {
        "t_status": "none",
        "rule_id": None,
        "confidence": None,
        "matched_paths": None,
        "commit_refs": None,
        "diff_kind": None,
        "skipped_reason": skipped_reason,
    }


def classify_t_signal(repo_root: Path, head_sha: str | None = None) -> dict:
    if not (repo_root / ".git").exists():
        return _empty_result("diff_unavailable")

    metadata = _commit_metadata_snapshot(repo_root, head_sha)
    if metadata is None:
        if head_sha is None:
            return _empty_result("diff_unavailable")
        return _empty_result(_missing_parent_reason(repo_root))

    resolved_head, parent_sha, head_message = metadata
    head = head_sha or resolved_head
    if parent_sha is None:
        return _empty_result(_missing_parent_reason(repo_root))

    diff_result = _run_git(repo_root, "diff", "--name-status", f"{parent_sha}..{head}")
    if diff_result.returncode != 0:
        return _empty_result("diff_unavailable")

    entries = _parse_name_status(diff_result.stdout)
    candidates = _collect_candidates(repo_root, parent_sha, head, entries, head_message)
    winner = _select_strongest(candidates)
    if winner is None:
        return {
            "t_status": "none",
            "rule_id": None,
            "confidence": None,
            "matched_paths": None,
            "commit_refs": None,
            "diff_kind": None,
            "skipped_reason": None,
        }

    return {
        "t_status": winner["t_status"],
        "rule_id": winner["rule_id"],
        "confidence": winner["confidence"],
        "matched_paths": winner["matched_paths"],
        "commit_refs": winner["commit_refs"],
        "diff_kind": winner["diff_kind"],
        "skipped_reason": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root_from_script(__file__))
    parser.add_argument("--head-sha", type=str)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    result = classify_t_signal(repo_root, head_sha=args.head_sha)
    emit_yaml(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
