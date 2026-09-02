from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

from .argparse_help_probe_support import run_help_commands_in_process
from .support import ROOT, run_script

SHARED_PARSER_HELPER = """
def add_shared_arguments(parser):
    parser.add_argument("--summary", action="store_true")
"""

PLAIN_SCRIPT = """
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    parser.add_argument("--run-checks", action="store_true")
    parser.parse_args()

main()
"""

SHARED_HELPER_SCRIPT = """
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_args import add_shared_arguments

parser = argparse.ArgumentParser()
parser.add_argument("--repo-root")
add_shared_arguments(parser)
parser.parse_args()
"""

SUBCOMMAND_SCRIPT = """
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--repo-root")
subparsers = parser.add_subparsers(dest="command")
resolve = subparsers.add_parser("resolve-destination")
resolve.add_argument("--current")
parser.parse_args()
"""


PROSE_CONTAMINATED_SCRIPT = """
import argparse

parser = argparse.ArgumentParser(description="Compare against HEAD; see --cached elsewhere.")
parser.add_argument("--staged", action="store_true", help="Diff the staged index (--cached) instead.")
parser.parse_args()
"""

BRACKET_FLAG_SCRIPT = """
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--class-key")
parser.add_argument("--converted", action="store_true")
parser.add_argument("--engine")
parser.parse_args()
"""


@pytest.fixture(scope="module")
def gate():
    spec = importlib.util.spec_from_file_location(
        "check_documented_command_flags", ROOT / "scripts" / "gates" / "check_documented_command_flags.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _repo(tmp_path: Path, *, scripts: dict[str, str], doc: str, doc_path: str = "docs/guide.md") -> Path:
    root = tmp_path / "repo"
    for name, body in scripts.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    written_doc = root / doc_path
    written_doc.parent.mkdir(parents=True, exist_ok=True)
    written_doc.write_text(doc, encoding="utf-8")
    return root


def _findings(gate, root: Path) -> list[str]:
    return list(_report(gate, root)["findings"])


def _report(gate, root: Path) -> dict:
    return gate.build_report(root, help_runner=run_help_commands_in_process)


def test_flag_deleted_from_its_owning_script_is_reported(gate, tmp_path: Path) -> None:
    # The motivating violation, reproduced against the real repo before this gate
    # existed: deleting `--run-checks` from check_skill_surface_preflight.py left
    # check_command_docs, check_doc_authoring_preflight, check_doc_links and both
    # preflight test files green while the documented command exited 2.
    root = _repo(
        tmp_path,
        scripts={"scripts/preflight.py": PLAIN_SCRIPT.replace('    parser.add_argument("--run-checks", action="store_true")\n', "")},
        doc="Run `python3 scripts/preflight.py --path X --run-checks` before authoring.\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "docs/guide.md:1" in findings[0]
    assert "`--run-checks`" in findings[0]
    assert "`--path`" not in findings[0]


def test_flag_added_by_a_shared_parser_helper_is_accepted(gate, tmp_path: Path) -> None:
    # Why this gate runs `--help` instead of scanning the named file's source:
    # this repo builds --repo-root/--summary/--detail through shared helpers, so a
    # source scan reported 34 false missing flags on a clean tree.
    root = _repo(
        tmp_path,
        scripts={
            "scripts/shared_args.py": SHARED_PARSER_HELPER,
            "scripts/inventory.py": SHARED_HELPER_SCRIPT,
        },
        doc="Run `python3 scripts/inventory.py --repo-root . --summary`.\n",
    )
    assert _findings(gate, root) == []


def test_flag_inside_a_quoted_argument_value_is_not_attributed_to_the_script(gate, tmp_path: Path) -> None:
    # `--verification "git diff --stat origin/main..HEAD"` documents --verification.
    # Reading --stat as this script's flag is a false positive, and the quoted
    # value also carries a literal `;` that must not be read as a shell operator.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT.replace('parser.parse_args()', 'parser.add_argument("--verification")\n    parser.parse_args()')},
        doc=(
            "```bash\n"
            'python3 scripts/log.py --path X --run-checks --verification "git diff --stat HEAD; ok"\n'
            "```\n"
        ),
    )
    assert _findings(gate, root) == []


def test_pipeline_stage_flags_are_not_attributed_to_the_script(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="```bash\npython3 scripts/log.py --path X | jq --raw-output .id\n```\n",
    )
    assert _findings(gate, root) == []


def test_subcommand_flag_resolves_when_the_subcommand_follows_a_top_level_flag(gate, tmp_path: Path) -> None:
    # `--repo-root . resolve-destination --current X` is a live shape: a
    # leading-words-only read attributes --current to the top-level parser that
    # never declares it. The single-choice `{resolve-destination}` usage rendering
    # is also the shape a two-or-more choices regex misses.
    root = _repo(
        tmp_path,
        scripts={"scripts/adapter.py": SUBCOMMAND_SCRIPT},
        doc=(
            "```bash\n"
            "python3 scripts/adapter.py --repo-root . \\\n"
            "  resolve-destination --current org/repo\n"
            "```\n"
        ),
    )
    assert _findings(gate, root) == []


def test_subparser_flag_documented_before_its_subcommand_is_reported(gate, tmp_path: Path) -> None:
    """F7, direction 1. Measured on this parser shape: argparse exits 2 with
    `argument command: invalid choice: 'org/repo'` because the top-level parser
    reaches the subcommand positional before the subparser ever sees `--current`.
    A set unioned across the resolved path calls this correct."""
    root = _repo(
        tmp_path,
        scripts={"scripts/adapter.py": SUBCOMMAND_SCRIPT},
        doc=(
            "```bash\n"
            "python3 scripts/adapter.py --current org/repo resolve-destination\n"
            "```\n"
        ),
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--current`" in findings[0]


def test_top_level_flag_documented_after_the_subcommand_is_reported(gate, tmp_path: Path) -> None:
    """F7, direction 2, and the correction of a comment this gate used to carry.

    It read "a top-level flag documented after the subcommand is still accepted by
    the top-level parser". Measured: `demo resolve --current y --top x` exits 2 with
    `unrecognized arguments: --top x`. argparse hands everything after the
    subcommand token to the subparser."""
    root = _repo(
        tmp_path,
        scripts={"scripts/adapter.py": SUBCOMMAND_SCRIPT},
        doc=(
            "```bash\n"
            "python3 scripts/adapter.py resolve-destination --current x --repo-root .\n"
            "```\n"
        ),
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--repo-root`" in findings[0]


VALUE_COLLIDES_WITH_SUBCOMMAND_SCRIPT = """
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--repo-root")
parser.add_argument("--accept-family")
parser.add_argument("--restamp-tool-version", action="store_true")
subparsers = parser.add_subparsers(dest="command")
record = subparsers.add_parser("record")
record.add_argument("--label")
parser.parse_args()
"""


def test_flag_value_equal_to_a_subcommand_name_does_not_reroute_the_probe(gate, tmp_path: Path) -> None:
    """F8. `--accept-family record` is a top-level flag with a value that happens to
    spell a subcommand. Reading the first bare word in the choices set regardless of
    position routes the whole probe into the `record` subparser, which declares none
    of the top-level flags -- a blocking false red on a correct doc."""
    root = _repo(
        tmp_path,
        scripts={"scripts/ratchet.py": VALUE_COLLIDES_WITH_SUBCOMMAND_SCRIPT},
        doc=(
            "```bash\n"
            "python3 scripts/ratchet.py --repo-root . --accept-family record --restamp-tool-version\n"
            "```\n"
        ),
    )
    assert _findings(gate, root) == []


def test_a_real_subcommand_still_resolves_when_a_value_precedes_it(gate, tmp_path: Path) -> None:
    """The other side of F8: value consumption must not swallow a genuine subcommand."""
    root = _repo(
        tmp_path,
        scripts={"scripts/ratchet.py": VALUE_COLLIDES_WITH_SUBCOMMAND_SCRIPT},
        doc=(
            "```bash\n"
            "python3 scripts/ratchet.py --repo-root . record --label x\n"
            "```\n"
        ),
    )
    assert _findings(gate, root) == []


def test_store_true_option_does_not_consume_the_following_subcommand(gate, tmp_path: Path) -> None:
    """A flag with no metavar takes no value, so the next word is still a subcommand."""
    root = _repo(
        tmp_path,
        scripts={"scripts/ratchet.py": VALUE_COLLIDES_WITH_SUBCOMMAND_SCRIPT},
        doc=(
            "```bash\n"
            "python3 scripts/ratchet.py --restamp-tool-version record --label x\n"
            "```\n"
        ),
    )
    assert _findings(gate, root) == []


def test_backslash_continuation_reports_the_line_the_invocation_starts_on(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/adapter.py": SUBCOMMAND_SCRIPT},
        doc=(
            "intro\n"
            "```bash\n"
            "python3 scripts/adapter.py resolve-destination \\\n"
            "  --gone org/repo\n"
            "```\n"
        ),
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "docs/guide.md:3" in findings[0]
    assert "`--gone`" in findings[0]


def test_command_quoted_inside_a_yaml_value_is_still_checked(gate, tmp_path: Path) -> None:
    # The live defect this gate found on its first run: an adapter-contract example
    # rendered as `command: "python3 scripts/x.py --json"`. The closing quote lands
    # in the argument tail, and dropping unparseable tails would skip exactly the
    # surface the gate exists to check.
    root = _repo(
        tmp_path,
        scripts={"scripts/render.py": PLAIN_SCRIPT},
        doc='```yaml\ncommand: "python3 scripts/render.py --json"\n```\n',
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--json`" in findings[0]


def test_placeholder_path_is_the_documented_escape(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="Consuming repos run `python3 <repo-root>/scripts/log.py --their-flag`.\n",
    )
    assert _findings(gate, root) == []


def test_skipped_invocations_are_counted_so_a_pass_cannot_over_claim(gate, tmp_path: Path) -> None:
    # A bare "validated N invocations" reads as full coverage of the documented
    # command surface. Every skip is an invocation whose flags were NOT proven, so
    # the count and its reason ride on the pass output too.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc=(
            "Consuming repos run `python3 <repo-root>/scripts/log.py --their-flag`.\n"
            "Run `python3 scripts/deleted.py --path X`.\n"
        ),
    )
    report = _report(gate, root)
    assert report["status"] == "pass"
    assert report["skipped"] == {
        "placeholder-path": 1,
        "unresolved-path-owned-by-check-doc-links": 1,
    }
    # `render_report` went away with `--json` on 2026-08-14; the not-proven tail it
    # appended to the PASS output is a payload key now, and it must still ride on a pass.
    assert "2 flag-bearing invocation(s) skipped" in gate.report_payload(report)["not_proven"]


def test_skill_dir_parent_traversal_resolves_into_a_sibling_package(gate, tmp_path: Path) -> None:
    # `$SKILL_DIR/../<other>/scripts/x.py` is this repo's cross-skill form. Left
    # unnormalized it resolves to nothing, and a whole class of the most-run
    # bootstrap commands goes silently unchecked.
    root = _repo(
        tmp_path,
        scripts={"skills/public/retro/scripts/probe.py": PLAIN_SCRIPT},
        doc='Run `python3 "$SKILL_DIR/../retro/scripts/probe.py" --path . --gone`.\n',
        doc_path="skills/public/achieve/references/goal-artifact.md",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--gone`" in findings[0]
    assert "skills/public/retro/scripts/probe.py" in findings[0]


def test_shared_reference_skill_dir_anchors_at_the_consuming_package_depth(gate, tmp_path: Path) -> None:
    # In `skills/shared/**`, `$SKILL_DIR` is the *consuming* skill's directory,
    # which always sits at `skills/<kind>/<name>` -- only that depth matters.
    root = _repo(
        tmp_path,
        scripts={"skills/shared/scripts/fingerprint.py": PLAIN_SCRIPT},
        doc='Run `python3 "$SKILL_DIR/../../shared/scripts/fingerprint.py" --path . --gone`.\n',
        doc_path="skills/shared/references/review.md",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "skills/shared/scripts/fingerprint.py" in findings[0]


def test_unresolvable_script_is_left_to_the_link_gate(gate, tmp_path: Path) -> None:
    # check_doc_links.py already reports a documented command naming a script that
    # does not exist; duplicating it would fail one doc typo in two gates with
    # different wording and two different fixes.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/deleted.py --path X`.\n",
    )
    assert _findings(gate, root) == []


def test_skill_dir_invocations_resolve_against_their_own_package(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"skills/public/quality/scripts/inventory.py": PLAIN_SCRIPT},
        doc="- source lines:\n  `$SKILL_DIR/scripts/inventory.py --path . --gone`\n",
        doc_path="skills/public/quality/references/dispatch.md",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--gone`" in findings[0]
    assert "skills/public/quality/scripts/inventory.py" in findings[0]


def test_flag_named_only_in_help_prose_is_not_treated_as_accepted(gate, tmp_path: Path) -> None:
    # The gate's central mechanism failing in its own dangerous direction. argparse
    # prints `description`, `epilog` and every `help=` string verbatim, so scanning
    # the whole render put --cached, --run-checks, --body-file, --min-confidence and
    # --mutation-coverage-command into the accepted sets of parsers that reject them.
    root = _repo(
        tmp_path,
        scripts={"scripts/cut.py": PROSE_CONTAMINATED_SCRIPT},
        doc="Run `python3 scripts/cut.py --staged --cached`.\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--cached`" in findings[0]
    assert "--staged" not in findings[0]


def test_help_itself_stays_accepted_after_the_prose_tightening(gate, tmp_path: Path) -> None:
    # usage renders it as `[-h]`, so a usage-only read would make --help a false red.
    root = _repo(
        tmp_path,
        scripts={"scripts/cut.py": PROSE_CONTAMINATED_SCRIPT},
        doc="Run `python3 scripts/cut.py --help`.\n",
    )
    assert _findings(gate, root) == []


def test_bracketed_and_inline_value_flag_forms_are_checked(gate, tmp_path: Path) -> None:
    # `[--converted --durable-kind <kind>]` and `--engine=tokei` are both live doc
    # forms. Unnormalized they fail fullmatch and get dropped -- and worse, the
    # invocation still counted as validated, so the run over-claimed coverage.
    root = _repo(
        tmp_path,
        scripts={"scripts/rca.py": BRACKET_FLAG_SCRIPT},
        doc="```bash\npython3 scripts/rca.py --class-key k [--converted --gone <x>] --engine=tokei\n```\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--gone`" in findings[0]
    assert "--converted" not in findings[0]
    assert "--engine" not in findings[0]


def test_two_invocations_in_one_carrier_do_not_cross_attribute_flags(gate, tmp_path: Path) -> None:
    # `,` is not a shell operator, so reading to the end of the carrier handed the
    # second command's flags to the first -- a blocking false red on a correct doc.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT, "scripts/rca.py": BRACKET_FLAG_SCRIPT},
        doc="verify: `python3 scripts/log.py --path X, python3 scripts/rca.py --engine tokei`\n",
    )
    assert _findings(gate, root) == []


def test_trailing_shell_comment_is_not_read_as_arguments(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="```bash\npython3 scripts/log.py --path X   # prefer --run-checks over --gone\n```\n",
    )
    assert _findings(gate, root) == []


def test_dangling_backslash_in_prose_does_not_crash_the_gate(gate, tmp_path: Path) -> None:
    # shlex raises on a dangling backslash as well as an unclosed quote, and only
    # the latter had a repair. A doc typo must not turn a blocking gate into a
    # stack trace.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/log.py --path \\`.\n",
    )
    assert _findings(gate, root) == []


def test_continuation_does_not_join_across_a_fence_boundary(gate, tmp_path: Path) -> None:
    # iter_doc_lines consumes fence delimiters silently, so a dangling `\` at the
    # end of one block would otherwise swallow the next block's first line and
    # attribute its flags to the wrong script.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT, "scripts/rca.py": BRACKET_FLAG_SCRIPT},
        doc=(
            "```bash\npython3 scripts/log.py --path X \\\n```\n"
            "text\n"
            "```bash\npython3 scripts/rca.py --engine tokei\n```\n"
        ),
    )
    assert _findings(gate, root) == []


def test_bare_basename_invocation_is_checked(gate, tmp_path: Path) -> None:
    # `issue_tool.py verify-closeout --expect-state CLOSED` -- prefix-free, dense in
    # the issue skill's docs, and previously unowned by this gate AND check_doc_links.
    root = _repo(
        tmp_path,
        scripts={"skills/public/issue/scripts/issue_tool.py": PLAIN_SCRIPT},
        doc="Run `issue_tool.py --path X --gone` to verify.\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--gone`" in findings[0]


def test_ambiguous_basename_is_counted_not_guessed(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={
            "skills/public/issue/scripts/resolve_adapter.py": PLAIN_SCRIPT,
            "skills/public/quality/scripts/resolve_adapter.py": PLAIN_SCRIPT,
        },
        doc="Run `resolve_adapter.py --path X --gone`.\n",
    )
    report = _report(gate, root)
    assert report["findings"] == []
    assert report["skipped"] == {"ambiguous-or-unknown-script-basename": 1}


def test_mirrored_plugin_copies_do_not_make_every_basename_ambiguous(gate, tmp_path: Path) -> None:
    # The generated `plugins/charness/scripts/` mirror duplicates every canonical
    # script, which defeated a repo-wide uniqueness index outright: all 40 live bare
    # invocations resolved to nothing.
    root = _repo(
        tmp_path,
        scripts={
            "scripts/log.py": PLAIN_SCRIPT,
            "plugins/charness/scripts/log.py": PLAIN_SCRIPT,
        },
        doc="Run `log.py --path X --gone`.\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "scripts/log.py" in findings[0]
    assert "plugins/" not in findings[0]


CHOICES_NOT_SUBCOMMANDS_SCRIPT = """
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["alpha", "beta"])
parser.add_argument("--path")
parser.parse_args()
"""

BROKEN_HELP_SCRIPT = """
import sys
print("boom", file=sys.stderr)
raise SystemExit(3)
"""


def test_main_reports_findings_on_stderr_and_exits_one(gate, tmp_path, monkeypatch, capsys) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/preflight.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/preflight.py --gone`.\n",
    )
    monkeypatch.setattr("sys.argv", ["check_documented_command_flags.py", "--repo-root", str(root)])
    assert gate.main(help_runner=run_help_commands_in_process) == 1
    captured = capsys.readouterr()
    # The `Documented command flag drift detected:` headline was deleted with `--json`;
    # what has to survive is the STREAM choice — a failing verdict goes to stderr so a
    # green run's stdout stays quotable — plus the finding and its remedy.
    report = yaml.safe_load(captured.err)
    assert report["status"] != "pass"
    assert any("`--gone`" in finding for finding in report["findings"])
    assert "Fix the doc or restore the flag" in report["fix_hint"]
    assert captured.out == ""


def test_main_payload_goes_to_stdout_when_clean(gate, tmp_path, monkeypatch, capsys) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/preflight.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/preflight.py --path X`.\n",
    )
    monkeypatch.setattr(
        "sys.argv", ["check_documented_command_flags.py", "--repo-root", str(root)]
    )
    assert gate.main(help_runner=run_help_commands_in_process) == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["status"] == "pass"
    assert payload["invocations"] == 1


def test_command_whose_help_itself_fails_is_reported_as_not_runnable(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/broken.py": BROKEN_HELP_SCRIPT},
        doc="Run `python3 scripts/broken.py --path X`.\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "exits 3" in findings[0]
    assert "not runnable" in findings[0]


def test_a_choices_brace_group_is_not_mistaken_for_a_subcommand(gate, tmp_path: Path) -> None:
    # `--mode {alpha,beta}` renders the same `{...}` shape a subparser does. The
    # documented value `alpha` therefore looks like a subcommand; probing
    # `script alpha --help` fails, and the path must trim back rather than report
    # a false "not runnable".
    root = _repo(
        tmp_path,
        scripts={"scripts/mode.py": CHOICES_NOT_SUBCOMMANDS_SCRIPT},
        doc="Run `python3 scripts/mode.py --mode alpha --path X`.\n",
    )
    assert _findings(gate, root) == []


def test_flagless_invocations_are_left_to_the_link_gate(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="First `python3 scripts/log.py`, then `python3 scripts/log.py --gone`.\n",
    )
    report = _report(gate, root)
    assert report["invocations"] == 1
    assert len(report["findings"]) == 1


def test_non_repo_owned_and_package_less_skill_dir_paths_are_counted(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc=(
            "Run `python3 build/vendor.py --their-flag`.\n"
            'Run `python3 "$SKILL_DIR/scripts/thing.py" --their-flag`.\n'
        ),
    )
    report = _report(gate, root)
    assert report["findings"] == []
    assert report["skipped"] == {
        "not-a-repo-owned-path": 1,
        "skill-dir-outside-a-skill-package": 1,
    }


def test_package_relative_path_resolves_inside_its_own_skill_package(gate, tmp_path: Path) -> None:
    # A portable skill package documents `python3 scripts/x.py` meaning its OWN
    # scripts/, not the repo's.
    root = _repo(
        tmp_path,
        scripts={"skills/public/quality/scripts/probe.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/probe.py --path . --gone`.\n",
        doc_path="skills/public/quality/references/dispatch.md",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "skills/public/quality/scripts/probe.py" in findings[0]


def test_skill_dir_path_escaping_the_repo_root_is_counted_not_resolved(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"skills/public/quality/scripts/probe.py": PLAIN_SCRIPT},
        doc='Run `python3 "$SKILL_DIR/../../../../outside/probe.py" --gone`.\n',
        doc_path="skills/public/quality/references/dispatch.md",
    )
    report = _report(gate, root)
    assert report["findings"] == []
    assert report["skipped"] == {"unresolved-path-owned-by-check-doc-links": 1}


def test_resolution_falls_back_to_the_filesystem_without_a_path_listing(gate, tmp_path: Path) -> None:
    # build_report always threads the git-honouring listing; the filesystem branch
    # is the library-caller path and must still resolve.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/log.py --gone`.\n",
    )
    found, skipped = gate.iter_documented_invocations(root, root / "docs" / "guide.md")
    assert skipped == []
    assert [(script, flags) for _, script, _, flags in found] == [("scripts/log.py", ("--gone",))]


def test_a_dangling_continuation_at_end_of_document_is_still_scanned(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="```bash\npython3 scripts/log.py --gone \\\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--gone`" in findings[0]


def test_a_dangling_continuation_is_flushed_when_prose_follows(gate, tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="```bash\npython3 scripts/log.py --gone \\\n```\nprose after the block\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--gone`" in findings[0]


def test_shared_reference_anchor_is_none_for_a_doc_outside_the_repo(gate, tmp_path: Path) -> None:
    assert gate.shared_reference_anchor(tmp_path / "repo", tmp_path / "elsewhere" / "x.md") is None


BRACES_AND_SUBPARSERS_SCRIPT = """
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["alpha", "beta"])
subparsers = parser.add_subparsers(dest="command")
subparsers.add_parser("run")
parser.parse_args()
"""


def test_a_choices_value_is_trimmed_back_when_it_is_not_a_real_subcommand(gate, tmp_path: Path) -> None:
    # argparse renders `--mode {alpha,beta}` with the same brace shape a subparser
    # uses, so `alpha` reads as a subcommand path. Here the script really does have
    # subparsers, so `script alpha --help` dies on invalid choice before --help can
    # short-circuit -- the exact case the trim exists to keep from becoming a false
    # "not runnable" verdict on a correct doc.
    root = _repo(
        tmp_path,
        scripts={"scripts/mode.py": BRACES_AND_SUBPARSERS_SCRIPT},
        doc="Run `python3 scripts/mode.py --mode alpha`.\n",
    )
    assert _findings(gate, root) == []


def test_module_entrypoint_exits_with_the_gate_verdict(gate, tmp_path: Path) -> None:
    # Covers the `if __name__ == "__main__"` guard: the exit code an operator and
    # the quality runner actually see.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/log.py --gone`.\n",
    )
    failing = run_script(
        str(ROOT / "scripts" / "gates" / "check_documented_command_flags.py"), "--repo-root", str(root)
    )
    assert failing.returncode == 1
    assert "`--gone`" in failing.stderr

    (root / "docs" / "guide.md").write_text("Run `python3 scripts/log.py --path X`.\n", encoding="utf-8")
    clean = run_script(
        str(ROOT / "scripts" / "gates" / "check_documented_command_flags.py"), "--repo-root", str(root)
    )
    assert clean.returncode == 0
    # The `Validated N documented command invocation(s)` sentence was deleted with
    # `--json`; the same two numbers are payload keys on the clean run's stdout.
    clean_payload = yaml.safe_load(clean.stdout)
    assert clean_payload["status"] == "pass"
    assert clean_payload["invocations"] == 1


CHOICES_POSITIONAL_PLUS_SUBPARSERS_SCRIPT = """
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["alpha", "beta"])
subparsers = parser.add_subparsers(dest="command")
run = subparsers.add_parser("run")
run.add_argument("--label")
parser.parse_args()
"""


def test_a_choices_positional_value_is_judged_as_a_flag_scope_not_as_an_unrunnable_command(gate, tmp_path: Path) -> None:
    """`subcommand_choices` deliberately still admits a plain `choices=` POSITIONAL,
    because argparse rejects an unlisted value with the same `invalid choice`
    error. So `alpha` is a free word in the depth-0 choice set and the walk
    descends into it.

    Verified against real argparse: `x.py alpha --label demo` exits 2
    (`argument command: invalid choice: 'demo'`), so a finding is CORRECT here.
    What must not happen is the OTHER finding -- "the documented command is not
    runnable" -- which is what the trim-back loop in `_resolve_paths` exists to
    prevent when a resolved path turns out not to be a real parser.
    """
    root = _repo(
        tmp_path,
        scripts={"scripts/x.py": CHOICES_POSITIONAL_PLUS_SUBPARSERS_SCRIPT},
        doc="```bash\npython3 scripts/x.py alpha --label demo\n```\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "does not accept documented flag(s) `--label`" in findings[0]
    assert "not runnable" not in findings[0]


def _write(root: Path, relative: str, body: str) -> Path:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


# --- carrier scope: the `--json` residue class ------------------------------
#
# Seven live callers passed a `--json` the migrated skill scripts had stopped
# accepting; six of them were invisible to this gate because they were not
# markdown, and the seventh was markdown this gate silently did not read. Each
# test below pins one of those carrier shapes.


def test_a_backtick_span_wrapping_across_a_prose_line_break_is_scanned(gate, tmp_path: Path) -> None:
    """The `docs/deferred-decisions.md` shape, and the worst kind of miss: not
    checked AND not counted as skipped, so the run reported full coverage of a
    doc it had not read. `BACKTICK_CONTENT_RE` excludes newlines and the fenced
    join only fires on a trailing backslash, so NEITHER line formed a carrier."""
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="Regenerate that fact with `python3 scripts/log.py --path .\n--gone` (2026-08-10).\n",
    )
    report = _report(gate, root)
    assert report["invocations"] == 1
    assert len(report["findings"]) == 1
    assert "docs/guide.md:1" in report["findings"][0]
    assert "`--gone`" in report["findings"][0]


def test_an_unclosed_backtick_span_ends_at_the_paragraph_break(gate, tmp_path: Path) -> None:
    # Markdown inline code cannot cross a blank line. Without that stop an odd
    # backtick count swallows the rest of the document into one carrier.
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT},
        doc="An unclosed `python3 scripts/log.py --gone\n\nprose --run-checks after the break\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "`--gone`" in findings[0]
    assert "`--run-checks`" not in findings[0]


def test_a_command_stored_in_an_agents_config_is_checked(gate, tmp_path: Path) -> None:
    """`.agents/surfaces.json` verify commands and `.agents/release-adapter.yaml`
    probe lists are executed verbatim by an adapter runner, so drift there breaks
    a run rather than a sentence. Two of the seven residues lived here."""
    root = _repo(tmp_path, scripts={"scripts/log.py": PLAIN_SCRIPT}, doc="no commands here\n")
    _write(root, ".agents/surfaces.json", '{\n  "verify_commands": [\n    "python3 scripts/log.py --repo-root . --gone >/dev/null"\n  ]\n}\n')
    _write(root, ".agents/release-adapter.yaml", "fresh_checkout_probes:\n- python3 scripts/log.py --path .\n")
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert ".agents/surfaces.json:3" in findings[0]
    assert "`--gone`" in findings[0]


def test_a_config_line_that_quotes_its_command_in_prose_is_read_as_a_span(gate, tmp_path: Path) -> None:
    """Instruction items are sentences, so the whole line ends the last
    flag with a fused closing backtick (``--gone` `` is not a flag token) and the
    invocation is silently judged flagless. This shape must remain covered."""
    root = _repo(tmp_path, scripts={"scripts/log.py": PLAIN_SCRIPT}, doc="no commands here\n")
    _write(
        root,
        ".agents/release-adapter.yaml",
        "update_instructions:\n- Run `python3 scripts/log.py --path . --gone` once and confirm findings.\n",
    )
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert ".agents/release-adapter.yaml:2" in findings[0]
    assert "`--gone`" in findings[0]


ARGV_CALLER = '''
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def run(repo_root):
    return subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts/log.py"),
            "--path",
            str(repo_root),
            "--gone",
        ],
        check=False,
    )
'''


def test_an_argv_sequence_built_in_python_is_checked(gate, tmp_path: Path) -> None:
    """The `draft_dup_ratchet_triage.py` shape. Its DEFAULT mode exited 2 on a
    clean tree with every gate green, because the flag claim lived in a list
    literal rather than a doc. `sys.executable` is why the interpreter prefix has
    to be synthesized: it renders as a placeholder, so nothing anchors the regex."""
    root = _repo(tmp_path, scripts={"scripts/log.py": PLAIN_SCRIPT}, doc="no commands here\n")
    _write(root, "scripts/caller.py", ARGV_CALLER)
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "scripts/caller.py" in findings[0]
    assert "`--gone`" in findings[0]


def test_a_cli_invocation_built_in_a_test_argv_is_checked(gate, tmp_path: Path) -> None:
    # The seventh residue: a `charness tool doctor --json` in a `release_only`
    # test, i.e. a flag claim with no `.py` anywhere in it.
    root = _repo(tmp_path, scripts={"charness": SUBCOMMAND_SCRIPT}, doc="no commands here\n")
    _write(root, "tests/test_cli.py", 'def test_x(run_script):\n    run_script("charness", "resolve-destination", "--gone")\n')
    findings = _findings(gate, root)
    assert len(findings) == 1
    assert "tests/test_cli.py:2" in findings[0]
    assert "`--gone`" in findings[0]


def test_a_list_of_shell_script_lines_is_not_read_as_one_argv(gate, tmp_path: Path) -> None:
    """A list of strings is argv only when its elements are TOKENS. A fixture that
    builds a shell script line by line is the other thing it is here, and joining
    those lines spliced each command's flags into its neighbour: nine findings no
    runnable command carried. An argv element with whitespace is always a value."""
    root = _repo(tmp_path, scripts={"scripts/log.py": PLAIN_SCRIPT}, doc="no commands here\n")
    _write(
        root,
        "tests/test_hook.py",
        'def test_x(tmp_path):\n'
        '    (tmp_path / "pre-push").write_text("\\n".join([\n'
        '        "#!/usr/bin/env bash",\n'
        '        "python3 scripts/log.py --path .",\n'
        '        "python3 -m pytest --gone -q tests",\n'
        '    ]))\n',
    )
    assert _findings(gate, root) == []


def test_an_argument_value_that_names_a_command_does_not_start_a_second_one(gate, tmp_path: Path) -> None:
    """`run_script("scripts/log.py", "--paths", "charness", "--run-checks")`. The
    value of `--paths` is not a program name: reading it as one cut the real
    command's tail at that token and reported every flag after it as drift."""
    root = _repo(tmp_path, scripts={"scripts/log.py": PLAIN_SCRIPT, "charness": SUBCOMMAND_SCRIPT}, doc="no commands here\n")
    _write(
        root,
        "tests/test_paths.py",
        'def test_x(run_script):\n'
        '    run_script("scripts/log.py", "--path", "charness", "--run-checks")\n',
    )
    assert _findings(gate, root) == []


def test_the_cli_name_used_as_an_option_value_is_counted_not_reported(gate, tmp_path: Path) -> None:
    """`--product-id charness` in a documented command. `charness` is this repo's
    product name as well as its CLI, so the value read as a second invocation cut
    six real flags off the first and reported all six as drift. Counted rather
    than dropped, because after a shell operator it really would be a command."""
    root = _repo(
        tmp_path,
        scripts={"scripts/log.py": PLAIN_SCRIPT, "charness": SUBCOMMAND_SCRIPT},
        doc="Run `python3 scripts/log.py --run-checks --path charness resolve-destination --gone`.\n",
    )
    report = _report(gate, root)
    assert report["findings"] == []
    assert report["skipped"] == {"cli-name-as-an-argument-value": 1}


def test_a_rejection_probe_flag_is_skipped_while_its_neighbour_is_still_checked(gate, tmp_path: Path) -> None:
    """`.agents/cli-side-effect-probes.json` asserts argparse REJECTS
    `--not-a-tool`. Read as a flag claim that inverts the assertion. Keyed on the
    flag rather than the config key because the same file writes a real
    `--dry-run` beside it, and a key-shaped rule would have to discard both."""
    root = _repo(tmp_path, scripts={"scripts/log.py": PLAIN_SCRIPT}, doc="no commands here\n")
    _write(
        root,
        ".agents/cli-side-effect-probes.json",
        '{\n'
        '  "option_like_positional_probes": ["python3 scripts/log.py --not-a-path"],\n'
        '  "dry_run_probe": "python3 scripts/log.py --path . --gone --not-a-path"\n'
        '}\n',
    )
    report = _report(gate, root)
    assert len(report["findings"]) == 1
    assert "`--gone`" in report["findings"][0]
    assert "`--not-a-path`" not in report["findings"][0]
    assert report["skipped"] == {"negative-probe-invocation": 1}
