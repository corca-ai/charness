from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
import yaml

import scripts.gates.check_consumer_validator_catalog as consumer_validator_catalog_module
import scripts.plugin_export.export_plugin as export_plugin_module
import scripts.plugin_export.packaging_lib as packaging_lib
import scripts.plugin_export.sync_root_plugin_manifests as sync_root_plugin_manifests_module
import scripts.plugin_export.validate_packaging as validate_packaging_module
import scripts.plugin_export.validate_packaging_install_surface as validate_packaging_install_surface_module
from tests.repo_copy import clone_seeded_charness_repo
from tests.script_main import run_loaded_script_main

from .support import EVAL_REGISTRY, ROOT, run_script


def test_exported_consumer_validator_catalog_rewrite_is_fail_closed(tmp_path: Path) -> None:
    catalog_path = tmp_path / "skills/quality/references/consumer-validator-catalog.yaml"
    catalog_path.parent.mkdir(parents=True)

    catalog_path.write_text("\npackage_root: .\n", encoding="utf-8")
    packaging_lib.rewrite_exported_consumer_validator_catalog(tmp_path)
    assert catalog_path.read_text(encoding="utf-8") == "\npackage_root: .\n"

    catalog_path.write_text("\npackage_root: unexpected\n", encoding="utf-8")
    with pytest.raises(packaging_lib.PackagingError, match="expected source-relative"):
        packaging_lib.rewrite_exported_consumer_validator_catalog(tmp_path)


def make_demo_packaging_repo(
    tmp_path: Path,
    *,
    codex_manifest_path: str = ".codex-plugin/plugin.json",
    include_unexpected_field: bool = False,
) -> Path:
    repo = tmp_path / "repo"
    for relative in (
        "packaging",
        "skills/public",
        "skills/support",
        "profiles",
        "presets",
        "integrations/tools",
    ):
        (repo / relative).mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    manifest = {
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
            "manifest_path": codex_manifest_path,
            "manifest": {
                "name": "demo",
                "version": "0.0.0-dev",
                "description": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "keywords": ["demo"],
                "skills": "./skills/",
                "interface": {
                    "displayName": "demo",
                    "shortDescription": "Demo package.",
                    "longDescription": "Demo package for plugin export tests.",
                    "developerName": "Demo",
                    "category": "Productivity",
                    "capabilities": ["Read"],
                    "websiteURL": "https://example.com/demo",
                    "defaultPrompt": ["Use the demo plugin."],
                },
            },
            "repo_marketplace": {
                "path": ".agents/plugins/marketplace.json",
                "default_source_path": "./plugins/demo",
                "materialized_source_path": "./plugins/demo",
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
                "author": {"name": "Demo"},
                "repository": "https://example.com/demo",
            },
            "marketplace": {
                "path": ".claude-plugin/marketplace.json",
                "name": "demo-marketplace",
                "source_path": "./plugins/demo",
            },
        },
    }
    if include_unexpected_field:
        manifest["unexpected"] = True
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return repo


@pytest.mark.boundary_contract(
    reason="construct the clean packaging fixture through real git staging and commit operations"
)
def make_clean_git_repo(tmp_path: Path, seeded_charness_git_repo: Path) -> Path:
    repo = clone_seeded_charness_repo(tmp_path, seeded_charness_git_repo)
    sync = run_loaded_script_main(
        "sync_root_plugin_manifests.py",
        sync_root_plugin_manifests_module,
        "--repo-root",
        str(repo),
    )
    assert sync.returncode == 0, sync.stderr
    subprocess.run(
        ["git", "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo,
        check=False,
    )
    if staged.returncode == 1:
        subprocess.run(
            ["git", "commit", "-m", "Sync temporary plugin export"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
    elif staged.returncode != 0:
        raise subprocess.CalledProcessError(staged.returncode, staged.args)
    return repo


@pytest.mark.release_only
def test_validate_packaging_default_allows_materialized_plugin_export_drift(
    tmp_path: Path, seeded_charness_git_repo: Path
) -> None:
    repo = make_clean_git_repo(tmp_path, seeded_charness_git_repo)
    readme_path = repo / "README.md"
    readme_path.write_text(readme_path.read_text(encoding="utf-8") + "\nDrift.\n", encoding="utf-8")

    result = run_loaded_script_main(
        "validate_packaging.py", validate_packaging_module, "--repo-root", str(repo)
    )
    assert result.returncode == 0, result.stderr

    export_result = run_loaded_script_main(
        "validate_packaging.py",
        validate_packaging_module,
        "--repo-root",
        str(repo),
        "--validate-export",
    )
    assert export_result.returncode == 1
    assert (
        "materialized plugin export does not match the generated install surface"
        in export_result.stderr
    )
    assert "scripts/plugin_export/sync_root_plugin_manifests.py" in export_result.stderr


def test_sync_root_plugin_manifests_writes_install_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    for relative in (
        "packaging",
        "skills/public",
        "skills/support",
        "profiles",
        "presets",
        "integrations/tools",
    ):
        (repo / relative).mkdir(parents=True)
    shutil.copy2(
        ROOT / "packaging" / "plugin.schema.json", repo / "packaging" / "plugin.schema.json"
    )
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
                        "author": {"name": "Demo"},
                        "homepage": "https://example.com/demo",
                        "repository": "https://example.com/demo",
                        "keywords": ["demo"],
                        "skills": "./skills/",
                        "interface": {
                            "displayName": "demo",
                            "shortDescription": "Demo package.",
                            "longDescription": "Demo package for plugin export tests.",
                            "developerName": "Demo",
                            "category": "Productivity",
                            "capabilities": ["Read"],
                            "websiteURL": "https://example.com/demo",
                            "defaultPrompt": ["Use the demo plugin."],
                        },
                    },
                    "repo_marketplace": {
                        "path": ".agents/plugins/marketplace.json",
                        "default_source_path": "./plugins/demo",
                        "materialized_source_path": "./plugins/demo",
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
                        "author": {"name": "Demo"},
                        "repository": "https://example.com/demo",
                    },
                    "marketplace": {
                        "path": ".claude-plugin/marketplace.json",
                        "name": "demo-marketplace",
                        "source_path": "./plugins/demo",
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_loaded_script_main(
        "sync_root_plugin_manifests.py",
        sync_root_plugin_manifests_module,
        "--repo-root",
        str(repo),
        "--package-id",
        "demo",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    summary = payload["change_summary"]
    assert "plugins/demo/README.md" in summary["added_paths"]
    assert summary["removed_paths"] == []
    assert isinstance(summary["unchanged_count"], int)
    assert (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").exists()
    assert (repo / ".claude-plugin" / "marketplace.json").exists()
    assert (repo / "plugins" / "demo" / ".codex-plugin" / "plugin.json").exists()
    assert (repo / ".agents" / "plugins" / "marketplace.json").exists()

    validate = run_loaded_script_main(
        "validate_packaging.py", validate_packaging_module, "--repo-root", str(repo)
    )
    assert validate.returncode == 0, validate.stderr


@pytest.mark.release_only
def test_validate_packaging_export_reads_gitignored_plugin_tree(
    tmp_path: Path, seeded_charness_git_repo: Path
) -> None:
    """The host-facing export is intentionally gitignored but still validated on disk."""
    repo = make_clean_git_repo(tmp_path, seeded_charness_git_repo)

    result = run_loaded_script_main(
        "validate_packaging.py",
        validate_packaging_module,
        "--repo-root",
        str(repo),
        "--validate-export",
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.release_only
def test_exported_consumer_validator_catalog_uses_installed_package_root(
    tmp_path: Path, seeded_charness_repo: Path
) -> None:
    repo = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)

    result = run_loaded_script_main(
        "sync_root_plugin_manifests.py",
        sync_root_plugin_manifests_module,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    source_catalog = repo / "skills/public/quality/references/consumer-validator-catalog.yaml"
    exported_catalog = (
        repo / "plugins/charness/skills/quality/references/consumer-validator-catalog.yaml"
    )
    assert "package_root: plugins/charness" in source_catalog.read_text(encoding="utf-8")
    assert "package_root: ." in exported_catalog.read_text(encoding="utf-8")

    validate = run_loaded_script_main(
        "check_consumer_validator_catalog.py",
        consumer_validator_catalog_module,
        "--repo-root",
        str(repo / "plugins/charness"),
        "--catalog-path",
        str(exported_catalog),
        "--package-root",
        str(repo / "plugins/charness"),
    )
    assert validate.returncode == 0, validate.stderr


@pytest.mark.release_only
def test_validate_packaging_committed_accepts_clean_head(
    tmp_path: Path, seeded_charness_git_repo: Path
) -> None:
    repo = make_clean_git_repo(tmp_path, seeded_charness_git_repo)

    result = run_script("tools/validate_packaging_committed.py", "--repo-root", str(repo), cwd=repo)
    assert result.returncode == 0, result.stderr


# DELETED 2026-08-29: `test_validate_packaging_committed_rejects_partial_commit_with_uncommitted_export`.
# It asserted that `validate_packaging_committed` refuses when "the materialized plugin
# export does not match the generated install surface". `--validate-export` was dropped
# when `plugins/` stopped being tracked, so there is no tracked plugin export and the
# scenario it drove cannot occur. It had been RED since that change. Kept as a comment
# rather than a skipped test or a renamed tombstone: this repo does not add "must not
# exist" tests for retired behaviour, and a red test nobody can make green is worse
# than an absent one. The surviving half -- committed manifests must be well-formed and
# agree -- is `test_validate_packaging_committed_accepts_clean_head` above.


def test_eval_registry_omits_redundant_current_repo_smokes() -> None:
    scenario_ids = EVAL_REGISTRY.scenario_ids()
    assert {"managed-cli-install", "packaging-valid", "packaging-export"}.isdisjoint(scenario_ids)


def test_eval_registry_scenarios_are_immutable_contract_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Load a fresh copy from source so the `@dataclass(frozen=True)` decorator
    # line re-executes under THIS test's coverage context. The decorator runs
    # once at import (before any test context is active), so mutation sampling
    # never attributes the frozen-dataclass line to this kill test and the
    # `frozen=True -> False` mutant survives as a false coverage gap (#198). A
    # fresh module copy avoids mutating `sys.modules` and so cannot contaminate
    # other tests that import `tools.eval_registry`.
    import importlib.util
    import sys

    source = ROOT / "tools" / "eval_registry.py"
    spec = importlib.util.spec_from_file_location("_eval_registry_immutability_probe", source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # `from __future__ import annotations` makes the field annotation a string;
    # dataclasses resolves it via `sys.modules[cls.__module__]`, so the probe
    # module must be registered before exec. `setitem` deletes the unique
    # throwaway name again at teardown, so it never leaks into other tests.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    scenario = module.SCENARIOS[0]

    with pytest.raises(FrozenInstanceError):
        scenario.description = "mutated"


def test_validate_packaging_rejects_wrong_codex_manifest_path(tmp_path: Path) -> None:
    repo = make_demo_packaging_repo(tmp_path, codex_manifest_path="plugin.json")
    result = run_loaded_script_main(
        "validate_packaging.py", validate_packaging_module, "--repo-root", str(repo)
    )
    assert result.returncode == 1
    assert ".codex-plugin/plugin.json" in result.stderr


def test_validate_packaging_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    repo = make_demo_packaging_repo(tmp_path, include_unexpected_field=True)
    result = run_loaded_script_main(
        "validate_packaging.py", validate_packaging_module, "--repo-root", str(repo)
    )
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


@pytest.mark.boundary_contract(
    reason="prove the packaging install-surface checker bootstraps from a clean interpreter "
    "with ambient repo-import variables removed"
)
def test_validate_packaging_install_surface_bootstraps_repo_imports(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("CHARNESS_REPO_ROOT", None)

    result = subprocess.run(
        [
            "python3",
            "-m",
            "scripts.plugin_export.validate_packaging_install_surface",
            "--repo-root",
            str(ROOT),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_plugin_import_smoke_script_lives_in_template_asset() -> None:
    template_path = ROOT / "scripts" / "templates" / "plugin_import_smoke.py.txt"
    assert template_path.read_text(encoding="utf-8") == (
        validate_packaging_install_surface_module._IMPORT_SMOKE_SCRIPT
    )


def test_plugin_import_smoke_allows_exported_script_sibling_imports(tmp_path: Path) -> None:
    plugin_root = tmp_path / "plugin"
    scripts_dir = plugin_root / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "helper_lib.py").write_text("VALUE = 7\n", encoding="utf-8")
    (scripts_dir / "uses_helper.py").write_text(
        "from helper_lib import VALUE\nassert VALUE == 7\n",
        encoding="utf-8",
    )

    validate_packaging_install_surface_module.smoke_exported_plugin_imports(plugin_root)


@pytest.mark.release_only
def test_validate_packaging_rejects_invalid_public_skill_policy_when_present(
    tmp_path: Path, seeded_charness_repo: Path
) -> None:
    repo = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    policy_path = repo / "docs" / "public-skill-validation.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["tiers"]["hitl-recommended"].remove("critique")
    policy_path.write_text(
        json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    result = run_loaded_script_main(
        "validate_packaging.py", validate_packaging_module, "--repo-root", str(repo)
    )
    assert result.returncode == 1
    assert "does not classify every public skill" in result.stderr


def test_export_plugin_materializes_codex_and_claude_layouts(tmp_path: Path) -> None:
    codex_root = tmp_path / "codex-export"
    claude_root = tmp_path / "claude-export"

    codex_result = run_loaded_script_main(
        "export_plugin.py",
        export_plugin_module,
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

    claude_result = run_loaded_script_main(
        "export_plugin.py",
        export_plugin_module,
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
    exported_gather_skill = claude_root / "plugins" / "charness" / "skills" / "gather" / "SKILL.md"
    exported_shared_ref = (
        claude_root / "plugins" / "charness" / "shared" / "references" / "binary-preflight.md"
    )
    exported_support_skill = (
        claude_root / "plugins" / "charness" / "support" / "web-fetch" / "SKILL.md"
    )
    exported_agent_browser = (
        claude_root / "plugins" / "charness" / "support" / "agent-browser" / "SKILL.md"
    )
    exported_specdown = claude_root / "plugins" / "charness" / "support" / "specdown" / "SKILL.md"
    exported_helper_script = claude_root / "plugins" / "charness" / "scripts" / "adapter_lib.py"
    exported_scripts = claude_root / "plugins" / "charness" / "scripts"
    exported_tools = claude_root / "plugins" / "charness" / "tools"
    assert claude_manifest.is_file()
    assert exported_readme.is_file()
    assert exported_profiles.is_dir()
    assert exported_gather_skill.is_file()
    assert exported_shared_ref.is_file()
    assert exported_support_skill.is_file()
    assert not exported_agent_browser.exists()
    assert not exported_specdown.exists()
    assert exported_helper_script.is_file()
    assert not exported_tools.exists()
    assert not (exported_scripts / "validate_skills.py").exists()
    assert (
        exported_scripts / "plugin_export" / "validate_packaging.py"
    ).exists()  # export machinery ships
    assert (exported_scripts / "gates_support" / "public_skill_dogfood_lib.py").is_file()
    assert (
        claude_root
        / "plugins"
        / "charness"
        / "skills"
        / "quality"
        / "scripts"
        / "suggest_public_skill_dogfood.py"  # sweep-keep: the skill's own script
    ).is_file()
    assert not (claude_root / "plugins" / "charness" / "skills" / "public").exists()
    assert not (claude_root / "plugins" / "charness" / "support" / "generated").exists()
    assert (
        json.loads(claude_manifest.read_text(encoding="utf-8"))["repository"]
        == "https://github.com/corca-ai/charness"
    )
    exported_readme_text = exported_readme.read_text(encoding="utf-8")
    assert exported_readme_text.startswith("<!--\ngenerated_file: true\n")
    assert "source_path: README.md" in exported_readme_text
    assert (
        "sync_command: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root ."
        in exported_readme_text
    )
    assert "./skills/public/" not in exported_readme_text
    assert "./skills/support/" not in exported_readme_text
    assert "./plugins/charness/support/" not in exported_readme_text
    assert "(./skills/)" in exported_readme_text
    assert "(./support/agent-browser/SKILL.md)" not in exported_readme_text
    assert "(./support/specdown/SKILL.md)" not in exported_readme_text
    assert (
        "(https://github.com/corca-ai/charness/blob/main/docs/cli-reference.md)"
        in exported_readme_text
    )
    assert (
        "(https://github.com/corca-ai/charness/blob/main/docs/host-packaging.md)"
        in exported_readme_text
    )

    validate_exported_skills = run_script(
        "tools/validate_skills.py",
        "--repo-root",
        str(claude_root / "plugins" / "charness"),
    )
    assert validate_exported_skills.returncode == 0, validate_exported_skills.stderr

    plugin_root = claude_root / "plugins" / "charness"
    for target in re.findall(r"\[[^\]]+\]\((\./[^)]+)\)", exported_readme_text):
        if target.startswith(
            (
                "./skills/",
                "./support/",
                "./integrations/",
                "./profiles/",
                "./presets/",
                "./README.md",
            )
        ):
            assert (plugin_root / target.removeprefix("./").split("#", 1)[0]).exists(), target

    consumer_root = tmp_path / "consumer"
    consumer_root.mkdir()
    gather_resolve = run_script(
        str(
            claude_root
            / "plugins"
            / "charness"
            / "skills"
            / "gather"
            / "scripts"
            / "resolve_adapter.py"
        ),
        "--repo-root",
        str(consumer_root),
        cwd=ROOT,
    )
    assert gather_resolve.returncode == 0, gather_resolve.stderr


def test_export_plugin_allows_version_override(tmp_path: Path) -> None:
    output_root = tmp_path / "codex-export"
    result = run_loaded_script_main(
        "export_plugin.py",
        export_plugin_module,
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(output_root),
        "--version-override",
        "1.2.3",
        "--with-marketplace",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["version"] == "1.2.3"

    codex_manifest = output_root / "plugins" / "charness" / ".codex-plugin" / "plugin.json"
    codex_marketplace = output_root / ".agents" / "plugins" / "marketplace.json"
    assert json.loads(codex_manifest.read_text(encoding="utf-8"))["version"] == "1.2.3"
    assert (
        json.loads(codex_marketplace.read_text(encoding="utf-8"))["plugins"][0]["name"]
        == "charness"
    )

    shared_manifest = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))
    assert shared_manifest["version"] != "1.2.3"


def test_install_surface_names_the_parser_adapter_lib_loads_by_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`adapter_lib` loads `adapter_yaml_parse` BY PATH at module scope, so an installed
    plugin missing it fails at IMPORT of `adapter_lib` — earlier than the
    `adapter_yaml_render_lib` case beside it in the floor, which earned its entry for the
    same reason. The file joined the required list when the YAML dialect moved out of
    `adapter_lib` (`#673`'s length-cap split).

    Drives `validate_materialized_plugin_export` directly with recording collaborators rather
    than cloning a seeded repo, so it runs in the STANDING lane. The release-marked sibling
    below proves the same requirement end-to-end; this one is what the changed-line gate can
    see, and a requirement no standing test covers can be deleted with every gate green.

    The export byte comparison is covered by the release-marked end-to-end tests below.
    Patch it here so this standing test remains narrowly about the required parser file.
    """
    from scripts.plugin_export import validate_packaging_install_surface as surface

    required: list[str] = []
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / "packaging" / "charness.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(
        surface, "validate_materialized_plugin_export_matches_generated", lambda *_args: None
    )
    surface.validate_materialized_plugin_export(
        root,
        manifest,
        require_dir=lambda *_a: None,
        require_file=lambda path, _field: required.append(path.name),
        require_json_matches=lambda *_a: None,
        validate_relative_path=lambda value, _field: str(value),
    )
    assert "adapter_yaml_parse.py" in required, required
    # Its neighbour, so a regression that dropped BOTH still fails here.
    assert "adapter_lib.py" in required, required


@pytest.mark.release_only
def test_install_surface_requires_the_parser_adapter_lib_loads_by_path(
    tmp_path: Path, seeded_charness_git_repo: Path
) -> None:
    """`adapter_lib` loads `adapter_yaml_parse` BY PATH at module scope, so an installed
    plugin missing it fails at IMPORT of `adapter_lib` — earlier than the
    `adapter_yaml_render_lib` case beside it in the floor, which earned its entry for the
    same reason. The file joined the required list when the YAML dialect moved out of
    `adapter_lib` (`#673`'s length-cap split); without the entry the floor under-specifies a
    hard import dependency it is the only thing speaking about.
    """
    repo = make_clean_git_repo(tmp_path, seeded_charness_git_repo)
    (repo / "plugins" / "charness" / "scripts" / "adapters" / "adapter_yaml_parse.py").unlink()

    result = run_loaded_script_main(
        "validate_packaging.py",
        validate_packaging_module,
        "--repo-root",
        str(repo),
        "--validate-export",
    )
    assert result.returncode == 1
    assert "adapter_yaml_parse" in result.stderr
