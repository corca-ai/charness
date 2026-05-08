from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from tests.quality_gates.support import ROOT, run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def test_issue_target_uses_default_org_for_bare_repo(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path), "--target", "demo")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/demo"
    assert payload["target"]["source"] == "argument-default-org"


def test_issue_target_infers_current_repo_from_git_remote(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:corca-ai/charness.git"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/charness"
    assert payload["target"]["source"] == "git-remote:origin"


def test_issue_selector_parses_single_and_range_without_github() -> None:
    single = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "17")
    ranged = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "17-19")

    assert single.returncode == 0, single.stderr
    assert ranged.returncode == 0, ranged.stderr
    assert json.loads(single.stdout)["numbers"] == [17]
    assert json.loads(ranged.stdout)["numbers"] == [17, 18, 19]


def test_issue_resolve_invocation_treats_single_number_as_selector(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-invocation", "--repo-root", str(tmp_path), "--", "120")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == f"corca-ai/{tmp_path.name}"
    assert payload["selector"] == "120"
    assert payload["numbers"] == [120]
    assert payload["selector_source"] == "argument"


def test_issue_resolve_invocation_accepts_repo_plus_selector(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-invocation", "--repo-root", str(tmp_path), "--", "ceal", "120")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/ceal"
    assert payload["selector"] == "120"
    assert payload["numbers"] == [120]


def test_issue_target_uses_adapter_default_repo_without_remote(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text(
        "\n".join(["version: 1", "default_org: corca-ai", "default_repo: ceal", "remote_name: origin", ""]),
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/ceal"
    assert payload["target"]["source"] == "adapter-default-repo-default-org"


def test_issue_preflight_fails_when_gh_auth_fails(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "if [[ \"$1 $2\" == \"auth status\" ]]; then",
                "  echo 'not logged in' >&2",
                "  exit 1",
                "fi",
                "exit 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)

    result = run_script(SCRIPT, "preflight", "--json", env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"})

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["gh_found"] is True
    assert payload["ok"] is False
    assert payload["auth_status"]["exit_code"] == 1


def test_issue_skill_records_github_sot_for_omitted_selector() -> None:
    skill_text = (ROOT / "skills" / "public" / "issue" / "SKILL.md").read_text(encoding="utf-8")
    resolve_flow = (ROOT / "skills" / "public" / "issue" / "references" / "resolve-flow.md").read_text(
        encoding="utf-8"
    )

    assert "GitHub is the source of truth" in skill_text
    assert "It must not use the current session's last created issue" in skill_text
    assert "omitted selector means newest open GitHub issue" in resolve_flow
