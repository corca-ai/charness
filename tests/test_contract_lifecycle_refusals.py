from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from scripts import apply_contract_transition as transition_writer
from scripts import contract_register_lib as register
from scripts import record_contract_citation as citation_writer
from scripts import record_contract_graduation_proposal as proposal_writer
from scripts import render_contract_retention_review as retention_review
from tests.test_contract_register import ROOT, _prepare


def _approval(repo: Path) -> str:
    path = repo / "approval.md"
    path.write_text("# Approval\n", encoding="utf-8")
    return path.name


def _graduation_event(**updates: object) -> dict[str, object]:
    event: dict[str, object] = {
        "sequence": 1,
        "event_id": "apply-a",
        "action": "apply-graduation",
        "approval_ref": "approval.md",
        "rationale": "Reviewed.",
        "proposal_id": "proposal-a",
    }
    event.update(updates)
    return event


def _proposal(**updates: object) -> dict[str, object]:
    proposal: dict[str, object] = {
        "proposal_id": "proposal-a",
        "lesson_id": "a",
        "source_retro": "charness-artifacts/retro/source.md",
        "evidence_session_ids": ["session-1", "session-2"],
        "target_path": "AGENTS.md",
        "target_heading": "New Unit",
        "proposed_unit_id": "AGENTS.md#new-unit",
        "rationale": "Reviewed.",
        "displacement_unit_ids": [],
    }
    proposal.update(updates)
    return proposal


def test_contract_reference_and_unit_shape_refusals(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    assert register.canonical_markdown_ref(tmp_path, "") is False
    assert register.canonical_markdown_ref(tmp_path, "../outside.md") is False
    with pytest.raises(ValueError, match="invalid unit shapes"):
        register._validate_units([{}], "units")
    valid = [
        {"unit_id": "z.md#z", "path": "z.md", "heading": "Z"},
        {"unit_id": "a.md#a", "path": "a.md", "heading": "A"},
    ]
    with pytest.raises(ValueError, match="lexically sorted"):
        register._validate_units(valid, "units")


def test_membership_replay_refuses_each_closed_transition_shape(tmp_path: Path) -> None:
    _approval(tmp_path)
    active = {"AGENTS.md#alpha": {"unit_id": "AGENTS.md#alpha", "path": "AGENTS.md", "heading": "Alpha"}}
    proposal = _proposal(displacement_unit_ids=["AGENTS.md#alpha"])
    cases = [
        ({"event_id": "bad"}, "invalid shape"),
        (_graduation_event(sequence=2), "sequences must start"),
        (_graduation_event(approval_ref=""), "reviewed approval"),
        (_graduation_event(action="unknown"), "unknown action"),
    ]
    for event, message in cases:
        with pytest.raises(ValueError, match=message):
            register._replay_membership(
                list(active.values()), [event], {"proposal-a": proposal}, budget=1, repo_root=tmp_path
            )

    with pytest.raises(ValueError, match="unexpected or missing"):
        register._apply_graduation({**_graduation_event(), "extra": True}, active.copy(), {}, {"proposal-a": proposal}, set())
    with pytest.raises(ValueError, match="unavailable proposal"):
        register._apply_graduation(_graduation_event(), active.copy(), {}, {}, set())
    with pytest.raises(ValueError, match="inactive displacement"):
        register._apply_graduation(
            _graduation_event(), active.copy(), {}, {"proposal-a": _proposal(displacement_unit_ids=["missing"])}, set()
        )
    with pytest.raises(ValueError, match="reuses membership identity"):
        register._apply_graduation(
            _graduation_event(), active.copy(), {}, {"proposal-a": _proposal(proposed_unit_id="AGENTS.md#alpha")}, set()
        )
    with pytest.raises(ValueError, match="unexpected or missing"):
        register._apply_retirement({"event_id": "retire"}, active.copy(), {})
    with pytest.raises(ValueError, match="invalid units or disposition"):
        register._apply_retirement(
            {
                "sequence": 1,
                "event_id": "retire",
                "action": "retire",
                "approval_ref": "approval.md",
                "rationale": "Reviewed.",
                "retired_unit_ids": [],
                "successor_unit_ids": [],
                "disposition": register.NO_BINDING_BEHAVIOR,
            },
            active.copy(),
            {},
        )
    with pytest.raises(ValueError, match="exceeds fixed unit budget"):
        register._replay_membership(
            [], [_graduation_event()], {"proposal-a": _proposal()}, budget=0, repo_root=tmp_path
        )


def test_register_replay_refuses_projection_and_inactive_proposal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _prepare(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    kwargs = {
        "repo_root": tmp_path,
        "output_dir": path.parent,
        "summary_path": path.parent / "recent-lessons.md",
        "path": path,
        "require_live_match": False,
    }
    monkeypatch.setattr(register, "_committed_state", lambda *_args: None)
    with pytest.raises(ValueError, match="deterministic replay"):
        register.replay_validated_contract_register_payload(
            **kwargs, payload={**payload, "units": []}
        )

    invalid_retired = [{"unit_id": "retired"}]
    monkeypatch.setattr(
        register,
        "_replay_membership",
        lambda *_args, **_kwargs: (payload["units"], invalid_retired, set()),
    )
    with pytest.raises(ValueError, match="invalid projection shape"):
        register.replay_validated_contract_register_payload(
            **kwargs, payload={**payload, "retired_units": invalid_retired}
        )

    proposal = _proposal(displacement_unit_ids=["missing"])
    monkeypatch.setattr(register, "_validate_proposals", lambda *_args: {"proposal-a": proposal})
    monkeypatch.setattr(
        register,
        "_replay_membership",
        lambda *_args, **_kwargs: (payload["units"], payload["retired_units"], set()),
    )
    with pytest.raises(ValueError, match="inactive displacement"):
        register.replay_validated_contract_register_payload(
            **kwargs, payload={**payload, "graduation_proposals": [proposal]}
        )


def test_operator_helpers_reject_missing_or_incompatible_inputs(tmp_path: Path) -> None:
    for call, message in (
        (lambda: transition_writer._nonblank(" ", "event_id"), "must be non-empty"),
        (lambda: proposal_writer._nonblank(" ", "proposal_id"), "must be non-empty"),
        (
            lambda: citation_writer.append_citation(
                repo_root=tmp_path, event_id="", source_retro="x", unit_id="u", anchor="a"
            ),
            "every field must be non-empty",
        ),
        (
            lambda: transition_writer.apply_transition(
                repo_root=tmp_path, action="retire", event_id="e", approval_ref="a.md",
                rationale="r", proposal_id=None, retired_unit_ids=[], successor_unit_ids=[],
                disposition=None, execute=False,
            ),
            "missing contract register",
        ),
        (
            lambda: proposal_writer.append_proposal(
                repo_root=tmp_path, proposal_id="p", lesson_id="a", source_retro="r.md",
                evidence_session_ids=["s1", "s2"], target_path="AGENTS.md",
                target_heading="H", rationale="r", displacement_unit_ids=[],
            ),
            "missing contract register",
        ),
    ):
        with pytest.raises((FileNotFoundError, ValueError), match=message):
            call()

    _prepare(tmp_path)
    common = dict(
        repo_root=tmp_path, event_id="e", approval_ref="approval.md", rationale="r",
        retired_unit_ids=[], successor_unit_ids=[], disposition=None, execute=False,
    )
    with pytest.raises(ValueError, match="graduation accepts only"):
        transition_writer.apply_transition(action="apply-graduation", proposal_id=None, **common)
    with pytest.raises(ValueError, match="retirement does not accept"):
        transition_writer.apply_transition(action="retire", proposal_id="p", **common)
    with pytest.raises(ValueError, match="unknown action"):
        transition_writer.apply_transition(action="unknown", proposal_id=None, **common)


def test_citation_and_retention_main_success_paths(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _prepare(tmp_path)
    unit_id = json.loads(path.read_text(encoding="utf-8"))["units"][0]["unit_id"]
    assert citation_writer.main([
        "--repo-root", str(tmp_path), "--event-id", "cite-main", "--source-retro",
        "charness-artifacts/retro/source.md", "--unit-id", unit_id, "--anchor", "Waste",
    ]) == 0
    assert json.loads(capsys.readouterr().out)["event_id"] == "cite-main"
    assert retention_review.main(["--repo-root", str(tmp_path)]) == 0
    assert json.loads(capsys.readouterr().out)["verdict"] == "non-authorizing-evidence-only"


@pytest.mark.parametrize(
    "script,args,error",
    [
        (
            "apply_contract_transition.py",
            ["--action", "retire", "--event-id", "e", "--approval-ref", "a.md", "--rationale", "r"],
            "missing contract register",
        ),
        (
            "record_contract_graduation_proposal.py",
            ["--proposal-id", "p", "--lesson-id", "a", "--source-retro", "r.md", "--evidence-session-id", "s1", "--evidence-session-id", "s2", "--target-path", "AGENTS.md", "--target-heading", "H", "--rationale", "r"],
            "missing contract register",
        ),
        (
            "record_contract_citation.py",
            ["--event-id", "c", "--source-retro", "r.md", "--unit-id", "u", "--anchor", "a"],
            "missing contract register",
        ),
        ("render_contract_retention_review.py", [], "missing contract register"),
    ],
)
def test_contract_operator_entrypoints_report_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    script: str,
    args: list[str],
    error: str,
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(sys, "argv", [script, "--repo-root", str(repo), *args])
    with pytest.raises(SystemExit) as exit_result:
        runpy.run_path(str(ROOT / "scripts" / script), run_name="__main__")
    assert exit_result.value.code == 1
    assert error in capsys.readouterr().err
