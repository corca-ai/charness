#!/usr/bin/env python3

"""Answer "what reads this?" for a symbol, a path, or a config key.

Issue #599, and the reason it is a command rather than a habit. Over one session
SEVEN removal-or-keep proposals were wrong, and every one was answerable by a
single grep that was never run: six proposed deletions each refuted by a file the
proposer had not opened, and one proposed KEEP whose defense the
source refutes. Settling them cost four bounded-reviewer spawns.

The GROUPING is the contribution, not the search. The same session hit the
inverse trap twice: `listed_skill_ids` and a generated fixture both look orphaned
and are consumed — one by an assertion on its value, one by a directory glob. A
plain `grep <name>` finds neither, and a zero result from a plain grep reads as
"nobody reads this" when it means "my search cannot see this kind of consumer".

So a zero result here never stands alone. Every answer carries the surfaces this
tool did NOT scan, and the negative case that matters is a reference living only
in one of them: it is reported as unscanned, never as zero. This narrows a blind
spot; it does not close it, and the difference is printed rather than implied.

Sibling: `removed_name_consumers.py` answers the same question for the narrower
case of a module-level name a slice just DELETED, from a diff. This one answers
it on demand, for three input kinds, before the deletion is proposed.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path, PurePosixPath

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

try:
    from scripts import what_reads_this_fallback as _fallback
except ModuleNotFoundError:
    import what_reads_this_fallback as _fallback

_inside_string_literal = _fallback.inside_string_literal
_lookup_column = _fallback.lookup_column
_position_in_string_span = _fallback.position_in_string_span
_fallback_string_spans = _fallback.string_spans
_fallback_structural_kind = _fallback.structural_kind

REPO_ROOT = repo_root_from_script(__file__)

_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
git_list_repo_files = _repo_file_listing.git_list_repo_files

#: Directories whose contents are copies, caches, or vendored code. ALWAYS
#: excluded -- unlike the `plugins/**` mirror below, no flag re-includes them.
#: A hit in one of them answers a different question than the one being asked.
_SKIP_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", "node_modules", "mutants", ".charness"}
_MIRROR_PREFIXES = ("plugins/",)

_TEXT_SUFFIXES = {
    ".py", ".sh", ".bash", ".zsh", ".md", ".yaml", ".yml", ".json", ".jsonc",
    ".toml", ".cfg", ".ini", ".txt", ".mjs", ".js", ".ts", "",
}

#: Stated on every answer, zero or not. Each line is a surface a reference can
#: live in that nothing below looks at.
UNSCANNED_SURFACES = (
    "git history — a consumer in a deleted or older revision is invisible here",
    "consumer repositories outside this checkout, including installed copies of this package",
    "names composed at runtime: f-strings, `getattr`, and paths built from variables",
    "binary files and any file that is not valid UTF-8",
    "`node_modules/**`, `mutants/**`, and cache directories, which are vendored or scratch copies",
    "files whose extension is outside this tool's text allowlist: tracked `.jsonl` ledgers and `.html` templates are valid UTF-8 and are NOT scanned",
    "for a path query: extension-only globs such as `*.json`, which match this file but say nothing about it",
    "for a path query: globs written outside source, config, and test files — a pattern in prose is not a program that opens the file",
)
_MIRROR_UNSCANNED = "the exported `plugins/**` mirror, which reads what the source reads (pass --include-mirrors to include it)"

_GLOB_LITERAL_RE = re.compile(r"""['"`]([^'"`\n]*[*?][^'"`\n]*)['"`]""")


def _iter_scan_files(repo_root: Path, *, include_mirrors: bool, require_git: bool) -> tuple[list[Path], bool]:
    """Text files to search, and whether the listing came from git.

    The flag is returned rather than logged because it changes what a zero
    result MEANS: a git listing sees tracked files, a filesystem walk sees
    whatever is on disk, and the two disagree exactly over files somebody has
    not committed yet.
    """
    tracked = git_list_repo_files(repo_root, include_untracked=True, require_git=require_git)
    from_git = tracked is not None
    candidates = tracked if from_git else [path for path in repo_root.rglob("*") if path.is_file()]
    files: list[Path] = []
    for path in candidates:
        # No `relative_to` guard. Both candidate sources are built FROM `repo_root` --
        # `git_list_repo_files` returns `repo_root / rel` and the fallback is
        # `repo_root.rglob("*")` -- and `pathlib` joins textually, so the prefix always
        # holds, including for a root spelled with `..`, a relative root, or a symlink.
        # The guard was a branch no input could reach: a line the changed-line gate can
        # never see covered, and one a reader can only mistake for a real case.
        rel = path.relative_to(repo_root).as_posix()
        if any(part in _SKIP_DIR_NAMES for part in PurePosixPath(rel).parts):
            continue
        if not include_mirrors and rel.startswith(_MIRROR_PREFIXES):
            continue
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        if path.is_file():
            files.append(path)
    return sorted(set(files)), from_git


def _surface_of(rel: str) -> str:
    if rel.startswith("tests/"):
        return "test"
    if rel.startswith(_MIRROR_PREFIXES):
        return "mirror"
    if rel.endswith(".md"):
        return "doc"
    if rel.rsplit(".", 1)[-1] in ("yaml", "yml", "json", "jsonc", "toml", "cfg", "ini"):
        return "config"
    return "source"


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _node_contains(node: ast.AST, position: tuple[int, int]) -> bool:
    """Whether an AST node spans a 1-based ``(line, UTF-8 byte column)``."""
    if not all(hasattr(node, field) for field in ("lineno", "col_offset", "end_lineno", "end_col_offset")):
        return False
    return (node.lineno, node.col_offset) <= position < (node.end_lineno, node.end_col_offset)


def _contains_node(container: ast.AST, candidate: ast.AST) -> bool:
    return container is candidate or any(node is candidate for node in ast.walk(container))


def _block_contains_raise(statements: list[ast.stmt]) -> bool:
    """Whether a branch refuses through a raise, excluding nested definitions."""
    pending: list[ast.AST] = list(statements)
    while pending:
        node = pending.pop()
        if isinstance(node, ast.Raise):
            return True
        if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef, ast.Lambda)):
            continue
        pending.extend(ast.iter_child_nodes(node))
    return False


class _PythonReferenceContext:
    """Structural context for symbol/config-key occurrences in Python code.

    Lexical references remain visible on every supported text surface. This
    context only upgrades a quoted occurrence when Python proves it is a mapping
    key or participates in a value-refusing condition, keeping an inert payload
    key and an error-message mention distinct from a live consumer.
    """

    def __init__(self, text: str, surface: str) -> None:
        self._tree: ast.AST | None = None
        self._parents: dict[ast.AST, ast.AST] = {}
        if surface not in ("source", "test"):
            return
        try:
            tree = ast.parse(text)
        except (SyntaxError, TypeError, ValueError):
            return
        self._tree = tree
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                self._parents[child] = parent

    @property
    def parseable(self) -> bool:
        return self._tree is not None

    def _candidate(self, line: str, line_no: int, column: int) -> ast.AST | None:
        if self._tree is None:
            return None
        position = (line_no, len(line[:column].encode("utf-8")))
        candidates = [node for node in ast.walk(self._tree) if _node_contains(node, position)]
        if not candidates:
            return None
        # Pick the leaf occurrence, not the enclosing comparison/call.
        return min(
            candidates,
            key=lambda node: (
                node.end_lineno - node.lineno,
                node.end_col_offset - node.col_offset
                if node.end_lineno == node.lineno
                else node.end_col_offset,
            ),
        )

    def _ancestors(self, node: ast.AST) -> list[ast.AST]:
        ancestors: list[ast.AST] = []
        while node in self._parents:
            node = self._parents[node]
            ancestors.append(node)
        return ancestors

    def kind(self, line: str, line_no: int, column: int) -> str | None:
        node = self._candidate(line, line_no, column)
        if node is None:
            return None
        ancestors = self._ancestors(node)
        for parent in ancestors:
            if isinstance(parent, ast.Assert) and _contains_node(parent.test, node):
                return "value-constraint"
            if isinstance(parent, ast.If) and _contains_node(parent.test, node):
                if _block_contains_raise(parent.body) or _block_contains_raise(parent.orelse):
                    return "value-constraint"
        for parent in ancestors:
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute) and parent.func.attr in {"get", "pop", "setdefault"}:
               if parent.args and _contains_node(parent.args[0], node):
                   return "lookup"
            if (
                isinstance(parent, ast.Subscript)
                and isinstance(parent.ctx, (ast.Load, ast.AugStore))
                and _contains_node(parent.slice, node)
            ):
               return "lookup"
        return None


def _symbol_kind(
    line: str,
    name: str,
    column: int,
    structural_kind: str | None = None,
    *,
    use_fallback: bool = True,
    fallback_inside_string: bool | None = None,
) -> str:
    """How this occurrence of ``name`` reads, from the line around it.

    AST context is supplied when the file is parseable Python; the line fallback
    keeps shell-like or incomplete source useful without turning a whole line's
    unrelated string into evidence. The categories exist so a reader can tell
    "three files define it" from "three files call it" at a glance; a misfiled
    category costs a second look, while a missing consumer costs a wrong deletion.
    """
    if use_fallback:
        structural_kind = structural_kind or _fallback_structural_kind(
            line, name, column, inside_string=fallback_inside_string
        )
    if structural_kind is not None:
        return structural_kind
    stripped = line.lstrip()
    if re.match(rf"(?:async\s+)?def\s+{re.escape(name)}\b", stripped) or re.match(rf"class\s+{re.escape(name)}\b", stripped):
        return "definition"
    if re.match(rf"{re.escape(name)}\s*(?::[^=]+)?=(?!=)", stripped):
        return "definition"
    if re.search(rf"\bimport\b[^#]*\b{re.escape(name)}\b", line):
        return "import"
    if column > 0 and line[column - 1] == ".":
        return "attribute-access"
    quoted = re.search(rf"""['"`][^'"`\n]*\b{re.escape(name)}\b[^'"`\n]*['"`]""", line)
    if quoted and quoted.start() <= column < quoted.end():
        return "string-literal"
    return "direct-name"


def _symbol_hits(text: str, name: str, surface: str) -> list[dict[str, object]]:
    pattern = re.compile(rf"(?<![\w]){re.escape(name)}(?![\w])")
    matches = [
        (line_no, line, match)
        for line_no, line in enumerate(text.splitlines(), start=1)
        for match in pattern.finditer(line)
    ]
    context = _PythonReferenceContext(text, surface) if matches else None
    fallback_string_spans = _fallback_string_spans(text) if context is None or not context.parseable else []
    hits: list[dict[str, object]] = []
    for line_no, line, match in matches:
        structural_kind = context.kind(line, line_no, match.start()) if context is not None else None
        use_fallback = context is None or (not context.parseable and surface in ("source", "test"))
        hits.append(
            {
                "kind": _symbol_kind(
                    line,
                    name,
                    match.start(),
                    structural_kind,
                    use_fallback=use_fallback,
                    fallback_inside_string=(
                        _position_in_string_span(fallback_string_spans, line_no, match.start())
                        if use_fallback
                        else None
                    ),
                ),
                "line": line_no,
                "source": line.strip()[:200],
            }
        )
    return hits


_GLOB_CACHE: dict[str, re.Pattern[str]] = {}


def _glob_regex(glob: str) -> re.Pattern[str]:
    """A glob compiled with PATH semantics, where `*` does not cross a `/`.

    `fnmatch` was the obvious reach here and it is wrong for this job: its `*`
    matches separators, so `*.json` matches every JSON file at every depth and
    `evals/*` matches the whole subtree. Measured before this fix, one query
    reported 248 glob consumers for a single fixture — an answer nobody reads,
    which is the same uselessness as a zero result wearing the opposite face.
    """
    cached = _GLOB_CACHE.get(glob)
    if cached is not None:
        return cached
    out: list[str] = []
    index = 0
    while index < len(glob):
        if glob.startswith("**/", index):
            out.append(r"(?:[^/]+/)*")
            index += 3
        elif glob.startswith("**", index):
            out.append(r".*")
            index += 2
        elif glob[index] == "*":
            out.append(r"[^/]*")
            index += 1
        elif glob[index] == "?":
            out.append(r"[^/]")
            index += 1
        else:
            out.append(re.escape(glob[index]))
            index += 1
    compiled = re.compile("".join(out) + r"\Z")
    _GLOB_CACHE[glob] = compiled
    return compiled


def _path_hits(text: str, target: str, surface: str) -> list[dict[str, object]]:
    """References to a path: literal, basename-only, or matched by a glob.

    The glob arm is the one a `grep <path>` cannot do, and it is the trap the
    issue records: a fixture consumed by `Path(dir).glob("*.fixture.json")` is
    read by nothing that names it.

    It runs only over source, config, and test files. A glob in a markdown artifact is
    prose about a pattern, not a program that will open the file, and including
    docs is most of what made the first measurement unreadable.

    Two strengths, kept apart. A glob containing `/` is anchored and matched
    against the whole path. A bare `*.fixture.json` is matched against the
    basename only, because the directory it will be joined to lives in code this
    does not read — so it is a candidate consumer, reported as `basename-glob`,
    not an established one.
    """
    basename = PurePosixPath(target).name
    suffix = PurePosixPath(target).suffix
    scan_globs = surface in ("source", "config", "test")
    hits: list[dict[str, object]] = []

    def too_generic(glob: str) -> bool:
        """Whether an unanchored glob says anything about THIS file.

        `*.fixture.json` names a family; `*.json` names a file extension. Both
        match, and only the first is evidence. Counting the second put 175
        matches on one query — the tool's answer becoming as unreadable as the
        grep it replaces, which is the same failure as reporting zero.
        """
        literal = re.sub(r"[*?]+", "", glob)
        return not literal.strip(".") or literal == suffix

    for line_no, line in enumerate(text.splitlines(), start=1):
        recorded = False
        if target in line:
            hits.append({"kind": "literal-path", "line": line_no, "source": line.strip()[:200]})
            recorded = True
        for match in _GLOB_LITERAL_RE.finditer(line) if scan_globs else ():
            glob = match.group(1)
            anchored = "/" in glob
            if not anchored and too_generic(glob):
                continue
            subject = target if anchored else basename
            if _glob_regex(glob).match(subject):
                hits.append(
                    {
                        "kind": "glob-consumption" if anchored else "basename-glob",
                        "line": line_no,
                        "source": line.strip()[:200],
                        "glob": glob,
                    }
                )
                recorded = True
        if not recorded and basename != target and re.search(rf"(?<![\w/]){re.escape(basename)}(?![\w])", line):
            # Weaker than a literal path and reported as such: a basename can
            # collide across directories, and calling that a consumer would make
            # the tool's confident answers less trustworthy than its uncertain
            # ones.
            hits.append({"kind": "basename-reference", "line": line_no, "source": line.strip()[:200]})
    return hits


def _config_key_hits(text: str, key: str, surface: str) -> list[dict[str, object]]:
    del surface  # config-key keeps its established lookup vocabulary
    quoted = re.escape(key)
    target_pattern = re.compile(rf"(?<![\w-]){quoted}(?![\w-])")
    hits: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        entry = {"line": line_no, "source": line.strip()[:200]}
        if re.match(rf"\s*-?\s*['\"]?{quoted}['\"]?\s*:", line):
            hits.append({"kind": "key-declaration", **entry})
            continue
        columns = [match.start() for match in target_pattern.finditer(line)]
        if any(_lookup_column(line, key, column) for column in columns):
            hits.append({"kind": "lookup", **entry})
            continue
        if re.search(rf"""['"]{quoted}['"]""", line):
            hits.append({"kind": "string-literal", **entry})
            continue
        if re.search(rf"(?<![\w-]){quoted}(?![\w-])", line):
            hits.append({"kind": "direct-name", **entry})
    return hits


_FINDERS = {"symbol": _symbol_hits, "path": _path_hits, "config-key": _config_key_hits}


def build_payload(
    repo_root: Path,
    *,
    target_kind: str,
    target: str,
    include_mirrors: bool = False,
    require_git: bool = False,
) -> dict[str, object]:
    files, from_git = _iter_scan_files(repo_root, include_mirrors=include_mirrors, require_git=require_git)
    finder = _FINDERS[target_kind]
    references: list[dict[str, object]] = []
    unreadable: list[str] = []
    for path in files:
        text = _read(path)
        rel = path.relative_to(repo_root).as_posix()
        if text is None:
            unreadable.append(rel)
            continue
        surface = _surface_of(rel)
        hits = finder(text, target, surface)
        if hits:
            references.append({"file": rel, "surface": surface, "hits": hits})
    by_kind: dict[str, int] = {}
    for entry in references:
        for hit in entry["hits"]:
            by_kind[str(hit["kind"])] = by_kind.get(str(hit["kind"]), 0) + 1
    unscanned = list(UNSCANNED_SURFACES)
    if not include_mirrors:
        unscanned.insert(0, _MIRROR_UNSCANNED)
    if not from_git:
        unscanned.append("nothing distinguished tracked from untracked files: git could not list this tree")
    if unreadable:
        unscanned.append(f"{len(unreadable)} file(s) this scan could not read -- not valid UTF-8, or not openable: {sorted(unreadable)[:5]}")
    return {
        "target_kind": target_kind,
        "target": target,
        "listing": "git" if from_git else "filesystem-walk",
        "files_scanned": len(files),
        "reference_count": sum(len(entry["hits"]) for entry in references),
        "reference_kinds": dict(sorted(by_kind.items())),
        "files_with_references": [entry["file"] for entry in references],
        "references": references,
        # Printed with every answer, not only the empty one. A reader who sees
        # this list on a NON-zero answer learns what the count excludes; a reader
        # who only ever saw it on zero would read it as an apology.
        "unscanned_surfaces": unscanned,
        "zero_result_caveat": (
            "No reference was found in the scanned surfaces. That is not "
            "'nothing reads this': read `unscanned_surfaces` before proposing a removal."
            if not references
            else None
        ),
    }


def _summary(payload: dict[str, object]) -> dict[str, object]:
    return {
        key: payload[key]
        for key in (
            "target_kind", "target", "listing", "files_scanned", "reference_count",
            "reference_kinds", "files_with_references", "unscanned_surfaces", "zero_result_caveat",
        )
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root to search")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--symbol", help="A function, class, constant, or attribute name")
    target.add_argument("--path", help="A repo-relative path, including one consumed only by a glob")
    target.add_argument("--config-key", help="An adapter, manifest, or settings key")
    parser.add_argument("--include-mirrors", action="store_true", help="Also search the exported plugins/** mirror")
    parser.add_argument("--require-git-file-listing", action="store_true", help="Refuse a filesystem walk when git cannot list the tree")
    parser.add_argument("--detail", action="store_true", help="Emit every reference with its line, not only the per-file summary")
    args = parser.parse_args()

    kind, value = ("symbol", args.symbol) if args.symbol else ("path", args.path) if args.path else ("config-key", args.config_key)
    payload = build_payload(
        args.repo_root.resolve(),
        target_kind=kind,
        target=value,
        include_mirrors=args.include_mirrors,
        require_git=args.require_git_file_listing,
    )
    emit_yaml(payload if args.detail else _summary(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
