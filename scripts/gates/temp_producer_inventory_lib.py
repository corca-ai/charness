"""Static producer discovery for the temporary-output registration gate."""

from __future__ import annotations

import ast
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_listing = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _listing.iter_matching_repo_files

# discovery-boundary: this gate intentionally inventories Python, shell, and JavaScript temp APIs
SCAN_GLOBS = (
    "scripts/**/*.py",
    "tools/**/*.py",
    "skills/public/*/scripts/**/*.py",
    "skills/shared/scripts/**/*.py",
    "scripts/**/*.sh",
    "tools/**/*.sh",
    "skills/public/*/scripts/**/*.sh",
    "scripts/**/*.js",
    "scripts/**/*.mjs",
    "scripts/**/*.cjs",
    "skills/public/*/scripts/**/*.js",
    "skills/public/*/scripts/**/*.mjs",
    "skills/public/*/scripts/**/*.cjs",
)
SKIP_PARTS = frozenset({"__pycache__", "generated", "vendor"})
TEMPFILE_APIS = {
    "TemporaryDirectory": "directory",
    "mkdtemp": "directory",
    "mkstemp": "atomic-file",
    "NamedTemporaryFile": "anonymous-file",
    "TemporaryFile": "anonymous-file",
    "mktemp": "anonymous-file",
}


@dataclass(frozen=True)
class Producer:
    identity: str
    path: str
    kind: str
    symbol: str
    line: int
    evidence: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "identity": self.identity,
            "path": self.path,
            "kind": self.kind,
            "symbol": self.symbol,
            "line": self.line,
            "evidence": self.evidence,
        }


def _relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _parents(tree: ast.AST) -> dict[int, ast.AST]:
    result: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            result[id(child)] = parent
    return result


def _assigned_name(node: ast.Call, parents: dict[int, ast.AST]) -> str:
    parent = parents.get(id(node))
    if isinstance(parent, ast.Assign) and len(parent.targets) == 1:
        target = parent.targets[0]
        return target.id if isinstance(target, ast.Name) else ""
    if isinstance(parent, ast.AnnAssign) and isinstance(parent.target, ast.Name):
        return parent.target.id
    if isinstance(parent, ast.withitem) and isinstance(parent.optional_vars, ast.Name):
        return parent.optional_vars.id
    return ""


class _PythonProducerVisitor(ast.NodeVisitor):
    def __init__(self, relative: str, modules: set[str], imported: dict[str, str], tree: ast.AST) -> None:
        self.relative = relative
        self.modules = modules
        self.imported = imported
        self.parents = _parents(tree)
        self.scopes: list[str] = []
        self.counts: Counter[str] = Counter()
        self.producers: list[Producer] = []

    def _scope(self) -> str:
        return ".".join(self.scopes) if self.scopes else "<module>"

    def _visit_scope(self, node: ast.AST, name: str) -> None:
        self.scopes.append(name)
        self.generic_visit(node)
        self.scopes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_scope(node, node.name)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_scope(node, node.name)

    def visit_Call(self, node: ast.Call) -> None:
        dotted = _dotted(node.func)
        api = ""
        if "." in dotted:
            owner, _, member = dotted.rpartition(".")
            if owner in self.modules and member in TEMPFILE_APIS:
                api = member
        elif dotted in self.imported:
            api = self.imported[dotted]
        if api:
            base = f"{self.relative}::{self._scope()}::"
            symbol = _assigned_name(node, self.parents) or api
            base += symbol
            self.counts[base] += 1
            identity = base if self.counts[base] == 1 else f"{base}#{self.counts[base]}"
            self.producers.append(
                Producer(
                    identity,
                    self.relative,
                    TEMPFILE_APIS[api],
                    symbol,
                    node.lineno,
                    f"Python tempfile.{api}()",
                )
            )
        self.generic_visit(node)


def python_producers(path: Path, repo_root: Path) -> list[Producer]:
    relative = _relative(path, repo_root)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return [Producer(f"{relative}::__parse__", relative, "parse-error", "__parse__", 1, str(exc))]
    modules = {"tempfile"}
    imported: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "tempfile":
                    modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "tempfile":
            for alias in node.names:
                if alias.name in TEMPFILE_APIS:
                    imported[alias.asname or alias.name] = alias.name
    visitor = _PythonProducerVisitor(relative, modules, imported, tree)
    visitor.visit(tree)
    return visitor.producers


def _mask_shell_line(line: str) -> str:
    result: list[str] = []
    quote = ""
    command_substitution = 0
    index = 0
    while index < len(line):
        char = line[index]
        next_char = line[index + 1] if index + 1 < len(line) else ""
        if quote == "'":
            result.append(" ")
            if char == "'":
                quote = ""
            index += 1
            continue
        if quote == '"' and command_substitution == 0:
            if char == '"':
                quote = ""
            elif char == "$" and next_char == "(":
                result.extend(("$", "("))
                command_substitution = 1
                index += 2
                continue
            elif char == "$":
                match = re.match(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?", line[index:])
                if match:
                    result.extend(match.group(0))
                    index += len(match.group(0))
                    continue
            result.append(" ")
            index += 1
            continue
        if command_substitution:
            if char == "(":
                command_substitution += 1
            elif char == ")":
                command_substitution -= 1
                if command_substitution == 0:
                    quote = '"'
            result.append(char)
            index += 1
            continue
        if char == "#" and (index == 0 or line[index - 1].isspace()):
            result.extend(" " for _ in line[index:])
            break
        if char in {"'", '"'}:
            quote = char
            result.append(" ")
        else:
            result.append(char)
        index += 1
    return "".join(result)


def _shell_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    heredoc: str | None = None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if heredoc is not None:
            if stripped == heredoc:
                heredoc = None
            continue
        if not stripped.startswith("#"):
            marker = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
            if marker:
                heredoc = marker.group(2)
            result.append((number, _mask_shell_line(line)))
    return result


def shell_producers(path: Path, repo_root: Path) -> list[Producer]:
    relative = _relative(path, repo_root)
    try:
        lines = _shell_lines(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return [Producer(f"{relative}::__parse__", relative, "parse-error", "__parse__", 1, str(exc))]
    producers: list[Producer] = []
    counts: Counter[str] = Counter()
    command = re.compile(r"(?:^|[;&|()])\s*(?:[A-Za-z_]\w*=\S+\s+)*mktemp\b(?P<tail>[^;&|)]*)")
    owned = re.compile(
        r"^\s*(?P<symbol>[A-Za-z_]\w*)\s*=\s*"
        r".*\$\{?CHARNESS_OWNED_SCRATCH_ROOT\}?"
    )
    for line, masked in lines:
        for match in command.finditer(masked):
            prefix = masked[: match.start()]
            assignment = re.search(r"([A-Za-z_]\w*)\s*=\s*(?:\$\(?\s*)?$", prefix)
            symbol = assignment.group(1) if assignment else "command"
            base = f"{relative}::shell::{symbol}"
            counts[base] += 1
            identity = base if counts[base] == 1 else f"{base}#{counts[base]}"
            directory = bool(re.search(r"(?:^|\s)(?:-d|--directory)(?:\s|$)", match.group("tail")))
            producers.append(Producer(identity, relative, "directory" if directory else "anonymous-file", symbol, line, "shell mktemp -d" if directory else "shell mktemp"))
        match = owned.match(masked)
        if match:
            symbol = match.group("symbol")
            base = f"{relative}::shell::{symbol}"
            counts[base] += 1
            identity = base if counts[base] == 1 else f"{base}#{counts[base]}"
            producers.append(Producer(identity, relative, "owned-directory", symbol, line, "explicit owned scratch root"))
    return producers


def _mask_js(text: str) -> str:
    result: list[str] = []
    quote = ""
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if quote:
            if char == "\\":
                result.extend((" ", " "))
                index += 2
                continue
            if char == quote:
                quote = ""
            result.append("\n" if char == "\n" else " ")
            index += 1
            continue
        if char == "/" and next_char == "/":
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            result.extend(" " for _ in text[index:end])
            if end < len(text):
                result.append("\n")
            index = end + 1 if end < len(text) else end
            continue
        if char == "/" and next_char == "*":
            end = text.find("*/", index + 2)
            end = len(text) if end < 0 else end + 2
            result.extend("\n" if value == "\n" else " " for value in text[index:end])
            index = end
            continue
        if char in {"'", '"', "`"}:
            quote = char
            result.append(" ")
        else:
            result.append(char)
        index += 1
    return "".join(result)


def javascript_producers(path: Path, repo_root: Path) -> list[Producer]:
    relative = _relative(path, repo_root)
    try:
        masked = _mask_js(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return [Producer(f"{relative}::__parse__", relative, "parse-error", "__parse__", 1, str(exc))]
    producers: list[Producer] = []
    counts: Counter[str] = Counter()
    raw = re.compile(r"\bmkdtempSync\s*\([^;\n]*?\btmpdir\s*\(\s*\)")
    owned = re.compile(
        r"\b(?:const|let|var)\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*=\s*"
        r"[^;]*\bjoin\s*\([^;]*\bCHARNESS_OWNED_SCRATCH_ROOT\b[^;]*"
    )
    for match in [*raw.finditer(masked), *owned.finditer(masked)]:
        line = masked.count("\n", 0, match.start()) + 1
        prefix = masked[: match.start()]
        functions = list(re.finditer(r"function\s+([A-Za-z_$][\w$]*)\s*\(", prefix))
        scope = functions[-1].group(1) if functions else "<module>"
        if match.re is raw:
            before = masked[max(0, masked.rfind("\n", 0, match.start())) : match.start()]
            assignment = re.search(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*$", before)
            symbol = assignment.group(1) if assignment else "mkdtempSync"
            kind, evidence = "directory", "JavaScript mkdtempSync(tmpdir())"
        else:
            symbol, kind, evidence = match.group("symbol"), "owned-directory", "explicit owned scratch root"
        base = f"{relative}::{scope}::{symbol}"
        counts[base] += 1
        identity = base if counts[base] == 1 else f"{base}#{counts[base]}"
        producers.append(Producer(identity, relative, kind, symbol, line, evidence))
    return producers


def discover_producers(repo_root: Path, *, require_git: bool = False) -> list[Producer]:
    paths = iter_matching_repo_files(repo_root, SCAN_GLOBS, require_git=require_git)
    paths = [path for path in paths if not set(path.parts).intersection(SKIP_PARTS)]
    result: list[Producer] = []
    for path in paths:
        if path.suffix == ".py":
            result.extend(python_producers(path, repo_root))
        elif path.suffix == ".sh":
            result.extend(shell_producers(path, repo_root))
        elif path.suffix in {".js", ".mjs", ".cjs"}:
            result.extend(javascript_producers(path, repo_root))
    return sorted(result, key=lambda producer: (producer.identity, producer.line))
