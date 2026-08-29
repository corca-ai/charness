"""The real-host proof gate refuses an unspeakable adapter version instead of INVERTING
its own verdict toward the permissive side.

This row is sharper than a degraded answer. Measured on the real CLI: a repo declaring
`real_host_required_path_globs: ["src/**"]` plus a checklist, handed the changed path
`src/a.py`, printed `real_host=not-required: This repo declares no release-time real-host
proof triggers` at exit 0 under a refused version — and `real_host=required` under a
speakable one. Same repo, same paths, opposite verdict, on the gate whose job is to stop a
publish that skipped real-host proof.

The module's own docstring builds a four-state `evaluation_scope` vocabulary precisely so
`not required` can never cover `we never checked`, and documents `not-configured` as "a
genuine opt-out". An unspeakable version was the fifth state that vocabulary did not have:
the opt-out was printed over a repo that opted IN.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from .support import ROOT

GATE = ROOT / "skills" / "public" / "release" / "scripts" / "check_real_host_proof.py"

DECLARED = 'real_host_required_path_globs:\n  - "src/**"\nreal_host_checklist:\n  - run it on a real host\n'


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "release-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GATE), "--repo-root", str(repo), "--paths", "src/a.py"],
        capture_output=True,
        text=True,
    )


def test_an_unspeakable_version_refuses_rather_than_inverting_the_verdict(tmp_path: Path) -> None:
    # The behavioral flip this row is paid down by. Before the guard this exact input
    # printed `real_host=not-required` at exit 0 over a repo whose declared glob the
    # changed path matches.
    result = _run(_repo(tmp_path, "version: 9\n" + DECLARED))
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    assert "release-adapter.yaml" in result.stderr
    assert "not-required" not in result.stdout


def test_a_speakable_version_still_reports_what_the_repo_declared(tmp_path: Path) -> None:
    # The polarity control that catches a gate which simply refuses everything. This is
    # also the reading that proves the refused-version arm was an INVERSION: same repo,
    # same paths, `required` here.
    result = _run(_repo(tmp_path, "version: 1\n" + DECLARED))
    assert result.returncode == 0, result.stderr
    assert "real_host=required" in result.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    # The documented opt-out survives. A repo that declares no triggers is not a repo
    # whose declaration could not be read, and conflating the two would refuse every
    # consumer that never opted in.
    result = _run(_repo(tmp_path, None))
    assert result.returncode == 0, result.stderr
    assert "real_host=not-required" in result.stdout


@pytest.mark.parametrize(
    ("report", "message"),
    [
        ("not json", "native classify report is missing or unparseable"),
        ('{"schema": "wrong"}', "expected schema repograph.classify.v1"),
        ('{"schema": "repograph.classify.v1"}', "no paths array"),
        ('{"schema": "repograph.classify.v1", "paths": [null]}', "non-object path record"),
        (
            '{"schema": "repograph.classify.v1", "paths": [{"path": 1, "role": "production"}]}',
            "path and role must be strings",
        ),
        (
            '{"schema": "repograph.classify.v1", "paths": [{"path": "other.py", "role": "production"}]}',
            "unexpected path 'other.py'",
        ),
        (
            '{"schema": "repograph.classify.v1", "paths": [{"path": "src/a.py", "role": "unknown"}]}',
            "unknown role 'unknown'",
        ),
    ],
)
def test_malformed_native_classify_reports_are_refused(
    report: str, message: str
) -> None:
    from tests.script_main import load_script_module

    module = load_script_module("check_real_host_proof_report_refusal", GATE)
    with pytest.raises(ValueError, match=message):
        module._classify_report_roles(report, ["src/a.py"])


@pytest.mark.parametrize(
    ("failure", "message"),
    [
        (OSError("native missing"), "native classify could not be executed: native missing"),
        (SimpleNamespace(returncode=2, stdout=""), "native classify exited with status 2"),
    ],
)
def test_native_classify_execution_failures_are_reported_as_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failure: object, message: str
) -> None:
    from tests.script_main import load_script_module

    module = load_script_module("check_real_host_proof_execution_refusal", GATE)
    monkeypatch.setattr(
        module,
        "resolve_native_core",
        lambda repo_root: SimpleNamespace(path=tmp_path / "repograph"),
    )
    if isinstance(failure, OSError):
        def run(*args: object, **kwargs: object) -> object:
            raise failure

        monkeypatch.setattr(module.subprocess, "run", run)
    else:
        monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: failure)

    path_hits, excluded, decision = module._classify_raw_glob_hits(tmp_path, ["src/a.py"])

    assert path_hits == ["src/a.py"]
    assert excluded == []
    assert decision == {
        "status": "unavailable",
        "native_core": {"status": "unavailable", "reason": message},
    }


@pytest.mark.parametrize(
    "importer", ["plan_release_run", "publish_release_cli", "publish_release_plan"]
)
def test_every_importer_of_build_payload_inherits_the_guard(tmp_path: Path, importer: str) -> None:
    """Each importer's BOUND SYMBOL carries the guard — which is less than call-site
    coverage, and a round-1 bounded review was right to say so.

    All three re-export `build_payload` as `build_real_host_payload`, and this asserts the
    object each of them bound refuses. It does NOT drive any importer's own code path. For
    two of the three that gap is empty (they stop earlier, at
    `publish_release_cli._valid_adapter_data`). For `plan_release_run` it is not: its call
    is behind `if adapter.get("valid")` and inside `except SystemExit`, which would demote
    a refusal to a payload field — so the planner is covered by its OWN guard, pinned in
    `test_release_planner_version_refusal.py`, not by this test.
    """
    from tests.script_main import load_script_module

    module = load_script_module(
        f"{importer}_for_real_host_guard_test",
        ROOT / "skills" / "public" / "release" / "scripts" / f"{importer}.py",
    )
    repo = _repo(tmp_path, "version: 9\n" + DECLARED)
    with pytest.raises(SystemExit) as excinfo:
        module.build_real_host_payload(repo, ["src/a.py"])
    assert "does not speak" in str(excinfo.value)
