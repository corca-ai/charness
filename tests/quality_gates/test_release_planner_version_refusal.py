"""The release planner refuses an unspeakable adapter version at its own read site, not
by inheritance from a callee.

This row is deliberately recorded as WEAKER than the three gate rows it follows. Measured
at `dd5b6dee9`, the planner did not go silent under a refused version: it printed
`next_action=repair_adapter: Release adapter is invalid.` at exit 0 and left the two
`valid`-gated evidence packets null. What it emitted anyway was a plan asserting
`package_id: <the temp directory's own name>`, two paths under `packaging/` and `plugins/`
that do not exist, and `blockers: []`.

The row for `current_release` ALONE already made this exit 1, by inheritance:
`build_release_payload` runs before the three unconditional `data` reads and its
`SystemExit` escapes the `except Exception` around it. The `check_real_host_proof` row
cannot have contributed — its call here is behind `if adapter.get("valid")` and inside
`except SystemExit`, which demotes a refusal to a payload field — and a round-1 bounded
review caught three surfaces crediting it. That inheritance is real and
was measured — and it is POSITIONAL. `test_the_refusal_is_this_file_s_own` is the test
that separates the two, by proving the refusal survives a callee that does not refuse.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

PLANNER = ROOT / "skills" / "public" / "release" / "scripts" / "plan_release_run.py"

DECLARED = 'release_record_path: charness-artifacts/release/mine.md\nreal_host_required_path_globs:\n  - "src/**"\n'


def _repo(tmp_path: Path, adapter: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(adapter, encoding="utf-8")
    # The planner asks git for the current branch on the arm that reaches a plan. Without
    # a repo here the speakable-version control would fail on git rather than on the
    # behavior it exists to pin — and a control that fails for the wrong reason proves
    # nothing about the refusal above it.
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PLANNER), "--repo-root", str(repo)], capture_output=True, text=True
    )


def test_an_unspeakable_version_refuses_instead_of_planning_from_defaults(tmp_path: Path) -> None:
    result = _run(_repo(tmp_path, "version: 9\n" + DECLARED))
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    assert "next_action" not in result.stdout


def test_a_speakable_but_otherwise_invalid_adapter_still_plans(tmp_path: Path) -> None:
    """The affordance this planner exists for is preserved.

    The refusal is narrow to a version this reader cannot speak — the one case where the
    planner cannot know what the repo declared. An adapter that is speakable but broken in
    some other way still gets a plan and its own next action, which is what an operator
    runs this command to obtain.
    """
    result = _run(_repo(tmp_path, "version: 1\nrelease_record_path: 12345\n"))
    assert result.returncode == 0, result.stderr
    assert "next_action=" in result.stdout


def test_the_refusal_is_this_file_s_own_not_inherited_from_a_callee(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutation this row is actually about.

    `build_release_payload` is called near the top of `build_plan` and already refuses,
    so the CLI test above passes with or without the guard in this file. Replacing that
    callee with one that does NOT refuse isolates the guard: with it, `build_plan` still
    raises; without it, the planner falls through to the three unconditional `data` reads
    and plans from charness defaults.

    The Namespace comes from the planner's OWN `parse_args`, not hand-built. A hand-built
    one made the mutant die on a missing attribute — a kill for the wrong reason, which
    would have let a later refactor break this proof without failing it.
    """
    from tests.script_main import load_script_module

    module = load_script_module("plan_release_run_for_guard_test", PLANNER)
    module.build_release_payload = lambda repo_root: {"surface_versions": {"packaging_manifest": "1.2.3"}}
    module.build_real_host_payload = lambda repo_root, paths: {}
    module.build_review_gate_payload = lambda repo_root, run_commands=True: {}
    repo = _repo(tmp_path, "version: 9\n" + DECLARED)
    monkeypatch.setattr(sys, "argv", ["plan_release_run.py", "--repo-root", str(repo)])
    args = module.parse_args()
    with pytest.raises(SystemExit) as excinfo:
        module.build_plan(args)
    assert "does not speak" in str(excinfo.value)
