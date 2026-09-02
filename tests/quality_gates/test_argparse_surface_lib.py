"""Direct in-process cover for the argparse readers both documented-command gates share.

The library had no test file of its own: every behavior was proven only through
`check_documented_command_flags`, which reaches it via
`import_repo_module(__file__, "scripts.core.argparse_surface_lib")` -- a DOTTED module
name, not a path literal, so the changed-line selector could not map it and its
changed lines went unanalyzed locally while the remote broad mirror judged them.
That is the same false-absence the 2026-08-09 remote-CI reconciliation contract
repaired for `check_regenerable_facts.py`. Loading through the path form here is
what makes the mapping real, and the tests below are the coverage that mapping
is supposed to find.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from runtime_bootstrap import import_repo_module

from .support import ROOT

_lib = import_repo_module(ROOT / "scripts/core/argparse_surface_lib.py", "scripts.core.argparse_surface_lib")
_probe_lib = import_repo_module(
    ROOT / "scripts/core/argparse_help_probe.py", "scripts.core.argparse_help_probe"
)
_emit = import_repo_module(ROOT / "scripts/core/gate_report_emit.py", "scripts.core.gate_report_emit")

# The two renderings of a choice set argparse produces. Only the second is a
# claim about what the next positional slot accepts.
HELP_WITH_OPTION_CHOICES = """usage: demo install [-h] [--role {runtime,validation}] [tool_ids ...]

positional arguments:
  tool_ids

options:
  -h, --help            show this help message and exit
  --role {runtime,validation}
"""

HELP_WITH_SUBPARSERS = """usage: demo [-h] {init,update,tool} ...

positional arguments:
  {init,update,tool}
    init                Bootstrap.
    update              Refresh.
    tool                External tools.

options:
  -h, --help  show this help message and exit
"""


def test_subcommand_choices_ignores_an_options_choice_set() -> None:
    """The usage line renders `--role {runtime,validation}` exactly like a
    subparsers action. Reading it as one gave `demo install` subcommands it does
    not have, and every documented `demo install <tool_id>` was reported as an
    invalid subcommand -- three false positives on this repo's own tree."""
    assert _lib.subcommand_choices(HELP_WITH_OPTION_CHOICES) == set()


def test_subcommand_choices_reads_the_positional_block() -> None:
    assert _lib.subcommand_choices(HELP_WITH_SUBPARSERS) == {"init", "update", "tool"}


def _tokens(*words: str) -> tuple[tuple[str, str], ...]:
    return tuple(("flag" if word.startswith("--") else "word", word) for word in words)


def _choices(tree: dict[tuple[str, ...], set[str]]):
    return lambda path: tree.get(path, set())


def test_walk_subcommands_reports_the_word_argparse_would_reject() -> None:
    walked = _lib.walk_subcommands(_tokens("verify"), _choices({(): {"init", "update"}}))
    assert walked == ((), "verify")


def test_walk_subcommands_reports_at_the_depth_that_owns_the_slot() -> None:
    tree = {(): {"tool"}, ("tool",): {"install", "doctor"}}
    assert _lib.walk_subcommands(_tokens("tool", "inspect"), _choices(tree)) == (
        ("tool",),
        "inspect",
    )


def test_walk_subcommands_stops_at_a_parser_with_no_subcommands() -> None:
    """A positional value is not a subcommand claim: `tool install demo-tool`
    walks to `install`, finds no subparsers under it, and never judges the id."""
    tree = {(): {"tool"}, ("tool",): {"install"}}
    walked = _lib.walk_subcommands(_tokens("tool", "install", "demo-tool"), _choices(tree))
    assert walked == (("tool", "install"), None)


def test_walk_subcommands_does_not_judge_a_flag_value_that_spells_a_word() -> None:
    # `--role runtime install` documents --role=runtime; reading `runtime` as the
    # subcommand slot is a blocking false red on a correct doc.
    tree = {(): {"install", "doctor"}}
    walked = _lib.walk_subcommands(
        _tokens("--role", "runtime", "install"),
        _choices(tree),
        lambda _path: {"--role"},
    )
    assert walked == (("install",), None)


def test_resolve_subcommands_stays_tolerant_where_walk_is_strict() -> None:
    """The two walks share `_descend` and differ only in selection policy. The
    flags gate needs tolerance -- a leading top-level flag value must not end the
    walk -- and the subcommand gate needs strictness, or the token argparse would
    reject is the one it skips."""
    tree = {(): {"resolve"}}
    tokens = _tokens("--repo-root", ".", "resolve")
    assert _lib.resolve_subcommands(tokens, _choices(tree), lambda _path: {"--repo-root"}) == (
        "resolve",
    )
    assert _lib.walk_subcommands(tokens, _choices(tree), lambda _path: {"--repo-root"}) == (
        ("resolve",),
        None,
    )


def test_resolve_subcommands_skips_a_leading_word_that_is_not_a_choice() -> None:
    # Where the two genuinely disagree, and why they cannot be one function.
    tree = {(): {"resolve"}}
    tokens = _tokens("extra", "resolve")
    assert _lib.resolve_subcommands(tokens, _choices(tree)) == ("resolve",)
    assert _lib.walk_subcommands(tokens, _choices(tree)) == ((), "extra")


def test_iter_invocation_tails_cuts_each_command_at_the_next_one() -> None:
    """One carrier can name two commands. Reading each to the END of the carrier
    hands the second command's arguments to the first -- a blocking false red on
    a correct doc, since `,` is not a shell operator to cut on."""
    import re

    invocation_re = re.compile(r"python3\s+")
    carrier = "verify: python3 a.py --alpha, python3 b.py --beta"
    tails = list(_lib.iter_invocation_tails(carrier, invocation_re))
    assert [flags for _match, _tokens, flags in tails] == [["--alpha"], ["--beta"]]


def test_help_probe_answers_nothing_for_a_target_that_did_not_probe_clean() -> None:
    probe = _probe_lib.HelpProbe(ROOT)
    target = ("demo",)
    assert probe.subcommand_choices(target) == set()
    probe._results[target] = subprocess.CompletedProcess(
        args=["x"], returncode=2, stdout="", stderr=""
    )
    assert probe.subcommand_choices(target) == set()
    assert probe.accepted_options(target) == set()
    assert probe.options_with_values(target) == set()


def test_help_probe_reads_a_clean_result() -> None:
    probe = _probe_lib.HelpProbe(ROOT)
    target = ("demo",)
    probe._results[target] = subprocess.CompletedProcess(
        args=["x"], returncode=0, stdout=HELP_WITH_SUBPARSERS, stderr=""
    )
    assert probe.subcommand_choices(target) == {"init", "update", "tool"}
    assert "--help" in probe.accepted_options(target)
    assert probe.count() == 1


def test_render_findings_with_skipped_states_the_unproven_tail_on_a_pass() -> None:
    """The half a gate author leaves out: a bare "validated N" reads as full
    coverage, and a gate that skipped anything has not covered it."""
    rendered = _emit.render_findings_with_skipped(
        {"findings": [], "skipped": {"placeholder-path": 2}},
        headline="drift:",
        fix_hint="fix it",
        validated="Validated 5 invocation(s).",
    )
    assert rendered.splitlines() == [
        "Validated 5 invocation(s).",
        "Not proven (2 invocation(s) skipped) — placeholder-path: 2.",
    ]


def test_render_findings_with_skipped_lists_findings_and_the_fix_hint() -> None:
    rendered = _emit.render_findings_with_skipped(
        {"findings": ["a.md:1: broken"], "skipped": {}},
        headline="drift:",
        fix_hint="fix it",
        validated="unused",
        skipped_noun="flag-bearing invocation(s)",
    )
    assert rendered.splitlines() == ["drift:", "- a.md:1: broken", "fix it"]


# `add_subparsers(description=...)` moves the action OUT of `_positionals` into
# its own argument group, so the section header is no longer `positional
# arguments:`. A header-keyed reader returns nothing for such a parser and every
# documented subcommand under it goes silently unproven.
HELP_WITH_SUBPARSERS_IN_A_NAMED_GROUP = """usage: demo [-h] {record,replay} ...

options:
  -h, --help  show this help message and exit

subcommands:
  Commands this tool accepts.

  {record,replay}
    record    Record.
    replay    Replay.
"""

# The same content under a locale that translated argparse's section titles.
HELP_WITH_TRANSLATED_HEADERS = HELP_WITH_SUBPARSERS.replace(
    "positional arguments:", "positionsbezogene Argumente:"
).replace("options:", "Optionen:")


def test_subcommand_choices_reads_a_subparsers_action_in_a_named_group() -> None:
    assert _lib.subcommand_choices(HELP_WITH_SUBPARSERS_IN_A_NAMED_GROUP) == {"record", "replay"}


def test_subcommand_choices_survives_translated_section_headers() -> None:
    """Every argparse section title goes through gettext. A header-keyed reader
    returns nothing for EVERY parser at once under a locale with a catalog, which
    is a repo-wide false verdict that depends on the machine, not the code. A
    brace is not translated."""
    assert _lib.subcommand_choices(HELP_WITH_TRANSLATED_HEADERS) == {"init", "update", "tool"}


@pytest.mark.boundary_contract(
    reason="__main__ dispatch smoke: the root charness CLI must render its real help surface"
)
def test_subcommand_choices_matches_the_real_cli_argparse_surface() -> None:
    """End-to-end against output argparse actually produced, not a hand-written
    fixture: a fixture cannot detect a rendering change, which is the whole risk
    of reading `--help` back."""
    help_text = subprocess.run(
        [sys.executable, "charness", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "COLUMNS": "200", "LC_ALL": "C", "LANGUAGE": ""},
    ).stdout
    declared = _lib.subcommand_choices(help_text)
    assert {"init", "update", "doctor", "version", "tool", "worktree"} <= declared
    assert "help" not in declared, "an option name must not read as a subcommand"


def test_help_probe_pins_the_locale_it_asks_readers_to_parse() -> None:
    # `accepted_options` keys on `usage:` and the option-row shape, both
    # gettext-translated. The probe owns the rendering, so it owns the pin.
    assert _probe_lib.HELP_LOCALE_ENV["LC_ALL"] == "C"
    assert _probe_lib.HELP_LOCALE_ENV["LANGUAGE"] == ""


def test_walk_subcommands_ends_quietly_when_no_free_word_reaches_the_slot() -> None:
    """A parser that declares subcommands, documented with flags only. There is
    no word in the subcommand slot to judge, so the walk ends with no path and no
    verdict -- distinct from both "clean" and "invalid choice"."""
    tree = {(): {"init", "update"}}
    assert _lib.walk_subcommands(_tokens("--repo-root"), _choices(tree)) == ((), None)


def test_one_underscore_choice_does_not_blank_the_whole_parser() -> None:
    """The fix carrying the class it fixed, caught by a round-2 review.

    `subcommand_choices` matches the WHOLE brace group, so with a
    `[a-z0-9-]`-only member class one choice containing `_` or a capital made the
    match fail and returned `set()` for that parser -- which reads as "this
    parser has no subcommands", so every documented subcommand under it went
    unchecked AND unskipped. The gate had just been widened to REPORT `charness
    a retired command` as drift while its authority reader could not represent that
    name at all.
    """
    hyphen = "usage: x [-h] {doctor,sync-support,install} ...\n\npositional arguments:\n  {doctor,sync-support,install}\n"
    assert _lib.subcommand_choices(hyphen) == {"doctor", "sync-support", "install"}
    assert _lib.subcommand_choices(hyphen.replace("sync-support", "sync_support")) == {
        "doctor",
        "sync_support",
        "install",
    }
    assert _lib.subcommand_choices(hyphen.replace("sync-support", "syncSupport")) == {
        "doctor",
        "syncSupport",
        "install",
    }


def test_subcommand_choices_still_ignores_a_braced_group_with_spaces() -> None:
    # The member class widened to "anything argparse puts between braces", which
    # must not swallow a JSON-ish line in an epilog.
    assert _lib.subcommand_choices('epilog:\n  {"key": "value"}\n') == set()


# A command carrier's own invocation regex, so these cases exercise the real boundary
# classes rather than a simplified stand-in. The trailing-quote consumption below is a
# property OF this regex, and a hand-written pattern would not reproduce it.
_INVOCATION_RE = __import__("runpy").run_path("scripts/check_documented_command_flags.py")[
    "INVOCATION_RE"
]


def _attribution(carrier: str) -> list[tuple[str, list[str]]]:
    return [
        (match.group(0), flags)
        for match, _tokens, flags in _lib.iter_invocation_tails(carrier, _INVOCATION_RE)
    ]


def test_a_quoted_script_path_is_not_a_nested_command() -> None:
    """The repo's most common documented shape, and the one a first repair broke.

    `python3 "$SKILL_DIR/scripts/x.py" --flags` quotes the PATH. The invocation regex
    consumes the closing quote, so a rule that treats "inside quotes" as "nested" cuts
    the tail at that quote and drops every flag. Measured when it happened: ~130
    carriers lost their flags and the gate's probe count fell by 54 — a silent coverage
    loss in a blocking gate, which is strictly worse than the false red being fixed.
    """
    carrier = 'python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . --slug <slug>'
    assert _attribution(carrier) == [
        ('"$SKILL_DIR/scripts/upsert_goal.py"', ["--repo-root", "--slug"])
    ]


def test_a_command_inside_another_commands_flag_value_keeps_its_own_flags() -> None:
    """Both commands were wrong at once before the boundary read quotes.

    The outer command lost every flag written after `--test-command`, and the inner one
    was handed `--write-fresh-marker`, which it does not accept — a blocking false red
    on a correct doc, which is what this repo's own command-surface gate hit.
    """
    carrier = (
        "python3 scripts/check_changed_line_mutation_coverage.py --repo-root . "
        '--test-command "python3 scripts/gates_support/run_standing_pytest.py --repo-root ." --write-fresh-marker'
    )
    outer, inner = _attribution(carrier)
    assert outer[1] == ["--repo-root", "--test-command", "--write-fresh-marker"]
    assert inner[1] == ["--repo-root"]


def test_a_nested_command_quoted_with_the_other_quote_character_is_still_bounded() -> None:
    """Single-inside-double is this repo's live spelling for a nested command.

    `.agents/quality-adapter.yaml` writes `"... --test-command 'python3 runner.py ...'"`.
    A single-state quote scanner ignores the inner `'` while inside `"`, so the inner
    command inherits the OUTER span and its tail runs past its own closing quote — the
    exact false attribution the boundary exists to stop.
    """
    carrier = (
        "python3 scripts/sample_mutation_files.py "
        "--test-command 'python3 scripts/gates_support/run_standing_pytest.py' --repo-root ."
    )
    outer, inner = _attribution(carrier)
    assert outer[1] == ["--test-command", "--repo-root"]
    assert inner[1] == []


def test_an_apostrophe_in_prose_does_not_swallow_the_rest_of_the_carrier() -> None:
    """An unterminated quote must yield NO span rather than a runaway one.

    A runaway span would silently stop checking every command after it, which fails in
    the direction a gate must never fail.
    """
    carrier = "python3 scripts/doctor.py --repo-root . # don't worry about this"
    assert _attribution(carrier) == [("python3 scripts/doctor.py", ["--repo-root"])]


def test_an_escaped_quote_does_not_close_a_span() -> None:
    """`.agents/surfaces.json` carries `\\"` inside JSON strings."""
    assert _lib._quoted_spans(r'a "b \" c" d') == [(3, 9)]
