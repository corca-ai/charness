"""In-process unit coverage for the helper internals this run changed.

The behavioural tests for these surfaces drive REAL SUBPROCESSES on purpose: the
defects being guarded (a shell eating a backtick before `argv` exists, an import cycle
that only appears when a module is imported FIRST in a fresh interpreter) are invisible
to an in-process test by construction. Those tests stay, and they are the proof.

But a subprocess is opaque to coverage, so the changed-line mutation lane saw these
files as untouched by any test and refused the push — correctly, by its own rule: it
cannot tell "exercised only through a subprocess" from "not exercised at all".

So this file exercises the same functions IN PROCESS. It is not a second copy of the
behavioural proof; it targets the pure decision helpers those entrypoints delegate to,
where a unit call is the honest shape anyway. Each test names the branch it covers.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


ACHIEVE = ROOT / "skills" / "public" / "achieve" / "scripts"
goal_cli = _load(ACHIEVE / "goal_cli_args.py", "goal_cli_args_unit")
upsert = _load(ACHIEVE / "upsert_goal.py", "upsert_goal_unit")
append_log = _load(ACHIEVE / "append_slice_log.py", "append_slice_log_unit")
imports_check = _load(ROOT / "scripts" / "check_standalone_imports.py", "check_standalone_imports_unit")
merge = _load(ROOT / "scripts" / "quality_policy_merge.py", "quality_policy_merge_unit")


# --- goal_cli_args.load_fields_file: the loader both helpers now share ----------------


def test_load_fields_file_returns_known_keys_and_refuses_the_rest(tmp_path: Path) -> None:
    path = tmp_path / "f.json"
    path.write_text(json.dumps({"title": "T", "goal-body": "B"}), encoding="utf-8")

    assert goal_cli.load_fields_file(path, known={"title", "goal-body"}) == {"title": "T", "goal-body": "B"}

    for body, expected in (
        ('{"nope": "x"}', "unknown field(s): nope"),
        ('{"title": 7}', "values must be strings"),
        ("[]", "must contain a JSON object"),
        ("{not json", "not valid JSON"),
        ('{"title": "a", "title": "b"}', "repeats field(s): title"),
    ):
        path.write_text(body, encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            goal_cli.load_fields_file(path, known={"title", "goal-body"})
        assert expected in str(exc.value), body

    path.write_bytes('{"title": "T"}'.encode("utf-16"))
    with pytest.raises(SystemExit, match="not UTF-8"):
        goal_cli.load_fields_file(path, known={"title"})

    with pytest.raises(SystemExit, match="unreadable"):
        goal_cli.load_fields_file(tmp_path / "missing.json", known={"title"})


def test_the_flag_name_travels_into_the_refusal(tmp_path: Path) -> None:
    """`flag` is a parameter so a future third caller's messages name ITS flag, not a
    hard-coded `--fields-file` inherited from the first caller."""
    path = tmp_path / "f.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(SystemExit, match=r"--other-file must contain"):
        goal_cli.load_fields_file(path, known=set(), flag="--other-file")


# --- upsert_goal decision helpers ----------------------------------------------------


def test_normalize_newlines_collapses_both_crlf_and_lone_cr() -> None:
    assert upsert._normalize_newlines("a\r\nb\rc\nd") == "a\nb\nc\nd"
    assert "\r" not in upsert._normalize_newlines("x\r\r\ny")


def test_reject_unwritable_prose_covers_each_refusal_and_the_clean_path() -> None:
    upsert._reject_unwritable_prose("Title", "a body\n\nwith paragraphs")
    upsert._reject_unwritable_prose("Title", "fenced:\n\n```bash\n# comment\n```")

    with pytest.raises(SystemExit, match="must be single-line"):
        upsert._reject_unwritable_prose("two\nlines", "")
    with pytest.raises(SystemExit, match="leaves a code fence unclosed"):
        upsert._reject_unwritable_prose("T", "intro\n\n```bash\nx\n")
    with pytest.raises(SystemExit, match="unfenced markdown heading"):
        upsert._reject_unwritable_prose("T", "intro\n\n## Slice Log\n")


def test_resolve_slug_passes_a_kebab_slug_and_refuses_a_coerced_one() -> None:
    assert upsert._resolve_slug("acme-184-push") == "acme-184-push"

    for bad, shown in (("Not Kebab", "not-kebab"), ("", "goal"), ("trailing-", "trailing")):
        with pytest.raises(SystemExit) as exc:
            upsert._resolve_slug(bad)
        assert f"would be written as {shown!r}" in str(exc.value), bad


def test_merge_field_prefers_the_flag_unless_it_is_an_empty_override() -> None:
    from_file = {"title": "from file", "goal-body": ""}

    assert upsert._merge_field(None, from_file, "title") == "from file"
    assert upsert._merge_field("from flag", from_file, "title") == "from flag"
    # an empty flag over an EMPTY file value is not a contradiction, so it passes through
    assert upsert._merge_field("", from_file, "goal-body") == ""

    with pytest.raises(SystemExit, match="was passed empty while --fields-file supplies"):
        upsert._merge_field("", from_file, "title")


def test_append_slice_log_keeps_its_own_single_line_rule(tmp_path: Path) -> None:
    """The one shape rule that did NOT move to the shared loader: a slice field renders
    as one `- <label>: <value>` list item."""
    path = tmp_path / "f.json"
    path.write_text(json.dumps({"name": "s", "lessons": "one line"}), encoding="utf-8")
    assert append_log._load_fields_file(path)["lessons"] == "one line"

    path.write_text(json.dumps({"name": "s", "lessons": "a\n### Slice 9: forged"}), encoding="utf-8")
    with pytest.raises(SystemExit, match="must be single-line"):
        append_log._load_fields_file(path)


# --- check_standalone_imports decision helpers ---------------------------------------


def test_is_cycle_matches_both_markers_and_nothing_else() -> None:
    assert imports_check._is_cycle("ImportError: ... partially initialized module ...")
    assert imports_check._is_cycle("most likely due to a CIRCULAR IMPORT")
    assert not imports_check._is_cycle("ModuleNotFoundError: No module named 'yaml'")


def test_is_wrong_shape_only_absorbs_a_missing_SIBLING(tmp_path: Path) -> None:
    (tmp_path / "sibling.py").write_text("", encoding="utf-8")
    target = tmp_path / "entry.py"

    assert imports_check._is_wrong_shape("ModuleNotFoundError: No module named 'sibling'", target)
    # a missing third-party distribution is NOT the wrong-shape signal
    assert not imports_check._is_wrong_shape("ModuleNotFoundError: No module named 'jsonschema'", target)
    # neither is any other error
    assert not imports_check._is_wrong_shape("SyntaxError: invalid syntax", target)


def test_probe_commands_offers_the_package_shape_only_for_scripts_modules() -> None:
    shapes = [name for name, _ in imports_check._probe_commands(ROOT, ROOT / "scripts" / "x.py")]
    assert shapes == ["package", "direct"]

    nested = ROOT / "skills" / "public" / "achieve" / "scripts" / "x.py"
    assert [name for name, _ in imports_check._probe_commands(ROOT, nested)] == ["direct"]


def test_probe_module_reports_a_cycle_and_a_clean_module(tmp_path: Path) -> None:
    """`probe_module` in process: it still SPAWNS a subprocess (that is the point), but
    the classification branches around the spawn are what this covers."""
    pkg = tmp_path / "scripts"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "clean.py").write_text("VALUE = 1\n", encoding="utf-8")
    (pkg / "a.py").write_text("from scripts.b import NAME\nVALUE = 1\n", encoding="utf-8")
    (pkg / "b.py").write_text("from scripts.a import VALUE\nNAME = 'b'\n", encoding="utf-8")

    assert imports_check.probe_module(tmp_path, pkg / "clean.py")["ok"] is True
    assert imports_check.probe_module(tmp_path, pkg / "a.py")["kind"] == "cycle"


def test_run_reports_scope_for_full_partial_and_empty(tmp_path: Path) -> None:
    pkg = tmp_path / "scripts"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "one.py").write_text("VALUE = 1\n", encoding="utf-8")

    full = imports_check.run(tmp_path, changed=None, workers=2, require_git=False)
    assert full["scope"] == "full" and full["ok"] and "checked all 1" in full["scope_note"]

    partial = imports_check.run(tmp_path, changed=[Path("scripts/one.py")], workers=2, require_git=False)
    assert partial["scope"] == "partial" and partial["checked"] == 1
    assert "PARTIAL: checked 1 of 1" in partial["scope_note"]

    empty = imports_check.run(tmp_path, changed=[Path("docs/x.md")], workers=2, require_git=False)
    assert empty["checked"] == 0 and empty["ok"]
    assert "NOTHING WAS CHECKED" in empty["scope_note"]
    assert "unmatched: docs/x.md" in empty["scope_note"]


# --- refilled_policy_subkeys ---------------------------------------------------------


DEFAULTS = {"flat": "d", "block": {"a": "1", "b": "2"}}


def test_refilled_policy_subkeys_covers_every_branch() -> None:
    # non-dict raw: every key reported, coarse
    assert merge.refilled_policy_subkeys("see docs", DEFAULTS, DEFAULTS) == ["block", "flat"]

    # partially-written nested block: dotted leaves
    raw = {"block": {"a": "custom"}}
    merged = {"flat": "d", "block": {"a": "custom", "b": "2"}}
    assert merge.refilled_policy_subkeys(raw, DEFAULTS, merged) == ["block.b", "flat"]

    # fully specified with CUSTOM values: nothing about the block
    raw_full = {"block": {"a": "x", "b": "y"}}
    merged_full = {"flat": "d", "block": {"a": "x", "b": "y"}}
    assert "block" not in merge.refilled_policy_subkeys(raw_full, DEFAULTS, merged_full)

    # nested block absent entirely: the block NAME, not its leaves
    reported = merge.refilled_policy_subkeys({"flat": "d"}, DEFAULTS, DEFAULTS)
    assert "block" in reported and not [n for n in reported if n.startswith("block.")]

    # the merge did not produce the block: block name rather than silence
    for lost in (None, "gone", {}, {"a": "custom"}):
        merged_lost = {"flat": "d", "block": lost}
        assert "block" in merge.refilled_policy_subkeys(raw, DEFAULTS, merged_lost), lost

    # a raw value equal to the default is NOT a refill
    assert "flat" not in merge.refilled_policy_subkeys({"flat": "d"}, {"flat": "d"}, {"flat": "d"})


def test_a_probe_that_times_out_is_reported_as_a_timeout_not_a_cycle(tmp_path: Path) -> None:
    """A hanging import is a real signal and blocks, but it must not be MIS-reported as a
    cycle — a wrong kind sends the reader looking for an import graph that is fine. The
    timeout also falls through to the remaining shapes rather than returning: a `scripts/`
    module whose PACKAGE-shape import hangs still deserves its legitimate direct shape."""
    pkg = tmp_path / "scripts"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "slow.py").write_text("import time\ntime.sleep(30)\n", encoding="utf-8")

    result = imports_check.probe_module(tmp_path, pkg / "slow.py", timeout=1)

    assert result["ok"] is False
    assert result["kind"] == "timeout"
    assert "did not finish within 1s" in result["detail"]


def test_the_json_output_carries_the_scope_note_and_the_findings(tmp_path: Path) -> None:
    """`--json` is the machine surface a gate consumes, so its shape is pinned rather
    than inferred from the human line."""
    import subprocess
    import sys

    pkg = tmp_path / "scripts"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "ok.py").write_text("VALUE = 1\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_standalone_imports.py"),
         "--repo-root", str(tmp_path), "--json"],
        capture_output=True, text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["scope"] == "full"
    assert payload["cycles"] == [] and payload["other_failures"] == []
    assert "checked all 1" in payload["scope_note"]


def test_an_invalid_date_is_reported_by_name_and_exits_2(tmp_path: Path) -> None:
    """`goal_path` raises rather than coercing a malformed date, and the CLI turns that
    into an operator-readable line plus exit 2 — not a traceback."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(ACHIEVE / "upsert_goal.py"), "--repo-root", str(tmp_path),
         "--slug", "g", "--date", "2026-8-7", "--title", "T"],
        capture_output=True, text=True,
    )

    assert result.returncode == 2
    assert "invalid date '2026-8-7'" in result.stdout
    assert "Traceback" not in result.stderr
