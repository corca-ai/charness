#!/usr/bin/env python3
"""Advisory: a blocked file's tests exercise it where coverage never attributed it (#465).

The changed-line gate blocks on lines coverage.py reports as unexecuted. One
recurring reason for that report is not "untested" but "exercised somewhere the
coverage data never reached" — and four slices in one session each re-derived that
diagnosis by hand after a BLOCK.

**The mechanism is narrower than "subprocess", and getting it wrong would make this
advisory false reassurance printed onto a blocking gate.** This repo's
mutation-coverage producer (`scripts/mutation_sampling_lib.py`) writes a
`sitecustomize` calling `coverage.process_startup()` and exports
`COVERAGE_PROCESS_START` / `PYTHONPATH`, so a child process that inherits the
parent environment IS measured. That is not a code-reading inference: it was
measured, with a purpose-built control. A script whose ONLY exercise was
an interpreter child launched for an in-repo path with an inherited
environment — no import, no in-process call, no copy — had its executed lines
attributed and its unexercised branch correctly reported missing. (A first attempt
at this measurement used `tests/quality_gates/test_release_narrative_audit.py` and
was CONFOUNDED: that file also loads the module in-process via
`tests/script_loader.load_script_module`, so its 143 attributed lines proved
nothing about the child. Round-2 review caught it. The clean control replaced it.)
A subprocess-driven test is therefore NOT by itself a reason to doubt a BLOCK, and
this advisory must never fire on one.

Two mechanisms DO lose the measurement, and both are re-derived from the test file
as it exists now:

* **`env-replaces`** — a spawn whose `env=` REPLACES the environment instead of
  extending it. `env={**os.environ, "PATH": ...}` — this repo's house style — carries
  `COVERAGE_PROCESS_START` through, so those children ARE measured. Only a literal
  mapping with no environ in it actually scrubs the wiring. Bound to the spawn call
  whose COMMAND names this script, not merely to the file: a test file that scrubs
  the env for an unrelated shell script must not cast doubt on a different script
  it happens to mention.
* **`copies-this-script`** — the test copies this script by name. If the copy lands
  outside the repo, the executed file falls outside the rcfile's
  `source = <repo_root>` (`mutation_sampling_lib._write_coverage_config`) and
  `_coverage_relative_path` drops it: the environment is fully intact and the lines
  are still unattributed. Also measured, and it is the mechanism behind the issue's
  own first instance. Running only
  `test_validate_maintainer_setup_requires_installed_hookspath` — which
  `shutil.copy2`s `scripts/validate_maintainer_setup.py` into `tmp_path` and spawns
  the copy with an inherited env — attributes **0** lines to the real path. The
  mechanism is named for what is CHECKED (the copy names this script); the
  destination is not proven to be out of tree, and the operator text says so.

Candidate tests come from two sources. The live boundary inventory supplies
current `test::script` pairs, and
`suggest_mutation_coverage_command.tests_referencing_paths` supplies the
test-to-module map the issue itself pointed at. Every candidate from either
source is re-checked against the test file as it exists today.

What it deliberately does NOT claim:

* **Line granularity.** Neither source records which LINE a test reaches, so the
  strongest honest claim is file-level.
* **That the copy lands outside the repo.** `copies-this-script` proves the copy
  names this script, not its destination.
* **Absence.** Silence is not "this file has only in-process tests". `scope` says
  what was actually examined so silence is a statement rather than an absence.
  Three known silences, all deliberate and all in the safe direction: a spawn whose
  COMMAND is built from a variable does not bind; an `env=` passed as a bare name
  cannot be followed, including the PATH-only dicts `tests/quality_gates/support.py`
  returns to dozens of callers; and a helper in another module that `copytree`s a
  whole seeded repo is not resolved.

It is not a gate, not a blocking condition, and it never suppresses a blocker.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

#: `shutil` copy entrypoints that can put an executable copy outside `source =`.
_COPY_FUNCS = frozenset({"copy", "copy2", "copyfile", "copytree"})


def _load_boundary_inventory(repo_root: Path) -> tuple[dict[str, list[str]], str]:
    """Read the live boundary inventory as advisory candidate metadata."""
    try:
        from scripts.inventory_boundary_bypass_lib import find_boundary_bypass_candidates

        payload = find_boundary_bypass_candidates(repo_root)
    except Exception:
        return {}, "unavailable"
    rows = payload.get("candidates") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}, "malformed"
    pairs: dict[str, set[str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        test_file = row.get("test_file")
        targets = row.get("import_safe_targets")
        if not isinstance(test_file, str) or not test_file or not isinstance(targets, list):
            continue
        for script in targets:
            if isinstance(script, str) and script:
                pairs.setdefault(script, set()).add(test_file)
    return {script: sorted(tests) for script, tests in sorted(pairs.items())}, "read"


def load_subprocess_boundary_pairs(repo_root: Path) -> dict[str, list[str]]:
    """Return `{script_path: [test_file, ...]}` from the live inventory payload."""
    return _load_boundary_inventory(repo_root)[0]


def _referencing_tests(repo_root: Path, paths: list[str]) -> dict[str, list[str]]:
    """`{script: [test_file, ...]}` from the repo's test-to-module reference map.

    Imported lazily and defensively: this advisory rides a gate that has already
    produced its verdict, so a mapper that is absent, renamed, or raising must
    degrade to "no candidates from this source", never to a lost blocking report.
    """
    try:
        from scripts.suggest_mutation_coverage_command import tests_referencing_paths
    except Exception:  # pragma: no cover - import-shape drift must not break a gate
        return {}
    try:
        found = tests_referencing_paths(repo_root, paths)
    except Exception:
        return {}
    if not isinstance(found, dict):
        return {}
    return {
        script: sorted(tests)
        for script, tests in found.items()
        if isinstance(script, str) and isinstance(tests, list)
    }


def unmeasured_spawn_mechanisms(repo_root: Path, test_file: str, script_path: str) -> list[str]:
    """Which coverage-losing mechanisms does `test_file`, as it exists NOW, show?

    Returns the mechanism names (`env-replaces`, `out-of-tree-copy`), or `[]` for
    "nothing detected — say nothing". Both halves are re-derived from the file
    rather than trusted from a candidate list:

    * the test must still MENTION the script (a converted pair usually stops naming
      it, and a candidate inventory may otherwise retain stale data);
    * some call in it must either pass an `env=` that REPLACES the environment, or
      copy this script out of the repo before running it.

    File-level on every count: it does not prove the detected call is the one that
    runs this script. Unreadable or unparseable -> `[]` (say nothing).
    """
    try:
        source = (repo_root / test_file).read_text(encoding="utf-8")
    except (OSError, ValueError):  # unreadable, or non-UTF-8 bytes
        return []
    if not _mentions_script(source, script_path):
        return []
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):  # ValueError: source containing NUL bytes
        return []
    mechanisms = []
    if _spawn_of_this_script_replaces_env(tree, script_path):
        mechanisms.append("env-replaces")
    if _copies_this_script(tree, script_path):
        mechanisms.append("copies-this-script")
    return mechanisms


def _names_script(node: ast.expr, script_path: str) -> bool:
    """Does this expression contain a string constant naming `script_path`?

    Borrows `inventory_boundary_bypass_lib`'s string-constant walker rather than
    re-walking the tree here: that module already owns "which string constants does
    this expression carry" for this repo, and the dup ratchet caught the copy.
    """
    try:
        from scripts.inventory_boundary_bypass_lib import _iter_string_constants
    except Exception:  # pragma: no cover - import-shape drift must not break a gate
        return False
    return any(_mentions_script(value, script_path) for value in _iter_string_constants(node))


def _spawn_of_this_script_replaces_env(tree: ast.AST, script_path: str) -> bool:
    """Is there a spawn of THIS script whose `env=` replaces the environment?

    Bound to the call, not to the file. An earlier cut asked only "does this file
    contain an env-replacing call anywhere", which named
    `scripts/check_supply_chain.py` — exercised only by inherited-env spawns at its
    real in-repo path — because the same test file scrubs the env for an unrelated
    SHELL script. That is false reassurance printed onto a true block, so the
    command argument must name this script.

    Reuses `inventory_boundary_bypass_lib`'s spawn recognisers, which already own
    "which argument is the command" for this repo's spawn vocabulary. A spawn whose
    command is built from a variable does not bind, and is silence by design.
    """
    try:
        from scripts.inventory_boundary_bypass_lib import (
            _is_spawn_call,
            _iter_spawn_command_strings,
        )
    except Exception:  # pragma: no cover - import-shape drift must not break a gate
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_spawn_call(node):
            continue
        if not any(
            _mentions_script(value, script_path) for value in _iter_spawn_command_strings(node)
        ):
            continue
        for keyword in node.keywords:
            if keyword.arg == "env" and _replaces_environment(keyword.value):
                return True
    return False


def _copies_this_script(tree: ast.AST, script_path: str) -> bool:
    """Does some `shutil.copy*` call in this file copy THIS script by name?

    Why it matters: a copy whose destination is outside the repo makes the executed
    file fall outside the rcfile's `source = <repo_root>`, so the child is
    unmeasured even with the coverage environment fully inherited.

    The mechanism name says only what is checked — that the copy names this script.
    The DESTINATION is deliberately not asserted: proving it lands outside the repo
    needs value tracking this reader does not do, and an earlier cut's
    `out-of-tree-copy` name claimed exactly that unchecked property. Matching is on
    a path boundary for the same reason `_mentions_script` is: an earlier cut used a
    bare substring plus the copy's PARENT DIRECTORY name, so any test copying
    anything out of a directory called `scripts` was reported as copying whichever
    script it happened to mention.

    A helper that `copytree`s a whole seeded repo from another module is NOT
    recognised — that needs cross-file analysis this reader does not do, so those
    stay silent rather than guessed at.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        attr = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if attr not in _COPY_FUNCS or not node.args:
            continue
        if _names_script(node.args[0], script_path):
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
    """True when this `env=` value provably does NOT carry the parent environment.

    Silence is the safe direction, so anything this reader cannot follow answers
    False (inherits): a bare name, a call it does not recognise, and — the case the
    first cut got backwards — a mapping with a `**` splat of anything other than a
    literal environ read. `env={**base, "PATH": ...}` may well splat an
    `os.environ.copy()` two lines up, in which case the child IS measured and
    advising on it is exactly the false reassurance this module must never print.

    Recognised as replacing: a dict literal with no splats and no environ read, and
    `dict(PATH=...)` with no positional argument.
    """
    if isinstance(node, ast.Dict):
        # A `**`-free dict literal cannot carry the parent environment wholesale, so
        # it replaces — even when a VALUE reads os.environ. `{"PATH": os.environ["PATH"]}`
        # forwards one variable and drops COVERAGE_PROCESS_START with it; an earlier cut
        # walked the whole node for `environ` and called that shape "inherits", which was
        # a false negative reached by the wrong reasoning.
        return not any(key is None for key in node.keys)
    if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "dict":
        # `dict(PATH=...)` replaces; `dict(os.environ, PATH=...)` (positional mapping)
        # and `dict(**os.environ, PATH=...)` (a `**` keyword, arg is None) both carry the
        # parent through.
        return (
            not node.args
            and bool(node.keywords)
            and all(keyword.arg is not None for keyword in node.keywords)
        )
    return False


_MECHANISM_TEXT = {
    "env-replaces": (
        "spawns this script with an environment-REPLACING `env=` (one that does not carry "
        "os.environ through, so COVERAGE_PROCESS_START is dropped and that child's lines are "
        "not attributed) -- bound to the spawn call whose command names this script"
    ),
    "copies-this-script": (
        "copies this script by name (`shutil.copy*`). If the destination is outside the repo, the "
        "executed file falls outside the coverage rcfile's `source = <repo-root>` and is dropped "
        "even with the environment fully inherited. The DESTINATION was not checked -- an in-repo "
        "copy is still measured, so read the copy's target before concluding anything"
    ),
}


def _note(path: str, mechanisms: dict[str, list[str]], lines: list[int]) -> str:
    line_text = ", ".join(str(line) for line in lines) if lines else "the blocked line(s)"
    per_test = "; ".join(
        f"{test} {' and '.join(_MECHANISM_TEXT[name] for name in names)}"
        for test, names in sorted(mechanisms.items())
    )
    return (
        f"{path} is named by {len(mechanisms)} candidate test file(s) that may lose the "
        f"measurement: {per_test}. A spawn that inherits the environment and runs the script at "
        "its real in-repo path IS measured here (measured 2026-07-30 on a script whose only "
        "exercise was such a spawn: its executed lines were attributed; see this module's "
        "docstring), so a subprocess test alone is never a reason to doubt a BLOCK. ESTABLISHED "
        "AT FILE GRANULARITY ONLY: the candidate pairing records test::file, not test::line. It "
        f"does NOT establish that line(s) {line_text} are reached by those tests. Read them "
        "first; if they do reach the line, add in-process coverage (or run the in-repo script "
        "with the coverage env passed through) rather than assuming the line is untested."
    )


def _advisory(
    repo_root: Path,
    blocking_targets: dict[str, list[dict[str, object]]],
    blocking: list[str] | None = None,
) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    # Union, not just the files WITH proof targets. A file that blocks but produced
    # no `path:line` target is reported by the narration as "could not produce exact
    # proof targets", and its `blocking_detail` literally reads "file not tracked by
    # the test suite (untested, or exercised only where coverage was never
    # attributed)" — i.e. it is the single most likely candidate for this diagnosis,
    # and keying on `blocking_targets` alone
    # examined it zero times while `scope` reported that as nothing to examine.
    blocked = sorted({*blocking_targets, *(blocking or [])})
    inventory, inventory_status = _load_boundary_inventory(repo_root)
    referenced = _referencing_tests(repo_root, blocked) if blocked else {}
    advisory: dict[str, dict[str, object]] = {}
    examined = 0
    for path in blocked:
        candidates = sorted({*(inventory.get(path) or []), *(referenced.get(path) or [])})
        examined += len(candidates)
        mechanisms = {
            test: found
            for test in candidates
            if (found := unmeasured_spawn_mechanisms(repo_root, test, path))
        }
        if not mechanisms:
            continue
        lines = sorted(
            int(entry["line"])
            for entry in blocking_targets.get(path) or []
            if isinstance(entry, dict) and isinstance(entry.get("line"), int)
        )
        advisory[path] = {
            "subprocess_tests": sorted(mechanisms),
            "mechanisms": mechanisms,
            "blocked_lines": lines,
            "established": (
                "file-level: the candidate pairing records test::file, not lines; a "
                "coverage-losing mechanism is confirmed PRESENT in the test file, not "
                "confirmed to be the call that runs this script"
            ),
            "note": _note(path, mechanisms, lines),
        }
    scope = {
        "blocked_files_examined": len(blocked),
        "candidate_tests_examined": examined,
        "candidate_sources": ["boundary-bypass-inventory", "test-reference-map"],
        "inventory": inventory_status,
        "inventory_recorded_scripts": len(inventory),
        "reference_map": "read" if referenced else "empty-or-unavailable",
        "files_named": sorted(advisory),
        "silence_means": (
            "no candidate test of that file was found to spawn it with a replacing environment "
            "or to copy it by name. That is NOT proof the file's coverage is honest: a candidate "
            "list is not exhaustive, a spawn whose command is built from a variable does not "
            "bind, an `env=` passed as a bare name cannot be followed, and a helper in another "
            "module that copies a whole seeded repo is deliberately not resolved."
        ),
    }
    return advisory, scope


def subprocess_coverage_advisory(
    repo_root: Path,
    blocking_targets: dict[str, list[dict[str, object]]],
) -> dict[str, dict[str, object]]:
    """Per blocked file whose candidate tests exercise it where coverage was lost.

    Files with no detected mechanism are simply absent; see `advisory_scope` for
    what silence actually covers. Total-failure guard: this rides a gate whose real
    job already ran, so ANY unexpected exception degrades to `{}` rather than
    replacing a blocking verdict with a traceback.
    """
    try:
        return _advisory(repo_root, blocking_targets)[0]
    except Exception:
        return {}


def advisory_scope(
    repo_root: Path,
    blocking_targets: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    """What the advisory actually examined, so silence is a statement not an absence."""
    try:
        return _advisory(repo_root, blocking_targets)[1]
    except Exception:
        return {"error": "advisory scope could not be computed; treat silence as unexamined"}


def subprocess_coverage_advisory_report(
    repo_root: Path,
    blocking_targets: dict[str, list[dict[str, object]]],
    *,
    blocking: list[str] | None = None,
) -> dict[str, object]:
    """Both report keys from ONE pass, so the gate does not build the reference map twice.

    Same total-failure guard as the two single-key entrypoints: a gate whose verdict
    already exists must never lose it to an advisory.
    """
    try:
        advisory, scope = _advisory(repo_root, blocking_targets, blocking)
    except Exception:
        advisory = {}
        scope = {"error": "advisory could not be computed; treat silence as unexamined"}
    return {
        "subprocess_coverage_advisory": advisory,
        "subprocess_coverage_advisory_scope": scope,
    }


def advisory_scope_line(scope: dict[str, object] | None) -> str | None:
    """One sentence making advisory SILENCE legible in the operator's own channel.

    Without this, the #465 class recurs on the repair: a BLOCK with an empty advisory
    printed byte-identical narration to the pre-#465 gate, so the reader could not
    tell "examined 7 candidate tests, found nothing" from "never ran". Only emitted
    when the advisory named nothing — when it DID fire, its own sentence carries the
    scope.
    """
    if not scope or scope.get("files_named"):
        return None
    if scope.get("error"):
        return (
            f"subprocess-coverage advisory did not run ({scope['error']}); silence is unexamined.\n"
        )
    return (
        f"subprocess-coverage advisory examined {scope.get('candidate_tests_examined', 0)} candidate "
        f"test file(s) across {scope.get('blocked_files_examined', 0)} blocked file(s) "
        f"(inventory: {scope.get('inventory')}) and named none. That is NOT proof these blocks are "
        "honest -- see subprocess_coverage_advisory_scope.silence_means for what it cannot see.\n"
    )


def advisory_stderr_line(advisory: dict[str, dict[str, object]]) -> str | None:
    """One operator-facing sentence, or None when nothing survived the re-check."""
    if not advisory:
        return None
    names = sorted(advisory)
    mechanisms = sorted(
        {
            mechanism
            for entry in advisory.values()
            for names_found in (entry.get("mechanisms") or {}).values()
            for mechanism in names_found
        }
    )
    detail = f" via {', '.join(mechanisms)}" if mechanisms else ""
    return (
        f"{len(advisory)} blocked file(s) ({', '.join(names)}) are named by a candidate test file "
        f"that may lose the coverage measurement{detail}. FILE granularity: this does not "
        "establish that those tests reach the blocked lines, nor that the lines are covered -- "
        "only that a coverage-losing mechanism naming this script is present in a test that "
        "references it. A spawn that inherits the environment and runs the script at its real "
        "in-repo path IS measured, and is not what this fires on. Read "
        "subprocess_coverage_advisory, then the tests, before concluding the lines are untested.\n"
    )
