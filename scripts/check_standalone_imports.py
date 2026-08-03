#!/usr/bin/env python3
"""Every module in this repo must import FIRST, in a fresh interpreter.

A package whose modules import each other resolves correctly under whatever order the
test suite happens to use, and the suite cannot observe any other order. That is not a
gap in the tests; it is a property a test suite structurally cannot measure. The whole
suite imports everything exactly once, in one order, as a side effect of collection.

The measured instance: `scripts/quality_policy_merge.py` was extracted from
`quality_policy_defaults.py` and the two referenced each other at module level. The
cycle resolved in exactly ONE order, every existing importer reached `defaults` first,
and **4979 tests passed with a module that could not be imported on its own**. It was
found by a person reading two import statements, not by any tool. `ruff` does not check
import cycles and `check_python_lengths` cannot.

That matters more here than in most repos, because this one forces length-cap
extractions routinely -- three in one goal, two of which introduced a defect the suite
could not see. An extraction is a CHANGE, not a move.

So this imports each module as the FIRST thing a fresh process does. The subprocess is
the whole point: in-process, an earlier test file or a conftest has already built the
module graph, which is precisely the masking being guarded against.

## What this check can and cannot establish

It establishes that each module it ENUMERATED can be imported first. A module the
enumeration misses is unchecked, not proven clean, and `--changed` runs are a strict
subset -- so the scope is printed with every verdict rather than left for the reader to
assume. A partial run must never read as a whole-package verdict.

It does not prove the absence of import cycles in general. Four known blind spots,
each measured rather than assumed:

* A cycle that resolves in both directions is invisible here, and harmless.
* A cycle reachable only on a SECOND import is out of reach; each module is probed once.
* **A cycle a module swallows itself is invisible, and this repo is full of the idiom
  that swallows it.** `try: from scripts.x import A / except ImportError: A = None`
  imports cleanly with `A` silently degraded, so there is no failure to observe. That is
  not a gap this check can close from outside: the module imported successfully, and
  whether the fallback is a degradation or the design is undecidable here.
* A module that catches the cycle and then raises a sibling `ModuleNotFoundError` from
  OUTSIDE the `except` block leaves no exception chain, so no cycle marker survives and
  the shape fallback clears it. No instance exists in this repo today -- the dominant
  preamble re-raises inside the handler, which chains -- but it is a distinct blind spot
  from the one above and costs nothing to record.

It also imposes one PRECONDITION that did not exist before: because a module which
imports in no shape now blocks, a hard top-level third-party import (`jsonschema`,
`yaml`) makes the commit boundary require those dependencies installed. That is
deliberate -- a changed module that cannot be imported at all is a defect of the commit,
not an environment quirk -- but it is a new requirement on the environment, not a free
check.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files

# Both skill layouts, deliberately. The AUTHORING tree nests `skills/public/<skill>/`
# and `skills/support/<skill>/`, but `skills/shared/scripts/` sits one level shallower --
# and the EXPORTED plugin mirror flattens every skill to `skills/<skill>/`. A pattern
# written for the deep layout alone missed all 10 `skills/shared/scripts/` modules (the
# `<thing>.py` + `<thing>_state.py` extraction pairs, i.e. the highest-risk family) and
# matched literally NOTHING in the mirror while still printing `checked all N`.
SCAN_PATTERNS = (
    # The two repo-root portability shims, imported by 135 scripts. They were missed by
    # every directory-shaped pattern, and found by the inversion test rather than by
    # anyone listing families -- which is the argument for the inversion test.
    "*.py",
    "scripts/*.py",
    "skills/*/*/scripts/*.py",
    "skills/*/scripts/*.py",
    "skills/*/*/references/*.py",
    # The export flattens TWICE and the first repair only covered one flattening:
    # `skills/public/quality/references/` -> `skills/quality/references/` (3 components),
    # and support is hoisted OUT of `skills/` entirely to `support/<skill>/scripts/`.
    # 27 modules -- including the acquire_public_url and route_public_fetch extraction
    # PAIRS -- were enumerated as zero by the MIRRORED gate, the copy a consuming repo
    # actually runs, while it printed `checked all N`.
    "skills/*/references/*.py",
    # Support AND shared are both hoisted out of `skills/` by the export. `shared/` was
    # found by the mirror inversion test, not by anyone listing layouts -- which is the
    # third time on this slice that the enumeration was wrong in a way only an inversion
    # could see, and the argument for having one per tree that ships.
    "support/*/scripts/*.py",
    "shared/scripts/*.py",
)

# floor-addition-restraint: BLOCKING, deliberately, against this repo's default of
# preferring an advisory on first sight.
#   1. Closeout-contract weight: NONE. It adds no field, section, or form an author must
#      satisfy up front -- the Problem-1 cost the rule exists to resist. It fires only on
#      a real ImportError in a module the commit touched, and the fix is the defect.
#   2. Is advisory enough? No, and the recurrence IS recorded rather than assumed: this
#      class shipped undetected once (the quality_policy_merge extraction, invisible to
#      4979 passing tests), and the same goal shipped a second extraction defect the
#      suite could not see. An advisory is read by whoever is looking; the whole point
#      here is that NOBODY can see this class, including the full suite. A cycle is also
#      unambiguous -- CPython names it in stderr -- so this cannot cry wolf the way a
#      judgment-bound gate does, which is the false-fire cost the rule actually guards.
#   3. Can a describe-first preflight absorb it? No. There is nothing to describe; the
#      property only exists when a fresh interpreter runs.
# Recorded per Floor-Addition Restraint (docs/conventions/implementation-discipline.md).

# The strings CPython uses when an import cycle is what actually failed. Matching on
# these rather than on "did it fail" keeps a genuine cycle distinguishable from a
# missing third-party dependency, which is a different problem with a different fix.
CYCLE_MARKERS = ("partially initialized", "circular import")


def _is_cycle(stderr: str) -> bool:
    """True when an import CYCLE is what failed, not a missing third-party dependency."""
    lowered = stderr.lower()
    return any(marker in lowered for marker in CYCLE_MARKERS)


_MISSING_MODULE = re.compile(r"ModuleNotFoundError: No module named '([\w.]+)'")


def _is_wrong_shape(stderr: str, path: Path) -> bool:
    """True only for the ONE failure the shape fallback exists to absorb.

    A module built for direct execution raises `ModuleNotFoundError` for a SIBLING when
    imported as a package member. That is the wrong loader, not a defect, and trying the
    next shape is right.

    Everything else must NOT fall through. The fallback used to run on any failure, and
    the `direct` shape loads a file as a top-level module under a different name -- a
    different module object, through which the cycle does not run -- so it cleared real
    failures found by the first shape. Narrowing the fallback to the signal it was built
    for is the difference between a fallback and a mask.
    """
    match = _MISSING_MODULE.search(stderr)
    if match is None:
        return False
    root = match.group(1).split(".")[0]
    return (path.parent / f"{root}.py").is_file() or (path.parent / root).is_dir()


def discover_modules(repo_root: Path, *, require_git: bool = False) -> list[Path]:
    """Every gated Python module, gitignore-aware via the repo's own listing helper."""
    return sorted(
        path
        for path in iter_matching_repo_files(repo_root, SCAN_PATTERNS, require_git=require_git)
        if path.name != "__init__.py"
    )


def _probe_commands(repo_root: Path, path: Path) -> list[tuple[str, str]]:
    """The import shapes a module may legitimately be loaded through, in order.

    Two shapes exist in this repo and both are correct for their own files. A module
    under `scripts/` that other code imports as `scripts.<name>` is loaded as a package
    member. A module carrying the sibling-import preamble (`sys.path.insert(parent)`) is
    designed to run as `python3 scripts/x.py` from a consuming checkout, and importing it
    as a package member raises `ModuleNotFoundError` for its siblings -- a wrong-shape
    error, not a defect in the module.

    So a module is failing only when EVERY shape it could be loaded through fails.
    Probing one shape would have reported 35 healthy `scripts/` modules as broken.
    """
    relative = path.relative_to(repo_root)
    shapes = []
    if relative.parts[0] == "scripts" and len(relative.parts) == 2:
        shapes.append(("package", f"import scripts.{path.stem}"))
    shapes.append(
        ("direct", f"import sys; sys.path.insert(0, {str(path.parent)!r}); import {path.stem}")
    )
    return shapes


def probe_module(repo_root: Path, path: Path, *, timeout: int = 60) -> dict:
    stderr = ""
    timed_out = False
    for shape, code in _probe_commands(repo_root, path):
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            # Try the remaining shapes rather than returning. A `scripts/` module whose
            # PACKAGE-shape import hangs still deserves its legitimate direct shape; the
            # early return refused a module on the strength of the wrong loader.
            stderr = f"import did not finish within {timeout}s"
            timed_out = True
            continue
        if result.returncode == 0:
            return {"path": str(path.relative_to(repo_root)), "ok": True, "shape": shape}
        stderr = result.stderr
        # BOTH conditions. A sibling `ModuleNotFoundError` is the wrong-shape signal AND
        # what a swallowed cycle looks like from outside: `try: from scripts.x import A /
        # except ImportError: import x as A` turns a cycle into a missing-sibling error.
        # But CPython's exception chaining keeps the original `partially initialized` text
        # in the same stderr, so a cycle marker ANYWHERE vetoes the fallback. Testing
        # wrong-shape alone re-opened the mask this loop was narrowed to close.
        if _is_cycle(stderr) or not _is_wrong_shape(stderr, path):
            # STOP unless the failure is the one wrong-shape signal the fallback exists
            # for. Measured twice: with the fallback unguarded the check reported `ok` for
            # `--changed scripts/quality_policy_merge.py` against the exact reconstructed
            # cycle from the issue -- the pre-push lane clearing the one module carrying
            # the defect the check was built for. Guarding it on `_is_cycle` alone was
            # still too narrow, because a module that catches ImportError can turn a cycle
            # into a differently-worded error, and then the mask returns.
            break
    lowered = stderr.lower()
    if timed_out and not _is_cycle(lowered):
        return {
            "path": str(path.relative_to(repo_root)),
            "ok": False,
            "kind": "timeout",
            "detail": stderr,
        }
    return {
        "path": str(path.relative_to(repo_root)),
        "ok": False,
        # A cycle is the class this check exists for and blocks. Anything else is
        # reported separately rather than folded in, because calling an unrelated
        # ImportError a cycle would make the first real cycle harder to believe.
        "kind": "cycle" if _is_cycle(lowered) else "import-error",
        "detail": (stderr.strip().splitlines() or ["(no stderr)"])[-1][:400],
    }


def run(repo_root: Path, *, changed: list[Path] | None, workers: int, require_git: bool) -> dict:
    discovered = discover_modules(repo_root, require_git=require_git)
    unmatched: list[str] = []
    if changed is None:
        modules, scope = discovered, "full"
    else:
        # Resolved against REPO_ROOT, not the process CWD. `Path("scripts/x.py").resolve()`
        # silently means "relative to wherever this happens to be running", which matched
        # by luck when CWD was the repo and matched NOTHING against any other root.
        wanted = {
            (path if path.is_absolute() else repo_root / path).resolve(): path for path in changed
        }
        by_resolved = {path.resolve(): path for path in discovered}
        modules = [by_resolved[key] for key in wanted if key in by_resolved]
        unmatched = sorted(str(orig) for key, orig in wanted.items() if key not in by_resolved)
        scope = "partial"
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda path: probe_module(repo_root, path), modules))
    cycles = [item for item in results if item.get("kind") == "cycle"]
    others = [item for item in results if not item["ok"] and item.get("kind") != "cycle"]
    # A module that imports in NO shape blocks too. Splitting cycle from import-error is
    # worth doing in the OUTPUT -- a missing dependency has a different fix -- but making
    # only one half blocking left the other as a hole: the gate would hold the evidence
    # that a changed module cannot be imported at all, print it as a note, and exit 0.
    return {
        "scope": scope,
        "checked": len(modules),
        "discovered": len(discovered),
        "cycles": cycles,
        "other_failures": others,
        "ok": not cycles and not others,
        # The scope note travels WITH the verdict. A partial run that renders a bare
        # `ok: true` reads as a whole-package clean bill, which is this repo's own
        # measured `partial` lesson: a verdict must state what it measured.
        "unmatched_changed": unmatched,
        "scope_note": (
            f"checked all {len(modules)} discovered module(s)"
            if scope == "full"
            else f"PARTIAL: checked {len(modules)} of {len(discovered)} discovered module(s); "
            "the rest are UNCHECKED, not proven clean"
            # An empty scope that prints `ok` is a green nobody earned. It does not BLOCK
            # -- a commit touching only non-module Python legitimately matches nothing --
            # but it says so, and it names the paths that matched nothing so a caller
            # passing paths in the wrong shape finds out here instead of trusting a pass.
            + (" -- NOTHING WAS CHECKED: no --changed path matched a discovered module" if not modules else "")
            # Named whenever there ARE unmatched paths, not only when the scope collapsed
            # to zero. A run that checked 1 of 2 given paths and stayed silent about the
            # other is strictly more misleading than one that checked none and said so.
            + (f"; unmatched: {', '.join(unmatched)}" if unmatched else "")
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import every repo module first in a fresh process, to surface cycles the suite masks."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--changed",
        nargs="*",
        type=Path,
        help="Restrict to these modules (pre-push lane). The result is explicitly marked PARTIAL.",
    )
    parser.add_argument("--workers", type=int, default=16, help="Concurrent import probes (1-64)")
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit the full report as JSON")
    args = parser.parse_args()

    report = run(
        args.repo_root.expanduser().resolve(),
        changed=args.changed,
        workers=min(64, max(1, args.workers)),
        require_git=args.require_git_file_listing,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"standalone-import: {'ok' if report['ok'] else 'BLOCKED'} ({report['scope_note']})")
        for item in report["cycles"]:
            print(f"CYCLE {item['path']}: {item['detail']}")
        for item in report["other_failures"]:
            print(f"BROKEN {item['path']} did not import in any shape: {item['detail']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
