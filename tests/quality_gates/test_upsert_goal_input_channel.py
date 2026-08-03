"""The goal-scaffolding helper's prose must not cross a shell either.

`append_slice_log.py` got a no-shell channel first; `upsert_goal.py` has the identical
argv channel and is the WORSE of the two to lose text through. `--goal-body` writes the
`## Goal` section — the statement a fresh or compacted session reads first to learn what
the goal IS — and a shell performs command substitution before this program starts, so
the artifact is created with words missing and the run reports `"action": "created"`.

These tests drive a REAL shell (`shell=True`) rather than asserting on the parser,
because the loss happens in the shell and a test that builds `argv` in Python cannot
reproduce it. The first test is the reproduction; the second is the repair, run through
the same shell so the two are a controlled comparison.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "skills" / "public" / "achieve" / "scripts" / "upsert_goal.py"
PROSE = "the type check dropped it, the default won, and the report still said `preserved`"


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HELPER), "--repo-root", str(tmp_path), *args],
        capture_output=True, text=True,
    )


def _created_goal(tmp_path: Path, slug: str = "g") -> Path:
    return tmp_path / "charness-artifacts" / "goals" / f"2026-08-07-{slug}.md"


def test_a_goal_body_through_a_shell_argument_is_silently_truncated(tmp_path: Path) -> None:
    """The reproduction, kept as a test so the repair can never be mistaken for a fix to
    the shell. This still loses text — that is the point: the channel is unfixable from
    inside the process, which is why a second channel exists rather than a validator."""
    command = (
        f'{sys.executable} {HELPER} --repo-root {tmp_path} '
        f'--slug g --date 2026-08-07 --title T --goal-body "{PROSE}"'
    )

    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["action"] == "created"  # exit 0, reports success
    written = _created_goal(tmp_path).read_text(encoding="utf-8")
    assert "preserved" not in written, "the shell ate it before the process started"
    assert "the default won, and the report still said" in written  # a hole, not a failure


def test_the_fields_file_channel_delivers_the_same_goal_body_intact(tmp_path: Path) -> None:
    """The repair, driven through the SAME shell. Only the path the prose travels
    changed, so this is a controlled comparison with the test above."""
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": PROSE}), encoding="utf-8")
    command = (
        f'{sys.executable} {HELPER} --repo-root {tmp_path} '
        f'--slug g --date 2026-08-07 --fields-file {fields}'
    )

    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert PROSE in _created_goal(tmp_path).read_text(encoding="utf-8")


def test_a_multi_line_goal_body_survives_the_file_channel(tmp_path: Path) -> None:
    """A goal body is a SECTION, not a list item, so — unlike a slice-log field — it is
    allowed newlines. Forcing it to one line would push callers straight back to the
    shell for anything real, which is the channel this exists to replace."""
    body = f"{PROSE}\n\nSecond paragraph citing `--fields-file` as well."
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": body}), encoding="utf-8")

    result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))

    assert result.returncode == 0, result.stderr
    assert body in _created_goal(tmp_path).read_text(encoding="utf-8")


def test_a_heading_in_the_goal_body_is_refused_through_every_channel(tmp_path: Path) -> None:
    """The body is written under `## Goal`. A heading line there ends that section early
    and hands `check_goal_artifact.py` a section nobody wrote — silent artifact
    corruption under a `created` verdict, the same class as the shell itself.

    Both channels, because the first round of this repair put the guard inside the
    `--fields-file` loader: the flag channel — which the references document as an
    equally SAFE way to pass prose, and which is safe against the shell — walked
    straight past it and wrote the forged heading with exit 0.
    """
    body = "intro\n\n## Slice Log\n\nforged"
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": body}), encoding="utf-8")

    for index, channel in enumerate((
        ["--fields-file", str(fields)],
        ["--title", "T", "--goal-body", body],
    )):
        # Each channel gets its own repo root: sharing one would let a leaked write from
        # the first iteration be asserted against in the second, reporting the failure
        # under the wrong channel's name.
        root = tmp_path / f"root{index}"
        root.mkdir()
        result = _run(root, "--slug", "g", "--date", "2026-08-07", *channel)
        assert result.returncode != 0, channel
        assert "contains an unfenced markdown heading line" in result.stderr, channel
        assert not _created_goal(root).exists(), "refused before writing anything"


def test_a_fenced_heading_in_the_goal_body_is_allowed(tmp_path: Path) -> None:
    """The false-positive control. Goal bodies in this repo routinely quote commands,
    and `# comment` inside a fenced block is not a heading to any reader — every
    heading check in `goal_artifact_lib` masks fences first. Refusing it would send the
    caller back to the one channel this helper exists to replace, with no way out."""
    body = "Reproduce with:\n\n```bash\n# run the gate\npython3 scripts/run_slice_closeout.py\n```"
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": body}), encoding="utf-8")

    result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))

    assert result.returncode == 0, result.stderr
    assert body in _created_goal(tmp_path).read_text(encoding="utf-8")


def test_a_bare_carriage_return_cannot_forge_a_heading(tmp_path: Path) -> None:
    """`write_text` passes a lone `\\r` through to disk, but every reader of a goal
    artifact uses `read_text`, which is universal-newline: the `\\r` comes BACK as a
    `\\n`. So a guard that only knows `\\n` passed text that became a heading on the
    next read. The helper normalizes before checking and before writing, so the bytes
    on disk agree with the bytes every reader sees."""
    fields = tmp_path / "fields.json"
    fields.write_text(
        json.dumps({"title": "T", "goal-body": "intro\r## Slice Log\r\rforged"}), encoding="utf-8"
    )

    result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))

    assert result.returncode != 0, "a CR that becomes a heading on read must refuse"
    assert "contains an unfenced markdown heading line" in result.stderr
    assert not _created_goal(tmp_path).exists()


def test_a_multi_line_title_is_refused_including_a_bare_carriage_return(tmp_path: Path) -> None:
    """The title is rendered into one `# Achieve Goal: <title>` heading; a newline would
    split it and leave the remainder as loose body text under a truncated heading. A
    lone `\\r` does the same thing one read later, so it refuses too."""
    fields = tmp_path / "fields.json"

    for raw in ("line one\nline two", "line one\rline two"):
        fields.write_text(json.dumps({"title": raw}), encoding="utf-8")
        result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))
        assert result.returncode != 0, raw
        assert "`title` must be single-line" in result.stderr, raw


def test_a_slug_that_lost_everything_is_refused(tmp_path: Path) -> None:
    """`slugify` never raises — it COERCES, and an empty result becomes the literal
    `goal`. So `--slug` emptied by a failed shell substitution did not fail; it created
    `<date>-goal.md` and reported `created`, which is the silent-damage-under-success
    class this helper is being repaired for."""
    for emptied in ("", "!!!", "   "):
        result = _run(tmp_path, "--slug", emptied, "--date", "2026-08-07", "--title", "T")
        assert result.returncode != 0, emptied
        assert "contains nothing usable" in result.stderr, emptied
    assert not (tmp_path / "charness-artifacts" / "goals" / "2026-08-07-goal.md").exists()


def test_a_merely_COERCED_slug_is_not_refused(tmp_path: Path) -> None:
    """The false-positive control, and the reason this guard was narrowed.

    Coercion is not damage: it is GLOBAL. `goal_path` slugifies too, and every sibling
    helper resolves through it, so `--slug PROJ_184` round-tripped across
    `upsert_goal`, `append_slice_log` and `check_goal_artifact` alike. The first cut
    refused any slug `slugify` would rewrite, which broke a correct caller while its
    siblings kept working — and, because the check ran before the `path.exists()`
    branch, it also refused a plain status flip against an artifact created weeks
    earlier. The caller never asked for a filename; it asked for a stable key.

    Caught by the release critique, as the SEVENTH instance this run of a guard placed
    at the boundary that was easy to test rather than the one that breaks the invariant.
    """
    for coerced in ("PROJ_184", "My Goal", "Acme 184 Push"):
        root = tmp_path / coerced.replace(" ", "_")
        root.mkdir()
        result = _run(root, "--slug", coerced, "--date", "2026-08-07", "--title", "T")
        assert result.returncode == 0, (coerced, result.stderr)

    # and the flip path on an EXISTING artifact, which the first cut also refused
    flip = _run(tmp_path / "PROJ_184", "--slug", "PROJ_184", "--date", "2026-08-07", "--status", "active")
    assert flip.returncode == 0, flip.stderr


def test_changed_prose_against_an_existing_artifact_is_refused_not_dropped(tmp_path: Path) -> None:
    """An existing artifact's heading and `## Goal` section are never overwritten —
    correct, and why a re-run cannot destroy a goal's prose. But supplied values were
    DROPPED in silence under `"action": "updated"`, and this slice makes that likelier
    by telling callers to author both fields in a file and re-run the same command.

    Both fields, because repairing only the body would leave the identical silent drop
    on the title — the half-swept sibling that is this whole goal's subject."""
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": "first body"}), encoding="utf-8")
    target = ("--slug", "g", "--date", "2026-08-07")
    assert _run(tmp_path, *target, "--fields-file", str(fields)).returncode == 0

    for changed, expected in (
        ({"title": "T", "goal-body": "revised body"}, "`goal-body`"),
        ({"title": "Renamed", "goal-body": "first body"}, "`title`"),
    ):
        fields.write_text(json.dumps(changed), encoding="utf-8")
        again = _run(tmp_path, *target, "--fields-file", str(fields), "--status", "active")
        assert again.returncode != 0, changed
        assert "refusing to discard" in again.stderr and expected in again.stderr, changed

    written = _created_goal(tmp_path).read_text(encoding="utf-8")
    assert "first body" in written and "revised body" not in written
    assert "Status: draft" in written, "the refusal is before the write, so nothing changed"


def test_re_running_with_unchanged_prose_still_flips_the_status(tmp_path: Path) -> None:
    """The false-positive control for the refusal above, and the reason it compares
    values instead of merely detecting their presence. `SKILL.md`'s bootstrap says
    "scaffold or locate" and runs this command on EVERY invocation, so refusing an
    idempotent re-run would break the helper's own first-listed command from the second
    call onward."""
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": "the body"}), encoding="utf-8")
    target = ("--slug", "g", "--date", "2026-08-07")
    assert _run(tmp_path, *target, "--fields-file", str(fields)).returncode == 0

    again = _run(tmp_path, *target, "--fields-file", str(fields), "--status", "active")

    assert again.returncode == 0, again.stderr
    assert json.loads(again.stdout)["action"] == "updated"
    assert "Status: active" in _created_goal(tmp_path).read_text(encoding="utf-8")


def test_an_empty_flag_cannot_blank_a_non_empty_file_value(tmp_path: Path) -> None:
    """`--goal-body "$(cat missing.txt)"` hands argv an empty string, which is not None,
    so it beat the file and the artifact was created carrying the scaffold placeholder
    under `"action": "created"`. That is this helper's own total-loss shape landing on
    the exact field the channel was built to protect."""
    fields = tmp_path / "fields.json"
    fields.write_text(
        json.dumps({"title": "Real Title", "goal-body": "the real body"}), encoding="utf-8"
    )
    target = ("--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))

    for flag in ("--goal-body", "--title"):
        result = _run(tmp_path, *target, flag, "")
        assert result.returncode != 0, flag
        assert "was passed empty while --fields-file supplies" in result.stderr, flag
        assert not _created_goal(tmp_path).exists()


def test_an_unclosed_fence_is_refused_on_its_own_cause(tmp_path: Path) -> None:
    """`mask_fences` FAILS OPEN on odd parity and returns the raw text — it says so in
    its own docstring, and hands callers `fences_balanced` so they can refuse instead of
    rendering a verdict over a reading they could not establish.

    Both arms were wrong before: a fenced `# comment` got a refusal telling the caller to
    fence a line they had already fenced, and a fence with no `#` inside passed here only
    for `check_goal_artifact.py` — the next documented command — to reject the artifact."""
    fields = tmp_path / "fields.json"
    for body in (
        "Reproduce with:\n\n```bash\n# run the gate\npython3 scripts/x.py\n",
        "Reproduce with:\n\n```bash\npython3 scripts/x.py\n",
    ):
        fields.write_text(json.dumps({"title": "T", "goal-body": body}), encoding="utf-8")
        result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))
        assert result.returncode != 0, body
        assert "leaves a code fence unclosed" in result.stderr, body
        assert not _created_goal(tmp_path).exists()


def test_a_benign_carriage_return_reaches_disk_as_a_newline(tmp_path: Path) -> None:
    """The other half of the CR repair, which a refusal-only test cannot pin: an
    implementation that dropped `_normalize_newlines` and instead taught both guards
    about `\\r` would pass every refusal test here while still writing CR bytes whose
    meaning changes on the next read. The claim is that disk agrees with every reader."""
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": "line one\rline two"}), encoding="utf-8")

    result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))

    assert result.returncode == 0, result.stderr
    raw = _created_goal(tmp_path).read_bytes()
    assert b"\r" not in raw, "a lone CR on disk changes meaning when read back"
    assert "line one\nline two" in _created_goal(tmp_path).read_text(encoding="utf-8")


def test_a_status_flip_needs_no_title(tmp_path: Path) -> None:
    """A title is required to CREATE an artifact and is ignored when updating one, so
    demanding it on a status flip only forced every caller — and every doc example — to
    re-type prose into a shell for a value nothing reads."""
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "Real Title", "goal-body": "body"}), encoding="utf-8")
    target = ("--slug", "g", "--date", "2026-08-07")
    assert _run(tmp_path, *target, "--fields-file", str(fields)).returncode == 0

    flipped = _run(tmp_path, *target, "--status", "active")

    assert flipped.returncode == 0, flipped.stderr
    written = _created_goal(tmp_path).read_text(encoding="utf-8")
    assert "Status: active" in written
    assert "# Achieve Goal: Real Title" in written, "the heading is untouched by the flip"


def test_a_flag_overrides_the_file_and_an_absent_flag_does_not_blank_it(tmp_path: Path) -> None:
    """`None` means "not given", not "empty". Defaulting the flags to `""` would make an
    unpassed flag silently erase its file value — the same silent-loss class again."""
    fields = tmp_path / "fields.json"
    fields.write_text(
        json.dumps({"title": "from file", "goal-body": "body kept"}), encoding="utf-8"
    )

    result = _run(
        tmp_path, "--slug", "g", "--date", "2026-08-07",
        "--fields-file", str(fields), "--title", "from flag",
    )

    assert result.returncode == 0, result.stderr
    written = _created_goal(tmp_path).read_text(encoding="utf-8")
    assert "# Achieve Goal: from flag" in written
    assert "body kept" in written


def test_creating_an_artifact_with_no_title_anywhere_is_refused(tmp_path: Path) -> None:
    """`--title` stopped being `required=True` when the file could supply it — and then
    stopped being an argparse-level check at all, so a status flip need not carry one.
    Both "neither was given" and "given but blank" stay refused on the CREATE path,
    which is the only path where a title is written."""
    for extra in (["--goal-body", "x"], ["--title", "   "]):
        result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", *extra)
        assert result.returncode != 0, extra
        assert "a new artifact needs --title" in result.stderr, extra
        assert not _created_goal(tmp_path).exists()

    fields = tmp_path / "f.json"
    fields.write_text(json.dumps({"title": "   ", "goal-body": "x"}), encoding="utf-8")
    blank = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))
    assert blank.returncode != 0
    assert "a new artifact needs --title" in blank.stderr


def test_the_shared_loader_refusals_are_reachable_through_this_helper(tmp_path: Path) -> None:
    """The parse and its refusals are `goal_cli_args.load_fields_file`, shared with
    `append_slice_log.py`. Asserting them HERE proves this helper is actually wired to
    the shared loader, not merely that the shared loader is correct somewhere else —
    a helper that silently accepted an unknown key would ship the class being repaired.
    """
    fields = tmp_path / "f.json"
    target = ("--slug", "g", "--date", "2026-08-07")

    cases = [
        ("[]", "must contain a JSON object"),
        ('{"title": 7}', "values must be strings"),
        ("{not json", "not valid JSON"),
        ('{"titel": "typo"}', "unknown field(s): titel"),
        ('{"title": "a", "title": "b"}', "repeats field(s): title"),
    ]
    for body, expected in cases:
        fields.write_text(body, encoding="utf-8")
        result = _run(tmp_path, *target, "--fields-file", str(fields))
        assert result.returncode != 0, body
        assert expected in result.stderr, (body, result.stderr)

    fields.write_bytes('{"title": "T"}'.encode("utf-16"))
    enc = _run(tmp_path, *target, "--fields-file", str(fields))
    assert enc.returncode != 0
    assert "not UTF-8" in enc.stderr and "Traceback" not in enc.stderr

    missing = _run(tmp_path, *target, "--fields-file", str(tmp_path / "nope.json"))
    assert missing.returncode != 0
    assert "unreadable" in missing.stderr
