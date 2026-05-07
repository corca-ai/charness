from __future__ import annotations

from .support import ROOT, skill_package_text


def test_spec_skill_surfaces_premortem_and_fresh_eye_review() -> None:
    skill_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    shared_review = (
        ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    ).read_text(encoding="utf-8")

    assert "premortem" in skill_text.lower()
    assert "fresh-eye" in skill_text
    assert "subagent" in skill_text or "subagents" in skill_text
    assert "../../shared/references/fresh-eye-subagent-review.md" in skill_text
    assert "likely implementer misread" in skill_text
    assert "overstated acceptance" in skill_text
    assert "Parent sessions that never spawned a fresh-eye reviewer" in shared_review


def test_spec_skill_distinguishes_public_executable_contract_from_implementation_guard() -> None:
    skill_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    package_text = skill_package_text("spec")
    reference_text = (
        ROOT / "skills" / "public" / "spec" / "references" / "public-executable-contracts.md"
    ).read_text(encoding="utf-8")

    assert "public executable contract" in skill_text
    assert "maintenance lint / implementation guard" in skill_text
    assert "future roadmap" in package_text
    assert "`references/public-executable-contracts.md`" in skill_text
    assert "reader-facing current claims" in reference_text
    assert "implementation-file pinning" in reference_text
    assert "fixed-string source assertions" in reference_text
    assert "viewer over the latest artifact" in reference_text


def test_specdown_on_demand_viewer_keeps_artifact_and_premortem_policy_visible() -> None:
    spec_text = (ROOT / "specs" / "on-demand-validation.spec.md").read_text(encoding="utf-8")

    assert "viewer for the latest checked on-demand validation" in spec_text
    assert "charness-artifacts/cautilus/latest.md" in spec_text
    assert "premortem" in spec_text
    assert "hitl-recommended" in spec_text
