from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _skill(path: Path, description: str) -> None:
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text(
        "\n".join(["---", f"name: {path.name}", f'description: "{description}"', "---", ""]) + "\n",
        encoding="utf-8",
    )


def test_list_capabilities_prefers_local_skill_over_trusted_duplicate(tmp_path: Path) -> None:
    _skill(tmp_path / "skills" / "public" / "demo", "Public demo.")
    _skill(tmp_path / "vendor" / "trusted-skills" / "demo", "Trusted demo.")
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/find-skills",
                "trusted_skill_roots:",
                "- vendor/trusted-skills",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", "skills/public/find-skills/scripts/list_capabilities.py", "--repo-root", str(tmp_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert [entry["id"] for entry in payload["public_skills"]] == ["demo"]
    assert payload["trusted_skills"] == []


def test_list_capabilities_dedupes_trusted_duplicate_ids(tmp_path: Path) -> None:
    _skill(tmp_path / "vendor" / "a" / "demo", "Trusted demo A.")
    _skill(tmp_path / "vendor" / "b" / "demo", "Trusted demo B.")
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/find-skills",
                "trusted_skill_roots:",
                "- vendor/a",
                "- vendor/b",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", "skills/public/find-skills/scripts/list_capabilities.py", "--repo-root", str(tmp_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert [entry["id"] for entry in payload["trusted_skills"]] == ["demo"]
