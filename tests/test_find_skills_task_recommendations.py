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


def _write_browserlike_surface(root: Path, *, populate_intent_triggers: bool) -> None:
    support = root / "skills" / "support" / "browserlike"
    support.mkdir(parents=True)
    (support / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: browserlike",
                (
                    'description: "Use browserlike CLI for browser automation, JS-rendered pages, '
                    'and interactive browser debugging."'
                ),
                "---",
                "",
                "# Browserlike",
                "",
                "Key references: `runtime.md`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (support / "runtime.md").write_text("# runtime.md\n", encoding="utf-8")
    (root / "integrations" / "tools").mkdir(parents=True)
    manifest: dict[str, object] = {
        "schema_version": "1",
        "tool_id": "browserlike",
        "kind": "external_binary_with_skill",
        "display_name": "browserlike",
        "summary": "Browser automation CLI for JS-rendered pages.",
        "upstream_repo": "example/browserlike",
        "homepage": "https://example.com/browserlike",
        "lifecycle": {
            "install": {
                "mode": "manual",
                "docs_url": "https://example.com/browserlike",
                "install_url": "https://example.com/browserlike#installation",
                "notes": ["Install browserlike."],
            },
            "update": {
                "mode": "manual",
                "docs_url": "https://example.com/browserlike",
                "notes": ["Update browserlike."],
            },
        },
        "checks": {
            "detect": {"commands": ["browserlike --version"], "success_criteria": ["exit_code:0"]},
            "healthcheck": {"commands": ["browserlike --version"], "success_criteria": ["exit_code:0"]},
        },
        "access_modes": ["binary", "degraded"],
        "support_skill_source": {"source_type": "upstream_repo", "path": "skills/browserlike"},
        "version_expectation": {"policy": "advisory", "constraint": "latest"},
    }
    if populate_intent_triggers:
        manifest["intent_triggers"] = [
            "browser automation",
            "headless browser",
            "playwright",
            "js-rendered",
        ]
    (root / "integrations" / "tools" / "browserlike.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_find_skills_adapter(root)


def _write_cautilus_integration(root: Path) -> None:
    (root / "integrations" / "tools").mkdir(parents=True)
    (root / "integrations" / "tools" / "cautilus.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "cautilus",
                "kind": "external_binary_with_skill",
                "display_name": "cautilus",
                "summary": "Standalone evaluation engine.",
                "upstream_repo": "corca-ai/cautilus",
                "homepage": "https://github.com/corca-ai/cautilus",
                "lifecycle": {
                    "install": {
                        "mode": "manual",
                        "docs_url": "https://github.com/corca-ai/cautilus",
                        "notes": ["Install cautilus."],
                    },
                    "update": {
                        "mode": "manual",
                        "docs_url": "https://github.com/corca-ai/cautilus/releases",
                        "notes": ["Update cautilus."],
                    },
                },
                "checks": {
                    "detect": {
                        "commands": ["no-such-cautilus-test-binary --version"],
                        "success_criteria": ["exit_code:0"],
                    },
                    "healthcheck": {
                        "commands": ["no-such-cautilus-test-binary doctor --help"],
                        "success_criteria": ["exit_code:0"],
                    },
                },
                "access_modes": ["binary", "degraded"],
                "supports_public_skills": ["impl", "quality", "spec"],
                "intent_triggers": [
                    "evaluator-backed behavior review",
                    "behavior evaluation",
                    "cautilus eval",
                ],
                "recommendation_role": "validation",
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_find_skills_adapter(root)


def test_recommend_for_task_surfaces_support_skill_via_intent_triggers(tmp_path: Path) -> None:
    _write_browserlike_surface(tmp_path, populate_intent_triggers=True)

    payload = _run_list_capabilities(tmp_path, "--recommend-for-task", "browser automation")

    matched_ids = [entry["id"] for entry in payload["support_skill_recommendations"]]
    assert matched_ids == ["browserlike"]
    assert payload["support_recommendation_note"] is None


def test_recommend_for_task_surfaces_named_validation_integration(tmp_path: Path) -> None:
    _write_cautilus_integration(tmp_path)

    task = "Use Cautilus to validate that Ceal Slack write requests choose the portable ceal slack CLI"
    payload = _run_list_capabilities(tmp_path, "--recommend-for-task", task)

    assert payload["tool_recommendation_query"] == {
        "mode": "task_text",
        "task_text": task,
        "next_skill_id": None,
        "only_blocking": False,
    }
    assert payload["support_skill_recommendations"] == []
    assert payload["support_recommendation_note"] is None
    recommendations = payload["tool_recommendations"]
    assert len(recommendations) == 1
    cautilus = recommendations[0]
    assert cautilus["tool_id"] == "cautilus"
    assert cautilus["recommendation_role"] == "validation"
    assert cautilus["next_skill_id"] == "impl"
    assert cautilus["recommendation_status"] == "install-needed"
    assert cautilus["matched_triggers"] == ["cautilus"]
    assert cautilus["verify_command"] == "python3 scripts/doctor.py --repo-root . --json --tool-id cautilus"


def test_recommend_for_task_filters_named_integration_by_explicit_next_skill(tmp_path: Path) -> None:
    _write_cautilus_integration(tmp_path)

    payload = _run_list_capabilities(
        tmp_path,
        "--recommend-for-task",
        "Use Cautilus to validate the announcement draft.",
        "--next-skill-id",
        "announcement",
    )

    assert payload["tool_recommendations"] == []
    assert payload["tool_recommendation_query"]["next_skill_id"] == "announcement"


def test_recommend_for_task_note_points_validation_shape_to_role_query(tmp_path: Path) -> None:
    _write_cautilus_integration(tmp_path)

    payload = _run_list_capabilities(tmp_path, "--recommend-for-task", "Please validate this behavior more deeply.")

    assert payload["tool_recommendations"] == []
    note = payload["support_recommendation_note"]
    assert isinstance(note, str)
    assert "--recommendation-role validation --next-skill-id <skill-id>" in note


def test_recommend_for_task_surfaces_worktree_workflow(tmp_path: Path) -> None:
    _write_find_skills_adapter(tmp_path)

    payload = _run_list_capabilities(
        tmp_path,
        "--recommend-for-task",
        "Create a git worktree for a spec slice and prepare it before editing docs.",
    )

    assert payload["support_skill_recommendations"] == []
    assert payload["tool_recommendations"] == []
    assert payload["support_recommendation_note"] is None
    assert payload["workflow_recommendations"] == [
        {
            "id": "worktree-create",
            "layer": "workflow integration",
            "path": "docs/worktree-prepare.md",
            "summary": "Create and prepare git worktrees through the Charness worktree CLI.",
            "matched_triggers": ["worktree", "git worktree"],
            "next_step": "Use `charness worktree create --path <path> --branch <branch> --base <ref>` instead of raw `git worktree add`; add `--prepare` when the operator wants adapter-declared setup to run immediately.",
        }
    ]
    artifact_json = json.loads((tmp_path / "charness-artifacts" / "find-skills" / "latest.json").read_text(encoding="utf-8"))
    assert artifact_json["inventory"]["workflow_recommendations"] == []


def test_recommend_for_task_surfaces_worktree_cleanup_workflow(tmp_path: Path) -> None:
    _write_find_skills_adapter(tmp_path)

    payload = _run_list_capabilities(
        tmp_path,
        "--recommend-for-task",
        "Cleanup worktree after the feature branch was merged locally.",
    )

    assert payload["support_skill_recommendations"] == []
    assert payload["tool_recommendations"] == []
    assert payload["support_recommendation_note"] is None
    assert payload["workflow_recommendations"] == [
        {
            "id": "worktree-cleanup",
            "layer": "workflow integration",
            "path": "docs/worktree-prepare.md",
            "summary": "Safely remove finished git worktrees through the Charness worktree CLI.",
            "matched_triggers": ["cleanup worktree"],
            "next_step": "Use `charness worktree cleanup --path <worktree>` for a dry-run plan; add `--delete-merged-branch --yes` only after local branch containment is the intended cleanup policy.",
        }
    ]


def test_recommend_for_task_surfaces_worktree_cleanup_when_words_are_separated(tmp_path: Path) -> None:
    _write_find_skills_adapter(tmp_path)

    payload = _run_list_capabilities(
        tmp_path,
        "--recommend-for-task",
        "cleanup a stale git worktree safely",
    )

    assert [entry["id"] for entry in payload["workflow_recommendations"]] == ["worktree-cleanup"]
    cleanup = payload["workflow_recommendations"][0]
    assert cleanup["matched_triggers"] == ["cleanup+worktree"]
    assert "worktree cleanup --path" in cleanup["next_step"]


def test_recommend_for_task_emits_empty_result_hint_when_intent_triggers_absent(tmp_path: Path) -> None:
    _write_browserlike_surface(tmp_path, populate_intent_triggers=False)

    payload = _run_list_capabilities(tmp_path, "--recommend-for-task", "browser automation")

    assert payload["support_skill_recommendations"] == []
    note = payload["support_recommendation_note"]
    assert isinstance(note, str)
    assert "support skill(s) are available locally" in note
    assert "intent_triggers" in note


def test_recommend_for_task_note_absent_when_recommendation_query_absent(tmp_path: Path) -> None:
    _write_specdown_surface(tmp_path)

    payload = _run_list_capabilities(tmp_path)

    assert payload["support_recommendation_note"] is None
