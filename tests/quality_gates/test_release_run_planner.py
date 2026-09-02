from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml

from tests.script_main import run_loaded_script_main

from .release_publish_fixtures import (
    PUBLISH_SCRIPT,
    REPO_ROOT,
    _seed_publish_release_repo,
)
from .seeding_support import load_module

PLANNER = "skills/public/release/scripts/plan_release_run.py"
pytestmark = pytest.mark.boundary_contract(
    reason="observe the release publish preparation's real git and external release child commands"
)


def _load_script_module(name: str, rel_path: str):
    return load_module(name, REPO_ROOT / rel_path)


_PLANNER = _load_script_module("plan_release_run_test_module", PLANNER)
_BUMP = _load_script_module(
    "bump_version_test_module",
    "skills/public/release/scripts/bump_version.py",
)
_PACKETS = _load_script_module(
    "plan_release_run_packets_test_module",
    "skills/public/release/scripts/plan_release_run_packets.py",
)
_PREPARED_STOP = _load_script_module(
    "plan_release_prepared_stop_test_module",
    "skills/public/release/scripts/plan_release_prepared_stop.py",
)
_CLOSEOUT_TOKENS = _PLANNER.release_binding_tokens
_CLOSEOUT_EVIDENCE = _PLANNER._closeout_evidence


def _args(**overrides: object) -> SimpleNamespace:
    values = {
        "repo_root": REPO_ROOT,
        "remote": "origin",
        "critique_artifact": None,
        "critique_blocked": None,
        "publish_current": False,
        "part": None,
        "set_version": None,
        "detail": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _run_plan(
    repo: Path, env: dict[str, str], *args: str, detail: bool = True
) -> subprocess.CompletedProcess[str]:
    previous_cwd = Path.cwd()
    try:
        os.chdir(REPO_ROOT)
        cli_args = ["--repo-root", str(repo)]
        if detail:
            cli_args.append("--detail")
        cli_args.extend(args)
        result = run_loaded_script_main(PLANNER, _PLANNER, *cli_args, env=env)
    finally:
        os.chdir(previous_cwd)
    return result


def _run_plan_in_process(
    repo: Path, *args: str, check_current_status: bool = False
) -> subprocess.CompletedProcess[str]:
    """Run planner logic in-process for payload-only matrix cases.

    These cases assert planner routing and packet shape, not the release status reader.
    Keep the dirty-tree case on the real status path, while clean payload cases avoid
    launching a second CLI and repeating a Git status read already covered by the release
    surface tests and the prepared-stop boundary test below.
    """
    values = _args(repo_root=repo)
    iterator = iter(args)
    for value in iterator:
        if value == "--part":
            values.part = next(iterator)
        elif value == "--publish-current":
            values.publish_current = True
        elif value == "--set-version":
            values.set_version = next(iterator)
        elif value == "--critique-blocked":
            values.critique_blocked = next(iterator)
        elif value == "--critique-artifact":
            values.critique_artifact = next(iterator)
        else:
            raise AssertionError(f"unsupported in-process planner argument: {value}")
    status_patch = patch.object(_PLANNER._current_release, "_git_status", return_value=[])
    with (
        status_patch
        if not check_current_status
        else patch.object(
            _PLANNER._current_release, "_git_status", wraps=_PLANNER._current_release._git_status
        )
    ):
        payload = _PLANNER.build_plan(values)
    return subprocess.CompletedProcess(
        ["plan_release_run.py"], 0, stdout=yaml.safe_dump(payload, sort_keys=False), stderr=""
    )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_release_run_planner_reports_inspect_packet_without_mutation(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    result = _run_plan_in_process(repo)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["schema_version"] == "release.run_plan.v1"
    assert payload["next_action"]["kind"] == "inspect_only"
    assert payload["release_state"]["drift"] == []
    assert payload["gate_packets"]
    structured_gate_commands = {
        packet["id"]: packet["command"]
        for packet in payload["gate_packets"]
        if packet["id"] in {"fresh-checkout-probes", "requested-review-gate"}
    }
    assert all("--detail" in command for command in structured_gate_commands.values())
    assert all("--json" not in command for command in structured_gate_commands.values())
    assert {item["path"] for item in payload["required_reads"]} >= {
        "references/index.md",
        "references/version-policy.md",
        "references/critique-boundary.md",
        "references/publication-boundary.md",
    }
    assert not (repo / ".quality-ran").exists()


def test_release_run_planner_routes_declared_specialized_lane_without_mutation(
    tmp_path: Path,
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    workflow = repo / ".github" / "workflows" / "demo-release.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: demo release\n", encoding="utf-8")
    adapter = repo / ".agents" / "release-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8")
        + "\nspecialized_release_lanes:\n"
        + "- id: demo-release\n"
        + "  workflow: .github/workflows/demo-release.yml\n"
        + "  tag_pattern: demo-v*\n"
        + "  command: demo release --plan\n",
        encoding="utf-8",
    )
    manifest = repo / "packaging" / "demo.json"
    before_manifest = manifest.read_bytes()

    result = _run_plan_in_process(repo)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["next_action"] == {
        "kind": "route_specialized_release_lane",
        "reason": (
            "A repo-declared specialized release lane supersedes generic planning; inspect or "
            "run the declared lane command. This planner performs no release mutation."
        ),
        "lane": {
            "id": "demo-release",
            "workflow": ".github/workflows/demo-release.yml",
            "tag_pattern": "demo-v*",
            "command": "demo release --plan",
        },
        "release_mutation": "not-performed",
    }
    assert payload["publish_packets"] == []
    assert "references/adapter-contract.md" in {item["path"] for item in payload["required_reads"]}
    assert manifest.read_bytes() == before_manifest
    assert not (repo / ".quality-ran").exists()


def test_release_run_planner_requires_critique_before_publish(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    result = _run_plan_in_process(repo, "--part", "patch")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target"]["target_version"] == "0.0.1"
    assert payload["next_action"]["kind"] == "needs_critique"
    # The planner must name the critique PRODUCER, not only the
    # `--critique-artifact` validator flag, so the required artifact shape is not
    # discoverable solely by failing `validate_critique_artifacts.py`.
    assert "scaffold_critique_artifact.py" in payload["next_action"]["scaffold_command"]
    assert payload["publish_packets"] == []


def test_release_run_planner_surfaces_stale_update_instructions_before_publish(
    tmp_path: Path,
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter = repo / ".agents" / "release-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8").replace(
            "update_instructions:\n- Run `demo update`.\n- Restart the host if the previous version is still visible.",
            "update_instructions:\n- Run `demo update` to pull 0.0.0.\n- Restart the host if the previous version is still visible.",
        ),
        encoding="utf-8",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "seed stale update instructions")

    result = _run_plan_in_process(
        repo, "--part", "patch", "--critique-blocked", "test host lacks agent tool"
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["next_action"]["kind"] == "prep_update_instructions"
    assert payload["blockers"]
    assert "0.0.0" in payload["next_action"]["reason"]
    assert "version-agnostic" in payload["next_action"]["reason"]


def test_release_run_planner_prioritizes_update_instruction_prep_over_dirty_tree(
    tmp_path: Path,
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter = repo / ".agents" / "release-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8").replace(
            "update_instructions:\n- Run `demo update`.\n- Restart the host if the previous version is still visible.",
            "update_instructions:\n- Run `demo update` to pull 0.0.0.\n- Restart the host if the previous version is still visible.",
        ),
        encoding="utf-8",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "seed stale update instructions")
    (repo / "WIP.txt").write_text("dirty tree should not hide prep guidance", encoding="utf-8")

    result = _run_plan_in_process(
        repo,
        "--part",
        "patch",
        "--critique-blocked",
        "test host lacks agent tool",
        check_current_status=True,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["release_state"]["git_status"]
    assert payload["next_action"]["kind"] == "prep_update_instructions"


def test_release_run_planner_points_to_publish_dry_run_when_ready(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    critique = repo / "charness-artifacts" / "critique" / "demo.md"
    critique.parent.mkdir(parents=True)
    critique.write_text("# Demo critique\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add critique")

    result = _run_plan_in_process(
        repo, "--part", "patch", "--critique-artifact", "charness-artifacts/critique/demo.md"
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["next_action"]["kind"] == "publish_dry_run"
    execute_packet = next(
        packet for packet in payload["publish_packets"] if packet["id"] == "publish-execute"
    )
    assert execute_packet["requires_user_confirmation"] is True
    assert PUBLISH_SCRIPT not in result.stderr


def test_release_run_planner_preserves_blocked_host_signal_in_publish_packet(
    tmp_path: Path,
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    signal = "host runtime has no subagent tool in this fixture"

    result = _run_plan_in_process(repo, "--part", "patch", "--critique-blocked", signal)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["next_action"]["kind"] == "publish_dry_run"
    assert payload["publish_packets"]
    assert all(signal in packet["command"] for packet in payload["publish_packets"])
    assert all("<host-signal>" not in packet["command"] for packet in payload["publish_packets"])


def test_release_run_planner_plain_output(capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_PLANNER, "parse_args", lambda: _args(detail=False))
    monkeypatch.setattr(
        _PLANNER,
        "build_plan",
        lambda _args: {"next_action": {"kind": "inspect_only", "reason": "choose target"}},
    )
    monkeypatch.setattr(
        _PLANNER.SKILL_RUNTIME,
        "arm_cli_timeout",
        lambda **_kwargs: lambda: None,
    )

    assert _PLANNER.main() == 0
    assert "next_action=inspect_only: choose target" in capsys.readouterr().out


def test_release_run_planner_main_emits_yaml_detail_in_process(
    capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = {"next_action": {"kind": "inspect_only", "reason": "test"}}
    monkeypatch.setattr(_PLANNER, "build_plan", lambda _args: plan)
    monkeypatch.setattr(_PLANNER.SKILL_RUNTIME, "arm_cli_timeout", lambda **_kwargs: lambda: None)

    monkeypatch.setattr(_PLANNER, "parse_args", lambda: _args(detail=True))
    assert _PLANNER.main() == 0
    assert yaml.safe_load(capsys.readouterr().out) == plan


def test_release_run_planner_help_points_to_detail_evidence_packets(
    capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["plan_release_run.py", "--help"])

    with pytest.raises(SystemExit) as excinfo:
        _PLANNER.parse_args()

    assert excinfo.value.code == 0
    assert "evidence_packets" in capsys.readouterr().out


def test_release_run_planner_help_describes_all_options(
    capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["plan_release_run.py", "--help"])

    with pytest.raises(SystemExit) as excinfo:
        _PLANNER.parse_args()

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    expected = {
        "--repo-root": "Repository root for adapter and release-surface resolution.",
        "--remote": "Git remote used to inspect release tags and history.",
        "--critique-artifact": "Path to the release critique artifact to include in planned publish commands.",
        "--critique-blocked": "Host signal explaining why the bounded critique could not run.",
        "--publish-current": "Plan publishing the current version without bumping it.",
        "--part": "Version bump part to include in the release plan: patch, minor, or major.",
        "--set-version": "Explicit target version to include in the release plan.",
        "--detail": "Emit the full release plan as YAML.",
    }
    for option, description in expected.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert description in option_block, f"missing help for {option}: {description}"
    assert "--json" not in output


def test_release_run_planner_bootstrap_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    class NoParentPath:
        def __init__(self, _value: str) -> None:
            pass

        def resolve(self):
            return self

        @property
        def parents(self) -> list[Path]:
            return []

    monkeypatch.setattr(_PLANNER, "Path", NoParentPath)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        _PLANNER._load_skill_runtime_bootstrap()


def test_release_run_planner_target_helpers_cover_selectors() -> None:
    assert _PLANNER._target_version(_args(), None) is None
    assert _PLANNER._target_version(_args(publish_current=True), "1.2.3") == "1.2.3"
    assert _PLANNER._target_version(_args(set_version="2.0.0"), "1.2.3") == "2.0.0"
    assert _PLANNER._target_selector(_args(publish_current=True)) == "publish-current"
    assert _PLANNER._target_selector(_args(set_version="2.0.0")) == "set-version"


def test_release_run_packets_add_adapter_read_when_adapter_unhealthy() -> None:
    reads = _PACKETS.required_reads(
        _args(),
        {"found": False, "valid": False, "warnings": [], "data": {}},
    )

    assert "references/adapter-contract.md" in {item["path"] for item in reads}


def test_release_run_packets_emit_publish_current_and_set_version_commands() -> None:
    current_packets = _PACKETS.publish_packets(
        _args(publish_current=True, critique_artifact="charness-artifacts/critique/demo.md"),
        target_version="1.2.3",
        next_action_kind="publish_dry_run",
    )
    set_packets = _PACKETS.publish_packets(
        _args(set_version="2.0.0", critique_artifact="charness-artifacts/critique/demo.md"),
        target_version="2.0.0",
        next_action_kind="publish_dry_run",
    )

    assert "--publish-current" in current_packets[0]["command"]
    assert "--set-version 2.0.0" in set_packets[0]["command"]


@pytest.mark.parametrize(
    ("adapter", "release_payload", "target_version", "expected"),
    [
        (
            {"found": False, "valid": False},
            {"drift": [], "git_status": []},
            None,
            "scaffold_adapter",
        ),
        ({"found": True, "valid": False}, {"drift": [], "git_status": []}, None, "repair_adapter"),
        ({"found": True, "valid": True}, None, None, "repair_release_surface"),
        (
            {"found": True, "valid": True},
            {"drift": ["packaging/charness.json"], "git_status": []},
            None,
            "sync_release_surface",
        ),
        (
            {"found": True, "valid": True},
            {"drift": [], "git_status": [" M file"]},
            "1.2.4",
            "clean_worktree",
        ),
    ],
)
def test_release_run_packets_next_action_blockers(
    adapter: dict[str, object],
    release_payload: dict[str, object] | None,
    target_version: str | None,
    expected: str,
) -> None:
    action = _PACKETS.next_action(
        args=_args(),
        adapter=adapter,
        release_payload=release_payload,
        target_version=target_version,
        update_blocker=None,
    )

    assert action["kind"] == expected
