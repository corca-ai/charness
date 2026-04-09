from __future__ import annotations

import importlib.util
import json
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


def test_validate_profiles_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(ROOT))
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
                "bundles": {"public_skills": ["missing-skill"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing artifact `missing-skill`" in result.stderr


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
    assert "Ran 8 eval scenario(s)." in result.stdout


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
