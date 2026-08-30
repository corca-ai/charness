"""Tests for the evidence-residual floor measurement.

The measurement exists because two previous attempts at this floor were withdrawn
on numbers nobody could re-run, one of them a count of TEST FIXTURES standing in
for a count of artifacts. A measurement script that is itself unverified would
repeat that shape one level up, so the script has its own tests.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from tests.residual_floor_support import residual_floor_message

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "measure_evidence_residual.py"


def _run(repo_root: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
    )
    # Command stdout is YAML; the persisted probe artifact this is compared against
    # is still JSON on disk and is still read with `json.loads` below.
    return result.returncode, yaml.safe_load(result.stdout)


def test_an_empty_corpus_does_not_read_as_the_floor_clearing_everything(tmp_path: Path) -> None:
    """The empty-scope case, refused rather than passed.

    With no artifacts there is no minimum to be below, so
    `floor_below_every_measured_minimum` must be False and the exit non-zero.
    Reporting True over an empty corpus is the exact "verdict over a scope it did
    not establish" class this floor was built to close.
    """
    (tmp_path / "charness-artifacts").mkdir()
    code, payload = _run(tmp_path)
    assert payload["corpus_established"] is False
    assert payload["floor_below_every_measured_minimum"] is False
    assert code != 0
    assert payload["kinds"]["markdown_artifacts"]["min_residual"] is None


def test_a_stub_scores_zero_and_a_real_artifact_does_not(tmp_path: Path) -> None:
    """The separation the floor rests on, measured rather than asserted."""
    critique = tmp_path / "charness-artifacts" / "critique"
    critique.mkdir(parents=True)
    (critique / "466.md").write_text("#466", encoding="utf-8")
    code, payload = _run(tmp_path)
    markdown = payload["kinds"]["markdown_artifacts"]
    assert markdown["files"] == 1
    assert markdown["min_residual"] == 0
    assert markdown["min_residual_path"] == "charness-artifacts/critique/466.md"
    assert payload["floor_below_every_measured_minimum"] is False
    assert code != 0

    (critique / "2026-08-01-real.md").write_text(
        "# Critique for 466\n\nAngle one: the accept path took presence for execution.\n",
        encoding="utf-8",
    )
    (critique / "466.md").unlink()
    _, payload = _run(tmp_path)
    assert payload["kinds"]["markdown_artifacts"]["min_residual"] > payload["floor"]


def test_the_json_probe_kind_is_measured_separately(tmp_path: Path) -> None:
    """Alphanumeric counting penalizes punctuation, so JSON is not assumed from prose."""
    probe = tmp_path / "charness-artifacts" / "probe"
    probe.mkdir(parents=True)
    (probe / "2026-08-01-host-log.json").write_text(
        '{"host": "claude-code", "surface": "session-log", "verdict": "probed"}\n',
        encoding="utf-8",
    )
    (tmp_path / "charness-artifacts" / "critique").mkdir(parents=True)
    (tmp_path / "charness-artifacts" / "critique" / "c.md").write_text(
        "# A critique with enough body to clear the floor comfortably.\n", encoding="utf-8"
    )
    code, payload = _run(tmp_path)
    assert payload["kinds"]["json_host_log_probes"]["files"] == 1
    assert payload["kinds"]["json_host_log_probes"]["min_residual"] > payload["floor"]
    assert payload["floor_below_every_measured_minimum"] is True
    assert code == 0


def test_the_recorded_run_matches_this_repo_today() -> None:
    """The checked-in probe artifact is the claim; this re-runs it.

    A recorded measurement nobody re-runs decays into the same unverifiable number
    the withdrawn attempts shipped.
    """
    recorded = json.loads(
        (REPO_ROOT / "charness-artifacts" / "probe" / "2026-08-01-evidence-residual-floor.json")
        .read_text(encoding="utf-8")
    )
    code, live = _run(REPO_ROOT)
    # MESSAGED, and this is the assertion that actually fires. The script exits 1 exactly when
    # the invariant is broken, so a stub artifact landing in the corpus reaches HERE and
    # short-circuits every messaged assertion below it. The first version of this repair gave
    # the message to those and left this bare, which fixed the diagnostic for the failure mode
    # that does not happen and left #561's reported one — "a new stub artifact reds it with no
    # cause and no remedy" — exactly as it was.
    assert code == 0, residual_floor_message("the command's exit status")
    assert live["floor"] == recorded["floor"], residual_floor_message("floor")
    # Belt-and-braces: unreachable while the script keeps its current exit contract, since the
    # exit check above already caught it. Kept deliberately so a change to that contract cannot
    # silently remove the claim itself.
    assert live["floor_below_every_measured_minimum"] is True, residual_floor_message(
        "floor_below_every_measured_minimum"
    )
    for kind, recorded_kind in recorded["kinds"].items():
        # Counts grow as artifacts land; the floor claim is what must hold.
        assert live["kinds"][kind]["min_residual"] >= live["floor"], residual_floor_message(
            "min_residual", kind=kind
        )
        # A DIFFERENT claim, and it needs a different message: both sides come from the recorded
        # probe, so nothing live participates. Rendering the drift text here told the reader to go
        # inspect a live tree that is fine, for a file that is not.
        assert recorded_kind["min_residual"] >= recorded["floor"], residual_floor_message(
            "min_residual", kind=kind, recorded_only=True
        )


def test_a_directory_and_an_unreadable_file_are_skipped_not_scored(tmp_path: Path) -> None:
    """Neither may enter the corpus as a zero-residual datapoint.

    A directory named `*.md` and a file the process cannot read would both score 0
    and become the reported minimum — a measurement whose floor claim is decided
    by something that is not evidence at all.
    """
    critique = tmp_path / "charness-artifacts" / "critique"
    critique.mkdir(parents=True)
    (critique / "a-directory.md").mkdir()
    (critique / "real.md").write_text(
        "# A critique with enough body to clear the floor comfortably.\n", encoding="utf-8"
    )
    unreadable = critique / "unreadable.md"
    unreadable.write_text("# also real, but unreadable\n", encoding="utf-8")
    unreadable.chmod(0o000)
    try:
        code, payload = _run(tmp_path)
        markdown = payload["kinds"]["markdown_artifacts"]
        scored = {entry["path"] for entry in markdown["smallest_five"]}
        assert "charness-artifacts/critique/a-directory.md" not in scored
        assert markdown["min_residual"] > payload["floor"]
        assert code == 0
    finally:
        unreadable.chmod(0o644)
