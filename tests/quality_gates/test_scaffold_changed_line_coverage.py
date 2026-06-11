"""Acceptance proof for issue #306: scaffold CLI lines read covered via the probe.

The scheduled mutation gate's changed-line signal blocks a changed line when
the gate's *own* coverage probe (``scripts/mutation_sampling_lib.run_test_coverage``)
records it as a missing statement. The recurring self-healing auto-issues were
driven by the public-skill ``scaffold_*_artifact.py`` CLI scripts: exercised
only via ``subprocess.run(["python3", SCAFFOLD, ...])``, their validator-fallback
and non-json print branches stayed uncovered, so any changed line on those
branches re-filed the issue.

``tests/test_scaffold_inprocess_coverage.py`` now imports and drives those
branches in-process. This gate test runs the GATE's coverage probe over that
in-process test and asserts the previously-recurring lines now read as covered
(not "subprocess-only -> 0%"). It is the focused probe run the slice acceptance
asks for, kept ``release_only`` because invoking the real coverage subprocess is
too slow for the standing pre-push gate.

This test does NOT weaken the changed-line gate: it asserts coverage went UP for
a known class. ``test_changed_line_gate_still_blocks_genuinely_uncovered_line``
keeps the non-weakening invariant honest by proving an actually-uncovered
changed line still classifies as blocking.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from mutation_changed_files_lib import classify_changed_line_scope_gap  # noqa: E402
from mutation_sampling_lib import (  # noqa: E402
    load_file_statement_lines,
    run_test_coverage,
)

# Scaffolds and the shared validator-fallback statement lines that the
# subprocess-only tests left uncovered and that the in-process test now drives.
# Re-resolved structurally below so a line shift does not silently pass.
SCAFFOLDS = ["critique", "debug", "handoff", "ideation", "quality", "retro"]
SCAFFOLD_HELPER_REL = "scripts/scaffold_artifact_lib.py"


def _scaffold_rel(slug: str) -> str:
    return f"skills/public/{slug}/scripts/scaffold_{slug}_artifact.py"


def _validator_fallback_lines() -> list[int]:
    """Statement line numbers inside the shared validator_command repo_local fallback."""
    path = REPO_ROOT / SCAFFOLD_HELPER_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    fallback: list[int] = []
    in_fallback = False
    for index, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("repo_local = repo_root /"):
            in_fallback = True
        if in_fallback and stripped.startswith("repo_local = repo_root /"):
            fallback.append(index)
        elif in_fallback and stripped.startswith("return f\"python3 scripts/"):
            fallback.append(index)
            break
    assert fallback, "could not locate shared validator fallback lines"
    return fallback


@pytest.mark.release_only
def test_scaffold_changed_lines_read_covered_through_gate_probe(tmp_path: Path) -> None:
    coverage_json = tmp_path / "scaffold-probe-coverage.json"
    # Drive ONLY the in-process test through the gate's coverage probe; if its
    # capture were honest before, the subprocess tests alone would already cover
    # these branches -- they did not, which is the bug this slice fixes.
    run_test_coverage(
        REPO_ROOT,
        "python3 -m pytest tests/test_scaffold_inprocess_coverage.py -q",
        coverage_json,
    )
    statement_lines = load_file_statement_lines(REPO_ROOT, coverage_json)

    assert SCAFFOLD_HELPER_REL in statement_lines, (
        f"{SCAFFOLD_HELPER_REL} not tracked by the probe -- shared fallback coverage is invisible"
    )
    executed, missing = statement_lines[SCAFFOLD_HELPER_REL]
    fallback_lines = _validator_fallback_lines()
    still_missing = [line for line in fallback_lines if line in missing]
    assert not still_missing, (
        f"{SCAFFOLD_HELPER_REL} validator fallback lines still uncovered: {still_missing} "
        f"(executed has {len(executed)} lines)"
    )

    for slug in SCAFFOLDS:
        rel = _scaffold_rel(slug)
        assert rel in statement_lines, (
            f"{rel} not tracked by the probe -- it would read as subprocess-only 0%"
        )


def test_changed_line_gate_still_blocks_genuinely_uncovered_line(tmp_path: Path) -> None:
    """Non-weakening invariant: an uncovered changed line still classifies as blocking.

    Pure-library check (no coverage subprocess) so it runs in the standing gate:
    a changed file with a changed statement line absent from its executed set
    must remain in the blocking set.
    """
    path = "skills/public/example/scripts/example.py"

    def _fake_changed_lines(_repo_root, _base, _head, target):
        # Changed line 5 is a real statement that coverage marks as missing.
        return {5} if target == path else set()

    import mutation_changed_files_lib as lib

    original = lib.changed_line_numbers
    lib.changed_line_numbers = _fake_changed_lines
    try:
        blocking = classify_changed_line_scope_gap(
            repo_root=tmp_path,
            base_sha="base",
            head_sha="head",
            changed_before_coverage=[path],
            statement_lines={path: ({4}, {5})},
            coverage_enabled=True,
        )
    finally:
        lib.changed_line_numbers = original

    assert path in blocking, "an uncovered changed line must still block"
