from __future__ import annotations

import copy
import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts import apply_contract_transition as transition_writer
from scripts import contract_register_lib as register
from scripts import lesson_ledger_lib as lesson_ledger
from scripts import record_contract_citation as citation_writer
from scripts import record_contract_graduation_proposal as proposal_writer
from scripts import render_contract_retention_review as retention_review
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _contract_sources(repo: Path) -> None:
    for relative, title in (
        ("AGENTS.md", "Alpha"),
        ("docs/conventions/implementation-discipline.md", "Beta"),
        ("docs/conventions/operating-contract.md", "Gamma"),
    ):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Contract\n\n## {title}\n", encoding="utf-8")


def _retro(repo: Path, name: str = "source.md") -> None:
    path = repo / "charness-artifacts/retro" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n- useful lesson (recurrence-class: a)\n",
        encoding="utf-8",
    )


def _session(session_id: str) -> dict:
    snapshot = {
        "kind": "charness.lesson-selection-preview",
        "schema_version": 1,
        "selection_policy_version": 2,
        "seed": session_id,
        "eligible_count": 1,
        "bucket_counts": {
            "recent": 1,
            "value": 0,
            "uncertainty": 0,
            "archive": 0,
            "archive_fallback_uncertainty": 0,
        },
        "lesson_ids": ["a"],
    }
    return {
        "session_id": session_id,
        "snapshot": snapshot,
        "snapshot_sha256": lesson_ledger.snapshot_sha256(snapshot),
    }


def _ledger(repo: Path) -> None:
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    payload = {
        "kind": "charness.lesson-ledger",
        "schema_version": lesson_ledger.SCHEMA_VERSION,
        "transitions": [
            {
                "sequence": 1,
                "transition_id": "seed-a",
                "lesson_id": "a",
                "source_retro": "charness-artifacts/retro/source.md",
            }
        ],
        "active_lesson_budget": 50,
        "lifecycle_events": [],
        "score_events": [
            {
                "event_id": "score-1",
                "session_id": "session-1",
                "source_retro": "charness-artifacts/retro/source.md",
                "lesson_id": "a",
                "score": 1,
            },
            {
                "event_id": "score-2",
                "session_id": "session-2",
                "source_retro": "charness-artifacts/retro/second.md",
                "lesson_id": "a",
                "score": 0,
            },
        ],
        "session_events": [_session("session-1"), _session("session-2")],
        "lessons": {
            "a": {
                "source_retro": "charness-artifacts/retro/source.md",
                "transition_id": "seed-a",
                "score_total": 1,
                "score_count": 2,
                "state": "active",
                "last_lifecycle_event_id": None,
            }
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _register(repo: Path) -> Path:
    path = repo / "charness-artifacts/retro/contract-register.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(register.initial_contract_register(repo)), encoding="utf-8")
    return path


def _prepare(repo: Path) -> Path:
    _contract_sources(repo)
    _retro(repo)
    _retro(repo, "second.md")
    _ledger(repo)
    return _register(repo)


def _validate(repo: Path) -> dict:
    return register.validate_contract_register(
        repo_root=repo,
        output_dir=repo / "charness-artifacts/retro",
        summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
    )


def test_register_rebuilds_unfenced_h2_units_and_checker_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    _prepare(tmp_path)
    (tmp_path / "AGENTS.md").write_text(
        "# Contract\n\n## Alpha — rule!\n\n````md\n~~~\n## Ignored\n````\n\n  ## Indented\n",
        encoding="utf-8",
    )
    _register(tmp_path)
    assert register.build_contract_units(tmp_path)[0] == {
        "unit_id": "AGENTS.md#alpha-rule",
        "path": "AGENTS.md",
        "heading": "Alpha — rule!",
    }
    units = register.build_contract_units(tmp_path)
    assert "AGENTS.md#ignored" not in {unit["unit_id"] for unit in units}
    assert "AGENTS.md#indented" in {unit["unit_id"] for unit in units}
    assert _validate(tmp_path)["unit_count"] == 4

    checker = load_script_module("check_contract_register_for_test", ROOT / "scripts/check_contract_register.py")
    monkeypatch.setattr(sys, "argv", ["check_contract_register.py", "--repo-root", str(tmp_path)])
    assert checker.main() == 0
    assert capsys.readouterr().out == (
        "Validated contract register: 4 active units, 0 retired, 0 citations, "
        "0 proposals, 0 applied transitions.\n"
    )


def test_register_rejects_noncanonical_citation_and_nonempty_catches(tmp_path: Path) -> None:
    path = _prepare(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    unit = payload["units"][0]["unit_id"]
    payload["citation_events"] = [{"event_id": "cite-1", "source_retro": "charness-artifacts/retro/../retro/source.md", "unit_id": unit, "anchor": "Lesson"}]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="existing repo retro"):
        _validate(tmp_path)
    (tmp_path / "charness-artifacts/retro/recent-lessons.md").write_text("# Summary\n", encoding="utf-8")
    payload["citation_events"][0]["source_retro"] = "charness-artifacts/retro/recent-lessons.md"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="existing repo retro"):
        _validate(tmp_path)
    payload["citation_events"] = []
    payload["catch_events"] = [{"event_id": "not-implemented"}]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="catch_events must remain empty"):
        _validate(tmp_path)


def test_empty_register_is_inspectable_without_a_lesson_ledger(tmp_path: Path) -> None:
    _contract_sources(tmp_path)
    _register(tmp_path)
    assert _validate(tmp_path) == {
        "unit_count": 3,
        "retired_unit_count": 0,
        "citation_event_count": 0,
        "graduation_proposal_count": 0,
        "applied_transition_count": 0,
        "path": "charness-artifacts/retro/contract-register.json",
    }


def test_register_requires_displacement_for_a_budgeted_graduation_proposal(tmp_path: Path) -> None:
    path = _prepare(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    proposal = {
        "proposal_id": "proposal-1",
        "lesson_id": "a",
        "source_retro": "charness-artifacts/retro/source.md",
        "evidence_session_ids": ["session-1", "session-2"],
        "target_path": "AGENTS.md",
        "target_heading": "A New Unit",
        "proposed_unit_id": "AGENTS.md#a-new-unit",
        "rationale": "Cited lesson warrants a proposed addition.",
        "displacement_unit_ids": [],
    }
    payload["graduation_proposals"] = [proposal]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="fixed unit budget"):
        _validate(tmp_path)
    proposal["displacement_unit_ids"] = [payload["units"][0]["unit_id"]]
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert _validate(tmp_path)["graduation_proposal_count"] == 1
    duplicate = copy.deepcopy(proposal)
    duplicate["proposal_id"] = "proposal-2"
    duplicate["displacement_unit_ids"] = [payload["units"][1]["unit_id"]]
    payload["graduation_proposals"].append(duplicate)
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="reuses a contract unit identity"):
        _validate(tmp_path)


def test_proposal_apply_and_retention_review_preserve_retired_history(tmp_path: Path) -> None:
    path = _prepare(tmp_path)
    approval = tmp_path / "approval.md"
    approval.write_text("# Reviewed Approval\n", encoding="utf-8")
    alpha = "AGENTS.md#alpha"
    proposal_command = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/record_contract_graduation_proposal.py"),
            "--repo-root",
            str(tmp_path),
            "--proposal-id",
            "proposal-a",
            "--lesson-id",
            "a",
            "--source-retro",
            "charness-artifacts/retro/source.md",
            "--evidence-session-id",
            "session-1",
            "--evidence-session-id",
            "session-2",
            "--target-path",
            "AGENTS.md",
            "--target-heading",
            "A New Unit",
            "--rationale",
            "Two declared sessions justify review, not automatic graduation.",
            "--displacement-unit-id",
            alpha,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proposal_command.returncode == 0, proposal_command.stderr
    assert yaml.safe_load(proposal_command.stdout)["proposal_id"] == "proposal-a"
    citation_writer.append_citation(
        repo_root=tmp_path,
        event_id="cite-alpha",
        source_retro="charness-artifacts/retro/source.md",
        unit_id=alpha,
        anchor="The session used the original rule.",
    )
    before_invalid = path.read_bytes()
    with pytest.raises(ValueError, match="two scored evidence sessions"):
        proposal_writer.append_proposal(
            repo_root=tmp_path,
            proposal_id="proposal-too-early",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            evidence_session_ids=["session-1"],
            target_path="AGENTS.md",
            target_heading="Too Early",
            rationale="Insufficient evidence.",
            displacement_unit_ids=[alpha],
        )
    assert path.read_bytes() == before_invalid

    (tmp_path / "AGENTS.md").write_text("# Contract\n\n## A New Unit\n", encoding="utf-8")
    before_dry_run = path.read_bytes()
    preview_command = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/apply_contract_transition.py"),
            "--repo-root",
            str(tmp_path),
            "--action",
            "apply-graduation",
            "--event-id",
            "apply-a",
            "--approval-ref",
            "approval.md",
            "--rationale",
            "Reviewed graduation with exact displacement.",
            "--proposal-id",
            "proposal-a",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert preview_command.returncode == 0, preview_command.stderr
    preview = yaml.safe_load(preview_command.stdout)
    assert preview["executed"] is False
    assert path.read_bytes() == before_dry_run
    transition_writer.apply_transition(
        repo_root=tmp_path,
        action="apply-graduation",
        event_id="apply-a",
        approval_ref="approval.md",
        rationale="Reviewed graduation with exact displacement.",
        proposal_id="proposal-a",
        retired_unit_ids=[],
        successor_unit_ids=[],
        disposition=None,
        execute=True,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert {unit["unit_id"] for unit in payload["units"]} == {
        "AGENTS.md#a-new-unit",
        "docs/conventions/implementation-discipline.md#beta",
        "docs/conventions/operating-contract.md#gamma",
    }
    assert payload["retired_units"][0]["unit_id"] == alpha
    assert payload["retired_units"][0]["successor_unit_ids"] == ["AGENTS.md#a-new-unit"]
    assert _validate(tmp_path)["applied_transition_count"] == 1
    review = retention_review.build_retention_review(tmp_path)
    alpha_row = next(row for row in review["rows"] if row["unit_id"] == alpha)
    assert alpha_row["membership"] == "retired"
    assert alpha_row["citation_count"] == 1
    assert review["verdict"] == "non-authorizing-evidence-only"


def test_retirement_requires_matching_docs_and_preserves_append_only_audit(
    tmp_path: Path,
) -> None:
    path = _prepare(tmp_path)
    approval = tmp_path / "approval.md"
    approval.write_text("# Approval\n", encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="live contract H2 inventory"):
        transition_writer.apply_transition(
            repo_root=tmp_path,
            action="retire",
            event_id="retire-alpha",
            approval_ref="approval.md",
            rationale="The behavior is obsolete.",
            proposal_id=None,
            retired_unit_ids=["AGENTS.md#alpha"],
            successor_unit_ids=[],
            disposition=register.NO_BINDING_BEHAVIOR,
            execute=True,
        )
    assert path.read_bytes() == before

    (tmp_path / "AGENTS.md").write_text("# Contract\n", encoding="utf-8")
    transition_writer.apply_transition(
        repo_root=tmp_path,
        action="retire",
        event_id="retire-alpha",
        approval_ref="approval.md",
        rationale="The behavior is obsolete.",
        proposal_id=None,
        retired_unit_ids=["AGENTS.md#alpha"],
        successor_unit_ids=[],
        disposition=register.NO_BINDING_BEHAVIOR,
        execute=True,
    )
    assert _validate(tmp_path)["retired_unit_count"] == 1
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "apply retirement")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["applied_transitions"][0]["rationale"] = "rewritten"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="committed applied transitions"):
        _validate(tmp_path)


def test_heading_slug_treats_underscore_as_punctuation_and_rejects_collisions(tmp_path: Path) -> None:
    _contract_sources(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# Contract\n\n## A_B\n\n## A B\n", encoding="utf-8")
    assert register.heading_slug("A_B") == "a-b"
    with pytest.raises(ValueError, match="colliding H2 identity"):
        register.build_contract_units(tmp_path)


def test_committed_register_state_and_event_prefixes_are_append_only(tmp_path: Path) -> None:
    path = _prepare(tmp_path)
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "seed register")

    initial = json.loads(path.read_text(encoding="utf-8"))
    first = {"event_id": "cite-1", "source_retro": "charness-artifacts/retro/source.md", "unit_id": initial["units"][0]["unit_id"], "anchor": "Lesson"}
    initial["citation_events"] = [first]
    path.write_text(json.dumps(initial), encoding="utf-8")
    assert _validate(tmp_path)["citation_event_count"] == 1
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "cite unit")

    _retro(tmp_path, "second.md")
    appended = copy.deepcopy(initial)
    appended["citation_events"].append({"event_id": "cite-2", "source_retro": "charness-artifacts/retro/second.md", "unit_id": initial["units"][0]["unit_id"], "anchor": "Lesson"})
    path.write_text(json.dumps(appended), encoding="utf-8")
    assert _validate(tmp_path)["citation_event_count"] == 2

    rewritten = copy.deepcopy(appended)
    rewritten["citation_events"][0]["anchor"] = "Edited"
    path.write_text(json.dumps(rewritten), encoding="utf-8")
    with pytest.raises(ValueError, match="committed citation events"):
        _validate(tmp_path)
    rewritten_units = copy.deepcopy(appended)
    rewritten_units["unit_budget"] = 4
    path.write_text(json.dumps(rewritten_units), encoding="utf-8")
    with pytest.raises(ValueError, match="fixed budget"):
        _validate(tmp_path)


def test_schema_v1_refuses_a_post_commit_contract_membership_change(tmp_path: Path) -> None:
    path = _prepare(tmp_path)
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "seed register")
    (tmp_path / "AGENTS.md").write_text("# Contract\n\n## Alpha\n\n## New Contract Unit\n", encoding="utf-8")
    changed = register.initial_contract_register(tmp_path)
    path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError, match="committed seed units"):
        _validate(tmp_path)


def test_register_refuses_a_committed_nonempty_catch_stream(tmp_path: Path, monkeypatch) -> None:
    path = _prepare(tmp_path)
    committed = json.loads(path.read_text(encoding="utf-8"))
    committed["catch_events"] = [{"event_id": "handwritten-catch"}]
    monkeypatch.setattr(register, "_committed_state", lambda *_args: committed)
    with pytest.raises(ValueError, match="committed catch events"):
        _validate(tmp_path)


def test_register_rejects_missing_sources_empty_slugs_and_closed_top_level_shapes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="normalizes to an empty"):
        register.heading_slug("---")
    _contract_sources(tmp_path)
    (tmp_path / "AGENTS.md").unlink()
    with pytest.raises(ValueError, match="missing contract source"):
        register.build_contract_units(tmp_path)
    path = _prepare(tmp_path)
    path.unlink()
    with pytest.raises(FileNotFoundError, match="missing contract register"):
        _validate(tmp_path)
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        _validate(tmp_path)
    payload = json.loads(json.dumps(register.initial_contract_register(tmp_path)))
    for invalid, message in (([], "expected strict"), ({**payload, "schema_version": 1}, "expected strict"), ({**payload, "unit_budget": True}, "container or fixed budget")):
        path.write_text(json.dumps(invalid), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)


def test_register_rejects_committed_invalid_shapes(tmp_path: Path, monkeypatch) -> None:
    path = _prepare(tmp_path)
    cases = [
        ("{", "invalid JSON"),
        ("{}", "unsupported shape"),
        (json.dumps({"kind": register.KIND, "schema_version": 1}), "unsupported shape"),
    ]
    for stdout, message in cases:
        monkeypatch.setattr(
            register.subprocess,
            "run",
            lambda *_args, _stdout=stdout, **_kwargs: subprocess.CompletedProcess([], 0, _stdout, ""),
        )
        with pytest.raises(ValueError, match=message):
            register._committed_state(tmp_path, path)


def test_register_rejects_closed_citation_and_proposal_shapes(tmp_path: Path, monkeypatch) -> None:
    _prepare(tmp_path)
    units = register.build_contract_units(tmp_path)
    ids = {unit["unit_id"] for unit in units}
    unit = units[0]["unit_id"]
    source = "charness-artifacts/retro/source.md"
    valid_citation = {"event_id": "cite", "source_retro": source, "unit_id": unit, "anchor": "Waste"}
    citation_cases = [
        ([{}], "unexpected or missing"),
        ([{**valid_citation, "anchor": ""}], "non-empty string"),
        ([valid_citation, {**valid_citation, "unit_id": units[1]["unit_id"]}], "duplicate identity"),
        ([{**valid_citation, "unit_id": "missing"}], "unknown unit"),
        ([{**valid_citation, "source_retro": "/outside.md"}], "existing repo retro"),
        ([valid_citation, {**valid_citation, "event_id": "cite-2"}], "duplicate citation for unit"),
    ]
    for events, message in citation_cases:
        with pytest.raises(ValueError, match=message):
            register._validate_citations(events, ids, tmp_path)

    base = {
        "proposal_id": "proposal",
        "lesson_id": "a",
        "source_retro": source,
        "evidence_session_ids": ["session-1", "session-2"],
        "target_path": "AGENTS.md",
        "target_heading": "Future",
        "proposed_unit_id": "AGENTS.md#future",
        "rationale": "because",
        "displacement_unit_ids": [unit],
    }
    ledger_path = tmp_path / "charness-artifacts/retro/lesson-ledger.json"
    monkeypatch.setattr(register, "validate_lesson_ledger", lambda **_kwargs: None)
    proposal_cases = [
        ([{}], "unexpected or missing"),
        ([{**base, "rationale": ""}], "non-empty string"),
        ([base, {**base}], "duplicate graduation proposal_id"),
        ([{**base, "source_retro": "other.md"}], "does not cite"),
        ([{**base, "target_path": "other.md"}], "non-canonical"),
        ([{**base, "target_heading": "Alpha", "proposed_unit_id": "AGENTS.md#alpha"}], "reuses a contract unit"),
        ([{**base, "displacement_unit_ids": "not-a-list"}], "invalid displacement"),
        ([{**base, "displacement_unit_ids": ["missing"]}], "invalid displacement"),
    ]
    assert ledger_path.is_file()
    for proposals, message in proposal_cases:
        with pytest.raises(ValueError, match=message):
            register._validate_proposals(
                proposals,
                ids,
                tmp_path,
                ledger_path.parent,
                ledger_path.parent / "recent-lessons.md",
            )

    successor = {
        **base,
        "proposal_id": "proposal-successor",
        "target_heading": "Later",
        "proposed_unit_id": "AGENTS.md#later",
        "displacement_unit_ids": [base["proposed_unit_id"]],
    }
    assert set(
        register._validate_proposals(
            [base, successor],
            ids,
            tmp_path,
            ledger_path.parent,
            ledger_path.parent / "recent-lessons.md",
        )
    ) == {"proposal", "proposal-successor"}


def test_register_checker_cli_reports_validation_failure(tmp_path: Path, monkeypatch, capsys) -> None:
    def fail_validation(**_kwargs: object) -> dict:
        raise ValueError("broken register")

    monkeypatch.setattr(register, "validate_contract_register", fail_validation)
    monkeypatch.setattr(sys, "argv", ["check_contract_register.py", "--repo-root", str(tmp_path)])
    with pytest.raises(SystemExit) as exit_result:
        runpy.run_path(str(ROOT / "scripts/check_contract_register.py"), run_name="__main__")
    assert exit_result.value.code == 1
    assert capsys.readouterr().err == "broken register\n"
