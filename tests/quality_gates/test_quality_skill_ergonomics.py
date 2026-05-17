from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_skill_ergonomics_reports_advisory_flags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
        "",
        "Use this when the repo needs a demo skill.",
        "",
        "Mode choice matters in this mode-heavy workflow.",
        "Another mode note keeps the mode pressure explicit.",
        "This option should probably be inference instead of an option.",
        "A second option mention keeps option pressure visible.",
        "",
        "## Bootstrap",
        "",
        "```bash",
        "echo first",
        "```",
        "",
        "```bash",
        "echo second",
        "```",
        "",
        "```bash",
        "echo third",
        "```",
        "",
    ]
    lines.extend(f"- filler line {index}" for index in range(90))
    (skill_dir / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--max-core-lines",
        "20",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    skill = payload["skills"][0]
    assert skill["skill_id"] == "demo"
    assert skill["skill_type"] == "public"
    assert skill["skill_path"] == "skills/public/demo/SKILL.md"
    assert set(skill["heuristics"]) == {
        "long_core",
        "progressive_disclosure_risk",
        "mode_pressure_terms_present",
        "option_pressure_terms_present",
        "code_fence_without_helper_script",
    }
    assert skill["bootstrap_fence_count"] == 3
    assert skill["review_prompts"]


def test_inventory_skill_ergonomics_flags_portable_helper_path_ambiguity(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo" / "references"
    skill_dir.mkdir(parents=True)
    (skill_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "Use `scripts/helper.py` before stopping.",
                "Cross-check `skills/public/other/SKILL.md` if the seam is ambiguous.",
                "",
                "## References",
                "",
                "- `references/note.md`",
                "- `scripts/helper.py`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    skill = payload["skills"][0]
    assert "portable_helper_path_ambiguity" in skill["heuristics"]
    assert any("installed-bundle portability" in item for item in skill["review_prompts"])


def test_inventory_skill_ergonomics_ignores_inline_code_for_pressure_terms(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo" / "references"
    skill_dir.mkdir(parents=True)
    (skill_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "Read `gather_provider.<source>.mode` and preserve `Access Mode`.",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    skill = payload["skills"][0]
    assert "mode_pressure_terms_present" not in skill["heuristics"]


def test_inventory_skill_ergonomics_uses_adapter_skill_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_root = repo / "packages" / "official-skills" / "ceal-native" / "skills"
    skill_dir = skill_root / "anniversary-roster-sync"
    skill_dir.mkdir(parents=True)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - packages/official-skills/ceal-native/skills",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: anniversary-roster-sync",
                'description: "Demo native skill."',
                "---",
                "",
                "# Anniversary Roster Sync",
                "",
                "Use this when the native roster needs sync review.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [skill["skill_path"] for skill in payload["skills"]] == [
        "packages/official-skills/ceal-native/skills/anniversary-roster-sync/SKILL.md"
    ]


def test_inventory_skill_ergonomics_reports_unconfigured_when_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "unconfigured"
    assert payload["scope_status"] == "unconfigured_no_skill_surface"
    assert payload["finding_status"] == "not_evaluated"
    assert payload["checked_skill_count"] == 0
    assert "skill_ergonomics_skill_paths" in payload["reason"]
    assert payload["skills"] == []


def test_inventory_skill_ergonomics_reports_clean_when_skills_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"Demo.\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "clean"
    assert payload["scope_status"] == "scanned"
    assert payload["finding_status"] == "zero_heuristic_findings"
    assert payload["prose_review_status"] == "still_required"
    assert payload["checked_skill_count"] == 1
    assert payload["heuristic_finding_count"] == 0
    assert payload["skills"] and payload["skills"][0]["skill_id"] == "demo"


def test_inventory_skill_ergonomics_reports_configured_scope_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fallback_skill = repo / "skills" / "public" / "fallback"
    fallback_skill.mkdir(parents=True)
    (fallback_skill / "SKILL.md").write_text(
        "---\nname: fallback\ndescription: \"Fallback.\"\n---\n\n# Fallback\n",
        encoding="utf-8",
    )
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - missing-skills",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "unconfigured"
    assert payload["scope_status"] == "configured_scope_empty"
    assert payload["finding_status"] == "not_evaluated"
    assert payload["checked_skill_count"] == 0
    assert payload["skills"] == []


def test_inventory_skill_ergonomics_marks_heuristic_findings_and_prose_review(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"Demo.\"\n---\n\n# Demo\n\nMode mode option option.\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["scope_status"] == "scanned"
    assert payload["finding_status"] == "heuristics_present"
    assert payload["prose_review_status"] == "required"
    assert payload["heuristic_finding_count"] == 2


def test_inventory_skill_ergonomics_surfaces_invalid_adapter_as_best_effort(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - typo_rule",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"Demo.\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["adapter_load_mode"] == "permissive"
    assert payload["adapter_valid"] is False
    assert "unknown rule `typo_rule`" in payload["adapter_errors"][0]
    assert any("best-effort" in warning for warning in payload["adapter_warnings"])
    assert payload["finding_status"] == "zero_heuristic_findings"


def test_inventory_skill_ergonomics_skips_vendored_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    own_skill = repo / "skills" / "public" / "demo"
    vendored_skill = repo / "packages" / "official-skills" / "charness-public" / "skills" / "vendored"
    own_skill.mkdir(parents=True)
    vendored_skill.mkdir(parents=True)
    body = "---\nname: x\ndescription: \"x.\"\n---\n\n# X\n"
    (own_skill / "SKILL.md").write_text(body, encoding="utf-8")
    (vendored_skill / "SKILL.md").write_text(body, encoding="utf-8")
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - skills/public",
                "  - packages/official-skills/charness-public/skills",
                "vendored_paths:",
                "  - packages/official-skills/charness-public",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    paths = [skill["skill_path"] for skill in payload["skills"]]
    assert paths == ["skills/public/demo/SKILL.md"]


def test_inventory_skill_ergonomics_runtime_install_accepts_skill_md_suffix(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "packages" / "official-skills" / "ceal-native" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Runtime-installed demo."',
                "---",
                "",
                "# Demo",
                "",
                "Use `scripts/process_receipt.py` before stopping.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - packages/official-skills/ceal-native/skills",
                "skill_ergonomics_runtime_install_skill_paths:",
                "  - packages/official-skills/ceal-native/skills/demo/SKILL.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    skill = payload["skills"][0]
    assert skill["skill_type"] == "runtime_install"
    assert "portable_helper_path_ambiguity" not in skill["heuristics"]


def test_inventory_skill_ergonomics_runtime_install_skips_portable_helper_heuristic(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "packages" / "official-skills" / "ceal-native" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Runtime-installed demo."',
                "---",
                "",
                "# Demo",
                "",
                "Use `scripts/process_receipt.py` before stopping.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - packages/official-skills/ceal-native/skills",
                "skill_ergonomics_runtime_install_skill_paths:",
                "  - packages/official-skills/ceal-native/skills",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    skill = payload["skills"][0]
    assert skill["skill_type"] == "runtime_install"
    assert "portable_helper_path_ambiguity" not in skill["heuristics"]
    assert any("runtime-install portability" in prompt for prompt in skill["review_prompts"])
    assert not any("installed-bundle portability" in prompt for prompt in skill["review_prompts"])
