from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_LIST_CAPABILITIES_CMD = ("python3", "plugins/charness/skills/find-skills/scripts/list_capabilities.py")


def _write_find_skills_adapter(root: Path) -> None:
    (root / ".agents").mkdir(parents=True)
    (root / ".agents" / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/find-skills",
                "trusted_skill_roots: []",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_skill(root: Path, skill_id: str, description: str, *, support_generated: bool = False) -> None:
    skill_dir = root / "skills" / ("support/generated" if support_generated else "public") / skill_id
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(["---", f"name: {skill_id}", f'description: "{description}"', "---", "", f"# {skill_id.title()}"]) + "\n",
        encoding="utf-8",
    )


def _run_plugin_list_capabilities(tmp_path: Path) -> dict[str, object]:
    result = subprocess.run(
        [*PLUGIN_LIST_CAPABILITIES_CMD, "--repo-root", str(tmp_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_plugin_export_prefers_repo_owned_skill_surface_for_source_repo(tmp_path: Path) -> None:
    _write_find_skills_adapter(tmp_path)
    _write_skill(tmp_path, "demo", "Demo skill.")
    _write_skill(tmp_path, "cautilus", "Synced support.", support_generated=True)

    payload = _run_plugin_list_capabilities(tmp_path)

    assert payload["artifacts"]["artifact_paths"] == [
        "charness-artifacts/find-skills/latest.md",
        "charness-artifacts/find-skills/latest.json",
    ]
    assert payload["artifacts"]["semantic_content_changed"] is True
    assert payload["artifacts"]["requires_repo_closeout"] is True
    assert payload["artifacts"]["commit_recommended"] is True
    assert payload["artifacts"]["closeout_reason"] == "canonical find-skills inventory changed"
    assert payload["public_skills"] == [
        {
            "id": "demo",
            "name": "demo",
            "description": "Demo skill.",
            "summary": "Demo skill.",
            "path": "skills/public/demo/SKILL.md",
            "skill_dir": "skills/public/demo",
            "canonical_path": "skills/public/demo/SKILL.md",
            "trigger_phrases": ["demo", "demo skill", "demo 스킬", "charness:demo"],
            "referenced_paths": [],
            "source": "local-public",
            "layer": "public skill",
        }
    ]
    assert payload["support_skills"] == [
        {
            "id": "cautilus",
            "name": "cautilus",
            "description": "Synced support.",
            "summary": "Synced support.",
            "path": "skills/support/generated/cautilus/SKILL.md",
            "skill_dir": "skills/support/generated/cautilus",
            "canonical_path": "skills/support/generated/cautilus/SKILL.md",
            "trigger_phrases": [
                "cautilus",
                "cautilus skill",
                "cautilus 스킬",
                "charness:cautilus",
                "support/cautilus",
                "cautilus support",
                "cautilus support skill",
                "cautilus helper",
            ],
            "referenced_paths": [],
            "source": "synced-support",
            "layer": "synced support skill",
        }
    ]
