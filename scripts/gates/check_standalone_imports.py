#!/usr/bin/env python3
"""Every selected module in this repo must import FIRST, in a fresh interpreter.

A package whose modules import each other resolves correctly under whatever order the
test suite happens to use, and the suite cannot observe any other order. That is not a
gap in the tests; it is a property a test suite structurally cannot measure. The whole
suite imports everything exactly once, in one order, as a side effect of collection.

The measured instance: `scripts/quality_policy_merge.py` was extracted from
`quality_policy_defaults.py` and the two referenced each other at module level. The
cycle resolved in exactly ONE order, every existing importer reached `defaults` first,
and **4979 tests passed with a module that could not be imported on its own**. It was
found by a person reading two import statements, not by any tool. `ruff` does not check
import cycles and `check_code_lengths` cannot.

That matters more here than in most repos, because this one forces length-cap
extractions routinely -- three in one goal, two of which introduced a defect the suite
could not see. An extraction is a CHANGE, not a move.

So this imports each module as the FIRST thing a fresh process does. The subprocess is
the whole point: in-process, an earlier test file or a conftest has already built the
module graph, which is precisely the masking being guarded against.

## What this check can and cannot establish

It establishes that each module selected by the native topology owner can be imported
first. Static selection is not runtime proof, so a partial run must never read as a
whole-package verdict.

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
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

native_gate_lib = import_repo_module(__file__, "scripts.native_gate_lib")
NativeGateError = native_gate_lib.NativeGateError
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

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
# Recorded per Floor-Addition Restraint (docs/implementation-discipline.md).

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


class NativeSelectionError(RuntimeError):
    """The native selection command did not emit an established v1 document."""


def _native_report_detail(document: object, stderr: str) -> str:
    if isinstance(document, dict):
        unestablished = document.get("unestablished")
        if isinstance(unestablished, list):
            details = [
                item.get("detail")
                for item in unestablished
                if isinstance(item, dict) and isinstance(item.get("detail"), str)
            ]
            if details:
                return "; ".join(details)
    return stderr.strip() or "(no native diagnostic)"


def _validate_selection_document(document: object) -> dict:
    if not isinstance(document, dict):
        raise NativeSelectionError("native standalone-targets did not emit a JSON object")
    if document.get("schema") != "repograph.standalone_targets.v1":
        raise NativeSelectionError(
            f"native standalone-targets emitted an unexpected schema: {document.get('schema')!r}"
        )
    targets = document.get("targets")
    if not isinstance(targets, list):
        raise NativeSelectionError("native standalone-targets document has no target list")
    for index, target in enumerate(targets):
        if not isinstance(target, dict) or not isinstance(target.get("path"), str):
            raise NativeSelectionError(
                f"native standalone-targets target {index} has no inventory-relative path"
            )
        shapes = target.get("shapes")
        if not isinstance(shapes, list):
            raise NativeSelectionError(
                f"native standalone-targets target {target['path']!r} has no shape list"
            )
        for shape_index, shape in enumerate(shapes):
            if not isinstance(shape, dict) or not isinstance(shape.get("command"), str):
                raise NativeSelectionError(
                    f"native standalone-targets target {target['path']!r} shape "
                    f"{shape_index} has no command"
                )
    if document.get("scope") == "unestablished" or document.get("unestablished"):
        raise NativeSelectionError(
            "native standalone-targets reported an unestablished condition: "
            + _native_report_detail(document, "")
        )
    return document


def select_standalone_targets(repo_root: Path, *, changed: list[Path] | None) -> dict:
    """Ask the D1-resolved native owner for the static probe plan."""
    resolved = native_gate_lib.resolve_native_core(repo_root)
    command = [str(resolved.path), "standalone-targets", "--repo-root", str(repo_root)]
    if changed is not None:
        command.extend(["--changed", *(str(path) for path in changed)])
    try:
        result = run_process(
            command,
            cwd=repo_root,
            timeout_seconds=None,
        )
    except OSError as exc:
        raise NativeSelectionError(
            f"native standalone-targets could not execute {resolved.path}: {exc}"
        ) from exc

    document = None
    if result.stdout.strip():
        try:
            document = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            if result.returncode == 0:
                raise NativeSelectionError(
                    f"native standalone-targets emitted invalid JSON: {exc}"
                ) from exc
    if result.returncode != 0:
        detail = _native_report_detail(document, result.stderr)
        raise NativeSelectionError(
            f"native standalone-targets exited {result.returncode} (native condition): {detail}"
        )
    return _validate_selection_document(document)


def probe_module(repo_root: Path, target: dict, *, timeout: int = 60) -> dict:
    relative_path = Path(target["path"])
    path = relative_path if relative_path.is_absolute() else repo_root / relative_path
    stderr = ""
    timed_out = False
    for shape_data in target["shapes"]:
        shape = shape_data["shape"]
        code = shape_data["command"]
        result = run_process(
            [sys.executable, "-c", code],
            cwd=repo_root,
            timeout_seconds=timeout,
        )
        if result.returncode == _subprocess_guard.TIMEOUT_EXIT_CODE:
            # Try the remaining shapes rather than returning. A `scripts/` module whose
            # PACKAGE-shape import hangs still deserves its legitimate direct shape; the
            # early return refused a module on the strength of the wrong loader.
            stderr = f"import did not finish within {timeout}s"
            timed_out = True
            continue
        if result.returncode == 0:
            return {"path": target["path"], "ok": True, "shape": shape}
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
            "path": target["path"],
            "ok": False,
            "kind": "timeout",
            "detail": stderr,
        }
    return {
        "path": target["path"],
        "ok": False,
        # A cycle is the class this check exists for and blocks. Anything else is
        # reported separately rather than folded in, because calling an unrelated
        # ImportError a cycle would make the first real cycle harder to believe.
        "kind": "cycle" if _is_cycle(lowered) else "import-error",
        "detail": (stderr.strip().splitlines() or ["(no stderr)"])[-1][:400],
    }


def run(repo_root: Path, *, changed: list[Path] | None, workers: int) -> dict:
    selection = select_standalone_targets(repo_root, changed=changed)
    targets = selection["targets"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda target: probe_module(repo_root, target), targets))
    cycles = [item for item in results if item.get("kind") == "cycle"]
    others = [item for item in results if not item["ok"] and item.get("kind") != "cycle"]
    # A module that imports in NO shape blocks too. Splitting cycle from import-error is
    # worth doing in the OUTPUT -- a missing dependency has a different fix -- but making
    # only one half blocking left the other as a hole: the gate would hold the evidence
    # that a changed module cannot be imported at all, print it as a note, and exit 0.
    return {
        "scope": selection["scope"],
        "checked": selection["checked"],
        "discovered": selection["discovered"],
        "cycles": cycles,
        "other_failures": others,
        "ok": not cycles and not others,
        "unmatched_changed": selection["unmatched_changed"],
        "scope_note": selection["scope_note"],
        "selection": "repograph standalone-targets v1",
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
    parser.add_argument(
        "--require-git-file-listing",
        action="store_true",
        help="Compatibility option; native selection always uses the repository inventory.",
    )
    args = parser.parse_args()

    try:
        report = run(
            args.repo_root.expanduser().resolve(),
            changed=args.changed,
            workers=min(64, max(1, args.workers)),
        )
    except NativeGateError as exc:
        print(f"native gate unavailable: {exc}", file=sys.stderr)
        return 1
    except NativeSelectionError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    # `verdict` and `failure_meaning` are folded in from the deleted human
    # renderer: the report carries `ok`, `cycles` and `other_failures`, but the
    # BLOCKED framing and the difference between the two failure classes (a cycle
    # is the class this gate exists for; an import-error is a module that imports
    # in NO shape, a different fix) lived only in its `CYCLE`/`BROKEN` prefixes.
    payload = dict(report)
    payload["verdict"] = "ok" if report["ok"] else "BLOCKED"
    if report["cycles"]:
        payload["cycle_meaning"] = (
            "an import CYCLE: this module cannot be imported first in a fresh interpreter"
        )
    if report["other_failures"]:
        payload["other_failure_meaning"] = (
            "did not import in any shape (not a cycle -- e.g. a missing third-party "
            "dependency; a different fix, and blocking all the same)"
        )
    emit_yaml(payload)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
