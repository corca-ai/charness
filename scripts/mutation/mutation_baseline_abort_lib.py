"""Shared helpers for the mutation coverage-baseline abort marker, and for the
status vocabulary both mutation slices report their verdicts in.

TWO concepts live here, declared rather than left for a reader to discover. A
round-2 review was right that the second arrived because both engines already
imported this module, not because the file had asked for it; the alternative was
minting a module for two symbols, which the taste ladder disprefers at equal
capability. The concepts are related but distinct, and this docstring names both
so nobody hunting the verdict vocabulary has to guess it lives in an
abort-marker file: an abort is ONE route to "nothing was measured", a zero
denominator is another, and `UNMEASURED_STATUS` is the single word both report.
Every spelling of that word in the repo resolves to the constant below; the
constant is the owner, not a suggestion.

When `scripts/mutation/sample_mutation_files.py`'s coverage-baseline pytest run fails,
no mutation manifest is written and the failing nodeids only ever reached the
CI step log. `check_mutation_score.py` then reported nothing but the
collateral "stats missing" symptom, and `check_js_mutation_score.py` appended
an unrelated "StrykerJS JSON report missing" slice on top of it. This marker
records the real blocking signal (the baseline pytest failure, with parsed
nodeids when available) so both downstream summary scripts can name it
instead of the collateral symptom.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_BASELINE_ABORT_MARKER = Path("reports/mutation/baseline-abort.json")
_MARKER_KIND = "coverage-baseline-pytest-failed"

# WHICH baseline aborted. Two different commands can abort a baseline and both make
# the JS slice's report absent, but only one of them is the sampler -- so a single
# hardcoded sentence was true for one path and false for the other. The marker kind
# is deliberately unchanged so an existing marker still reads.
STAGE_SAMPLER_COVERAGE = "sampler-coverage-baseline"
STAGE_COSMIC_RAY_BASELINE = "cosmic-ray-baseline"
# The CAUSE only. Each reader frames it for its own vantage point: the Python
# summary is written by the stage that failed, the JS summary is written by a slice
# that never ran. One shared sentence had to be wrong for one of them.
_STAGE_CAUSES = {
    STAGE_SAMPLER_COVERAGE: "the sampler's coverage-baseline pytest failed",
    STAGE_COSMIC_RAY_BASELINE: "`cosmic-ray baseline` failed",
}
# The status word a slice has EARNED. This lib already owns the vocabulary for "the
# run never measured anything"; the abort marker is one route into that state and a
# zero denominator is the other, so both spellings belong to one owner.
UNMEASURED_STATUS = "UNMEASURED"


def verdict_token(reachable: int, passed: bool) -> str:
    """`PASS`/`FAIL` only when a denominator exists; otherwise `UNMEASURED`.

    `reachable` is killed + survived -- the mutants that actually returned a verdict.
    At zero there is no score, so neither PASS nor FAIL is earned, and reporting
    either asserts a measurement that never happened.

    Both engines call this instead of spelling the rule twice. The first cut DID
    spell it twice -- once per slice -- and the duplicate ratchet flagged the pair on
    the same commit that introduced it. A rule with two implementations is the defect
    this repo keeps paying for, so it gets one owner here.
    """
    if not int(reachable):
        return UNMEASURED_STATUS
    return "PASS" if passed else "FAIL"


_FAILED_SHORT_SUMMARY_RE = re.compile(r"^FAILED (\S+)(?: - .*)?$", re.MULTILINE)
_FAILED_VERBOSE_RE = re.compile(r"^(\S+::\S+) FAILED\b", re.MULTILINE)
_ERROR_COLLECTION_RE = re.compile(r"^ERROR (\S+)(?: - .*)?$", re.MULTILINE)


def parse_failed_nodeids(text: str) -> list[str]:
    """Extract pytest failing nodeids from combined stdout/stderr.

    Matches the short-summary form (``FAILED <nodeid>``, optionally followed
    by `` - <reason>``), the verbose per-test form (``<nodeid> FAILED``), and
    pytest collection-error lines (``ERROR <nodeid-or-path>``, optionally
    followed by `` - <reason>``), deduping while preserving first-seen order.
    """
    matches = [
        (match.start(), match.group(1))
        for pattern in (_FAILED_SHORT_SUMMARY_RE, _FAILED_VERBOSE_RE, _ERROR_COLLECTION_RE)
        for match in pattern.finditer(text)
    ]
    matches.sort(key=lambda item: item[0])
    nodeids: list[str] = []
    seen: set[str] = set()
    for _position, nodeid in matches:
        if nodeid not in seen:
            seen.add(nodeid)
            nodeids.append(nodeid)
    return nodeids


def resolve_baseline_abort_marker(repo_root: Path, marker_path: Path) -> Path:
    return marker_path if marker_path.is_absolute() else repo_root / marker_path


def delete_stale_baseline_abort_marker(marker_path: Path) -> None:
    # missing_ok (no exists() pre-check): a concurrent run may remove the
    # marker between any check and this unlink; absence is the desired state.
    marker_path.unlink(missing_ok=True)


def write_baseline_abort_marker(
    marker_path: Path,
    *,
    exit_code: int,
    test_command: str,
    failing_nodeids: list[str],
    log_tail: list[str],
    stage: str,
) -> None:
    # REQUIRED, not defaulted. A default of "sampler" is the same defect one layer
    # down: a future writer that forgets the kwarg gets a silently valid, silently
    # wrong label -- which is exactly the hardcoded-sampler sentence this vocabulary
    # exists to remove. Both current callers already know their stage.
    if stage not in _STAGE_CAUSES:
        raise ValueError(
            f"unknown baseline-abort stage {stage!r}; allowed: {sorted(_STAGE_CAUSES)}"
        )
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "kind": _MARKER_KIND,
        "stage": stage,
        "exit_code": exit_code,
        "test_command": test_command,
        "failing_nodeids": failing_nodeids,
        "log_tail": log_tail,
    }
    marker_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_baseline_abort_marker(marker_path: Path) -> dict | None:
    """Return the marker payload, or None when absent, unreadable, or malformed.

    Callers use ``None`` as the "no abort recorded" signal, so any read/parse
    failure must fall back to that instead of raising.
    """
    if not marker_path.is_file():
        return None
    try:
        data = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("kind") != _MARKER_KIND:
        return None
    return data


def log_tail_lines(text: str, limit: int = 30) -> list[str]:
    return text.splitlines()[-limit:]


def baseline_abort_cause(marker: dict) -> str:
    """WHICH baseline aborted, owned HERE so two readers cannot disagree about it.

    A marker written before `stage` existed has none and reads as the sampler stage --
    the only writer at that time. An unknown stage renders as unknown rather than as
    either real one, because guessing is how a report names the wrong cause.
    """
    stage = marker.get("stage", STAGE_SAMPLER_COVERAGE)
    cause = _STAGE_CAUSES.get(stage)
    if cause is None:
        return f"a mutation baseline aborted at an unrecognized stage ({stage!r})"
    return cause
