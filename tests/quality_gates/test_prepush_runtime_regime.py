"""The docs-only pre-push subset must not file its samples as full-queue ones (#544).

The hook runs the SAME fourteen labels the full queue runs, against a tenth of the
competition. Measured on `local-linux-x86_64-36cpu`, those labels came in 2.1x-4.8x
faster under the subset than under the ~85-gate queue. Because a recorded sample
carries only `{timestamp, elapsed_ms, status}`, both populations landed in one
twenty-sample window and the enforcement median became a function of how many
docs-only pushes happened recently rather than of the code being checked.

This file proves the regime label actually reaches `run-quality.sh` from the real
hook body. `test_quality_runtime_recorder.py` proves what the recorder then does
with it; neither test is sufficient alone, because a regime that is derived
correctly and never passed is indistinguishable from no fix at all.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _seed_prepush_repo(tmp_path: Path) -> Path:
    """A repo whose `pre-push` is this repo's real hook, with the gate stubbed out.

    Only the phases downstream of classification are stubbed. The classification
    itself runs the real `classify_push_diff.py`, so a change that stopped routing
    docs pushes to the subset would surface here rather than being assumed away.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)

    shutil.copy2(ROOT / ".githooks" / "pre-push", repo / ".githooks" / "pre-push")
    for name in ("classify_push_diff.py", "classify_push_diff_lib.py"):
        shutil.copy2(ROOT / "scripts" / name, repo / "scripts" / name)

    # Pre-classification phases the hook runs unconditionally; they are not what
    # this test is about, and each needs the full repo to do anything real.
    for name in ("sync_root_plugin_manifests.py", "validate_current_pointer_freshness.py"):
        (repo / "scripts" / name).write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    # The stub records the ENVIRONMENT the hook handed the runner, which is the
    # fact under test, plus argv so the read-only mode stays visible.
    (repo / "scripts" / "run-quality.sh").write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'python3 -c "'
        "import json,os,sys;"
        "json.dump({'argv':sys.argv[1:],"
        "'labels':os.environ.get('CHARNESS_QUALITY_LABELS',''),"
        "'regime':os.environ.get('CHARNESS_RUNTIME_REGIME',''),"
        "'pre_push':os.environ.get('CHARNESS_PRE_PUSH','')},"
        "open(os.environ['QUALITY_INVOCATION_LOG'],'w'))"
        '" -- "$@"\n',
        encoding="utf-8",
    )
    (repo / "scripts" / "run-quality.sh").chmod(0o755)
    (repo / ".githooks" / "pre-push").chmod(0o755)

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "docs" / "seed.md").write_text("# seed\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "seed")
    return repo


def _run_hook(repo: Path, base_sha: str, head_sha: str, log: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["QUALITY_INVOCATION_LOG"] = str(log)
    env.pop("CHARNESS_RUNTIME_REGIME", None)
    env.pop("CHARNESS_QUALITY_LABELS", None)
    env.pop("CHARNESS_FORCE_FULL_GATE", None)
    return subprocess.run(
        [str(repo / ".githooks" / "pre-push"), "origin", "https://example.invalid/x.git"],
        cwd=repo,
        input=f"refs/heads/main {head_sha} refs/heads/main {base_sha}\n",
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def prepush_repo(tmp_path: Path) -> Path:
    return _seed_prepush_repo(tmp_path)


def test_the_docs_only_subset_names_its_regime_so_its_samples_stay_out_of_the_full_window(
    prepush_repo: Path, tmp_path: Path
) -> None:
    base = _git(prepush_repo, "rev-parse", "HEAD")
    (prepush_repo / "docs" / "note.md").write_text("# note\n", encoding="utf-8")
    _git(prepush_repo, "add", "-A")
    _git(prepush_repo, "commit", "-m", "docs only")
    head = _git(prepush_repo, "rev-parse", "HEAD")

    log = tmp_path / "invocation.json"
    result = _run_hook(prepush_repo, base, head, log)
    assert result.returncode == 0, result.stderr

    payload = json.loads(log.read_text(encoding="utf-8"))
    assert payload["labels"], "the docs-only branch must still pass a label subset"
    assert payload["regime"] == "docs-only", (
        "a subset run that does not name its regime files its cheap samples into the "
        "window the full-queue budgets are enforced against -- the #544 defect"
    )
    assert "--read-only" in payload["argv"]


def test_a_full_gate_push_leaves_the_regime_empty(prepush_repo: Path, tmp_path: Path) -> None:
    # The inverse arm matters as much: if the full queue ever acquired a regime,
    # every budget in the adapter would be enforced against an empty window and
    # the gate would silently stop having teeth.
    #
    # Honest about its own strength: this arm kills no mutant of the CURRENT
    # change, because with the regime popped from the environment the assertion
    # also holds with the whole fix reverted. It constrains a FUTURE edit that
    # regimes the full-gate branch. Do not count it as coverage of the fix.
    base = _git(prepush_repo, "rev-parse", "HEAD")
    (prepush_repo / "scripts" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _git(prepush_repo, "add", "-A")
    _git(prepush_repo, "commit", "-m", "code change")
    head = _git(prepush_repo, "rev-parse", "HEAD")

    log = tmp_path / "invocation.json"
    result = _run_hook(prepush_repo, base, head, log)
    assert result.returncode == 0, result.stderr

    payload = json.loads(log.read_text(encoding="utf-8"))
    assert payload["labels"] == "", "a code push must run the full queue, unfiltered"
    assert payload["regime"] == ""
