from __future__ import annotations

import json
from pathlib import Path

from tests.quality_gates.support import ROOT, run_script

SCRIPT = "scripts/check_skill_ownership_overlap.py"


def test_current_repo_passes_with_seeded_allowlist() -> None:
    result = run_script(SCRIPT, "--repo-root", str(ROOT), "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"] == []
    assert payload["scanned_skills"] >= 1
    assert payload["allowlist_size"] >= 1


def test_unallowlisted_cross_namespace_artifact_write_fails(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills" / "public"
    rogue = skills_dir / "rogue"
    rogue.mkdir(parents=True)
    (rogue / "SKILL.md").write_text(
        "---\nname: rogue\ndescription: \"rogue\"\n---\n\n"
        "# Rogue\n\nWrites into `<repo-root>/charness-artifacts/quality/latest.md`.\n",
        encoding="utf-8",
    )
    other = skills_dir / "neighbor"
    other.mkdir()
    (other / "SKILL.md").write_text(
        "---\nname: neighbor\ndescription: \"n\"\n---\n\n# Neighbor\n\nstays in own namespace.\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir()

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--json")

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    findings = payload["findings"]
    assert len(findings) == 1
    finding = findings[0]
    assert finding["skill"] == "rogue"
    assert finding["kind"] == "artifact"
    assert finding["owner"] == "quality"
    assert finding["allowlist_entry"] == "rogue:artifact:quality:<reason>"


def test_allowlist_entry_silences_finding(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills" / "public"
    skill = skills_dir / "demo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "# Demo\n\nReads from `<repo-root>/charness-artifacts/release/latest.md`.\n",
        encoding="utf-8",
    )
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "check_skill_ownership_overlap.allowlist.txt").write_text(
        "demo:artifact:release:read-only cite\n", encoding="utf-8"
    )

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"] == []
    assert payload["allowlist_size"] == 1


def test_unallowlisted_adapter_namespace_mention_fails(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills" / "public"
    skill = skills_dir / "stub"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "# Stub\n\nReads `<repo-root>/.agents/quality-adapter.yaml`.\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir()

    result = run_script(SCRIPT, "--repo-root", str(tmp_path), "--json")

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    finding = payload["findings"][0]
    assert finding["kind"] == "adapter"
    assert finding["owner"] == "quality"
