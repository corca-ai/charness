from __future__ import annotations

import json
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

import yaml

import scripts.cli.cmd_init as cmd_init
import scripts.task_run.task_run_status_report as status_report
import scripts.task_run.task_run_train_core as train_core


def test_landing_review_plan_shape(tmp_path: Path) -> None:
    plan = train_core.landing_review_plan(
        "python3",
        tmp_path / "prepare.py",
        tmp_path / "review.py",
        tmp_path / "repo",
        tmp_path / "runtime",
        "base-sha",
        "landed-sha",
        "run-7",
    )
    assert plan["attempt_id"] == "train-landing-run-7"
    assert plan["record"]["base_sha"] == "base-sha"
    assert plan["record"]["landed_sha"] == "landed-sha"
    assert plan["prepare_command"][-2:] == ["--slug", "train-landing-run-7"]
    assert "--packet-file" in plan["review_command"]


def test_stack_order_ok() -> None:
    assert train_core.stack_order(["a", "b"]) == ("a", "b")


def test_decide_main_moved_requeues() -> None:
    decision = train_core.decide_next_action(["a"], {}, main_at_start="sha-1", main_now="sha-2")
    assert decision["action"] == "requeue"
    assert decision["requeue_branches"] == ["a"]


def test_decide_land_and_bisect() -> None:
    landed = train_core.decide_next_action(["a"], {1: True}, main_at_start="sha", main_now="sha")
    assert landed["action"] == "land"
    assert landed["landed_branches"] == ["a"]

    probing = train_core.decide_next_action(
        ["a", "b"], {2: False}, main_at_start="sha", main_now="sha"
    )
    assert probing["action"] == "verify-prefix"
    assert probing["prefix_count"] == 1

    red = train_core.decide_next_action(
        ["a", "b"], {1: True, 2: False}, main_at_start="sha", main_now="sha"
    )
    assert red["action"] == "land-prefix"
    assert red["first_bad_branch"] == "b"


def test_routing_branches() -> None:
    try:
        train_core.derive_landing_review_routing("nope")  # type: ignore[arg-type]
    except train_core.TrainError:
        pass
    else:
        raise AssertionError("expected TrainError for a non-sequence")

    try:
        train_core.derive_landing_review_routing([42])  # type: ignore[list-item]
    except train_core.TrainError:
        pass
    else:
        raise AssertionError("expected TrainError for a non-mapping finding")

    routes = train_core.derive_landing_review_routing(
        [
            {"severity": "P1", "topic": "red"},
            {"severity": " p2 ", "topic": "slow"},
            {"severity": 7, "topic": "odd"},
            {"severity": "P9", "topic": "unknown"},
        ]
    )
    assert [item["topic"] for item in routes["next_unit"]] == ["red"]
    assert [item["topic"] for item in routes["batch"]] == ["slow"]
    assert [item["topic"] for item in routes["unrouted"]] == ["odd", "unknown"]


def test_validate_loosening_branches() -> None:
    bad = {
        "version": 1,
        "commands": [{"id": "c", "argv": ["x"]}],
        "known_failures": [],
        "loosening": "parallel",
    }
    assert any(
        "loosening must be a mapping" in item for item in train_core.validate_verify_profile(bad)
    )

    good = {
        "version": 1,
        "commands": [{"id": "c", "argv": ["x"]}],
        "known_failures": [],
    }
    assert train_core.validate_verify_profile(good) == []


def test_bootstrap_inserts_repo_root(monkeypatch) -> None:
    import sys

    root = str(Path(status_report.__file__).resolve().parents[2])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != root])
    assert root not in sys.path
    status_report._load_repo_runtime_bootstrap()
    assert sys.path[0] == root


def test_parse_time_branches() -> None:
    assert status_report._parse_time(123) is None
    assert status_report._parse_time(None) is None
    assert status_report._parse_time("   ") is None
    assert status_report._parse_time("not-a-time") is None
    assert status_report._parse_time("2026-01-01T00:00:00") is None
    stamp = status_report._parse_time("2026-01-01T00:00:00Z")
    assert stamp is not None and stamp.tzinfo is not None


def _event(event_id: str, occurred_at: str, source: str, kind: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "event_id": event_id,
        "occurred_at": occurred_at,
        "source": source,
        "event_kind": kind,
        "facts": {},
    }


def test_window_events_branches(tmp_path: Path) -> None:
    moment = datetime(2026, 9, 25, tzinfo=timezone.utc)
    cutoff = datetime(2026, 9, 24, tzinfo=timezone.utc)

    missing = tmp_path / "missing.jsonl"
    assert status_report._window_events(missing, "friction-log", cutoff=cutoff, moment=moment) == (
        [],
        0,
    )

    path = tmp_path / "events.jsonl"
    path.write_text(
        "\n".join(
            [
                "   ",
                "{malformed json",
                json.dumps(
                    _event("w", "2026-09-25T00:00:05Z", "decision-ledger", "contract-amendment")
                ),
                json.dumps(_event("o", "2000-01-01T00:00:00Z", "friction-log", "block")),
                json.dumps(_event("k", "2026-09-25T00:00:05Z", "friction-log", "block")),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    events, skipped = status_report._window_events(
        path, "friction-log", cutoff=cutoff, moment=moment
    )
    assert [event["event_id"] for event in events] == ["k"]
    assert skipped == 2


def _doctor_payload() -> dict[str, object]:
    return {
        "codex_host_guidance": {
            "status": "installed",
            "manual_action_required": False,
            "message": "ok",
        },
        "claude_host_guidance": {},
        "grok_host_guidance": {},
        "repo_onboarding": {},
        "host_next_steps": {},
        "next_action": "none",
        "checkout_version": "1.0.9",
        "codex_source_version": "1.0.9",
        "codex_cache_manifest_version": "0.0.0",
        "codex_cache_manifest_status": "invalid",
        "codex_source_cache_drift": True,
    }


def _finish_kwargs(home_root: Path, repo_root: Path, managed: bool) -> dict[str, object]:
    return {
        "home_root": home_root,
        "managed_checkout": managed,
        "target_repo_root": repo_root,
        "plugin_root": home_root / "plugin",
        "codex_marketplace_path": home_root / "marketplace.json",
        "claude_wrapper_path": home_root / "cli",
        "cli_path": home_root / "cli" / "charness",
        "checkout": {"repo_root": str(repo_root)},
        "cli_reexec_state": None,
        "script_path": repo_root / "charness",
        "embedded_repo_root": None,
    }


def _finish_args(home_root: Path, repo_root: Path) -> Namespace:
    return Namespace(
        home_root=home_root,
        repo_root=repo_root,
        target_repo_root=repo_root,
        repo_url="https://example.invalid/charness.git",
        skip_cli_install=True,
        skip_claude_wrapper=True,
        no_pull=True,
        skip_codex_cache_refresh=True,
        scope=None,
        detail=False,
    )


def _patch_finish(monkeypatch, maybe_install: dict[str, object]) -> dict[str, object]:
    seen: dict[str, object] = {}
    monkeypatch.setattr(cmd_init, "install_surface", lambda *_a, **_k: {"host_next_steps": {}})
    monkeypatch.setattr(cmd_init, "build_doctor_payload", lambda **_k: _doctor_payload())
    monkeypatch.setattr(cmd_init, "maybe_install_codex_host", lambda **_k: dict(maybe_install))
    monkeypatch.setattr(cmd_init, "write_version_state", lambda *_a, **_k: {})
    monkeypatch.setattr(cmd_init, "build_version_provenance", lambda **_k: {})
    monkeypatch.setattr(cmd_init, "write_host_state", lambda *_a, **_k: None)

    def _fake_install_state(*args: object, **kwargs: object) -> None:
        seen["write_install_state"] = kwargs

    monkeypatch.setattr(cmd_init, "write_install_state", _fake_install_state)
    return seen


def test_finish_init_install_incomplete(tmp_path: Path, monkeypatch, capsys) -> None:
    home_root = tmp_path / "home"
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _patch_finish(monkeypatch, {"status": "attempted", "method": "codex-app-server-plugin-install"})

    result = cmd_init.finish_init(
        _finish_args(home_root, repo_root),
        **_finish_kwargs(home_root, repo_root, managed=False),  # type: ignore[arg-type]
    )
    assert result == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    install = payload["codex_host_install"]
    assert install["status"] == "failed"
    assert install["reason"] == "install-incomplete"
    assert "error" in install


def test_finish_init_managed_checkout_writes_state(tmp_path: Path, monkeypatch, capsys) -> None:
    home_root = tmp_path / "home"
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    seen = _patch_finish(monkeypatch, {"status": "skipped", "reason": "flag-disabled"})

    result = cmd_init.finish_init(
        _finish_args(home_root, repo_root),
        **_finish_kwargs(home_root, repo_root, managed=True),  # type: ignore[arg-type]
    )
    assert result == 0
    assert seen["write_install_state"] == {
        "repo_root": repo_root,
        "managed_checkout": True,
    }
    capsys.readouterr()
