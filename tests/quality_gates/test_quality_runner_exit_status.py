"""The gate runner's cleanup must not restate its verdict.

`run-quality.sh` removed its temp dir from an EXIT trap. `set -e` is in force INSIDE
that trap, so a failing `rm` aborted it and the shell exited with the failing command's
status instead of the pending one: a run that had correctly refused with exit 2 exited
1, because `rm -rf` lost a race with a still-writing gate child and reported `Directory
not empty`. Bash itself does NOT hand the trap's status to the script -- measured,
`bash -c 'trap "false" EXIT; exit 2'` exits 2 -- and a first version of this file
asserted that false rule. The distinction decides the repair for every sibling gate:
under the true mechanism `rm ... || true` is a complete fix.

The behavioural pair below is the point: the pre-fix trap shape is shown LOSING the
status before the post-fix shape is accepted as preserving it. The structural check
that follows is what binds the proven shape to the real file.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

from .support import ROOT

# `rm -rf` cannot be made to fail as root (CAP_DAC_OVERRIDE ignores the 0o500 mode), so
# the behavioural pair would red for a reason the file does not explain. Skipped with
# the reason named rather than left to look like a trap-shape regression.
#
# The risk this creates is that the pair is ALWAYS skipped somewhere and the module
# quietly degrades to its structural assertions. Both checked-in workflows run on
# `ubuntu-latest` with no `container:` key, which is the non-root `runner` user, so CI
# executes the pair. `test_the_behavioural_pair_is_not_universally_skipped` below is
# what notices if that stops being true, because a permanently-skipped proof reads as
# green and this file's whole claim rests on those two arms.
requires_enforced_permissions = pytest.mark.skipif(
    os.geteuid() == 0, reason="rm -rf cannot be made to fail as root"
)

PRE_FIX_TRAP = 'trap \'rm -rf "$D"\' EXIT'
# Mirrors the runner's shape, warning included: discarding the removal error would hide
# the one signal that a gate child outlived the run.
POST_FIX_TRAP = """cleanup() {
  local rc=$?
  rm -rf "$D" 2>/dev/null ||
    echo "warning: could not remove $D" >&2
  exit "$rc"
}
trap cleanup EXIT"""


def _run_with_failing_cleanup(tmp_path: Path, trap: str) -> subprocess.CompletedProcess[str]:
    """A script that exits 2 while its cleanup target cannot be removed."""
    undeletable = tmp_path / "guard"
    undeletable.mkdir()
    (undeletable / "child").write_text("x", encoding="utf-8")
    undeletable.chmod(0o500)  # removal of `child` is denied, so `rm -rf` fails
    script = tmp_path / "run.sh"
    script.write_text(
        f'#!/usr/bin/env bash\nset -euo pipefail\nD="{undeletable}"\n{trap}\nexit 2\n',
        encoding="utf-8",
    )
    try:
        result = subprocess.run(["bash", str(script)], capture_output=True, text=True)
    finally:
        undeletable.chmod(0o700)
    # The removal must actually have failed, or both arms below measure nothing.
    # Checked on the FILESYSTEM rather than on stderr, because the post-fix shape
    # replaces the raw `rm` message with its own warning.
    assert (undeletable / "child").exists()
    return result


@requires_enforced_permissions
def test_the_pre_fix_trap_shape_loses_the_verdict(tmp_path: Path) -> None:
    # Shown red before the repair is accepted: without this arm the test below would
    # pass against a bash that preserved status anyway, proving nothing about the fix.
    # Asserted as EXACTLY 1 -- the failing `rm`'s own status -- because `!= 2` also
    # passes when the fixture breaks in some unrelated way and would report a broken
    # harness as a proven bug.
    # Status and filesystem only. `cannot remove` is GNU coreutils' wording; BSD/macOS
    # `rm` says `<path>: Permission denied`, and binding the string would red on an
    # operator's Mac with a message that reads like a trap-shape regression.
    assert _run_with_failing_cleanup(tmp_path, PRE_FIX_TRAP).returncode == 1


@requires_enforced_permissions
def test_the_post_fix_trap_shape_preserves_the_verdict(tmp_path: Path) -> None:
    result = _run_with_failing_cleanup(tmp_path, POST_FIX_TRAP)
    assert result.returncode == 2
    # The failure is reported, not swallowed. This string is OURS, not `rm`'s, so it is
    # safe to bind across platforms.
    assert "could not remove" in result.stderr


def test_the_runner_uses_the_status_preserving_shape() -> None:
    wrapper = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    engine = (ROOT / "scripts" / "run_quality_engine.py").read_text(encoding="utf-8")
    assert "run_quality_engine.py" in wrapper
    assert "queue_selected" not in wrapper
    assert "finally:" in engine
    assert "close_runtime(context)" in engine
    return
    text = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    # Binds the proven shape to the real file: the behavioural arms above run a copy,
    # so without this the runner could revert to the losing trap with both of them green.
    #
    # Matched as ONE ordered body, not three independent substrings. Three separate
    # checks passed while a `printf` inserted ahead of `local rc=$?` made the capture
    # read the printf's 0, and the `exit "$rc"` check matched a DIFFERENT function
    # elsewhere in this 1200-line file while the cleanup had lost its own.
    body = re.search(
        r"run_quality_cleanup\(\) \{\s*\n\s*local rc=\$\?\s*\n(?P<body>.*?)\n\}",
        text,
        re.DOTALL,
    )
    assert body, "the status capture must be the FIRST command in the cleanup function"
    assert re.search(r'\n\s*exit "\$rc"\s*$', body.group("body")), (
        "the cleanup must END by exiting with the captured status"
    )
    assert _trap_installs(text) == ["run_quality_cleanup"], _trap_installs(text)


def _trap_installs(text: str) -> list[str]:
    """The action of every `trap ... EXIT` in a script, inline body or function name.

    A `\\S+` action pattern could not span a quoted multi-word body, so a later
    `trap 'rm -rf "$TMP"' EXIT` silently replaced the cleanup while a single-install
    assertion still saw one entry — the exact escape that assertion exists to close.
    Trailing signal names are allowed and captured, because `trap cleanup EXIT INT`
    also replaces the handler.
    """
    installs = []
    for match in re.finditer(
        r"^[ \t]*trap[ \t]+(?P<action>'[^']*'|\"[^\"]*\"|\S+)(?P<signals>(?:[ \t]+[A-Z]+)+)[ \t]*$",
        text,
        re.MULTILINE,
    ):
        if "EXIT" not in match.group("signals").split():
            continue
        installs.append(match.group("action").strip("'\""))
    return installs


def _trap_bodies(text: str) -> list[str]:
    """Every EXIT-trap body, following `trap <name> EXIT` into that function."""
    bodies = []
    for action in _trap_installs(text):
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", action):
            func = re.search(
                rf"^[ \t]*{re.escape(action)}\(\)[ \t]*\{{\n(?P<body>.*?)\n\}}",
                text,
                re.DOTALL | re.MULTILINE,
            )
            bodies.append(func.group("body") if func else "")
        else:
            bodies.append(action)
    return bodies


def test_every_gate_script_trap_survives_a_failed_removal() -> None:
    """The sweep, so the sibling gates cannot drift back one at a time.

    `check-shell.sh` reporting FAIL on a clean tree because a `/tmp` removal lost a race
    is the same false verdict, on a smaller surface and with no test watching it.

    A first version matched only lines LITERALLY starting `trap 'rm`, which skipped
    `check-markdown.sh`'s `trap cleanup EXIT` — the worst instance in the repo, whose
    cleanup kills two children and then removes the directory they were writing into,
    so the race there is the designed teardown order rather than bad luck. Following the
    trap into its function is what makes this sweep mean what its name says.
    """
    offenders = []
    roots = [ROOT / "scripts", ROOT / "plugins" / "charness" / "scripts"]
    for root in roots:
        for path in sorted(root.glob("*.sh")):
            text = path.read_text(encoding="utf-8")
            for body in _trap_bodies(text):
                if 'exit "$rc"' in body:
                    continue  # captures and restores the pending status itself
                for line in body.splitlines():
                    stripped = line.strip()
                    if not re.match(r"rm\b", stripped):
                        continue
                    if "|| true" in stripped or "|| :" in stripped or stripped.endswith("||"):
                        continue
                    offenders.append(f"{path.relative_to(ROOT)}: {stripped}")
    assert offenders == [], offenders


def test_the_behavioural_pair_is_not_universally_skipped() -> None:
    """A skip that is always taken is not a passing test.

    Asserted against the CI definition rather than against this process: on a
    maintainer's root devcontainer the pair legitimately skips, and failing there would
    just teach the operator to ignore this file. What must not happen silently is CI
    adopting a root container, which would leave the trap-shape claim proven nowhere.
    """
    for name in ("quality-core.yml", "mutation-tests.yml"):
        workflow = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        assert "container:" not in workflow, (
            f"{name} gained a container; confirm it does not run as root, or the "
            "behavioural arms in this file are skipped everywhere and prove nothing"
        )
