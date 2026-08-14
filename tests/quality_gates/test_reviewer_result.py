"""Tests for the bounded-reviewer result diagnostic reader.

`reviewer_result.py` is the recovery floor for a reviewer whose findings never
reached the parent, NOT the delivery contract path (the contract is the unnamed
one-shot spawn documented in `fresh-eye-subagent-review.md` "Result Delivery").
These tests pin the typed statuses, the context-safety cap, and the honest
`layout-not-found` degradation on a host whose transcript shape is unknown.

Fixtures are synthetic and mirror the observed Claude Code record shape; real
session transcripts are never checked into the repo.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

SCRIPT_PATH = ROOT / "skills/shared/scripts/reviewer_result.py"
MODULE = load_script_module("tests.quality_gates.support_reviewer_result", SCRIPT_PATH)


def _run(*args: str, env: dict[str, str] | None = None):
    return run_loaded_script_main("reviewer_result.py", MODULE, *args, env=env)


def _payload(result) -> dict:
    return yaml.safe_load(result.stdout)


def _assistant_text(text: str) -> str:
    message = {
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "stop_reason": "end_turn",
    }
    return json.dumps({"type": "assistant", "message": message})


def _assistant_tool_use() -> str:
    message = {
        "role": "assistant",
        "content": [{"type": "tool_use", "id": "t1", "name": "Read", "input": {}}],
        "stop_reason": "tool_use",
    }
    return json.dumps({"type": "assistant", "message": message})


def _tool_result() -> str:
    content = [{"type": "tool_result", "tool_use_id": "t1", "content": "x" * 5000}]
    return json.dumps({"type": "user", "message": {"role": "user", "content": content}})


def _agent(root: Path, agent_id: str, lines: list[str], **meta: object) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"agent-{agent_id}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {"agentType": "bounded-reviewer", **meta}
    (root / f"agent-{agent_id}.meta.json").write_text(json.dumps(payload), encoding="utf-8")


def _finished(root: Path, agent_id: str, text: str, **meta: object) -> None:
    _agent(root, agent_id, [_assistant_tool_use(), _tool_result(), _assistant_text(text)], **meta)


def test_get_returns_only_the_final_text_block(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "aportability-1", "FINDING: portable\n- one", name="portability-1")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "portability-1"))

    assert payload["status"] == "found"
    assert payload["text"] == "FINDING: portable\n- one"
    assert payload["truncated"] is False
    assert payload["diagnostic_only"] is True
    # The bulky tool_result body must never ride along into the caller.
    assert "x" * 100 not in json.dumps(payload)


def test_found_exits_zero_and_names_the_resolved_root(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "a1", "done", name="lens-1")

    result = _run("get", "--transcript-root", str(root), "--agent", "lens-1")

    assert result.returncode == 0
    assert _payload(result)["transcript_root"] == str(root)


def test_selector_matches_transcript_id_as_well_as_name(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "a9f0", "by id")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "a9f0"))

    assert payload["status"] == "found"
    assert payload["agent"]["id"] == "a9f0"


def test_unfinished_transcript_reports_still_running_without_text(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _agent(root, "a2", [_assistant_tool_use(), _tool_result()], name="mid-flight")

    result = _run("get", "--transcript-root", str(root), "--agent", "mid-flight")
    payload = _payload(result)

    assert result.returncode == 1
    assert payload["status"] == "still-running"
    assert payload["text"] is None
    assert "died mid-turn" in payload["note"]


def test_allow_partial_returns_last_text_block_marked_partial(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _agent(root, "a3", [_assistant_text("half a review"), _tool_result()], name="stalled")

    result = _run("get", "--transcript-root", str(root), "--agent", "stalled", "--allow-partial")
    payload = _payload(result)

    assert result.returncode == 0
    assert payload["status"] == "partial"
    assert payload["text"] == "half a review"
    assert "not a confirmed final result" in payload["note"]


def test_unknown_selector_reports_not_found(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "a4", "done", name="present")

    result = _run("get", "--transcript-root", str(root), "--agent", "absent")

    assert result.returncode == 1
    assert _payload(result)["status"] == "not-found"


def test_multiple_matches_report_ambiguous_with_candidates_but_no_text(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "a5", "one", name="lens-a")
    _finished(root, "a6", "two", name="lens-b")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "lens"))

    assert payload["status"] == "ambiguous"
    assert {agent["name"] for agent in payload["agents"]} == {"lens-a", "lens-b"}
    assert "text" not in payload


def test_exact_match_wins_over_substring(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "a7", "exact", name="lens")
    _finished(root, "a8", "longer", name="lens-extended")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "lens"))

    assert payload["status"] == "found"
    assert payload["text"] == "exact"


def test_max_chars_caps_a_pathological_final_message(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "aflood", "y" * 200_000, name="flood")

    payload = _payload(
        _run("get", "--transcript-root", str(root), "--agent", "flood", "--max-chars", "64")
    )

    assert payload["status"] == "found"
    assert len(payload["text"]) == 64
    assert payload["truncated"] is True
    assert payload["text_chars"] == 200_000


def test_default_cap_applies_without_an_explicit_flag(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "aflood2", "z" * 50_000, name="flood2")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "flood2"))

    assert payload["truncated"] is True
    assert len(payload["text"]) == MODULE._DEFAULT_MAX_CHARS


def test_list_enumerates_reviewers_without_returning_any_text(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _finished(root, "a10", "secret findings", name="lens-1", description="Portability")
    _agent(root, "a11", [_assistant_tool_use()], name="lens-2")

    result = _run("list", "--transcript-root", str(root))
    payload = _payload(result)

    assert result.returncode == 0
    assert [agent["name"] for agent in payload["agents"]] == ["lens-1", "lens-2"]
    assert "secret findings" not in result.stdout
    assert all("text" not in agent for agent in payload["agents"])


def test_unresolvable_layout_degrades_honestly_instead_of_guessing(tmp_path: Path) -> None:
    env = {"HOME": str(tmp_path / "home"), "PATH": "/usr/bin:/bin"}

    result = _run("list", "--repo-root", str(tmp_path / "repo"), env=env)
    payload = _payload(result)

    assert result.returncode == 3
    assert payload["status"] == "layout-not-found"
    assert payload["transcript_root"] is None
    assert "--transcript-root" in payload["note"]
    assert "Codex" in payload["note"]


def test_env_override_resolves_the_root_when_no_flag_is_passed(tmp_path: Path) -> None:
    root = tmp_path / "elsewhere"
    _finished(root, "a12", "from env", name="env-lens")
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "CHARNESS_REVIEWER_TRANSCRIPT_ROOT": str(root),
    }

    payload = _payload(_run("get", "--agent", "env-lens", env=env))

    assert payload["layout"] == "env"
    assert payload["text"] == "from env"


def test_missing_transcript_root_is_a_usage_error(tmp_path: Path) -> None:
    result = _run("get", "--transcript-root", str(tmp_path / "nope"), "--agent", "x")

    assert result.returncode == 2
    assert "not a directory" in _payload(result)["error"]


def test_claude_layout_resolves_most_recent_session_and_reports_it(tmp_path: Path) -> None:
    home = tmp_path / "home"
    repo = tmp_path / "codes" / "proj"
    slug = MODULE._slugify_repo_root(str(repo))
    older = home / ".claude" / "projects" / slug / "sess-old" / "subagents"
    newer = home / ".claude" / "projects" / slug / "sess-new" / "subagents"
    _finished(older, "a13", "old", name="old-lens")
    _finished(newer, "a14", "new", name="new-lens")
    os.utime(older, (1_600_000_000, 1_600_000_000))

    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    payload = _payload(_run("get", "--repo-root", str(repo), "--agent", "new-lens", env=env))

    assert payload["layout"] == "claude-code"
    assert payload["session"] == "sess-new"
    assert payload["session_resolution"] == "most-recent"


def test_unknown_session_on_a_resolved_layout_is_not_a_host_claim(tmp_path: Path) -> None:
    """A mistyped session id must not be recordable as "this host has no layout"."""
    home = tmp_path / "home"
    repo = tmp_path / "codes" / "proj"
    slug = MODULE._slugify_repo_root(str(repo))
    _finished(home / ".claude/projects" / slug / "sess-real" / "subagents", "a16", "hi")
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}

    result = _run("list", "--repo-root", str(repo), "--session", "typo", env=env)
    payload = _payload(result)

    assert result.returncode == 1
    assert payload["status"] == "session-not-found"
    assert payload["sessions"] == ["sess-real"]
    assert payload["session_count"] == 1
    assert "Codex" not in json.dumps(payload)


def test_unknown_session_with_no_layout_at_all_is_layout_not_found(tmp_path: Path) -> None:
    env = {"HOME": str(tmp_path / "home"), "PATH": "/usr/bin:/bin"}

    result = _run(
        "list", "--repo-root", str(tmp_path / "repo"), "--session", "no-such-session", env=env
    )

    assert result.returncode == 3
    assert _payload(result)["status"] == "layout-not-found"


def test_trailing_text_beside_a_tool_call_is_not_a_finished_result(tmp_path: Path) -> None:
    """A mid-loop preamble that happens to be the last flushed record is not `found`."""
    root = tmp_path / "subagents"
    mixed = json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Let me read the file."},
                    {"type": "tool_use", "id": "t2", "name": "Read", "input": {}},
                ],
                "stop_reason": "tool_use",
            },
        }
    )
    _agent(root, "a17", [mixed], name="preamble")

    result = _run("get", "--transcript-root", str(root), "--agent", "preamble")

    assert result.returncode == 1
    assert _payload(result)["status"] == "still-running"


def test_layout_without_stop_reason_still_resolves_positionally(tmp_path: Path) -> None:
    """Hosts that do not record stop reasons must not be silently unreadable."""
    root = tmp_path / "subagents"
    record = json.dumps(
        {
            "type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "text", "text": "final"}]},
        }
    )
    _agent(root, "a18", [record], name="no-stop-reason")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "no-stop-reason"))

    assert payload["status"] == "found"
    assert payload["text"] == "final"


def test_trailing_non_turn_record_does_not_hide_a_finished_reviewer(tmp_path: Path) -> None:
    """Hosts that append summary/usage records after the final message exist."""
    root = tmp_path / "subagents"
    trailer = json.dumps({"type": "summary", "summary": "session ended"})
    _agent(root, "a19", [_assistant_text("real findings"), trailer], name="trailed")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "trailed"))

    assert payload["status"] == "found"
    assert payload["text"] == "real findings"


def test_explicit_null_stop_reason_is_treated_as_unfinished(tmp_path: Path) -> None:
    """Absent means "host does not report it"; null means "turn not closed"."""
    root = tmp_path / "subagents"
    record = json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "streaming"}],
                "stop_reason": None,
            },
        }
    )
    _agent(root, "a20", [record], name="null-stop")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "null-stop"))

    assert payload["status"] == "still-running"


def test_identifier_and_path_fields_are_never_truncated(tmp_path: Path) -> None:
    """A clipped id would not round-trip back into --agent; a clipped path lies."""
    root = tmp_path / "subagents"
    long_id = "a" + "b" * 210
    _finished(root, long_id, "ok", name="long-id")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "long-id"))

    assert payload["agent"]["id"] == long_id
    assert Path(payload["agent"]["file"]).is_file()


def test_list_bounds_agent_count_and_metadata_length(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    for index in range(MODULE._MAX_AGENTS + 5):
        _finished(root, f"a{index:04d}", "x", name=f"lens-{index}", description="d" * 5000)

    payload = _payload(_run("list", "--transcript-root", str(root)))

    assert payload["agent_count"] == MODULE._MAX_AGENTS + 5
    assert len(payload["agents"]) == MODULE._MAX_AGENTS
    assert all(len(agent["description"]) == 200 for agent in payload["agents"])


def test_corrupt_records_do_not_crash_the_read(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    _agent(root, "a15", ["{not json", "", _assistant_text("survived")], name="corrupt")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "corrupt"))

    assert payload["status"] == "found"
    assert payload["text"] == "survived"


def test_missing_meta_file_still_lists_and_reads_the_transcript(tmp_path: Path) -> None:
    root = tmp_path / "subagents"
    root.mkdir(parents=True)
    (root / "agent-abare.jsonl").write_text(_assistant_text("no meta") + "\n", encoding="utf-8")

    payload = _payload(_run("get", "--transcript-root", str(root), "--agent", "abare"))

    assert payload["status"] == "found"
    assert payload["agent"]["name"] is None


def test_script_carries_the_diagnostic_not_contract_framing() -> None:
    text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "NOT THE DELIVERY CONTRACT PATH" in text
    assert "never sleeps, retries, or polls" in text


def test_reference_points_at_the_helper_without_issue_anchors() -> None:
    reference = ROOT / "skills/shared/references/fresh-eye-subagent-review.md"
    text = reference.read_text(encoding="utf-8")

    assert "reviewer_result.py" in text
    assert "diagnostic" in text.split("## Result Delivery", 1)[1]
