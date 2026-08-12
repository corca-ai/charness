from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import contract_register_lib as register
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


def _ledger(repo: Path) -> None:
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    payload = {
        "kind": "charness.lesson-ledger",
        "schema_version": 2,
        "transitions": [
            {
                "sequence": 1,
                "transition_id": "seed-a",
                "lesson_id": "a",
                "source_retro": "charness-artifacts/retro/source.md",
            }
        ],
        "score_events": [],
        "lessons": {
            "a": {
                "source_retro": "charness-artifacts/retro/source.md",
                "transition_id": "seed-a",
                "score_total": 0,
                "score_count": 0,
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
    assert capsys.readouterr().out == "Validated contract register: 4 units, 0 citations, 0 proposals.\n"


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
        "citation_event_count": 0,
        "graduation_proposal_count": 0,
        "path": "charness-artifacts/retro/contract-register.json",
    }


def test_register_requires_displacement_for_a_budgeted_graduation_proposal(tmp_path: Path) -> None:
    path = _prepare(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    proposal = {
        "proposal_id": "proposal-1",
        "lesson_id": "a",
        "source_retro": "charness-artifacts/retro/source.md",
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
    with pytest.raises(ValueError, match="duplicate proposed unit ID"):
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
    with pytest.raises(ValueError, match="fixed initial budget"):
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
    with pytest.raises(ValueError, match="committed active units"):
        _validate(tmp_path)


def test_register_refuses_a_committed_nonempty_catch_stream(tmp_path: Path, monkeypatch) -> None:
    path = _prepare(tmp_path)
    committed = json.loads(path.read_text(encoding="utf-8"))
    committed["catch_events"] = [{"event_id": "handwritten-catch"}]
    monkeypatch.setattr(register, "_committed_state", lambda *_args: committed)
    with pytest.raises(ValueError, match="unsupported non-empty catch"):
        _validate(tmp_path)
