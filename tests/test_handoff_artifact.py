from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module
from tests.handoff_artifact_fixtures import (
    OWNED_NEXT,
    OWNED_STATE,
    run_on_state,
    run_script,
    seed_repo,
    seed_with_current_state,
)

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
                "- [guide](docs/guide.md) — the demo guide.",
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
                "- [guide](docs/guide.md) — the demo guide.",
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
    references = [f"- [guide {index}](docs/guide.md) — the demo guide." for index in range(12)]
    repo = seed_repo(tmp_path, _handoff_with(state, references))
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    raw_line_count = len((repo / "docs" / "handoff.md").read_text(encoding="utf-8").splitlines())
    assert raw_line_count > 70, "fixture must exceed the retired raw cap to prove the re-base"
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def _run_with_references(tmp_path: Path, *reference_lines: str) -> object:
    repo = seed_repo(tmp_path, _handoff_with([OWNED_STATE], list(reference_lines)))
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))


def test_validate_handoff_artifact_rejects_a_reference_link_with_no_descriptor(
    tmp_path: Path,
) -> None:
    # The shape the scaffold used to TEACH: `## References` is exempt from the
    # content ceiling and required to hold a link, so links pool here, and the
    # placeholder modelled them arriving context-free.
    result = _run_with_references(tmp_path, "- [guide](docs/guide.md)")
    assert result.returncode == 1
    assert "no descriptor on the link's own line" in result.stderr
    assert "- [guide](docs/guide.md)" in result.stderr


def test_validate_handoff_artifact_accepts_a_reference_descriptor(tmp_path: Path) -> None:
    result = _run_with_references(tmp_path, "- [guide](docs/guide.md) — what the guide holds.")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_accepts_a_descriptor_before_the_link(tmp_path: Path) -> None:
    # Context ahead of the link is context. The rule asks for a line that is not
    # ONLY a link, not for one particular punctuation.
    result = _run_with_references(tmp_path, "- See [guide](docs/guide.md) for the demo walkthrough.")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_rejects_a_descriptor_wrapped_onto_the_next_line(
    tmp_path: Path,
) -> None:
    # SAME-LINE is the decision, and this is the case that makes it non-obvious:
    # the entry reads fine to a human and still leaves a physical line whose whole
    # content is one link, which a same-entry rule would call clean. This repo's
    # own handoff carried entries of exactly this shape when the rule landed --
    # under `## Continuation Capability`, not `## References`, so the rule did not
    # refuse them; the docs-graph gate is what counted them.
    result = _run_with_references(
        tmp_path,
        "- [guide](docs/guide.md)",
        "  — what the guide holds, on the following line.",
    )
    assert result.returncode == 1
    assert "no descriptor on the link's own line" in result.stderr


def test_the_reference_rule_stops_at_the_next_heading() -> None:
    # The rule is scoped to `## References`, and the H2 check asserts membership,
    # not ORDER. With the scan running to EOF, a handoff whose References section
    # was not last had the FOLLOWING section's bullets refused under a message
    # naming References.
    #
    # In-process, unlike its neighbours here: the CLI contract for this rule is
    # already proven by the tests above, and this one is about which LINES the
    # predicate reads. A fourth subprocess call site would buy no coverage the
    # others do not have.
    validator = import_repo_module(__file__, "scripts.validate_handoff_artifact")
    lines = [
        "# Demo Handoff",
        "",
        "## References",
        "",
        "- [guide](docs/guide.md) — what the guide holds.",
        "",
        "## Discuss",
        "",
        "- [guide](docs/guide.md)",
    ]
    validator.validate_reference_descriptors(lines)

    # And the same bare bullet INSIDE the section is still refused, so the bound
    # is what changed rather than the rule going quiet.
    lines[4] = "- [guide](docs/guide.md)"
    with pytest.raises(validator.ValidationError):
        validator.validate_reference_descriptors(lines)


def test_validate_handoff_artifact_reports_every_descriptorless_reference_at_once(
    tmp_path: Path,
) -> None:
    # One pass, like the ownership rule: a References section with N bare links
    # must not cost N gate runs.
    result = _run_with_references(
        tmp_path,
        "- [first](docs/guide.md)",
        "- [second](docs/guide.md)",
        "- [third](docs/guide.md) — this one is fine.",
    )
    assert result.returncode == 1
    assert "2 `## References` entry(s)" in result.stderr


def test_handoff_budget_still_charges_for_prose_density(tmp_path: Path) -> None:
    # The other half: padding `## References` buys no room for content. 56 state
    # bullets + 4 fixed content lines put the body 2 over the ceiling.
    state = [f"- state detail {index} in `git status --short`" for index in range(MAX_CONTENT_LINES - 2)]
    repo = seed_repo(tmp_path, _handoff_with(state, ["- [guide](docs/guide.md) — the demo guide."]))
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert f"{MAX_CONTENT_LINES + 2} content lines (limit {MAX_CONTENT_LINES})" in result.stderr


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
        "- Reproduce per [the guide](docs/guide.md):",
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
                "- [guide](docs/guide.md) — the demo guide.",
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
                "- [guide](docs/guide.md) — the demo guide.",
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
                "- [guide](docs/guide.md) — the demo guide.",
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
                "- [guide](docs/guide.md) — the demo guide.",
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
