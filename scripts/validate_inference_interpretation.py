#!/usr/bin/env python3

"""Meta-validator for the advisory-interpretation contract (#330, sequel to #322).

Enumerates the inference-layer surfaces from
`.agents/inference-interpretation-surfaces.json` and asserts each one still emits
the 4-field `interpretation` self-declaration (measures / proxy_for / blind_spots
/ interpretation_question) with non-empty values AND carries a paired
consumer-must-answer line in its consuming reference.

It ALSO AST-scans every git-tracked `*.py` (outside the registry's exclude
prefixes) for a dict literal carrying all four fields and fails closed when one
is found that is not a registered surface: that is either a verified fact that
leaked a distrust declaration (the contract's cardinal error) or a new
inference-layer surface added without registering its consumer pairing.

It is a STRUCTURAL presence/pairing check, not a content classifier (#330
Non-Goal). It is file-granular: it cannot judge whether, inside a file that has
both an inference variant and a verified-fact variant (e.g. check_python_lengths'
warn band vs over-limit gate), the declaration rides only the inference path —
that intra-file boundary stays owned by the per-surface #322 tests and the
fresh-eye review. As a deterministic gate, its OWN output is a verified fact and
never carries the declaration.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
iter_repo_files = _repo_file_listing.iter_repo_files

DEFAULT_REGISTRY_PATH = Path(".agents/inference-interpretation-surfaces.json")
CONTRACT_FIELDS = ("measures", "proxy_for", "blind_spots", "interpretation_question")
VALID_KINDS = ("python", "prose")


class InterpretationContractError(Exception):
    """Raised when the registry itself is malformed (a load-time fault)."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InterpretationContractError(message)


def load_registry(path: Path) -> dict | None:
    """Load + structurally validate the registry. Returns None if absent."""
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InterpretationContractError(f"invalid JSON in `{path}`: {exc}") from exc
    _require(isinstance(raw, dict), "registry must be a JSON object")
    _require(raw.get("version") == 1, "registry `version` must be 1")
    _require(
        raw.get("declaration_fields") == list(CONTRACT_FIELDS),
        f"registry `declaration_fields` must be {list(CONTRACT_FIELDS)}",
    )
    leak = raw.get("leak_scan")
    _require(isinstance(leak, dict), "registry `leak_scan` must be an object")
    excludes = leak.get("exclude_prefixes")
    _require(
        isinstance(excludes, list) and all(isinstance(p, str) and p for p in excludes),
        "registry `leak_scan.exclude_prefixes` must be a list of non-empty strings",
    )
    surfaces = raw.get("surfaces")
    _require(isinstance(surfaces, list) and bool(surfaces), "registry `surfaces` must be a non-empty list")
    seen: set[str] = set()
    for index, surface in enumerate(surfaces):
        _validate_surface_shape(surface, index, seen)
    return raw


def _validate_surface_shape(surface: object, index: int, seen: set[str]) -> None:
    field = f"surfaces[{index}]"
    _require(isinstance(surface, dict), f"`{field}` must be an object")
    surface_id = surface.get("surface_id")
    _require(isinstance(surface_id, str) and bool(surface_id), f"`{field}.surface_id` must be a non-empty string")
    _require(surface_id not in seen, f"duplicate surface_id `{surface_id}`")
    seen.add(surface_id)
    kind = surface.get("kind")
    _require(kind in VALID_KINDS, f"`{field}.kind` must be one of {VALID_KINDS}")
    for key in ("declaration_file", "consumer_reference", "consumer_anchor"):
        _require(
            isinstance(surface.get(key), str) and bool(surface.get(key)),
            f"`{field}.{key}` must be a non-empty string",
        )
    if kind == "python":
        _require(
            isinstance(surface.get("declaration_symbol"), str) and bool(surface.get("declaration_symbol")),
            f"`{field}.declaration_symbol` must be a non-empty string for a python surface",
        )
    else:  # prose
        anchors = surface.get("prose_anchors")
        _require(
            isinstance(anchors, list) and bool(anchors) and all(isinstance(a, str) and a for a in anchors),
            f"`{field}.prose_anchors` must be a non-empty list of non-empty strings for a prose surface",
        )


def _field_values(dict_node: ast.Dict) -> dict[str, str | None]:
    values: dict[str, str | None] = {}
    for key_node, value_node in zip(dict_node.keys, dict_node.values):
        if isinstance(key_node, ast.Constant) and key_node.value in CONTRACT_FIELDS:
            try:
                evaluated = ast.literal_eval(value_node)
            except (ValueError, SyntaxError):
                evaluated = None
            values[key_node.value] = evaluated if isinstance(evaluated, str) else None
    return values


def _assigned_dict(node: ast.AST) -> tuple[list[str], ast.Dict] | None:
    """Return (target_names, dict_node) for a plain or annotated assignment whose
    value is a dict literal, else None. Covers both `X = {...}` and the equally
    idiomatic annotated `X: dict = {...}` form so an annotated declaration cannot
    slip past the leak scan."""
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
        return [t.id for t in node.targets if isinstance(t, ast.Name)], node.value
    if isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Dict):
        names = [node.target.id] if isinstance(node.target, ast.Name) else []
        return names, node.value
    return None


def find_declaration_dicts(source: str) -> list[tuple[str | None, dict[str, str | None]]]:
    """Return (symbol, field_values) for every dict LITERAL assigned to a name
    (plain `X = {...}` or annotated `X: dict = {...}`, at any statement depth) whose
    keys are a superset of CONTRACT_FIELDS.

    Scope boundary (honest non-claim): this targets the established declaration
    idiom — a dict literal bound to a name. Non-literal constructions (`dict(...)`
    calls, a dict built dynamically, or a literal nested as another dict's value)
    are out of structural scope and rely on registration discipline plus the
    per-surface #322 tests; the contract authors declarations as literals."""
    tree = ast.parse(source)
    found: list[tuple[str | None, dict[str, str | None]]] = []
    for node in ast.walk(tree):
        assigned = _assigned_dict(node)
        if assigned is None:
            continue
        names, dict_node = assigned
        keys = {k.value for k in dict_node.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        if not set(CONTRACT_FIELDS) <= keys:
            continue
        found.append((names[0] if names else None, _field_values(dict_node)))
    return found


def scan_repo_declarations(
    repo_root: Path, exclude_prefixes: list[str], *, require_git: bool
) -> dict[str, list[tuple[str | None, dict[str, str | None]]]]:
    """rel_path -> declaration dicts found in it, across git-visible *.py files."""
    found: dict[str, list[tuple[str | None, dict[str, str | None]]]] = {}
    for path in iter_repo_files(repo_root, require_git=require_git):
        rel = path.relative_to(repo_root).as_posix()
        if not rel.endswith(".py") or any(rel.startswith(prefix) for prefix in exclude_prefixes):
            continue
        try:
            declarations = find_declaration_dicts(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        if declarations:
            found[rel] = declarations
    return found


def _check_consumer(repo_root: Path, surface: dict) -> list[str]:
    ref = surface["consumer_reference"]
    ref_path = repo_root / ref
    if not ref_path.exists():
        return [f"{surface['surface_id']}: consumer_reference `{ref}` not found"]
    text = ref_path.read_text(encoding="utf-8")
    if surface["consumer_anchor"] not in text:
        return [
            f"{surface['surface_id']}: paired consumer-must-answer line missing — "
            f"anchor `{surface['consumer_anchor']}` not found in `{ref}`"
        ]
    return []


def _check_python_surface(
    repo_root: Path,
    surface: dict,
    found: dict[str, list[tuple[str | None, dict[str, str | None]]]],
) -> list[str]:
    errors: list[str] = []
    rel = surface["declaration_file"]
    abs_path = repo_root / rel
    if not abs_path.exists():
        return [f"{surface['surface_id']}: declaration_file `{rel}` not found"]
    declarations = found.get(rel)
    if declarations is None:
        try:
            declarations = find_declaration_dicts(abs_path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            declarations = []
    symbol = surface["declaration_symbol"]
    match = next((values for name, values in declarations if name == symbol), None)
    if match is None:
        return [
            f"{surface['surface_id']}: declaration_symbol `{symbol}` is no longer a 4-field "
            f"interpretation dict in `{rel}` (drift / removal / renamed half-contract)"
        ]
    for contract_field in CONTRACT_FIELDS:
        value = match.get(contract_field)
        if not (isinstance(value, str) and value.strip()):
            errors.append(
                f"{surface['surface_id']}: declaration field `{contract_field}` must be a "
                f"non-empty static string in `{rel}`"
            )
    errors.extend(_check_consumer(repo_root, surface))
    return errors


def _check_prose_surface(repo_root: Path, surface: dict) -> list[str]:
    errors: list[str] = []
    rel = surface["declaration_file"]
    abs_path = repo_root / rel
    if not abs_path.exists():
        return [f"{surface['surface_id']}: declaration_file `{rel}` not found"]
    text = abs_path.read_text(encoding="utf-8")
    for anchor in surface["prose_anchors"]:
        if anchor not in text:
            errors.append(
                f"{surface['surface_id']}: prose declaration anchor `{anchor}` missing from `{rel}`"
            )
    errors.extend(_check_consumer(repo_root, surface))
    return errors


def evaluate(repo_root: Path, registry: dict | None, registry_path: Path, *, require_git: bool) -> tuple[int, list[str]]:
    exclude_prefixes = registry["leak_scan"]["exclude_prefixes"] if registry else ["plugins/", "mutants/", "tests/"]
    found = scan_repo_declarations(repo_root, exclude_prefixes, require_git=require_git)

    if registry is None:
        if found:
            return 1, [
                f"{len(found)} interpretation declaration(s) found but no registry at "
                f"`{registry_path}`: {sorted(found)}"
            ]
        return 0, []

    surfaces = registry["surfaces"]
    python_surfaces = [s for s in surfaces if s["kind"] == "python"]
    prose_surfaces = [s for s in surfaces if s["kind"] == "prose"]
    registered_files = {s["declaration_file"] for s in python_surfaces}

    errors: list[str] = []
    for rel in sorted(found):
        if rel not in registered_files:
            errors.append(
                f"LEAK: `{rel}` defines a 4-field interpretation declaration but is not a "
                f"registered inference-layer surface. A verified fact must never carry the "
                f"declaration (cardinal error); a new inference surface must be registered in "
                f"`{registry_path}` with its paired consumer line."
            )
    for surface in python_surfaces:
        errors.extend(_check_python_surface(repo_root, surface, found))
    for surface in prose_surfaces:
        errors.extend(_check_prose_surface(repo_root, surface))

    if errors:
        return 1, errors
    return 0, [
        f"Validated advisory-interpretation contract across {len(surfaces)} inference-layer "
        f"surface(s) ({len(python_surfaces)} python, {len(prose_surfaces)} prose); "
        f"{len(found)} declaration(s) scanned, all registered and consumer-paired."
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--registry-path", type=Path, default=None)
    parser.add_argument(
        "--require-git-file-listing",
        action="store_true",
        help="Fail instead of falling back to a filesystem walk when git file listing is unavailable.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    registry_path = (args.registry_path or (repo_root / DEFAULT_REGISTRY_PATH)).resolve()

    try:
        registry = load_registry(registry_path)
    except InterpretationContractError as exc:
        print(f"{registry_path}: {exc}", file=sys.stderr)
        return 1

    code, messages = evaluate(
        repo_root, registry, registry_path, require_git=args.require_git_file_listing
    )
    stream = sys.stdout if code == 0 else sys.stderr
    for message in messages:
        print(message, file=stream)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
