from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.seeding_support import environment_with_path, write_json_executable
from tests.quality_gates.support import ROOT, run_script
from tests.script_main import load_script_module

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
issue_read = load_script_module(
    "issue_read_under_test",
    ROOT / "skills" / "public" / "issue" / "scripts" / "issue_read.py",
)


@pytest.mark.boundary_contract(
    reason="exact process exit-code contract: run_script must select the current interpreter when PATH shadows python"
)
def test_run_script_uses_current_python_when_path_shadows_python(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_python = bin_dir / "python3"
    fake_python.write_text("#!/usr/bin/env bash\nexit 88\n", encoding="utf-8")
    fake_python.chmod(0o755)
    script = tmp_path / "probe.py"
    script.write_text("print('current-python')\n", encoding="utf-8")

    result = run_script(
        str(script),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "current-python"


@pytest.mark.boundary_contract(
    reason="target spawns gh and this test observes the backend response contract"
)
def test_issue_read_fails_when_backend_omits_comments(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_json_executable(
        bin_dir / "gh",
        {"number": 42, "title": "Demo", "body": "Body", "state": "OPEN"},
        trigger="view",
    )

    result = run_script(
        SCRIPT,
        "read",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--repo-root",
        str(tmp_path),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
        real_process=True,
    )

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "comments list" in payload["error"]


def test_issue_read_reports_backend_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        issue_read,
        "_run_backend",
        lambda _argv: subprocess.CompletedProcess(["gh"], 2, "", "boom"),
    )

    with pytest.raises(RuntimeError, match="issue read failed"):
        issue_read.read_issue_with_comments("corca-ai/charness", 42)


def test_goal_run_read_requests_native_sub_issue_summary_only_for_default_gh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[list[str]] = []

    def fake_run(argv: list[str]) -> subprocess.CompletedProcess[str]:
        captured.append(argv)
        return subprocess.CompletedProcess(
            argv,
            0,
            '{"number":42,"title":"Demo","body":"Body","comments":[],"state":"OPEN",'
            '"url":"https://github.com/corca-ai/charness/issues/42",'
            '"subIssuesSummary":{"total":31,"completed":23,"percentCompleted":74}}',
            "",
        )

    monkeypatch.setattr(issue_read, "_run_backend", fake_run)

    result = issue_read.read_issue_with_comments(
        "corca-ai/charness",
        42,
        include_sub_issues_summary=True,
    )

    assert captured[0][-1] == issue_read.GOAL_RUN_READ_FIELDS
    assert issue_read.normalise_sub_issues_summary(result["issue"]) == {
        "total": 31,
        "completed": 23,
        "open": 8,
        "percent_completed": 74,
    }


def test_goal_run_summary_request_preserves_custom_backend_read_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[list[str]] = []

    def fake_run(argv: list[str]) -> subprocess.CompletedProcess[str]:
        captured.append(argv)
        return subprocess.CompletedProcess(
            argv,
            0,
            '{"number":42,"title":"Demo","body":"Body","comments":[],"state":"OPEN",'
            '"url":"https://github.com/corca-ai/charness/issues/42"}',
            "",
        )

    monkeypatch.setattr(issue_read, "_run_backend", fake_run)
    custom = {
        "id": "acme",
        "binary": "acme",
        "commands": {"view": ["view", "{repo}", "{number}", "{json_fields}"]},
    }

    issue_read.read_issue_with_comments(
        "corca-ai/charness",
        42,
        backend=custom,
        include_sub_issues_summary=True,
    )

    assert captured[0][-1] == issue_read.READ_FIELDS


def test_issue_read_reports_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        issue_read,
        "_run_backend",
        lambda _argv: subprocess.CompletedProcess(["gh"], 0, "{", ""),
    )

    with pytest.raises(RuntimeError, match="invalid JSON"):
        issue_read.read_issue_with_comments("corca-ai/charness", 42)


def test_issue_read_load_local_missing_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        issue_read._load_local.__globals__["importlib"].util,
        "spec_from_file_location",
        lambda *_args, **_kwargs: None,
    )

    with pytest.raises(ImportError, match="Unable to load"):
        issue_read._load_local("missing")


def test_issue_read_command_stops_on_invalid_adapter(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text(
        "version: 1\nissue_backend: broken\n", encoding="utf-8"
    )

    result = run_script(
        SCRIPT,
        "read",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
