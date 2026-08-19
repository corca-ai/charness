"""The announcement preflight refuses an unhonored declaration instead of clearing a
delivery it exists to block.

Rows 24-25 of slice 5, and `preflight_sources` is the sharpest publish-boundary reading in
the slice: its whole job is to stop a delivery that would claim an in-progress source is
finished, and an unhonored declaration does not degrade that — it INVERTS it.

Measured at `254fa5c44`: a repo declaring one `in_progress_sources` entry got
`delivery_blocked: false`, `ok: true`, `surfaces: []`, exit 0 — clear to announce. The same
repo at a speakable version gets `delivery_blocked: true`, `ok: false`, exit 2.

The mechanism is worth naming because it is why the flip is total rather than partial:
`announcement_preflight_lib.preflight_sources` short-circuits to ok/unblocked the moment
`in_progress_sources` is empty, and an unhonored declaration is indistinguishable there
from a repo that declared none.

`record_announcement`'s guard sits BEFORE its `except Exception` fallback, deliberately.
That fallback is correct for a resolution FAILURE — it records `adapter_resolved: False`
and keeps the disagreement typed and visible. It is wrong for a resolution that SUCCEEDED
while honoring nothing, because `requires_delivery_kind_agreement` then compares the
recorded kind against a charness default.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

PREFLIGHT = "skills/public/announcement/scripts/preflight_sources.py"
RECORD = "skills/public/announcement/scripts/record_announcement.py"

# `in_progress_sources` entries are MAPPINGS with a `kind`, not strings — an earlier
# stimulus in this slice used a bare string and the control could not fail, because
# `_validate_in_progress_sources` rejected it and the empty list took the short-circuit.
DECLARED = """version: {v}
repo: demo
delivery_kind: release-notes
release_notes_path: docs/mine-notes.md
in_progress_sources:
  - kind: path
    path: docs/pending-migration.md
    summary: a migration the announcement must not claim finished
"""


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "announcement-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(rel: str, repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / rel), "--repo-root", str(repo), *args],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_preflight_refuses_rather_than_clearing_the_delivery(
    tmp_path: Path, version: str
) -> None:
    result = _run(PREFLIGHT, _repo(tmp_path, DECLARED.format(v=version)))
    assert result.returncode != 0, result.stdout
    if version == "9":
        assert "announcement-adapter.yaml" in result.stderr, result.stderr
        assert "does not speak" in result.stderr, result.stderr
    else:
        # announcement is one of six resolvers that let a parser refusal's `ValueError`
        # out rather than recording it (#673), so this door refuses with a raw traceback.
        assert "Traceback" in result.stderr, result.stderr
    # The cleared verdict must not be reported alongside the refusal.
    assert "delivery_blocked: false" not in result.stdout
    assert "ok: true" not in result.stdout


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_recorder_refuses_before_its_own_fallback(tmp_path: Path, version: str) -> None:
    """THE TWO DOORS LAND DIFFERENTLY HERE, and the asymmetry is correct rather than a
    gap — measured, then reasoned about, not the other way round.

    `version: 9` resolves cleanly to a payload carrying a `delivery_kind` the repo never
    wrote, so the guard refuses: `requires_delivery_kind_agreement` would otherwise
    compare the recorded kind against a charness default.

    `version: !!int 9` makes announcement's resolver RAISE (one of the six in #673). The
    guard swallows that and answers None, and the module's own `except Exception` arm
    catches it and records `adapter_resolved: false` — which is a typed, visible signal
    and exactly the case that fallback was written for. Verified by reading the written
    record, not assumed. Forcing symmetry here would replace a legible fallback with a
    stop, for the one input where the fallback is right.
    """
    repo = _repo(tmp_path, DECLARED.format(v=version))
    result = _run(
        RECORD, repo, "--head-commit", "deadbeef", "--delivery-kind", "release-notes",
    )
    if version == "9":
        assert result.returncode != 0, result.stdout
        assert "announcement-adapter.yaml" in result.stderr
        return
    assert result.returncode == 0, result.stderr
    import json

    log = (repo / ".charness" / "announcement" / "announcements.jsonl").read_text(encoding="utf-8")
    entry = json.loads(log.strip().splitlines()[-1])
    check = entry.get("delivery_kind_check") or entry
    assert check.get("adapter_resolved") is False, entry


def test_a_speakable_version_still_blocks_the_delivery(tmp_path: Path) -> None:
    """The polarity control, and the one that carries the whole claim.

    `delivery_blocked: true` at exit 2 is what the gate is FOR. A control asserting only
    exit 0 would be satisfied by a preflight that blocks nothing, which is the base
    behavior this row repairs.
    """
    result = _run(PREFLIGHT, _repo(tmp_path, DECLARED.format(v="1")))
    assert result.returncode == 2, result.stdout
    assert "delivery_blocked: true" in result.stdout
    assert "ok: false" in result.stdout
    assert "docs/pending-migration.md" in result.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    """Opt-in surface. A repo that declared no in-progress sources is genuinely clear to
    deliver, which is the answer that was wrong only over a repo that declared some."""
    result = _run(PREFLIGHT, _repo(tmp_path, None))
    assert result.returncode == 0, result.stderr
    assert "delivery_blocked: false" in result.stdout


def test_an_ordinary_invalid_field_is_not_refused(tmp_path: Path) -> None:
    """`valid: false` from an unrelated bad field must NOT refuse, and the declared
    sources must still block — asserting both halves."""
    adapter = DECLARED.format(v="1").replace("repo: demo", "repo: demo\npreset_version: 3")
    result = _run(PREFLIGHT, _repo(tmp_path, adapter))
    assert result.returncode == 2, result.stdout
    assert "delivery_blocked: true" in result.stdout
