from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def seed_quality_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (repo / "tsconfig.json").write_text('{"compilerOptions":{"noEmit":true}}\n', encoding="utf-8")
    (repo / "package.json").write_text('{"name":"demo","workspaces":["packages/*"]}\n', encoding="utf-8")
    (repo / "pnpm-workspace.yaml").write_text("packages:\n  - packages/*\n", encoding="utf-8")
    (repo / "scripts" / "run-quality.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "scripts" / "validate_maintainer_setup.py").write_text("print('ok')\n", encoding="utf-8")
    (repo / "scripts" / "check-secrets.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "scripts" / "check_supply_chain.py").write_text("print('ok')\n", encoding="utf-8")
    return repo


def test_quality_bootstrap_adapter_records_installed_and_inferred_fields(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    result = run_script("skills/public/quality/scripts/bootstrap_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["adapter_status"] == "written"
    assert payload["field_statuses"] == {
        "coverage_fragile_margin_pp": "defaulted",
        "coverage_floor_policy": "defaulted",
        "concept_paths": "inferred",
        "gate_commands": "installed",
        "preflight_commands": "installed",
        "preset_lineage": "inferred",
        "prompt_asset_policy": "defaulted",
        "prompt_asset_roots": "defaulted",
        "review_commands": "inferred",
        "runtime_budgets": "defaulted",
        "startup_probes": "defaulted",
        "skill_ergonomics_gate_rules": "defaulted",
        "specdown_smoke_patterns": "defaulted",
        "spec_pytest_reference_format": "defaulted",
        "security_commands": "installed",
    }
    assert payload["preset_lineage"] == ["python-quality", "typescript-quality", "monorepo-quality"]
    assert payload["deferred_setup"] == []
    report_path = repo / ".charness" / "quality" / "bootstrap.json"
    assert report_path.is_file()

    resolve_result = run_script("skills/public/quality/scripts/resolve_adapter.py", "--repo-root", str(repo))
    assert resolve_result.returncode == 0, resolve_result.stderr
    resolved = json.loads(resolve_result.stdout)
    assert resolved["data"]["preset_lineage"] == ["python-quality", "typescript-quality", "monorepo-quality"]
    assert resolved["data"]["coverage_fragile_margin_pp"] == 1.0
    assert resolved["data"]["coverage_floor_policy"] == {
        "min_statements_threshold": 30,
        "fail_below_pct": 80.0,
        "warn_ceiling_pct": 95.0,
        "floor_drift_lock_pp": 1.0,
        "exemption_list_path": "scripts/coverage-floor-exemptions.txt",
        "gate_script_pattern": "*-quality-gate.sh",
        "lefthook_path": "lefthook.yml",
        "ci_workflow_glob": ".github/workflows/*.yml",
    }
    assert resolved["data"]["specdown_smoke_patterns"] == []
    assert resolved["data"]["spec_pytest_reference_format"] == (
        r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
    )
    assert resolved["data"]["prompt_asset_roots"] == []
    assert resolved["data"]["prompt_asset_policy"] == {
        "source_globs": [],
        "min_multiline_chars": 400,
        "exemption_globs": [],
    }
    assert resolved["data"]["skill_ergonomics_gate_rules"] == []
    assert resolved["data"]["runtime_budgets"] == {}
    assert resolved["data"]["startup_probes"] == []
    assert resolved["data"]["gate_commands"] == ["./scripts/run-quality.sh"]
    assert resolved["data"]["review_commands"] == ["./scripts/run-quality.sh --review"]
    assert resolved["data"]["preflight_commands"] == ["python3 scripts/validate_maintainer_setup.py --repo-root ."]


def test_quality_bootstrap_adapter_preserves_existing_explicit_commands(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "preset_id: python-quality",
                "customized_from: python-quality",
                "preset_lineage:",
                "- python-quality",
                "coverage_fragile_margin_pp: 0.5",
                "coverage_floor_policy:",
                "  min_statements_threshold: 45",
                "  fail_below_pct: 82.0",
                "  warn_ceiling_pct: 96.0",
                "  floor_drift_lock_pp: 0.5",
                "  exemption_list_path: scripts/custom-exemptions.txt",
                "  gate_script_pattern: \"*-boundary-gate.sh\"",
                "  lefthook_path: config/lefthook.yml",
                "  ci_workflow_glob: .github/workflows/quality-*.yml",
                "specdown_smoke_patterns: []",
                "spec_pytest_reference_format: \"Covered by pytest:\\s+`tests/custom[^`]+`\"",
                "prompt_asset_roots:",
                "- prompts",
                "prompt_asset_policy:",
                "  source_globs:",
                "  - src/**/*.py",
                "  min_multiline_chars: 256",
                "  exemption_globs:",
                "  - tests/**",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
                "startup_probes:",
                "  - label: demo-version",
                "    command:",
                "      - python3",
                "      - -V",
                "    class: standing",
                "    startup_mode: warm",
                "    surface: direct",
                "    samples: 2",
                "gate_commands:",
                "- python3 -m pytest -q",
                "preflight_commands: []",
                "security_commands: []",
                "concept_paths: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("skills/public/quality/scripts/bootstrap_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["adapter_status"] == "updated"
    assert payload["field_statuses"]["gate_commands"] == "preserved"
    assert payload["field_statuses"]["coverage_fragile_margin_pp"] == "preserved"
    assert payload["field_statuses"]["coverage_floor_policy"] == "preserved"
    assert payload["field_statuses"]["specdown_smoke_patterns"] == "preserved"
    assert payload["field_statuses"]["spec_pytest_reference_format"] == "preserved"
    assert payload["field_statuses"]["prompt_asset_roots"] == "preserved"
    assert payload["field_statuses"]["prompt_asset_policy"] == "preserved"
    assert payload["field_statuses"]["skill_ergonomics_gate_rules"] == "preserved"
    assert payload["field_statuses"]["startup_probes"] == "preserved"

    resolve_result = run_script("skills/public/quality/scripts/resolve_adapter.py", "--repo-root", str(repo))
    assert resolve_result.returncode == 0, resolve_result.stderr
    resolved = json.loads(resolve_result.stdout)
    assert resolved["data"]["gate_commands"] == ["python3 -m pytest -q"]
    assert resolved["data"]["coverage_fragile_margin_pp"] == 0.5
    assert resolved["data"]["coverage_floor_policy"] == {
        "min_statements_threshold": 45,
        "fail_below_pct": 82.0,
        "warn_ceiling_pct": 96.0,
        "floor_drift_lock_pp": 0.5,
        "exemption_list_path": "scripts/custom-exemptions.txt",
        "gate_script_pattern": "*-boundary-gate.sh",
        "lefthook_path": "config/lefthook.yml",
        "ci_workflow_glob": ".github/workflows/quality-*.yml",
    }
    assert resolved["data"]["specdown_smoke_patterns"] == []
    assert resolved["data"]["spec_pytest_reference_format"] == r"Covered by pytest:\s+`tests/custom[^`]+`"
    assert resolved["data"]["prompt_asset_roots"] == ["prompts"]
    assert resolved["data"]["prompt_asset_policy"] == {
        "source_globs": ["src/**/*.py"],
        "min_multiline_chars": 256,
        "exemption_globs": ["tests/**"],
    }
    assert resolved["data"]["skill_ergonomics_gate_rules"] == ["mode_option_pressure_terms"]
    assert resolved["data"]["startup_probes"] == [
        {
            "label": "demo-version",
            "command": ["python3", "-V"],
            "class": "standing",
            "startup_mode": "warm",
            "surface": "direct",
            "samples": 2,
        }
    ]
    assert resolved["data"]["preset_lineage"] == ["python-quality", "typescript-quality", "monorepo-quality"]


def test_quality_bootstrap_rejects_invalid_explicit_skill_ergonomics_rules(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "preset_id: python-quality",
                "customized_from: python-quality",
                "skill_ergonomics_gate_rules: invalid",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("skills/public/quality/scripts/bootstrap_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "invalid `skill_ergonomics_gate_rules`" in result.stderr
    assert "Repair the adapter before rerunning bootstrap" in result.stderr


def test_quality_bootstrap_detects_repo_owned_github_actions_check(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    (repo / "scripts" / "run-quality.sh").unlink()
    (repo / "scripts" / "check_github_actions.py").write_text("print('ok')\n", encoding="utf-8")

    result = run_script("skills/public/quality/scripts/bootstrap_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr

    resolve_result = run_script("skills/public/quality/scripts/resolve_adapter.py", "--repo-root", str(repo))
    assert resolve_result.returncode == 0, resolve_result.stderr
    resolved = json.loads(resolve_result.stdout)
    assert resolved["data"]["gate_commands"] == ["python3 scripts/check_github_actions.py --repo-root ."]


def test_quality_bootstrap_infers_specdown_defaults(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    (repo / ".specdown").mkdir()

    result = run_script("skills/public/quality/scripts/bootstrap_adapter.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["field_statuses"]["specdown_smoke_patterns"] == "inferred"
    assert "specdown-quality" in payload["preset_lineage"]

    resolve_result = run_script("skills/public/quality/scripts/resolve_adapter.py", "--repo-root", str(repo))
    assert resolve_result.returncode == 0, resolve_result.stderr
    resolved = json.loads(resolve_result.stdout)
    assert resolved["data"]["coverage_fragile_margin_pp"] == 1.0
    assert resolved["data"]["coverage_floor_policy"]["min_statements_threshold"] == 30
    assert resolved["data"]["specdown_smoke_patterns"] == [
        r"\bgrep\s+-q\b",
        r"\[pycheck\]",
        r"\b(?:uv\s+run\s+)?python\s+-m\s+pytest\b",
        r"\bpytest\b.*\s-k\s+",
    ]
    assert resolved["data"]["spec_pytest_reference_format"] == (
        r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
    )
    assert resolved["data"]["skill_ergonomics_gate_rules"] == []


def test_quality_init_adapter_seeds_specdown_defaults(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(
        "skills/public/quality/scripts/init_adapter.py",
        "--repo-root",
        str(repo),
        "--preset-id",
        "specdown-quality",
    )
    assert result.returncode == 0, result.stderr

    resolve_result = run_script("skills/public/quality/scripts/resolve_adapter.py", "--repo-root", str(repo))
    assert resolve_result.returncode == 0, resolve_result.stderr
    resolved = json.loads(resolve_result.stdout)
    assert resolved["data"]["preset_lineage"] == ["specdown-quality"]
    assert resolved["data"]["coverage_fragile_margin_pp"] == 1.0
    assert resolved["data"]["coverage_floor_policy"]["gate_script_pattern"] == "*-quality-gate.sh"
    assert resolved["data"]["specdown_smoke_patterns"] == [
        r"\bgrep\s+-q\b",
        r"\[pycheck\]",
        r"\b(?:uv\s+run\s+)?python\s+-m\s+pytest\b",
        r"\bpytest\b.*\s-k\s+",
    ]
    assert resolved["data"]["spec_pytest_reference_format"] == (
        r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
    )
