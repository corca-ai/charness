"""Three readers refuse an unhonored adapter declaration instead of silently working on
the WRONG FILE.

Rows 11-13 of slice 5. The shared harm here is sharper than a relocated write target:
`parse_handoff_entries` READS the file it resolves and reports counts from it, so an
unhonored declaration produces a confident, well-formed answer about a document the repo
does not use.

Measured on the real CLIs at `97dfc881a`, one temp repo declaring `output_dir: docs/mine`
and holding a distinguishable handoff at each location:

    parse_handoff_entries  handoff_path: <repo>/docs/handoff.md, ok: true, entry_count: 1
    plan_handoff_run       artifact_path: docs/handoff.md
    sync_review_artifact   artifact_path: charness-artifacts/hitl/latest.md, status: synced

All at exit 0. The third WRITES: without `--check` it calls `write_current_pointer_text`
at the resolved path.

`plan_handoff_run` is the row worth reading twice. It already read `adapter["errors"]` —
and that was not enough, because the read only adds an advisory and echoes the errors into
the output envelope. It never gated the `artifact_path` or the `next_action` built from
the defaulted data. An echoed error beside an acted-on default is the "a read is not a
check" shape this whole slice is about.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

# Literal, not derived: `suggest_mutation_coverage_command` maps a source file to the
# standing tests that reference it BY NAME, and a file that builds its paths from
# f-strings is invisible to it — which made the changed-line producer report an
# exercised guard line as uncovered earlier in this slice.
PARSE_ENTRIES = "skills/public/handoff/scripts/parse_handoff_entries.py"
PLAN_HANDOFF = "skills/public/handoff/scripts/plan_handoff_run.py"
SYNC_REVIEW = "skills/public/hitl/scripts/sync_review_artifact.py"

DECLARED_HANDOFF = "version: {v}\nrepo: demo\noutput_dir: docs/mine\n"
DECLARED_HITL = "version: {v}\nrepo: demo\noutput_dir: docs/mine-hitl\n"


def _repo(tmp_path: Path, *, handoff: str | None, hitl: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "mine").mkdir(parents=True, exist_ok=True)
    # Two handoffs with DIFFERENT bodies, so "read the declared file" and "read ours"
    # are distinguishable in the parsed output rather than only in the path.
    (repo / "docs" / "mine" / "handoff.md").write_text(
        "# Handoff\n\n## Next Session\n\n1. the declared one\n", encoding="utf-8"
    )
    (repo / "docs" / "handoff.md").write_text(
        "# Handoff\n\n## Next Session\n\n1. the charness default one\n", encoding="utf-8"
    )
    session = repo / ".charness" / "hitl" / "runtime" / "s1"
    session.mkdir(parents=True, exist_ok=True)
    (session / "state.yaml").write_text("session_id: s1\nstatus: in_progress\n", encoding="utf-8")
    agents = repo / ".agents"
    agents.mkdir(parents=True, exist_ok=True)
    if handoff is not None:
        (agents / "handoff-adapter.yaml").write_text(handoff, encoding="utf-8")
    if hitl is not None:
        (agents / "hitl-adapter.yaml").write_text(hitl, encoding="utf-8")
    return repo


def _run(rel: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / rel), *args], capture_output=True, text=True
    )


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_handoff_readers_refuse_rather_than_reading_the_wrong_file(
    tmp_path: Path, version: str
) -> None:
    repo = _repo(tmp_path, handoff=DECLARED_HANDOFF.format(v=version), hitl=None)
    for rel in (PARSE_ENTRIES, PLAN_HANDOFF):
        result = _run(rel, "--repo-root", str(repo))
        assert result.returncode == 1, (rel, result.stdout)
        assert "handoff-adapter.yaml" in result.stderr, rel
        # The wrong path must not be reported alongside the refusal.
        assert "docs/handoff.md" not in result.stdout, rel


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_hitl_sync_refuses_before_it_writes(tmp_path: Path, version: str) -> None:
    repo = _repo(tmp_path, handoff=None, hitl=DECLARED_HITL.format(v=version))
    result = _run(SYNC_REVIEW, "--repo-root", str(repo), "--session-id", "s1")
    assert result.returncode == 1, result.stdout
    assert "hitl-adapter.yaml" in result.stderr
    assert not (repo / "charness-artifacts" / "hitl" / "latest.md").exists()


def test_a_speakable_version_reads_and_writes_where_the_repo_said(tmp_path: Path) -> None:
    """The polarity control. Without it every assertion above is satisfied by a reader
    that refuses everything."""
    repo = _repo(tmp_path, handoff=DECLARED_HANDOFF.format(v="1"), hitl=DECLARED_HITL.format(v="1"))
    parsed = _run(PARSE_ENTRIES, "--repo-root", str(repo))
    assert parsed.returncode == 0, parsed.stderr
    assert "docs/mine/handoff.md" in parsed.stdout
    planned = _run(PLAN_HANDOFF, "--repo-root", str(repo))
    assert planned.returncode == 0, planned.stderr
    assert "artifact_path: docs/mine/handoff.md" in planned.stdout
    synced = _run(SYNC_REVIEW, "--repo-root", str(repo), "--session-id", "s1")
    assert synced.returncode == 0, synced.stderr
    assert "artifact_path: docs/mine-hitl/latest.md" in synced.stdout


def test_an_explicitly_named_file_is_not_refused(tmp_path: Path) -> None:
    """`parse_handoff_entries.py <path>` asks the adapter nothing FOR THE PATH IT PARSES.

    The guard sits AFTER the explicit-path arm on purpose. Refusing here would break the
    natural direct invocation over a repo whose adapter happens to be broken — and that
    caller is not relying on the declaration for the file it named.

    The qualifier is load-bearing and was added by a round-2 bounded review:
    `--with-issues` DOES reach the adapter. See
    `test_the_explicit_path_arm_with_issues_does_not_act_on_a_charness_default`.
    """
    repo = _repo(tmp_path, handoff=DECLARED_HANDOFF.format(v="9"), hitl=None)
    result = _run(PARSE_ENTRIES, str(repo / "docs" / "mine" / "handoff.md"))
    assert result.returncode == 0, result.stderr
    assert "docs/mine/handoff.md" in result.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    """Opt-in surfaces. A repo that declared nothing is not a repo whose declaration could
    not be read."""
    repo = _repo(tmp_path, handoff=None, hitl=None)
    parsed = _run(PARSE_ENTRIES, "--repo-root", str(repo))
    assert parsed.returncode == 0, parsed.stderr
    assert "docs/handoff.md" in parsed.stdout
    synced = _run(SYNC_REVIEW, "--repo-root", str(repo), "--session-id", "s1")
    assert synced.returncode == 0, synced.stderr
    assert "charness-artifacts/hitl/latest.md" in synced.stdout


def test_the_explicit_path_arm_with_issues_does_not_act_on_a_charness_default(
    tmp_path: Path,
) -> None:
    """The gap a round-2 bounded review found, closed by measurement rather than prose.

    `parse_handoff_entries.py <path>` was exempted from the guard on the ground that a
    caller naming the file "asks the adapter nothing". That is true FOR THE PATH IT
    PARSES and false in general: `--with-issues` reaches the handoff adapter through
    `chunked_routing_issue_source.build_issue_entries` ->
    `chunked_routing_issue_config.load_issue_source_config`, which loads it by repo root.

    The outcome is safe, and this pins WHY: that helper checks `adapter.get("valid") is
    False` and returns `enabled: False`, so `build_issue_entries` yields nothing and no
    charness default is acted on. The safety is the helper's property, not the
    exemption's, and before this test nothing held it. The record's `Call sites unproven:
    none` was resolving `covers_all_call_sites: true` while the record's own body named
    this path as untested.
    """
    repo = _repo(tmp_path, handoff=DECLARED_HANDOFF.format(v="9"), hitl=None)
    result = _run(PARSE_ENTRIES, str(repo / "docs" / "mine" / "handoff.md"),
                  "--repo-root", str(repo), "--with-issues")
    assert result.returncode == 0, result.stderr
    # The named file is still parsed — the exemption holds for what it covers.
    assert "docs/mine/handoff.md" in result.stdout
    # And the adapter-derived issue source contributed nothing.
    assert "issue_entry_count: 0" in result.stdout
