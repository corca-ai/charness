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
import subprocess
import sys
from pathlib import Path

import pytest

from tests.quality_gates.prepush_close_keyword_fixtures import head as _head
from tests.script_closure import script_import_closure

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.boundary_contract(
    reason=(
        "exercise the repository-owned pre-push hook as a real process because stdin, "
        "environment, exit status, and one-shot receipt consumption are its public boundary"
    )
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.email=test@example.com", "-c", "user.name=Test", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _seed_prepush_repo(tmp_path: Path) -> Path:
    """A repo whose `pre-push` is this repo's real hook, with the gate stubbed out.

    Only the phases downstream of classification are stubbed. The classification
    itself runs the real `classify_push_diff.py`, so a change that stopped routing
    docs pushes to the subset would surface here rather than being assumed away.
    """
    from .repo_shapes import install_committed_repo

    files = {
        ".githooks/pre-push": (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8"),
        ".githooks/runtime-env.sh": (ROOT / ".githooks" / "runtime-env.sh").read_text(
            encoding="utf-8"
        ),
        "docs/seed.md": "# seed\n",
        ".gitignore": "plugins/\n",
        "plugins/charness/plugin.txt": "seed\n",
        "scripts/sync_root_plugin_manifests.py": "#!/usr/bin/env python3\n",
        "scripts/validate_current_pointer_freshness.py": "#!/usr/bin/env python3\n",
        "scripts/run_quality_engine.py": (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--print-docs-only-labels' in sys.argv:\n"
            "    print('check-docs')\n"
        ),
        # Records hook stdin so the classifier and the guard both see the range.
        "scripts/prepush_close_keyword_guard.py": (
            "#!/usr/bin/env python3\n"
            "import os, sys\n"
            "open(os.environ['GUARD_STDIN_LOG'], 'w').write(sys.stdin.read())\n"
        ),
        "scripts/run-quality.sh": (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'python3 -c "'
            "import json,os,sys;"
            "json.dump({'argv':sys.argv[1:],"
            "'labels':os.environ.get('CHARNESS_QUALITY_LABELS',''),"
            "'regime':os.environ.get('CHARNESS_RUNTIME_REGIME','')},"
            "open(os.environ['QUALITY_INVOCATION_LOG'],'w'))"
            '" -- "$@"\n'
        ),
    }
    # DERIVED, not listed. `yaml_output.py` once had to be added here BY HAND after
    # `classify_push_diff.py` began importing `emit_yaml` at module scope -- a
    # synthetic repo without it fails at import and never reaches classification.
    # A literal list restates the import graph and goes stale on the next such
    # import; deriving it removes the restatement rather than repairing it again.
    for name in script_import_closure(
        "classify_push_diff.py", "prepush_quality_receipt.py"
    ):
        files[f"scripts/{name}"] = (ROOT / "scripts" / name).read_text(encoding="utf-8")

    return install_committed_repo(
        tmp_path / "repo",
        files,
        executable=(".githooks/pre-push", "scripts/run-quality.sh"),
    )


def _run_hook(
    repo: Path,
    base_sha: str,
    head_sha: str,
    log: Path,
    *,
    receipt: Path | None = None,
    push_input: str | None = None,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["QUALITY_INVOCATION_LOG"] = str(log)
    env["GUARD_STDIN_LOG"] = str(log.with_name("guard-stdin.txt"))
    env.pop("CHARNESS_RUNTIME_REGIME", None)
    env.pop("CHARNESS_QUALITY_LABELS", None)
    env.pop("CHARNESS_FORCE_FULL_GATE", None)
    env.pop("CHARNESS_PREPUSH_QUALITY_RECEIPT", None)
    if receipt is not None:
        env["CHARNESS_PREPUSH_QUALITY_RECEIPT"] = str(receipt)
    return subprocess.run(
        [str(repo / ".githooks" / "pre-push"), "origin", "https://example.invalid/x.git"],
        cwd=repo,
        input=push_input or f"refs/heads/main {head_sha} refs/heads/main {base_sha}\n",
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
    base = _head(prepush_repo)
    (prepush_repo / "docs" / "note.md").write_text("# note\n", encoding="utf-8")
    _git(prepush_repo, "add", "-A")
    _git(prepush_repo, "commit", "-m", "docs only")
    head = _head(prepush_repo)

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


def test_release_receipt_reuses_quality_but_still_runs_the_irreversible_guard(
    prepush_repo: Path, tmp_path: Path
) -> None:
    base = _head(prepush_repo)
    (prepush_repo / "scripts" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _git(prepush_repo, "add", "scripts/thing.py")
    _git(prepush_repo, "commit", "-m", "code change")
    head = _head(prepush_repo)
    receipt = tmp_path / "quality-receipt.json"
    semantic = tmp_path / "semantic-quality.json"
    semantic.write_text(
        json.dumps(
            {
                "surface": "quality",
                "status": "pass",
                "measured_scope": ["pytest-release", "validate-skills"],
                "adverse_subjects": [],
                "unproven_subjects": [],
                "cause": None,
                "effective_exit_code": 0,
                "details": {
                    "passed": 2,
                    "failed": 0,
                    "elapsed": "1s",
                    "execution_mode": "read-only",
                    "release": True,
                    "full_queue": True,
                    "non_claim": "",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            str(prepush_repo / "scripts" / "prepush_quality_receipt.py"),
            "seal",
            "--repo-root",
            str(prepush_repo),
            "--quality-command",
            "./scripts/run-quality.sh --release",
            "--semantic-receipt",
            str(semantic),
            "--materialized-root",
            "plugins/charness",
            "--output",
            str(receipt),
        ],
        cwd=prepush_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    unestablished = json.loads(semantic.read_text(encoding="utf-8"))
    unestablished["status"] = "unestablished"
    unestablished["unproven_subjects"] = ["release-changed-line-coverage"]
    unestablished_path = tmp_path / "unestablished-quality.json"
    unestablished_path.write_text(json.dumps(unestablished) + "\n", encoding="utf-8")
    refused = subprocess.run(
        [
            sys.executable,
            str(prepush_repo / "scripts" / "prepush_quality_receipt.py"),
            "seal",
            "--repo-root",
            str(prepush_repo),
            "--quality-command",
            "./scripts/run-quality.sh --release",
            "--semantic-receipt",
            str(unestablished_path),
            "--materialized-root",
            "plugins/charness",
            "--output",
            str(tmp_path / "must-not-exist.json"),
        ],
        cwd=prepush_repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 1
    assert "not an established release/full pass" in refused.stderr

    log = tmp_path / "quality-invocation.json"
    multi_ref_input = (
        f"refs/heads/main {head} refs/heads/main {base}\n"
        f"refs/tags/v1 {base} refs/tags/v1 {'0' * 40}\n"
    )
    result = _run_hook(
        prepush_repo, base, head, log, receipt=receipt, push_input=multi_ref_input
    )

    assert result.returncode == 0, result.stderr
    assert not log.exists(), "a valid release receipt must omit the duplicate broad gate"
    assert "reusing release quality receipt" in result.stdout
    assert not receipt.exists(), "a successful hook validation consumes its one-push receipt"
    assert (tmp_path / "guard-stdin.txt").read_text(encoding="utf-8") == multi_ref_input

    export_receipt = tmp_path / "export-quality-receipt.json"
    subprocess.run(
        [
            sys.executable,
            str(prepush_repo / "scripts" / "prepush_quality_receipt.py"),
            "seal",
            "--repo-root",
            str(prepush_repo),
            "--quality-command",
            "./scripts/run-quality.sh --release",
            "--semantic-receipt",
            str(semantic),
            "--materialized-root",
            "plugins/charness",
            "--output",
            str(export_receipt),
        ],
        cwd=prepush_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (prepush_repo / "plugins" / "charness" / "plugin.txt").write_text(
        "changed after quality\n", encoding="utf-8"
    )
    export_fallback = _run_hook(prepush_repo, base, head, log, receipt=export_receipt)
    assert export_fallback.returncode == 0, export_fallback.stderr
    assert "materialized plugin export changed" in export_fallback.stderr
    (prepush_repo / "plugins" / "charness" / "plugin.txt").write_text(
        "seed\n", encoding="utf-8"
    )

    stale_receipt = tmp_path / "stale-quality-receipt.json"
    subprocess.run(
        [
            sys.executable,
            str(prepush_repo / "scripts" / "prepush_quality_receipt.py"),
            "seal",
            "--repo-root",
            str(prepush_repo),
            "--quality-command",
            "./scripts/run-quality.sh --release",
            "--semantic-receipt",
            str(semantic),
            "--materialized-root",
            "plugins/charness",
            "--output",
            str(stale_receipt),
        ],
        cwd=prepush_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (prepush_repo / "scripts" / "later.py").write_text("x = 2\n", encoding="utf-8")
    _git(prepush_repo, "add", "scripts/later.py")
    _git(prepush_repo, "commit", "-m", "later change")
    later = _head(prepush_repo)
    fallback = _run_hook(prepush_repo, head, later, log, receipt=stale_receipt)

    assert fallback.returncode == 0, fallback.stderr
    assert "receipt was not reusable" in fallback.stderr
    assert json.loads(log.read_text(encoding="utf-8"))["argv"][-2:] == ["--full", "--read-only"]


def test_a_full_gate_push_leaves_the_regime_empty(prepush_repo: Path, tmp_path: Path) -> None:
    # The inverse arm matters as much: if the full queue ever acquired a regime,
    # every budget in the adapter would be enforced against an empty window and
    # the gate would silently stop having teeth.
    #
    # Honest about its own strength: this arm kills no mutant of the CURRENT
    # change, because with the regime popped from the environment the assertion
    # also holds with the whole fix reverted. It constrains a FUTURE edit that
    # regimes the full-gate branch. Do not count it as coverage of the fix.
    base = _head(prepush_repo)
    (prepush_repo / "scripts" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _git(prepush_repo, "add", "-A")
    _git(prepush_repo, "commit", "-m", "code change")
    head = _head(prepush_repo)

    log = tmp_path / "invocation.json"
    result = _run_hook(prepush_repo, base, head, log)
    assert result.returncode == 0, result.stderr

    payload = json.loads(log.read_text(encoding="utf-8"))
    assert payload["labels"] == "", "a code push must run the full queue, unfiltered"
    assert payload["regime"] == ""


def test_both_stdin_consumers_receive_the_push_range(prepush_repo: Path, tmp_path: Path) -> None:
    """The close-keyword guard and the diff classifier both get the range.

    A git hook's stdin is a pipe read once. Before the guard existed the classifier
    read it directly; adding a second consumer in front of it would have drained it,
    and the classifier would have seen no refs, taken its `saw_ref == 0` branch, and
    forced the full gate on every push -- a silent regime regression this file's other
    two tests would still have passed, because both drive the docs/code branch through
    file contents rather than through stdin. Reading stdin once and replaying it is
    what makes both true at the same time, and this is the assertion that holds it.
    """
    base = _head(prepush_repo)
    (prepush_repo / "docs" / "note.md").write_text("# note\n", encoding="utf-8")
    _git(prepush_repo, "add", "-A")
    _git(prepush_repo, "commit", "-m", "docs only")
    head = _head(prepush_repo)

    log = tmp_path / "invocation.json"
    result = _run_hook(prepush_repo, base, head, log)
    assert result.returncode == 0, result.stderr

    guard_stdin = log.with_name("guard-stdin.txt").read_text(encoding="utf-8")
    assert guard_stdin.split() == ["refs/heads/main", head, "refs/heads/main", base]
    # And the classifier downstream of it still saw the same range: `docs-only` is
    # reachable only through the ref pair, so this asserts the replay, not a default.
    assert json.loads(log.read_text(encoding="utf-8"))["regime"] == "docs-only"
