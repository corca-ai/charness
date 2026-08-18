"""The requested-review gate refuses an unspeakable adapter version instead of
reporting the opposite of what the repo declared.

This is the sharpest shape in the adapter-consumer debt: a gate that reads a payload it
could not actually read, finds the charness default, and reports `not_configured` —
"this repo declares none" — over a repo that declared a command AND a
`block-if-unconfigured` policy, at exit 0. The enforcement it was supposed to apply
downgrades itself to advisory, and nothing says so.

Measured on the real CLI before the repair, not argued. The guard sits at the READ SITE
rather than at `main()` because this gate has three entrypoints: its own CLI, and
`plan_release_run` and `publish_release_cli`, which both import `build_payload`
directly. A refusal in `main()` would have left two of them reading defaults.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

GATE = ROOT / "skills" / "public" / "release" / "scripts" / "check_requested_review_gate.py"


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text("# release\n", encoding="utf-8")
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "release-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GATE), "--repo-root", str(repo)], capture_output=True, text=True
    )


DECLARED = 'requested_review_commands:\n  - echo declared\nrequested_review_policy: block-if-unconfigured\n'


def test_an_unspeakable_version_refuses_rather_than_reporting_not_configured(tmp_path: Path) -> None:
    # The behavioral flip this row is paid down by. Before the guard this exact input
    # printed `configuration status: not_configured` and warned that enforcement was
    # advisory-only, exit 0 — over a repo that declared a command.
    result = _run(_repo(tmp_path, "version: 9\n" + DECLARED))
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    assert "release-adapter.yaml" in result.stderr
    assert "not_configured" not in result.stdout


def test_a_speakable_version_still_reports_what_the_repo_declared(tmp_path: Path) -> None:
    # The polarity control. Every assertion above is satisfied by a gate that refuses
    # everything; this is the one that would catch it.
    result = _run(_repo(tmp_path, "version: 1\n" + DECLARED))
    assert result.returncode == 0, result.stderr
    assert "configuration status: configured" in result.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    # The opt-in design survives: a repo that declares nothing is not a repo whose
    # declaration could not be read, and conflating them would refuse every consumer
    # that never opted in.
    result = _run(_repo(tmp_path, None))
    assert result.returncode == 0, result.stderr
    assert "configuration status: not_configured" in result.stdout


@pytest.mark.parametrize("importer", ["plan_release_run", "publish_release_cli"])
def test_every_importer_of_build_payload_inherits_the_guard(tmp_path: Path, importer: str) -> None:
    """The call-site coverage this row's probe record claims.

    `build_payload` has three entrypoints and the guard is inside it, so the two modules
    that import it directly cannot be guarded at one call site and unguarded at another —
    which is the failure class the census's own blind note names.
    """
    from tests.script_main import load_script_module

    module = load_script_module(
        f"{importer}_for_guard_test",
        ROOT / "skills" / "public" / "release" / "scripts" / f"{importer}.py",
    )
    repo = _repo(tmp_path, "version: 9\n" + DECLARED)
    with pytest.raises(SystemExit) as excinfo:
        module.build_review_gate_payload(repo)
    assert "does not speak" in str(excinfo.value)
