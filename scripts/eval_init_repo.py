from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable


def run_init_repo_inspect_states(
    root: Path,
    *,
    run_command: Callable[..., object],
    expect_success: Callable[..., None],
    error_type: type[Exception],
) -> None:
    inspect_script = root / "skills" / "public" / "init-repo" / "scripts" / "inspect_repo.py"

    with tempfile.TemporaryDirectory(prefix="charness-eval-init-repo-greenfield-") as tmpdir:
        tmp = Path(tmpdir)
        greenfield_result = run_command(["python3", str(inspect_script), "--repo-root", str(tmp)], cwd=root)
        expect_success(greenfield_result, "init-repo greenfield inspect")
        greenfield = json.loads(greenfield_result.stdout)
        if greenfield.get("repo_mode") != "GREENFIELD":
            raise error_type(f"init-repo greenfield inspect: unexpected repo_mode {greenfield.get('repo_mode')!r}")
        if greenfield.get("agent_docs", {}).get("recommended_action") != "create_agents_and_symlink":
            raise error_type(
                "init-repo greenfield inspect: unexpected agent-doc action "
                f"{greenfield.get('agent_docs', {}).get('recommended_action')!r}"
            )

    with tempfile.TemporaryDirectory(prefix="charness-eval-init-repo-partial-") as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "docs").mkdir(parents=True)
        (tmp / "README.md").write_text("# Demo\n", encoding="utf-8")
        (tmp / "CLAUDE.md").write_text("project-specific instructions\n", encoding="utf-8")
        partial_result = run_command(["python3", str(inspect_script), "--repo-root", str(tmp)], cwd=root)
        expect_success(partial_result, "init-repo partial inspect")
        partial = json.loads(partial_result.stdout)
        if partial.get("repo_mode") != "PARTIAL":
            raise error_type(f"init-repo partial inspect: unexpected repo_mode {partial.get('repo_mode')!r}")
        if partial.get("agent_docs", {}).get("recommended_action") != "ask_to_promote_claude_into_agents":
            raise error_type(
                "init-repo partial inspect: unexpected agent-doc action "
                f"{partial.get('agent_docs', {}).get('recommended_action')!r}"
            )
        if partial.get("agent_docs", {}).get("claude_has_text") is not True:
            raise error_type("init-repo partial inspect: expected CLAUDE.md content to be detected")

    with tempfile.TemporaryDirectory(prefix="charness-eval-init-repo-targeted-") as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "docs").mkdir(parents=True)
        (tmp / "README.md").write_text("# Demo\n", encoding="utf-8")
        (tmp / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
        (tmp / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
        targeted_result = run_command(["python3", str(inspect_script), "--repo-root", str(tmp)], cwd=root)
        expect_success(targeted_result, "init-repo targeted partial inspect")
        targeted = json.loads(targeted_result.stdout)
        if targeted.get("repo_mode") != "PARTIAL":
            raise error_type(f"init-repo targeted partial inspect: unexpected repo_mode {targeted.get('repo_mode')!r}")
        if targeted.get("partial_kind") != "targeted_missing_surface":
            raise error_type(
                "init-repo targeted partial inspect: unexpected partial_kind "
                f"{targeted.get('partial_kind')!r}"
            )
        if targeted.get("missing_surfaces") != ["operator_acceptance"]:
            raise error_type(
                "init-repo targeted partial inspect: unexpected missing_surfaces "
                f"{targeted.get('missing_surfaces')!r}"
            )


def run_init_repo_operator_acceptance_synthesis(
    root: Path,
    *,
    run_command: Callable[..., object],
    expect_success: Callable[..., None],
    error_type: type[Exception],
) -> None:
    with tempfile.TemporaryDirectory(prefix="charness-eval-init-repo-acceptance-") as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "docs" / "specs").mkdir(parents=True)
        (tmp / "scripts").mkdir(parents=True)
        (tmp / "README.md").write_text("# Demo\n", encoding="utf-8")
        (tmp / "docs" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
        (tmp / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
        (tmp / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
        (tmp / "docs" / "specs" / "smoke.spec.md").write_text(
            "\n".join(
                [
                    "# Demo Spec",
                    "",
                    "## CLI Smoke",
                    "",
                    "### Functional Check",
                    "",
                    "```bash",
                    "./scripts/run-quality.sh",
                    "```",
                    "",
                    "## Hosted Publish",
                    "",
                    "### Functional Check",
                    "",
                    "```bash",
                    "gh workflow run release.yml",
                    "```",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (tmp / "scripts" / "run-quality.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

        result = run_command(
            [
                "python3",
                "skills/public/init-repo/scripts/synthesize_operator_acceptance.py",
                "--repo-root",
                str(tmp),
                "--json",
            ],
            cwd=root,
        )
        expect_success(result, "init-repo operator acceptance synthesis")
        payload = json.loads(result.stdout)
        cheap = payload["acceptance_buckets"]["cheap_first"]
        external = payload["acceptance_buckets"]["external_or_costly"]
        human = payload["acceptance_buckets"]["human_judgment"]
        if len(cheap) != 1 or cheap[0]["commands"] != "./scripts/run-quality.sh":
            raise error_type(f"init-repo operator acceptance synthesis: unexpected cheap bucket {cheap!r}")
        if len(external) != 1 or "gh workflow run" not in external[0]["commands"]:
            raise error_type(f"init-repo operator acceptance synthesis: unexpected external bucket {external!r}")
        if not human:
            raise error_type(f"init-repo operator acceptance synthesis: expected human review items {payload!r}")
        if "## Environment Prerequisites" not in payload["markdown"]:
            raise error_type(f"init-repo operator acceptance synthesis: missing prerequisites section {payload!r}")
