"""Execution contract between mutation-coverage production and consumption."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from .mutation_coverage_producer_fixtures import seed_mutation_coverage_repo


def _producer_payload(base: str, command: str) -> dict[str, object]:
    return {"executed_commands": [{
        "produced_mutation_coverage": True,
        "mutation_coverage_base_sha": base,
        "mutation_coverage_consumer_command": command,
    }]}


def _consumer_command(prod, repo: Path, base: str) -> str:
    return prod.consumer_command_for_produced_coverage(
        repo, base_sha=base, coverage_json=repo / "reports/mutation/test-coverage.json"
    )


def test_produced_coverage_runs_authoritative_consumer_and_records_pass(tmp_path: Path) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = seed_mutation_coverage_repo(tmp_path)
    command = _consumer_command(prod, repo, base)
    payload = _producer_payload(base, command)
    seen: list[str] = []

    def fake_run(repo_root, received, phase):
        seen.append(received)
        return {
            "phase": phase,
            "command": received,
            "returncode": 0,
            "stdout": json.dumps({"ok": True, "blocking": [], "base_sha": base, "head_sha": "HEAD"}),
            "stderr": "",
        }

    assert prod.run_produced_coverage_consumer(repo, payload, fake_run) is False
    assert seen == [command]
    assert payload["executed_commands"][0]["mutation_coverage_consumer"]["status"] == "passed"
    assert payload["executed_commands"][-1]["mutation_coverage_consumer"] is True
    assert payload["mutation_coverage_changed_line_proof"]["status"] == "passed"


def test_produced_coverage_consumer_block_stops_closeout(tmp_path: Path) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = seed_mutation_coverage_repo(tmp_path)
    command = _consumer_command(prod, repo, base)
    payload = _producer_payload(base, command)

    def fake_run(repo_root, received, phase):
        return {"phase": phase, "command": received, "returncode": 1, "stdout": json.dumps({"blocking": ["scripts/foo.py"]}), "stderr": "blocked"}

    assert prod.run_produced_coverage_consumer(repo, payload, fake_run) is True
    assert payload["status"] == "failed"
    assert payload["executed_commands"][0]["mutation_coverage_consumer"]["status"] == "blocked"


@pytest.mark.parametrize("stdout", ["not json", "[]"])
def test_produced_coverage_consumer_unreadable_verdict_fails_closeout(
    tmp_path: Path, stdout: str
) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = seed_mutation_coverage_repo(tmp_path)
    command = _consumer_command(prod, repo, base)
    payload = _producer_payload(base, command)

    def fake_run(repo_root, received, phase):
        return {"phase": phase, "command": received, "returncode": 0, "stdout": stdout, "stderr": ""}

    assert prod.run_produced_coverage_consumer(repo, payload, fake_run) is True
    assert payload["status"] == "failed"
    assert payload["executed_commands"][0]["mutation_coverage_consumer"]["status"] == "failed"


@pytest.mark.parametrize(
    "command",
    [
        "python3 scripts/check_changed_line_mutation_coverage.py --base-sha 'unterminated",
        "python3 scripts/check_changed_line_mutation_coverage.py --base-sha base",
    ],
)
def test_consumer_range_rejects_malformed_or_incomplete_command(command: str) -> None:
    from scripts import mutation_coverage_producer as prod

    assert prod._consumer_range(command) is None


def test_consumer_clean_verdict_rejects_command_base_mismatch() -> None:
    from scripts import mutation_coverage_producer as prod

    command = (
        "python3 scripts/check_changed_line_mutation_coverage.py "
        "--base-sha command-base --head-sha HEAD"
    )
    report = {"ok": True, "blocking": [], "base_sha": "command-base", "head_sha": "HEAD"}

    assert prod._consumer_pass_validation_error(
        report, command=command, producer_base_sha="producer-base"
    ) == "consumer command range does not match producer metadata"


def test_produced_coverage_skips_already_consumed_result(tmp_path: Path) -> None:
    from scripts import mutation_coverage_producer as prod

    existing = {"status": "passed", "command": "already ran"}
    payload = {"executed_commands": [{
        "produced_mutation_coverage": True,
        "mutation_coverage_consumer": existing,
    }]}

    def must_not_run(*args, **kwargs):
        raise AssertionError("already-consumed producer must remain idempotent")

    assert prod.run_produced_coverage_consumer(tmp_path, payload, must_not_run) is False
    assert payload["executed_commands"][0]["mutation_coverage_consumer"] is existing


def test_committed_consumer_nonverification_fails_closeout(tmp_path: Path) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = seed_mutation_coverage_repo(tmp_path)
    command = _consumer_command(prod, repo, base)
    payload = _producer_payload(base, command)

    def fake_run(repo_root, received, phase):
        return {
            "phase": phase,
            "command": received,
            "returncode": 0,
            "stdout": json.dumps({
                "ok": True,
                "blocking": [],
                "base_sha": base,
                "head_sha": "HEAD",
                "coverage_not_verified": True,
            }),
            "stderr": "coverage unavailable",
        }

    assert prod.run_produced_coverage_consumer(repo, payload, fake_run) is True
    assert payload["status"] == "failed"
    assert "not verified" in payload["error"]
    record = payload["executed_commands"][0]["mutation_coverage_consumer"]
    assert record["status"] == "not_checked"
    assert payload["mutation_coverage_changed_line_proof"] is record


@pytest.mark.parametrize(
    "report",
    [
        {},
        {"ok": False, "blocking": [], "base_sha": "BASE", "head_sha": "HEAD"},
        {"ok": True, "blocking": {}, "base_sha": "BASE", "head_sha": "HEAD"},
        {"ok": True, "blocking": ["scripts/foo.py"], "base_sha": "BASE", "head_sha": "HEAD"},
        {"ok": True, "blocking": [], "base_sha": "wrong", "head_sha": "HEAD"},
        {"ok": True, "blocking": [], "base_sha": "BASE", "head_sha": "wrong"},
    ],
)
def test_produced_coverage_consumer_rejects_invalid_clean_shape(
    tmp_path: Path, report: dict[str, object]
) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = seed_mutation_coverage_repo(tmp_path)
    command = _consumer_command(prod, repo, base)
    report = {key: (base if value == "BASE" else value) for key, value in report.items()}
    payload = _producer_payload(base, command)

    def fake_run(repo_root, received, phase):
        return {
            "phase": phase,
            "command": received,
            "returncode": 0,
            "stdout": json.dumps(report),
            "stderr": "",
        }

    assert prod.run_produced_coverage_consumer(repo, payload, fake_run) is True
    record = payload["executed_commands"][0]["mutation_coverage_consumer"]
    assert record["status"] == "failed"
    assert record["reason"]


def test_produced_coverage_missing_consumer_metadata_fails_closeout(tmp_path: Path) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, _base = seed_mutation_coverage_repo(tmp_path)
    payload = {"executed_commands": [{"produced_mutation_coverage": True}]}

    assert prod.run_produced_coverage_consumer(repo, payload, lambda *args: None) is True
    assert payload["status"] == "failed"
    assert payload["mutation_coverage_changed_line_proof"]["status"] == "failed"


def test_produced_coverage_marks_precommit_range_not_checked(tmp_path: Path) -> None:
    from scripts import mutation_coverage_producer as prod

    repo, base = seed_mutation_coverage_repo(tmp_path)
    (repo / "scripts" / "foo.py").write_text("def a():\n    return 9\n", encoding="utf-8")
    command = _consumer_command(prod, repo, base)
    payload = _producer_payload(base, command)

    def must_not_run(*args, **kwargs):
        raise AssertionError("precommit base..HEAD consumer must not run")

    assert prod.run_produced_coverage_consumer(repo, payload, must_not_run) is False
    record = payload["executed_commands"][0]["mutation_coverage_consumer"]
    assert record["status"] == "not_checked"
    assert record["uncommitted_eligible_files"] == ["scripts/foo.py"]
    assert payload["mutation_coverage_changed_line_proof"]["status"] == "not_checked"
