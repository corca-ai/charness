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
