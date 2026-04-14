from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_list_capabilities_surfaces_generated_support_skill_and_cross_links_integration(tmp_path: Path) -> None:
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
                "trusted_skill_roots: []",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "skills" / "support" / "generated" / "cautilus").mkdir(parents=True)
    (tmp_path / "skills" / "support" / "generated" / "cautilus" / "SKILL.md").write_text(
        "\n".join(["---", "name: cautilus", 'description: "Generated support."', "---", "", "# Cautilus"]) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "integrations" / "tools").mkdir(parents=True)
    (tmp_path / "integrations" / "tools" / "cautilus.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "cautilus",
                "kind": "external_binary_with_skill",
                "display_name": "cautilus",
                "upstream_repo": "corca-ai/cautilus",
                "homepage": "https://github.com/corca-ai/cautilus",
                "lifecycle": {
                    "install": {
                        "mode": "manual",
                        "docs_url": "https://github.com/corca-ai/cautilus",
                        "install_url": "https://github.com/corca-ai/cautilus/blob/main/install.md",
                    },
                    "update": {"mode": "manual", "docs_url": "https://github.com/corca-ai/cautilus/releases"},
                },
                "checks": {
                    "detect": {"commands": ["cautilus --version"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["cautilus doctor --help"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/cautilus",
                    "ref": "main",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
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
    assert payload["support_skills"] == [
        {
            "id": "cautilus",
            "name": "cautilus",
            "description": "Generated support.",
            "path": "skills/support/generated/cautilus/SKILL.md",
            "source": "synced-support",
            "layer": "synced support skill",
        }
    ]
    assert payload["integrations"] == [
        {
            "id": "cautilus",
            "kind": "external_binary_with_skill",
            "access_modes": ["binary", "degraded"],
            "support_state": "upstream-consumed",
            "support_skill_path": "skills/support/generated/cautilus/SKILL.md",
            "capability_requirements": {},
            "config_layers": [],
            "readiness_checks": [],
            "supports_public_skills": [],
            "recommendation_role": None,
            "path": "integrations/tools/cautilus.json",
            "source": "local-integration",
            "layer": "external integration",
        }
    ]
