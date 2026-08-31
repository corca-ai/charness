"""The HITL bootstrap refuses an unspeakable adapter version before it WRITES a policy
the repo never declared into a durable session artifact.

Measured on the real CLI: a repo declaring `require_explicit_apply: false` under a refused
version got `require_explicit_apply: true` and `apply_mode: explicit-after-all-chunks`
written into `state.yaml`, exit 0.

This row's harm is asymmetric, and the tests say so rather than dramatizing it. The
reader's fallback is `.get("require_explicit_apply", True)`, so an unspeakable version
always lands on the STRICTER apply policy — it cannot weaken this control. What it does is
persist a policy the repo never declared into an artifact that an operator and later runs
read as the repo's own contract, and silently run a different workflow than the one asked
for.

The guard sits before `mkdir`, earlier than the other rows in this slice need to be,
because everything after it writes: a refusal after the session directory exists leaves a
half-bootstrapped session an operator then has to tell apart from a real one.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from .support import ROOT, run_script

BOOTSTRAP = ROOT / "skills" / "public" / "hitl" / "scripts" / "bootstrap_review.py"


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "README.md").write_text("# probe\n", encoding="utf-8")
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "hitl-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(repo: Path, session_id: str) -> subprocess.CompletedProcess:
    return run_script(
        str(BOOTSTRAP),
        "--repo-root",
        str(repo),
        "--session-id",
        session_id,
        "--target",
        "README.md",
    )


def test_an_unspeakable_version_refuses_before_writing_the_session(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "version: 9\nrequire_explicit_apply: false\n")
    result = _run(repo, "probe")
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    assert "hitl-adapter.yaml" in result.stderr
    # The half-bootstrapped-session check. A guard placed after `mkdir` would pass every
    # assertion above and still leave this directory behind.
    assert not (repo / ".charness" / "hitl" / "runtime" / "probe").exists()


def test_a_speakable_version_still_persists_what_the_repo_declared(tmp_path: Path) -> None:
    # The polarity control, and the reading that shows the refused-version arm was writing
    # the OPPOSITE of the declaration rather than merely omitting it.
    repo = _repo(tmp_path, "version: 1\nrequire_explicit_apply: false\n")
    result = _run(repo, "ctl")
    assert result.returncode == 0, result.stderr
    state = (repo / ".charness" / "hitl" / "runtime" / "ctl" / "state.yaml").read_text(encoding="utf-8")
    assert "require_explicit_apply: false" in state
    assert "apply_mode: accepted-chunk-or-final-apply-boundary" in state


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    # The documented default survives for a repo that never opted in. `True` here is the
    # reader's own fallback, not a repo declaration, and nothing claims otherwise.
    repo = _repo(tmp_path, None)
    result = _run(repo, "ctl")
    assert result.returncode == 0, result.stderr
    state = (repo / ".charness" / "hitl" / "runtime" / "ctl" / "state.yaml").read_text(encoding="utf-8")
    assert "require_explicit_apply: true" in state


def test_a_parser_refusal_reaches_the_same_guard_before_any_write(tmp_path: Path) -> None:
    """The write case for the round-1 review's blocker.

    `version: !!int 9` makes the parser refuse the document; the resolver answers with
    charness defaults, and before the guard keyed on the condition this wrote
    `require_explicit_apply: true` into `state.yaml` at exit 0 over a repo declaring
    `false`. The session directory must be absent for the same reason as above.
    """
    repo = _repo(tmp_path, "version: !!int 9\nrequire_explicit_apply: false\n")
    result = _run(repo, "parsefail")
    assert result.returncode == 1, result.stdout
    assert "could not be parsed" in result.stderr
    assert not (repo / ".charness" / "hitl" / "runtime" / "parsefail").exists()
