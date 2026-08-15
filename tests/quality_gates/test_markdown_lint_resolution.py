"""Which markdownlint binary `check-markdown.sh` reaches for, and what it costs.

Issue #630. Two sibling gates in the same package spelled the same fallback
differently: `check-secrets.sh` guarded npm against the registry with
`--no-install`, `check-markdown.sh` did not. Measured in a consumer repo on a
single 907-line file, that difference was ~5s, and the whole `npm exec` detour
was ~9.7s against a direct invocation that cost nothing.

So the fallback has two defects, not one, and both are pinned here: the missing
registry guard, and the missing middle tier — a repo that has run `npm install`
already has the binary in `node_modules/.bin/`, and asking npm to find a file
already sitting in the tree pays the whole cost for none of the benefit.

The fixture helpers are imported from `test_shell_gate_root_resolution` rather
than copied. That module owns the charness-shaped git repo these gates need, and
a second copy would be a fixture that drifts from the gate it fixtures.
"""
from __future__ import annotations

import os
from pathlib import Path

from .support import run_shell_script, write_executable
from .test_shell_gate_root_resolution import _charness_shaped_repo

_ARGV_LOGGER = '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$TEST_OUTPUT"\n'

#: A machine with no registry access. `npm exec` without `--no` asks the registry
#: whether it should install the package before running it, so here it fails —
#: which is the point: the fallback has to work on a machine that cannot reach
#: the registry, not merely run faster on one that can.
_OFFLINE_NPM = """#!/usr/bin/env bash
printf '%s\\n' "$@" > "$NPM_ARGV"
if [[ "$1" == exec && "$2" != "--no" && "$2" != "--no-install" ]]; then
  echo "npm error: registry unreachable and no --no flag was passed" >&2
  exit 1
fi
exit 0
"""

_REFUSING_NPM = """#!/usr/bin/env bash
echo "npm must not be invoked when the binary is already in the tree" >&2
exit 97
"""


def _path_without_markdownlint(bin_dir: Path) -> str:
    """The real PATH minus any directory that already offers `markdownlint-cli2`.

    Subtracted rather than replaced with a fixed list: the gate also needs `git`,
    `mktemp`, and `python3`, and a hand-built PATH that happens to miss one of
    them fails for a reason that has nothing to do with what is under test.
    """
    entries = [
        entry
        for entry in os.environ.get("PATH", "").split(os.pathsep)
        if entry and not (Path(entry) / "markdownlint-cli2").exists()
    ]
    return os.pathsep.join([str(bin_dir), *entries])


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo, source, _mirror = _charness_shaped_repo(tmp_path, "check-markdown.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    return repo, source, bin_dir


def test_a_markdownlint_on_path_is_used_directly(tmp_path: Path) -> None:
    repo, source, bin_dir = _fixture(tmp_path)
    log = tmp_path / "argv.txt"
    write_executable(bin_dir / "markdownlint-cli2", _ARGV_LOGGER)
    write_executable(bin_dir / "npm", _REFUSING_NPM)

    result = run_shell_script(
        source,
        cwd=repo,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}", "TEST_OUTPUT": str(log)},
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "README.md" in log.read_text(encoding="utf-8")


def test_the_node_modules_binary_is_preferred_over_npm(tmp_path: Path) -> None:
    """The tier that makes the expensive tier rare."""
    repo, source, bin_dir = _fixture(tmp_path)
    log = tmp_path / "argv.txt"
    local_bin = repo / "node_modules" / ".bin"
    local_bin.mkdir(parents=True)
    write_executable(local_bin / "markdownlint-cli2", _ARGV_LOGGER)
    write_executable(bin_dir / "npm", _REFUSING_NPM)

    result = run_shell_script(
        source,
        cwd=repo,
        env={**os.environ, "PATH": _path_without_markdownlint(bin_dir), "TEST_OUTPUT": str(log)},
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "README.md" in log.read_text(encoding="utf-8")
    # `_REFUSING_NPM` exits 97, so a gate that reached for npm could not have
    # returned 0 here. The assertion above alone would not have said that.
    assert "npm must not be invoked" not in result.stderr


def test_the_npm_fallback_runs_with_no_registry_access(tmp_path: Path) -> None:
    """SC4, and the direction #630 actually filed.

    No binary on PATH and no `node_modules`, so the last tier is taken. The stub
    npm refuses exactly as an offline machine would when `--no` is absent, so
    this test goes red on the pre-fix spelling rather than merely describing it.
    """
    repo, source, bin_dir = _fixture(tmp_path)
    npm_argv = tmp_path / "npm-argv.txt"
    write_executable(bin_dir / "npm", _OFFLINE_NPM)

    result = run_shell_script(
        source,
        cwd=repo,
        env={
            **os.environ,
            "PATH": _path_without_markdownlint(bin_dir),
            "NPM_ARGV": str(npm_argv),
            "TEST_OUTPUT": str(tmp_path / "unused.txt"),
        },
    )

    assert result.returncode == 0, result.stdout + result.stderr
    argv = npm_argv.read_text(encoding="utf-8").splitlines()
    assert argv[:4] == ["exec", "--no", "--", "markdownlint-cli2"]


def test_the_two_sibling_gates_both_guard_npm_against_the_registry() -> None:
    """The inconsistency #630 opened on, asserted rather than described.

    Spelled as "neither file carries a bare `npm exec`" so that adding a third
    unguarded call site to either one fails, not only reverting the two that were
    measured."""
    from .support import ROOT

    for name in ("check-markdown.sh", "check-secrets.sh"):
        text = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") or "npm exec" not in stripped:
                continue
            assert "npm exec --no" in stripped, f"{name}:{line_no} reaches the registry: {stripped}"
