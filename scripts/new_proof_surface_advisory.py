#!/usr/bin/env python3
"""Advisory: a slice that ADDS a proof surface owes that surface a fresh-eye pass.

The 2026-07 evidence-surface hunt established the shape of this risk. Thirty
defects across the repo's proof surfaces, and they were **not regressions** —
`git log -S` on the defective expressions shows most were written once and never
revised. The defect was the ORIGINAL code. The risk concentrates at a proof
surface's BIRTH, not at its edits, which is also why an edit-triggered check would
be useless: 60-163 proof-surface files are touched per week against a population
of ~135, while 8-62 are born.

Why the repo's own suite does not catch this: a gate's author writes that gate's
tests in the same sitting, from the same mental model, so the blind spot in the
code and the blind spot in its test are the same blind spot. Test count measures
breadth, not independence. The one mechanism that caught the class reliably was a
bounded fresh-eye review by a different agent.

`docs/design-north-star.md` classifies proof-surface authoring as an irreversible
boundary, so P4 already requires a distinct observer here. This advisory is that
requirement made visible at the moment it applies; it is NOT the enforcement.

**It deliberately does not classify.** The first cut tried to decide which new
files were proof surfaces from their text. Measured against the hunt's own 30
files as positives and 20 hand-labelled non-gates as negatives, the best content
classifier reached 73% recall at 55% false-fire, and the shipped one reached 60%
— it missed `check_staged_reversion.py` (whose verdict vocabulary is
`clean`/`blocked`, not `passed`/`violation`) while firing on scaffolders, adapters
and recorders. The separating signal is not in the token stream: a proof surface
and an artifact writer look alike. So the classification is handed to the reader,
who can actually make it, and the advisory's job is to guarantee the question gets
asked. Equipping judgment rather than encoding a rulebook that rots is P1/P3; a
73%-recall regex that also cries wolf is the worst of both.

floor-addition-restraint: deliberately ADVISORY, not a blocking gate. (1) It would
raise closeout-contract weight on every slice that adds a file here. (2) A gate
that refuses a commit until a review is *recorded* buys a recorded string, not a
review — this repo has measured that a length/format floor cannot refuse a fluent
excuse. (3) The tooth that works is making a SKIP LOUD, so the advisory names each
surface and the durable closeout payload carries which ones were dispositioned.
Meeting a gate-quality problem with another blocking gate is the anti-pattern the
north star names.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

_advisories = import_repo_module(__file__, "scripts.slice_closeout_advisories")
_scope = import_repo_module(__file__, "scripts.critique_enforcement_scope")

# Every family the hunt's 30 defects lived in. Verified: this pattern covers
# 30/30 of them, where the previous name-prefix pattern covered 21/30 — the nine
# misses were all `scripts/*_lib.py`-style modules that render verdicts under a
# non-gate name (`helper_provenance_lib`, `artifact_validator`,
# `staged_commit_gate_plan`, ...). `skills/shared/` is included because omitting
# it is literally audit row D9's own defect ("an identical violation was caught
# under `scripts/` and `skills/public/` and invisible under `skills/shared/`").
PROOF_SURFACE_PATH = re.compile(
    r"^(?:scripts/[A-Za-z0-9_]+\.py"
    r"|skills/(?:public|support|shared)/[A-Za-z0-9_-]+/scripts/[A-Za-z0-9_]+\.py"
    r"|skills/shared/scripts/[A-Za-z0-9_]+\.py)$"
)

# A HINT for the reader, never a gate. These fire on ~73% of known proof surfaces
# and on ~55% of known non-surfaces, so they order the list and nothing more; a
# file without them is still listed and still needs a disposition.
_HINT_SIGNALS = (
    re.compile(r"\b(findings|violations|blockers|offenders|blocking)\b", re.I),
    re.compile(r"ValidationError"),
    re.compile(r"return\s+1\b|sys\.exit\(1\)|SystemExit\(1\)|return\s+0\s+if"),
)

# `Fresh-eye pass: <path> — <outcome>`. The path is REQUIRED and is matched
# per-surface: the first cut searched for any one marker in the slice and applied
# that single boolean to every new surface, so one line silenced N surfaces and
# the record then read as if all N were reviewed — N-1 quiet skips, which is the
# one thing this advisory exists to prevent.
_MARKER = re.compile(r"^[\s>#*_`-]*fresh[- ]eye pass\s*:\s*(?P<target>[^\s,;—-]+)", re.IGNORECASE | re.M)

# This module documents its own marker form, and a doc that shows the form must
# not count as a use of it. Same exclusion the sibling floor-addition nudge keeps
# for its own rule doc.
_SELF_DOCUMENTING = ("scripts/new_proof_surface_advisory.py", "docs/conventions/implementation-discipline.md")

SCOPE_EVALUATED = "evaluated"
SCOPE_NOT_ESTABLISHED = "not-established"

DEFECT_CLASSES = (
    "(a) empty/degenerate input still returns PASS",
    "(b) verdict keyed on a field that is constant or coarse where it must discriminate",
    "(c) a backstop suppressed by a condition the normal case satisfies",
    "(d) PASS reported for a check that silently did not run",
    "(e) the check lives only in the copy the caller chose",
    "(f) a ratio whose denominator can empty or be silently narrowed",
    "(g) fenced/quoted text read as the author's own assertion",
    "(h) a self-declared field deciding whether the surface's own floors run",
)


def is_proof_surface_path(path: str) -> bool:
    return bool(PROOF_SURFACE_PATH.match(path))


def looks_like_a_verdict(text: str) -> bool:
    """Hint only — see `_HINT_SIGNALS`. Never used to drop a file from the list."""
    return any(pattern.search(text) for pattern in _HINT_SIGNALS)


def new_surface_candidates(repo_root: Path, changed_paths: list[str], base: str = "origin/main") -> tuple[list[dict], str]:
    """``(candidates, scope)`` — newly added files in the proof-surface families.

    Returns the SCOPE alongside the list because `[]` alone cannot distinguish
    "this slice added nothing here" from "the base ref did not resolve, so nothing
    was compared". That ambiguity is class (a)/(d) — the exact defect family this
    advisory exists to trigger on — and the first cut shipped it.
    """
    candidates = [path for path in changed_paths if is_proof_surface_path(path)]
    if not candidates:
        return [], SCOPE_EVALUATED
    probe = _advisories.subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base], cwd=repo_root, capture_output=True
    )
    if probe.returncode != 0:
        return [], SCOPE_NOT_ESTABLISHED
    rows: list[dict] = []
    for path in sorted(set(_advisories._added_vs_base(repo_root, candidates, base=base))):
        try:
            text = (repo_root / path).read_text(encoding="utf-8")
        except (OSError, ValueError):
            # `ValueError` covers UnicodeDecodeError: an unreadable file must not
            # abort a closeout that would otherwise pass, and must not vanish
            # silently either — it is listed with the hint left unknown.
            rows.append({"path": path, "likely_verdict_surface": None})
            continue
        rows.append({"path": path, "likely_verdict_surface": looks_like_a_verdict(text)})
    return rows, SCOPE_EVALUATED


def dispositioned_paths(repo_root: Path, changed_paths: list[str], base: str = "origin/main") -> set[str]:
    """Paths named by a `Fresh-eye pass: <path> …` marker in the slice's added lines.

    Fences are stripped first. Content rendered as code is shown to the reader,
    not asserted by the author, and a critique artifact *about this advisory* is
    exactly the document that quotes the marker form — this repo has now shipped
    that defect four times, so it is not a hypothetical.
    """
    scanned = [path for path in changed_paths if path not in _SELF_DOCUMENTING]
    added = _advisories._added_diff_lines(repo_root, base, scanned)
    return {match.group("target").strip("`'\"") for match in _MARKER.finditer(_scope.strip_display_fences(added))}


def advise_new_proof_surface(repo_root: Path, changed_paths: list[str], base: str = "origin/main") -> dict:
    """Name every newly added candidate surface that carries no disposition."""
    candidates, scope = new_surface_candidates(repo_root, changed_paths, base=base)
    record: dict = {
        "scope": scope,
        "new_surface_candidates": [row["path"] for row in candidates],
        "dispositioned": [],
        "undispositioned": [],
    }
    if not candidates:
        return record
    dispositioned = dispositioned_paths(repo_root, changed_paths, base=base)
    record["dispositioned"] = sorted(path for path in record["new_surface_candidates"] if path in dispositioned)
    pending = [row for row in candidates if row["path"] not in dispositioned]
    record["undispositioned"] = [row["path"] for row in pending]
    if not pending:
        return record
    listed = "\n".join(
        f"  - {row['path']}" + (" (renders a verdict? likely)" if row["likely_verdict_surface"] else "")
        for row in pending
    )
    print(
        "ADVISORY: this slice adds file(s) in the proof-surface families with no recorded "
        "disposition:\n" + listed + "\n"
        "Decide for each whether it renders a verdict about other code or artifacts. If it does, "
        "it is a proof surface, and proof-surface authoring is an irreversible boundary "
        "(docs/design-north-star.md): a gate that fails open emits no failure, no log line, no "
        "ticket, ships to every consuming repo, and every later session trusts it. Its own tests "
        "are not a second observer — the same mental model wrote both. Spawn a bounded read-only "
        "reviewer against these classes:\n  " + "\n  ".join(DEFECT_CLASSES) + "\n"
        "Then record ONE line per path — the path is required, a marker naming one path does not "
        "cover the others:\n"
        "  `Fresh-eye pass: <path> — <what the reviewer found, or none>`\n"
        "  `Fresh-eye pass: <path> — not a proof surface, <why>`\n"
        "  `Fresh-eye pass: <path> — skipped, <concrete reason>`\n"
        "Skipping is an accepted answer; skipping SILENTLY is not.",
        file=sys.stderr,
    )
    return record


def attach_new_proof_surface_advisory(payload: dict, repo_root: Path, base: str = "origin/main") -> None:
    """Attach the record to the durable closeout payload and emit the advisory."""
    payload["new_proof_surface_advisory"] = advise_new_proof_surface(
        repo_root, payload["changed_paths"], base=base
    )
