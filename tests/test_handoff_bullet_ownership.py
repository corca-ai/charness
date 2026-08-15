"""The handoff ownership rule: every state/next-action entry carries an owner.

Split out of `test_handoff_artifact.py` when that module crossed its length cap.
The boundary is cohesive rather than mechanical: these cases all exercise one
predicate and one parser (`handoff_bullet_ownership`), while the parent module
keeps the artifact's shape, budget, and regenerable-facts rules.

Most of these name an input that PASSED a previous implementation. Three review
rounds each found the repair carrying the class it fixed, so the inputs are the
record of what the rule actually got wrong.
"""
from __future__ import annotations

from pathlib import Path

from tests.handoff_artifact_fixtures import (
    OWNED_NEXT,
    OWNED_STATE,
    run_on_state,
    run_script,
    seed_repo,
)


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
                "- [guide](docs/guide.md) — the demo guide.",
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

def test_validate_handoff_artifact_gives_a_fenced_block_no_ownership(tmp_path: Path) -> None:
    """A fenced block owns nothing, and that is the narrowed contract.

    Attaching a fence to the bullet above it was the feature two review rounds
    kept finding laundering paths through: the `charness-publish-state-claim`
    ledger block exempted whatever bullet preceded it, and the rule that
    detached it could be defeated by deleting one blank line. The owned sections
    are a flat list of links; a bullet that needs a code block belongs in the
    artifact it should be linking.
    """
    result = run_on_state(
        tmp_path,
        "- Reproduce with:",
        "",
        "```bash",
        "python3 -m pytest -q tests/test_handoff_artifact.py",
        "```",
    )
    assert result.returncode == 1
    assert "carry no owner" in result.stderr

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
                "- [guide](docs/guide.md) — the demo guide.",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr

def test_validate_handoff_artifact_charges_a_sub_bullet_on_its_own(tmp_path: Path) -> None:
    """There is no child rule: every marker starts an entry.

    Each of five review rounds found a defect in whichever child rule was
    current — a merge that laundered an unowned parent upward, a skip whose
    verdict flipped on a blank line, and an indent test that swallowed a real
    SIBLING of a numbered parent so it was never reported at all. A flat list
    has no children, so the branch is gone; nesting costs a repeated link.
    """
    result = run_on_state(
        tmp_path,
        "- Ruling status lives in [the rulings artifact](docs/guide.md).",
        "  - Ruling 4's deletion half predates its ruling.",
    )
    assert result.returncode == 1
    assert "deletion half predates" in result.stderr


def test_validate_handoff_artifact_reports_a_sibling_of_a_numbered_parent(tmp_path: Path) -> None:
    # A `1. ` marker's content column is 3, so a marker indented 2 is a SIBLING.
    # The fixed-width child test read it as a child and dropped it entirely.
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
                "1. [Thesis](docs/guide.md) — what it holds.",
                "  2. An unowned claim nobody checks.",
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
    assert "An unowned claim nobody checks" in result.stderr


def test_validate_handoff_artifact_refuses_an_unclosed_fence(tmp_path: Path) -> None:
    """Silence is the one failure a floor must not have.

    Every line after a stray delimiter reads as fenced, so the ownership scan
    sees no entries and passes green. Markdownlint has no rule for this, so an
    earlier record deferring it to the lint gate was false.
    """
    result = run_on_state(
        tmp_path,
        "- [ok](docs/guide.md) — holds it.",
        "",
        "```bash",
        "echo no closing fence",
    )
    assert result.returncode == 1
    assert "could not be paired" in result.stderr


def test_validate_handoff_artifact_accepts_a_tilde_line_inside_a_backtick_fence(tmp_path: Path) -> None:
    """Pins the CommonMark half of the fence rule, not just the toggle's output.

    The existing tilde test asserts a failure plus a substring, so a toggle
    regression would ADD a spurious violation and leave both assertions true —
    it cannot fail from the bug it looks like it guards. This one exits 0 only
    if a `~~~` line inside a backtick fence is content.
    """
    result = run_on_state(
        tmp_path,
        "- [ok](docs/guide.md) — holds it.",
        "",
        "```",
        "~~~",
        "```",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_accepts_a_longer_closing_fence_run(tmp_path: Path) -> None:
    # `len(run) >= len(open_marker)` had no test at all: a 3-run opener closed
    # by a 4-run is valid CommonMark and must not read as unpaired.
    result = run_on_state(
        tmp_path,
        "- [ok](docs/guide.md) — holds it.",
        "",
        "```",
        "content",
        "````",
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


# --- round-1 review findings ---
# Each names an input the first implementation got wrong. Most PASSED when they
# should have failed; the blank-line case is the opposite -- round 1 made it
# pass, and the later narrowing deliberately charges it again.


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
                "- [guide](docs/guide.md) — the demo guide.",
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


def test_validate_handoff_artifact_ends_an_entry_at_a_blank_line(tmp_path: Path) -> None:
    """A blank line ends the entry, so an owner below one is not found.

    Carrying an entry across a blank into a second paragraph was one of the
    three branches whose interaction produced the round-2 and round-3 defects.
    A multi-paragraph list item is not the shape these sections have, and the
    failure direction is the safe one: the author is told to put the link on
    the bullet.
    """
    result = run_on_state(
        tmp_path,
        "- Ruling 1 is executed, both halves.",
        "",
        "  Status per ruling lives in [the rulings artifact](docs/guide.md).",
    )
    assert result.returncode == 1
    assert "carry no owner" in result.stderr


# --- round-2 and round-3 review findings: the repairs' own defects ---


def test_validate_handoff_artifact_does_not_let_a_child_launder_its_parent(tmp_path: Path) -> None:
    """Round 3: the inheritance merge ran BACKWARDS.

    It appended the child's text into the parent's, so a link in the child made
    an unowned parent owned. Round 4 found the same laundering surviving for an
    ATTACHED child, where the verdict then turned on whether a blank line
    happened to precede it. A child is now skipped, never merged.
    """
    result = run_on_state(
        tmp_path,
        "- An unowned claim nobody checks.",
        "<!-- charness-publish-state-claim:demo -->",
        "",
        "  - Detail in [the guide](docs/guide.md).",
    )
    assert result.returncode == 1
    assert "An unowned claim nobody checks" in result.stderr


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


def test_validate_handoff_artifact_reads_a_backticked_path_as_unowned(tmp_path: Path) -> None:
    """A path is a link, not a command owner.

    Accepting a bare code-span path contradicted two shipped surfaces that tell
    the author it is not an owner, and this repo's own link gate rejects a
    backticked repo path in the handoff outright — so the accepted form could
    not have shipped here anyway.
    """
    result = run_on_state(tmp_path, "- Re-take the gate with `./scripts/run-quality.sh`.")
    assert result.returncode == 1
    assert "carry no owner" in result.stderr


def test_validate_handoff_artifact_reads_a_padded_identifier_as_unowned(tmp_path: Path) -> None:
    # CommonMark padding put spaces inside the span, so an unstripped
    # whitespace test read a bare identifier as a command.
    result = run_on_state(tmp_path, "- The module ` inventory_boundary_bypass_lib ` records nothing.")
    assert result.returncode == 1
    assert "carry no owner" in result.stderr
