"""The semantic review wrapper's worker timeout, decided by the worker's own deadline.

Split from `test_semantic_review_command.py`, which sits at the length cap: this
case runs the wrapper in-process so the outer runner bound cannot race the
worker's timeout path under load.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.test_semantic_review_command import ROOT, WRAPPER, _fake_codex, _repo
from tests.script_loader import load_script_module


def test_worker_timeout_keeps_started_and_non_approval_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The worker's own timeout is the only deadline that can end this run.

    The backend never finishes on its own, so the worker's 1 s budget must fire.
    The wrapper's outer runner bound (worker budget plus a 2 s grace) raced the
    worker's kill-and-receipt path under full-suite load and recorded the attempt
    `interrupted`; it is removed here by running the wrapper in-process with that
    one phase unbounded, so the verdict waits on the worker's own exit.
    """
    _repo(tmp_path, timeout=1)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_REVIEW_VERDICT", "pass")
    monkeypatch.setenv("FAKE_REVIEW_SLEEP", "3600")
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(tmp_path.parent / f"{tmp_path.name}-external-runtime"))
    for name in ("CHARNESS_RUNTIME_ROOT_AUTO", "CHARNESS_RUNTIME_REPO_KEY", "FAKE_REVIEW_OBSERVATIONS"):
        monkeypatch.delenv(name, raising=False)
    review = load_script_module("run_review_worker_timeout_under_test", WRAPPER)
    bounded_phase = review.SUPPORT.run_monitored_phase

    def worker_budget_only(command, **kwargs):
        if kwargs.get("phase") == "critique-review-runner":
            kwargs["timeout_seconds"] = None
        return bounded_phase(command, **kwargs)

    monkeypatch.setattr(review.SUPPORT, "run_monitored_phase", worker_budget_only)
    monkeypatch.chdir(ROOT)

    returncode = review.main([
        "--repo-root", str(tmp_path), "--scope", "semantic command", "--lens", "operability",
        "--attempt-id", "backend-timeout", "--backend", "codex_exec", "--reviewed-path", "reviewed.txt",
    ])
    captured = capsys.readouterr()
    assert captured.out, captured.err
    payload = yaml.safe_load(captured.out)

    assert returncode == 1, captured.err + captured.out
    assert payload["reviewer_started"] is True
    assert payload["delivery_state"] == "timed-out"
    assert payload["verdict_state"] == "not-applicable"
    assert payload["approval_eligible"] is False
    assert payload["execution_state"] == "started"
    assert payload["lifecycle_state"] == "timed-out"
    assert payload["output_state"] == "partial"
    assert payload["output"]["approval_eligible"] is False
    assert payload["output"]["artifacts"]
    ledger = json.loads((tmp_path / payload["paths"]["ledger"]).read_text(encoding="utf-8"))
    assert ledger["attempts"][-1]["state"] == "timed-out"
    durable = (tmp_path / payload["paths"]["summary"]).parent
    manifest = json.loads((durable / "attempt-manifest.json").read_text(encoding="utf-8"))
    assert manifest["reusable"] is True
    assert manifest["approval_eligible"] is False
    assert manifest["use_class"] == "diagnostic-retryable"
    assert (durable / "review-prompt.md").is_file()
    assert (durable / "run-plan.json").is_file()
    assert not (tmp_path / ".charness" / "scratch").exists()
    assert all(
        not (isinstance(path, str) and "/scratch/critique-review/" in path)
        for path in payload["paths"].values()
    )
