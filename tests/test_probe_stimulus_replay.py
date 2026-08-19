"""The stimulus replay: a probe record's reproduction steps must actually reproduce.

The regression corpus is REAL, not invented. Every `_STIMULUS` constant below whose name
ends in `_DEAD` is the verbatim adapter document a probe record published on 2026-08-19,
before a bounded reviewer hand-traced it through `scripts/adapter_lib.py` and found the
polarity control could not fail. The `_LIVE` twin is the corrected document from the same
record. Each pair is one round of review this detector is meant to replace.

These tests drive the REAL resolvers as subprocesses. That is deliberate and it is the
`green-test-is-not-covered-line` lesson applied at the level above coverage: a stub
resolver would prove the ablation loop runs, not that this repo's sixteen readers actually
ignore the shapes the records used, which is the whole claim.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts import probe_stimulus_replay as replay

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "check_probe_record.py"


def _stimulus(filename: str, body: str, *, quote: str = "'") -> str:
    return f"mkdir -p $D/.agents\ncat > $D/.agents/{filename} <<{quote}YAML{quote}\n{body}YAML\n"


def _replay(stimulus: str) -> dict:
    return replay.replay_probe_stimulus({"sections": {"stimulus": stimulus}}, repo_root=ROOT)


# --- the measured regression corpus (#674) ------------------------------------------

NARRATIVE_DEAD = "version: 9\nrepo: demo\nsource_documents: [docs/mine-narrative.md]\n"
NARRATIVE_LIVE = "version: 9\nrepo: demo\nsource_documents:\n  - docs/mine-narrative.md\n"
QUALITY_DEAD = (
    "version: 9\nrepo: demo\noutput_dir: docs/mine-q\n"
    'startup_probes:\n  - id: probe-one\n    command: [python3, "-c", "pass"]\n'
)
QUALITY_LIVE = (
    "version: 9\nrepo: demo\noutput_dir: docs/mine-q\n"
    "startup_probes:\n  - label: probe-one\n    command:\n      - python3\n"
    '      - "-c"\n      - "pass"\n    class: standing\n    startup_mode: warm\n'
    "    surface: direct\n"
)
HANDOFF_DEAD = "version: 9\nrepo: demo\nartifact_path: docs/mine/handoff.md\n"
HANDOFF_LIVE = "version: 9\nrepo: demo\noutput_dir: docs/mine\n"
ANNOUNCEMENT_DEAD = (
    "version: 9\nrepo: demo\ndelivery_kind: release-notes\n"
    "in_progress_sources:\n  - docs/pending-migration.md\n"
)
ANNOUNCEMENT_LIVE = (
    "version: 9\nrepo: demo\ndelivery_kind: release-notes\n"
    "in_progress_sources:\n  - kind: path\n    path: docs/pending-migration.md\n"
    "    summary: a migration the announcement must not claim finished\n"
)
# The FIFTH, and the one no review round found: `release_record_path` is DERIVED from
# `output_dir` by `plan_release_prepared_stop.release_record_path`, so declaring it names a
# key nothing in this repo reads. The detector found it on its first sweep of the corpus.
RELEASE_DEAD = "version: 9\nrelease_record_path: charness-artifacts/release/mine.md\n"
RELEASE_LIVE = "version: 9\noutput_dir: charness-artifacts/release-mine\n"

DEAD_CONTROLS = [
    pytest.param("narrative-adapter.yaml", NARRATIVE_DEAD, "source_documents", id="narrative-flow-sequence"),
    pytest.param("quality-adapter.yaml", QUALITY_DEAD, "startup_probes", id="quality-wrong-probe-shape"),
    pytest.param("handoff-adapter.yaml", HANDOFF_DEAD, "artifact_path", id="handoff-unread-key"),
    pytest.param("announcement-adapter.yaml", ANNOUNCEMENT_DEAD, "in_progress_sources", id="announcement-bare-string"),
    pytest.param("release-adapter.yaml", RELEASE_DEAD, "release_record_path", id="release-derived-key"),
]
LIVE_CONTROLS = [
    pytest.param("narrative-adapter.yaml", NARRATIVE_LIVE, id="narrative"),
    pytest.param("quality-adapter.yaml", QUALITY_LIVE, id="quality"),
    pytest.param("handoff-adapter.yaml", HANDOFF_LIVE, id="handoff"),
    pytest.param("announcement-adapter.yaml", ANNOUNCEMENT_LIVE, id="announcement"),
    pytest.param("release-adapter.yaml", RELEASE_LIVE, id="release"),
]


@pytest.mark.parametrize(("filename", "body", "inert_key"), DEAD_CONTROLS)
def test_a_published_dead_control_is_refused_and_names_the_inert_key(filename, body, inert_key):
    result = _replay(_stimulus(filename, body))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert result["documents"][0]["inert_declarations"] == [inert_key]
    assert inert_key in " ".join(result["reasons"])


@pytest.mark.parametrize(("filename", "body"), LIVE_CONTROLS)
def test_the_corrected_document_from_the_same_record_passes(filename, body):
    result = _replay(_stimulus(filename, body))
    assert result["state"] == replay.STIMULUS_EVALUATED, result["reasons"]
    assert result["documents"][0]["inert_declarations"] == []


def test_the_ablation_runs_at_a_speakable_version_not_the_recorded_one():
    """The corpus declares `version: 9` so the reader honors NOTHING; ablating there would
    call every declaration inert and refuse all thirteen honest records. The check has to
    make the version speakable first, and this is what pins that it does."""
    assert replay.with_supported_version(NARRATIVE_LIVE).startswith("version: 1\n")
    assert _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))["state"] == replay.STIMULUS_EVALUATED


def test_the_document_is_ablated_as_text_so_a_malformed_shape_is_not_repaired():
    """Parse-and-re-render would turn the flow sequence back into a block sequence and the
    dead control would resolve as honored -- the detector repairing the defect it detects."""
    assert "[docs/mine-narrative.md]" in replay.without_key(NARRATIVE_DEAD, "repo")
    assert replay.without_key(QUALITY_DEAD, "startup_probes") == "version: 9\nrepo: demo\noutput_dir: docs/mine-q\n"


def test_a_templated_stimulus_names_no_resolver_and_is_refused():
    result = _replay(_stimulus("<skill>-adapter.yaml", "version: 9\nrepo: demo\n"))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "names no public resolver" in " ".join(result["reasons"])


def test_an_unquoted_heredoc_delimiter_is_refused_because_the_shell_rewrites_the_body():
    result = _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE, quote=""))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "UNQUOTED delimiter" in " ".join(result["reasons"])


def test_a_line_this_repos_own_reader_drops_is_refused():
    result = _replay(_stimulus("narrative-adapter.yaml", "version: 9\n  repo: demo\n"))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "does not interpret" in " ".join(result["reasons"])


def test_a_construct_the_reader_refuses_outright_is_a_verdict_and_not_a_traceback():
    """`adapter_lib` RAISES on `version: !!int 9` from the shared parser, so the first cut
    of this module let the ValueError out -- tracebacking on precisely the input class
    `#673` is filed about, which is the defect shape reproduced inside the detector for it.
    Found by this test before review, and it is the reason the parse is guarded."""
    result = _replay(_stimulus("quality-adapter.yaml", "version: !!int 9\nrepo: demo\n"))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "refuses outright" in " ".join(result["reasons"])


def test_a_resolver_that_never_answers_is_refused_rather_than_read_as_agreement():
    """Both runs producing NOTHING must not compare equal and pass as "no inert key". A
    resolver that times out is the reachable form of that, and treating its silence as
    agreement is the exact `a read is not a check` shape this corpus is about."""
    result = _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))
    assert result["state"] == replay.STIMULUS_EVALUATED, "precondition: this document passes"
    original = replay._RESOLVE_TIMEOUT_SECONDS
    try:
        replay._RESOLVE_TIMEOUT_SECONDS = 0.001
        timed_out = _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))
    finally:
        replay._RESOLVE_TIMEOUT_SECONDS = original
    assert timed_out["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "rendered no `data:` payload" in " ".join(timed_out["reasons"])


def test_a_resolver_that_tracebacks_yields_no_data_block_to_compare():
    """`_data_block` is what turns "the resolver answered" into a comparable value, so its
    None arm is the one that must not silently become an empty string that equals itself."""
    assert replay._data_block('Traceback (most recent call last):\n  File "x"\nValueError: no\n') is None
    assert replay._data_block("found: true\ndata:\n  repo: demo\nerrors: []\n") == "data:\n  repo: demo"


def test_a_heredoc_that_writes_something_other_than_an_adapter_is_passed_over():
    """A stimulus may legitimately seed a fixture beside its adapter. Only the
    `*-adapter.yaml` documents are this module's subject; the rest are not its business and
    must not become a refusal."""
    stimulus = (
        "cat > $D/notes.txt <<'EOF'\nnot an adapter\nEOF\n"
        + _stimulus("narrative-adapter.yaml", NARRATIVE_LIVE)
    )
    result = _replay(stimulus)
    assert [document["document"] for document in result["documents"]] == ["narrative-adapter.yaml"]
    assert result["state"] == replay.STIMULUS_EVALUATED, result["reasons"]


@pytest.mark.parametrize(
    ("stimulus", "why"),
    [
        pytest.param("", "no stimulus", id="absent"),
        pytest.param("python3 scripts/check_probe_record.py --record x.md\n", "no adapter", id="no-adapter-document"),
    ],
)
def test_a_stimulus_this_module_cannot_read_says_not_configured_rather_than_passing(stimulus, why):
    result = _replay(stimulus)
    assert result["state"] == replay.STIMULUS_NOT_CONFIGURED, why
    assert result["reasons"]


# --- how the replay verdict folds into the record's -----------------------------------

_RECORD_FIELDS = """\
Claim: the reader refuses instead of returning a charness default
Claim kind: change
Observable: the process exit status
Source ref: scripts/probe_stimulus_replay.py
Source conditions: the adapter declares a version the reader cannot speak
Base ref: aaaaaaa
Head ref: bbbbbbb
Base arm: base-observed
Call sites unproven: none
"""
_QUOTED_SOURCE = 'def top_level_keys(text: str) -> list[str]:'


def _record_text(stimulus_body: str, *, filename: str = "narrative-adapter.yaml") -> str:
    return (
        f"# Probe Record: fold\n\n{_RECORD_FIELDS}\n"
        f"## Source text\n\n```\n{_QUOTED_SOURCE}\n```\n\n"
        f"## Stimulus\n\n```\n{_stimulus(filename, stimulus_body)}```\n\n"
        "## Base observable\n\n```\nartifact_path: charness-artifacts/narrative\n```\n\n"
        "## Head observable\n\n```\nrefusing: the reader honored nothing\n```\n"
    )


def _cli(record: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--repo-root", str(ROOT), "--record", str(record), *flags],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )


def test_a_dead_control_demotes_a_record_the_static_resolver_calls_evaluated(tmp_path):
    """The whole point of #674: this record passes every static check and its reproduction
    steps still do not reproduce."""
    record = tmp_path / "record.md"
    record.write_text(_record_text(NARRATIVE_DEAD), encoding="utf-8")
    assert "state: evaluated" in _cli(record).stdout
    replayed = _cli(record, "--replay-stimulus")
    assert "state: not-established" in replayed.stdout
    assert "the stimulus does not reproduce" in replayed.stdout
    assert _cli(record, "--replay-stimulus", "--require-evaluated").returncode == 1


def test_the_replay_is_opt_in_so_a_close_boundary_does_not_silently_shell_out(tmp_path):
    record = tmp_path / "record.md"
    record.write_text(_record_text(NARRATIVE_DEAD), encoding="utf-8")
    passing = _cli(record, "--require-evaluated")
    assert passing.returncode == 0
    # The KEY at column 0, not the substring: this record cites `probe_stimulus_replay.py`
    # as its source, so a bare substring test passes on the `Source ref:` echo instead.
    assert "\nstimulus_replay:" not in passing.stdout


def test_a_passing_replay_never_promotes_a_record_the_static_resolver_refused(tmp_path):
    """The two mechanisms answer different questions; only the static one can say
    `evaluated`, and a green replay must not launder a record that failed it."""
    record = tmp_path / "record.md"
    record.write_text(_record_text(NARRATIVE_LIVE).replace("Base arm: base-observed", "Base arm: base-unrunnable"), encoding="utf-8")
    replayed = _cli(record, "--replay-stimulus")
    assert "state: not-established" in replayed.stdout
    assert "a base that could not run is not a base that disagreed" in replayed.stdout
