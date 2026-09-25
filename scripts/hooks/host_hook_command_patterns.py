"""Command-guard pattern tables: parallel window, verdict channel, discard.

Tables live apart from the matching engine (`host_hook_command_guards`)
so each grows under its own length budget. A repository extends these
without forking the guard through `.agents/command-guards.local.yaml`
(`extra_patterns` per guard with id, pattern, reason, overridable, and
`extra_verdict_commands`).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuardPattern:
    id: str
    pattern: str
    reason: str
    overridable: bool = True


PARALLEL_WINDOW = "parallel-window"
VERDICT_CHANNEL = "verdict-channel"
DISCARD_WORKTREE = "discard-worktree"
GUARD_KEYS = (PARALLEL_WINDOW, VERDICT_CHANNEL, DISCARD_WORKTREE)

OVERRIDE_MARKERS = {
    PARALLEL_WINDOW: "window-ok",
    VERDICT_CHANNEL: "verdict-ok",
    DISCARD_WORKTREE: "discard-ok",
}

# A foreground wait on a job that notifies anyway has no override: the
# strictly better alternative (a host background job) always exists.
PARALLEL_WINDOW_PATTERNS: tuple[GuardPattern, ...] = (
    GuardPattern(
        "long-sleep",
        r"(?<![\w-])sleep\s+(?P<seconds>\d+)",
        "a sleep of 5s or more idles the turn; background it",
    ),
    GuardPattern(
        "test-bundle",
        r"(?<![\w-])(?:pytest|python\s+-m\s+pytest|jest|vitest|mocha|go\s+test|cargo\s+test|npm\s+test|npm\s+run\s+(?:test|verify)|ctest)(?![\w-])",
        "a test bundle idles the turn; background it or select one file",
    ),
    GuardPattern(
        "install",
        r"(?<![\w-])(?:pip3?\s+install|npm\s+(?:ci|install)|pnpm\s+install|yarn\s+install|cargo\s+(?:build|fetch)|bundle\s+install)(?![\w-])",
        "an install idles the turn; background it",
    ),
    GuardPattern(
        "lint-build-gate",
        r"(?<![\w-])(?:tsc(?:\s+-p\b|\b)|make\b|gradle\b|mvn\b|ruff\s+check|eslint\b|run-quality\.sh|check-python-lint\.sh)(?![\w-])",
        "a lint/build gate idles the turn; background it",
    ),
    GuardPattern(
        "foreground-lane-launch",
        r"(?<![\w-])charness\s+task\s+run\b(?![\w-])(?!.*--detach)",
        "a foreground lane launch idles the turn; launch with --detach",
    ),
    GuardPattern(
        "foreground-task-wait",
        r"(?<![\w-])charness\s+task\s+wait\b",
        "a foreground wait never notifies better than a host background job",
        overridable=False,
    ),
)

VERDICT_COMMANDS: tuple[str, ...] = (
    "pytest",
    "jest",
    "vitest",
    "mocha",
    "go test",
    "cargo test",
    "npm test",
    "git apply",
    "git merge",
    "git rebase",
    "git push",
    "charness task",
)

FIXED_WIDTH_PATTERNS: tuple[GuardPattern, ...] = (
    GuardPattern(
        "fixed-width-cut",
        r"(?<![\w-])(?:cut\s+-[cb]\S*|head\s+-c\S*|fold\s+-[sw]\S*)",
        "fixed-width truncation cuts off exactly the verdict fields",
    ),
)

DISCARD_PATTERNS: tuple[GuardPattern, ...] = (
    GuardPattern(
        "checkout-path",
        r"(?<![\w-])git\s+checkout\s+(?:--(?=\s|$)|\S+\s+--(?=\s|$)|\.(?=\s|/|$))",
        "restoring a path destroys uncommitted work; name what and why",
    ),
    GuardPattern(
        "restore-path",
        r"(?<![\w-])git\s+restore\b(?![\w-])(?!\s+--staged\s*(?:$|#))",
        "restoring destroys uncommitted work; name what and why",
    ),
    GuardPattern(
        "reset-hard",
        r"(?<![\w-])git\s+reset\s+--(?:hard|merge)(?![\w-])",
        "a hard reset destroys uncommitted work; name what and why",
    ),
    GuardPattern(
        "clean-force",
        r"(?<![\w-])git\s+clean\b(?![\w-])(?=.*(?:-[a-z]*f|--force))",
        "a forced clean destroys untracked work; name what and why",
    ),
    GuardPattern(
        "stash-drop",
        r"(?<![\w-])git\s+stash\s+(?:drop|clear)(?![\w-])",
        "dropping a stash destroys shelved work; name what and why",
    ),
    GuardPattern(
        "worktree-force-remove",
        r"(?<![\w-])git\s+worktree\s+remove\b(?![\w-])(?=.*--force)",
        "a forced worktree removal destroys its checkout; name what and why",
    ),
)
