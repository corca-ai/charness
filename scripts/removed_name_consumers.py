#!/usr/bin/env python3

"""Name who still reads a module-level name this slice deleted.

Deleting a module-level name is a LEGITIMATE move and this must never block one.
The failure it exists for is narrower: nothing told the author there were readers.

The measured instance. A slice moved `LINK_RE` out of `check_doc_links.py` into a
shared module -- correct, and the right refactor. But
`check_doc_authoring_preflight.py` read it as `_doc_links.LINK_RE`, and that
consumption is a **dynamic attribute access on a module object** returned by
`import_repo_module`. Ruff cannot see it, an import graph cannot see it, and the
commit-boundary gates do not run the broad suite. The slice shipped a red suite
and a bounded reviewer found it a round later.

So the answer is information, not teeth: list the readers and let the author
decide. That is P1 -- judgment is enough on reversible work once the facts are
present, and the fact that was missing here was simply "there are three of these".

Frequency, measured over the 13 commits before this one: module-level deletions
in `scripts/` and skill `scripts/` occurred in ONE commit and removed exactly ONE
name -- the `LINK_RE` case. So this stays quiet enough to be worth reading when it
does speak.

Non-claim: a reader matched here is a TEXTUAL `.<name>` in a file that also
mentions the module. That is a candidate, not a proven binding -- an unrelated
attribute of the same name in a file that happens to mention the module will be
listed. The inverse is also possible: a consumer that reaches the module through
a variable built at runtime is not found. This narrows a blind spot; it does not
close it.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


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

try:
    from scripts.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from subprocess_guard import run_process
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_parity = import_repo_module(__file__, "scripts.parity_harness")
baseline_source = _parity.baseline_source

SCAN_GLOBS = ("scripts/**/*.py", "tools/**/*.py", "skills/**/scripts/**/*.py", "tests/**/*.py")
SKIP_DIR_NAMES = {"__pycache__", "plugins", "mutants", "node_modules", ".git"}


_BLOCK_NODES = (ast.Try, ast.If, ast.With, ast.For, ast.While)


def module_level_names(source: str) -> set[str]:
    """Names bound at module scope, including inside module-scope BLOCKS.

    Private names are INCLUDED. This repo really does read them across modules --
    `reviewer_boundary_fingerprint.py` binds `_STATE._status_path_map` -- so
    excluding them by convention would blind the check to real consumers.

    Blocks are descended into because a module-scope `try/except ImportError`
    fallback binds a real module-level name, and this repo uses that idiom
    (`rca_link_advisory.py`, `check_bootstrap_shim_consistency.py`,
    a retired producer). Scanning `tree.body` alone made the OPPOSITE
    error the loud one: wrapping an existing top-level definition in a portability
    `try/except` -- which removes nothing -- reported it as REMOVED and named every
    still-working reader. That is the false alarm that trains a reader to skip the
    advisory. Function and class bodies are NOT descended into: those bind locals
    and attributes, not module-level names.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    names: set[str] = set()

    def bind(target: ast.AST) -> None:
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                bind(element)

    def walk(body: list[ast.stmt]) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    bind(target)
            elif isinstance(node, ast.AnnAssign):
                bind(node.target)
            elif isinstance(node, _BLOCK_NODES):
                walk(node.body)
                walk(getattr(node, "orelse", []) or [])
                walk(getattr(node, "finalbody", []) or [])
                for handler in getattr(node, "handlers", []) or []:
                    walk(handler.body)

    walk(tree.body)
    return names


def removed_names(baseline: str, current: str) -> list[str]:
    return sorted(module_level_names(baseline) - module_level_names(current))


def _scan_files(repo_root: Path) -> list[Path]:
    seen: list[Path] = []
    for pattern in SCAN_GLOBS:
        for path in repo_root.glob(pattern):
            if not SKIP_DIR_NAMES & set(path.relative_to(repo_root).parts):
                seen.append(path)
    return sorted(set(seen))


def consumers_of(repo_root: Path, module_path: str, names: list[str]) -> dict[str, list[str]]:
    """`consumer_path -> [names it appears to read]`.

    Two conditions, both required, because either alone is far too broad: the file
    must mention the module (by stem, which catches `import_repo_module(__file__,
    "scripts.check_doc_links")` as well as a plain import), AND it must contain an
    attribute access `.<name>`. The module itself is excluded.
    """
    stem = Path(module_path).stem
    # `[ \t]*` not `\s*`: `\s` spans newlines, so a docstring sentence ending in
    # `.` followed by a line starting with the name matched, and these modules
    # carry long prose that cites both stems and constant names.
    # The second alternative catches `from <module> import NAME`, which contains no
    # dot at all. That shape fails loudly at import rather than silently, but it is
    # live in this repo and costs one branch.
    patterns = {
        name: re.compile(
            rf"\.[ \t]*{re.escape(name)}\b|from\s[^\n]*\b{re.escape(stem)}\s+import[^\n]*\b{re.escape(name)}\b"
        )
        for name in names
    }
    found: dict[str, list[str]] = {}
    for path in _scan_files(repo_root):
        relative = path.relative_to(repo_root).as_posix()
        if relative == module_path:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
        except OSError:
            continue
        if stem not in text:
            continue
        hits = sorted(name for name, pattern in patterns.items() if pattern.search(text))
        if hits:
            found[relative] = hits
    return found


def build_report(repo_root: Path, paths: list[str], against: str) -> dict:
    report: dict = {"against": against, "removed": {}, "consumers": {}, "uncomparable": {}}
    for path in sorted(paths):
        baseline = baseline_source(repo_root, path, against)
        if baseline is None:
            # NOT the same answer as "nothing was removed". On a shallow clone or a
            # consumer repo with no `origin/main`, every path lands here, and a
            # silent pass would read as a clean check that never ran.
            report["uncomparable"][path] = f"no baseline at `{against}`"
            continue
        target = repo_root / path
        if target.exists():
            try:
                current = target.read_text(encoding="utf-8", errors="surrogateescape")
            except OSError:
                report["uncomparable"][path] = "unreadable in the worktree"
                continue
        else:
            # A deleted file removes every name it defined, which is the useful answer.
            current = ""
        gone = removed_names(baseline, current)
        if not gone:
            continue
        readers = consumers_of(repo_root, path, gone)
        report["removed"][path] = gone
        if readers:
            report["consumers"][path] = readers
    report["consumer_count"] = sum(len(readers) for readers in report["consumers"].values())
    report["uncomparable_count"] = len(report["uncomparable"])
    # The ATTENTION STATE, named in the payload rather than only in a prose line
    # ("skipped: N uncomparable path(s)"). A neutral `uncomparable_count` does not
    # say those paths went UNEXAMINED, and that distinction -- an empty result
    # versus an unexamined one -- is the whole reason this file is declared in
    # `skills/public/quality/references/attention-state-visibility.json`.
    report["skipped"] = {"reason": "uncomparable", "path_count": report["uncomparable_count"]}
    return report


def slice_base_paths(repo_root: Path, against: str, fallback: list[str]) -> list[str]:
    """Every `.py` changed since the slice base, committed ones included.

    Changing the BASELINE without changing the PATH SET is only half the fix: a
    name deleted in an earlier slice commit leaves that file clean, so the
    worktree-dirty set does not contain it and it is never inspected -- which is
    the measured incident replayed exactly. Falls back to the caller's set when
    the base does not resolve.
    """
    proc = run_process(
        ["git", "-C", str(repo_root), "diff", "--name-only", f"{against}...HEAD"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if proc.returncode != 0:
        return fallback
    return sorted(set(fallback) | {line for line in proc.stdout.split() if line.endswith(".py")})


def advise_removed_name_consumers(
    repo_root: Path, changed_paths: list[str], against: str = "HEAD"
) -> None:
    """Print an ADVISORY naming the files that still read a deleted module-level name."""
    changed_paths = slice_base_paths(Path(repo_root), against, list(changed_paths))
    candidates = [
        path
        for path in changed_paths
        # `plugins/` and `mutants/` are generated copies; reporting them doubles
        # every finding under a path no author edits.
        if path.endswith(".py") and not path.startswith(("plugins/", "mutants/"))
    ]
    if not candidates:
        return
    report = build_report(Path(repo_root), candidates, against)
    if not report["consumers"]:
        return
    rendered = "; ".join(
        f"{module} lost {', '.join(report['removed'][module])} — still read by "
        + ", ".join(f"{reader} ({', '.join(names)})" for reader, names in sorted(readers.items()))
        for module, readers in sorted(report["consumers"].items())
    )
    print(
        f"ADVISORY: this slice removed module-level name(s) that {report['consumer_count']} other file(s) "
        f"still appear to read — {rendered}. Deleting the name is fine; shipping it without updating those "
        "readers is not, and a dynamic `module.NAME` access is invisible to ruff and to the import graph, "
        "so no commit-boundary gate will catch it. Each hit is a textual candidate, not a proven binding.",
        file=sys.stderr,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--against", default="HEAD")
    parser.add_argument("--paths", nargs="*", default=None)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    paths = args.paths or _parity.changed_python_paths(root)
    report = build_report(root, paths, args.against)

    # The prose branch restated `against`, `uncomparable_count`, `removed`, and
    # `consumers` -- all payload keys. Its only added token was the phrase
    # "no candidate reader found", which is the absence of a `consumers` entry for
    # that module and is readable as such.
    emit_yaml(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
