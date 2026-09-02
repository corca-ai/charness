#!/usr/bin/env python3

"""Prove a repair changed only what it meant to change.

A bounded reviewer's finding is a POINT. The repair is a change to a FUNCTION.
The blast radius is that function's entire prior behaviour, and the tests written
for the original only cover properties someone already thought to name. So a
repair can silently NARROW a property no test ever asserted, and every gate stays
green while the narrowing ships.

That is not a hypothesis. In one slice of this repo, three surfaces were repaired
by the same agent in the same session:

    check_doc_links.validate_link      differentially verified   0 defects found
    markdown_doc_scan.iter_doc_lines   differentially verified   0 defects found
    check_plugin_doc_links.iter_unfollowable_links   NOT verified   3 defects found

The three defects were all narrowings: per-line scanning stopped matching
prose-wrapped links, a fence toggle inverted on mismatched markers, and live text
after a mid-line `-->` was dropped. Each was invisible to every existing test,
because each removed a behaviour nothing had named.

So the discipline this module makes affordable is:

    **State the intended delta. Prove the complement is unchanged.**

Two baselines, and the second is the one that matters:

- a committed ref (`--against <ref>`), for repairing a function that shipped;
- the **reviewer-boundary snapshot** (`--against review-snapshot`), for repairing
  a function created earlier in this same slice. The defect above lives here:
  at commit granularity `iter_unfollowable_links` is a NEW function with nothing
  to diff against, and a commit-ranged tool cannot see the repair at all. What
  the reviewer READ is the only honest baseline for it.

Non-claim: identical outcomes over a corpus is evidence about that corpus, not a
proof of equivalence. This harness narrows where a narrowing can hide; it does
not prove none is left.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Iterable


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

REVIEW_SNAPSHOT = "review-snapshot"
SNAPSHOT_RELATIVE_PATH = Path(".charness/reviewer-boundary/snapshot.json")
BLOB_RELATIVE_DIR = Path(".charness/reviewer-boundary/blobs")


class ParityError(Exception):
    pass


def source_at_ref(repo_root: Path, path: str, ref: str) -> str | None:
    """Source of `path` at a committed ref, or None when it did not exist there."""
    proc = run_process(
        ["git", "-C", str(repo_root), "show", f"{ref}:{path}"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    return proc.stdout if proc.returncode == 0 else None


def source_at_review_snapshot(repo_root: Path, path: str) -> str | None:
    """Source of `path` as the last bounded reviewer read it, or None.

    None has two distinct meanings and the caller must not conflate them: the path
    was never captured (no snapshot, a stale one, or a file that was clean when the
    reviewer read it), versus it WAS captured and its blob is now gone or
    unreadable -- a lost baseline. `captured_paths()` separates them. A captured
    empty file returns `""`, never None.
    """
    blob_key = _snapshot_source_blobs(repo_root).get(path)
    if blob_key is None:
        return None
    blob = repo_root / BLOB_RELATIVE_DIR / blob_key
    try:
        return blob.read_text(encoding="utf-8", errors="surrogateescape")
    except OSError:
        return None


def _current_head(repo_root: Path) -> str | None:
    proc = run_process(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def snapshot_payload(repo_root: Path) -> dict:
    """The reviewer snapshot, but ONLY while it still describes the current HEAD.

    The snapshot file is durable gitignored state that nothing expires. Without
    this binding, a snapshot written during slice N keeps answering for slice
    N+1, and the advisory built on it announces "a bounded reviewer read this"
    about a slice where no review ran -- a false claim, and exactly the
    false-alarm-trains-the-reader failure this tool exists to avoid.

    Binding to HEAD is deliberately conservative: committing mid-slice discards
    the baseline and every path becomes `uncomparable`, which is a visible
    "unexamined" rather than a reassuring zero.
    """
    try:
        payload = json.loads((repo_root / SNAPSHOT_RELATIVE_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    head = _current_head(repo_root)
    if head is not None and payload.get("head") != head:
        return {}
    return payload


def _snapshot_source_blobs(repo_root: Path) -> dict[str, str]:
    blobs = snapshot_payload(repo_root).get("source_blobs")
    return blobs if isinstance(blobs, dict) else {}


def captured_paths(repo_root: Path) -> list[str]:
    return sorted(_snapshot_source_blobs(repo_root))


def baseline_source(repo_root: Path, path: str, against: str) -> str | None:
    if against == REVIEW_SNAPSHOT:
        return source_at_review_snapshot(repo_root, path)
    return source_at_ref(repo_root, path, against)


def _function_shapes(source: str) -> dict[str, tuple[str, str]]:
    """`qualified_name -> (signature_dump, body_dump)` for every function in the module.

    Names are QUALIFIED by their enclosing classes and functions (`A.run`, not
    `run`). A flat `node.name` key collapses same-named siblings -- two classes
    with a `run`, a helper shadowed by a method -- and a collapse is wrong in both
    directions: repairing `A.run` becomes invisible when `B.run` is walked later
    and overwrites it, and merely ADDING `B.helper` reads as a repair of
    `A.helper`. Both were reproduced before this was qualified.

    Nested functions are included: a closure a repaired function delegates to is
    exactly where a narrowing hides.

    Decorators are compared as part of the BODY, not the signature. Swapping
    `@lru_cache` on, adding `@staticmethod`, or changing `@retry(3)` to
    `@retry(1)` changes behaviour while leaving the caller-visible interface
    identical -- which is the definition of the shape this harness hunts, so it
    must not be filed under "signature changed" and excluded.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ParityError(f"cannot parse source: {exc}") from exc
    shapes: dict[str, tuple[str, str]] = {}

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified = f"{prefix}{child.name}"
                # Qualifying by scope is not enough: a name can be defined TWICE in
                # one scope and legitimately so -- an import-fallback `try/except`
                # pair, `@property` + `@x.setter`, `@overload` stubs before the
                # implementation. Last-definition-wins reintroduced exactly the
                # collapse qualification was added to remove, so redefinitions get
                # an ordinal suffix instead of overwriting.
                if qualified in shapes:
                    ordinal = 2
                    while f"{qualified}#{ordinal}" in shapes:
                        ordinal += 1
                    qualified = f"{qualified}#{ordinal}"
                decorators = "".join(ast.dump(dec) for dec in child.decorator_list)
                body = ast.dump(ast.Module(body=child.body, type_ignores=[]))
                shapes[qualified] = (ast.dump(child.args), decorators + "|" + body)
                walk(child, f"{qualified}.")
            elif isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}.")
            else:
                walk(child, prefix)

    walk(tree, "")
    return shapes


def repair_shaped_functions(baseline: str, current: str) -> list[str]:
    """Functions whose signature is unchanged but whose body changed.

    That pair is the silent-narrowing shape specifically. A changed SIGNATURE is
    loud — every caller has to be updated, so the blast radius is walked by hand.
    A new function has no prior behaviour to preserve. It is the function that
    still looks the same from outside while behaving differently inside that ships
    a narrowing nobody is looking for.
    """
    before, after = _function_shapes(baseline), _function_shapes(current)
    return sorted(
        name
        for name, (signature, body) in after.items()
        if name in before and before[name][0] == signature and before[name][1] != body
    )


def load_module_from_source(source: str, module_name: str) -> Any:
    """Import a module from source text, without leaving it in `sys.modules`.

    The baseline module and the current one define the same names, so leaking
    either into `sys.modules` would let the second import win and silently make
    the comparison compare a module against itself.
    """
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    if spec is None:
        raise ParityError(f"cannot build a module spec for {module_name}")
    module = importlib.util.module_from_spec(spec)
    module.__file__ = f"<parity:{module_name}>"
    saved_path = list(sys.path)
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)  # noqa: S102
    except Exception as exc:  # noqa: BLE001 - a baseline that cannot load is a usage error
        raise ParityError(f"baseline module {module_name} failed to load: {exc!r}") from exc
    finally:
        sys.path[:] = saved_path
    return module


ITERATOR_MATERIALISE_CAP = 10_000
_DEFAULT_REPR_ADDRESS_RE = re.compile(r"(?<= at )0x[0-9a-fA-F]+(?=>)")


def _render_value(value: Any) -> str:
    """A comparable rendering of a return value.

    Two hazards, both of which produced FALSE GREENS before this existed:

    - **A generator is not its contents.** Calling a generator function runs no
      body; it returns an object whose repr is an address. Two totally different
      generators therefore compared EQUAL and the harness reported "0 divergences"
      for a function it never executed -- intermittently, since it depended on
      CPython reusing the freed address. Generators are materialised, capped at
      `ITERATOR_MATERIALISE_CAP` ITEMS. Three costs, stated rather than hidden:
      the body RUNS (twice per input, once per side, so side effects happen), the
      cap bounds items and not time or memory (a generator that blocks still
      hangs), and a raise mid-iteration keeps the prefix already yielded.
    - **Only true generators**, via `inspect.isgenerator`, not everything with
      `__next__`. A file handle, socket, or DB cursor has one too; iterating a
      returned handle consumed it AND erased the `name=`/`mode=` repr that made
      two different handles distinguishable, so the broader test lost signal.
    - **Default reprs carry addresses.** An object without `__repr__` renders its
      identity, which differs between the two loads, so the ` at 0x...>` tail of
      that exact shape is normalised. The regex is anchored to the default-repr
      form on purpose: normalising every `0x...` token erased legitimate hex DATA,
      making `hex(n)` and `hex(n * 2)` compare equal. The residual cost is that two
      distinct objects rendering only their identity still compare equal.
    """
    if inspect.isgenerator(value):
        items: list[str] = []
        try:
            for index, item in enumerate(value):
                if index >= ITERATOR_MATERIALISE_CAP:
                    items.append(f"<truncated at {ITERATOR_MATERIALISE_CAP}>")
                    break
                items.append(repr(item))
        except Exception as exc:  # noqa: BLE001 - a raise mid-iteration is behaviour
            # The prefix is KEPT. Discarding it made "yields 1,2,3 then raises" and
            # "raises immediately" render identically, hiding a narrowing that
            # stopped yielding before the same failure.
            return "generator-partial:" + repr((items, type(exc).__name__, str(exc)))
        return "generator:" + repr(items)
    return _DEFAULT_REPR_ADDRESS_RE.sub("0xADDR", repr(value))


def outcome(fn: Callable[..., Any], args: tuple) -> tuple:
    """Normalise a call to a comparable `(kind, payload)`.

    An exception is an OUTCOME, not a harness failure: "used to raise
    ValidationError, now returns None" is precisely a narrowing worth catching,
    and a harness that let exceptions escape would report it as a crash instead.
    A generator that raises only once iterated raises HERE, inside
    `_render_value`, and is reported the same way -- which is the point.
    """
    try:
        return ("return", _render_value(fn(*args)))
    except Exception as exc:  # noqa: BLE001 - comparing behaviour includes failure behaviour
        return ("raise", type(exc).__name__, str(exc))


def compare_callables(
    baseline_fn: Callable[..., Any],
    current_fn: Callable[..., Any],
    inputs: Iterable[tuple],
) -> list[dict]:
    """Every input where the two disagree. Empty means agreement ON THIS CORPUS."""
    divergences: list[dict] = []
    for args in inputs:
        before, after = outcome(baseline_fn, args), outcome(current_fn, args)
        if before != after:
            divergences.append({"input": repr(args), "baseline": before, "current": after})
    return divergences


def changed_python_paths(repo_root: Path) -> list[str]:
    """Changed and untracked `.py` paths, via `-z` so no path shape is dropped.

    Line-oriented `--porcelain` C-quotes any path with a quote, backslash, control
    character, or (by default) a non-ASCII byte, so `"scripts/caf\303\251.py"`
    stopped ending in `.py` and vanished from the set. `-z` emits paths verbatim,
    which is what the sibling `reviewer_boundary_state._status_entries` already does.

    A rename yields BOTH sides: the new path is what exists now, and the old path
    is what the reviewer's snapshot captured under, so keeping both is what lets a
    rename-plus-repair still find its baseline.
    """
    try:
        proc = run_process(
            [
                "git",
                "-C",
                str(repo_root),
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
            ],
            cwd=repo_root,
            timeout_seconds=None,
        )
    except OSError:
        return []
    if proc.returncode != 0:
        return []
    fields = [field for field in proc.stdout.split("\0") if field]
    paths: list[str] = []
    index = 0
    while index < len(fields):
        entry = fields[index]
        index += 1
        if len(entry) < 4:
            continue
        status, candidate = entry[:2], entry[3:]
        paths.append(candidate)
        if "R" in status or "C" in status:
            # Under -z the ORIGINAL path is the next NUL-separated field.
            if index < len(fields):
                paths.append(fields[index])
                index += 1
    return [path for path in paths if path.endswith(".py")]


def _render_repairs(repo_root: Path, paths: list[str], against: str) -> dict:
    report: dict[str, Any] = {"against": against, "files": {}, "uncomparable": {}}
    if against == REVIEW_SNAPSHOT:
        snapshot = snapshot_payload(repo_root)
        report["snapshot_window"] = (snapshot.get("window") or {}).get("id")
        report["snapshot_head"] = snapshot.get("head")
    for path in paths:
        baseline = baseline_source(repo_root, path, against)
        if baseline is None:
            if against == REVIEW_SNAPSHOT and path in _snapshot_source_blobs(repo_root):
                report["uncomparable"][path] = (
                    "LOST baseline: the snapshot recorded a blob for this path and the blob is "
                    "gone or unreadable — the reviewer's version can no longer be recovered"
                )
            else:
                report["uncomparable"][path] = (
                    "no baseline: the path did not exist at that ref, or the reviewer snapshot "
                    "did not capture it (only Python sources dirty at snapshot time are captured)"
                )
            continue
        try:
            current = (repo_root / path).read_text(encoding="utf-8", errors="surrogateescape")
        except OSError:
            report["uncomparable"][path] = "unreadable in the worktree"
            continue
        repairs = repair_shaped_functions(baseline, current)
        if repairs:
            report["files"][path] = repairs
    report["repair_count"] = sum(len(names) for names in report["files"].values())
    return report


# The next step a repair-shaped finding demands. Output is unconditionally YAML,
# so this lives in the payload: it used to exist only in the human rendering, and
# the report itself NAMES functions without ever saying what to do about them --
# dropping it would leave a reader with a list and no obligation.
NEXT_STEP = (
    "State the INTENDED delta for each, then prove the complement is unchanged -- "
    "load the baseline with `load_module_from_source(baseline_source(...))` and run "
    "`compare_callables` over a real corpus. Identical outcomes on that corpus is "
    "evidence about the corpus, not a proof of equivalence."
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--against",
        default=REVIEW_SNAPSHOT,
        help=f"a git ref, or `{REVIEW_SNAPSHOT}` for what the last bounded reviewer read",
    )
    parser.add_argument(
        "--paths", nargs="*", default=None, help="defaults to the captured/changed set"
    )
    args = parser.parse_args()

    root = args.repo_root.resolve()
    paths = args.paths
    if not paths:
        if args.against == REVIEW_SNAPSHOT:
            # UNION, not just the captured set. A file that was clean when the
            # reviewer read it is never captured, so a captured-only default would
            # print a reassuring zero for the most ordinary case there is --
            # reviewing already-committed code and repairing it. Including the
            # changed set puts those paths in `uncomparable`, where "could not
            # compare" stays distinguishable from "nothing was repaired".
            paths = sorted(set(captured_paths(root)) | set(changed_python_paths(root)))
        else:
            proc = run_process(
                ["git", "-C", str(root), "diff", "--name-only", args.against],
                cwd=root,
                timeout_seconds=None,
            )
            paths = [line for line in proc.stdout.split() if line.endswith(".py")]
    report = _render_repairs(root, sorted(paths), args.against)
    # Unconditional YAML. Everything the retired rendering said EXCEPT the next step
    # and the skip LABEL was a projection of `against`, `files`, `repair_count`, and
    # `uncomparable`; the next step is only present when there is something to do about.
    report["next_step"] = NEXT_STEP if report["files"] else None
    # The retired line read `skipped: N uncomparable path(s)`. The COUNT is derivable
    # from `uncomparable`, but the word that names this as an attention state is not:
    # a bare per-path map reads as data, while `skipped` says these paths were never
    # examined. `attention-state-visibility.json` declares this file's state as
    # `skipped` for exactly that reason, so the label rides in the payload.
    report["skipped"] = f"skipped: {len(report['uncomparable'])} uncomparable path(s)"
    emit_yaml(report)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ParityError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
