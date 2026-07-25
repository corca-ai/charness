from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

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
        "check_documented_command_flags", ROOT / "scripts" / "check_documented_command_flags.py"
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
    return list(gate.build_report(root)["findings"])


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
    report = gate.build_report(root)
    assert report["status"] == "pass"
    assert report["skipped"] == {
        "placeholder-path": 1,
        "unresolved-path-owned-by-check-doc-links": 1,
    }
    assert "Not proven (2 flag-bearing invocation(s) skipped)" in gate.render_report(report)


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
    report = gate.build_report(root)
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
    assert gate.main() == 1
    captured = capsys.readouterr()
    assert "Documented command flag drift detected:" in captured.err
    assert "`--gone`" in captured.err
    assert captured.out == ""


def test_main_json_payload_goes_to_stdout_when_clean(gate, tmp_path, monkeypatch, capsys) -> None:
    root = _repo(
        tmp_path,
        scripts={"scripts/preflight.py": PLAIN_SCRIPT},
        doc="Run `python3 scripts/preflight.py --path X`.\n",
    )
    monkeypatch.setattr(
        "sys.argv", ["check_documented_command_flags.py", "--repo-root", str(root), "--json"]
    )
    assert gate.main() == 0
    payload = json.loads(capsys.readouterr().out)
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
    report = gate.build_report(root)
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
    report = gate.build_report(root)
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
    report = gate.build_report(root)
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
        str(ROOT / "scripts" / "check_documented_command_flags.py"), "--repo-root", str(root)
    )
    assert failing.returncode == 1
    assert "`--gone`" in failing.stderr

    (root / "docs" / "guide.md").write_text("Run `python3 scripts/log.py --path X`.\n", encoding="utf-8")
    clean = run_script(
        str(ROOT / "scripts" / "check_documented_command_flags.py"), "--repo-root", str(root)
    )
    assert clean.returncode == 0
    assert "Validated 1 documented command invocation(s)" in clean.stdout
