from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml

from tests.quality_gates.support import ROOT, run_script, write_issue_adapter_with_backend
from tests.quality_gates.seeding_support import load_module

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
ISSUE_TOOL_PATH = ROOT / SCRIPT


def _load_issue_tool():
    return load_module("issue_tool_under_test", ISSUE_TOOL_PATH)


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

    result = run_script(
        SCRIPT,
        "preflight",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["gh_found"] is True
    assert payload["ok"] is False
    assert payload["auth_status"]["exit_code"] == 1
    assert payload["selected_backend"]["id"] == "gh"
    assert payload["selected_backend"]["binary"] == "gh"
    # The deleted "found but not authenticated/healthy" text line, now a payload field.
    assert payload["preflight_status"] == "found-but-not-authenticated-or-unhealthy"


def test_issue_preflight_reports_backend_config_error(monkeypatch, capsys, tmp_path: Path) -> None:
    """The backend-probe failure the deleted text renderer used to print alone.

    That branch was the only channel carrying WHICH failure happened; it is now
    `error` plus `preflight_status` in the one YAML payload, so this reads the
    payload rather than a human line. Parsed rather than substring-matched because
    YAML folds a long scalar across lines.
    """
    issue_tool = _load_issue_tool()
    monkeypatch.setattr(
        issue_tool,
        "_resolve_backend",
        lambda _repo_root: {
            "adapter_ok": True,
            "adapter": {"valid": True},
            "backend": {"commands": None},
        },
    )

    code = issue_tool.command_preflight(argparse.Namespace(repo_root=tmp_path))

    assert code == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["ok"] is False
    assert "issue_backend produced no binary" in payload["error"]
    assert payload["preflight_status"] == "backend-probe-failed"


def test_issue_preflight_resolves_adapter_backend_when_gh_absent(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "acme"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "if [[ \"$1\" == \"--version\" ]]; then",
                "  echo 'acme 0.0.1'",
                "  exit 0",
                "fi",
                "exit 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")

    result = run_script(
        SCRIPT,
        "preflight",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["preflight_status"] == "ready"
    backend = payload["selected_backend"]
    assert backend["id"] == "acme-github"
    assert backend["binary"] == "acme"
    assert backend["found"] is True
    assert backend["commands"]["create"][0] == "github"
    assert "gh_found" not in payload


def test_issue_preflight_resolves_adapter_from_process_cwd_when_repo_root_omitted(
    tmp_path: Path,
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "acme"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "if [[ \"$1\" == \"--version\" ]]; then echo 'acme 0.0.1'; exit 0; fi",
                "exit 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")

    result = run_script(
        str(ROOT / SCRIPT),
        "preflight",
        cwd=tmp_path,
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["adapter"]["found"] is True, payload
    assert payload["adapter"]["path"] == str(tmp_path / ".agents" / "issue-adapter.yaml")
    assert payload["selected_backend"]["id"] == "acme-github"


def test_issue_preflight_reports_missing_backend_binary_with_explicit_error(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")

    result = run_script(
        SCRIPT,
        "preflight",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["selected_backend"]["id"] == "acme-github"
    assert payload["selected_backend"]["found"] is False
    assert "acme" in payload["error"]
    # The deleted "backend binary missing" text line, now a payload field.
    assert payload["preflight_status"] == "backend-binary-missing"


def test_issue_preflight_rejects_unhealthy_non_gh_version_probe(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "acme"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == \"--version\" ]]; then echo unhealthy >&2; exit 3; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")

    result = run_script(
        SCRIPT,
        "preflight",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["selected_backend"]["version"]["exit_code"] == 3
    assert payload["preflight_status"] == "found-but-not-authenticated-or-unhealthy"
