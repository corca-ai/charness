#!/usr/bin/env python3
"""Refuse a test whose verdict rides on a short timeout, and let the recorded ones only shrink.

The wall-clock form check (`check_wall_clock_form.py`) refuses `time.sleep`,
`time.monotonic`, and `time.perf_counter` calls in `tests/`. Hosted mutation run
33701977188 failed on 2026-09-03 in a test with none of them: a
`*_TIMEOUT_SECONDS` knob set to 0.5 s and an assertion that the child's stdout
held a line the child had to print before that deadline. On a loaded runner the
deadline fired first. The census that named every site of that shape is
`charness-artifacts/goal-runs/784/timeout-census.md` (#786); this gate is the
mechanism the class `detector-blind-class-unstated` graduates onto.

The rule is one closed AST predicate over a single `def test_*` function:

1. **Knob-bound.** A `*_TIMEOUT_SECONDS` name set to a literal under
   `KNOB_LIMIT_SECONDS` (5 s) by `env["X_TIMEOUT_SECONDS"] = "0.1"`,
   `monkeypatch.setenv("X_TIMEOUT_SECONDS", "0.1")`, `module.X_TIMEOUT_SECONDS = 0.25`,
   or `monkeypatch.setattr(module, "X_TIMEOUT_SECONDS", 0.25)`, together with an
   `assert` in the same function that reads `.stdout`, `.stderr`, `.returncode`,
   or a name bound from a `.communicate()` call -- directly, or through a name
   assigned from such a read in that function (`payload = yaml.safe_load(result.stdout)`
   then `assert payload[...]`; the hosted shape reads `probe["stdout_preview"]`
   two assignments away from `result.stdout`).
2. **Deadline-bound.** A `.communicate(timeout=N)`, `.run(..., timeout=N)`, or
   `.wait(timeout=N)` with a literal `N` under `DEADLINE_LIMIT_SECONDS` (1 s) in a
   `try` whose `except ... TimeoutExpired` handler holds an `assert` or a
   `raise AssertionError`.

A function that installs a controlled clock -- a `setattr` whose string target
ends in `time.monotonic`, `time.time`, or `time.perf_counter` -- is exempt: the
knob there is a heartbeat cadence and the budget is spent by an observation,
which is the replacement the wall-clock rule prescribes.

What this rule is deliberately blind to, stated so nobody reads a green as
"no timeout-bound test exists": a knob set in a fixture, helper, or module
constant rather than in the test function; a deadline passed through a
variable or a helper parameter rather than a literal; an assertion on a value
that reaches the test through a call or tuple unpack rather than through an
attribute read (`returncode, output = run(...)`); a fake that raises
`TimeoutExpired` (no clock is involved). Files under a `fixtures` directory are
children, not tests, and are not scanned. An empty matched universe is a
refusal (S40), never a pass.

The record, `charness-artifacts/quality/timeout-bound-baseline.json`, has the
wall-clock record's shape plus a `reasons` map: a kept site is kept with a
written reason (the census rule), a file above its count is red, a file below
its count is a prompt to lower the record, and `--write-baseline` refuses to
raise any count.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_repo_file_listing_module = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _repo_file_listing_module.iter_matching_repo_files

DEFAULT_SCAN_GLOBS = ("tests/*.py", "tests/**/*.py")
DEFAULT_BASELINE_REL = "charness-artifacts/quality/timeout-bound-baseline.json"
SKIP_PATH_PARTS = {"__pycache__", "fixtures"}
BASELINE_SCHEMA = "charness.timeout-bound-baseline/v1"
KNOB_SUFFIX = "_TIMEOUT_SECONDS"
KNOB_LIMIT_SECONDS = 5.0
DEADLINE_LIMIT_SECONDS = 1.0
DEADLINE_CALLS = frozenset({"communicate", "run", "wait"})
OUTPUT_ATTRS = frozenset({"stdout", "stderr", "returncode"})
CONTROLLED_CLOCKS = ("time.monotonic", "time.time", "time.perf_counter")


def _literal_seconds(node: ast.AST) -> float | None:
    """The numeric value of a literal knob or deadline; None for anything else."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return None
        if isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node.value, str):
            try:
                return float(node.value.strip())
            except ValueError:
                return None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _literal_seconds(node.operand)
        return None if inner is None else -inner
    return None


def _is_knob_name(name: str) -> bool:
    return name.endswith(KNOB_SUFFIX)


def _attr_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _string_constant(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _knob_sets(function: ast.FunctionDef) -> list[tuple[int, str, float]]:
    """Every `(line, knob, seconds)` the function sets to a literal under the limit."""
    sets: list[tuple[int, str, float]] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            seconds = _literal_seconds(node.value)
            if seconds is None:
                continue
            for target in node.targets:
                if isinstance(target, ast.Subscript):
                    key = _string_constant(target.slice)
                    if key and _is_knob_name(key):
                        sets.append((node.lineno, key, seconds))
                elif _is_knob_name(_attr_name(target)):
                    sets.append((node.lineno, _attr_name(target), seconds))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method == "setenv" and len(node.args) >= 2:
                key = _string_constant(node.args[0])
                seconds = _literal_seconds(node.args[1])
                if key and _is_knob_name(key) and seconds is not None:
                    sets.append((node.lineno, key, seconds))
            elif method == "setattr" and len(node.args) >= 3:
                key = _string_constant(node.args[1])
                seconds = _literal_seconds(node.args[2])
                if key and _is_knob_name(key) and seconds is not None:
                    sets.append((node.lineno, key, seconds))
    return [entry for entry in sets if entry[2] < KNOB_LIMIT_SECONDS]


def _reads_output(node: ast.AST, tainted: set[str]) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and sub.attr in OUTPUT_ATTRS:
            return True
        if isinstance(sub, ast.Name) and sub.id in tainted:
            return True
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr == "communicate":
                return True
    return False


def _tainted_names(function: ast.FunctionDef) -> set[str]:
    """Names bound, transitively, from an output read or a `communicate()` call."""
    tainted: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in ast.walk(function):
            if not isinstance(node, ast.Assign):
                continue
            if not _reads_output(node.value, tainted):
                continue
            for target in node.targets:
                for leaf in ast.walk(target):
                    if isinstance(leaf, ast.Name) and leaf.id not in tainted:
                        tainted.add(leaf.id)
                        changed = True
    return tainted


def _output_asserts(function: ast.FunctionDef) -> list[int]:
    tainted = _tainted_names(function)
    return [
        node.lineno
        for node in ast.walk(function)
        if isinstance(node, ast.Assert) and _reads_output(node.test, tainted)
    ]


def _has_controlled_clock(function: ast.FunctionDef) -> bool:
    for node in ast.walk(function):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr != "setattr" or not node.args:
            continue
        target = _string_constant(node.args[0])
        if target and target.endswith(CONTROLLED_CLOCKS):
            return True
        if len(node.args) >= 2:
            member = _string_constant(node.args[1])
            if member in {"monotonic", "time", "perf_counter"} and _dotted(node.args[0]).endswith(
                "time"
            ):
                return True
    return False


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return ""


def _handler_asserts(handler: ast.ExceptHandler) -> bool:
    for node in ast.walk(handler):
        if isinstance(node, ast.Assert):
            return True
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            if _attr_name(exc) == "AssertionError":
                return True
    return False


def _timeout_handlers(try_node: ast.Try) -> list[ast.ExceptHandler]:
    handlers = []
    for handler in try_node.handlers:
        if handler.type is None:
            continue
        names = (
            [_attr_name(elt) for elt in handler.type.elts]
            if isinstance(handler.type, ast.Tuple)
            else [_attr_name(handler.type)]
        )
        if "TimeoutExpired" in names:
            handlers.append(handler)
    return handlers


def _deadline_sites(function: ast.FunctionDef) -> list[tuple[int, str]]:
    """`(line, detail)` for each sub-second deadline whose TimeoutExpired handler asserts."""
    sites: list[tuple[int, str]] = []
    for try_node in ast.walk(function):
        if not isinstance(try_node, ast.Try):
            continue
        handlers = _timeout_handlers(try_node)
        if not any(_handler_asserts(handler) for handler in handlers):
            continue
        for node in try_node.body:
            for call in ast.walk(node):
                if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)):
                    continue
                if call.func.attr not in DEADLINE_CALLS:
                    continue
                for keyword in call.keywords:
                    if keyword.arg != "timeout":
                        continue
                    seconds = _literal_seconds(keyword.value)
                    if seconds is not None and seconds < DEADLINE_LIMIT_SECONDS:
                        sites.append(
                            (
                                call.lineno,
                                f"{call.func.attr}(timeout={seconds:g}) with an asserting TimeoutExpired handler",
                            )
                        )
    return sites


def timeout_bound_sites(source: str, filename: str) -> list[tuple[int, str]]:
    """Every timeout-bound verdict in one module: `(line, detail)`, one per test function."""
    tree = ast.parse(source, filename=filename)
    sites: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        if _has_controlled_clock(node):
            continue
        knobs = _knob_sets(node)
        asserts = _output_asserts(node)
        if knobs and asserts:
            line, knob, seconds = knobs[0]
            sites.append(
                (
                    node.lineno,
                    f"{node.name}: {knob}={seconds:g}s at line {line} with an assert on the child's output at line {asserts[0]}",
                )
            )
        for line, detail in _deadline_sites(node):
            sites.append((node.lineno, f"{node.name}: {detail} at line {line}"))
    return sites


def _iter_scan_paths(repo_root: Path, *, require_git: bool) -> list[Path]:
    paths = iter_matching_repo_files(repo_root, DEFAULT_SCAN_GLOBS, require_git=require_git)
    return [path for path in paths if not (set(path.parts) & SKIP_PATH_PARTS)]


def measure(repo_root: Path, *, require_git: bool) -> tuple[dict[str, list[tuple[int, str]]], int]:
    """Per-file timeout-bound sites for every scanned test file, plus the file count."""
    scan_paths = _iter_scan_paths(repo_root, require_git=require_git)
    found: dict[str, list[tuple[int, str]]] = {}
    for path in scan_paths:
        relative = path.relative_to(repo_root).as_posix()
        sites = timeout_bound_sites(path.read_text(encoding="utf-8"), str(path))
        if sites:
            found[relative] = sites
    return found, len(scan_paths)


def load_baseline(path: Path) -> tuple[dict[str, int], dict[str, str]]:
    """`(counts, reasons)`; every recorded file carries a written reason."""
    if not path.is_file():
        return {}, {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != BASELINE_SCHEMA:
        raise SystemExit(f"{path}: not a {BASELINE_SCHEMA} record")
    files = payload.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(k, str) and isinstance(v, int) and v > 0 for k, v in files.items()
    ):
        raise SystemExit(f"{path}: `files` must map test paths to positive site counts")
    reasons = payload.get("reasons")
    if not isinstance(reasons, dict) or not all(
        isinstance(reasons.get(k), str) and reasons[k].strip() for k in files
    ):
        raise SystemExit(f"{path}: `reasons` must carry a written reason for every recorded file")
    return dict(files), {k: str(v) for k, v in reasons.items()}


def judge(
    found: dict[str, list[tuple[int, str]]], baseline: dict[str, int]
) -> tuple[list[str], list[str]]:
    """`(failures, shrink_prompts)` for the measured tree against the record."""
    failures: list[str] = []
    prompts: list[str] = []
    for relative, sites in sorted(found.items()):
        allowed = baseline.get(relative, 0)
        if len(sites) > allowed:
            listed = "; ".join(f"{line} {detail}" for line, detail in sites)
            failures.append(
                f"{relative}: {len(sites)} timeout-bound verdict(s), baseline {allowed} "
                f"(sites: {listed}); a test's verdict must not depend on a deadline -- "
                "spend the budget by an observation on a controlled clock, delete the test, "
                "or record it with a written reason"
            )
        elif len(sites) < allowed:
            prompts.append(f"{relative}: {len(sites)} < baseline {allowed}; lower the record")
    for relative, allowed in sorted(baseline.items()):
        if relative not in found:
            prompts.append(f"{relative}: 0 < baseline {allowed}; drop it from the record")
    return failures, prompts


def write_baseline(
    path: Path,
    found: dict[str, list[tuple[int, str]]],
    previous: dict[str, int],
    reasons: dict[str, str],
) -> None:
    files = {relative: len(sites) for relative, sites in sorted(found.items())}
    raised = [rel for rel, count in files.items() if count > previous.get(rel, 0) and previous]
    if raised:
        raise SystemExit(
            "refusing to raise the timeout-bound baseline for: " + ", ".join(raised) + "; "
            "the record only shrinks"
        )
    missing = [rel for rel in files if not reasons.get(rel, "").strip()]
    if missing:
        raise SystemExit(
            "refusing to record a timeout-bound site without a written reason: "
            + ", ".join(missing)
        )
    payload = {
        "schema": BASELINE_SCHEMA,
        "files": files,
        "reasons": {rel: reasons[rel] for rel in files},
        "total": sum(files.values()),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    baseline_path = args.baseline or (repo_root / DEFAULT_BASELINE_REL)
    found, scanned = measure(repo_root, require_git=args.require_git_file_listing)
    if not scanned:
        raise SystemExit(
            "refusing empty matched universe for check_timeout_bound_form "
            f"(scan globs: {', '.join(DEFAULT_SCAN_GLOBS)})."
        )
    previous, reasons = load_baseline(baseline_path)
    if args.write_baseline:
        write_baseline(baseline_path, found, previous, reasons)
        print(
            f"Wrote timeout-bound baseline: {sum(len(s) for s in found.values())} site(s) in {len(found)} file(s)."
        )
        return 0
    failures, prompts = judge(found, previous)
    for prompt in prompts:
        print(f"ADVISORY: {prompt}", file=sys.stderr)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    total = sum(len(sites) for sites in found.values())
    print(
        f"Validated timeout-bound form: {scanned} test file(s) scanned, {total} recorded site(s) "
        f"in {len(found)} file(s), none new."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
