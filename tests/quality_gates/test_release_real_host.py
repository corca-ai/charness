from __future__ import annotations

import json

from .support import ROOT, run_script


def test_release_real_host_proof_triggers_for_support_tool_surfaces() -> None:
    result = run_script(
        "skills/public/release/scripts/check_real_host_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "integrations/tools/cautilus.json",
        "scripts/doctor.py",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["required"] is True
    assert "integrations-and-control-plane" in payload["surface_hits"]
    assert any("cautilus" in item for item in payload["checklist"])
    assert any("install.md" in item for item in payload["checklist"])


def test_release_real_host_proof_stays_off_for_unrelated_paths() -> None:
    result = run_script(
        "skills/public/release/scripts/check_real_host_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/retro-self-improvement-spec.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["required"] is False
    assert payload["checklist"] == []


def test_release_skill_enforces_phase_barriers_for_mutating_commands() -> None:
    skill_text = (ROOT / "skills" / "public" / "release" / "SKILL.md").read_text(encoding="utf-8")

    assert "keep release work phase-ordered: mutate, then sync generated surfaces," in skill_text
    assert "then verify, then push/tag/publish" in skill_text
    assert "public release surface verified" in skill_text
    assert "tag push alone as publish completion" in skill_text
    assert "Do not run sync, export, bump, install/update, or git-mutation commands in" in skill_text
    assert "parallel with validators" in skill_text
