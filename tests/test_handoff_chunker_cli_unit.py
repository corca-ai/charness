"""#251 Slice 3: in-process unit tests pinning ``chunked_routing_cli.py``
helper behaviors that survived mutation.

The #248 contract test (``test_handoff_chunker_cli_contract.py``) drives the
stages as subprocesses, which left the shared-helper edges unmutated-killed:
keyword-only enforcement (the ``*`` marker), the help-suffix branch, equality
(not ordering) on the stdin sentinel, the ``hint`` branch, and non-ASCII
preservation. These tests exercise the functions directly so each mutant flips
an observable assertion.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = (
    REPO_ROOT / "skills" / "public" / "handoff" / "scripts" / "chunked_routing_cli.py"
)


def _load_cli():
    spec = importlib.util.spec_from_file_location("chunked_routing_cli", CLI_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def cli():
    return _load_cli()


def _input_help(parser: argparse.ArgumentParser) -> str:
    return next(a.help for a in parser._actions if a.dest == "input")


# --- add_input_argument ----------------------------------------------------


def test_add_input_argument_registers_input_and_default(cli):
    parser = argparse.ArgumentParser()
    cli.add_input_argument(parser, legacy=("--entries",))
    assert parser.parse_args(["--entries", "x.json"]).input == "x.json"
    assert parser.parse_args(["-i", "y.json"]).input == "y.json"
    assert parser.parse_args([]).input == "-"  # default = stdin sentinel


def test_add_input_argument_legacy_is_keyword_only(cli):
    """The ``*`` keyword-only marker (mutated to ``/`` positional-only) is
    enforced — ``legacy`` cannot be passed positionally."""
    parser = argparse.ArgumentParser()
    with pytest.raises(TypeError):
        cli.add_input_argument(parser, ("--entries",))


def test_add_input_argument_help_suffix_branch(cli):
    """``if help_text`` (mutated to ``if not help_text``) gates the suffix."""
    with_help = argparse.ArgumentParser()
    cli.add_input_argument(with_help, help_text="EXTRA-HELP")
    without_help = argparse.ArgumentParser()
    cli.add_input_argument(without_help)
    assert "EXTRA-HELP" in _input_help(with_help)
    assert "EXTRA-HELP" not in _input_help(without_help)
    assert _input_help(without_help).endswith("(default: stdin).")


# --- read_pipeline_json ----------------------------------------------------


def test_read_pipeline_json_stage_expects_keyword_only(cli):
    """``stage``/``expects`` are keyword-only (the ``*`` marker)."""
    with pytest.raises(TypeError):
        cli.read_pipeline_json("-", "stage", "expects")


def test_read_pipeline_json_reads_stdin_sentinel(cli, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"k": 1}'))
    assert cli.read_pipeline_json("-", stage="s", expects="e") == {"k": 1}


def test_read_pipeline_json_sentinel_is_equality_not_ordering(cli, monkeypatch, tmp_path):
    """``input_arg == "-"`` (mutated to ``<=``) must pick stdin ONLY for the
    exact sentinel. ``+probe.json`` is lexically ``<= "-"`` yet must read the
    FILE, so the ordering mutant diverges (it would wrongly read stdin)."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "+probe.json").write_text('{"from": "file"}', encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", io.StringIO("not json from stdin"))
    assert cli.read_pipeline_json("+probe.json", stage="s", expects="e") == {"from": "file"}


def test_read_pipeline_json_missing_file_exits_2(cli, tmp_path):
    with pytest.raises(SystemExit) as exc:
        cli.read_pipeline_json(str(tmp_path / "nope.json"), stage="s", expects="e")
    assert exc.value.code == 2


def test_read_pipeline_json_invalid_json_exits_2_with_hint(cli, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("not json"))
    with pytest.raises(SystemExit) as exc:
        cli.read_pipeline_json("-", stage="propose", expects="entries[]")
    assert exc.value.code == 2
    err = json.loads(capsys.readouterr().err)
    assert err["stage"] == "propose" and "not valid JSON" in err["error"]
    assert "hint" in err  # the decode path supplies a hint


# --- _fail -----------------------------------------------------------------


def test_fail_includes_hint_only_when_given(cli, capsys):
    """``if hint`` (mutated to ``if not hint``) gates the hint key."""
    with pytest.raises(SystemExit):
        cli._fail(stage="s", source="src", expects="e", reason="r", hint="do this")
    assert json.loads(capsys.readouterr().err)["hint"] == "do this"

    with pytest.raises(SystemExit):
        cli._fail(stage="s", source="src", expects="e", reason="r")
    assert "hint" not in json.loads(capsys.readouterr().err)


def test_fail_preserves_non_ascii(cli, capsys):
    """``ensure_ascii=False`` (mutated to ``True``) keeps non-ASCII raw."""
    with pytest.raises(SystemExit):
        cli._fail(stage="s", source="src", expects="e", reason="입력 오류")
    raw = capsys.readouterr().err
    assert "입력 오류" in raw
    assert "\\uc785" not in raw  # the \\uXXXX escape would appear if flipped to True
