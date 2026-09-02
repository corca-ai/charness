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

The charness-shaped git repo these gates need comes from `support`, not from a
second copy that would drift from the gate it fixtures. It previously came from a
private helper in `test_shell_gate_root_resolution`; a cross-module private import
made the fixture's owner a sibling test file, so promoting the helper broke this
module. `support` is the owner.
"""
from __future__ import annotations

import ast
import os
import re
from pathlib import Path

from .support import charness_shaped_repo, run_shell_script, write_executable

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
    repo, source, _mirror = charness_shaped_repo(tmp_path, "check-markdown.sh")
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


#: Both refusing spellings, as a WHOLE-FLAG pattern. `--no` is the current documented
#: flag (check-markdown.sh); `--no-install` is the older alias check-secrets.sh still
#: uses. Unifying them is a separate behavior change with its own proof, so either is
#: accepted.
#:
#: Written as a substring pair first — `("--no ", "--no-install")` — and then `.strip()`ed
#: at the comparison, which cancelled the trailing space that was the whole point and
#: left a bare `--no` substring test. `npm exec -- markdownlint-cli2 --no-progress` then
#: satisfied a guard about reaching the registry, and so did any line merely containing
#: the characters `--no`. A bounded review found that in this repair.
_NPM_EXEC_GUARD_RE = re.compile(r"(?<![\w-])--no(?:-install)?(?![\w-])")

#: A shell `npm exec ...`, and the argv-list spelling a Python caller uses. The second
#: pattern is why this test exists in its current form: the previous version iterated a
#: hardcoded pair of `.sh` filenames while its own docstring claimed to catch "a third
#: unguarded call site". It could not see Python at all, and there WAS one --
#: `check_doc_authoring_preflight.py` spelled the fallback `["npm", "exec", "--", ...]`
#: with no guard, in a file three planners emit as an operator command. A guard whose
#: reach is narrower than its docstring is the class #630 is filed under.
_NPM_EXEC_PATTERNS = (
    re.compile(r"npm\s+exec\b(?P<rest>.*)"),
    re.compile(r"""["']npm["']\s*,\s*["']exec["'](?P<rest>.*)"""),
)


def _docstring_line_numbers(text: str) -> frozenset[int]:
    """Line numbers occupied by module/class/function docstrings.

    Parsed rather than pattern-matched, and deliberately NARROWER than "every string
    literal": an argv call site is `["npm", "exec", "--no", ...]`, whose lines carry
    string constants too, and skipping those would hide the very call sites this scan
    exists to find. Only docstrings -- prose that cannot execute -- are excluded.

    A file that does not parse contributes nothing here, so its prose is scanned as
    before; that is the conservative direction (a false blocker on unparseable Python,
    which a repo-owned script is not).
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return frozenset()
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)):
            continue
        if not isinstance(first.value.value, str):
            continue
        lines.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return frozenset(lines)


def test_no_repo_owned_source_reaches_the_npm_registry_through_exec() -> None:
    """Every repo-owned `npm exec` call site refuses an install, in ANY language.

    Scanned by DISCOVERY over `scripts/**`, not from a filename list, so a new call
    site in a file nobody thought to name here still fails. Comments are skipped:
    `check-markdown.sh` documents the unguarded spelling and its measured cost on
    purpose, and refusing its own prose would teach an author to delete the reasoning.
    """
    from .support import ROOT

    scanned: list[str] = []
    for path in sorted((ROOT / "scripts").rglob("*")):
        if not path.is_file() or path.suffix not in {".sh", ".py"}:
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        prose_lines = _docstring_line_numbers(text) if path.suffix == ".py" else frozenset()
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            # `#` only. A shell `case` default arm begins `*)` and can carry a real
            # command (`*) npm exec -- markdownlint-cli2 ;;`), so skipping `*` would
            # hide exactly the call site this scan exists to find.
            if stripped.startswith("#"):
                continue
            # Docstring prose is skipped STRUCTURALLY, by parsing. The retired version
            # claimed the whole-flag pattern handled it; it did not. `markdownlint_probe`
            # documents the unguarded `npm exec --` spelling in prose, and that sentence
            # matched -- passing the guard only because a later `--no` happened to land
            # on the same physical line. Two consequences, both bad: reflowing the
            # sentence would have gone red on pure prose, and the liveness anchor below
            # could be satisfied by a file whose real call site had been deleted.
            if line_no in prose_lines:
                continue
            for pattern in _NPM_EXEC_PATTERNS:
                match = pattern.search(stripped)
                if match is None:
                    continue
                scanned.append(f"{rel}:{line_no}")
                rest = match.group("rest")
                assert _NPM_EXEC_GUARD_RE.search(rest), (
                    f"{rel}:{line_no} reaches the registry: {stripped}"
                )

    # The scan finding nothing would pass vacuously, which is how this guard would rot
    # if `scripts/` were reorganized. The known call sites are the liveness proof.
    assert "scripts/check-markdown.sh" in " ".join(scanned)
    assert "scripts/check-secrets.sh" in " ".join(scanned)
    # The Python call site moved out of check_doc_authoring_preflight.py into its own
    # engine-adapter module when that file hit its length cap. With docstrings excluded
    # above, this anchor now means what it says: an EXECUTABLE npm-exec line exists in
    # the Python lane. Deleting the real tier while leaving the prose that describes it
    # fails here, which is the rot this anchor guards.
    assert "scripts/evidence/markdownlint_probe.py" in " ".join(scanned)
