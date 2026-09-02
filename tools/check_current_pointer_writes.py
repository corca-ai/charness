#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import importlib.util
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from scripts.core.repo_file_listing import (
        RepoFileSnapshot,
        iter_matching_repo_files,
        iter_repo_files,
    )
    from scripts.core.repo_layout import support_dir
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:  # invoked directly with only the scripts directory importable
    _repo_file_listing_spec = importlib.util.spec_from_file_location(
        "repo_file_listing",
        Path(__file__).resolve().parents[1] / "scripts" / "core" / "repo_file_listing.py",
    )
    if _repo_file_listing_spec is None or _repo_file_listing_spec.loader is None:
        raise
    _repo_file_listing = importlib.util.module_from_spec(_repo_file_listing_spec)
    _repo_file_listing_spec.loader.exec_module(_repo_file_listing)
    RepoFileSnapshot = _repo_file_listing.RepoFileSnapshot
    iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files
    iter_repo_files = _repo_file_listing.iter_repo_files
    _repo_layout_spec = importlib.util.spec_from_file_location(
        "repo_layout", Path(__file__).resolve().parents[1] / "scripts" / "core" / "repo_layout.py"
    )
    if _repo_layout_spec is None or _repo_layout_spec.loader is None:
        raise
    _repo_layout = importlib.util.module_from_spec(_repo_layout_spec)
    _repo_layout_spec.loader.exec_module(_repo_layout)
    support_dir = _repo_layout.support_dir

    from yaml_output import emit_yaml

_SUPPORT_PATTERN_PREFIX = "skills/support"
#: Namespace discriminator for a finding in an EXTERNAL support tree. Deliberately
#: not a spellable repo path: naming such a file `skills/support/<rel>` collides
#: with a real, different, in-repo file, so a consumer of the emitted `path`/`line`
#: pair would be pointed at unrelated code. Round-2 review.
_EXTERNAL_SUPPORT_PREFIX = "<external-support>"

CURRENT_POINTER_NAMES = {"latest.md", "latest.json"}
WRITE_CALL_TOKENS = ("write_text", "write_bytes", "open")
HELPER_FILES = {
    Path("scripts/artifacts/current_pointer_writer_lib.py"),
}
SCAN_ROOTS = (
    Path("scripts"),
    Path("skills/public"),
    Path("skills/support"),
    # `skills/shared` was omitted, so a direct current-pointer write there was
    # never scanned and the gate reported clean over a scope excluding it (D9).
    # Confirmed: an identical violation was caught under `scripts/` and
    # `skills/public/` and invisible under `skills/shared/`.
    Path("skills/shared"),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    target: str
    reason: str


def _git_visible_python_files(repo_root: Path, *, require_git: bool = False) -> list[Path]:
    """The scanned population, derived by the repo's ONE population owner.

    A guard's population IS a verdict surface: a sweep that is wrong about which
    files it covers reports clean over a scope that excluded the violation. This
    file already carries that scar -- `skills/shared` was omitted from
    ``SCAN_ROOTS`` and an identical violation was invisible there while being
    caught under two other roots.

    So the roots stay here (they are this check's scope, and this check owns
    them) and the LISTING is delegated to ``repo_file_listing``, which 10+ other
    validators already share. Delegating fixes three things the hand-rolled copy
    got wrong, none of which its tests could see:

    - it split ``git ls-files`` output on newlines. Without ``-z`` git C-QUOTES
      such a path (measured: the entry arrives as ``"scripts/we\\nird.py"``,
      quotes and escape included), so the old code got one quoted non-path that
      failed ``is_file()`` and the real file silently left the population. The
      owner uses ``-z``. (Round-1 review corrected the MECHANISM here: the first
      draft of this sentence said "two bogus fragments", which is what a raw
      newline would produce and is not what git emits.)
    - on git failure it fell back to ``rglob`` SILENTLY, swapping a
      gitignore-aware population for one that is not, with no signal. The owner
      exposes ``require_git``, and ``main`` now passes it through
      ``--require-git-file-listing`` so this gate can REFUSE rather than report
      clean over a population it did not establish.
    - it matched roots with ``is_relative_to``, so a support tree relocated by
      ``CHARNESS_SUPPORT_DIR`` was silently empty. The owner resolves that split
      and returns paths in the external tree.

    Scope of that last one, stated precisely because the first draft of this
    docstring claimed more than the code did and round-1 review caught it: the
    external support tree is now REACHED, and ``_display_path`` gives its files a
    reportable name instead of crashing on ``relative_to``. It is NOT
    gitignore-filtered -- ``iter_matching_repo_files`` globs an external support
    root directly, with no ``git ls-files`` intersection. And the sibling split
    is unhandled: ``skills/public`` has a packaged-layout fallback in
    ``repo_layout`` that the pattern-based population does not consult, exactly
    as before this change.

    Population measured before and after the delegation, at ``90ebf423``: 683
    files both times, identical set. The COUNT goes stale the next time a ``.py``
    file lands under one of the roots; the identity is the claim that matters.
    """
    patterns = tuple(f"{root.as_posix()}/**/*.py" for root in SCAN_ROOTS)
    # ONE explicit snapshot, threaded through both listing calls below. Passing it
    # is what actually makes the second call free: without it, each call falls
    # back to whatever `RepoFileSnapshot` the process happens to have bound as the
    # pytest subject (or none at all outside pytest), and the inline claim that
    # "there is no second git call" held only by that accident.
    snapshot = RepoFileSnapshot(repo_root, require_git=require_git)
    files = set(
        iter_matching_repo_files(repo_root, patterns, require_git=require_git, snapshot=snapshot)
    )
    # UNION, not swap. The owner REPLACES a `skills/support/` pattern with the
    # external tree when `CHARNESS_SUPPORT_DIR` is set -- so delegating naively
    # dropped this repo's own 25 tracked files under `skills/support/` from the
    # population, silently, on exactly the hosts that set it. That is D9 again in
    # the file that carries the D9 scar, and round-2 review caught it: the first
    # repair traded a silently-empty EXTERNAL tree for a silently-dropped IN-REPO
    # one. Both are scanned now. Measured: 683 with no override, 660 under an
    # override before this union, 683 + external after it.
    in_repo_support = repo_root / _SUPPORT_PATTERN_PREFIX
    if support_dir(repo_root) != in_repo_support.resolve() and in_repo_support.is_dir():
        # No second git call: the SAME snapshot instance answers this listing too.
        tracked = set(iter_repo_files(repo_root, require_git=require_git, snapshot=snapshot))
        files.update(path for path in in_repo_support.glob("**/*.py") if path in tracked)
    return sorted(files)


_POINTER_STEMS = tuple(sorted({name.split(".", 1)[0] for name in CURRENT_POINTER_NAMES}))


def _could_write_current_pointer(text: str) -> bool:
    # Matches the STEM (`latest`), not only the full filename. Requiring
    # `latest.md`/`latest.json` verbatim meant a file that builds the name —
    # `f"latest.{ext}"` — never reached the AST scan at all, so the computed-name
    # detector below could not have fired even once (D9).
    return any(f"{stem}." in text for stem in _POINTER_STEMS) and any(
        token in text for token in WRITE_CALL_TOKENS
    )


def _string_constants(node: ast.AST) -> set[str]:
    return {item.value for item in ast.walk(node) if isinstance(item, ast.Constant) and isinstance(item.value, str)}


def _pointer_names_in(node: ast.AST) -> set[str]:
    return _string_constants(node) & CURRENT_POINTER_NAMES


def _assigned_pointer_names(tree: ast.AST, constants: dict[str, str]) -> dict[str, str]:
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        pointer_names = _pointer_names_in_resolved(node.value, constants, _scope_assigned_names(node))
        if not pointer_names:
            continue
        pointer_name = sorted(pointer_names)[0]
        for target in node.targets:
            if isinstance(target, ast.Name):
                names[target.id] = pointer_name
    return names


def _resolved_string_constants(tree: ast.AST) -> dict[str, str]:
    constants: dict[str, str] = {}
    body = tree.body if isinstance(tree, ast.Module) else []
    for node in body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            constants[target.id] = node.value.value
    return constants


def _attach_parent_links(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "_parent", parent)


def _scope_assigned_names(node: ast.AST) -> set[str]:
    scope = getattr(node, "_parent", None)
    while scope is not None and not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        scope = getattr(scope, "_parent", None)
    if scope is None:
        return set()
    names: set[str] = set()
    for child in ast.walk(scope):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _pointer_names_in_resolved(node: ast.AST, constants: dict[str, str], shadowed: set[str]) -> set[str]:
    names = _pointer_names_in(node)
    for child in ast.walk(node):
        if (
            isinstance(child, ast.Name)
            and child.id not in shadowed
            and constants.get(child.id) in CURRENT_POINTER_NAMES
        ):
            names.add(constants[child.id])
    return names


def _computed_pointer_name_in(node: ast.AST) -> str | None:
    """A pointer filename BUILT at runtime rather than written as a literal.

    ``_pointer_names_in`` matches string constants only, so ``f"latest.{ext}"``
    or ``"latest" + suffix`` produced a path this gate could not see and it
    reported clean over it (D9). Deliberately narrow — an f-string or
    concatenation whose literal head is a pointer stem — because the point is to
    refuse silence about a computed pointer name, not to chase every expression
    that could theoretically evaluate to one.
    """
    for child in ast.walk(node):
        parts: list[str] = []
        if isinstance(child, ast.JoinedStr):
            parts = [v.value for v in child.values if isinstance(v, ast.Constant) and isinstance(v.value, str)]
        elif isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add):
            # BOTH operands. Inspecting only `left` missed the shape that
            # actually occurs: Python parses `a + b + c` left-associatively, so
            # in `str(out) + "/latest." + ext` the pointer-ish literal is only
            # ever a RIGHT operand and was never looked at.
            parts = [
                side.value
                for side in (child.left, child.right)
                if isinstance(side, ast.Constant) and isinstance(side.value, str)
            ]
        for part in parts:
            head = part.split("/")[-1]
            if any(head == f"{stem}." or head.startswith(f"{stem}.") for stem in _POINTER_STEMS):
                return f"{head}<computed>"
            if head in _POINTER_STEMS:
                return f"{head}.<computed>"
    return None


def _write_target_node(call: ast.Call) -> ast.AST | None:
    """The expression a MUTATING write call targets, or ``None``.

    One dispatch for `Path.write_text` / `write_bytes`, `Path.open(mode=...)`
    and builtin `open(path, mode)`. The literal and computed resolvers below had
    grown a copy each, which is one place for the three call shapes to drift
    apart and two places to fix when a fourth appears.
    """
    func = call.func
    if isinstance(func, ast.Attribute) and func.attr in {"write_text", "write_bytes"}:
        return func.value
    if isinstance(func, ast.Attribute) and func.attr == "open":
        if _write_mode_is_mutating(call.args[0] if call.args else None, call.keywords):
            return func.value
        return None
    if isinstance(func, ast.Name) and func.id == "open" and call.args:
        if _write_mode_is_mutating(call.args[1] if len(call.args) > 1 else None, call.keywords):
            return call.args[0]
    return None


def _call_target_name(call: ast.Call, assigned: dict[str, str], constants: dict[str, str]) -> str | None:
    node = _write_target_node(call)
    if node is None:
        return None
    if isinstance(node, ast.Name) and node.id in assigned:
        return assigned[node.id]
    pointer_names = _pointer_names_in_resolved(node, constants, _scope_assigned_names(call))
    return sorted(pointer_names)[0] if pointer_names else None


def _assigned_computed_names(tree: ast.AST) -> dict[str, str]:
    """Locals bound to a COMPUTED pointer name, mirroring
    ``_assigned_pointer_names`` for the literal case.

    Without this the detector saw only the single-expression form. The
    two-statement form — ``target = out / f"latest.{ext}"`` then
    ``target.write_text(...)`` — is the idiom this repo actually writes, and the
    literal detector already handles its literal twin, so covering one and not
    the other left the dominant shape invisible.
    """
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        computed = _computed_pointer_name_in(node.value)
        if computed is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                names[target.id] = computed
    return names


def _write_mode_is_mutating(mode_node: ast.AST | None, keywords: list[ast.keyword]) -> bool:
    node = mode_node
    if node is None:
        node = next((kw.value for kw in keywords if kw.arg == "mode"), None)
    text = node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else "r"
    return any(flag in text for flag in ("w", "a", "+"))


def _computed_write_target(call: ast.Call, computed_assigned: dict[str, str]) -> str | None:
    """The computed-name counterpart of ``_call_target_name``: same write calls,
    same dispatch, but the filename is assembled rather than spelled out."""
    node = _write_target_node(call)
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return computed_assigned.get(node.id)
    return _computed_pointer_name_in(node)


def _display_path(repo_root: Path, path: Path) -> Path:
    """The path this gate REPORTS and matches ``HELPER_FILES`` against.

    A bare ``path.relative_to(repo_root)`` raises for any file outside the repo,
    and one is reachable: with ``CHARNESS_SUPPORT_DIR`` pointing at an external
    support tree, the population owner correctly returns absolute paths there.
    Three call sites did the bare conversion, so a split-layout host got an
    uncaught ``ValueError`` from a standing quality gate.

    A gate that CRASHES is not the failure this file exists to prevent, but it is
    still a gate that renders no verdict. Round-1 review found the crash, and
    found that the docstring shipped alongside it claimed the opposite.

    THREE outcomes, not two -- round-2 review noted the first draft described two
    and shipped a third:

    - under ``repo_root`` -> the repo-relative path;
    - under the external support root -> ``<external-support>/<rel>``. The prefix
      is not a spellable repo path ON PURPOSE: naming it ``skills/support/<rel>``
      collides with a real, different, in-repo file, so a reader following the
      clickable ``path:line`` would land on unrelated code;
    - under neither -> the absolute path. Unreachable from ``scan_repo`` (the
      owner returns only those two roots) but reachable via the public
      ``scan_path``, so it is a real branch rather than a dead one.

    Both sides are ``resolve()``d before comparison. ``support_dir`` resolves its
    override and this did not, so a repo or tmpdir reached through a symlink (the
    macOS ``/tmp -> /private/tmp`` case) fell to the absolute branch on one
    platform and not another.
    """
    resolved = path.resolve()
    root = repo_root.resolve()
    try:
        return resolved.relative_to(root)
    except ValueError:
        pass
    try:
        return Path(_EXTERNAL_SUPPORT_PREFIX) / resolved.relative_to(support_dir(repo_root))
    except ValueError:
        return resolved


def _scan_text(repo_root: Path, path: Path, text: str) -> list[Finding]:
    relative = _display_path(repo_root, path)
    if relative in HELPER_FILES:
        return []
    try:
        tree = ast.parse(text, filename=str(relative))
    except SyntaxError:
        return []
    _attach_parent_links(tree)
    constants = _resolved_string_constants(tree)
    assigned = _assigned_pointer_names(tree, constants)
    computed_assigned = _assigned_computed_names(tree)
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = _call_target_name(node, assigned, constants)
        reason = "direct write to current-pointer filename; use scripts.artifacts.current_pointer_writer_lib"
        if target is None:
            target = _computed_write_target(node, computed_assigned)
            if target is None:
                continue
            reason = (
                "write to a current-pointer filename BUILT at runtime; this gate cannot prove "
                "the target is not a current pointer -- use scripts.artifacts.current_pointer_writer_lib, "
                "or write the literal filename so the scope is establishable"
            )
        findings.append(
            Finding(
                path=relative.as_posix(),
                line=getattr(node, "lineno", 0),
                target=target,
                reason=reason,
            )
        )
    return findings


def scan_path(repo_root: Path, path: Path) -> list[Finding]:
    # No HELPER_FILES check here: `_scan_text` does the identical one. `scan_repo`
    # keeps its copy because there it avoids a file read; this one only avoided
    # re-deriving the display path, which is now one cheap owner. Round-2 review.
    return _scan_text(repo_root, path, path.read_text(encoding="utf-8"))


def scan_repo(repo_root: Path, *, require_git: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    for path in _git_visible_python_files(repo_root, require_git=require_git):
        relative = _display_path(repo_root, path)
        if relative in HELPER_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        if not _could_write_current_pointer(text):
            continue
        findings.extend(_scan_text(repo_root, path, text))
    return sorted(findings, key=lambda item: (item.path, item.line, item.target))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--require-empty", action="store_true")
    # The cohort convention (~18 standing gates pass this). Without it, a run in a
    # tree where `git ls-files` fails silently swaps a gitignore-aware population
    # for a plain glob and still prints "No direct current-pointer writes found."
    # -- the exact false green this gate exists to close. Round-1 review: the
    # slice ADDED the ability to refuse and did not exercise it.
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    findings = scan_repo(repo_root, require_git=args.require_git_file_listing)
    payload = {
        "status": "clean" if not findings else "findings",
        "finding_count": len(findings),
        "findings": [asdict(item) for item in findings],
    }
    emit_yaml(payload)
    return 1 if args.require_empty and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
