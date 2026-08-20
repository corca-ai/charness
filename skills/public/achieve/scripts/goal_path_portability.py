"""Classify absolute paths in goal prose at the portability boundary.

An absolute path is not one fact.  In a goal it can be an executable checkout
root, a historical evidence locator, or an ambiguous reference whose intent is
not established.  The old string-scan shape collapsed those cases and either
missed executable roots or made harmless historical records fail.

This module deliberately owns only the pure classification contract.  It does
not inspect the host filesystem: a path that happens to exist on this machine
can still be stale on the machine that will activate the goal.  A consuming
readiness gate can use :func:`check_goal_path_portability` and render its
structured result at the final decision boundary.

Blind class: lexical context cannot prove that a command will really execute.
Executable or ambiguous checkout-root references therefore need an explicit
``Path portability disposition:`` with a substantive reason.  Intentional
historical evidence is classified separately and does not fail a goal merely
because it mentions an old host path.
"""

import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable

# These are checkout-container names, not generic absolute-path components.
# Keeping this list narrow is what prevents /tmp fixtures and /usr/bin tools
# from becoming portability findings.
DEFAULT_CHECKOUT_ROOT_MARKERS = frozenset(
    {
        "checkouts",
        "checkout",
        "code",
        "codes",
        "dev",
        "development",
        "project",
        "projects",
        "repo",
        "repos",
        "src",
        "workspace",
        "workspaces",
        "worktree",
        "worktrees",
    }
)

EVIDENCE_SECTIONS = frozenset(
    {
        "auto-retro",
        "context sources",
        "final verification",
        "off-goal findings",
        "plan critique findings",
        "slice log",
    }
)

EXECUTION_SECTIONS = frozenset(
    {
        "active operating frame",
        "agent verification plan",
        "boundaries",
        "closeout binding plan",
        "coordination cues",
        "goal",
        "slice plan",
        "user acceptance",
    }
)

_UNIX_PATH = re.compile(
    r"(?<![\w:])/(?=[^\s`\"'<>()[\]{};,]+)"
    r"(?:[^/\s`\"'<>()[\]{};,]+/)*[^/\s`\"'<>()[\]{};,]+"
)
_WINDOWS_PATH = re.compile(
    r"(?<![\w])[A-Za-z]:[\\/]"
    r"(?:[^\\/\s`\"'<>()[\]{};,]+[\\/])*"
    r"[^\\/\s`\"'<>()[\]{};,]+"
)
_H2 = re.compile(r"^##\s+(.+?)[ \t]*$", re.MULTILINE)

_STRONG_EVIDENCE = re.compile(
    r"\b(?:historical|history|evidence|observed|reproduction|reproduced|"
    r"captured|recorded|previous|prior|stale|absent|non[- ]claim|not\s+"
    r"(?:run|executed|used)|was\s+(?:run|executed|absent)|source\s+read)\b",
    re.IGNORECASE,
)
_FUTURE_EXECUTION = re.compile(
    r"\b(?:will|shall|must|should|next|to)\s+(?:run|execute|invoke|use|open|read|write)\b",
    re.IGNORECASE,
)
_EXECUTION_MARKER = re.compile(
    r"\b(?:run(?:s|ning)?|execute(?:s|d)?|invoke|call|open|read|write|cd|"
    r"python(?:3(?:\.\d+)?)?|bash|sh|pytest|charness|git)\b|"
    r"--(?:cwd|goal-path|path|repo-root|worktree)\b|"
    r"\b(?:checkout|working)\s+(?:root|tree)\b",
    re.IGNORECASE,
)

_DISPOSITION_LABEL = re.compile(
    r"^\s*(?:[-*>]\s*)?"
    r"(?:path\s+portability(?:\s+disposition)?|"
    r"host[- ]path\s+disposition|"
    r"absolute\s+checkout[- ]path\s+disposition)\s*:\s*(?P<value>.+?)\s*$",
    re.IGNORECASE,
)
_DISPOSITION_STATUSES = (
    "intentional evidence",
    "historical evidence",
    "machine-bound",
    "host-bound",
    "not applicable",
    "rewritten",
    "portable",
    "accepted",
    "n/a",
)
_PLACEHOLDER = re.compile(r"^(?:todo|tbd|fixme|<[^>]+>|fill(?:\s+me)?\s+in)$", re.IGNORECASE)


@dataclass(frozen=True)
class PathReference:
    """One absolute path and the context used to classify it."""

    path: str
    line: int
    section: str | None
    kind: str
    reason: str


@dataclass(frozen=True)
class PortabilityDisposition:
    """The explicit author decision, if the goal contains one."""

    present: bool
    valid: bool
    status: str | None
    reason: str | None
    line: int | None
    raw: str | None


def _normalise_section(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _normalise_path(value: str) -> str:
    return value.rstrip(".,;:)]}>")


def _path_parts(path: str) -> tuple[str, ...]:
    return tuple(part.lower() for part in re.split(r"[\\/]", path) if part)


def is_checkout_root(path: str, *, markers: Iterable[str] | None = None) -> bool:
    """Return whether ``path`` resembles an absolute checkout-root reference."""

    marker_set = {str(marker).strip().lower() for marker in (markers or DEFAULT_CHECKOUT_ROOT_MARKERS)}
    parts = _path_parts(path)
    # A marker must have a repository-looking child after it.  This keeps a
    # bare /src or /tmp from becoming a host-path finding while matching both
    # /home/user/codes/repo and C:\\Users\\user\\worktrees\\repo.
    return any(
        part in marker_set and index < len(parts) - 1
        for index, part in enumerate(parts)
    )


def _absolute_paths(line: str) -> list[str]:
    values = [_normalise_path(match.group(0)) for match in _UNIX_PATH.finditer(line)]
    values.extend(_normalise_path(match.group(0)) for match in _WINDOWS_PATH.finditer(line))
    # A Windows path can also be seen by the Unix expression after its drive
    # prefix; preserve order and remove that duplicate representation.
    return list(dict.fromkeys(value for value in values if value not in {"/", "//"}))


def _classify(path: str, *, line: str, section: str | None) -> tuple[str, str]:
    section_key = _normalise_section(section or "")
    strong_evidence = bool(_STRONG_EVIDENCE.search(line))
    future_execution = bool(_FUTURE_EXECUTION.search(line))
    execution_marker = bool(_EXECUTION_MARKER.search(line))

    if strong_evidence and not future_execution:
        return "intentional-evidence", "historical or captured evidence context"
    if section_key in EVIDENCE_SECTIONS and not future_execution and not execution_marker:
        return "intentional-evidence", f"path appears in the `{section}` evidence section"
    if execution_marker or section_key in EXECUTION_SECTIONS:
        return "executable", "checkout-root reference appears in an execution-bearing context"
    return "ambiguous", "checkout-root reference has no explicit execution or evidence context"


def _parse_disposition(lines: list[str]) -> PortabilityDisposition:
    for line_number, line in enumerate(lines, start=1):
        match = _DISPOSITION_LABEL.match(line)
        if match is None:
            continue
        raw = match.group("value").strip()
        lowered = raw.lower()
        status = next(
            (candidate for candidate in _DISPOSITION_STATUSES if lowered == candidate or lowered.startswith(candidate + " ") or lowered.startswith(candidate + " —") or lowered.startswith(candidate + " -") or lowered.startswith(candidate + ":")),
            None,
        )
        if status is None:
            return PortabilityDisposition(True, False, None, raw, line_number, raw)
        remainder = raw[len(status) :].lstrip(" \t:-—")
        valid = bool(remainder) and not _PLACEHOLDER.fullmatch(remainder.strip())
        return PortabilityDisposition(True, valid, status, remainder or None, line_number, raw)
    return PortabilityDisposition(False, False, None, None, None, None)


def inspect_goal_paths(
    text: str,
    *,
    checkout_markers: Iterable[str] | None = None,
) -> list[PathReference]:
    """Extract and classify absolute checkout-root references from goal text."""

    references: list[PathReference] = []
    section: str | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        heading = _H2.match(line)
        if heading:
            section = heading.group(1).strip()
            continue
        for path in _absolute_paths(line):
            if not is_checkout_root(path, markers=checkout_markers):
                continue
            kind, reason = _classify(path, line=line, section=section)
            references.append(PathReference(path, line_number, section, kind, reason))
    return references


def check_goal_path_portability(
    text: str,
    *,
    checkout_markers: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return the structured portability verdict for one goal artifact.

    Intentional evidence is reported for observability but never enters the
    refusal set.  Executable and ambiguous references share one refusal class:
    they require a valid, substantive disposition, so adding a new execution
    context cannot silently create another fail-open branch.
    """

    lines = text.splitlines()
    disposition = _parse_disposition(lines)
    references = inspect_goal_paths(text, checkout_markers=checkout_markers)
    findings = [reference for reference in references if reference.kind != "intentional-evidence"]
    issues: list[str] = []
    if findings and not disposition.present:
        issues.append(
            "absolute checkout-root reference(s) require an explicit "
            "`Path portability disposition:`"
        )
    elif findings and not disposition.valid:
        issues.append(
            "`Path portability disposition:` is missing a recognized status or "
            "a substantive reason"
        )
    elif disposition.present and not disposition.valid:
        issues.append("`Path portability disposition:` is not a usable disposition")

    return {
        "ok": not issues,
        "issues": issues,
        "references": [asdict(reference) for reference in references],
        "executable_paths": [asdict(reference) for reference in findings],
        "intentional_evidence": [
            asdict(reference)
            for reference in references
            if reference.kind == "intentional-evidence"
        ],
        "disposition": asdict(disposition),
    }


# Compatibility-oriented names keep the pure detector easy to consume while
# leaving one implementation and one verdict owner.
check_goal_paths = check_goal_path_portability


def find_executable_absolute_paths(
    text: str,
    *,
    checkout_markers: Iterable[str] | None = None,
) -> list[PathReference]:
    """Return only references that need a disposition."""

    return [
        reference
        for reference in inspect_goal_paths(text, checkout_markers=checkout_markers)
        if reference.kind != "intentional-evidence"
    ]


__all__ = [
    "DEFAULT_CHECKOUT_ROOT_MARKERS",
    "PathReference",
    "PortabilityDisposition",
    "check_goal_path_portability",
    "check_goal_paths",
    "find_executable_absolute_paths",
    "inspect_goal_paths",
    "is_checkout_root",
]
