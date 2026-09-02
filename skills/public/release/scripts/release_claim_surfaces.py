#!/usr/bin/env python3

"""The claim surfaces a release note is allowed to assert a quantity about.

The recorded failure this exists for. The prepared `6.0.0` notes said *"twelve
public skill scripts still declare one, and that is the convention"* over a tree
where the measured answer was ZERO. Those notes had already been repaired
by hand for four false claims one day earlier and went stale again within a day.
Hand-repair is the move that failed twice, so the quantities move out of the
author's memory and into a derivation over the tree.

What a surface IS: one question with a mechanical answer over the shipped tree,
a declared scan scope, and a declared blind spot. `derive_surfaces` answers all
of them; `release_notes_claims` renders and compares them.

The non-claim, stated here rather than implied. This proves *notes ==
derivation*. It never proves *derivation == truth* — a claim surface nobody
thought to register is invisible to every check built on this file, and adding
one is the only way it becomes visible. The registry is therefore written to be
appended to, and each surface carries its own `unscanned` list so a reader can
see the edge of what was measured instead of inferring a completeness nobody
established.
"""

from __future__ import annotations

import ast
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, NamedTuple


# fmt: off
def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))
# fmt: on


SKILL_RUNTIME = _load_skill_runtime_bootstrap()

_repo_file_listing = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.repo_file_listing"
)
git_list_repo_files = _repo_file_listing.git_list_repo_files
RepoFileSnapshot = _repo_file_listing.RepoFileSnapshot

#: Python sources this repo OWNS. `plugins/**` and `mutants/**` are absent by
#: construction rather than by exclusion: neither matches these globs. That is
#: deliberate — the exported mirror is a generated copy of the same sources, so
#: counting it would double every answer, and a reader seeing `24` where the
#: repo has 12 files would reasonably conclude the derivation is broken.
_PYTHON_SCAN_GLOBS = ("scripts/**/*.py", "skills/**/scripts/**/*.py")

#: The CLI entrypoint is a Python script with no `.py` suffix, so no glob above
#: reaches it. It is the single most script-against-able surface this repo
#: ships; omitting it would put the repo's most-consumed flag surface outside
#: every derivation here.
_CLI_ENTRYPOINT = "charness"

_PYTHON_UNSCANNED = (
    "the exported `plugins/charness/**` mirror and `mutants/**`, which are generated copies of these same sources",
    "flag names composed at runtime from a variable rather than written as a string literal",
    "flags a wrapper forwards without declaring, which no parser in this tree names",
)


class Surface(NamedTuple):
    """One derivable claim surface.

    `derive` returns `(items, extra_unscanned)`. The second element is not
    decoration: a file that fails to parse is a file this derivation did NOT
    read, and reporting its absence as a zero is the exact over-claim shape the
    whole mechanism exists to refuse. A surface that could not look says so.
    """

    id: str
    question: str
    scanned: tuple[str, ...]
    unscanned: tuple[str, ...]
    derive: Callable[..., tuple[list[str], list[str]]]


class TrackedReleaseTree(NamedTuple):
    repo_root: Path
    allowed: frozenset[Path] | None


def _tracked_release_tree(
    repo_root: Path,
    *,
    require_git: bool,
    snapshot: RepoFileSnapshot | None = None,
) -> TrackedReleaseTree:
    root = repo_root.resolve()
    listing = snapshot or RepoFileSnapshot(root, require_git=require_git)
    listed = listing.list_files(include_untracked=False)
    allowed = frozenset(path for path in listed if path.is_file()) if listed is not None else None
    return TrackedReleaseTree(root, allowed)


def _rel(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def _tracked(tree: TrackedReleaseTree, patterns: tuple[str, ...]) -> list[Path]:
    """Files matching ``patterns`` that are actually part of the release.

    `include_untracked=False` is the whole point and it is not the library
    default. A release ships COMMITTED content, so an untracked or gitignored
    file under `skills/public/` or `scripts/` is not in it. Counting them made
    the mechanism produce the fault it exists to refuse: a note synced in a
    worktree holding an untracked scratch skill asserted a skill the release does
    not contain, and the same worktree state made the publish gate refuse notes
    that were correct about the shipped tree.
    """
    matches: set[Path] = set()
    for pattern in patterns:
        for path in tree.repo_root.glob(pattern):
            if not path.is_file() or (tree.allowed is not None and path not in tree.allowed):
                continue
            matches.add(path)
    return sorted(matches)


def _python_sources(tree: TrackedReleaseTree) -> list[Path]:
    paths = _tracked(tree, _PYTHON_SCAN_GLOBS)
    paths.extend(_tracked(tree, (_CLI_ENTRYPOINT,)))
    return sorted(set(paths))


def _parsed(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return None


def _method_calls(tree: ast.Module, method: str):
    """Every `<anything>.method(...)` call in ``tree``.

    Both derivations below are the same walk over `ast.Call` with an
    `ast.Attribute` func, differing only in the method name and what they read
    off the matched node. Written twice, the second copy is where the `isinstance`
    chain gets one condition wrong and the surface silently measures zero.
    """
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == method
        ):
            yield node


def _declares_option(tree: ast.Module, option: str) -> bool:
    """Whether any `add_argument` in ``tree`` declares ``option`` exactly.

    EQUALITY against the option string, never a prefix or a substring. The
    measurement that refuted the prepared notes turned on exactly this: the
    remaining `--json` spellings in this tree are pass-through arguments to
    external CLIs (`gh`, package-manager audit commands), one `--json-path` in
    `proof_receipt.py`, and one suppressed `--json-out`. A prefix test reports those as `--json` declarations and
    reproduces the false claim from the other direction — a derivation agreeing
    with prose that is wrong.
    """
    return any(
        any(isinstance(arg, ast.Constant) and arg.value == option for arg in node.args)
        for node in _method_calls(tree, "add_argument")
    )


def _json_declaring_scripts(
    repo_root: Path, *, tracked_tree: TrackedReleaseTree
) -> tuple[list[str], list[str]]:
    hits: list[str] = []
    unreadable: list[str] = []
    for path in _python_sources(tracked_tree):
        tree = _parsed(path)
        if tree is None:
            unreadable.append(_rel(repo_root, path))
            continue
        if _declares_option(tree, "--json"):
            hits.append(_rel(repo_root, path))
    extra = (
        [
            f"{len(unreadable)} source(s) this derivation could not parse and therefore did not measure: {sorted(unreadable)}"
        ]
        if unreadable
        else []
    )
    return sorted(set(hits)), extra


def _charness_subcommands(
    repo_root: Path,
    *,
    tracked_tree: TrackedReleaseTree | None = None,
    require_git: bool = False,
) -> tuple[list[str], list[str]]:
    """Top-level `charness` subcommands, by AST over the entrypoint.

    Matched on the receiver NAME `subparsers`, which is what makes this the
    TOP-LEVEL set rather than every subcommand at every depth. `task_subparsers`,
    `catalog_subparsers`, and their siblings are nested groups; folding them in
    would produce a flat list that no invocation matches — `charness run` is
    not a command, `charness task run` is.
    """
    tree = tracked_tree or _tracked_release_tree(repo_root, require_git=require_git)
    tracked = _tracked(tree, (_CLI_ENTRYPOINT,))
    if not tracked:
        return [], [
            f"`{_CLI_ENTRYPOINT}` is not a tracked file in this tree, so no subcommand was derived"
        ]
    path = tracked[0]
    tree = _parsed(path)
    if tree is None:
        return [], [f"`{_CLI_ENTRYPOINT}` did not parse, so no subcommand was derived from it"]
    names: list[str] = []
    for node in _method_calls(tree, "add_parser"):
        receiver = node.func.value
        if not (isinstance(receiver, ast.Name) and receiver.id == "subparsers"):
            continue
        if (
            node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            names.append(node.args[0].value)
    return sorted(set(names)), []


def _public_skills(
    repo_root: Path, *, tracked_tree: TrackedReleaseTree
) -> tuple[list[str], list[str]]:
    manifests = _tracked(tracked_tree, ("skills/public/*/SKILL.md",))
    if not manifests:
        return [], [
            "no tracked `skills/public/*/SKILL.md` was found in this tree, so no public skill was derived"
        ]
    return sorted({path.parent.name for path in manifests}), []


def _repo_shell_gates(
    repo_root: Path, *, tracked_tree: TrackedReleaseTree
) -> tuple[list[str], list[str]]:
    return sorted({path.name for path in _tracked(tracked_tree, ("scripts/**/check-*.sh",))}), []


#: Append-only in spirit: removing a surface removes a check, and every id here
#: is quotable from a released note, so a rename is a break for anyone reading an
#: older note against a newer tree.
SURFACES: tuple[Surface, ...] = (
    Surface(
        id="json-declaring-scripts",
        question="which repo-owned Python sources declare their own `--json` option",
        scanned=(*_PYTHON_SCAN_GLOBS, _CLI_ENTRYPOINT),
        unscanned=_PYTHON_UNSCANNED,
        derive=_json_declaring_scripts,
    ),
    Surface(
        id="charness-subcommands",
        question="which top-level subcommands the `charness` CLI declares",
        scanned=(_CLI_ENTRYPOINT,),
        unscanned=(
            "nested subcommand groups such as `charness task run`, which are declared on their own subparser",
            "subcommands a host adapter adds outside this entrypoint",
        ),
        derive=_charness_subcommands,
    ),
    Surface(
        id="public-skills",
        question="which public skills this repo ships",
        scanned=("skills/public/*/SKILL.md",),
        unscanned=(
            "support, profile, and integration skills, which are not part of the public surface",
            "skills a consuming repo installs from elsewhere",
        ),
        derive=_public_skills,
    ),
    Surface(
        id="repo-shell-gates",
        question="which `check-*.sh` shell gates this repo ships",
        scanned=("scripts/**/check-*.sh",),
        unscanned=(
            "Python gates under `scripts/`, which are far more numerous and are not this surface",
            "gates a consuming repo wires from its own tree",
        ),
        derive=_repo_shell_gates,
    ),
)

SURFACE_IDS: tuple[str, ...] = tuple(surface.id for surface in SURFACES)


def derive_surface(
    surface: Surface,
    repo_root: Path,
    *,
    require_git: bool = False,
    tracked_tree: TrackedReleaseTree | None = None,
) -> dict[str, object]:
    tree = tracked_tree or _tracked_release_tree(repo_root, require_git=require_git)
    items, extra_unscanned = surface.derive(repo_root, tracked_tree=tree)
    return {
        "id": surface.id,
        "question": surface.question,
        "scanned": list(surface.scanned),
        "unscanned": [*surface.unscanned, *extra_unscanned],
        "count": len(items),
        "items": items,
    }


def derive_surfaces(
    repo_root: Path,
    *,
    require_git: bool = False,
    tracked_tree: TrackedReleaseTree | None = None,
) -> list[dict[str, object]]:
    """Every registered surface, measured against ``repo_root``, in registry order."""
    tree = tracked_tree or _tracked_release_tree(repo_root, require_git=require_git)
    return [
        derive_surface(
            surface,
            repo_root,
            require_git=require_git,
            tracked_tree=tree,
        )
        for surface in SURFACES
    ]


def surface_field(derived: dict[str, object], field: str) -> str | None:
    """The renderable value of ``field`` on a derived surface, or `None`.

    `None` means "this file does not know that field", which the caller must
    report as an unresolvable claim rather than as a mismatch. The two are
    different operator problems: a typo'd field name is a note nobody can
    validate, while a mismatch is a note the tree contradicts.
    """
    if field == "count":
        return str(derived["count"])
    if field == "items":
        items = derived["items"]
        assert isinstance(items, list)
        return ", ".join(items) if items else "(none)"
    return None


RENDERABLE_FIELDS: tuple[str, ...] = ("count", "items")
