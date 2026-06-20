from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


deleg = _load("goal_artifact_closeout_delegation")
gal = _load("goal_artifact_lib")


def _apply(text: str) -> dict:
    report = {"ok": True}
    deleg.apply_closeout_delegation(report, text)
    return report


# --- standalone default is untouched (the #318 non-weakening constraint) ---


def test_absent_section_is_standalone_noop() -> None:
    report = _apply("# Goal\n\n## Final Verification\n\nbody\n")
    assert report["ok"] is True
    assert report["closeout_delegation"]["mode"] == "standalone"
    assert report["closeout_delegation"]["declared"] is False
    assert "failures" not in report["closeout_delegation"]


def test_explicit_standalone_is_noop() -> None:
    report = _apply("## Closeout Delegation\n\n- Closeout mode: standalone\n")
    assert report["ok"] is True
    assert "failures" not in report["closeout_delegation"]


# --- orchestrated sub-goal: must name an orchestrator AND list delegated items ---


def test_orchestrated_missing_orchestrator_and_items_blocks() -> None:
    report = _apply("## Closeout Delegation\n\n- Closeout mode: orchestrated\n")
    assert report["ok"] is False
    failures = report["closeout_delegation"]["failures"]
    assert any("Orchestrator goal" in f for f in failures)
    assert any("Delegated proof" in f for f in failures)


def test_orchestrated_placeholder_orchestrator_blocks() -> None:
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrated\n"
        "- Orchestrator goal: <fill me>\n- Delegated proof:\n  - pushed-ci — owner\n"
    )
    report = _apply(text)
    assert report["ok"] is False
    assert any("Orchestrator goal" in f for f in report["closeout_delegation"]["failures"])


def test_orchestrated_complete_passes() -> None:
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrated\n"
        "- Orchestrator goal: charness-artifacts/goals/2026-06-06-orch.md\n"
        "- Closeout state: impl-local / carrier complete\n"
        "- Delegated proof:\n"
        "  - pushed-ci — orchestrator owns the final push + CI watch\n"
        "  - issue-closed — orchestrator verifies #5 CLOSED after push\n"
    )
    report = _apply(text)
    assert report["ok"] is True
    assert report["closeout_delegation"]["delegated_items"] == [
        "pushed-ci — orchestrator owns the final push + CI watch",
        "issue-closed — orchestrator verifies #5 CLOSED after push",
    ]


# --- orchestrator: every delegated checklist item must be resolved ---


def test_orchestrator_unresolved_item_blocks() -> None:
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrator\n"
        "- Delegated proof checklist:\n"
        "  - pushed-ci — verified: CI green on abc123\n"
        "  - live — pending\n"
    )
    report = _apply(text)
    assert report["ok"] is False
    assert report["closeout_delegation"]["unresolved_items"] == ["live — pending"]


def test_orchestrator_all_resolution_forms_pass() -> None:
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrator\n"
        "- Delegated proof checklist:\n"
        "  - pushed-ci — verified: CI green on abc123 (run https://ci/1)\n"
        "  - instance-synced — skipped: instance update deferred to next window — operator directed\n"
        "  - issue-closed — issue #5\n"
        "  - carrier — see #12\n"
    )
    report = _apply(text)
    assert report["ok"] is True
    assert report["closeout_delegation"]["unresolved_items"] == []


def test_orchestrator_empty_checklist_blocks() -> None:
    report = _apply(
        "## Closeout Delegation\n\n- Closeout mode: orchestrator\n- Delegated proof checklist:\n"
    )
    assert report["ok"] is False
    assert any("at least one" in f for f in report["closeout_delegation"]["failures"])


def test_unchecked_box_overrides_resolution_token() -> None:
    # An explicit unchecked box is unresolved even when the line names a token.
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrator\n"
        "- Delegated proof checklist:\n"
        "  - [ ] pushed-ci — verified later\n"
    )
    report = _apply(text)
    assert report["ok"] is False
    assert report["closeout_delegation"]["unresolved_items"] == ["[ ] pushed-ci — verified later"]


def test_unknown_mode_blocks() -> None:
    report = _apply("## Closeout Delegation\n\n- Closeout mode: bogus\n")
    assert report["ok"] is False
    assert any("unknown" in f.lower() for f in report["closeout_delegation"]["failures"])


# --- regression guards for the critique's four blockers ---


def test_blank_orchestrator_field_does_not_borrow_next_line() -> None:
    # B1: a blank `Orchestrator goal:` must not capture the following line as its
    # value; an orchestrated sub-goal with no named orchestrator is blocked.
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrated\n"
        "- Orchestrator goal:\n- Delegated proof:\n  - live — owner\n"
    )
    report = _apply(text)
    assert report["closeout_delegation"]["orchestrator"] == ""
    assert report["ok"] is False
    assert any("Orchestrator goal" in f for f in report["closeout_delegation"]["failures"])


def test_negated_verified_is_unresolved() -> None:
    # B2: a future/negated "verified" must not pass as resolved.
    for phrase in (
        "live — not verified yet",
        "live — to be verified",
        "live — owner not yet verified",
        "live — will be verified next push",
    ):
        text = (
            "## Closeout Delegation\n\n- Closeout mode: orchestrator\n"
            f"- Delegated proof checklist:\n  - {phrase}\n"
        )
        report = _apply(text)
        assert report["ok"] is False, phrase
        assert report["closeout_delegation"]["unresolved_items"] == [phrase]


def test_negation_after_verified_still_resolves() -> None:
    # The negation guard must only fire when negation precedes "verified".
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrator\n"
        "- Delegated proof checklist:\n  - pushed-ci — verified: CI green, not flaky\n"
    )
    report = _apply(text)
    assert report["ok"] is True


def test_blank_line_between_items_does_not_hide_unresolved() -> None:
    # B3: a blank line inside the checklist must not stop parsing and let later
    # unresolved items escape the gate.
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrator\n"
        "- Delegated proof checklist:\n"
        "  - pushed-ci — verified: CI green on abc123\n\n"
        "  - live — pending\n"
        "  - issue-closed — pending\n"
    )
    report = _apply(text)
    assert report["ok"] is False
    assert report["closeout_delegation"]["unresolved_items"] == ["live — pending", "issue-closed — pending"]


def test_standalone_with_trailing_text_is_noop() -> None:
    # B4: a trailing clause after `standalone` must not reclassify the mode and
    # block an otherwise-standalone goal.
    report = _apply("## Closeout Delegation\n\n- Closeout mode: standalone (owns all proof)\n")
    assert report["closeout_delegation"]["mode"] == "standalone"
    assert report["ok"] is True
    assert "failures" not in report["closeout_delegation"]


def test_orchestrator_mode_with_trailing_comment_still_enforced() -> None:
    text = (
        "## Closeout Delegation\n\n- Closeout mode: orchestrator (final boundary)\n"
        "- Delegated proof checklist:\n  - live — pending\n"
    )
    report = _apply(text)
    assert report["closeout_delegation"]["mode"] == "orchestrator"
    assert report["ok"] is False


def test_closeout_state_levels_are_documented_in_lifecycle() -> None:
    # CLOSEOUT_STATE_LEVELS is the single source for the taxonomy; the canonical
    # lifecycle reference must name every level so the docs and the constant can
    # never drift (this is what makes the exported tuple load-bearing).
    lifecycle = (_SCRIPTS.parent / "references" / "lifecycle.md").read_text(encoding="utf-8")
    missing = [level for level in deleg.CLOSEOUT_STATE_LEVELS if level not in lifecycle]
    assert not missing, f"lifecycle.md is missing closeout-state levels: {missing}"


def test_fenced_delegation_section_is_not_parsed() -> None:
    # The goal-artifact docs show the section inside a code fence; a fenced
    # heading must not activate the gate (it parses as undeclared/standalone).
    text = (
        "# doc\n\nExample:\n\n```markdown\n## Closeout Delegation\n\n"
        "- Closeout mode: orchestrator\n- Delegated proof checklist:\n  - live — pending\n```\n"
    )
    report = _apply(text)
    assert report["closeout_delegation"]["declared"] is False
    assert report["ok"] is True


# --- wiring: the gate runs inside check_complete_evidence ---


_GOAL_TAIL = (
    "## Final Verification\n\n"
    "Retro: charness-artifacts/retro/2026-06-06-demo.md\n"
    "Host log probe: skipped: host-log-not-exposed: no codex rollout file in this env\n\n"
)


def test_check_complete_evidence_wires_orchestrator_block(tmp_path: Path) -> None:
    text = (
        "# Achieve Goal: demo\n\nStatus: complete\nCreated: 2026-06-06\n"
        "Activation: `/goal @charness-artifacts/goals/2026-06-06-demo.md`\n\n"
        + _GOAL_TAIL
        + "## Closeout Delegation\n\n- Closeout mode: orchestrator\n"
        "- Delegated proof checklist:\n  - live — pending\n"
    )
    report = gal.check_complete_evidence(tmp_path, text)
    assert report["closeout_delegation"]["mode"] == "orchestrator"
    assert report["closeout_delegation"]["failures"]
    assert report["ok"] is False


def test_check_complete_evidence_standalone_adds_no_delegation_failure(tmp_path: Path) -> None:
    text = (
        "# Achieve Goal: demo\n\nStatus: complete\nCreated: 2026-06-06\n"
        "Activation: `/goal @charness-artifacts/goals/2026-06-06-demo.md`\n\n" + _GOAL_TAIL
    )
    report = gal.check_complete_evidence(tmp_path, text)
    # Other floors may fail, but delegation specifically must not add a failure.
    assert report["closeout_delegation"]["mode"] == "standalone"
    assert "failures" not in report["closeout_delegation"]
