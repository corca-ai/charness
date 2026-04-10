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
                    "env_vars": ["GITHUB_TOKEN"],
                    "permission_scopes": ["repo:read"],
                },
                "config_layers": [
                    {
                        "layer_id": "github-grant",
                        "layer_type": "grant",
                        "summary": "Use a host-provided GitHub read grant first.",
                    },
                    {
                        "layer_id": "github-cli",
                        "layer_type": "authenticated-binary",
                        "summary": "Reuse authenticated gh CLI state when available.",
                    },
                    {
                        "layer_id": "github-env",
                        "layer_type": "env",
                        "summary": "Fallback to GITHUB_TOKEN in ordinary local setups.",
                    },
                ],
                "readiness_checks": [
                    {
                        "check_id": "github-auth",
                        "summary": "GitHub auth is configured.",
                        "commands": ["gh auth status"],
                        "success_criteria": ["exit_code:0"],
                    }
                ],
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
                "env_vars": ["GITHUB_TOKEN"],
                "permission_scopes": ["repo:read"],
            },
            "config_layers": [
                {
                    "layer_id": "github-grant",
                    "layer_type": "grant",
                    "summary": "Use a host-provided GitHub read grant first.",
                },
                {
                    "layer_id": "github-cli",
                    "layer_type": "authenticated-binary",
                    "summary": "Reuse authenticated gh CLI state when available.",
                },
                {
                    "layer_id": "github-env",
                    "layer_type": "env",
                    "summary": "Fallback to GITHUB_TOKEN in ordinary local setups.",
                },
            ],
            "readiness_checks": [
                {
                    "check_id": "github-auth",
                    "summary": "GitHub auth is configured.",
                }
            ],
            "path": "integrations/tools/example.json",
            "source": "local-integration",
            "layer": "external integration",
        }
    ]


def test_list_capabilities_includes_support_capabilities(tmp_path: Path) -> None:
    (tmp_path / "skills" / "public" / "gather").mkdir(parents=True)
    (tmp_path / "skills" / "public" / "gather" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: gather",
                'description: "Gather skill."',
                "---",
                "",
                "# Gather",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "skills" / "support" / "gather-slack").mkdir(parents=True)
    (tmp_path / "skills" / "support" / "gather-slack" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: gather-slack",
                'description: "Slack support."',
                "---",
                "",
                "# Gather Slack",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "skills" / "support" / "capability.schema.json").write_text(
        (REPO_ROOT / "skills" / "support" / "capability.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "skills" / "support" / "gather-slack" / "capability.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "capability_id": "gather-slack",
                "kind": "support_runtime",
                "display_name": "Slack gather",
                "summary": "Support-owned Slack runtime.",
                "support_skill_path": "skills/support/gather-slack/SKILL.md",
                "supports_public_skills": ["gather"],
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "capability_requirements": {
                    "grant_ids": ["slack.history"],
                    "env_vars": ["SLACK_BOT_TOKEN"],
                },
                "config_layers": [
                    {
                        "layer_id": "slack-grant",
                        "layer_type": "grant",
                        "summary": "Prefer runtime grant first.",
                    },
                    {
                        "layer_id": "slack-env",
                        "layer_type": "env",
                        "summary": "Fallback to env.",
                    },
                ],
                "readiness_checks": [
                    {
                        "check_id": "slack-ready",
                        "summary": "Slack runtime is ready.",
                        "commands": ["true"],
                        "success_criteria": ["exit_code:0"],
                    }
                ],
                "version_expectation": {"policy": "advisory", "constraint": "local"},
            },
            ensure_ascii=False,
            indent=2,
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
    assert payload["support_capabilities"] == [
        {
            "id": "gather-slack",
            "kind": "support_runtime",
            "access_modes": ["grant", "env", "degraded"],
            "capability_requirements": {
                "grant_ids": ["slack.history"],
                "env_vars": ["SLACK_BOT_TOKEN"],
            },
            "config_layers": [
                {
                    "layer_id": "slack-grant",
                    "layer_type": "grant",
                    "summary": "Prefer runtime grant first.",
                },
                {
                    "layer_id": "slack-env",
                    "layer_type": "env",
                    "summary": "Fallback to env.",
                },
            ],
            "readiness_checks": [
                {
                    "check_id": "slack-ready",
                    "summary": "Slack runtime is ready.",
                }
            ],
            "path": "skills/support/gather-slack/capability.json",
            "support_skill_path": "skills/support/gather-slack/SKILL.md",
            "supports_public_skills": ["gather"],
            "source": "local-support-capability",
            "layer": "support capability",
        }
    ]
