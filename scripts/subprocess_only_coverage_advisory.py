#!/usr/bin/env python3
"""Advisory: a blocked file's recorded test spawns it with a scrubbed env (#465).

The changed-line gate blocks on lines coverage.py reports as unexecuted. One
recurring reason for that report is not "untested" but "tested across a process
boundary the coverage data never reached" — and four slices in one session each
re-derived that diagnosis by hand after a BLOCK.

**The mechanism is narrower than "subprocess", and getting that wrong would make
this advisory false reassurance printed onto a blocking gate.** This repo's
mutation-coverage producer (`scripts/mutation_sampling_lib.py`) writes a
`sitecustomize` calling `coverage.process_startup()` and exports
`COVERAGE_PROCESS_START` / `PYTHONPATH`, so a child process that INHERITS the
parent environment IS measured. A subprocess-driven test is therefore not by
itself a reason to doubt a BLOCK.

What drops the measurement is narrower still: a spawn whose `env=` REPLACES the
environment rather than extending it. `env={**os.environ, "PATH": ...}` — this
repo's house style, 60+ times under `tests/` — carries `COVERAGE_PROCESS_START`
and `PYTHONPATH` straight through, so those children ARE measured. Only a
literal dict that does not splat the parent environment (a bare
`{"PATH": "/usr/bin"}`) actually scrubs the wiring. That, and only that, is what
this advisory fires on.

Two things it deliberately does NOT claim:

* **Line granularity.** `scripts/boundary-bypass-baseline.json` records
  `test_file::script_file` pairs, so the strongest honest claim is file-level.
* **That the pair is live.** The baseline is a no-increase RATCHET, not a current
  inventory: it never prunes a pair that has since been converted to an in-process
  test. So each recorded pair is re-checked against the test file as it exists now
  before anything is said about it.

It is not a gate, not a blocking condition, and it never suppresses a blocker.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

BASELINE_REL = "scripts/boundary-bypass-baseline.json"


def load_subprocess_boundary_pairs(repo_root: Path, *, baseline_rel: str = BASELINE_REL) -> dict[str, list[str]]:
    """`{script_path: [test_file, ...]}` from the boundary-bypass ratchet baseline.

    Absent, unreadable, or malformed baseline -> `{}`. This is advisory-only, so a
    missing baseline must degrade to "said nothing" and never to a blocked verdict
    or a crash on a gate whose real job already ran.
    """
    try:
        payload = json.loads((repo_root / baseline_rel).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    keys = payload.get("candidate_keys") if isinstance(payload, dict) else None
    if not isinstance(keys, list):
        return {}
    pairs: dict[str, set[str]] = {}
    for key in keys:
        if not isinstance(key, str):
            continue
        test_file, separator, script = key.partition("::")
        if not separator or not test_file.strip() or not script.strip():
            continue
        pairs.setdefault(script.strip(), set()).add(test_file.strip())
    return {script: sorted(tests) for script, tests in sorted(pairs.items())}


def spawns_with_scrubbed_env(repo_root: Path, test_file: str, script_path: str) -> bool:
    """Does `test_file`, as it exists NOW, spawn `script_path` with an explicit `env=`?

    Both halves matter and both are re-derived from the file rather than trusted
    from the baseline:

    * the test must still MENTION the script (a converted pair usually stops naming
      it, and a ratchet baseline never prunes the stale entry);
    * some call in it must pass an `env=` that REPLACES the environment. A dict
      that splats the parent (`{**os.environ, ...}`, `os.environ.copy()`,
      `dict(os.environ)`) keeps `COVERAGE_PROCESS_START`, so that child IS
      measured and a BLOCK on it is a true block this advisory must not
      second-guess. Anything the shape of which cannot be read is treated as
      inheriting, because silence is the safe direction for an advisory.

    File-level on both counts: it does not prove the env-replacing call is the one
    that runs this script. Unparseable or unreadable -> False (say nothing).
    """
    try:
        source = (repo_root / test_file).read_text(encoding="utf-8")
    except (OSError, ValueError):  # unreadable, or non-UTF-8 bytes
        return False
    if not _mentions_script(source, script_path):
        return False
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):  # ValueError: source containing NUL bytes
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg == "env" and _replaces_environment(keyword.value):
                return True
    return False


def _mentions_script(source: str, script_path: str) -> bool:
    """Does `source` name this script, on a path boundary?

    Plain basename containment matched far too much: `scripts/doctor.py` hit any
    file mentioning `test_doctor.py`, and `bump_version.py` hit `test_bump_version.py`.
    """
    if script_path in source:
        return True
    name = Path(script_path).name
    return re.search(rf"(?<![\w./-]){re.escape(name)}(?![\w])", source) is not None


def _replaces_environment(node: ast.expr) -> bool:
    """True when this `env=` value does NOT carry the parent environment through.

    `{**os.environ, "PATH": ...}`, `os.environ.copy()`, `dict(os.environ)` and a
    bare name (which this reader cannot follow) all keep, or may keep, the
    coverage wiring -> False. Only a literal dict with no environ splat, or an
    explicit `None`-less literal that plainly replaces, is a real scrub.
    """
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if key is None and _reads_environ(value):  # {**os.environ, ...}
                return False
        return True
    return False


def _reads_environ(node: ast.expr) -> bool:
    """`os.environ`, `environ`, `os.environ.copy()`, `dict(os.environ)`, ..."""
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr == "environ":
            return True
        if isinstance(child, ast.Name) and child.id == "environ":
            return True
    return False


def _note(path: str, tests: list[str], lines: list[int]) -> str:
    line_text = ", ".join(str(line) for line in lines) if lines else "the blocked line(s)"
    return (
        f"{path} is named by {len(tests)} recorded test file(s) ({', '.join(tests)}) that "
        "contain at least one spawn passing an environment-REPLACING `env=` (one that does "
        "not splat os.environ, so COVERAGE_PROCESS_START is dropped and that child's lines "
        "are not attributed). A spawn inheriting the environment IS measured here, so this "
        "does not fire on those. ESTABLISHED AT FILE GRANULARITY ONLY: the pair comes from "
        f"{BASELINE_REL}, which records test::file, not test::line. It does NOT establish "
        f"that line(s) {line_text} are reached by those tests, and it does NOT establish "
        "that the env-replacing call is the one running this script -- both are the same "
        "file, which is all that was checked. Read them first; if they do reach the line, "
        "add in-process coverage (or pass the coverage env through) rather than assuming "
        "the line is untested."
    )


def subprocess_coverage_advisory(
    repo_root: Path,
    blocking_targets: dict[str, list[dict[str, object]]],
    *,
    baseline_rel: str = BASELINE_REL,
) -> dict[str, dict[str, object]]:
    """Per blocked file whose recorded tests still spawn it with a scrubbed env.

    Files with no surviving pair are simply absent. Silence means "nothing recorded
    and re-confirmed for this file", which is NOT "this file has only in-process
    tests" -- the baseline is a curated ratchet, not a proof of absence.
    """
    pairs = load_subprocess_boundary_pairs(repo_root, baseline_rel=baseline_rel)
    advisory: dict[str, dict[str, object]] = {}
    for path in sorted(blocking_targets):
        recorded = pairs.get(path) or []
        tests = [test for test in recorded if spawns_with_scrubbed_env(repo_root, test, path)]
        if not tests:
            continue
        lines = sorted(
            int(entry["line"])
            for entry in blocking_targets[path]
            if isinstance(entry, dict) and isinstance(entry.get("line"), int)
        )
        advisory[path] = {
            "subprocess_tests": tests,
            "blocked_lines": lines,
            "established": (
                "file-level: baseline records test::file pairs, not lines; an "
                "environment-replacing env= spawn is confirmed PRESENT in the test file, "
                "not confirmed to be the call that runs this script"
            ),
            "note": _note(path, tests, lines),
        }
    return advisory


def advisory_stderr_line(advisory: dict[str, dict[str, object]]) -> str | None:
    """One operator-facing sentence, or None when nothing survived the re-check."""
    if not advisory:
        return None
    return (
        f"{len(advisory)} blocked file(s) ({', '.join(sorted(advisory))}) are named by a "
        "recorded test file that contains an environment-REPLACING `env=` spawn, which "
        "drops COVERAGE_PROCESS_START so that child's lines are not attributed. Same FILE "
        "only -- this does not establish that the env-replacing call runs this script, nor "
        "that these lines are covered. Read subprocess_coverage_advisory, then the tests, "
        "before concluding the lines are untested.\n"
    )
