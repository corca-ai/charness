from __future__ import annotations

from pathlib import Path

import yaml

from .seeding_support import write_quality_adapter, write_skill, write_text
from .skill_ergonomics_support import run_inventory_skill_ergonomics as _run


def test_inventory_skill_ergonomics_reports_advisory_flags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    lines = [
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
    write_skill(repo, lines).parent

    result = _run(
        "--repo-root",
        str(repo),
        "--max-core-lines",
        "20",
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
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
    assert set(skill["review_topic_ids"]) >= {
        "helper_owned_workflow_packet",
        "concept_split_references",
    }
    assert any("planner/report packet" in item for item in skill["review_prompts"])
    assert any("split the concepts" in item for item in skill["review_prompts"])


def test_inventory_skill_ergonomics_flags_portable_helper_path_ambiguity(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = write_skill(
        repo,
        [
            "Use `scripts/helper.py` before stopping.",
            "Cross-check `skills/public/other/SKILL.md` if the seam is ambiguous.",
            "",
            "## References",
            "",
            "- `references/note.md`",
            "- `scripts/helper.py`",
        ],
    )
    write_text(skill_dir.parent / "references" / "note.md", "# Note\n")

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert "portable_helper_path_ambiguity" in skill["heuristics"]
    assert any("installed-bundle portability" in item for item in skill["review_prompts"])


def test_inventory_skill_ergonomics_ignores_closeout_vocabulary_mode_terms(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_skill(
        repo,
        [
            "Use this when the repo needs a demo skill.",
            "",
            "## Closeout Vocabulary",
            "",
            "- mode: one of `manual` / `script`.",
            "- option: one of `keep` / `drop`.",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
    )
    write_text(repo / "skills" / "public" / "demo" / "references" / "note.md", "# Note\n")

    result = _run("--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    skill = yaml.safe_load(result.stdout)["skills"][0]
    assert "mode_pressure_terms_present" not in skill["heuristics"]
    assert "option_pressure_terms_present" not in skill["heuristics"]


def test_inventory_skill_ergonomics_does_not_treat_fenced_references_as_a_heading(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_skill(
        repo,
        [
            "Use this when the repo needs a demo skill.",
            "",
            "```markdown",
            "## References",
            "- `references/note.md`",
            "```",
            "",
            "Mode choice matters in this mode-heavy workflow.",
            "Another mode note keeps the mode pressure explicit.",
        ],
    )

    result = _run("--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    skill = yaml.safe_load(result.stdout)["skills"][0]
    assert "mode_pressure_terms_present" in skill["heuristics"]


def test_inventory_skill_ergonomics_ignores_inline_code_for_pressure_terms(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = write_skill(
        repo,
        [
            "Read `gather_provider.<source>.mode` and preserve `Access Mode`.",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
    )
    write_text(skill_dir.parent / "references" / "note.md", "# Note\n")

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert "mode_pressure_terms_present" not in skill["heuristics"]


def test_inventory_skill_ergonomics_flags_issue_and_dated_incident_anchors(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = write_skill(
        repo,
        [
            "Use the 2026-05-28 routing miss as the reason this workflow owns next-step routing.",
            "Keep the guard from #123 in the active workflow.",
            "Inline code like `#456` is inert.",
            "",
            "## References",
            "",
            "- `references/history.md`",
        ],
    ).parent
    history_path = skill_dir / "references" / "history.md"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("# Source History\n\n- #999 belongs here.\n", encoding="utf-8")

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert "issue_anchor_in_core" in skill["heuristics"]
    assert "dated_incident_in_core" in skill["heuristics"]
    assert "portable_package_issue_anchor" in skill["heuristics"]
    assert "portable_package_dated_incident" in skill["heuristics"]
    assert skill["package_issue_anchor_count"] == 3
    assert skill["subcheck_counts"]["package_issue_anchor"] == 3
    assert skill["subcheck_counts"]["package_dated_incident"] == 1
    assert any("issue-number and dated incident anchors" in item for item in skill["review_prompts"])


def test_inventory_skill_ergonomics_reports_package_host_and_reference_subchecks(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_dir = write_skill(
        repo,
        [
            "This assumes Claude Code settings.json behavior instead of an adapter.",
            "",
            "## References",
            "",
            "- `references/visible.md`",
        ],
    ).parent
    references_dir = skill_dir / "references"
    write_text(references_dir / "hidden.md", "# Hidden\n")

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert "portable_package_host_surface_reference" in skill["heuristics"]
    assert "reference_discoverability_gap" in skill["heuristics"]
    assert payload["subcheck_counts"]["host_surface_reference"] == 1
    assert payload["subcheck_counts"]["reference_discoverability"] == 1
    assert skill["host_surface_reference_count"] == 1
    assert skill["unlisted_reference_count"] == 1
    assert skill["unlisted_reference_files"][0]["excerpt"] == "references/hidden.md is not listed in SKILL.md"


def test_inventory_skill_ergonomics_ignores_cache_files_for_reference_discoverability(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    cache_dir = skill_dir / "references" / "__pycache__"
    cache_dir.mkdir(parents=True)
    (cache_dir / "generated.cpython-310.pyc").write_bytes(b"\0\0\0\0")
    write_skill(repo, [], description="Demo.")

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert "reference_discoverability_gap" not in skill["heuristics"]
    assert payload["subcheck_counts"]["reference_discoverability"] == 0
    assert skill["unlisted_reference_count"] == 0


def test_inventory_skill_ergonomics_scans_whole_portable_package_for_issue_anchors(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "support" / "demo"
    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    references_dir.mkdir(parents=True)
    scripts_dir.mkdir()
    write_skill(repo, [], package="support", description="Demo.")
    (references_dir / "history.md").write_text(
        "# History\n\nThis used to cite corca-ai/charness#123.\n",
        encoding="utf-8",
    )
    (scripts_dir / "helper.py").write_text(
        '"""Keep issues/456 visible until migration is cleaned."""\n',
        encoding="utf-8",
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert skill["skill_type"] == "support"
    assert payload["package_issue_anchor_count"] == 2
    assert skill["package_issue_anchor_count"] == 2
    assert "portable_package_issue_anchor" in skill["heuristics"]
    assert {finding["path"] for finding in skill["package_issue_anchor_findings"]} == {
        "skills/support/demo/references/history.md",
        "skills/support/demo/scripts/helper.py",
    }


def test_inventory_skill_ergonomics_allows_version_fields_and_portable_placeholders(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    write_skill(repo, [], description="Demo.")
    (skill_dir / "adapter.example.yaml").write_text(
        "defaults_version: issue-64\nrecommendation_defaults_version: issue-65\n",
        encoding="utf-8",
    )
    (scripts_dir / "helper.py").write_text(
        '"""`gh issue create` prints ``.../issues/123`` as a portable placeholder."""\n',
        encoding="utf-8",
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert skill["package_issue_anchor_count"] == 0
    assert "portable_package_issue_anchor" not in skill["heuristics"]


def test_inventory_skill_ergonomics_allows_short_number_labels_but_flags_explicit_issue_refs(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    write_skill(
        repo,
        ["Use option #1 before attempt #2 when ordering local choices."],
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert "issue_anchor_in_core" not in payload["skills"][0]["heuristics"]

    write_skill(
        repo,
        ["Carry forward issue #7 as the reason this workflow owns the guard."],
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert "issue_anchor_in_core" in payload["skills"][0]["heuristics"]
    assert "portable_package_issue_anchor" in payload["skills"][0]["heuristics"]


def test_inventory_skill_ergonomics_uses_adapter_skill_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_root = repo / "packages" / "official-skills" / "acme-native" / "skills"
    skill_dir = skill_root / "anniversary-roster-sync"
    skill_dir.mkdir(parents=True)
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_skill_paths:",
            "  - packages/official-skills/acme-native/skills",
        ],
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

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [skill["skill_path"] for skill in payload["skills"]] == [
        "packages/official-skills/acme-native/skills/anniversary-roster-sync/SKILL.md"
    ]


def test_inventory_skill_ergonomics_reports_unconfigured_when_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "unconfigured"
    assert payload["scope_status"] == "unconfigured_no_skill_surface"
    assert payload["finding_status"] == "not_evaluated"
    assert payload["checked_skill_count"] == 0
    assert "skill_ergonomics_skill_paths" in payload["reason"]
    assert payload["skills"] == []


def test_inventory_skill_ergonomics_reports_clean_when_skills_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_skill(repo, [], description="Demo.")
    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "clean"
    assert payload["scope_status"] == "scanned"
    assert payload["finding_status"] == "zero_heuristic_findings"
    assert payload["prose_review_status"] == "still_required"
    assert payload["checked_skill_count"] == 1
    assert payload["heuristic_finding_count"] == 0
    assert [item["advisory_id"] for item in payload["advisories"]] == [
        "skill_ergonomics_prose_review_still_required"
    ]
    assert payload["skills"] and payload["skills"][0]["skill_id"] == "demo"

    plain = _run(
        "--repo-root",
        str(repo),
    )
    assert plain.returncode == 0, plain.stderr
    assert "ADVISORY: No heuristic findings were found" in plain.stdout


def test_inventory_skill_ergonomics_reports_configured_scope_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_skill(repo, [], skill_id="fallback", description="Fallback.", title="Fallback")
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_skill_paths:",
            "  - missing-skills",
        ],
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "unconfigured"
    assert payload["scope_status"] == "configured_scope_empty"
    assert payload["finding_status"] == "not_evaluated"
    assert payload["checked_skill_count"] == 0
    assert payload["skills"] == []


def test_inventory_skill_ergonomics_reports_requested_scope_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = _run(
        "--repo-root",
        str(repo),
        "--skill-path",
        "missing-skill",
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "clean"
    assert payload["scope_status"] == "empty_requested_scope"
    assert payload["finding_status"] == "not_evaluated"
    assert payload["checked_skill_count"] == 0
    assert payload["skills"] == []


def test_inventory_skill_ergonomics_marks_heuristic_findings_and_prose_review(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_skill(repo, ["Mode mode option option."], description="Demo.")

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["scope_status"] == "scanned"
    assert payload["finding_status"] == "heuristics_present"
    assert payload["prose_review_status"] == "required"
    assert payload["heuristic_finding_count"] == 2
    assert [item["advisory_id"] for item in payload["advisories"]] == [
        "skill_ergonomics_prose_review_required"
    ]

    plain = _run(
        "--repo-root",
        str(repo),
    )
    assert plain.returncode == 0, plain.stderr
    assert "ADVISORY: Heuristic findings are present" in plain.stdout


def test_inventory_skill_ergonomics_surfaces_invalid_adapter_as_best_effort(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_gate_rules:",
            "  - typo_rule",
        ],
    )
    write_skill(repo, [], description="Demo.")

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
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
    write_quality_adapter(
        repo,
        [
            "skill_ergonomics_skill_paths:",
            "  - skills/public",
            "  - packages/official-skills/charness-public/skills",
            "vendored_paths:",
            "  - packages/official-skills/charness-public",
        ],
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    paths = [skill["skill_path"] for skill in payload["skills"]]
    assert paths == ["skills/public/demo/SKILL.md"]


def test_inventory_skill_ergonomics_runtime_install_accepts_skill_md_suffix(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "packages" / "official-skills" / "acme-native" / "skills" / "demo"
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
                "  - packages/official-skills/acme-native/skills",
                "skill_ergonomics_runtime_install_skill_paths:",
                "  - packages/official-skills/acme-native/skills/demo/SKILL.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert skill["skill_type"] == "runtime_install"
    assert "portable_helper_path_ambiguity" not in skill["heuristics"]


def test_inventory_skill_ergonomics_runtime_install_skips_portable_helper_heuristic(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "packages" / "official-skills" / "acme-native" / "skills" / "demo"
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
                "Historical note corca-ai/charness#123 stays out of portable package metrics here.",
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
                "  - packages/official-skills/acme-native/skills",
                "skill_ergonomics_runtime_install_skill_paths:",
                "  - packages/official-skills/acme-native/skills",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _run(
        "--repo-root",
        str(repo),
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skill = payload["skills"][0]
    assert skill["skill_type"] == "runtime_install"
    assert skill["package_issue_anchor_count"] == 0
    assert "portable_helper_path_ambiguity" not in skill["heuristics"]
    assert "portable_package_issue_anchor" not in skill["heuristics"]
    assert any("runtime-install portability" in prompt for prompt in skill["review_prompts"])
    assert not any("installed-bundle portability" in prompt for prompt in skill["review_prompts"])
