#!/usr/bin/env python3
"""Residue detection: did a durable record already decline to close this issue?

STRUCTURAL SIGNALS ONLY. NO PROSE MATCHING. This module reads exactly one thing out of a
durable record: an explicit, typed `Premise-residue:` marker naming issue anchors. It does
not guess a decline from English or Korean wording, and the removal of that guessing is the
whole design, not a simplification.

WHY, IN THE ORDER THE EVIDENCE ARRIVED. A first version carried a hand-written vocabulary
of decline phrases -- `NOT closed`, `remains open`, `carried`, `보류` -- measured off this
repo's own goal artifacts. Three things were wrong with it, and each is worse than the last:

1. It was repo-specific hardcoding inside a PORTABLE public skill. A consuming repo writes
   its records with different words, gets no match, and is told the issue is closable. The
   failure is silent and points the one direction this tool must never drift.
2. It was language-specific. Two languages were enumerated because two happened to be in
   front of the author; a third would fail closed-looking-green.
3. Worst: the thresholds were fitted. A proximity window went 160 chars, then two tiers at
   160 and 40, then a nearest-anchor rule -- and the clean count on this repo's 22 open
   issues went 1, then 3, then 7, then 10. Each step was tuned by looking at that
   distribution. No principle produced those numbers; the backlog they were measured on
   did. A verdict surface whose constants were fitted to its own test set is precisely the
   defect this goal family exists to remove, arriving inside the tool built to remove it.

WHAT REPLACED IT. A marker a record AUTHOR writes deliberately:

    Premise-residue: <issue anchor> — part 2 (the automated recount helper) is unbuilt.

Nothing infers it, so nothing can infer it wrongly. A record that does not carry the marker
contributes no residue, and that is reported rather than assumed -- `classify` states that
the record channel ran and found no typed marker, which is a different sentence from "no
record declined". The body-side signals (an enumerated multi-part ask, unchecked task
items) live in `recount_premise_lib` and are structural for the same reason.

THE COST, STATED PLAINLY. Historical records carry no marker, so the record channel is
empty for them until authors start writing it. The instance this whole tool was built from
is still caught -- by its body's two-part enumerated ask, a structural signal -- but an
issue whose only residue is a sentence in an old goal artifact will now read as having no
record residue. That is a real loss of recall, accepted deliberately: a channel that
honestly reports "no typed marker found" is worth more than one that guesses from prose and
is wrong in a direction nobody can see.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

GIT_TIMEOUT_SECONDS = 10

# Durable-record roots. `charness-artifacts/` is taken WHOLE rather than as a hand-listed
# set of subdirectories: an earlier hand-listed version missed `quality/`, and there is no
# principle that admits `audit/` and excludes `debug/`, `spec/`, or `release/`. The two
# named docs are durable decision records living outside the artifact tree.
RECORD_DIRS = ("charness-artifacts",)
RECORD_FILES = ("docs/deferred-decisions.md",)

# Markdown only. Decision records in this repo are prose documents; JSON and JSONL under the
# same tree are payloads and captured transcripts, and scanning a captured agent transcript
# for a marker would let a quoted example become a live disposition.
RECORD_SUFFIXES = (".md",)

# The typed marker. One line, one label, any of the issue-anchor forms after it. Tolerates
# the bullet and emphasis decoration this repo's artifacts use, mirroring how the other
# achieve floors read their fields -- `- **Premise-residue:** <anchor> — reason` is the same
# record as the bare form. The reason text is required: a marker with no reason records a
# ritual, and the whole point is that a human wrote down WHY.
_MARKER_RE = re.compile(
    r"^[ \t]*[-*+]?[ \t]*[`*_~]*Premise-residue[`*_~]*[ \t]*:[ \t]*(?P<body>.+)$",
    re.IGNORECASE | re.MULTILINE,
)

_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")


def issue_token_re(number: int) -> "re.Pattern[str]":
    """Match every form this repo cites an issue in, and nothing longer.

    Three forms, because durable records here do use bare URLs
    (`follow-up: https://github.com/.../issues/462`). The trailing `(?!\\d)` on each is the
    whole guard: without it a backlog holding both a two-digit and a four-digit issue
    cross-contaminates every verdict, and the failure is silent because a spurious hit LOOKS
    like the tool working.
    """
    return re.compile(rf"(?:#{number}(?!\d)|issues/{number}(?!\d)|\bGH-{number}(?!\d))")


def _fenced_line_flags(lines: list[str]) -> list[bool]:
    """Which physical lines sit inside a fenced code block.

    Kept even though matching is now exact-form: documentation ABOUT the marker -- including
    this skill's own reference -- shows the marker in a fenced example, and a fenced example
    must not become a live disposition. Skips are reported with locators, never dropped.
    """
    flags: list[bool] = []
    inside = False
    for line in lines:
        if _FENCE_RE.match(line):
            inside = not inside
            flags.append(True)
            continue
        flags.append(inside)
    return flags


def _git_tracked_records(repo_root: Path) -> set[Path] | None:
    """Records git knows about, or None when this is not a usable git checkout.

    Gitignore-awareness, kept self-contained rather than imported: this is a PORTABLE skill
    helper and the repo's own `iter_repo_files` lives in `scripts/`, which a consuming repo
    does not install. Without it the scanner would read build output and vendored trees a
    consumer gitignored.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return {
        repo_root / rel.decode("utf-8", errors="replace")
        for rel in result.stdout.split(b"\0")
        if rel
    }


def _record_paths(repo_root: Path) -> tuple[list[Path], str]:
    """Candidate record files, plus the listing mode actually used.

    The mode is returned rather than assumed because the fallback is a real degradation: an
    `rglob` walk outside a git checkout reads whatever is on disk, which is what the git
    listing exists to prevent.
    """
    tracked = _git_tracked_records(repo_root)
    mode = "git-tracked" if tracked is not None else "rglob-no-git"
    paths: list[Path] = []
    for name in RECORD_DIRS:
        root = repo_root / name
        if not root.is_dir():
            continue
        paths.extend(
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.suffix in RECORD_SUFFIXES
            and (tracked is None or path in tracked)
        )
    for name in RECORD_FILES:
        path = repo_root / name
        if path.is_file() and (tracked is None or path in tracked):
            paths.append(path)
    return sorted(set(paths)), mode


def scan_residue(
    repo_root: Path,
    number: int,
    *,
    exclude: tuple[Path, ...] = (),
) -> dict:
    """Typed `Premise-residue:` markers naming this issue, plus scan provenance.

    `declining` holds only markers that name this issue. There is no `informational`
    bucket any more: an ordinary mention of an issue number in a record is not evidence of
    anything, and counting mentions was what made the prose version look informative while
    being wrong.

    Provenance is not decoration. "No marker found" and "there were no records, or I could
    not read them" must not be the same output, because `classify` refuses on the second and
    may proceed on the first.
    """
    token = issue_token_re(number)
    excluded = {path.resolve() for path in exclude}
    declining: list[dict] = []
    scanned = 0
    markers_seen = 0
    excluded_count = 0
    unreadable: list[str] = []
    fenced_markers: list[str] = []
    roots_present = [name for name in RECORD_DIRS if (repo_root / name).is_dir()]
    roots_present += [name for name in RECORD_FILES if (repo_root / name).is_file()]

    record_paths, listing_mode = _record_paths(repo_root)
    for path in record_paths:
        if path.resolve() in excluded:
            excluded_count += 1
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            unreadable.append(str(path.relative_to(repo_root)))
            continue
        scanned += 1
        lines = text.splitlines()
        fenced = _fenced_line_flags(lines)
        for match in _MARKER_RE.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            markers_seen += 1
            if fenced[line_number - 1]:
                fenced_markers.append(f"{path.relative_to(repo_root)}:{line_number}")
                continue
            if not token.search(match.group("body")):
                continue
            declining.append(
                {
                    "path": str(path.relative_to(repo_root)),
                    "line": line_number,
                    "text": match.group("body").strip()[:400],
                }
            )
    return {
        "declining": declining,
        "provenance": {
            "roots_present": roots_present,
            "files_scanned": scanned,
            "files_unreadable": unreadable,
            "markers_seen": markers_seen,
            # A count with no locator is not a report.
            "fenced_markers_skipped": fenced_markers,
            "listing_mode": listing_mode,
            "suffixes_scanned": list(RECORD_SUFFIXES),
            "records_excluded": excluded_count,
            "excluded": [str(path) for path in exclude],
            "prose_matching": (
                "disabled by design -- residue is read from explicit `Premise-residue:` "
                "markers only, never inferred from record wording"
            ),
        },
    }
