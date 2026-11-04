"""A `- Risk Class:` value is read apart from the explanatory prose an author appends.

Reading the whole line as the value turned prose into an unknown class, routed every new
subject in the repo to `repair-risk-declaration`, and pointed that run at another
subject's record.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_debug_plan import run_plan, write_adapter, write_forced_risk_artifact

RISK_CLASS_WITH_PROSE = (
    ("none yet; provider-seam note: the listing cap is undocumented", ["none"]),
    ("none (no seam: the failure is local, see Evidence)", ["none"]),
    ("none -- the retry path is local", ["none"]),
    ("none — the retry path is local", ["none"]),
    ("operator-visible-recovery: the operator reruns the sweep", ["operator-visible-recovery"]),
    ("external-seam (runner disk state, owned by a shared workflow)", ["external-seam"]),
    ("external-seam, repeated-symptom; both observed on the host", ["external-seam", "repeated-symptom"]),
)


@pytest.mark.parametrize(("risk_line", "classes"), RISK_CLASS_WITH_PROSE)
def test_risk_class_value_is_read_apart_from_explanatory_prose(
    tmp_path: Path, risk_line: str, classes: list[str]
) -> None:
    """A valid value followed by prose is a valid declaration, not an unparseable one."""
    repo = tmp_path / "repo"
    write_forced_risk_artifact(repo, risk_class=risk_line)

    payload = run_plan(repo, subject="fresh-subject")

    assert payload["artifact"]["risk_classes"] == classes
    assert payload["artifact"]["risk_parse_error"] is None
    assert payload["artifact"]["risk_scope_established"] is True
    assert payload["mode"] != "repair-risk-declaration"


@pytest.mark.parametrize("risk_line", ["none, bogus (prose)", "bogus; prose", "(prose first) none"])
def test_prose_does_not_launder_an_unknown_risk_value(tmp_path: Path, risk_line: str) -> None:
    repo = tmp_path / "repo"
    write_forced_risk_artifact(repo, risk_class=risk_line)

    payload = run_plan(repo, subject="fresh-subject")

    assert payload["artifact"]["risk_scope_established"] is False
    assert payload["mode"] == "repair-risk-declaration"


@pytest.mark.parametrize(("risk_line", "_classes"), RISK_CLASS_WITH_PROSE[:4])
def test_new_subject_leaves_another_subjects_valid_prose_record_alone(
    tmp_path: Path, risk_line: str, _classes: list[str]
) -> None:
    """The reported instance: an open record of ANOTHER subject whose risk line carries prose.

    The planner told the new subject's run to repair -- and so write into -- that record.
    """
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    foreign = "charness-artifacts/debug/2026-05-06-orphan-cache-sweep.md"
    (repo / foreign).write_text(
        "\n".join(
            [
                "# Debug Review",
                "",
                "## Seam Risk",
                "",
                "- Interrupt ID: none",
                f"- Risk Class: {risk_line}",
                "- Seam: none",
                "- Disproving Observation: none",
                "- What Local Reasoning Cannot Prove: none",
                "- Generalization Pressure: none",
                "",
                "## Interrupt Decision",
                "",
                "- Resolution: open",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (debug_dir / "latest.md").symlink_to(Path(foreign).name)

    payload = run_plan(repo, subject="retention-orphan-enoent")

    assert payload["mode"] == "fresh-investigation-with-prior-memory"
    assert payload["next_action"]["kind"] == "scaffold-debug-artifact"
    assert payload["next_action"]["write_artifact_path"] != foreign
    assert payload["next_action"]["write_artifact_effect"] == "create_new_file"
    assert payload["next_action"]["refused_write_artifact_path"] == foreign

    owner = run_plan(repo, subject="orphan-cache-sweep")
    assert owner["mode"] == "continue-existing-artifact"
    assert owner["next_action"]["write_artifact_path"] == foreign
