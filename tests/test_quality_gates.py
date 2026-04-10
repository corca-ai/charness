from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_LIB_PATH = ROOT / "scripts" / "adapter_lib.py"
ADAPTER_LIB_SPEC = importlib.util.spec_from_file_location("adapter_lib", ADAPTER_LIB_PATH)
assert ADAPTER_LIB_SPEC is not None and ADAPTER_LIB_SPEC.loader is not None
ADAPTER_LIB = importlib.util.module_from_spec(ADAPTER_LIB_SPEC)
ADAPTER_LIB_SPEC.loader.exec_module(ADAPTER_LIB)


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def make_minimal_skill_repo(tmp_path: Path, description: str) -> Path:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                f"description: {description}",
                "---",
                "",
                "# Demo",
            ]
        ),
        encoding="utf-8",
    )
    return repo


def test_validate_skills_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-skills.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_unquoted_description(tmp_path: Path) -> None:
    repo = make_minimal_skill_repo(
        tmp_path,
        "Use when something has punctuation: this should be rejected.",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "double-quoted" in result.stderr


def test_validate_skills_rejects_missing_references_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing `## References` section" in result.stderr


def test_validate_skills_rejects_unlisted_reference_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
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
                "## References",
                "",
                "- `references/other.md`",
            ]
        ),
        encoding="utf-8",
    )
    (references_dir / "other.md").write_text("# Other\n", encoding="utf-8")
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "unlisted reference file(s): `references/note.md`" in result.stderr


def test_validate_profiles_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_presets_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-presets.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_packaging_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-packaging.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_sync_root_plugin_manifests_writes_install_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "skills" / "public").mkdir(parents=True)
    (repo / "skills" / "support").mkdir(parents=True)
    (repo / "profiles").mkdir(parents=True)
    (repo / "presets").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    shutil.copy2(ROOT / "packaging" / "plugin.schema.json", repo / "packaging" / "plugin.schema.json")
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.1.0",
                "summary": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "source": {
                    "readme": "README.md",
                    "skills_dir": "skills",
                    "public_skills_dir": "skills/public",
                    "support_skills_dir": "skills/support",
                    "profiles_dir": "profiles",
                    "presets_dir": "presets",
                    "integrations_dir": "integrations/tools",
                },
                "codex": {
                    "manifest_path": ".codex-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.1.0",
                        "description": "Demo package.",
                        "skills": "./skills/",
                    },
                    "repo_marketplace": {
                        "path": ".agents/plugins/marketplace.json",
                        "default_source_path": "./plugins/demo",
                        "repo_root_source_path": "./",
                        "display_name": "demo",
                        "category": "Productivity",
                    },
                },
                "claude": {
                    "manifest_path": ".claude-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.1.0",
                        "description": "Demo package.",
                        "repository": "https://example.com/demo",
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/sync_root_plugin_manifests.py", "--repo-root", str(repo), "--package-id", "demo")
    assert result.returncode == 0, result.stderr
    assert (repo / ".claude-plugin" / "plugin.json").exists()
    assert (repo / ".codex-plugin" / "plugin.json").exists()
    assert (repo / ".agents" / "plugins" / "marketplace.json").exists()

    validate = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert validate.returncode == 0, validate.stderr


def test_check_python_lengths_passes_on_current_repo() -> None:
    result = run_script("scripts/check-python-lengths.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


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
                "bundles": {"public_skills": ["handoff"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing artifact `handoff`" in result.stderr


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
    result = run_script("scripts/validate-presets.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "organization-scope presets must use `preset_kind: product-slice`" in result.stderr


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
    result = run_script("scripts/validate-presets.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "product-slice presets must include an `## Exposure Contract` section" in result.stderr


def test_check_python_lengths_rejects_too_long_function(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    long_body = "\n".join(f"    value_{i} = {i}" for i in range(101))
    (scripts_dir / "long.py").write_text(
        "\n".join(
            [
                "def too_long():",
                long_body,
                "    return 0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/check-python-lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "function `too_long` length" in result.stderr


def test_check_python_lengths_rejects_too_long_skill_helper_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "helper.py").write_text(
        "\n".join(f"print({i})" for i in range(221)) + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-python-lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "file length 221 exceeds limit 220" in result.stderr


def test_validate_profiles_rejects_unknown_smoke_scenario(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "handoff"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
        encoding="utf-8",
    )
    (profiles_dir / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "demo",
                "display_name": "Demo",
                "purpose": "Test",
                "bundles": {"public_skills": ["handoff"]},
                "validation": {"smoke_scenarios": ["not-a-real-scenario"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "unknown eval scenario `not-a-real-scenario`" in result.stderr


def test_validate_profiles_rejects_missing_extends_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "handoff"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
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
                "bundles": {"public_skills": ["handoff"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "extends[]` references missing artifact `missing-base`" in result.stderr


def test_validate_profiles_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "handoff"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n\n## References\n\n- `references/demo.md`\n",
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
                "bundles": {"public_skills": ["handoff"]},
                "unexpected": True,
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


def test_validate_adapters_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-adapters.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_check_skill_contracts_passes_on_current_repo() -> None:
    result = run_script("scripts/check-skill-contracts.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_foreign_absolute_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(
        "[bad](/tmp/not-in-repo.md)\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "foreign absolute link" in result.stderr


def test_check_duplicates_passes_clean_repo() -> None:
    result = run_script("scripts/check-duplicates.py", "--repo-root", str(ROOT), "--json", "--fail-on-match")
    assert result.returncode == 0, result.stderr
    duplicates = json.loads(result.stdout)
    assert isinstance(duplicates, list)
    assert duplicates == []


def test_adapter_lib_renders_and_loads_simple_yaml_mapping() -> None:
    rendered = ADAPTER_LIB.render_yaml_mapping(
        [
            ("version", 1),
            ("repo", "demo"),
            ("output_dir", "skill-outputs/demo"),
            ("commands", ["pytest -q", "ruff check ."]),
            ("empty", []),
        ]
    )

    assert ADAPTER_LIB.load_yaml(rendered) == {
        "version": 1,
        "repo": "demo",
        "output_dir": "skill-outputs/demo",
        "commands": ["pytest -q", "ruff check ."],
        "empty": [],
    }


def test_check_duplicates_rejects_near_duplicate_docs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    repeated_lines = "\n".join(f"- repeated line {i}" for i in range(20))
    (docs_dir / "alpha.md").write_text(f"# Alpha\n\n{repeated_lines}\n", encoding="utf-8")
    (docs_dir / "beta.md").write_text(f"# Beta\n\n{repeated_lines}\n", encoding="utf-8")

    result = run_script(
        "scripts/check-duplicates.py",
        "--repo-root",
        str(repo),
        "--fail-on-match",
        "--json",
    )
    assert result.returncode == 1
    duplicates = json.loads(result.stdout)
    assert duplicates
    assert duplicates[0]["left"] == "docs/alpha.md"
    assert duplicates[0]["right"] == "docs/beta.md"


def test_run_evals_passes_on_current_repo() -> None:
    result = run_script("scripts/run-evals.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "Ran 12 eval scenario(s)." in result.stdout


def test_validate_packaging_rejects_wrong_codex_manifest_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "skills" / "public").mkdir(parents=True)
    (repo / "skills" / "support").mkdir(parents=True)
    (repo / "profiles").mkdir(parents=True)
    (repo / "presets").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.0.0-dev",
                "summary": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "source": {
                    "readme": "README.md",
                    "skills_dir": "skills",
                    "public_skills_dir": "skills/public",
                    "support_skills_dir": "skills/support",
                    "profiles_dir": "profiles",
                    "presets_dir": "presets",
                    "integrations_dir": "integrations/tools",
                },
                "codex": {
                    "manifest_path": "plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "skills": "./skills/",
                    },
                    "repo_marketplace": {
                        "path": ".agents/plugins/marketplace.json",
                        "default_source_path": "./plugins/demo",
                        "display_name": "demo",
                        "category": "Productivity",
                    },
                },
                "claude": {
                    "manifest_path": ".claude-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "repository": "https://example.com/demo",
                    },
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert ".codex-plugin/plugin.json" in result.stderr


def test_validate_packaging_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "skills" / "public").mkdir(parents=True)
    (repo / "skills" / "support").mkdir(parents=True)
    (repo / "profiles").mkdir(parents=True)
    (repo / "presets").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.0.0-dev",
                "summary": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "source": {
                    "readme": "README.md",
                    "skills_dir": "skills",
                    "public_skills_dir": "skills/public",
                    "support_skills_dir": "skills/support",
                    "profiles_dir": "profiles",
                    "presets_dir": "presets",
                    "integrations_dir": "integrations/tools",
                },
                "codex": {
                    "manifest_path": ".codex-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "skills": "./skills/",
                    },
                    "repo_marketplace": {
                        "path": ".agents/plugins/marketplace.json",
                        "default_source_path": "./plugins/demo",
                        "display_name": "demo",
                        "category": "Productivity",
                    },
                },
                "claude": {
                    "manifest_path": ".claude-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "repository": "https://example.com/demo",
                    },
                },
                "unexpected": True,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


def test_export_plugin_materializes_codex_and_claude_layouts(tmp_path: Path) -> None:
    codex_root = tmp_path / "codex-export"
    claude_root = tmp_path / "claude-export"

    codex_result = run_script(
        "scripts/export-plugin.py",
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(codex_root),
        "--with-marketplace",
    )
    assert codex_result.returncode == 0, codex_result.stderr
    codex_manifest = codex_root / "plugins" / "charness" / ".codex-plugin" / "plugin.json"
    codex_marketplace = codex_root / ".agents" / "plugins" / "marketplace.json"
    assert codex_manifest.is_file()
    assert codex_marketplace.is_file()
    assert json.loads(codex_manifest.read_text(encoding="utf-8"))["skills"] == "./skills/"
    assert (
        json.loads(codex_marketplace.read_text(encoding="utf-8"))["plugins"][0]["source"]["path"]
        == "./plugins/charness"
    )

    claude_result = run_script(
        "scripts/export-plugin.py",
        "--repo-root",
        str(ROOT),
        "--host",
        "claude",
        "--output-root",
        str(claude_root),
    )
    assert claude_result.returncode == 0, claude_result.stderr
    claude_manifest = claude_root / "plugins" / "charness" / ".claude-plugin" / "plugin.json"
    exported_readme = claude_root / "plugins" / "charness" / "README.md"
    exported_profiles = claude_root / "plugins" / "charness" / "profiles"
    assert claude_manifest.is_file()
    assert exported_readme.is_file()
    assert exported_profiles.is_dir()
    assert json.loads(claude_manifest.read_text(encoding="utf-8"))["repository"] == "https://github.com/corca-ai/charness"


def test_check_skill_contracts_rejects_missing_required_snippet(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    handoff_skill_dir = repo / "skills" / "public" / "handoff"
    gather_skill_dir = repo / "skills" / "public" / "gather"
    create_skill_dir = repo / "skills" / "public" / "create-skill"
    spec_skill_dir = repo / "skills" / "public" / "spec"
    handoff_skill_dir.mkdir(parents=True)
    gather_skill_dir.mkdir(parents=True)
    create_skill_dir.mkdir(parents=True)
    spec_skill_dir.mkdir(parents=True)

    (handoff_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
        encoding="utf-8",
    )
    (gather_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (create_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "create-skill" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (spec_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = run_script("scripts/check-skill-contracts.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required contract snippet" in result.stderr


def test_find_skills_lists_adapter_configured_official_roots(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    local_skill_dir = repo / "skills" / "public" / "local-demo"
    official_skill_dir = repo / "vendor" / "official-skills" / "official-demo"
    adapter_dir = repo / ".agents"
    local_skill_dir.mkdir(parents=True)
    official_skill_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)

    (local_skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: local-demo",
                'description: "Local demo skill."',
                "---",
                "",
                "# Local Demo",
            ]
        ),
        encoding="utf-8",
    )
    (official_skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: official-demo",
                'description: "Official demo skill."',
                "---",
                "",
                "# Official Demo",
            ]
        ),
        encoding="utf-8",
    )
    (adapter_dir / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: skill-outputs/find-skills",
                "official_skill_roots:",
                "- vendor/official-skills",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/find-skills/scripts/list_capabilities.py",
        "--repo-root",
        str(repo),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["public_skills"][0]["id"] == "local-demo"
    assert payload["official_skills"][0]["id"] == "official-demo"
