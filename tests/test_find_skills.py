from __future__ import annotations

import json
import os
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
                "trusted_skill_roots: []",
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
                "display_name": "example",
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
            "supports_public_skills": [],
            "recommendation_role": None,
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
                "trusted_skill_roots: []",
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


def test_list_capabilities_can_emit_tool_recommendations_for_public_skill(tmp_path: Path) -> None:
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
    (tmp_path / "integrations" / "tools").mkdir(parents=True)
    (tmp_path / "bin").mkdir(parents=True)
    (tmp_path / "bin" / "gws").write_text(
        "\n".join(
            [
                "#!/bin/sh",
                "if [ \"$1\" = \"--version\" ]; then",
                "  echo 'gws 1.2.3'",
                "  exit 0",
                "fi",
                "if [ \"$1\" = \"auth\" ] && [ \"$2\" = \"--help\" ]; then",
                "  echo 'login'",
                "  exit 0",
                "fi",
                "if [ \"$1\" = \"auth\" ] && [ \"$2\" = \"status\" ]; then",
                "  exit 0",
                "fi",
                "exit 1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "bin" / "gws").chmod(0o755)
    (tmp_path / "integrations" / "tools" / "gws-cli.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "gws-cli",
                "kind": "external_binary",
                "display_name": "Google Workspace CLI (gws)",
                "summary": "Private Google Workspace gather provider.",
                "upstream_repo": "googleworkspace/cli",
                "homepage": "https://github.com/googleworkspace/cli",
                "lifecycle": {
                    "install": {"mode": "manual", "docs_url": "https://github.com/googleworkspace/cli", "notes": ["Install gws."]},
                    "update": {"mode": "manual", "docs_url": "https://github.com/googleworkspace/cli/releases", "notes": ["Update gws."]},
                },
                "checks": {
                    "detect": {"commands": ["gws --version"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["gws auth --help"], "success_criteria": ["exit_code:0", "stdout_contains:login"]},
                },
                "access_modes": ["binary", "degraded"],
                "readiness_checks": [
                    {
                        "check_id": "gws-auth-ready",
                        "summary": "Google Workspace auth is ready.",
                        "commands": ["gws auth status"],
                        "success_criteria": ["exit_code:0"],
                    }
                ],
                "version_expectation": {"policy": "advisory", "constraint": "latest", "detected_by": "stdout"},
                "supports_public_skills": ["gather"],
                "recommendation_role": "runtime",
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
            "--recommend-for-skill",
            "gather",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{tmp_path / 'bin'}:{os.environ.get('PATH', '')}"},
    )

    payload = json.loads(result.stdout)
    assert payload["tool_recommendations"] == [
        {
            "tool_id": "gws-cli",
            "display_name": "Google Workspace CLI (gws)",
            "kind": "external_binary",
            "summary": "Private Google Workspace gather provider.",
            "why_recommended": "Recommended because `gather` can use this tool as a supported runtime path.",
            "supports_public_skills": ["gather"],
            "recommendation_role": "runtime",
            "recommendation_status": "ready",
            "doctor_status": "ok",
            "support_state": "integration-only",
            "support_sync_status": "not-tracked",
            "detect_ok": True,
            "healthcheck_ok": True,
            "readiness_ok": True,
            "install": {
                "mode": "manual",
                "commands": [],
                "docs_url": "https://github.com/googleworkspace/cli",
                "install_url": None,
                "notes": ["Install gws."],
            },
            "verify_command": "python3 scripts/doctor.py --repo-root . --json --tool-id gws-cli",
            "next_skill_id": "gather",
        }
    ]
