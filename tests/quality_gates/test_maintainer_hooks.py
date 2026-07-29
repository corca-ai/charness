"""Maintainer git-hook setup: installation, and whether the installed hook still
does the thing it was installed to do.

Split out of `test_quality_runner.py` when that file passed its length cap. This
is a cohesive concept (`scripts/install-git-hooks.sh` +
`scripts/validate_maintainer_setup.py` + `.githooks/`), not a mechanical spill:
the runner tests next door exercise gate SELECTION and verdict rendering, while
these exercise whether the hook that invokes the runner exists and is armed.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

from .support import ROOT


def test_install_git_hooks_sets_core_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    shutil.copy2(ROOT / ".githooks" / "pre-commit", repo / ".githooks" / "pre-commit")
    shutil.copy2(ROOT / ".githooks" / "commit-msg", repo / ".githooks" / "commit-msg")
    shutil.copy2(ROOT / ".githooks" / "pre-push", repo / ".githooks" / "pre-push")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    result = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    hookspath = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert hookspath.stdout.strip() == str((repo / ".githooks").resolve())


def test_install_git_hooks_materializes_consumer_commit_msg_hook(tmp_path: Path) -> None:
    source = tmp_path / "source"
    consumer = tmp_path / "consumer"
    (source / "scripts").mkdir(parents=True)
    (consumer / ".git").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", source / "scripts" / "install-git-hooks.sh")
    checker = source / "scripts" / "check_issue_closeout_commit_msg.py"
    checker.write_text("#!/usr/bin/env python3\nprint('checker')\n", encoding="utf-8")
    checker.chmod(0o755)
    subprocess.run(["git", "init"], cwd=consumer, check=True, capture_output=True, text=True)

    result = subprocess.run(
        ["bash", str(source / "scripts" / "install-git-hooks.sh"), "--repo-root", str(consumer)],
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    hook = consumer / ".githooks" / "commit-msg"
    assert hook.is_file()
    assert str(checker) in hook.read_text(encoding="utf-8")
    hookspath = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=consumer,
        check=True,
        capture_output=True,
        text=True,
    )
    assert hookspath.stdout.strip() == str((consumer / ".githooks").resolve())


def test_validate_maintainer_setup_requires_installed_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "validate_maintainer_setup.py", repo / "scripts" / "validate_maintainer_setup.py")
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    shutil.copy2(ROOT / ".githooks" / "pre-commit", repo / ".githooks" / "pre-commit")
    shutil.copy2(ROOT / ".githooks" / "commit-msg", repo / ".githooks" / "commit-msg")
    shutil.copy2(ROOT / ".githooks" / "pre-push", repo / ".githooks" / "pre-push")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    missing = subprocess.run(
        ["python3", "scripts/validate_maintainer_setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert missing.returncode == 1
    assert "install-git-hooks.sh" in missing.stderr

    install = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert install.returncode == 0, install.stderr

    ready = subprocess.run(
        ["python3", "scripts/validate_maintainer_setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ready.returncode == 0, ready.stderr


def _seed_source_repo_for_maintainer_setup(tmp_path: Path, pre_push_text: str) -> Path:
    """A charness-source-shaped clone whose `pre-push` body is under test."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    (repo / "packaging").mkdir(parents=True)
    (repo / "plugins" / "charness").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text("{}\n", encoding="utf-8")
    shutil.copy2(ROOT / "scripts" / "validate_maintainer_setup.py", repo / "scripts" / "validate_maintainer_setup.py")
    for name in ("pre-commit", "commit-msg"):
        shutil.copy2(ROOT / ".githooks" / name, repo / ".githooks" / name)
    (repo / ".githooks" / "pre-push").write_text(pre_push_text, encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _run_maintainer_setup(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "scripts/validate_maintainer_setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def test_validate_maintainer_setup_refuses_a_pre_push_hook_that_stopped_arming_the_lane(tmp_path: Path) -> None:
    """Existence was the only thing checked, so deleting one env prefix disarmed
    the push-time changed-line refusal with this gate green.

    Reproduced against a copy of this repo's real hook before the fix: the
    disarmed hook printed `Validated maintainer hook setup` and exited 0.
    """
    hook = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    assert "CHARNESS_PRE_PUSH=1 " in hook, "the real hook must arm the lane, or this test proves nothing"

    armed = _run_maintainer_setup(_seed_source_repo_for_maintainer_setup(tmp_path / "armed", hook))
    assert armed.returncode == 0, armed.stderr

    disarmed = _run_maintainer_setup(
        _seed_source_repo_for_maintainer_setup(tmp_path / "disarmed", hook.replace("CHARNESS_PRE_PUSH=1 ", ""))
    )
    assert disarmed.returncode == 1
    assert "without arming the push-time changed-line refusal" in disarmed.stderr


def test_the_content_check_actually_runs_in_this_repo() -> None:
    """`is_charness_source_repo` is what turns the content check on.

    A packaging refactor that moved `packaging/charness.json` or
    `plugins/charness/` would silently drop `pre-push` from the expected set and
    take the arming check with it, leaving this gate green over an unchecked
    hook. Rekeying the check on hook EXISTENCE was rejected instead of applied:
    a consumer repo can own an unrelated `.githooks/pre-push` (cautilus runs
    `npm run verify` in its own), and this gate must not demand that it invoke
    charness's runner. So the scoping stays, and this pins that it resolves
    TRUE here.
    """
    module = import_repo_module(__file__, "scripts.validate_maintainer_setup")
    assert module.is_charness_source_repo(ROOT) is True
    assert (ROOT / ".githooks" / "pre-push").is_file()


def test_validate_maintainer_setup_reads_invocations_not_mentions() -> None:
    """A mention is not an invocation, and the empty case is not a pass.

    The real hook echoes `./scripts/run-quality.sh` in a status line two lines
    above the real call, so counting mentions would fail on the echo; and a hook
    that stopped calling the runner entirely would satisfy "every invocation is
    armed" vacuously — the empty-input-passes class this lane exists to refuse.
    """
    module = import_repo_module(__file__, "scripts.validate_maintainer_setup")
    invocations = module.quality_runner_invocations

    hook = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    armed, unarmed, unclear, swallowed = invocations(hook)
    assert len(armed) == 2, armed  # the docs-only branch and the full branch
    assert not unarmed and not unclear and not swallowed, (unarmed, unclear, swallowed)
    assert not any("echo" in line for line in armed)

    # An env prefix that is not the arming one is an invocation, just unarmed.
    _, partial_unarmed, _, _ = invocations('CHARNESS_QUALITY_LABELS="x" ./scripts/run-quality.sh --read-only\n')
    assert len(partial_unarmed) == 1

    # A comment naming the variable is not an invocation and does not arm one.
    commented_armed, commented_unarmed, _, _ = invocations(
        "# CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh\n./scripts/run-quality.sh --read-only\n"
    )
    assert commented_armed == [] and len(commented_unarmed) == 1

    # The var named inside ANOTHER variable's quoted value does not arm anything.
    quoted_armed, quoted_unarmed, _, _ = invocations(
        'CHARNESS_QUALITY_LABELS="CHARNESS_PRE_PUSH=1" ./scripts/run-quality.sh\n'
    )
    assert quoted_armed == [] and len(quoted_unarmed) == 1

    # Shell last-assignment-wins: the gate must read the value the shell would.
    reassigned_armed, reassigned_unarmed, _, _ = invocations(
        "CHARNESS_PRE_PUSH=1 CHARNESS_PRE_PUSH=0 ./scripts/run-quality.sh\n"
    )
    assert reassigned_armed == [] and len(reassigned_unarmed) == 1

    # An escaped quote inside a double-quoted echo must not desync the splitter
    # into fabricating an ARMED entry out of a string (round 2 found it doing so).
    assert invocations(
        'echo "quality runner \\"; CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only"\n'
    ) == ([], [], [], [])

    # No invocation at all is the empty case; the caller must treat it as an error.
    assert invocations('echo "./scripts/run-quality.sh --read-only"\n') == ([], [], [], [])


DISARMING_REWRITES = {
    # Round 1: the parser knew ONE invocation spelling and silently skipped the
    # rest, so each of these left the OTHER branch armed and the gate green.
    "exec": "  exec ./scripts/run-quality.sh --read-only",
    "repo-root path": '  "$REPO_ROOT"/scripts/run-quality.sh --read-only',
    "if-not": "  if ! ./scripts/run-quality.sh --read-only; then :; fi",
    "pipe into runner": "  true | ./scripts/run-quality.sh --read-only",
    "via variable": "  RUNNER=./scripts/run-quality.sh; $RUNNER --read-only",
    "prefix deleted": "  ./scripts/run-quality.sh --read-only",
    # Round 2, reading round 1's repair and finding the same class in it.
    "comment ending in backslash": "  # CHARNESS_PRE_PUSH=1 \\\n  ./scripts/run-quality.sh --read-only",
    "fake heredoc in a comment": "  # advice uses <<MSG ... MSG when tty\n  ./scripts/run-quality.sh --read-only",
    "fake heredoc in a string": '  echo "we emit <<MSG blocks"\n  ./scripts/run-quality.sh --read-only',
    "left shift over a variable": "  mask=$(( 1 << bits ))\n  ./scripts/run-quality.sh --read-only",
    "a different file": "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh.disabled --read-only",
    "a runner outside the repo": '  CHARNESS_PRE_PUSH=1 "$VENDOR_ROOT"/scripts/run-quality.sh --read-only',
    # Armed, but the verdict cannot block the push — a more complete disarm than
    # dropping the variable.
    "verdict swallowed by || true": "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only || true",
    "verdict backgrounded": "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only &",
    "verdict piped away": "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only | tee /tmp/q.log",
}

LEGITIMATE_REWRITES = {
    "line continuation": "  CHARNESS_PRE_PUSH=1 \\\n    ./scripts/run-quality.sh --read-only",
    "env spelling": "  env CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only",
    "export on an earlier line": "  export CHARNESS_PRE_PUSH=1\n  ./scripts/run-quality.sh --read-only",
    "defensive -x guard": (
        "  if [[ ! -x ./scripts/run-quality.sh ]]; then echo missing; exit 1; fi\n"
        "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only"
    ),
    "quoted heredoc advice": (
        "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only\n"
        "  cat <<'EOF'\n  tip: ./scripts/run-quality.sh --read-only\nEOF"
    ),
    "unquoted heredoc advice": (
        "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only\n"
        "  cat <<EOF\n  tip: ./scripts/run-quality.sh\nEOF"
    ),
    "left shift over a literal": (
        "  mask=$(( 1 << 2 ))\n  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only"
    ),
    "stderr redirect": "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only 2>&1",
}


def _rewrite_full_branch(replacement: str) -> str:
    hook = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    full_branch = "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only"
    assert full_branch in hook, "the full-gate branch moved; these rewrites are stale"
    return hook.replace(full_branch, replacement)


@pytest.mark.parametrize("label", sorted(DISARMING_REWRITES))
def test_every_known_disarm_of_one_branch_is_reported(label: str) -> None:
    """The hook arms TWO branches, so disarming one leaves the other armed.

    Every rewrite here was executed against the version of the gate that let it
    through — the first eight against round 1's, the rest against round 1's
    repair, which round 2 caught carrying the same class. None is hypothetical.
    """
    module = import_repo_module(__file__, "scripts.validate_maintainer_setup")
    armed, unarmed, unclear, swallowed = module.quality_runner_invocations(
        _rewrite_full_branch(DISARMING_REWRITES[label])
    )
    assert unarmed or unclear or swallowed, f"{label} was not reported; armed={armed}"


@pytest.mark.parametrize("label", sorted(LEGITIMATE_REWRITES))
def test_legitimate_hook_spellings_do_not_false_fire(label: str) -> None:
    """A false stop is how a lane gets disabled — `scripts/run-quality.sh:654`
    records that happening to this very lane, so the no-false-positive half is
    load-bearing rather than politeness."""
    module = import_repo_module(__file__, "scripts.validate_maintainer_setup")
    armed, unarmed, unclear, swallowed = module.quality_runner_invocations(
        _rewrite_full_branch(LEGITIMATE_REWRITES[label])
    )
    assert len(armed) == 2, f"{label}: armed={armed}"
    assert not unarmed and not unclear and not swallowed, (unarmed, unclear, swallowed)


def test_validate_maintainer_setup_refuses_a_single_disarmed_branch(tmp_path: Path) -> None:
    """The hook arms two branches; disarming ONE must still fail.

    This is the arm the zero-invocation backstop cannot catch, because the other
    branch keeps `armed` non-empty.
    """
    hook = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    full_branch = "  CHARNESS_PRE_PUSH=1 ./scripts/run-quality.sh --read-only"
    assert full_branch in hook
    disarmed = hook.replace(full_branch, "  ./scripts/run-quality.sh --read-only")
    result = _run_maintainer_setup(_seed_source_repo_for_maintainer_setup(tmp_path, disarmed))
    assert result.returncode == 1
    assert "without arming the push-time changed-line refusal" in result.stderr


def test_validate_maintainer_setup_refuses_a_pre_push_hook_that_stopped_calling_the_runner(tmp_path: Path) -> None:
    hook = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    gutted = "\n".join(
        "true" if "run-quality.sh" in line and not line.strip().startswith(("#", "echo")) else line
        for line in hook.splitlines()
    )
    result = _run_maintainer_setup(_seed_source_repo_for_maintainer_setup(tmp_path, gutted + "\n"))
    assert result.returncode == 1
    assert "no longer invokes `scripts/run-quality.sh` at all" in result.stderr


def test_pre_push_arming_var_is_the_one_the_runner_actually_reads() -> None:
    """The hook, the runner, and this gate are three surfaces naming one var.

    Renaming it in `run-quality.sh` alone would leave the gate pinning a var
    nothing reads — green, and enforcing nothing.
    """
    module = import_repo_module(__file__, "scripts.validate_maintainer_setup")
    runner = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    guard = f'"${{{module.PRE_PUSH_ARMING_VAR}:-0}}" == "1"'
    assert guard in runner
    # The flag must be added INSIDE the guarded branch. `--refuse-unestablished`
    # also appears in a comment four lines above, so asserting mere presence
    # would stay green with the branch body gutted.
    body = runner.split(guard, 1)[1].split("fi", 1)[0]
    assert "--refuse-unestablished" in body, body


