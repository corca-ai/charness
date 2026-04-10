from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_list_capabilities_includes_integration_access_modes(tmp_path: Path) -> None:
    (tmp_path / "skills" / "public" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "public" / "demo" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: skill-outputs/find-skills",
                "preset_id: portable-defaults",
                "customized_from: portable-defaults",
                "official_skill_roots: []",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "integrations" / "tools").mkdir(parents=True)
    (tmp_path / "integrations" / "tools" / "example.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "example",
                "kind": "external_binary",
                "upstream_repo": "https://example.com/tool",
                "homepage": "https://example.com/tool",
                "lifecycle": {
                    "install": {"commands": ["tool install"], "notes": "Install the tool."},
                    "update": {"commands": ["tool update"], "notes": "Update the tool."},
                },
                "checks": {
                    "detect": {"commands": ["tool --version"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["tool health"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "binary", "degraded"],
                "capability_requirements": {
                    "grant_ids": ["github.repo.read"],
                    "permission_scopes": ["repo:read"],
                },
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "skills/public/find-skills/scripts/list_capabilities.py",
            "--repo-root",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["integrations"] == [
        {
            "id": "example",
            "kind": "external_binary",
            "access_modes": ["grant", "binary", "degraded"],
            "capability_requirements": {
                "grant_ids": ["github.repo.read"],
                "permission_scopes": ["repo:read"],
            },
            "path": "integrations/tools/example.json",
            "source": "local-integration",
            "layer": "external integration",
        }
    ]
