"""#248 CLI contract: the chunker pipeline stages share one predictable
input convention and fail loudly on bad input.

Pins the regression hit while picking up a session via chunked routing:
- each JSON-consuming stage (propose -> chunk-packet -> prepare -> draft) accepts uniform
  ``--input``/``-i`` flags and defaults to stdin, so
  ``parse | propose | chunk-packet | prepare`` composes without a temp file or per-stage
  ``--help`` lookup;
- a malformed input fails at the stage that read it (structured stderr +
  exit 2), instead of masquerading as an opaque JSONDecodeError downstream.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "public" / "handoff" / "scripts"
PARSE = SCRIPTS / "parse_handoff_entries.py"
PROPOSE = SCRIPTS / "propose_merges.py"
PREPARE = SCRIPTS / "prepare_ranker_packet.py"
CHUNK_PACKET = SCRIPTS / "prepare_chunk_packet.py"
DRAFT = SCRIPTS / "draft_goal_from_chunk.py"
HANDOFF = REPO_ROOT / "docs" / "handoff.md"


def _run(args, *, stdin=None):
    return subprocess.run(
        ["python3", *[str(a) for a in args]],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
    )


@pytest.fixture(scope="module")
def entries_json():
    """The first-stage output, used to drive the downstream stages."""
    res = _run([PARSE, "--repo-root", REPO_ROOT])
    assert res.returncode == 0, res.stderr
    return res.stdout


@pytest.fixture(scope="module")
def proposal_json(entries_json):
    res = _run([PROPOSE], stdin=entries_json)
    assert res.returncode == 0, res.stderr
    return res.stdout


def test_parse_accepts_positional_path():
    """`parse_handoff_entries.py docs/handoff.md` works (no `unrecognized
    arguments` — the #248 first-hop complaint)."""
    res = _run([PARSE, HANDOFF])
    assert res.returncode == 0, res.stderr
    assert yaml.safe_load(res.stdout)["ok"] is True


def test_propose_reads_stdin_by_default(entries_json):
    """No flag at all: the stage reads stdin so a plain pipe composes."""
    res = _run([PROPOSE], stdin=entries_json)
    assert res.returncode == 0, res.stderr
    assert "standalone" in yaml.safe_load(res.stdout)


@pytest.mark.parametrize("flag", ["--input", "-i"])
def test_propose_input_flags_are_equivalent(entries_json, proposal_json, tmp_path, flag):
    """`--input` and `-i` name the same input and yield identical output."""
    entries_file = tmp_path / "entries.json"
    entries_file.write_text(entries_json, encoding="utf-8")
    res = _run([PROPOSE, flag, entries_file])
    assert res.returncode == 0, res.stderr
    assert yaml.safe_load(res.stdout) == yaml.safe_load(proposal_json)


def test_prepare_reads_stdin_by_default(proposal_json):
    res = _run([PREPARE], stdin=proposal_json)
    assert res.returncode == 0, res.stderr
    assert yaml.safe_load(res.stdout)["version"] >= 1


def test_prepare_chunk_packet_reads_entries_stdin_by_default(entries_json):
    res = _run([CHUNK_PACKET], stdin=entries_json)
    assert res.returncode == 0, res.stderr
    payload = yaml.safe_load(res.stdout)
    assert payload["version"] >= 1
    assert "sources" in payload
    assert "chunk_proposer_prompt" in payload


@pytest.mark.parametrize("flag", ["--input", "-i"])
def test_prepare_chunk_packet_input_flags_are_equivalent(entries_json, tmp_path, flag):
    entries_file = tmp_path / "entries.json"
    entries_file.write_text(entries_json, encoding="utf-8")
    res = _run([CHUNK_PACKET, flag, entries_file])
    assert res.returncode == 0, res.stderr
    assert "sources" in yaml.safe_load(res.stdout)


@pytest.mark.parametrize("flag", ["--input", "-i"])
def test_prepare_input_flags_are_equivalent(proposal_json, tmp_path, flag):
    proposal_file = tmp_path / "proposal.json"
    proposal_file.write_text(proposal_json, encoding="utf-8")
    res = _run([PREPARE, flag, proposal_file])
    assert res.returncode == 0, res.stderr


@pytest.mark.parametrize("stage,script", [
    ("propose_merges", PROPOSE),
    ("prepare_chunk_packet", CHUNK_PACKET),
    ("prepare_ranker_packet", PREPARE),
    ("draft_goal_from_chunk", DRAFT),
])
def test_unreadable_input_fails_loudly_at_reading_stage(stage, script, tmp_path):
    """Input the stage cannot read must fail HERE with a structured error + exit
    2, not as an opaque decode error two stages later.

    Restated probe, same contract. The old probe was argparse usage text
    (``usage: prepare ... [-h] ...``), chosen because it is not valid JSON. Since
    the stages gained a YAML fallback -- required, because upstream stages now
    emit YAML on stdout -- that exact string IS readable: YAML parses it as the
    mapping ``{"usage": "prepare ... [-h] (argparse leak, not JSON)"}``, so it no
    longer reaches the refusal this test is about. The probe is now input that is
    unparseable as BOTH JSON and YAML, which is what "the stage cannot read it"
    means under the current reader.

    The argparse-leak case is guarded separately, and no longer by this test. It
    was briefly a live defect -- ``prepare_ranker_packet`` accepted that mapping
    and exited 0 with an empty packet -- until ``chunked_routing_cli`` gained a
    pre-YAML guard that refuses raw text starting with ``usage:`` before the
    fallback can launder it. That guard is proved by
    ``test_argparse_usage_text_is_refused_before_the_yaml_fallback`` below; this
    test keeps only the both-parsers-reject case.
    """
    extra = ["--date", "2026-05-29", "--repo-root", tmp_path] if script == DRAFT else []
    res = _run([script, *extra], stdin='{"entries": [1, 2\n')
    assert res.returncode == 2, (res.returncode, res.stdout, res.stderr)
    assert res.stdout.strip() == "", "no half-output on stdout"
    err = yaml.safe_load(res.stderr)
    assert err["ok"] is False
    assert err["stage"] == stage
    assert "not valid YAML or JSON" in err["error"]
    # The operator-facing hint still names the argparse-leak cause it was
    # written for, even though the probe above no longer produces it.
    assert "argparse usage text" in err["hint"]


@pytest.mark.parametrize("stage,script", [
    ("propose_merges", PROPOSE),
    ("prepare_chunk_packet", CHUNK_PACKET),
    ("prepare_ranker_packet", PREPARE),
    ("draft_goal_from_chunk", DRAFT),
])
def test_argparse_usage_text_is_refused_before_the_yaml_fallback(stage, script, tmp_path):
    """The case the YAML fallback briefly laundered, now pinned on every stage.

    `usage: prog [-h]` + `prog: error: ...` is NOT valid JSON but IS a valid YAML
    mapping, so adding the YAML fallback turned a loud upstream failure into a
    readable payload: `prepare_ranker_packet` exited 0 with a complete packet whose
    `standalone`/`merged` were empty. A wrong upstream `--flag` produced a plausible
    empty RESULT instead of an error -- the worst available outcome, because nothing
    downstream can tell it from a real empty answer.

    Parametrized over all four stages rather than the one where it was observed: the
    guard lives in the shared reader, so a stage that stopped routing through it would
    regress silently.
    """
    extra = ["--date", "2026-05-29", "--repo-root", tmp_path] if script == DRAFT else []
    leak = "usage: prog [-h] --input INPUT\nprog: error: unrecognized arguments: --json\n"
    res = _run([script, *extra], stdin=leak)

    assert res.returncode == 2, (res.returncode, res.stdout, res.stderr)
    assert res.stdout.strip() == "", "a laundered leak would emit a plausible packet here"
    err = yaml.safe_load(res.stderr)
    assert err["ok"] is False
    assert err["stage"] == stage
    assert "argparse usage text" in err["error"]


@pytest.mark.parametrize("stage,script", [
    ("propose_merges", PROPOSE),
    ("prepare_chunk_packet", CHUNK_PACKET),
    ("prepare_ranker_packet", PREPARE),
])
@pytest.mark.parametrize("label,payload,expected", [
    (
        "a refusal packet from an upstream stage",
        'ok: false\nstage: propose_merges\nsource: "<stdin>"\n'
        'expects: "an entries array"\nerror: "input file not found"\n',
        "refusal payload",
    ),
    ("empty input", "", "input is empty"),
    ("a bare scalar", "just a stray log line\n", "not a payload"),
])
def test_contaminated_input_is_refused_rather_than_laundered(
    stage, script, label, payload, expected, tmp_path
):
    """The `usage:` guard was a denylist; these are the contaminants it did not name.

    Each of these parses as valid YAML, so the fallback accepted it and the stage read
    its own keys off it with `.get(..., [])` -- producing a COMPLETE packet with empty
    `standalone`/`merged` at exit 0. A wrong upstream step yielding a plausible empty
    RESULT is the worst available outcome, because nothing downstream can tell it from
    a real empty answer.

    The refusal-packet case is the sharpest: `_fail` and `stage_refusal` now emit valid
    YAML themselves, so redirecting a failing stage's stderr onward hands the next stage
    something that parses perfectly and carries none of the fields it reads. Empty input
    is the ordinary shape of that mistake in a pipe -- an upstream stage that exits 2
    writes nothing -- and it used to die with an `AttributeError` traceback, the exact
    opposite of the typed refusal this module's docstring promises.
    """
    source = tmp_path / "contaminated.yaml"
    source.write_text(payload, encoding="utf-8")
    res = _run([script, "--input", source])

    assert res.returncode == 2, (res.returncode, res.stdout, res.stderr)
    assert res.stdout.strip() == "", "a laundered payload would emit a packet here"
    err = yaml.safe_load(res.stderr)
    assert err["ok"] is False
    assert err["stage"] == stage
    assert expected in err["error"], err["error"]


def test_missing_input_file_fails_loudly(tmp_path):
    res = _run([PROPOSE, "--input", tmp_path / "does-not-exist.json"])
    assert res.returncode == 2, (res.stdout, res.stderr)
    err = yaml.safe_load(res.stderr)
    assert err["ok"] is False
    assert err["stage"] == "propose_merges"
    assert "not found" in err["error"]


def test_draft_accepts_uniform_input_flag(tmp_path):
    chunk = {
        "entries": [
            {
                "index": 1,
                "title": "CLI contract smoke",
                "body": "Keep the draft input alias stable.",
                "referenced_paths": ["docs/handoff.md"],
                "referenced_issues": [],
                "referenced_skills": ["handoff"],
                "boundary_tokens": ["docs/handoff.md"],
            }
        ],
        "label": "cli-contract-smoke",
        "objective_summary": "Verify draft accepts the shared input alias.",
    }
    res = _run(
        [DRAFT, "--input", "-", "--date", "2026-05-29", "--slug", "cli-contract-smoke",
         "--repo-root", tmp_path],
        stdin=json.dumps(chunk),
    )
    assert res.returncode == 0, res.stderr
    payload = yaml.safe_load(res.stdout)
    assert payload["ok"] is True
    assert Path(payload["path"]).is_file()
