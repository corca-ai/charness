"""The lane-side changed-line gate owned by `scripts/task_run/task_run_changed_line.py`.

A lane reported a focused green and the pre-push hook refused the same commit four
times on 2026-09-03, each time on a changed line nobody had proven. The receipt
now carries the gate's verdict; these tests drive the gate runner with a fake
phase outcome for each shape, and one real lane through the runner with a seeded
gate script in the lane tree so the wiring is proven end to end.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from scripts.task_run import task_run_changed_line as gate
from tests.quality_gates.repo_shapes import install_committed_repo

from .test_task_run_fixtures import _codex, _run

_CONSUMER_REPORT = {
    "ok": False,
    "blocking": ["scripts/example.py"],
    "blocking_detail": {"scripts/example.py": {"changed_and_missing": [12, 13]}},
    "blocking_targets": {
        "scripts/example.py": [
            {"line": 12, "source": "if flag:"},
            {"line": 13, "source": "return 'unproven'"},
        ]
    },
}


def _wrapper_yaml(status: str, *, consumer: dict[str, Any] | None = None, reason: str = "") -> str:
    payload: dict[str, Any] = {
        "status": status,
        "reason": reason,
        "base_sha": "f" * 40,
        "analyzed_changed_pool_files": ["scripts/example.py"],
        "unmapped_changed_pool_files": [],
    }
    if consumer is not None:
        payload["consumer_stdout"] = yaml.safe_dump(consumer, sort_keys=False)
    return yaml.safe_dump(payload, sort_keys=False)


def _outcome(returncode: int, stdout: str, *, timed_out: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        returncode=returncode, stdout=stdout, stderr="", timed_out=timed_out, elapsed_seconds=0.0
    )


def _fake_run(outcome: SimpleNamespace):
    calls: list[dict[str, Any]] = []

    def run(command, **kwargs):
        calls.append({"command": list(command), **kwargs})
        return outcome

    run.calls = calls  # type: ignore[attr-defined]
    return run


def _tree_with_gate(tmp_path: Path, *, with_mirror_sync: bool = False) -> Path:
    tree = tmp_path / "lane"
    (tree / gate.GATE_SCRIPT).parent.mkdir(parents=True)
    (tree / gate.GATE_SCRIPT).write_text("# stand-in\n", encoding="utf-8")
    if with_mirror_sync:
        (tree / gate.MIRROR_SYNC_SCRIPT).parent.mkdir(parents=True)
        (tree / gate.MIRROR_SYNC_SCRIPT).write_text("# stand-in\n", encoding="utf-8")
    return tree


def _fake_run_sequence(outcomes: list[SimpleNamespace]):
    calls: list[dict[str, Any]] = []
    remaining = list(outcomes)

    def run(command, **kwargs):
        calls.append({"command": list(command), **kwargs})
        return remaining.pop(0)

    run.calls = calls  # type: ignore[attr-defined]
    return run


def test_a_tree_with_the_exporter_regenerates_its_mirror_before_the_gate(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path, with_mirror_sync=True)
    run = _fake_run_sequence(
        [
            _outcome(0, ""),
            _outcome(0, _wrapper_yaml("clean", consumer={"blocking_detail": {}}, reason="all covered")),
        ]
    )

    verdict = gate.run_changed_line_gate(tree, base_sha="a" * 40, log_dir=tmp_path / "l", run=run)

    assert [call["phase"] for call in run.calls] == [gate.MIRROR_PHASE, gate.PHASE]
    mirror_command = run.calls[0]["command"]
    assert mirror_command[1] == str(tree / gate.MIRROR_SYNC_SCRIPT)
    assert mirror_command[mirror_command.index("--repo-root") + 1] == str(tree)
    assert run.calls[0]["cwd"] == tree
    assert verdict["status"] == "clean"
    assert verdict["mirror_sync"]["exit_code"] == 0
    assert verdict["mirror_sync"]["command"] == mirror_command


def test_a_failed_mirror_regeneration_is_no_verdict_and_never_runs_the_gate(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path, with_mirror_sync=True)
    failed = _outcome(1, "")
    failed.stderr = "exporter: refused\n"
    run = _fake_run_sequence([failed])

    verdict = gate.run_changed_line_gate(tree, base_sha="a" * 40, log_dir=tmp_path / "l", run=run)

    assert len(run.calls) == 1
    assert verdict["status"] == gate.NO_VERDICT
    assert verdict["blocking"] is True
    assert "plugin mirror could not be regenerated" in verdict["reason"]
    assert verdict["mirror_sync"]["exit_code"] == 1
    assert verdict["mirror_sync"]["stderr_tail"] == "exporter: refused\n"


def test_a_tree_without_the_exporter_records_no_mirror_sync(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path)
    run = _fake_run(_outcome(0, _wrapper_yaml("noop", reason="no eligible mutation-pool files changed")))

    verdict = gate.run_changed_line_gate(tree, base_sha="a" * 40, log_dir=tmp_path / "l", run=run)

    assert verdict["mirror_sync"] is None
    assert [call["phase"] for call in run.calls] == [gate.PHASE]
    assert verdict["blocking"] is False


def test_a_tree_without_the_gate_script_is_not_applicable_never_clean(tmp_path: Path) -> None:
    run = _fake_run(_outcome(0, ""))

    verdict = gate.run_changed_line_gate(
        tmp_path / "other-repo", base_sha="a" * 40, log_dir=tmp_path / "logs", run=run
    )

    assert verdict["status"] == gate.NOT_APPLICABLE
    assert verdict["blocking"] is False
    assert gate.GATE_SCRIPT.as_posix() in verdict["reason"]
    assert run.calls == []


def test_a_refusal_carries_the_consumer_blocking_detail_verbatim(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path)
    run = _fake_run(_outcome(1, _wrapper_yaml("blocked", consumer=_CONSUMER_REPORT)))
    log_dir = tmp_path / "logs"

    verdict = gate.run_changed_line_gate(tree, base_sha="b" * 40, log_dir=log_dir, run=run)

    assert verdict["status"] == "blocked"
    assert verdict["blocking"] is True
    assert verdict["exit_code"] == 1
    assert verdict["blocking_detail"] == _CONSUMER_REPORT["blocking_detail"]
    assert verdict["blocking_targets"] == _CONSUMER_REPORT["blocking_targets"]
    assert verdict["summary"] == (
        "changed-line gate blocked (exit 1): scripts/example.py lines 12, 13"
    )
    command = run.calls[0]["command"]
    assert command[1] == str(tree / gate.GATE_SCRIPT)
    assert command[command.index("--base-sha") + 1] == "b" * 40
    assert command[command.index("--repo-root") + 1] == str(tree)
    assert "--refuse-unestablished" in command
    assert run.calls[0]["cwd"] == tree
    assert yaml.safe_load((log_dir / gate.STDOUT_LOG_NAME).read_text(encoding="utf-8"))["status"] == "blocked"
    assert verdict["logs"]["stdout"] == str(log_dir / gate.STDOUT_LOG_NAME)


def test_a_clean_verdict_is_not_blocking(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path)
    run = _fake_run(
        _outcome(
            0,
            _wrapper_yaml(
                "clean",
                consumer={"ok": True, "blocking": [], "blocking_detail": {}},
                reason="every mapped changed pool file's changed lines are covered",
            ),
        )
    )

    verdict = gate.run_changed_line_gate(tree, base_sha="c" * 40, log_dir=tmp_path / "l", run=run)

    assert verdict["status"] == "clean"
    assert verdict["blocking"] is False
    assert verdict["blocking_detail"] == {}
    assert verdict["summary"].startswith("changed-line gate clean: every mapped")


def test_an_unestablished_or_partial_exit_blocks_like_the_hook(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path)
    for code, status in ((3, "unestablished"), (4, "unproven"), (1, "unestablished")):
        run = _fake_run(_outcome(code, _wrapper_yaml(status, reason="a dirty pool")))
        verdict = gate.run_changed_line_gate(
            tree, base_sha="d" * 40, log_dir=tmp_path / f"l{code}", run=run
        )
        assert verdict["blocking"] is True, (code, status)
        assert verdict["status"] == status
        assert verdict["summary"] == f"changed-line gate {status} (exit {code}): a dirty pool"


def test_an_unreadable_payload_is_no_verdict_and_blocks(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path)
    run = _fake_run(_outcome(0, "Traceback (most recent call last):\n  boom\n"))

    verdict = gate.run_changed_line_gate(tree, base_sha="e" * 40, log_dir=tmp_path / "l", run=run)

    assert verdict["status"] == gate.NO_VERDICT
    assert verdict["blocking"] is True
    assert "stands for nothing" in verdict["reason"]


def test_a_malformed_payload_is_no_verdict_and_blocks(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path)
    run = _fake_run(_outcome(0, "status: [unclosed\nreason: {bad\n"))

    verdict = gate.run_changed_line_gate(tree, base_sha="e" * 40, log_dir=tmp_path / "l", run=run)

    assert verdict["status"] == gate.NO_VERDICT
    assert verdict["blocking"] is True


def test_a_timed_out_gate_is_no_verdict_and_blocks(tmp_path: Path) -> None:
    tree = _tree_with_gate(tmp_path)
    run = _fake_run(_outcome(124, "", timed_out=True))

    verdict = gate.run_changed_line_gate(
        tree, base_sha="e" * 40, log_dir=tmp_path / "l", timeout_seconds=7, run=run
    )

    assert verdict["status"] == gate.NO_VERDICT
    assert verdict["blocking"] is True
    assert "7 s" in verdict["reason"]


def test_summarize_names_an_untracked_file_by_its_prose_detail() -> None:
    assert gate.summarize_blocking_detail(
        {"scripts/b.py": "file not tracked by the test suite", "scripts/a.py": {"changed_and_missing": [3]}}
    ) == "scripts/a.py lines 3; scripts/b.py: file not tracked by the test suite"
    assert gate.summarize_blocking_detail({}) == ""
    assert gate.summarize_blocking_detail("prose") == ""


_SEEDED_GATE = """#!/usr/bin/env python3
import json, sys
argv = sys.argv[1:]
base = argv[argv.index("--base-sha") + 1]
consumer = json.dumps({
    "ok": False,
    "blocking": ["module.py"],
    "blocking_detail": {"module.py": {"changed_and_missing": [1]}},
    "blocking_targets": ["module.py:1"],
})
print(json.dumps({
    "status": "blocked",
    "reason": "a mapped changed pool file has uncovered changed lines",
    "base_sha": base,
    "analyzed_changed_pool_files": ["module.py"],
    "unmapped_changed_pool_files": [],
    "consumer_stdout": consumer,
}))
sys.exit(1)
"""

_CLEAN_GATE = """#!/usr/bin/env python3
import json, sys
argv = sys.argv[1:]
print(json.dumps({
    "status": "clean",
    "reason": "every mapped changed pool file's changed lines are covered",
    "base_sha": argv[argv.index("--base-sha") + 1],
    "analyzed_changed_pool_files": ["module.py"],
    "unmapped_changed_pool_files": [],
    "consumer_stdout": json.dumps({"ok": True, "blocking": [], "blocking_detail": {}}),
}))
"""


def _repo_with_gate(tmp_path: Path, gate_source: str) -> Path:
    return install_committed_repo(
        tmp_path / "parent",
        {"module.py": "VALUE = 1\n", gate.GATE_SCRIPT.as_posix(): gate_source},
    )


def test_a_lane_whose_tree_refuses_the_changed_line_gate_is_not_done(tmp_path: Path) -> None:
    repo = _repo_with_gate(tmp_path, _SEEDED_GATE)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable)

    verdict = payload["changed_line_gate"]
    assert verdict["status"] == "blocked", payload
    assert verdict["blocking"] is True
    assert verdict["blocking_detail"] == {"module.py": {"changed_and_missing": [1]}}
    assert verdict["command"][command_index(verdict["command"], "--base-sha") + 1] == payload["base_sha"]
    assert payload["status"] == "validated-partial-result", payload
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["candidate"]["status"] == "validated"
    assert "changed-line gate blocked (exit 1): module.py lines 1" in payload["next_step"]
    persisted = json.loads(Path(payload["result_path"]).read_text(encoding="utf-8"))
    assert persisted["status"] == "validated-partial-result"
    assert persisted["changed_line_gate"]["blocking_detail"] == verdict["blocking_detail"]
    assert Path(verdict["logs"]["stdout"]).is_file()
    assert os.path.dirname(verdict["logs"]["stdout"]) == os.path.dirname(payload["logs"]["stdout"])


def test_a_lane_whose_tree_passes_the_changed_line_gate_completes_as_before(tmp_path: Path) -> None:
    repo = _repo_with_gate(tmp_path, _CLEAN_GATE)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["approval_eligibility"] == "eligible"
    assert payload["changed_line_gate"]["status"] == "clean"
    assert payload["changed_line_gate"]["blocking"] is False


def test_a_lane_in_a_tree_without_the_gate_records_not_applicable(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "parent", {"module.py": "VALUE = 1\n"})
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["changed_line_gate"]["status"] == gate.NOT_APPLICABLE


def command_index(command: list[str], flag: str) -> int:
    return command.index(flag)
