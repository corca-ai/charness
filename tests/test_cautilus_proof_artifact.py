from __future__ import annotations

from pathlib import Path

from .test_quality_artifact import run_script


def seed_repo(tmp_path: Path, artifact_body: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "skills" / "public" / "impl").mkdir(parents=True)
    (repo / "charness-artifacts" / "cautilus").mkdir(parents=True)
    (repo / "skills" / "public" / "impl" / "SKILL.md").write_text("# Impl\n", encoding="utf-8")
    if artifact_body is not None:
        (repo / "charness-artifacts" / "cautilus" / "latest.md").write_text(artifact_body, encoding="utf-8")
    return repo


def test_validate_cautilus_proof_requires_artifact_for_prompt_changes(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    result = run_script(
        "scripts/validate-cautilus-proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
    )
    assert result.returncode == 1
    assert "require refreshing `charness-artifacts/cautilus/latest.md`" in result.stderr


def test_validate_cautilus_proof_requires_ab_compare_for_improve_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "- claim: `improve`",
                "",
                "## Validation Goal",
                "",
                "- goal: `improve`",
                "- reason: demo",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus instruction-surface test --repo-root .`",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate-cautilus-proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 1
    assert "`## A/B Compare` is required when `goal: improve`" in result.stderr


def test_validate_cautilus_proof_accepts_preserve_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "- claim: `preserve`",
                "",
                "## Validation Goal",
                "",
                "- goal: `preserve`",
                "- reason: demo",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus instruction-surface test --repo-root .`",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate-cautilus-proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 0, result.stderr
