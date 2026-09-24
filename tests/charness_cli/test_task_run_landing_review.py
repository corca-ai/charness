"""Stub-boundary evidence for merge-train landing review triggers.

These fixtures observe routing derivation, launch intent, and the trigger record.
They make no claim about live reviewer execution or P1 delivery.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

from scripts.task_run import task_run_train as train
from scripts.task_run.task_run_train_core import derive_landing_review_routing
from tests.quality_gates.repo_shapes import install_committed_repo


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _repo_with_branch(tmp_path: Path) -> tuple[Path, str]:
    repo = install_committed_repo(tmp_path / "repo", {"base.txt": "base\n"}, branch="main")
    base_sha = _git(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "--quiet", "-c", "lane/landing-review")
    (repo / "landed.txt").write_text("landed\n", encoding="utf-8")
    _git(repo, "add", "landed.txt")
    _git(
        repo,
        "-c",
        "user.name=Landing Review Test",
        "-c",
        "user.email=landing-review-test@example.com",
        "commit",
        "--quiet",
        "-m",
        "landing review fixture",
    )
    _git(repo, "switch", "--quiet", "main")
    return repo, base_sha


def _stub_successful_train(monkeypatch, repo: Path) -> None:
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", os.fspath(repo.parent / "runtime"))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.setattr(
        train._doctor,
        "run_prepare",
        lambda *_args, **_kwargs: {"status": train.PASS, "doctor": {"status": train.PASS}},
    )
    monkeypatch.setattr(
        train,
        "run_verify_profile",
        lambda *_args, **_kwargs: (True, [{"command_id": "fixture", "status": train.PASS}]),
    )

    def fast_forward(
        repo_root: Path, branch_ref: str, base_sha: str, tip_sha: str
    ) -> tuple[bool, str]:
        _git(repo_root, "update-ref", branch_ref, tip_sha, base_sha)
        return True, ""

    monkeypatch.setattr(train, "_land_main", fast_forward)


def _stub_packet_preparation(monkeypatch) -> None:
    monkeypatch.setattr(
        train,
        "_prepare_landing_review_packet",
        lambda *_args: (
            "charness-artifacts/critique/train-landing-packet.json",
            "a" * 64,
        ),
    )


def test_landing_review_routing_sends_p1_to_next_unit_and_p2_p3_to_batch() -> None:
    routes = derive_landing_review_routing(
        [
            {"id": "urgent", "severity": "P1"},
            {"id": "important", "severity": "P2"},
            {"id": "minor", "severity": "P3"},
        ]
    )

    assert [item["id"] for item in routes["next_unit"]] == ["urgent"]
    assert [item["id"] for item in routes["batch"]] == ["important", "minor"]
    assert routes["unrouted"] == []


def test_fast_forward_records_packet_identity_and_nonblocking_lifecycle_launch(
    tmp_path: Path, monkeypatch
) -> None:
    repo, _base_sha = _repo_with_branch(tmp_path)
    _stub_successful_train(monkeypatch, repo)
    _stub_packet_preparation(monkeypatch)
    calls: list[tuple[list[str], dict[str, object]]] = []

    def popen(command, **kwargs):
        calls.append((list(command), kwargs))
        return SimpleNamespace(pid=4321)

    monkeypatch.setattr(train, "_launch_popen", popen)

    result = train.run_train(repo, ["lane/landing-review"])

    trigger = result["landing_review_trigger"]
    record_path = Path(trigger["launch_record_path"])
    record = json.loads(record_path.read_text(encoding="utf-8"))
    command, options = calls[0]
    assert result["status"] == train.PASS
    assert trigger["status"] == "launched"
    assert trigger["packet_identity"] == "a" * 64
    assert record["packet_identity"] == "a" * 64
    assert record["launch_record_path"] == str(record_path)
    assert record["process_id"] == 4321
    assert record_path.is_relative_to(tmp_path / "runtime")
    assert Path(record["log_path"]).is_file()
    assert any(Path(item).name == "run_review.py" for item in command)
    assert options["start_new_session"] is True
    assert options["stdin"] == subprocess.DEVNULL
    assert options["stdout"] is options["stderr"]
    assert "NON-CLAIM" in trigger["non_claim"]
    assert "P1 delivery" in trigger["non_claim"]


def test_review_launch_failure_records_nonclaim_and_keeps_landing_successful(
    tmp_path: Path, monkeypatch
) -> None:
    repo, base_sha = _repo_with_branch(tmp_path)
    _stub_successful_train(monkeypatch, repo)
    _stub_packet_preparation(monkeypatch)
    calls: list[list[str]] = []

    def unavailable(command, **_kwargs):
        calls.append(list(command))
        raise OSError("reviewer process could not start")

    monkeypatch.setattr(train, "_launch_popen", unavailable)

    result = train.run_train(repo, ["lane/landing-review"])

    trigger = result["landing_review_trigger"]
    record = json.loads(Path(trigger["launch_record_path"]).read_text(encoding="utf-8"))
    assert len(calls) == 1
    assert result["status"] == train.PASS
    assert _git(repo, "rev-parse", "main") != base_sha
    assert trigger["status"] == "unavailable-skip"
    assert record["status"] == "unavailable-skip"
    assert record["packet_identity"] == "a" * 64
    assert "reviewer process could not start" in record["reason"]
    assert "NON-CLAIM" in trigger["non_claim"]
    assert "not review-passed" in trigger["non_claim"]
