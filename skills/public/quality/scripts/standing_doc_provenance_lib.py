"""Scan standing/contract docs for drifted provenance placement.

Generalizes the skill-package anchor gate (`skill_text_quality_lib`:
`ISSUE_ANCHOR_RE`, `DATED_INCIDENT_RE`) to standing *docs* with an explicit
standing-vs-tracking allowlist. The provenance-placement policy
(`docs/conventions/provenance-placement.md`) is the rule this enforces: a
standing-rule doc states the timeless rule; provenance is a terse trailing
`(#NNN)` only when load-bearing, else a link to the owning record artifact —
never stacked dates / incident-names in rule prose.

A rule line of a configured standing doc is flagged when it carries:
  - an ISO date `20\\d{2}-\\d{2}-\\d{2}` (`standing_doc_date`), OR
  - two or more issue refs (`standing_doc_multiple_issue_refs`), OR
  - a dated-incident phrase (`standing_doc_dated_incident`).
A single load-bearing trailing `(#NNN)` with no date does NOT flag. Fenced code
blocks and lines carrying the configured inline-allow marker are excluded.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import skill_text_quality_lib as tqlib  # noqa: E402
from git_inventory_lib import visible_repo_files  # noqa: E402

ISO_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")


def _excerpt(line: str) -> str:
    return line.strip()[:160]


def _strip_sanctioned_spans(line: str) -> str:
    """Remove spans where a date/ref is sanctioned placement, not rule-prose
    diary noise: inline-code examples (a backticked anchor or a `<date> lesson`)
    and markdown link targets — a link to the owning record artifact
    (`](.../<date>-foo.md)`) is exactly the placement the policy prescribes,
    so its date must not flag. Link *text* is kept so a stacked-ref pair in the
    visible text still counts."""
    return _LINK_TARGET_RE.sub("]", _INLINE_CODE_RE.sub("``", line))


def _strip_path_tokens(text: str) -> str:
    """Drop whitespace tokens that contain a path/URL separator so a raw
    record-path date (`charness-artifacts/<record>/2026-06-07-x.md`) — the
    sanctioned record-layer pointer — does not flag, while a free-prose date
    (`added 2026-06-07`) still does."""
    return " ".join(token for token in text.split() if "/" not in token)


def _resolve_paths(repo_root: Path, standing_docs: list[str], tracking_allowlist: list[str]) -> list[Path]:
    """Expand `standing_docs` globs under repo_root, minus `tracking_allowlist`.

    Allowlist entries are matched both as globs and as posix-relative prefixes so
    a consuming repo can allowlist a single file or a whole tree.
    """
    # Gitignore-aware file source: never check provenance of an ignored/untracked
    # doc. `visible_repo_files` returns the git-visible set, or None when git
    # listing is unavailable (e.g. a non-git fixture) — in which case the raw glob
    # stands. This keeps the config-driven glob from becoming a blind repo-wide
    # scan (inventory-gitignore-scan-hygiene).
    visible = visible_repo_files(repo_root, require_git=False, context="standing-doc provenance scan")
    allowed: set[Path] = set()
    for pattern in tracking_allowlist:
        for candidate in repo_root.glob(pattern):
            resolved_candidate = candidate.resolve()
            if visible is None or resolved_candidate in visible:
                allowed.add(resolved_candidate)
    selected: dict[Path, None] = {}
    for pattern in standing_docs:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if visible is not None and resolved not in visible:
                continue
            if resolved in allowed:
                continue
            rel = resolved.relative_to(repo_root.resolve()).as_posix()
            if any(rel == a or rel.startswith(f"{a.rstrip('/')}/") for a in tracking_allowlist):
                continue
            selected[resolved] = None
    return list(selected)


def _line_findings(line: str) -> list[str]:
    base = _strip_sanctioned_spans(line)
    date_text = _strip_path_tokens(base)
    heuristics: list[str] = []
    if ISO_DATE_RE.search(date_text):
        heuristics.append("standing_doc_date")
    if len(tqlib.ISSUE_ANCHOR_RE.findall(base)) >= 2:
        heuristics.append("standing_doc_multiple_issue_refs")
    if tqlib.DATED_INCIDENT_RE.search(date_text):
        heuristics.append("standing_doc_dated_incident")
    return heuristics


def scan_standing_doc(repo_root: Path, path: Path, inline_allow_marker: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return findings
    in_fence = False
    for index, line in enumerate(lines, start=1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if inline_allow_marker and inline_allow_marker in line:
            continue
        heuristics = _line_findings(line)
        if not heuristics:
            continue
        findings.append(
            {
                "path": str(path.resolve().relative_to(repo_root.resolve())),
                "line": index,
                "heuristics": heuristics,
                "excerpt": _excerpt(line),
            }
        )
    return findings


def scan_standing_docs(repo_root: Path, config: dict[str, object]) -> dict[str, object]:
    """Run the provenance-placement scan over the configured standing docs.

    `config` is the validated `standing_doc_provenance` adapter block. Returns
    `{scanned, findings, inert}`; `inert` is True when `standing_docs` is empty
    (the stack-neutral default), so callers can distinguish "opted out" from
    "opted in and clean".
    """
    standing_docs = list(config.get("standing_docs") or [])
    tracking_allowlist = list(config.get("tracking_allowlist") or [])
    inline_allow_marker = str(config.get("inline_allow_marker") or "")
    if not standing_docs:
        return {"scanned": [], "findings": [], "inert": True}
    paths = _resolve_paths(repo_root, standing_docs, tracking_allowlist)
    findings: list[dict[str, object]] = []
    scanned: list[str] = []
    for path in sorted(paths):
        scanned.append(str(path.resolve().relative_to(repo_root.resolve())))
        findings.extend(scan_standing_doc(repo_root, path, inline_allow_marker))
    findings.sort(key=lambda item: (item["path"], item["line"]))
    return {"scanned": sorted(scanned), "findings": findings, "inert": False}
