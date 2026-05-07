from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIST_CAPABILITIES_CMD = ("python3", "skills/public/find-skills/scripts/list_capabilities.py")


def _run_list_capabilities(repo: Path, *args: str) -> dict[str, object]:
    result = subprocess.run(
        [*LIST_CAPABILITIES_CMD, "--repo-root", str(repo), *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


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


def _write_specdown_surface(root: Path) -> None:
    support = root / "skills" / "support" / "specdown"
    support.mkdir(parents=True)
    (support / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: specdown",
                (
                    'description: "Write executable specs. Use for `*.spec.md`, '
                    '`docs/specs`, `run:shell`, `check:jq`, reports, and focused iteration."'
                ),
                "---",
                "",
                "# Specdown",
                "",
                "Key references: `syntax.md`, `best-practices.md`, `cli.md`, `report.md`, `config.md`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for name in ("syntax.md", "best-practices.md", "cli.md", "report.md", "config.md"):
        (support / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "integrations" / "tools").mkdir(parents=True)
    (root / "integrations" / "tools" / "specdown.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "specdown",
                "kind": "external_binary",
                "display_name": "specdown",
                "summary": "Executable specification runner.",
                "upstream_repo": "corca-ai/specdown",
                "homepage": "https://github.com/corca-ai/specdown",
                "lifecycle": {
                    "install": {
                        "mode": "manual",
                        "docs_url": "https://github.com/corca-ai/specdown",
                        "notes": ["Install specdown."],
                    },
                    "update": {
                        "mode": "manual",
                        "docs_url": "https://github.com/corca-ai/specdown/releases",
                        "notes": ["Update specdown."],
                    },
                },
                "checks": {
                    "detect": {"commands": ["specdown version"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["specdown run -help"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary", "degraded"],
                "intent_triggers": ["docs/specs", ".spec.md", "run:shell", "check:jq", "report.json"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_find_skills_adapter(root)


def test_list_capabilities_recommends_support_skill_from_task_text(tmp_path: Path) -> None:
    _write_specdown_surface(tmp_path)

    task = "Please edit docs/specs/user/foo.spec.md and add a check:jq assertion without a full specdown run."
    payload = _run_list_capabilities(tmp_path, "--recommend-for-task", task)

    assert payload["support_recommendation_query"] == {"mode": "task_text", "task_text": task}
    assert payload["support_skill_recommendations"] == [
        {
            "id": "specdown",
            "layer": "support skill",
            "path": "skills/support/specdown/SKILL.md",
            "summary": "Write executable specs. Use for `*.spec.md`, `docs/specs`, `run:shell`, `check:jq`, reports, and focused iteration.",
            "matched_triggers": ["specdown", "docs/specs", ".spec.md", "check:jq"],
            "referenced_paths": [
                "skills/support/specdown/syntax.md",
                "skills/support/specdown/best-practices.md",
                "skills/support/specdown/cli.md",
                "skills/support/specdown/report.md",
                "skills/support/specdown/config.md",
            ],
            "next_step": "Read `skills/support/specdown/SKILL.md` before modifying or running this support-backed surface.",
        }
    ]
    artifact_json = json.loads((tmp_path / "charness-artifacts" / "find-skills" / "latest.json").read_text(encoding="utf-8"))
    assert artifact_json["inventory"]["support_skill_recommendations"] == []
    assert artifact_json["inventory"]["support_recommendation_query"] is None


def test_list_capabilities_does_not_recommend_specdown_from_weak_task_text(tmp_path: Path) -> None:
    _write_specdown_surface(tmp_path)

    payload = _run_list_capabilities(
        tmp_path,
        "--recommend-for-task",
        "Please inspect the report.json and doctest output emitted by the generic data export job.",
    )

    assert payload["support_skill_recommendations"] == []
