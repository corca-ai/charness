"""Requested-review gate policy tests for release publication.

This module owns the requested-review configuration contract—unavailable,
waived, advisory-only, and blocking outcomes—so it stays distinct from the
release mutation and post-create verification scenarios.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from .release_publish_fixtures import _run_review_gate
from .seeding_support import write_release_adapter
from .test_release_publish import (
    _release_env,
    _run_publish_patch,
    _seed_publish_release_repo,
)

pytestmark = pytest.mark.boundary_contract(
    reason="exercise the exported release publish entrypoint with its real git and GitHub-backed topology"
)


def test_requested_review_gate_blocks_unavailable_release_record(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(repo, language=None)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- requested review unavailable: missing executor_variants\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo)

    assert result.returncode == 1
    assert "requested review unavailable" in result.stdout


def test_requested_review_gate_allows_explicit_waiver(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(repo, language=None)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "\n".join(
            [
                "# Release Surface Check",
                "",
                "- requested review unavailable: external provider outage",
                "- review waiver: maintainer accepted this release without that requested gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "waived"
    assert payload["unavailable_hits"]
    assert payload["waiver_hits"]


def test_requested_review_gate_warns_when_commands_are_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(repo, ["requested_review_commands: []"], language=None)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- Release proof complete.\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "ok"
    assert payload["configuration_status"] == "not_configured"
    assert "requested_review_commands is empty" in payload["warnings"][0]

    plain = _run_review_gate(repo)
    assert plain.returncode == 0, plain.stderr
    assert "WARNING: requested_review_commands is empty" in plain.stdout
    assert "configuration status: not_configured" in plain.stdout


def test_requested_review_gate_honors_advisory_only_policy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(
        repo,
        ["requested_review_commands: []", "requested_review_policy: advisory-only"],
        language=None,
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- Release proof complete.\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["configuration_status"] == "advisory_only"
    assert payload["warnings"] == []

    plain = _run_review_gate(repo)
    assert plain.returncode == 0, plain.stderr
    assert "configuration status: advisory_only" in plain.stdout


def test_requested_review_gate_blocks_failed_command_under_advisory_only_policy(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(
        repo,
        [
            "requested_review_policy: advisory-only",
            "requested_review_commands:",
            "- \"bash -c 'echo review failed >&2; exit 1'\"",
        ],
        language=None,
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- Release proof complete.\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["configuration_status"] == "configured"
    assert payload["requested_review_policy"] == "advisory-only"
    assert "requested review command failed" in payload["blockers"][0]


@pytest.mark.release_only
def test_publish_release_blocks_failed_requested_review_command(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nrequested_review_commands:\n- \"bash -c 'echo review unavailable >&2; exit 1'\"\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", ".agents/release-adapter.yaml"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Configure requested review gate"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 1
    assert "requested release review gate blocked publish" in result.stderr
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)
