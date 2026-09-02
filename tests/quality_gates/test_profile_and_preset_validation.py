from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import validate_presets as VALIDATE_PRESETS
from scripts.gates import validate_adapters as VALIDATE_ADAPTERS
from tests.quality_gates.repo_shapes import install_committed_repo
from tools import validate_profiles as VALIDATE_PROFILES

from .support import run_script


def test_validate_profiles_rejects_missing_skill_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    profiles_dir.mkdir(parents=True)
    (profiles_dir / "constitutional.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "constitutional",
                "display_name": "Constitutional",
                "purpose": "Test",
                "bundles": {"public_skills": ["impl"]},
            }
        ),
        encoding="utf-8",
    )
    try:
        VALIDATE_PROFILES.validate_profile(profiles_dir / "constitutional.json", repo)
    except VALIDATE_PROFILES.ValidationError as exc:
        assert "missing artifact `impl`" in str(exc)
    else:
        raise AssertionError("validate_profile did not reject missing skill reference")


def test_validate_presets_rejects_organization_scope_without_product_slice(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    presets_dir = repo / "presets"
    presets_dir.mkdir(parents=True)
    (presets_dir / "bad-preset.md").write_text(
        "\n".join(
            [
                "---",
                "name: bad-preset",
                'description: "Bad preset."',
                "preset_kind: sample-vocabulary",
                "install_scope: organization",
                "---",
                "",
                "# bad-preset",
                "",
                "## Intended Use",
                "",
                "Broken example.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    try:
        VALIDATE_PRESETS.validate_preset(presets_dir / "bad-preset.md")
    except VALIDATE_PRESETS.ValidationError as exc:
        assert "organization-scope presets must use `preset_kind: product-slice`" in str(exc)
    else:
        raise AssertionError("validate_preset did not reject organization-scope sample preset")


def test_validate_presets_rejects_product_slice_without_exposure_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    presets_dir = repo / "presets"
    presets_dir.mkdir(parents=True)
    (presets_dir / "org-slice.md").write_text(
        "\n".join(
            [
                "---",
                "name: org-slice",
                'description: "Org slice."',
                "preset_kind: product-slice",
                "install_scope: organization",
                "---",
                "",
                "# org-slice",
                "",
                "## Intended Use",
                "",
                "Missing exposure contract.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    try:
        VALIDATE_PRESETS.validate_preset(presets_dir / "org-slice.md")
    except VALIDATE_PRESETS.ValidationError as exc:
        assert "product-slice presets must include an `## Exposure Contract` section" in str(exc)
    else:
        raise AssertionError(
            "validate_preset did not reject product slice without exposure contract"
        )


def test_validate_presets_accepts_nested_reconciliation_contract(tmp_path: Path) -> None:
    preset = tmp_path / "strict.md"
    preset.write_text(
        '---\nname: strict\ndescription: "Strict."\npreset_kind: sample-vocabulary\ninstall_scope: maintainer\n'
        "reconciliation:\n  required_adapter_commands:\n    - python3 -m pytest\n---\n# strict\n\n## Intended Use\n\nTest.\n",
        encoding="utf-8",
    )

    VALIDATE_PRESETS.validate_preset(preset)


def test_validate_presets_refuses_invalid_reconciliation_frontmatter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    preset = tmp_path / "invalid.md"
    preset.write_text("---\nname: invalid\n---\n# invalid\n", encoding="utf-8")
    from scripts import adapter_lib

    def invalid_yaml(_text: str) -> object:
        raise ValueError("bad YAML")

    monkeypatch.setattr(adapter_lib, "load_yaml", invalid_yaml)
    with pytest.raises(VALIDATE_PRESETS.ValidationError, match="invalid YAML frontmatter"):
        VALIDATE_PRESETS.parse_frontmatter_data(preset)

    monkeypatch.setattr(adapter_lib, "load_yaml", lambda _text: [])
    with pytest.raises(VALIDATE_PRESETS.ValidationError, match="frontmatter must be a mapping"):
        VALIDATE_PRESETS.parse_frontmatter_data(preset)

    with pytest.raises(VALIDATE_PRESETS.ValidationError, match="non-empty string list"):
        VALIDATE_PRESETS.validate_reconciliation_frontmatter(
            {"reconciliation": {"required_adapter_commands": []}}
        )


def test_validate_presets_ignores_gitignored_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "presets/generated-*.md\n",
            "presets/kept.md": "\n".join(
                [
                    "---",
                    "name: kept",
                    'description: "Kept preset."',
                    "preset_kind: portable-defaults",
                    "install_scope: maintainer",
                    "---",
                    "",
                    "# kept",
                    "",
                    "## Intended Use",
                    "",
                    "Valid tracked preset.",
                    "",
                ]
            )
            + "\n",
        },
    )
    (repo / "presets" / "generated-bad.md").write_text(
        "# Missing frontmatter on ignored file.\n", encoding="utf-8"
    )

    result = run_script("scripts/validate_presets.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_sample_quality_presets_carry_concrete_lint_defaults() -> None:
    root = Path(__file__).resolve().parents[2]
    python_quality = (root / "presets" / "python-quality.md").read_text(encoding="utf-8")
    typescript_quality = (root / "presets" / "typescript-quality.md").read_text(encoding="utf-8")
    presets_readme = (root / "presets" / "README.md").read_text(encoding="utf-8")

    assert "`ruff check` with `E`, `F`, `I`, and `C90`" in python_quality
    assert "[tool.ruff.lint.mccabe] max-complexity = 15" in python_quality
    assert "`eslint` with a standing `complexity` rule" in typescript_quality
    assert 'complexity: ["error", 15]' in typescript_quality
    assert "including `eslint` + `complexity` and `tsc --noEmit` defaults" in presets_readme
    assert "including `ruff` + `C90` and one type-checker default" in presets_readme


def test_validate_adapters_rejects_charness_quality_coverage_floor_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: charness",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "coverage_floor_policy:",
                "  min_statements_threshold: 30",
                "  fail_below_pct: 80.0",
                "  warn_ceiling_pct: 95.0",
                "  floor_drift_lock_pp: 1.0",
                "  exemption_list_path: scripts/coverage-floor-exemptions.txt",
                '  gate_script_pattern: "*-quality-gate.sh"',
                "  lefthook_path: lefthook.yml",
                "  ci_workflow_glob: .github/workflows/*.yml",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- ./charness --help",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "cli_skill_surface_change_globs:",
                "- charness",
                "canonical_markdown_surfaces:",
                "- AGENTS.md",
                "- CLAUDE.md",
                "- docs/index.md",
                "runtime_profile_default: default",
                "runtime_budget_profiles:",
                "  local-linux-aarch64-4cpu:",
                "    budgets:",
                "      pytest: 70000",
                "startup_probes:",
                "- label: demo",
                "  command:",
                "  - python3",
                "  - -V",
                "  class: standing",
                "  startup_mode: warm",
                "  surface: direct",
                "preflight_commands:",
                "- python3 scripts/setup/validate_maintainer_setup.py --repo-root .",
                "gate_commands:",
                "- ./scripts/run-quality.sh",
                "review_commands:",
                "- ./scripts/run-quality.sh --review",
                "security_commands:",
                "- ./scripts/check-secrets.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert (
        "coverage_floor_policy.fail_below_pct must match check_coverage.py (85.0)" in result.stderr
    )


def test_validate_profiles_rejects_unknown_smoke_scenario(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "impl"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        '---\nname: impl\ndescription: "demo"\n---\n\n# Impl\n',
        encoding="utf-8",
    )
    (profiles_dir / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "demo",
                "display_name": "Demo",
                "purpose": "Test",
                "bundles": {"public_skills": ["impl"]},
                "validation": {"smoke_scenarios": ["not-a-real-scenario"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("tools/validate_profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "unknown eval scenario `not-a-real-scenario`" in result.stderr


def test_validate_profiles_rejects_missing_extends_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "impl"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        '---\nname: impl\ndescription: "demo"\n---\n\n# Impl\n',
        encoding="utf-8",
    )
    (profiles_dir / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "demo",
                "display_name": "Demo",
                "purpose": "Test",
                "extends": ["missing-base"],
                "bundles": {"public_skills": ["impl"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("tools/validate_profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "extends[]` references missing artifact `missing-base`" in result.stderr


def test_validate_profiles_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "impl"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        '---\nname: impl\ndescription: "demo"\n---\n\n# Impl\n\n## References\n\n- `references/demo.md`\n',
        encoding="utf-8",
    )
    (public_skill_dir / "references").mkdir(parents=True)
    (public_skill_dir / "references" / "demo.md").write_text("# Demo\n", encoding="utf-8")
    (profiles_dir / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "demo",
                "display_name": "Demo",
                "purpose": "Test",
                "bundles": {"public_skills": ["impl"]},
                "unexpected": True,
            }
        ),
        encoding="utf-8",
    )
    result = run_script("tools/validate_profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


def test_validate_profiles_ignores_gitignored_profiles(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "profiles/generated-*.json\n",
            "skills/public/impl/SKILL.md": (
                '---\nname: impl\ndescription: "demo"\n---\n\n# Impl\n\n## References\n\n'
                "- `references/demo.md`\n"
            ),
            "skills/public/impl/references/demo.md": "# Demo\n",
            "profiles/kept.json": json.dumps(
                {
                    "schema_version": "1",
                    "profile_id": "kept",
                    "display_name": "Kept",
                    "purpose": "Test",
                    "bundles": {"public_skills": ["impl"]},
                }
            )
            + "\n",
        },
    )
    (repo / "profiles" / "generated-bad.json").write_text(
        '{"profile_id":"generated-bad"}\n', encoding="utf-8"
    )

    result = run_script("tools/validate_profiles.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_adapters_ignores_gitignored_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "skills/public/generated/\n",
            "skills/public/kept/scripts/resolve_adapter.py": "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import json",
                    'print(json.dumps({"valid": True, "artifact_filename": "latest.md", "artifact_path": "charness-artifacts/kept/latest.md"}))',
                    "",
                ]
            )
            + "\n",
        },
    )
    ignored = repo / "skills" / "public" / "generated" / "scripts" / "resolve_adapter.py"
    ignored.parent.mkdir(parents=True)
    ignored.write_text("#!/usr/bin/env python3\nraise SystemExit(1)\n", encoding="utf-8")

    result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_adapters_rejects_charness_quality_adapter_with_missing_mature_fields(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "charness"
    agents_dir = repo / ".agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: charness",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "gate_commands:",
                "  - ./scripts/run-quality.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "mature charness quality adapter must explicitly declare" in result.stderr
    assert "`product_surfaces`" in result.stderr


def test_validate_adapters_accepts_charness_quality_adapter_mature_fields(tmp_path: Path) -> None:
    repo = tmp_path / "charness"
    agents_dir = repo / ".agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: charness",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "coverage_floor_policy:",
                "  min_statements_threshold: 30",
                "  fail_below_pct: 85.0",
                "  warn_ceiling_pct: 95.0",
                "  floor_drift_lock_pp: 1.0",
                "  exemption_list_path: scripts/coverage-floor-exemptions.txt",
                "  gate_script_pattern: tools/check_coverage.py",
                "  lefthook_path: lefthook.yml",
                "  ci_workflow_glob: .github/workflows/*.yml",
                "product_surfaces:",
                "  - installable_cli",
                "  - bundled_skill",
                "cli_skill_surface_probe_commands:",
                "  - ./charness --help",
                "cli_skill_surface_command_docs:",
                "  - .agents/command-docs.yaml",
                "cli_skill_surface_change_globs:",
                "  - charness",
                "canonical_markdown_surfaces:",
                "  - AGENTS.md",
                "  - CLAUDE.md",
                "  - docs/index.md",
                "runtime_profile_default: default",
                "runtime_budget_profiles:",
                "  local-linux-aarch64-4cpu:",
                "    budgets:",
                "      pytest: 70000",
                "startup_probes:",
                "  - label: charness-version",
                "    command:",
                "      - python3",
                "      - charness",
                "      - --version",
                "    class: standing",
                "    startup_mode: warm",
                "    surface: direct",
                "    samples: 3",
                "preflight_commands:",
                "  - python3 scripts/setup/validate_maintainer_setup.py --repo-root .",
                "gate_commands:",
                "  - ./scripts/run-quality.sh",
                "review_commands:",
                "  - ./scripts/run-quality.sh --review",
                "security_commands:",
                "  - ./scripts/check-secrets.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_validate_adapters_rejects_invalid_quality_adapter_rule(tmp_path: Path) -> None:
    repo = tmp_path / "quality-rule-drift"
    agents_dir = repo / ".agents"
    agents_dir.mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\nUse this when adapter validation needs a skill surface.\n",
        encoding="utf-8",
    )
    (agents_dir / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                "skill_ergonomics_gate_rules:",
                "  - typo_rule",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "skill_ergonomics_gate_rules contains unknown rule `typo_rule`" in result.stderr


def test_validate_adapters_allows_consumer_quality_gate_commands(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    agents_dir = repo / ".agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: my-repo\ngate_commands:\n  - ./tools/quality-gate.sh\n",
        encoding="utf-8",
    )

    result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "Validated" in result.stdout


def test_validate_adapters_accepts_checked_in_charness_quality_coverage_floor() -> None:
    result = run_script(
        "scripts/gates/validate_adapters.py", "--repo-root", str(Path(__file__).resolve().parents[2])
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.boundary_contract(
    reason="prove the exported validator runs from its flattened installed layout in a "
    "scrubbed child environment"
)
def test_exported_validate_adapters_runs_from_flattened_layout(tmp_path: Path) -> None:
    output_root = tmp_path / "export"
    exported = subprocess.run(
        [
            sys.executable,
            str(
                Path(__file__).resolve().parents[2]
                / "scripts"
                / "plugin_export"
                / "export_plugin.py"
            ),
            "--repo-root",
            str(Path(__file__).resolve().parents[2]),
            "--host",
            "claude",
            "--output-root",
            str(output_root),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert exported.returncode == 0, exported.stderr
    plugin_root = output_root / "plugins" / "charness"

    child_env = os.environ.copy()
    child_env.pop("CHARNESS_REPO_ROOT", None)
    result = subprocess.run(
        [
            sys.executable,
            str(plugin_root / "scripts" / "validate_adapters.py"),
            "--repo-root",
            str(plugin_root),
        ],
        cwd=tmp_path,
        env=child_env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    match = re.search(r"Validated (\d+) adapter resolvers and (\d+) adapter YAML", result.stdout)
    assert match and int(match.group(1)) > 0, result.stdout


def test_validate_adapters_covers_flattened_and_missing_layout_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resolver = tmp_path / "skills" / "demo" / "scripts" / "resolve_adapter.py"
    resolver.parent.mkdir(parents=True)
    resolver.write_text("def load_adapter(repo_root):\n    return {}\n", encoding="utf-8")

    assert VALIDATE_ADAPTERS.iter_resolvers(tmp_path) == [resolver]

    monkeypatch.setattr(VALIDATE_ADAPTERS, "REPO_ROOT", tmp_path / "missing")
    with pytest.raises(ImportError, match="retro resolve_adapter.py not found"):
        VALIDATE_ADAPTERS._load_retro_resolver_module()


def test_validate_adapters_rejects_charness_quality_command_drift(tmp_path: Path) -> None:
    repo = tmp_path / "command-drift"
    agents_dir = repo / ".agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: charness",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "coverage_floor_policy:",
                "  min_statements_threshold: 30",
                "  fail_below_pct: 85.0",
                "  warn_ceiling_pct: 95.0",
                "  floor_drift_lock_pp: 1.0",
                "  exemption_list_path: scripts/coverage-floor-exemptions.txt",
                "  gate_script_pattern: tools/check_coverage.py",
                "  lefthook_path: lefthook.yml",
                "  ci_workflow_glob: .github/workflows/*.yml",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- ./charness --help",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "cli_skill_surface_change_globs:",
                "- charness",
                "canonical_markdown_surfaces:",
                "- AGENTS.md",
                "- CLAUDE.md",
                "- docs/index.md",
                "runtime_profile_default: default",
                "runtime_budget_profiles:",
                "  local-linux-aarch64-4cpu:",
                "    budgets:",
                "      pytest: 70000",
                "startup_probes:",
                "- label: demo",
                "  command:",
                "  - python3",
                "  - -V",
                "  class: standing",
                "  startup_mode: warm",
                "  surface: direct",
                "preflight_commands:",
                "- python3 scripts/setup/validate_maintainer_setup.py --repo-root .",
                "gate_commands:",
                "- ./scripts/run-quality-stale.sh",
                "review_commands:",
                "- ./scripts/run-quality.sh --review",
                "security_commands:",
                "- ./scripts/check-secrets.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "gate_commands must exactly name the standing quality gate" in result.stderr


def test_validate_adapters_rejects_charness_quality_coverage_floor_threshold_drift(
    tmp_path: Path,
) -> None:
    cases = [
        (
            "min_statements_threshold",
            "31",
            "coverage_floor_policy.min_statements_threshold must match check_coverage.py (30)",
        ),
        (
            "warn_ceiling_pct",
            "94.0",
            "coverage_floor_policy.warn_ceiling_pct must match check_coverage.py (95.0)",
        ),
        (
            "gate_script_pattern",
            "scripts/other_coverage.py",
            "coverage_floor_policy.gate_script_pattern must name the actual coverage gate",
        ),
    ]
    for field, bad_value, expected_error in cases:
        repo = tmp_path / field
        agents_dir = repo / ".agents"
        agents_dir.mkdir(parents=True)
        policy = {
            "min_statements_threshold": "30",
            "fail_below_pct": "85.0",
            "warn_ceiling_pct": "95.0",
            "floor_drift_lock_pp": "1.0",
            "exemption_list_path": "scripts/coverage-floor-exemptions.txt",
            "gate_script_pattern": "tools/check_coverage.py",
            "lefthook_path": "lefthook.yml",
            "ci_workflow_glob": ".github/workflows/*.yml",
        }
        policy[field] = bad_value
        (agents_dir / "quality-adapter.yaml").write_text(
            "\n".join(
                [
                    "version: 1",
                    "repo: charness",
                    "language: en",
                    "output_dir: charness-artifacts/quality",
                    "coverage_floor_policy:",
                    *[f"  {key}: {value}" for key, value in policy.items()],
                    "product_surfaces:",
                    "- installable_cli",
                    "- bundled_skill",
                    "cli_skill_surface_probe_commands:",
                    "- ./charness --help",
                    "cli_skill_surface_command_docs:",
                    "- .agents/command-docs.yaml",
                    "cli_skill_surface_change_globs:",
                    "- charness",
                    "canonical_markdown_surfaces:",
                    "- AGENTS.md",
                    "- CLAUDE.md",
                    "- docs/index.md",
                    "runtime_profile_default: default",
                    "runtime_budget_profiles:",
                    "  local-linux-aarch64-4cpu:",
                    "    budgets:",
                    "      pytest: 70000",
                    "startup_probes:",
                    "- label: demo",
                    "  command:",
                    "  - python3",
                    "  - -V",
                    "  class: standing",
                    "  startup_mode: warm",
                    "  surface: direct",
                    "preflight_commands:",
                    "- python3 scripts/setup/validate_maintainer_setup.py --repo-root .",
                    "gate_commands:",
                    "- ./scripts/run-quality.sh",
                    "review_commands:",
                    "- ./scripts/run-quality.sh --review",
                    "security_commands:",
                    "- ./scripts/check-secrets.sh",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = run_script("scripts/gates/validate_adapters.py", "--repo-root", str(repo))
        assert result.returncode == 1
        assert expected_error in result.stderr
