"""The slice-log helper's prose must not cross a shell.

Free prose delivered as a shell ARGUMENT has an unguardable lossy layer in front of
it. A slice report cites identifiers, so it is full of backticks; the shell performs
command substitution before the process starts, and the helper receives well-formed
text with words missing, writes it, and reports `"action": "appended"` with exit 0.
No validation inside the process can detect that — there is nothing left to compare
the text against. The observed instance lost three slice-log lines and was caught
only by reading the file back.

These tests drive a REAL shell (`shell=True`) rather than asserting on the parser,
because the loss happens in the shell and a test that builds `argv` in Python cannot
reproduce it. The first test is the reproduction; the second is the repair.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "skills" / "public" / "achieve" / "scripts" / "append_slice_log.py"
PROSE = "the type check dropped it, the default won, and the report still said `preserved`"


def _goal(tmp_path: Path) -> Path:
    path = tmp_path / "charness-artifacts" / "goals" / "2026-08-06-g.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x.md`\n\n## Slice Log\n",
        encoding="utf-8",
    )
    return path


def test_prose_through_a_shell_argument_is_silently_truncated(tmp_path: Path) -> None:
    """The reproduction, kept as a test so the repair cannot be mistaken for a fix to
    the shell. This still loses text — that is the point: the channel is unfixable from
    inside, which is why a second channel exists rather than a validator."""
    goal = _goal(tmp_path)
    command = (
        f'{sys.executable} {HELPER} --repo-root {tmp_path} --goal-path {goal} '
        f'--name s --lessons "{PROSE}"'
    )

    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["action"] == "appended"  # exit 0, reports success
    written = goal.read_text(encoding="utf-8")
    assert "preserved" not in written, "the shell ate it before the process started"
    assert "the default won, and the report still said" in written  # a hole, not a failure


def test_the_fields_file_channel_delivers_the_same_prose_intact(tmp_path: Path) -> None:
    """The repair, driven through the SAME shell. Only the path the prose travels
    changed, so this is a controlled comparison with the test above."""
    goal = _goal(tmp_path)
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"name": "s", "lessons": PROSE}), encoding="utf-8")
    command = (
        f'{sys.executable} {HELPER} --repo-root {tmp_path} --goal-path {goal} '
        f'--fields-file {fields}'
    )

    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert PROSE in goal.read_text(encoding="utf-8")


def test_an_unknown_field_name_is_refused_rather_than_ignored(tmp_path: Path) -> None:
    """A typo in a file the caller cannot see the effect of is the same silent-loss
    shape: the run would report `appended` over a record missing that field."""
    goal = _goal(tmp_path)
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"name": "s", "lesson": "typo"}), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(HELPER), "--repo-root", str(tmp_path), "--goal-path", str(goal),
         "--fields-file", str(fields)],
        capture_output=True, text=True,
    )

    assert result.returncode != 0
    assert "unknown field(s): lesson" in result.stderr


def test_a_flag_overrides_the_file_and_an_absent_flag_does_not_blank_it(tmp_path: Path) -> None:
    """`None` means "not given", not "empty". Defaulting the flags to `""` would make
    every unpassed flag silently erase its file value — the same class again."""
    goal = _goal(tmp_path)
    fields = tmp_path / "fields.json"
    fields.write_text(
        json.dumps({"name": "s", "lessons": "from file", "objective": "kept"}), encoding="utf-8"
    )

    subprocess.run(
        [sys.executable, str(HELPER), "--repo-root", str(tmp_path), "--goal-path", str(goal),
         "--fields-file", str(fields), "--lessons", "from flag"],
        capture_output=True, text=True, check=True,
    )

    written = goal.read_text(encoding="utf-8")
    assert "- Lessons carried forward: from flag" in written
    assert "- Objective: kept" in written


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HELPER), "--repo-root", str(tmp_path), *args],
        capture_output=True, text=True,
    )


def test_every_fields_file_refusal_names_its_cause(tmp_path: Path) -> None:
    """A refusal nobody can act on is a refusal that gets worked around.

    Each malformed input gets its OWN message rather than one generic parse error,
    because the caller wrote this file blind: the whole point of the channel is that
    the prose never crossed a shell, so the only feedback they get is this sentence.
    """
    goal = _goal(tmp_path)
    fields = tmp_path / "f.json"
    cases = [
        ("[]", "must contain a JSON object"),
        ('{"name": 7}', "values must be strings"),
        ("{not json", "not valid JSON"),
    ]
    for body, expected in cases:
        fields.write_text(body, encoding="utf-8")
        result = _run(tmp_path, "--goal-path", str(goal), "--fields-file", str(fields))
        assert result.returncode != 0, body
        assert expected in result.stderr, (body, result.stderr)

    missing = _run(tmp_path, "--goal-path", str(goal), "--fields-file", str(tmp_path / "nope.json"))
    assert missing.returncode != 0
    assert "unreadable" in missing.stderr


def test_a_run_with_no_name_anywhere_is_refused(tmp_path: Path) -> None:
    """`--name` stopped being `required=True` when the file could supply it, so the
    "neither was given" case became reachable and has to refuse rather than write a
    slice heading with an empty name."""
    goal = _goal(tmp_path)

    neither = _run(tmp_path, "--goal-path", str(goal), "--lessons", "x")
    assert neither.returncode != 0
    assert "provide --name, or --fields-file" in neither.stderr

    fields = tmp_path / "f.json"
    fields.write_text(json.dumps({"name": "   ", "lessons": "x"}), encoding="utf-8")
    blank = _run(tmp_path, "--goal-path", str(goal), "--fields-file", str(fields))
    assert blank.returncode != 0
    assert "slice name is empty" in blank.stderr


def test_the_slug_and_date_selector_resolves_and_refuses(tmp_path: Path) -> None:
    """`goal_cli_args.resolve_goal_path` is the one statement of "which file is the
    goal", now shared by two helpers — so its selector and both of its refusals are
    tested once, here, rather than inferred from either caller."""
    goal = _goal(tmp_path)
    fields = tmp_path / "f.json"
    fields.write_text(json.dumps({"name": "s"}), encoding="utf-8")

    resolved = _run(tmp_path, "--slug", "g", "--date", "2026-08-06", "--fields-file", str(fields))
    assert resolved.returncode == 0, resolved.stderr
    assert json.loads(resolved.stdout)["path"] == str(goal)

    partial = _run(tmp_path, "--slug", "g", "--date", "", "--fields-file", str(fields))
    assert partial.returncode != 0
    assert "provide --goal-path, or both --slug and --date" in partial.stderr

    malformed = _run(tmp_path, "--slug", "g", "--date", "2026-8-6", "--fields-file", str(fields))
    assert malformed.returncode != 0
    assert "invalid date" in malformed.stderr
