from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from .support import ROOT

# A stand-in for the real CLI. Two levels of subparsers, plus the two shapes that
# produced false positives in the first design: an OPTION with `choices=`
# (rendered `{runtime,validation}` in the usage line) and a free positional under
# a leaf subcommand.
CLI = """
import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")
subparsers.add_parser("update")
tool = subparsers.add_parser("tool")
tool_sub = tool.add_subparsers(dest="tool_command")
install = tool_sub.add_parser("install")
install.add_argument("tool_ids", nargs="*")
install.add_argument("--recommendation-role", choices=["runtime", "validation"])
tool_sub.add_parser("doctor")
tool_sub.add_parser("sync-support")
parser.parse_args()
"""

BROKEN_CLI = """
import sys
sys.exit(3)
"""


@pytest.fixture(scope="module")
def gate():
    spec = importlib.util.spec_from_file_location(
        "check_documented_subcommands", ROOT / "scripts" / "check_documented_subcommands.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _repo(
    tmp_path: Path,
    doc: str = "",
    *,
    cli: str = CLI,
    doc_path: str = "docs/guide.md",
    extra: dict[str, str] | None = None,
) -> Path:
    root = tmp_path / "repo"
    root.mkdir(parents=True, exist_ok=True)
    (root / "charness").write_text(cli, encoding="utf-8")
    for rel, body in {doc_path: doc, **(extra or {})}.items():
        written = root / rel
        written.parent.mkdir(parents=True, exist_ok=True)
        written.write_text(body, encoding="utf-8")
    return root


def _report(gate, root: Path) -> dict:
    return gate.build_report(root)


def _findings(gate, root: Path) -> list[str]:
    return list(_report(gate, root)["findings"])


def _fence(*lines: str, language: str = "bash") -> str:
    return "\n".join([f"```{language}", *lines, "```", ""])


def test_documented_subcommand_the_cli_never_declared_is_reported(gate, tmp_path: Path) -> None:
    """The motivating violation, and the fail-before tripwire for this gate.

    `charness verify` was live in this repo's shipped prose AND in
    `DEFAULT_CANONICAL_GATE_PATTERNS` as `\\bcharness\\s+verify\\b`, naming a
    subcommand that has never existed. `domain_language_contract`'s
    hand-declared `deprecated_aliases` list could not see it: the list only
    carries names someone remembered to retire.
    """
    root = _repo(tmp_path, _fence("charness verify"))
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "docs/guide.md:2" in findings[0]
    assert "`charness` has no subcommand `verify`" in findings[0]


def test_every_retired_alias_the_declared_list_carried_is_caught_by_derivation(gate, tmp_path: Path) -> None:
    """The replacement proof for `domain_language_contract`'s `deprecated_aliases`.

    That list carried exactly three strings, all retired `charness` invocation
    forms: `charness install <tool>`, `charness sync-support`, and `charness
    update-tools`. Derivation rejects all three without being told any of them --
    and unlike the list, it also rejects the fourth retirement nobody remembers
    to declare.
    """
    doc = _fence("charness install pkg", "charness sync-support", "charness update-tools")
    findings = _findings(gate, _repo(tmp_path, doc))
    assert len(findings) == 3
    assert {"install", "sync-support", "update-tools"} == {
        finding.rsplit("`", 2)[1] for finding in findings
    }


def test_declared_subcommand_passes(gate, tmp_path: Path) -> None:
    assert _findings(gate, _repo(tmp_path, _fence("charness update --dry-run"))) == []


def test_nested_subcommand_drift_is_reported_against_its_own_parser(gate, tmp_path: Path) -> None:
    # Depth is the point: a rename of `tool doctor` is invisible to a check that
    # only proves the first token resolves.
    findings = _findings(gate, _repo(tmp_path, _fence("charness tool inspect")))
    assert len(findings) == 1
    assert "`charness tool` has no subcommand `inspect`" in findings[0]


def test_positional_argument_under_a_leaf_subcommand_is_not_judged(gate, tmp_path: Path) -> None:
    """`charness tool install cautilus` -- three false positives on the real tree.

    An option's `choices=` renders `{runtime,validation}` into the usage line
    exactly like a subparsers action, so a usage-wide read gave `install`
    subcommands it does not have and rejected every documented tool id. The
    authority is the `positional arguments:` block.
    """
    assert _findings(gate, _repo(tmp_path, _fence("charness tool install cautilus"))) == []


def test_option_value_that_spells_a_subcommand_does_not_reroute_the_walk(gate, tmp_path: Path) -> None:
    root = _repo(tmp_path, _fence("charness tool install --recommendation-role runtime pkg"))
    assert _findings(gate, root) == []


def test_prose_mention_of_the_product_name_is_not_an_invocation(gate, tmp_path: Path) -> None:
    # 72 hits across 36 tokens when all prose is scanned; that is what makes the
    # carrier rule load-bearing rather than a tidiness preference.
    root = _repo(tmp_path, "charness verify runs nowhere, and charness itself ships no such thing.\n")
    assert _findings(gate, root) == []


def test_inline_code_span_in_prose_is_scanned(gate, tmp_path: Path) -> None:
    root = _repo(tmp_path, "Operators run `charness verify` after install.\n")
    assert len(_findings(gate, root)) == 1


def test_comment_line_inside_a_shell_fence_is_skipped(gate, tmp_path: Path) -> None:
    # One of the three surviving hits in the design measurement was exactly this.
    assert _findings(gate, _repo(tmp_path, _fence("# charness verify is not a thing"))) == []


def test_non_shell_fence_is_not_scanned(gate, tmp_path: Path) -> None:
    # `text` fences carry sample OUTPUT, and `docs/generated/cli-reference.md`
    # alone has 41 of them.
    assert _findings(gate, _repo(tmp_path, _fence("charness verify", language="text"))) == []


def test_undeclared_fence_is_not_scanned(gate, tmp_path: Path) -> None:
    assert _findings(gate, _repo(tmp_path, _fence("charness verify", language=""))) == []


def test_parenthesized_attribution_is_not_read_as_an_invocation(gate, tmp_path: Path) -> None:
    """`# >>> mutation_testing (charness propose) >>>` names the STAGE that wrote a
    block, not a command to run. It is a literal in `propose_mutation_testing.py`
    and is already written into consumer adapters, where it doubles as the
    idempotence marker -- so reading it as drift would have cost a compatibility
    break to satisfy a gate."""
    root = _repo(tmp_path, "The block is fenced by `# >>> mutation_testing (charness propose) >>>`.\n")
    assert _findings(gate, root) == []


def test_command_substitution_is_read_as_an_invocation(gate, tmp_path: Path) -> None:
    # The other half of that boundary: `$(` really does invoke.
    root = _repo(tmp_path, _fence('version="$(charness verify)"'))
    assert len(_findings(gate, root)) == 1


def test_alternation_shorthand_is_skipped_and_counted(gate, tmp_path: Path) -> None:
    root = _repo(tmp_path, "`charness tool install/update/doctor` leave lock state.\n")
    report = _report(gate, root)
    assert report["findings"] == []
    assert report["skipped"]["not-a-single-subcommand-token"] == 1


def test_help_flag_and_bare_name_carry_no_subcommand_claim(gate, tmp_path: Path) -> None:
    root = _repo(tmp_path, _fence("charness --help", "charness"))
    assert _findings(gate, root) == []


def test_unreadable_cli_errors_instead_of_reporting_a_clean_run(gate, tmp_path: Path) -> None:
    """No derivable authority means no verdict. A gate whose derivation source is
    broken must not render the same 'validated N invocations' a real pass does."""
    report = _report(gate, _repo(tmp_path, _fence("charness verify"), cli=BROKEN_CLI))
    assert report["status"] == "error"
    assert "declares no subcommands" in report["findings"][0]


def test_render_states_the_surface_it_did_not_prove(gate, tmp_path: Path) -> None:
    root = _repo(tmp_path, "`charness tool install/update/doctor` and `charness update`.\n")
    rendered = gate.render_report(_report(gate, root))
    assert "Validated" in rendered
    assert "Not proven" in rendered


def test_cli_exit_code_fails_on_drift(gate, tmp_path: Path, monkeypatch, capsys) -> None:
    root = _repo(tmp_path, _fence("charness verify"))
    monkeypatch.setattr("sys.argv", ["check_documented_subcommands.py", "--repo-root", str(root)])
    assert gate.main() == 1
    assert "has no subcommand `verify`" in capsys.readouterr().err


def test_subshell_leading_invocation_is_reported(gate, tmp_path: Path) -> None:
    """The blind spot the first design bought to spare one quoted marker.

    `(cmd)` opens a subshell, so this is an ordinary invocation. Excluding `(`
    from the boundary class -- justified at the time as "shell's own distinction
    between `(` and `$(`", which is backwards -- silently skipped every one of
    them. A bounded review found it.
    """
    root = _repo(tmp_path, _fence("(charness verify --repo-root .)"))
    assert len(_findings(gate, root)) == 1


def test_underscore_and_capitalized_drift_are_reported_not_skipped(gate, tmp_path: Path) -> None:
    """The two likeliest REAL drift shapes, which a lowercase-hyphen token rule
    routed into the skipped bucket. A doc written from the code identifier says
    `session_capture` where the command is `session-capture`; argparse rejects
    both these tokens, so both are this gate's to report."""
    report = _report(gate, _repo(tmp_path, _fence("charness tool_install pkg", "charness Update")))
    assert len(report["findings"]) == 2
    assert "not-a-single-subcommand-token" not in report["skipped"]


def test_a_broken_probe_below_the_root_is_counted_not_read_as_a_leaf(gate, tmp_path: Path) -> None:
    """A parser with no subcommands and a parser whose `--help` FAILED give the
    walk the same empty answer. Left merged, a `charness tool` that cannot run
    makes every documented `charness tool <anything>` pass unchecked while the
    receipt still claims it validated them."""
    broken_child = CLI.replace(
        'tool = subparsers.add_parser("tool")',
        'tool = subparsers.add_parser("tool")\nimport sys as _s\nif _s.argv[1:2] == ["tool"]: _s.exit(3)',
    )
    report = _report(gate, _repo(tmp_path, _fence("charness tool inspect"), cli=broken_child))
    assert report["findings"] == []
    assert report["skipped"]["subcommand-help-probe-failed"] == 1


def test_probe_count_reports_only_probes_that_produced_help(gate, tmp_path: Path) -> None:
    broken_child = CLI.replace(
        'tool = subparsers.add_parser("tool")',
        'tool = subparsers.add_parser("tool")\nimport sys as _s\nif _s.argv[1:2] == ["tool"]: _s.exit(3)',
    )
    report = _report(gate, _repo(tmp_path, _fence("charness tool inspect"), cli=broken_child))
    assert report["probes"] == 1


def test_a_runtime_string_in_a_python_source_file_is_scanned(gate, tmp_path: Path) -> None:
    """The retired contract scanned `charness` and `scripts/**/*.py`; a markdown-only
    replacement would delete that coverage. This repo writes operator-facing next
    actions as backtick spans inside strings the CLI prints."""
    source = 'def hint(task):\n    return f"Run `charness verify {task} --now` to finish."\n'
    root = _repo(tmp_path, extra={"scripts/hint.py": source})
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "scripts/hint.py:2" in findings[0]


def test_an_fstring_placeholder_does_not_break_the_span(gate, tmp_path: Path) -> None:
    """The subcommand sits before the `{...}` and the closing backtick after it,
    so a reader that sees the literal parts separately never closes the span.
    Both directions, or "no finding" would just mean "never matched"."""
    valid = 'def hint(t):\n    return f"Run `charness tool install {t} --dry-run` next."\n'
    assert _findings(gate, _repo(tmp_path, extra={"scripts/hint.py": valid})) == []

    broken = 'def hint(t):\n    return f"Run `charness verify {t} --dry-run` next."\n'
    findings = _findings(gate, _repo(tmp_path, extra={"scripts/hint.py": broken}))
    assert len(findings) == 1
    assert "scripts/hint.py:2" in findings[0]


def test_a_docstring_discussing_a_retired_name_is_not_an_invocation(gate, tmp_path: Path) -> None:
    """A docstring is prose ABOUT the code. This gate's own module docstring
    explains why `charness verify` was a defect; a line scan reports it and
    teaches authors to stop quoting."""
    source = '"""Why `charness verify` was removed."""\n\n\ndef f():\n    """See `charness propose`."""\n'
    assert _findings(gate, _repo(tmp_path, extra={"scripts/note.py": source})) == []


def test_a_python_comment_is_not_an_invocation(gate, tmp_path: Path) -> None:
    assert _findings(gate, _repo(tmp_path, extra={"scripts/note.py": "# see `charness verify`\nX = 1\n"})) == []


def test_an_executed_specdown_fence_is_scanned(gate, tmp_path: Path) -> None:
    """specdown fences are RUN, so drift there breaks a proof rather than a doc --
    and `check_doc_links.DOC_GLOBS` does not reach `specs/`."""
    spec = _fence("python3 ./charness verify --repo-root .", language="run:shell")
    findings = _findings(gate, _repo(tmp_path, extra={"specs/x.spec.md": spec}))
    assert len(findings) == 1
    assert "specs/x.spec.md:2" in findings[0]


def test_a_session_transcript_language_is_not_treated_as_a_comment_fence(gate, tmp_path: Path) -> None:
    """`console` and `shell-session` are deliberately OUT of the shell set. In a
    transcript `#` is the root prompt, not a comment, so admitting them would
    have widened the scope and blinded it to every privileged invocation in the
    same line. Out of scope is honest; in-scope-and-skipped is not."""
    root = _repo(tmp_path, _fence("# charness verify", language="console"))
    assert _findings(gate, root) == []
