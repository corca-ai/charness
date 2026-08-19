"""The stimulus replay: a probe record's reproduction steps must actually reproduce.

PROVENANCE OF THE CORPUS, stated per case rather than in one sweeping sentence. A round-1
bounded review found the first version of this docstring claiming every `_DEAD` constant
was "the verbatim adapter document a probe record published", and refuted it: two were
reconstructions and one was a hybrid of two generations that was never published in any
form. Publishing an unverified provenance claim inside the detector built to catch
unverified claims is this goal's own class, so each constant now carries its source.

- PUBLISHED, verbatim (`git show <sha>:<record>`): `QUALITY_DEAD` (`724fe8a55`),
  `NARRATIVE_DEAD` / `IMPL_DEAD` (`5ecf7575f`), `RELEASE_DEAD` (`f7d3fb70e`, corrected in
  this slice by this detector).
- RECONSTRUCTED from the record's own prose account of a stimulus corrected before it was
  ever committed: `HANDOFF_DEAD` (scaffold-family `## Polarity controls`) and
  `ANNOUNCEMENT_DEAD` (announcement `## Stimulus` preamble). These are what the records SAY
  they ran, not documents git can show.

`_LIVE` twins are the corrected documents, verbatim from the records as they stand.

These tests drive the REAL resolvers as subprocesses. A stub resolver would prove the
ablation loop runs, not that this repo's readers actually ignore the shapes the records
used, which is the whole claim.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts import probe_stimulus_replay as replay

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "check_probe_record.py"


def _stimulus(filename: str, body: str, *, quote: str = "'", directory: str = ".agents") -> str:
    return f"mkdir -p $D/{directory}\ncat > $D/{directory}/{filename} <<{quote}YAML{quote}\n{body}YAML\n"


def _replay(stimulus: str) -> dict:
    return replay.replay_probe_stimulus({"sections": {"stimulus": stimulus}}, repo_root=ROOT)


# --- the measured regression corpus (#674) ------------------------------------------

NARRATIVE_DEAD = (
    "version: 9\nrepo: demo\nremote_name: upstream\n"
    "source_documents: [docs/mine-narrative.md]\nmutable_documents: [docs/mine-narrative.md]\n"
)
NARRATIVE_LIVE = (
    "version: 9\nrepo: demo\nremote_name: upstream\n"
    "source_documents:\n  - docs/mine-narrative.md\n"
    "mutable_documents:\n  - docs/mine-narrative.md\n"
)
IMPL_DEAD = "version: 9\nrepo: demo\nverification_tools: [mytool]\n"
IMPL_LIVE = "version: 9\nrepo: demo\nverification_tools:\n  - mytool\n"
_QUALITY_PROBE_TAIL = (
    "    class: standing\n    startup_mode: warm\n    surface: direct\n"
    "runtime_budgets:\n  pytest: 70000\n"
)
QUALITY_DEAD = (
    "version: 9\nrepo: demo\noutput_dir: docs/mine-q\n"
    'startup_probes:\n  - label: probe-one\n    command: [python3, "-c", "pass"]\n'
    + _QUALITY_PROBE_TAIL
)
QUALITY_LIVE = (
    "version: 9\nrepo: demo\noutput_dir: docs/mine-q\n"
    "startup_probes:\n  - label: probe-one\n    command:\n      - python3\n"
    '      - "-c"\n      - "pass"\n' + _QUALITY_PROBE_TAIL
)
HANDOFF_DEAD = "version: 9\nrepo: demo\nartifact_path: docs/mine/handoff.md\n"
HANDOFF_LIVE = "version: 9\nrepo: demo\noutput_dir: docs/mine\n"
ANNOUNCEMENT_DEAD = (
    "version: 9\nrepo: demo\ndelivery_kind: release-notes\n"
    "release_notes_path: docs/mine-notes.md\n"
    "in_progress_sources:\n  - docs/pending-migration.md\n"
)
ANNOUNCEMENT_LIVE = (
    "version: 9\nrepo: demo\ndelivery_kind: release-notes\n"
    "release_notes_path: docs/mine-notes.md\n"
    "in_progress_sources:\n  - kind: path\n    path: docs/pending-migration.md\n"
    "    summary: a migration the announcement must not claim finished\n"
)
# The FIFTH RECORD in this family to ship a control that could not fail, and the only one
# no review round found: `release_record_path` is DERIVED from `output_dir` by both
# `plan_release_prepared_stop` and `publish_release_claims_review`, so no ADAPTER consumer
# reads the key. The detector found it on its first sweep of the corpus.
RELEASE_DEAD = (
    "version: 9\nrelease_record_path: charness-artifacts/release/mine.md\n"
    'real_host_required_path_globs:\n  - "src/**"\n'
)
RELEASE_LIVE = (
    "version: 9\noutput_dir: charness-artifacts/release-mine\n"
    'real_host_required_path_globs:\n  - "src/**"\n'
)

DEAD_CONTROLS = [
    pytest.param("narrative-adapter.yaml", NARRATIVE_DEAD, ["source_documents: [docs/mine-narrative.md]", "mutable_documents: [docs/mine-narrative.md]"], id="narrative-flow-sequence"),
    pytest.param("impl-adapter.yaml", IMPL_DEAD, ["verification_tools: [mytool]"], id="impl-flow-sequence"),
    # The WHOLE probe entry is inert, not only the flow-sequence `command` that caused it:
    # one unreadable field sends `adapter_validators.startup_probes` back to `[]`, so every
    # sibling stops mattering too. Naming all six is the honest report of what died.
    pytest.param("quality-adapter.yaml", QUALITY_DEAD, [
        "startup_probes:", "- label: probe-one", 'command: [python3, "-c", "pass"]',
        "class: standing", "startup_mode: warm", "surface: direct",
    ], id="quality-flow-sequence-command"),
    pytest.param("handoff-adapter.yaml", HANDOFF_DEAD, ["artifact_path: docs/mine/handoff.md"], id="handoff-unread-key"),
    pytest.param("announcement-adapter.yaml", ANNOUNCEMENT_DEAD, ["in_progress_sources:", "- docs/pending-migration.md"], id="announcement-bare-string"),
    pytest.param("release-adapter.yaml", RELEASE_DEAD, ["release_record_path: charness-artifacts/release/mine.md"], id="release-derived-key"),
]
LIVE_CONTROLS = [
    pytest.param("narrative-adapter.yaml", NARRATIVE_LIVE, id="narrative"),
    pytest.param("impl-adapter.yaml", IMPL_LIVE, id="impl"),
    pytest.param("quality-adapter.yaml", QUALITY_LIVE, id="quality"),
    pytest.param("handoff-adapter.yaml", HANDOFF_LIVE, id="handoff"),
    pytest.param("announcement-adapter.yaml", ANNOUNCEMENT_LIVE, id="announcement"),
    pytest.param("release-adapter.yaml", RELEASE_LIVE, id="release"),
]


@pytest.mark.parametrize(("filename", "body", "inert"), DEAD_CONTROLS)
def test_a_published_dead_control_is_refused_and_names_the_inert_declaration(filename, body, inert):
    result = _replay(_stimulus(filename, body))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert result["documents"][0]["inert_declarations"] == inert


@pytest.mark.parametrize(("filename", "body"), LIVE_CONTROLS)
def test_the_corrected_document_from_the_same_record_passes(filename, body):
    result = _replay(_stimulus(filename, body))
    assert result["state"] == replay.STIMULUS_EVALUATED, result["reasons"]
    assert result["documents"][0]["inert_declarations"] == []


def test_the_ablation_runs_at_a_speakable_version_not_the_recorded_one():
    """The corpus declares `version: 9` so the reader honors NOTHING; ablating there would
    call every declaration inert and refuse all thirteen honest records."""
    assert replay.with_supported_version(NARRATIVE_LIVE).startswith("version: 1\n")
    assert _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))["state"] == replay.STIMULUS_EVALUATED


def test_the_document_is_ablated_as_text_so_a_malformed_shape_is_not_repaired():
    """Parse-and-re-render would turn the flow sequence back into a block sequence and the
    dead control would resolve as honored -- the detector repairing the defect it detects."""
    without_repo = replay.without_line(NARRATIVE_DEAD, 1)
    assert "[docs/mine-narrative.md]" in without_repo
    assert "repo: demo" not in without_repo


def test_ablating_a_block_key_removes_its_whole_block_and_nothing_after_it():
    ablated = replay.without_line(QUALITY_LIVE, 3)
    assert "startup_probes" not in ablated
    assert "command" not in ablated
    assert "runtime_budgets:\n  pytest: 70000" in ablated


# --- the round-1 review's defeating inputs ------------------------------------------


def test_a_nested_unread_declaration_is_caught_even_though_its_parent_is_live():
    """Round 1's sharpest input. Top-level-only ablation worked on the measured records by
    accident: each dead declaration was the sole entry under its key, so the key collapsed
    to its default. Append the ORIGINAL defect key to the CORRECTED quality probe and the
    parent stays live while the record's control still cannot fail."""
    nested = QUALITY_LIVE.replace("    surface: direct\n", "    surface: direct\n    id: probe-one\n")
    result = _replay(_stimulus("quality-adapter.yaml", nested))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert result["documents"][0]["inert_declarations"] == ["id: probe-one"]


def test_a_declaration_that_merely_restates_a_default_is_reported_and_not_refused():
    """The other reason an ablation comes back unchanged, and the one that must NOT refuse.
    `exemption_globs: []` in the prompt-bulk record deletes without effect because the
    declared value IS the reader's default. Varying the value separates the two: an unread
    key cannot move the payload at any value, a restated default can."""
    body = (
        "version: 9\nrepo: demo\nprompt_asset_policy:\n  source_globs:\n    - \"src/**/*.py\"\n"
        "  min_multiline_chars: 40\n  exemption_globs: []\n"
    )
    result = _replay(_stimulus("quality-adapter.yaml", body))
    assert result["state"] == replay.STIMULUS_EVALUATED, result["reasons"]
    assert result["documents"][0]["restated_defaults"] == ["exemption_globs: []"]


def test_the_variant_is_emitted_in_a_shape_this_repos_reader_parses():
    """The discriminator's first cut varied `[]` to the FLOW sequence `["probe-mutation"]`,
    which `adapter_lib` renders as a plain string and every validator drops -- so it
    measured nothing and reported restated defaults as unread keys. The detector emitting
    the exact malformed shape it exists to detect is this corpus's defect class, again."""
    varied = replay.with_mutated_value("version: 1\nexemption_globs: []\n", 1)
    assert varied == "version: 1\nexemption_globs:\n  - probe-mutation\n"
    assert "[" not in varied


def test_a_document_declaring_nothing_but_a_version_cannot_control_anything():
    """The maximal form of the defect class, one line long: the speakable control resolves
    charness defaults, byte-identical to the base observable every record contrasts with."""
    result = _replay(_stimulus("release-adapter.yaml", "version: 9\n"))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "declares nothing but a version" in " ".join(result["reasons"])


def test_a_document_written_where_no_reader_looks_is_refused():
    """This module resolves from `.agents/`, the one directory every adapter reader in this
    repo opens. A stimulus that wrote elsewhere describes a run where NOTHING was read, and
    replaying it from the readable path would manufacture the contrast the record lacked."""
    result = _replay(_stimulus("quality-adapter.yaml", QUALITY_LIVE, directory="adapters"))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "opens `.agents/` only" in " ".join(result["reasons"])


@pytest.mark.parametrize(
    "line",
    [
        pytest.param('cat > "$D/.agents/narrative-adapter.yaml" <<\'YAML\'', id="quoted-path"),
        pytest.param("cat > $D/.agents/narrative-adapter.yaml <<-'YAML'", id="dash-heredoc"),
        pytest.param("cat > $D/.agents/narrative-adapter.yaml <<'YAML'  # write it", id="trailing-comment"),
    ],
)
def test_ordinary_shell_spellings_of_the_same_heredoc_are_read_not_dropped(line):
    """A heredoc this regex misses is dropped SILENTLY and the record renders
    `not-configured`, which does not demote -- so every unmatched spelling was an escape
    hatch, and round 1 enumerated six. Quoting the path is better hygiene, not evasion."""
    result = _replay(f"{line}\n{NARRATIVE_LIVE}YAML\n")
    assert [document["document"] for document in result["documents"]] == ["narrative-adapter.yaml"]
    assert result["state"] == replay.STIMULUS_EVALUATED, result["reasons"]


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("${s}-adapter.yaml", id="shell-expanded"),
        pytest.param("<skill>-adapter.yaml", id="angle-placeholder"),
        pytest.param("quality-adapter.yml", id="yml-spelling-no-reader-opens"),
    ],
)
def test_an_adapter_shaped_target_this_module_cannot_resolve_is_refused_not_dropped(filename):
    result = _replay(_stimulus(filename, NARRATIVE_LIVE))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "reads as an adapter document" in " ".join(result["reasons"])


@pytest.mark.parametrize(
    ("text", "index", "expected"),
    [
        pytest.param("version: 1\nhost_extensions: {}\n", 1, "version: 1\nhost_extensions:\n  probe-mutation: 1\n", id="empty-mapping-becomes-block"),
        pytest.param("version: 1\nmin_multiline_chars: 40\n", 1, "version: 1\nmin_multiline_chars: 41\n", id="number-increments"),
        pytest.param("version: 1\nrepo: demo\n", 1, "version: 1\nrepo: demo-probe-mutation\n", id="scalar-suffixed"),
        pytest.param("version: 1\nglobs:\n  - a\n", 2, "version: 1\nglobs:\n  - a-probe-mutation\n", id="sequence-item-suffixed"),
        pytest.param("version: 1\nglobs:\n  - a\n", 1, None, id="block-parent-owns-no-scalar"),
        pytest.param("version: 1\nnote: |\n  free text\n", 2, None, id="block-scalar-body-owns-no-key"),
    ],
)
def test_the_variant_generator_covers_every_declaration_shape(text, index, expected):
    """A variant this repo's reader cannot parse measures nothing, and `None` is the honest
    answer for a line that owns no scalar to vary -- the caller then reads the deletion
    alone, which for a whole dead block is already the unread verdict."""
    assert replay.with_mutated_value(text, index) == expected


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("Quality-adapter.yaml", id="not-a-skill-directory-name"),
        pytest.param("nosuchskill-adapter.yaml", id="no-such-public-skill"),
    ],
)
def test_a_document_naming_no_public_resolver_is_refused(filename):
    result = _replay(_stimulus(filename, NARRATIVE_LIVE))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "names no public resolver" in " ".join(result["reasons"])


def _resolve_seam(monkeypatch, plan):
    """Drive `_resolve`'s Nth call to a chosen outcome.

    A subprocess failure cannot be provoked for the ABLATED arm alone from outside -- the
    timeout is global, so shortening it fails the whole arm first and returns early. The
    seam is the only way to reach these two branches, and they are the two that decide
    whether an untested declaration reads as a live one."""
    real = replay._resolve
    calls: list[dict] = []

    def fake(repo_root, resolver, sandbox, filename, text):
        outcome = plan[min(len(calls), len(plan) - 1)]
        result = real(repo_root, resolver, sandbox, filename, text) if outcome == "real" else (
            calls[0] if outcome == "echo-whole" else {"data": None, "output": "resolver died", "exit_code": None}
        )
        calls.append(result)
        return result

    monkeypatch.setattr(replay, "_resolve", fake)
    return calls


def test_an_ablated_resolve_that_produced_no_payload_is_reported_not_read_as_liveness(monkeypatch):
    """Compared with the whole arm a None ablation is UNEQUAL, which reads as `this
    declaration is live` -- so a resolver that timed out turned a refusal into a pass."""
    _resolve_seam(monkeypatch, ["real", "dead"])
    result = _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "was never tested" in " ".join(result["reasons"])


def test_a_varied_resolve_that_produced_no_payload_leaves_the_key_unsettled(monkeypatch):
    """When the deletion changed nothing, the VARIANT is what separates an unread key from
    a restated default. If the variant did not resolve, neither verdict was earned."""
    _resolve_seam(monkeypatch, ["real", "echo-whole", "dead"])
    result = _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "was never settled" in " ".join(result["reasons"])


def test_a_construct_the_reader_refuses_outright_is_a_verdict_and_not_a_traceback():
    """`adapter_lib` RAISES on `version: !!int 9` from the shared parser, so the first cut
    let the ValueError out -- tracebacking on precisely the input class `#673` is filed
    about, the defect shape reproduced inside the detector for it."""
    result = _replay(_stimulus("quality-adapter.yaml", "version: !!int 9\nrepo: demo\n"))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "refuses outright" in " ".join(result["reasons"])


def test_a_resolver_that_never_answers_is_refused_rather_than_read_as_agreement():
    """Two silences must not compare equal and pass. The WHOLE arm's None was refused from
    the start; the ABLATED arm's None was not, and compared against a real payload it is
    unequal -- so a timed-out resolver read as `this declaration is live` and turned a
    refusal into a nondeterministic pass. Both arms fail closed now."""
    assert _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))["state"] == replay.STIMULUS_EVALUATED
    original = replay._RESOLVE_TIMEOUT_SECONDS
    try:
        replay._RESOLVE_TIMEOUT_SECONDS = 0.001
        timed_out = _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE))
    finally:
        replay._RESOLVE_TIMEOUT_SECONDS = original
    assert timed_out["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "rendered no `data:` payload" in " ".join(timed_out["reasons"])


def test_an_unquoted_heredoc_delimiter_is_refused_because_the_shell_rewrites_the_body():
    result = _replay(_stimulus("narrative-adapter.yaml", NARRATIVE_LIVE, quote=""))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "UNQUOTED delimiter" in " ".join(result["reasons"])


def test_a_line_this_repos_own_reader_drops_is_refused():
    result = _replay(_stimulus("narrative-adapter.yaml", "version: 9\n  repo: demo\n"))
    assert result["state"] == replay.STIMULUS_NOT_ESTABLISHED
    assert "does not interpret" in " ".join(result["reasons"])


def test_indent_is_measured_in_spaces_as_this_repos_parser_measures_it():
    """A tab-led line is a TOP-LEVEL key to `adapter_lib._line_shape` and an indented
    continuation to anything asking `str.isspace()`. Disagreeing made an honestly declared
    tab-indented key read as inert -- a false refusal on a proof surface."""
    assert replay._indent_of("\tremote_name: upstream") == 0
    assert replay._indent_of("  remote_name: upstream") == 2


def test_a_resolver_that_tracebacks_yields_no_data_block_to_compare():
    assert replay._data_block('Traceback (most recent call last):\n  File "x"\nValueError: no\n') is None
    assert replay._data_block("found: true\ndata:\n  repo: demo\nerrors: []\n") == "data:\n  repo: demo"


def test_a_heredoc_that_writes_something_other_than_an_adapter_is_passed_over():
    """A stimulus may legitimately seed a fixture beside its adapter. Only adapter-shaped
    targets are this module's subject; the rest must not become a refusal."""
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
_QUOTED_SOURCE = "def declaration_lines(text: str) -> list[dict]:"


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
