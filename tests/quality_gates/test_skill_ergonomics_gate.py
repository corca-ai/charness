from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/validate_skill_ergonomics.py"


def _seed_repo(tmp_path: Path, *, rules: list[str]) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "skills" / "public" / "demo" / "references").mkdir(parents=True)
    (repo / "skills" / "public" / "steady" / "references").mkdir(parents=True)
    adapter_lines = [
        "version: 1",
        "repo: testrepo",
        "output_dir: charness-artifacts/quality",
    ]
    if rules:
        adapter_lines.append("skill_ergonomics_gate_rules:")
        for rule in rules:
            adapter_lines.append(f"  - {rule}")
    else:
        adapter_lines.append("skill_ergonomics_gate_rules: []")
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / "skills" / "public" / "steady" / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
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
                "Mode choice matters in this mode-heavy workflow.",
                "Another mode note keeps the mode pressure explicit.",
                "This option should probably be inference instead of an option.",
                "A second option mention keeps option pressure visible.",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "skills" / "public" / "steady" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: steady",
                'description: "Steady skill."',
                "---",
                "",
                "# Steady",
                "",
                "Use this when the repo needs a stable skill.",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def test_skill_ergonomics_gate_no_rules_passes(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=[])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["rules"] == []
    assert payload["violations"] == []
    assert payload["discovery_errors"] == []
    assert payload["warnings"][0]["warning_id"] == "skill_ergonomics_gate_rules_empty"
    assert payload["warnings"][0]["skill_count"] == 2

    plain = run_script(SCRIPT, "--repo-root", str(repo))
    assert plain.returncode == 0, plain.stderr
    assert "WARNING: skill_ergonomics_gate_rules is empty" in plain.stdout


def test_skill_ergonomics_gate_warns_when_empty_rules_have_broken_explicit_paths(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=[])
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - missing-skills",
                "skill_ergonomics_gate_rules: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["warnings"][0]["warning_id"] == "skill_ergonomics_requested_paths_empty"
    assert payload["warnings"][0]["requested_paths"] == ["missing-skills"]

    plain = run_script(SCRIPT, "--repo-root", str(repo))
    assert plain.returncode == 0, plain.stderr
    assert "WARNING: skill_ergonomics_skill_paths is configured but resolved no non-vendored skills" in plain.stdout


def test_skill_ergonomics_gate_fails_when_opted_in_rule_matches(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=["mode_option_pressure_terms"])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["rules"] == ["mode_option_pressure_terms"]
    assert payload["violations"][0]["rule"] == "mode_option_pressure_terms"
    assert payload["violations"][0]["skill_id"] == "demo"
    plain = run_script(SCRIPT, "--repo-root", str(repo))
    assert plain.returncode == 1
    assert "mode_option_pressure_terms" in plain.stdout
    assert "skills/public/demo/SKILL.md" in plain.stdout


def test_skill_ergonomics_gate_fails_on_issue_and_dated_incident_rules(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - issue_anchor_in_core",
                "  - dated_incident_in_core",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "The 2026-05-28 routing miss is the reason this workflow owns next-step routing.",
                "Preserve the active guard from #123.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert [violation["rule"] for violation in payload["violations"]] == [
        "issue_anchor_in_core",
        "dated_incident_in_core",
    ]
    assert all(violation["skill_id"] == "demo" for violation in payload["violations"])


def test_skill_ergonomics_gate_fails_on_package_issue_anchor_rule_for_support_skill(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "support" / "demo" / "references"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - portable_package_issue_anchor",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "skills" / "support" / "demo" / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"Demo.\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (skill_dir / "history.md").write_text(
        "# History\n\nThis support package still names corca-ai/charness#123.\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violations"][0]["rule"] == "portable_package_issue_anchor"
    assert payload["violations"][0]["skill_id"] == "demo"
    assert payload["checked_skills"][0]["package_issue_anchor_count"] == 1


def test_skill_ergonomics_gate_fails_on_package_text_quality_rules(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - portable_package_dated_incident",
                "  - portable_package_host_surface_reference",
                "  - reference_discoverability_gap",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (references_dir / "hidden.md").write_text(
        "# Hidden\n\nA 2026-05-28 incident note belongs outside portable prose.\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"Demo.\"\n---\n\n# Demo\n\nCodex settings.json owns this host behavior.\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert [violation["rule"] for violation in payload["violations"]] == [
        "portable_package_dated_incident",
        "portable_package_host_surface_reference",
        "reference_discoverability_gap",
    ]
    assert all(violation["findings"] for violation in payload["violations"])


def test_skill_ergonomics_gate_keeps_existing_rules_public_only_for_support_skills(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "support" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "Mode choice matters in this mode-heavy workflow.",
                "Another mode note keeps the mode pressure explicit.",
                "This option should probably be inference instead of an option.",
                "A second option mention keeps option pressure visible.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["checked_skills"][0]["skill_type"] == "support"
    assert payload["violations"] == []


def test_skill_ergonomics_gate_fails_on_invalid_rule_adapter_error(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=["typo_rule"])

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["adapter_errors"]
    assert "unknown rule `typo_rule`" in payload["adapter_errors"][0]
    assert payload["discovery_skipped_reason"] == "adapter_invalid"
    assert payload["checked_skills"] == []
    assert payload["violations"] == []

    plain = run_script(SCRIPT, "--repo-root", str(repo))
    assert plain.returncode == 1
    assert "quality adapter: skill_ergonomics_gate_rules contains unknown rule `typo_rule`" in plain.stdout

    wrapper = run_script("scripts/validate_skill_ergonomics.py", "--repo-root", str(repo), "--json")
    assert wrapper.returncode == 1
    wrapper_payload = json.loads(wrapper.stdout)
    assert "unknown rule `typo_rule`" in wrapper_payload["adapter_errors"][0]


def test_skill_ergonomics_gate_ignores_mode_option_terms_inside_fences(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "## Bootstrap",
                "",
                "```bash",
                "echo mode option mode option",
                "```",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []


def test_skill_ergonomics_gate_fails_when_rules_check_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "no skills were checked" in payload["discovery_errors"][0]["message"]

    wrapper = run_script("scripts/validate_skill_ergonomics.py", "--repo-root", str(repo), "--json")
    assert wrapper.returncode == 1


def test_skill_ergonomics_gate_discovers_direct_skill_layout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "cautilus"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\nname: cautilus\n---\n\n# Cautilus\n\nA compact skill body.\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["checked_skills"][0]["skill_path"] == "skills/cautilus/SKILL.md"
    assert payload["discovery_errors"] == []


def test_skill_ergonomics_gate_skips_runtime_install_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "packages" / "official-skills" / "ceal-native" / "skills" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_skill_paths:",
                "  - packages/official-skills/ceal-native/skills",
                "skill_ergonomics_runtime_install_skill_paths:",
                "  - packages/official-skills/ceal-native/skills",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Runtime-install demo."',
                "---",
                "",
                "# Demo",
                "",
                "Mode choice matters in this mode-heavy workflow.",
                "Another mode note keeps the mode pressure explicit.",
                "This option should probably be inference instead of an option.",
                "A second option mention keeps option pressure visible.",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []
    assert payload["checked_skills"][0]["skill_type"] == "runtime_install"


def test_skill_ergonomics_gate_skips_vendored_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    own = repo / "skills" / "public" / "demo"
    vendored = repo / "packages" / "official-skills" / "charness-public" / "skills" / "vendored"
    own.mkdir(parents=True)
    vendored.mkdir(parents=True)
    (own / "references").mkdir()
    (own / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "vendored_paths:",
                "  - packages/official-skills/charness-public",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    body_lines = [
        "---",
        "name: bad",
        'description: "Vendored bad skill."',
        "---",
        "",
        "# Bad",
        "",
        "Mode choice matters in this mode-heavy workflow.",
        "Another mode note keeps the mode pressure explicit.",
        "This option should probably be inference instead of an option.",
        "A second option mention keeps option pressure visible.",
    ]
    (vendored / "SKILL.md").write_text("\n".join(body_lines) + "\n", encoding="utf-8")
    (own / "SKILL.md").write_text(
        "---\nname: demo\ndescription: \"clean.\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []
    paths = [skill["skill_path"] for skill in payload["checked_skills"]]
    assert paths == ["skills/public/demo/SKILL.md"]


def test_skill_ergonomics_gate_fails_when_opted_in_progressive_disclosure_risk_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - progressive_disclosure_risk",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    filler = [f"filler line {index}" for index in range(90)]
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                *filler,
                "",
                "## References",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["rules"] == ["progressive_disclosure_risk"]
    assert payload["violations"][0]["rule"] == "progressive_disclosure_risk"


def test_skill_ergonomics_gate_fails_when_opted_in_long_core_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo" / "references"
    skill_dir.mkdir(parents=True)
    (skill_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - long_core",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    filler = [f"filler line {index}" for index in range(170)]
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
                *filler,
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violations"][0]["rule"] == "long_core"


def test_skill_ergonomics_gate_fails_when_opted_in_code_fence_rule_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - code_fence_without_helper_script",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
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
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violations"][0]["rule"] == "code_fence_without_helper_script"


def test_skill_ergonomics_gate_fails_when_opted_in_portable_helper_rule_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo" / "references"
    skill_dir.mkdir(parents=True)
    (skill_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - portable_helper_path_ambiguity",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
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
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violations"][0]["rule"] == "portable_helper_path_ambiguity"
