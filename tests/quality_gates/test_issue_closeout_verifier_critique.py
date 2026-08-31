"""Resolution-critique gate tests for issue verify-closeout.

Split out of `test_issue_closeout_verifier.py` so the carrier/state file stays
under the test-file length cap. Tests here only exercise the
`resolution_critique_check` payload; the adapter-backed final-state cases live
in the sibling file.
"""
from __future__ import annotations

from pathlib import Path

from tests.quality_gates.issue_closeout_support import (
    bug_closeout_body,
    load_verify_module,
)

_FENCED_CRITIQUE = (
    "```text\n"
    "Critique: blocked synthetic-test-harness: this fenced example "
    "does not count as live resolution proof\n"
    "```"
)


def _write_critique(tmp_path: Path, relative: str, body: str = "# Critique\n\nbody\n") -> Path:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _critique_check(repo: Path, body: str, numbers: list[int] | None = None):
    return load_verify_module()._CRITIQUE.check_resolution_critique(
        repo_root=repo,
        body=body,
        classification="bug",
        numbers=list(numbers or [42]),
        repository="corca-ai/charness",
    )


def test_bug_closeout_treats_absent_or_fenced_critique_as_missing(tmp_path: Path) -> None:
    for critique_line in (None, _FENCED_CRITIQUE):
        check = _critique_check(tmp_path, bug_closeout_body(critique_line=critique_line))
        assert check["missing"] == ["resolution_critique"], critique_line


def test_bug_closeout_with_critique_artifact_path_is_accepted(tmp_path: Path) -> None:
    _write_critique(tmp_path, "charness-artifacts/critique/res-42.md")
    check = _critique_check(
        tmp_path,
        bug_closeout_body(critique_line="Critique: charness-artifacts/critique/res-42.md"),
    )
    assert check["ok"] is True
    via = {entry["via"] for entry in check["satisfied"]}
    assert via == {"evidence"}


def test_a_bundle_critique_must_bind_every_closed_number(tmp_path: Path) -> None:
    cases = (
        (
            "Critique #2: charness-artifacts/critique/only-2.md",
            "only-2.md",
            "# Critique\n\nIssue 2 only.\n",
            [1],
            None,
        ),
        (
            "Critique: charness-artifacts/critique/unqualified.md",
            "unqualified.md",
            "# Critique\n\nIssue 2 only.\n",
            [1, 2],
            None,
        ),
        (
            "Critique #1 #2: charness-artifacts/critique/both.md",
            "both.md",
            "# Critique\n\nBundle for #1 and #2.\n",
            [],
            None,
        ),
        (
            "Critique #1 #2: charness-artifacts/critique/only-1.md",
            "only-1.md",
            "# Critique\n\nIssue 1 only.\n",
            [2],
            2,
        ),
    )
    for critique_line, artifact, artifact_body, missing, binding_failure in cases:
        path = _write_critique(
            tmp_path, f"charness-artifacts/critique/{artifact}", artifact_body
        )
        body = bug_closeout_body(
            close_line="Close #1.\nClose #2.",
            critique_line=critique_line,
            behavior_line=(
                "Behavior #1: behavior test exercises the fix (distinct channel)\n"
                "Behavior #2: fetch/readback of the affected surface (distinct channel)"
            ),
        )
        check = _critique_check(tmp_path, body, numbers=[1, 2])
        assert check["missing_issue_bindings"] == missing, artifact
        if critique_line.startswith("Critique:") and " #" not in critique_line:
            assert check["checks"] == []
        if binding_failure is not None:
            assert check["binding_failures"][0]["number"] == binding_failure
            assert check["binding_failures"][0]["path"] == str(path)
            assert str(binding_failure) in check["binding_failures"][0]["reason"]


def test_a_blocked_critique_shorter_than_the_floor_is_rejected(tmp_path: Path) -> None:
    for critique_line in (
        "Critique: blocked host-down",
        "Critique: blocked xxxxxxxxxxxxxxxxx",
    ):
        check = _critique_check(tmp_path, bug_closeout_body(critique_line=critique_line))
        assert check["ok"] is False, critique_line
        assert check["invalid_skips"][0]["name"] == "resolution_critique"


def test_non_bug_classifications_skip_the_critique_floor(tmp_path: Path) -> None:
    helper = load_verify_module()._CRITIQUE.check_resolution_critique
    for classification in ("question", "feature", "deferred-work"):
        check = helper(
            repo_root=tmp_path,
            body="Close #42.\n",
            classification=classification,
            numbers=[42],
            repository="corca-ai/charness",
        )
        assert check == {"ok": True, "skipped_classification": classification}, classification


def test_a_skipped_critique_is_named_on_the_check_and_the_verdict(tmp_path: Path) -> None:
    check = _critique_check(tmp_path, bug_closeout_body())
    assert check["ok"] is True
    assert "was SKIPPED" in check["review_advisory"][0]
    assert "#42" in check["review_advisory"][0]


def test_an_executed_critique_leaves_the_skip_advisory_empty(tmp_path: Path) -> None:
    _write_critique(
        tmp_path, "charness-artifacts/critique/res-42.md", "Critique of the #42 resolution.\n"
    )
    check = _critique_check(
        tmp_path,
        bug_closeout_body(critique_line="Critique: charness-artifacts/critique/res-42.md"),
    )
    assert check["ok"] is True
    assert check.get("review_advisory", []) == []
