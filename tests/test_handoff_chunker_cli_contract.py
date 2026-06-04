"""#248 CLI contract: the chunker pipeline stages share one predictable
input convention and fail loudly on bad input.

Pins the regression hit while picking up a session via chunked routing:
- each JSON-consuming stage (propose -> chunk-packet -> prepare -> draft) accepts a uniform
  ``--input``/``-i`` plus its legacy alias and defaults to stdin, so
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
    assert json.loads(res.stdout)["ok"] is True


def test_propose_reads_stdin_by_default(entries_json):
    """No flag at all: the stage reads stdin so a plain pipe composes."""
    res = _run([PROPOSE], stdin=entries_json)
    assert res.returncode == 0, res.stderr
    assert "standalone" in json.loads(res.stdout)


@pytest.mark.parametrize("flag", ["--input", "-i", "--entries"])
def test_propose_input_flags_are_equivalent(entries_json, proposal_json, tmp_path, flag):
    """`--input`, `-i`, and the legacy `--entries` alias all name the same
    input and yield identical output."""
    entries_file = tmp_path / "entries.json"
    entries_file.write_text(entries_json, encoding="utf-8")
    res = _run([PROPOSE, flag, entries_file])
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout) == json.loads(proposal_json)


def test_prepare_reads_stdin_by_default(proposal_json):
    res = _run([PREPARE], stdin=proposal_json)
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout)["version"] >= 1


def test_prepare_chunk_packet_reads_entries_stdin_by_default(entries_json):
    res = _run([CHUNK_PACKET], stdin=entries_json)
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["version"] >= 1
    assert "sources" in payload
    assert "chunk_proposer_prompt" in payload


@pytest.mark.parametrize("flag", ["--input", "-i", "--entries"])
def test_prepare_chunk_packet_input_flags_are_equivalent(entries_json, tmp_path, flag):
    entries_file = tmp_path / "entries.json"
    entries_file.write_text(entries_json, encoding="utf-8")
    res = _run([CHUNK_PACKET, flag, entries_file])
    assert res.returncode == 0, res.stderr
    assert "sources" in json.loads(res.stdout)


@pytest.mark.parametrize("flag", ["--input", "--merge-proposal"])
def test_prepare_input_flag_alias(proposal_json, tmp_path, flag):
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
def test_invalid_json_fails_loudly_at_reading_stage(stage, script, tmp_path):
    """A wrong upstream flag whose argparse usage text leaked into the input
    must fail HERE with a structured error + exit 2, not as an opaque
    JSONDecodeError two stages later."""
    extra = ["--date", "2026-05-29", "--repo-root", tmp_path] if script == DRAFT else []
    res = _run([script, *extra], stdin="usage: prepare ... [-h] (argparse leak, not JSON)\n")
    assert res.returncode == 2, (res.returncode, res.stdout, res.stderr)
    assert res.stdout.strip() == "", "no half-output on stdout"
    err = json.loads(res.stderr)
    assert err["ok"] is False
    assert err["stage"] == stage
    assert "not valid JSON" in err["error"]


def test_missing_input_file_fails_loudly(tmp_path):
    res = _run([PROPOSE, "--input", tmp_path / "does-not-exist.json"])
    assert res.returncode == 2, (res.stdout, res.stderr)
    err = json.loads(res.stderr)
    assert err["ok"] is False
    assert err["stage"] == "propose_merges"
    assert "not found" in err["error"]


def test_draft_input_alias_matches_chunk(tmp_path):
    """draft accepts `--input -` (alias of the legacy `--chunk -`)."""
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
    payload = json.loads(res.stdout)
    assert payload["ok"] is True
    assert Path(payload["path"]).is_file()
