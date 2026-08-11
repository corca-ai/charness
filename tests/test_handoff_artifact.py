from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Read the ceiling from the module that OWNS it. These fixtures used to restate it as
# literals, and raising the budget 58 -> 78 silently turned the over-limit body into a
# passing one: the tests kept their names and stopped testing them.
_BUDGET_SPEC = importlib.util.spec_from_file_location(
    "handoff_content_budget_under_test",
    ROOT / "skills" / "public" / "handoff" / "scripts" / "handoff_content_budget.py",
)
_BUDGET = importlib.util.module_from_spec(_BUDGET_SPEC)
_BUDGET_SPEC.loader.exec_module(_BUDGET)
MAX_CONTENT_LINES = _BUDGET.DEFAULT_MAX_CONTENT_LINES

# Scaffolding bullets for `## Current State` / `## Next Session`. They exist to
# make the section non-empty for a test about some OTHER rule, so they carry a
# cheap owner: the ownership rule reads those two sections, and a bare `- state`
# would make every one of these fixtures fail for a reason it is not testing.
OWNED_STATE = "- state; recheck with `git status --short`"
OWNED_NEXT = "- next: [guide](docs/guide.md)"


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def seed_repo(tmp_path: Path, artifact_body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / ".agents" / "handoff-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: docs",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "docs" / "handoff.md").write_text(artifact_body, encoding="utf-8")
    return repo
def test_validate_handoff_artifact_rejects_extra_top_level_section(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## History",
                "",
                "- stale",
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "canonical sections" in result.stderr


def test_validate_handoff_artifact_rejects_missing_reference_link(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- docs/guide.md",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "at least one markdown link" in result.stderr


def test_validate_handoff_artifact_rejects_overlong_handoff(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                *[f"- stale detail {index} in `git status --short`" for index in range(MAX_CONTENT_LINES + 7)],
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert f"content lines (limit {MAX_CONTENT_LINES})" in result.stderr


def _handoff_with(state_lines: list[str], reference_lines: list[str]) -> str:
    return (
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                *state_lines,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                *reference_lines,
                "",
            ]
        )
        + "\n"
    )


def test_handoff_budget_ignores_blank_lines_headings_and_references(tmp_path: Path) -> None:
    # The re-base: a file well OVER the old raw cap of 70 lines passes, because
    # its length is structure and reference links rather than content the next
    # operator has to read: the body sits 4 content lines under the ceiling.
    state = []
    for index in range(MAX_CONTENT_LINES - 8):
        state.append(f"- state detail {index} in `git status --short`")
        state.append("")
    references = [f"- [guide {index}](docs/guide.md)" for index in range(12)]
    repo = seed_repo(tmp_path, _handoff_with(state, references))
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    raw_line_count = len((repo / "docs" / "handoff.md").read_text(encoding="utf-8").splitlines())
    assert raw_line_count > 70, "fixture must exceed the retired raw cap to prove the re-base"
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_handoff_budget_still_charges_for_prose_density(tmp_path: Path) -> None:
    # The other half: padding `## References` buys no room for content. 56 state
    # bullets + 4 fixed content lines put the body 2 over the ceiling.
    state = [f"- state detail {index} in `git status --short`" for index in range(MAX_CONTENT_LINES - 2)]
    repo = seed_repo(tmp_path, _handoff_with(state, ["- [guide](docs/guide.md)"]))
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert f"{MAX_CONTENT_LINES + 2} content lines (limit {MAX_CONTENT_LINES})" in result.stderr


def seed_with_current_state(tmp_path: Path, *state_lines: str) -> Path:
    return seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                *state_lines,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )


def run_on_state(tmp_path: Path, *state_lines: str) -> subprocess.CompletedProcess[str]:
    repo = seed_with_current_state(tmp_path, *state_lines)
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))


def test_validate_handoff_artifact_rejects_a_transcribed_release_version(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- Released through v2.7.0; the backlog is clear.")
    assert result.returncode == 1
    assert "v2.7.0" in result.stderr
    assert "regenerate" in result.stderr


def test_validate_handoff_artifact_rejects_a_transcribed_tool_version(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The baseline was rewritten under nose 0.19.0.")
    assert result.returncode == 1
    assert "0.19.0" in result.stderr


def test_validate_handoff_artifact_rejects_a_transcribed_commit_sha(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The rule landed in 1f7dece6 and has not moved.")
    assert result.returncode == 1
    assert "1f7dece6" in result.stderr


def test_validate_handoff_artifact_rejects_an_as_of_count(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The blocker is cleared: 66 tests across five files.")
    assert result.returncode == 1
    assert "66 tests" in result.stderr


def test_validate_handoff_artifact_allows_a_version_inside_a_link_target(tmp_path: Path) -> None:
    # A path that happens to contain a version is an address, not a claim about
    # current state, and the doc-link gate already keeps it honest.
    repo = seed_with_current_state(tmp_path, "- See the [release notes](docs/v2.5.0-notes.md).")
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (repo / "docs" / "v2.5.0-notes.md").write_text("# Notes\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_allows_a_quoted_version_for_baton_reconcile(tmp_path: Path) -> None:
    # Load-bearing carve-out, not an accident: `release`'s post-publish baton
    # reconcile asks the baton to stop claiming the previous version, and its
    # scan counts a backticked version as a claim. Closing this escape would make
    # the two public skills contradict each other.
    result = run_on_state(tmp_path, "- Published `2.8.0`; scope in the [release artifact](docs/guide.md).")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_does_not_read_a_date_as_a_count(tmp_path: Path) -> None:
    # `25 docs` from an ISO date: the lookbehind excluded `#` and word chars but
    # not `-`, and a dated reference is the commonest shape in handoff prose.
    result = run_on_state(
        tmp_path, "- The 2026-07-25 docs sweep is signed off; nothing pending — [guide](docs/guide.md)."
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_does_not_scan_inline_code(tmp_path: Path) -> None:
    # The rule tells the author to carry a command; it must not then reject the
    # command. `-n 16 tests/...` is idiomatic for this repo's pytest runner.
    result = run_on_state(tmp_path, "- Reproduce with `python3 -m pytest -n 16 tests/quality_gates`.")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_does_not_scan_fenced_blocks(tmp_path: Path) -> None:
    result = run_on_state(
        tmp_path,
        "- Reproduce with:",
        "",
        "```bash",
        "git checkout v2.7.0 && python3 -m pytest -n 16 tests/",
        "```",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_does_not_read_a_bare_url_as_a_version(tmp_path: Path) -> None:
    # A link address is not a claim, whichever of the three markdown link
    # syntaxes carries it.
    result = run_on_state(
        tmp_path,
        "- Compare: https://github.com/corca-ai/charness/compare/v0.18.0...v0.19.0",
        "- Autolink: <https://example.com/releases/v1.0.4>",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_rejects_a_two_component_version(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- Shipped in v1.2; the backlog is clear.")
    assert result.returncode == 1
    assert "v1.2" in result.stderr


def test_validate_handoff_artifact_rejects_an_uppercase_sha(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The rule landed in 6DB86CD5 and has not moved.")
    assert result.returncode == 1
    assert "6DB86CD5" in result.stderr


def test_validate_handoff_artifact_does_not_read_an_issue_id_as_a_count(tmp_path: Path) -> None:
    # Found by running the count rule across the other current-pointer artifacts:
    # `#371 issue disposition` is an identifier followed by a noun, not "371 issues".
    result = run_on_state(tmp_path, "- Closed with #371 issue disposition; nothing pending.")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_allows_issue_ids_and_commands(tmp_path: Path) -> None:
    # An issue id is a stable identifier, not a snapshot; the command is the
    # replacement the rule asks for.
    result = run_on_state(
        tmp_path,
        "- #453 stays open; re-check with `gh issue list --state open`.",
        "- Released state: `git describe --tags --abbrev=0`.",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_accepts_the_optional_continuation_capability(tmp_path: Path) -> None:
    # The handoff skill's Output Shape lists this section; a repo validator that
    # rejects it makes following the skill a gate failure.
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Continuation Capability",
                "",
                "- the reader can pick a slice without re-deriving state",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_rejects_an_empty_continuation_capability(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Continuation Capability",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Continuation Capability" in result.stderr


def test_validate_handoff_artifact_rejects_explicit_allowance_as_subagent_blocker(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                "- The canonical subagent path was blocked because this session did not explicitly allow subagents.",
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must not treat missing explicit subagent allowance" in result.stderr


def _triple_violating_body() -> str:
    """Draft violating three DISTINCT rules: title, empty section, missing link.

    One rule per gate run is what turned a 3-violation draft into 8 validator
    rounds on one artifact; these tests pin the one-pass contract so the
    regression cannot return silently.
    """
    return (
        "\n".join(
            [
                "# Demo Baton",  # no "Handoff" in the title
                "",
                "## Workflow Trigger",
                "",  # empty section
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- no markdown link here",
                "",
            ]
        )
        + "\n"
    )


def test_validate_handoff_artifact_reports_every_violation_in_one_pass(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _triple_violating_body())
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "3 handoff artifact rule violation(s):" in result.stderr
    assert "must start with a `# ... Handoff` heading" in result.stderr
    assert "`## Workflow Trigger` must not be empty" in result.stderr
    assert "`## References` must contain at least one markdown link" in result.stderr


def test_validate_handoff_artifact_names_the_owning_scaffold_on_failure(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _triple_violating_body())
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    # The hint is what makes the lesson bind at the point of use: the author is
    # told the scaffold command instead of rediscovering it one failure at a time.
    assert "scaffold_handoff_artifact.py" in result.stderr
    assert "hint:" in result.stderr


def test_validate_handoff_artifact_fail_fast_stops_at_the_first_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _triple_violating_body())
    result = run_script(
        "scripts/validate_handoff_artifact.py", "--repo-root", str(repo), "--fail-fast"
    )
    assert result.returncode == 1
    assert "rule violation(s):" not in result.stderr
    assert "must start with a `# ... Handoff` heading" in result.stderr


def test_validate_handoff_artifact_path_argument_bypasses_the_adapter(tmp_path: Path) -> None:
    """Acceptance needs a candidate draft checked WITHOUT overwriting the live handoff."""
    repo = seed_repo(tmp_path, _triple_violating_body())
    good = tmp_path / "candidate.md"
    good.write_text(
        "\n".join(
            [
                "# Candidate Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- run the thing",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script(
        "scripts/validate_handoff_artifact.py",
        "--repo-root",
        str(repo),
        "--artifact-path",
        str(good),
    )
    # The adapter-resolved artifact is invalid; the explicit path is not. Passing
    # proves the argument overrode the adapter rather than being ignored.
    assert result.returncode == 0, result.stderr
    assert "candidate.md" in result.stdout


def test_validate_handoff_artifact_path_argument_reports_a_missing_file(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _triple_violating_body())
    result = run_script(
        "scripts/validate_handoff_artifact.py",
        "--repo-root",
        str(repo),
        "--artifact-path",
        str(tmp_path / "absent.md"),
    )
    assert result.returncode == 1
    assert "No handoff artifact at" in result.stderr


def test_validate_handoff_artifact_rejects_an_unowned_state_bullet(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The umbrella class still holds and nothing is closable yet.")
    assert result.returncode == 1
    assert "carry no owner" in result.stderr


def test_validate_handoff_artifact_rejects_an_unowned_numbered_next_item(tmp_path: Path) -> None:
    # `## Next Session` is a NUMBERED queue in practice. A rule that only saw `-`
    # would have exempted the section it most needed to read.
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                "1. Redesign the selection policy — the operator has the design.",
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "carry no owner" in result.stderr
    assert "Redesign the selection policy" in result.stderr


def test_validate_handoff_artifact_accepts_each_owner_form(tmp_path: Path) -> None:
    result = run_on_state(
        tmp_path,
        "- Ruling status lives in [the rulings artifact](docs/guide.md).",
        "- Re-take the count with `git log --oneline origin/main..HEAD | wc -l`.",
        "- #604 is open and blocks the bump.",
        "- Compare https://github.com/corca-ai/charness/issues/605 before closing.",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_reads_two_bare_identifiers_as_unowned(tmp_path: Path) -> None:
    """Regression: the command test must not match the PROSE BETWEEN two spans.

    A regex of the form `` `[^`]*\\s[^`]*` `` finds its leftmost match starting
    at the CLOSING backtick of the first span, so a bullet holding two bare
    identifiers and no pointer read as carrying a command. Measured on a live
    handoff bullet, which the gate passed.
    """
    result = run_on_state(
        tmp_path,
        "- `check-changed-line-mutation-coverage` reads UNPROVEN and the "
        "`charness-publish-state-claim` block is a frozen snapshot.",
    )
    assert result.returncode == 1
    assert "carry no owner" in result.stderr


def test_validate_handoff_artifact_accepts_a_fenced_command_block_as_the_owner(tmp_path: Path) -> None:
    result = run_on_state(
        tmp_path,
        "- Reproduce with:",
        "",
        "```bash",
        "python3 -m pytest -q tests/test_handoff_artifact.py",
        "```",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_does_not_require_an_owner_in_discuss(tmp_path: Path) -> None:
    # An open question legitimately has no owner yet; that is what makes it open.
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
                "",
                "## Discuss",
                "",
                "- Should a capability be deletable without a portable replacement?",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_lets_a_sub_bullet_inherit_its_parent_owner(tmp_path: Path) -> None:
    # Charging an indented elaboration separately would push authors to repeat
    # the same link on every child.
    result = run_on_state(
        tmp_path,
        "- Ruling status lives in [the rulings artifact](docs/guide.md).",
        "  - Ruling 4's deletion half predates its ruling.",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_reports_every_unowned_entry_in_one_message(tmp_path: Path) -> None:
    result = run_on_state(
        tmp_path,
        "- first unowned claim about current state",
        "- second unowned claim about current state",
    )
    assert result.returncode == 1
    assert "2 entry(s)" in result.stderr
    assert "first unowned claim" in result.stderr
    assert "second unowned claim" in result.stderr


# --- round-1 review findings: each of these passed the first implementation ---


def test_validate_handoff_artifact_reads_an_unbalanced_backtick_as_unowned(tmp_path: Path) -> None:
    # A dropped closing backtick turned the rest of the entry into a "command"
    # and laundered the bullet — the same class as the two-span bug.
    result = run_on_state(tmp_path, "- Authors keep typing ` instead of a quote when naming flags.")
    assert result.returncode == 1
    assert "carry no owner" in result.stderr


def test_validate_handoff_artifact_accepts_a_double_backtick_command(tmp_path: Path) -> None:
    # The form an author MUST use when the command itself contains a backtick.
    # Rejecting it refuses the replacement the rule asks for.
    result = run_on_state(tmp_path, "- Re-take it with ``git log --oneline`` before inheriting.")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_requires_a_left_boundary_on_an_issue_id(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- See issue#5 and guide.md#42 for the background.")
    assert result.returncode == 1
    assert "carry no owner" in result.stderr


def test_validate_handoff_artifact_ignores_a_heading_inside_a_fence(tmp_path: Path) -> None:
    """A fenced `## Next Session` used to bind the section to the EXAMPLE.

    The real section was then never scanned and reported line numbers pointed
    into a code block — a whole-section bypass.
    """
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                OWNED_STATE,
                "",
                "```markdown",
                "## Next Session",
                "",
                "1. a fenced example",
                "```",
                "",
                "## Next Session",
                "",
                "1. An unowned claim nobody checks.",
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "An unowned claim nobody checks" in result.stderr
    assert "a fenced example" not in result.stderr


def test_validate_handoff_artifact_does_not_let_a_tilde_line_close_a_backtick_fence(tmp_path: Path) -> None:
    # A plain (```|~~~) toggle inverts on the inner `~~~` and leaks fence
    # content into the document for the rest of the section.
    result = run_on_state(
        tmp_path,
        "- Reproduce with:",
        "",
        "```",
        "~~~",
        "```",
        "",
        "- An unowned claim after the block.",
    )
    assert result.returncode == 1
    assert "An unowned claim after the block" in result.stderr


def test_validate_handoff_artifact_does_not_let_a_detached_fence_exempt_a_bullet(tmp_path: Path) -> None:
    """The live artifact's ledger block used to exempt whatever bullet sat above it.

    `docs/handoff.md` must carry the `charness-publish-state-claim` block at the
    end of `## Current State`, so the exemption was permanent, in the gate's own
    canonical artifact, and in the section the gate exists to police.
    """
    result = run_on_state(
        tmp_path,
        "- An unowned claim nobody checks.",
        "",
        "<!-- charness-publish-state-claim:demo -->",
        "```json",
        '{"kind":"demo"}',
        "```",
    )
    assert result.returncode == 1
    assert "An unowned claim nobody checks" in result.stderr


def test_validate_handoff_artifact_reports_an_indented_top_level_marker(tmp_path: Path) -> None:
    # One leading space used to make the entry vanish: not reported at all,
    # which is worse than a false pass.
    result = run_on_state(tmp_path, " - An unowned claim nobody checks.")
    assert result.returncode == 1
    assert "carry no owner" in result.stderr


def test_validate_handoff_artifact_finds_an_owner_in_a_later_paragraph(tmp_path: Path) -> None:
    # A list item may hold several paragraphs; the owner is often in the second.
    result = run_on_state(
        tmp_path,
        "- Ruling 1 is executed, both halves.",
        "",
        "  Status per ruling lives in [the rulings artifact](docs/guide.md).",
    )
    assert result.returncode == 0, result.stderr


# --- round-2 review findings: the repairs' own defects ---


def test_validate_handoff_artifact_lets_a_sub_bullet_inherit_across_the_parents_fence(tmp_path: Path) -> None:
    """The indent repair and the fence repair collided.

    Closing the entry at a fence cleared the same variable the indent rule read
    as "no parent to inherit from", so a child following its parent's own
    command block was charged for a pointer the parent already carried.
    """
    result = run_on_state(
        tmp_path,
        "- Reproduce with [the guide](docs/guide.md):",
        "",
        "  ```bash",
        "  python3 -m pytest -q",
        "  ```",
        "",
        "  - Then compare against the ledger.",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_detaches_a_fence_across_a_marker_comment(tmp_path: Path) -> None:
    """Deleting one blank line used to restore the laundering.

    With no blank, the `charness-publish-state-claim` marker read as a lazy
    continuation, so the entry stayed open and the ledger fence re-attached to
    the bullet above it. Nothing requires that blank line.
    """
    result = run_on_state(
        tmp_path,
        "- An unowned claim nobody checks.",
        "<!-- charness-publish-state-claim:demo -->",
        "```json",
        '{"kind":"demo"}',
        "```",
    )
    assert result.returncode == 1
    assert "An unowned claim nobody checks" in result.stderr


def test_validate_handoff_artifact_accepts_a_path_only_command(tmp_path: Path) -> None:
    # A blocking floor in a public skill must not refuse the replacement it
    # asks for; an argument-free path is still something to run.
    result = run_on_state(tmp_path, "- Re-take the gate with `./scripts/run-quality.sh`.")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_reads_a_padded_identifier_as_unowned(tmp_path: Path) -> None:
    # CommonMark padding put spaces inside the span, so an unstripped
    # whitespace test read a bare identifier as a command.
    result = run_on_state(tmp_path, "- The module ` inventory_boundary_bypass_lib ` records nothing.")
    assert result.returncode == 1
    assert "carry no owner" in result.stderr
