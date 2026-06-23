from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_publish_fixtures import (
    PUBLISH_SCRIPT,
    REPO_ROOT,
    _release_env,
    _seed_publish_release_repo,
)

PLANNER = "skills/public/release/scripts/plan_release_run.py"


def _load_script_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_PLANNER = _load_script_module("plan_release_run_test_module", PLANNER)
_PACKETS = _load_script_module(
    "plan_release_run_packets_test_module",
    "skills/public/release/scripts/plan_release_run_packets.py",
)


def _args(**overrides: object) -> SimpleNamespace:
    values = {
        "repo_root": REPO_ROOT,
        "remote": "origin",
        "critique_artifact": None,
        "critique_blocked": None,
        "publish_current": False,
        "part": None,
        "set_version": None,
        "json": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _run_plan(repo: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(REPO_ROOT / PLANNER), "--repo-root", str(repo), "--json", *args],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_release_run_planner_reports_inspect_packet_without_mutation(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)

    result = _run_plan(repo, env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "release.run_plan.v1"
    assert payload["next_action"]["kind"] == "inspect_only"
    assert payload["release_state"]["drift"] == []
    assert payload["gate_packets"]
    assert {item["path"] for item in payload["required_reads"]} >= {
        "references/index.md",
        "references/version-policy.md",
        "references/critique-boundary.md",
        "references/publication-boundary.md",
    }
    assert not (repo / ".quality-ran").exists()


def test_release_run_planner_requires_critique_before_publish(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)

    result = _run_plan(repo, env, "--part", "patch")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["target_version"] == "0.0.1"
    assert payload["next_action"]["kind"] == "needs_critique"
    assert payload["publish_packets"] == []


def test_release_run_planner_surfaces_stale_update_instructions_before_publish(tmp_path: Path) -> None:
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
    env = _release_env(tmp_path, bin_dir)

    result = _run_plan(repo, env, "--part", "patch", "--critique-blocked", "test host lacks agent tool")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["next_action"]["kind"] == "prep_update_instructions"
    assert payload["blockers"]
    assert "0.0.1" in payload["next_action"]["reason"]


def test_release_run_planner_points_to_publish_dry_run_when_ready(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    critique = repo / "charness-artifacts" / "critique" / "demo.md"
    critique.parent.mkdir(parents=True)
    critique.write_text("# Demo critique\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add critique")
    env = _release_env(tmp_path, bin_dir)

    result = _run_plan(repo, env, "--part", "patch", "--critique-artifact", "charness-artifacts/critique/demo.md")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["next_action"]["kind"] == "publish_dry_run"
    execute_packet = next(packet for packet in payload["publish_packets"] if packet["id"] == "publish-execute")
    assert execute_packet["requires_user_confirmation"] is True
    assert PUBLISH_SCRIPT not in result.stderr


def test_release_run_planner_preserves_blocked_host_signal_in_publish_packet(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    signal = "host runtime has no subagent tool in this fixture"

    result = _run_plan(repo, env, "--part", "patch", "--critique-blocked", signal)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["next_action"]["kind"] == "publish_dry_run"
    assert payload["publish_packets"]
    assert all(signal in packet["command"] for packet in payload["publish_packets"])
    assert all("<host-signal>" not in packet["command"] for packet in payload["publish_packets"])


def test_release_run_planner_plain_output(capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_PLANNER, "parse_args", lambda: _args(json=False))
    monkeypatch.setattr(
        _PLANNER,
        "build_plan",
        lambda _args: {"next_action": {"kind": "inspect_only", "reason": "choose target"}},
    )
    monkeypatch.setattr(
        _PLANNER.SKILL_RUNTIME,
        "arm_cli_timeout",
        lambda label: (lambda: None),
    )

    assert _PLANNER.main() == 0
    assert "next_action=inspect_only: choose target" in capsys.readouterr().out


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


def test_release_run_planner_records_real_host_probe_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        _PLANNER,
        "load_adapter",
        lambda _repo: {"found": True, "valid": True, "path": None, "warnings": [], "errors": [], "data": {}},
    )
    monkeypatch.setattr(
        _PLANNER,
        "build_release_payload",
        lambda _repo: {"surface_versions": {"packaging_manifest": "1.2.3"}, "drift": [], "git_status": []},
    )
    monkeypatch.setattr(_PLANNER, "collect_changed_paths", lambda _repo: ["skills/public/release/SKILL.md"])
    monkeypatch.setattr(
        _PLANNER,
        "safe_real_host_payload",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(SystemExit("probe failed")),
    )
    monkeypatch.setattr(_PLANNER, "build_review_gate_payload", lambda _repo, run_commands: {"status": "ok"})
    monkeypatch.setattr(_PLANNER, "build_fresh_checkout_payload", lambda _repo, run_probes: {"status": "configured"})
    monkeypatch.setattr(_PLANNER, "current_branch", lambda _repo: "main")

    payload = _PLANNER.build_plan(_args(repo_root=REPO_ROOT))

    assert payload["evidence_packets"]["real_host"] == {"status": "blocked", "error": "probe failed"}


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
        ({"found": False, "valid": False}, {"drift": [], "git_status": []}, None, "scaffold_adapter"),
        ({"found": True, "valid": False}, {"drift": [], "git_status": []}, None, "repair_adapter"),
        ({"found": True, "valid": True}, None, None, "repair_release_surface"),
        ({"found": True, "valid": True}, {"drift": ["packaging/charness.json"], "git_status": []}, None, "sync_release_surface"),
        ({"found": True, "valid": True}, {"drift": [], "git_status": [" M file"]}, "1.2.4", "clean_worktree"),
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
