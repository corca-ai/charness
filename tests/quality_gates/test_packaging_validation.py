from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .support import EVAL_REGISTRY, ROOT, run_script

REPO_COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    ".venv",
    "node_modules",
    "history",
)


def copy_repo_snapshot(repo: Path) -> None:
    shutil.copytree(ROOT, repo, ignore=REPO_COPY_IGNORE)


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
                "checked_in_source_path": "./plugins/demo",
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


def init_committed_repo(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed repo"], cwd=repo, check=True, capture_output=True, text=True)


def test_validate_packaging_rejects_checked_in_plugin_tree_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    copy_repo_snapshot(repo)
    readme_path = repo / "README.md"
    readme_path.write_text(readme_path.read_text(encoding="utf-8") + "\nDrift.\n", encoding="utf-8")

    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "checked-in plugin tree does not match the generated install surface" in result.stderr


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
                        "checked_in_source_path": "./plugins/demo",
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
    result = run_script("scripts/sync_root_plugin_manifests.py", "--repo-root", str(repo), "--package-id", "demo")
    assert result.returncode == 0, result.stderr
    assert (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").exists()
    assert (repo / ".claude-plugin" / "marketplace.json").exists()
    assert (repo / "plugins" / "demo" / ".codex-plugin" / "plugin.json").exists()
    assert (repo / ".agents" / "plugins" / "marketplace.json").exists()

    validate = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert validate.returncode == 0, validate.stderr


def test_validate_packaging_committed_accepts_clean_head(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    copy_repo_snapshot(repo)
    init_committed_repo(repo)

    result = run_script("scripts/validate-packaging-committed.py", "--repo-root", str(repo), cwd=repo)
    assert result.returncode == 0, result.stderr


def test_validate_packaging_committed_rejects_partial_commit_with_uncommitted_export(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    copy_repo_snapshot(repo)
    init_committed_repo(repo)

    source_skill = repo / "skills" / "public" / "create-cli" / "SKILL.md"
    source_skill.write_text(source_skill.read_text(encoding="utf-8") + "\nPartial commit sentinel.\n", encoding="utf-8")

    sync = run_script("scripts/sync_root_plugin_manifests.py", "--repo-root", str(repo), cwd=repo)
    assert sync.returncode == 0, sync.stderr

    subprocess.run(["git", "add", "skills/public/create-cli/SKILL.md"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Commit source without synced plugin export"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    worktree_validate = run_script("scripts/validate-packaging.py", "--repo-root", str(repo), cwd=repo)
    assert worktree_validate.returncode == 0, worktree_validate.stderr

    committed_validate = run_script("scripts/validate-packaging-committed.py", "--repo-root", str(repo), cwd=repo)
    assert committed_validate.returncode == 1
    assert "checked-in plugin tree does not match the generated install surface" in committed_validate.stderr
    assert "plugins/charness/skills/create-cli/SKILL.md" in committed_validate.stderr


def test_eval_registry_omits_redundant_current_repo_smokes() -> None:
    scenario_ids = EVAL_REGISTRY.scenario_ids()
    assert {"managed-cli-install", "packaging-valid", "packaging-export"}.isdisjoint(scenario_ids)


def test_validate_packaging_rejects_wrong_codex_manifest_path(tmp_path: Path) -> None:
    repo = make_demo_packaging_repo(tmp_path, codex_manifest_path="plugin.json")
    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert ".codex-plugin/plugin.json" in result.stderr


def test_validate_packaging_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    repo = make_demo_packaging_repo(tmp_path, include_unexpected_field=True)
    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


def test_validate_packaging_rejects_invalid_public_skill_policy_when_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    copy_repo_snapshot(repo)
    policy_path = repo / "docs" / "public-skill-validation.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["tiers"]["hitl-recommended"].remove("premortem")
    policy_path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "does not classify every public skill" in result.stderr


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
    exported_gather_skill = claude_root / "plugins" / "charness" / "skills" / "gather" / "SKILL.md"
    exported_support_skill = claude_root / "plugins" / "charness" / "support" / "gather-slack" / "SKILL.md"
    exported_agent_browser = claude_root / "plugins" / "charness" / "support" / "agent-browser" / "SKILL.md"
    exported_specdown = claude_root / "plugins" / "charness" / "support" / "specdown" / "SKILL.md"
    exported_helper_script = claude_root / "plugins" / "charness" / "scripts" / "adapter_lib.py"
    assert claude_manifest.is_file()
    assert exported_readme.is_file()
    assert exported_profiles.is_dir()
    assert exported_gather_skill.is_file()
    assert exported_support_skill.is_file()
    assert exported_agent_browser.is_file()
    assert exported_specdown.is_file()
    assert exported_helper_script.is_file()
    assert not (claude_root / "plugins" / "charness" / "skills" / "public").exists()
    assert not (claude_root / "plugins" / "charness" / "support" / "generated").exists()
    assert json.loads(claude_manifest.read_text(encoding="utf-8"))["repository"] == "https://github.com/corca-ai/charness"
    exported_readme_text = exported_readme.read_text(encoding="utf-8")
    assert exported_readme_text.startswith("<!--\ngenerated_file: true\n")
    assert "source_path: README.md" in exported_readme_text
    assert "sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root ." in exported_readme_text

    consumer_root = tmp_path / "consumer"
    consumer_root.mkdir()
    gather_resolve = run_script(
        str(claude_root / "plugins" / "charness" / "skills" / "gather" / "scripts" / "resolve_adapter.py"),
        "--repo-root",
        str(consumer_root),
        cwd=ROOT,
    )
    assert gather_resolve.returncode == 0, gather_resolve.stderr


def test_export_plugin_allows_version_override(tmp_path: Path) -> None:
    output_root = tmp_path / "codex-export"
    result = run_script(
        "scripts/export-plugin.py",
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
    payload = json.loads(result.stdout)
    assert payload["version"] == "1.2.3"

    codex_manifest = output_root / "plugins" / "charness" / ".codex-plugin" / "plugin.json"
    codex_marketplace = output_root / ".agents" / "plugins" / "marketplace.json"
    assert json.loads(codex_manifest.read_text(encoding="utf-8"))["version"] == "1.2.3"
    assert json.loads(codex_marketplace.read_text(encoding="utf-8"))["plugins"][0]["name"] == "charness"

    shared_manifest = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))
    assert shared_manifest["version"] != "1.2.3"
