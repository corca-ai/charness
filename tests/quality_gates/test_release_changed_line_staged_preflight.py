"""Preflight the release gate's staged-tree candidate before coverage production."""

from __future__ import annotations

import json
import sys
from types import SimpleNamespace

import pytest
import yaml

from .support import ROOT
from .test_release_changed_line_coverage import SCRIPT, _blocking_consumer_stub


@pytest.fixture()
def gate():
    from tests.script_loader import load_script_module

    return load_script_module("release_changed_line_staged_preflight_under_test", ROOT / SCRIPT)


def test_refusing_release_rejects_staged_invisible_pool_before_production(
    gate, monkeypatch, capsys
) -> None:
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": []})
    producer_calls = []
    scopes = []
    eligible = {"scripts/mapped.py", "scripts/unmapped.py"}
    monkeypatch.setattr(gate, "list_eligible", lambda _root: sorted(eligible))
    monkeypatch.setattr(
        gate,
        "staged_invisible_pool_changes",
        lambda _root, paths: scopes.append(set(paths)) or ["scripts/mapped.py"],
    )
    monkeypatch.setattr(
        gate._producer,
        "produce_command_coverage",
        lambda *_args, **_kwargs: producer_calls.append(True),
    )

    code = gate.main(
        ["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"]
    )

    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert code == 1
    assert producer_calls == []
    assert scopes == [eligible]
    assert payload["status"] == gate.UNESTABLISHED_STATUS
    assert payload["uncommitted_pool_files"] == ["scripts/mapped.py"]
    assert "coverage production was refused" in payload["reason"]
    assert "refusing release" in captured.err


@pytest.mark.parametrize("refuse", [False, True])
def test_unknown_staged_status_stops_without_a_verdict_before_production(
    gate, monkeypatch, capsys, refuse: bool
) -> None:
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": []})
    producer_calls = []
    monkeypatch.setattr(gate, "list_eligible", lambda _root: ["scripts/mapped.py"])
    monkeypatch.setattr(gate, "staged_invisible_pool_changes", lambda *_args: None)
    monkeypatch.setattr(
        gate._producer,
        "produce_command_coverage",
        lambda *_args, **_kwargs: producer_calls.append(True),
    )
    args = ["--repo-root", str(ROOT), "--base-sha", "b" * 40]
    if refuse:
        args.append("--refuse-unestablished")

    code = gate.main(args)

    captured = capsys.readouterr()
    assert code == gate.NO_VERDICT_EXIT
    assert producer_calls == []
    assert yaml.safe_load(captured.out)["status"] == "no-verdict"
    assert "could not inspect the worktree" in captured.err


def test_staged_only_candidate_is_allowed_to_produce_a_clean_verdict(
    gate, monkeypatch, capsys
) -> None:
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": []})
    events = []
    consumer_argv = []
    monkeypatch.setattr(gate, "list_eligible", lambda _root: ["scripts/mapped.py"])
    monkeypatch.setattr(
        gate,
        "staged_invisible_pool_changes",
        lambda *_args: events.append("preflight") or [],
    )
    monkeypatch.setattr(
        gate._producer,
        "produce_command_coverage",
        lambda *_args, **_kwargs: events.append("producer")
        or {"returncode": 0, "produced_mutation_coverage": True},
    )
    monkeypatch.setattr(
        gate._trust,
        "uncommitted_pool_changes",
        lambda *_args: events.append("late-trust") or ["scripts/mapped.py"],
    )

    def clean_consumer():
        events.append("consumer")
        consumer_argv.extend(sys.argv)
        print(json.dumps({"ok": True, "blocking": []}))
        return 0

    monkeypatch.setattr(
        gate, "import_repo_module", lambda *_args: SimpleNamespace(main=clean_consumer)
    )

    code = gate.main(
        ["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"]
    )

    assert code == 0
    assert events == ["preflight", "producer", "late-trust", "consumer"]
    assert consumer_argv[consumer_argv.index("--head-sha") + 1] == gate.STAGED_HEAD
    assert "--allow-dirty" in consumer_argv
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "clean"


def test_post_production_pool_change_still_refuses(
    gate, monkeypatch, capsys
) -> None:
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": []})
    events = []
    consumer_argv = []
    monkeypatch.setattr(gate, "list_eligible", lambda _root: ["scripts/mapped.py"])
    monkeypatch.setattr(
        gate,
        "staged_invisible_pool_changes",
        lambda *_args: events.append("preflight") or [],
    )
    monkeypatch.setattr(
        gate._producer,
        "produce_command_coverage",
        lambda *_args, **_kwargs: events.append("producer")
        or {"returncode": 0, "produced_mutation_coverage": True},
    )
    monkeypatch.setattr(
        gate._trust,
        "uncommitted_pool_changes",
        lambda *_args: events.append("late-trust") or ["scripts/mapped.py"],
    )

    def unestablished_consumer():
        events.append("consumer")
        consumer_argv.extend(sys.argv)
        print(json.dumps({"ok": True, "blocking": [], "dirty_pool_unverified": True}))
        return 3

    monkeypatch.setattr(
        gate,
        "import_repo_module",
        lambda *_args: SimpleNamespace(main=unestablished_consumer),
    )

    code = gate.main(
        ["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"]
    )

    assert code == 1
    assert events == ["preflight", "producer", "late-trust", "consumer"]
    assert consumer_argv[consumer_argv.index("--head-sha") + 1] == gate.STAGED_HEAD
    assert yaml.safe_load(capsys.readouterr().out)["status"] == gate.UNESTABLISHED_STATUS


def test_known_staged_mismatch_remains_advisory_without_release_refusal(
    gate, monkeypatch, capsys
) -> None:
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": []})
    events = []
    monkeypatch.setattr(gate, "list_eligible", lambda _root: ["scripts/mapped.py"])
    monkeypatch.setattr(
        gate,
        "staged_invisible_pool_changes",
        lambda *_args: events.append("preflight") or ["scripts/mapped.py"],
    )
    monkeypatch.setattr(
        gate._producer,
        "produce_command_coverage",
        lambda *_args, **_kwargs: events.append("producer")
        or {"returncode": 0, "produced_mutation_coverage": True},
    )
    monkeypatch.setattr(
        gate._trust,
        "uncommitted_pool_changes",
        lambda *_args: events.append("late-trust") or ["scripts/mapped.py"],
    )

    def unestablished_consumer():
        events.append("consumer")
        print(json.dumps({"ok": True, "blocking": [], "dirty_pool_unverified": True}))
        return 3

    monkeypatch.setattr(
        gate,
        "import_repo_module",
        lambda *_args: SimpleNamespace(main=unestablished_consumer),
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == gate.UNESTABLISHED_EXIT
    assert events == ["preflight", "producer", "late-trust", "consumer"]
    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["status"] == gate.UNESTABLISHED_STATUS
    assert "refusing release" not in captured.err
