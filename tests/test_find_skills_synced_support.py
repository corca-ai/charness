from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_list_capabilities_cross_links_materialized_support_and_discovery_stub(tmp_path: Path) -> None:
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
    (tmp_path / "skills" / "support" / "generated" / "demo-tool").mkdir(parents=True)
    (tmp_path / "skills" / "support" / "generated" / "demo-tool" / "SKILL.md").write_text("# demo tool\n", encoding="utf-8")
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "charness-discovery").mkdir(parents=True)
    (tmp_path / ".agents" / "charness-discovery" / "demo-tool.md").write_text("# demo-tool\n", encoding="utf-8")
    (tmp_path / ".agents" / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/find-skills",
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
    (tmp_path / "integrations" / "tools" / "demo-tool.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "demo-tool",
                "kind": "external_binary_with_skill",
                "display_name": "demo-tool",
                "summary": "Demo integration with synced support.",
                "upstream_repo": "example/demo-tool",
                "homepage": "https://example.com/demo-tool",
                "lifecycle": {
                    "install": {"mode": "manual", "install_url": "https://example.com/demo-tool/install"},
                    "update": {"mode": "manual"},
                },
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/demo-tool",
                    "ref": "main",
                },
                "intent_triggers": ["verify", "evaluate"],
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
            "id": "demo-tool",
            "kind": "external_binary_with_skill",
            "access_modes": ["binary", "degraded"],
            "support_state": "upstream-consumed",
            "support_skill_path": "skills/support/generated/demo-tool/SKILL.md",
            "discovery_stub_path": ".agents/charness-discovery/demo-tool.md",
            "capability_requirements": {},
            "intent_triggers": ["verify", "evaluate"],
            "config_layers": [],
            "readiness_checks": [],
            "supports_public_skills": [],
            "recommendation_role": None,
            "path": "integrations/tools/demo-tool.json",
            "source": "local-integration",
            "layer": "external integration",
        }
    ]
