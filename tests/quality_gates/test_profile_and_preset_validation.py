from __future__ import annotations

import json
from pathlib import Path

from .support import init_git_repo, run_script


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
    result = run_script("scripts/validate_profiles.py", "--repo-root", str(repo))
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
    result = run_script("scripts/validate_presets.py", "--repo-root", str(repo))
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
    result = run_script("scripts/validate_presets.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "product-slice presets must include an `## Exposure Contract` section" in result.stderr


def test_validate_presets_ignores_gitignored_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    presets_dir = repo / "presets"
    presets_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("presets/generated-*.md\n", encoding="utf-8")
    (presets_dir / "kept.md").write_text(
        "\n".join(
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
        ),
        encoding="utf-8",
    )
    (presets_dir / "generated-bad.md").write_text("# Missing frontmatter on ignored file.\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "presets/kept.md")

    result = run_script("scripts/validate_presets.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_sample_quality_presets_carry_concrete_lint_defaults() -> None:
    root = Path(__file__).resolve().parents[2]
    python_quality = (root / "presets" / "python-quality.md").read_text(encoding="utf-8")
    typescript_quality = (root / "presets" / "typescript-quality.md").read_text(encoding="utf-8")
    presets_readme = (root / "presets" / "README.md").read_text(encoding="utf-8")

    assert '`ruff check` with `E`, `F`, `I`, and `C90`' in python_quality
    assert '[tool.ruff.lint.mccabe] max-complexity = 15' in python_quality
    assert '`eslint` with a standing `complexity` rule' in typescript_quality
    assert 'complexity: ["error", 15]' in typescript_quality
    assert "including `eslint` + `complexity` and `tsc --noEmit` defaults" in presets_readme
    assert "including `ruff` + `C90` and one type-checker default" in presets_readme


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
    result = run_script("scripts/validate_profiles.py", "--repo-root", str(repo))
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
    result = run_script("scripts/validate_profiles.py", "--repo-root", str(repo))
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
    result = run_script("scripts/validate_profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


def test_validate_profiles_ignores_gitignored_profiles(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "handoff"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("profiles/generated-*.json\n", encoding="utf-8")
    (public_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n\n## References\n\n- `references/demo.md`\n",
        encoding="utf-8",
    )
    (public_skill_dir / "references").mkdir(parents=True)
    (public_skill_dir / "references" / "demo.md").write_text("# Demo\n", encoding="utf-8")
    (profiles_dir / "kept.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "kept",
                "display_name": "Kept",
                "purpose": "Test",
                "bundles": {"public_skills": ["handoff"]},
            }
        ),
        encoding="utf-8",
    )
    (profiles_dir / "generated-bad.json").write_text('{"profile_id":"generated-bad"}\n', encoding="utf-8")
    init_git_repo(
        repo,
        ".gitignore",
        "profiles/kept.json",
        "skills/public/handoff/SKILL.md",
        "skills/public/handoff/references/demo.md",
    )

    result = run_script("scripts/validate_profiles.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
def test_validate_adapters_ignores_gitignored_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    kept_dir = repo / "skills" / "public" / "kept" / "scripts"
    ignored_dir = repo / "skills" / "public" / "generated" / "scripts"
    kept_dir.mkdir(parents=True)
    ignored_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("skills/public/generated/\n", encoding="utf-8")
    (kept_dir / "resolve_adapter.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                'print(json.dumps({"valid": True, "artifact_filename": "latest.md", "artifact_path": "charness-artifacts/kept/latest.md"}))',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ignored_dir / "resolve_adapter.py").write_text("#!/usr/bin/env python3\nraise SystemExit(1)\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "skills/public/kept/scripts/resolve_adapter.py")

    result = run_script("scripts/validate_adapters.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_adapters_checks_named_cautilus_adapter_yaml(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapters_dir = repo / ".agents" / "cautilus-adapters"
    adapters_dir.mkdir(parents=True)
    (adapters_dir / "chatbot-proposals.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "evaluation_surfaces:",
                "  - chatbot proposals",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/validate_adapters.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
