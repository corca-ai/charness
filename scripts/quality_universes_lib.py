"""Shared adapter-owned scan universes for quality gates.

The defaults in this module are copied from the gate literals they replace. A
consumer can declare one file family in its quality adapter; an omitted family
continues to use the corresponding default, while an explicit empty list is a
real (and refusing) empty universe.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

try:
    from scripts.subprocess_guard import run_process
except ModuleNotFoundError:  # loaded as a standalone sibling module
    from subprocess_guard import run_process

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:  # loaded as a standalone sibling module
    from yaml_output import emit_yaml

UniverseSource = Literal["adapter", "default", "deliberately-absent"]


@dataclass(frozen=True)
class Universe:
    """One resolved file-family scope and the provenance of its pattern set."""

    patterns: tuple[str, ...]
    declared: bool
    source: UniverseSource


DEFAULT_ARTIFACT_ROOTS = {
    "spec": "charness-artifacts/spec",
    "quality": "charness-artifacts/quality",
    "release": "charness-artifacts/release",
    "dogfood": "charness-artifacts/dogfood",
    "debug": "charness-artifacts/debug",
    "premortem": "charness-artifacts/premortem",
    "design-studies": "charness-artifacts/design-studies",
    "goals": "charness-artifacts/goals",
    "critique": "charness-artifacts/critique",
    "ideation": "charness-artifacts/ideation",
    "retro": "charness-artifacts/retro",
    "probe": "charness-artifacts/probe",
    "issues": "charness-artifacts/issues",
    "release-review": "charness-artifacts/release-review",
}

_SHELL_COMMAND_PREFIX = (
    r"(?m)(?:^|(?:&&|\|\||[;|])\s*)\s*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=(?:\"[^\"]*\"|'[^']*'|\S+)\s+)*"
)


# These are the literal families named by the #769 lane brief. Keep this table
# here, rather than in quality_adapter_lib.py, so every future consumer imports
# the same defaults and that resolver remains under its root line cap.
DEFAULT_UNIVERSES = {
    "pytest_targets": [
        "tests/quality_gates",
        "tests/control_plane",
        "tests/test_*.py",
        "tests/charness_cli",
        "tests/coverage_debt",
    ],
    "python_sources": [
        "scripts/*.py",
        "scripts/**/*.py",
        "tools/*.py",
        "tools/**/*.py",
        "skills/public/*/scripts/*.py",
        "skills/public/*/scripts/**/*.py",
        "skills/support/*/scripts/*.py",
        "skills/support/*/scripts/**/*.py",
        "skills/shared/scripts/*.py",
        "skills/shared/scripts/**/*.py",
        "skills/support/*/vendor/*.py",
    ],
    "shell_sources": ["*.sh", "scripts/*.sh", "tools/*.sh", "tests/**/*.sh", ".githooks/*"],
    "test_roots": ["tests"],
    "doc_surfaces": [
        "README.md",
        "AGENTS.md",
        "docs/**/*.md",
        "presets/**/*.md",
        "profiles/**/*.md",
        "skills/public/**/*.md",
        "skills/support/**/*.md",
        "skills/shared/**/*.md",
    ],
    "artifact_roots": DEFAULT_ARTIFACT_ROOTS,
    "scanner_globs": [
        "skills/public/quality/scripts/*.py",
        "skills/public/quality/scripts/**/*.py",
        "skills/public/quality/references/*.py",
        "skills/public/quality/references/**/*.py",
        "scripts/*inventory*.py",
        "scripts/**/*inventory*.py",
        "scripts/*quality*.py",
        "scripts/**/*quality*.py",
        "scripts/*scan*.py",
        "scripts/**/*scan*.py",
        "tools/*inventory*.py",
        "tools/**/*inventory*.py",
        "tools/*quality*.py",
        "tools/**/*quality*.py",
        "tools/*scan*.py",
        "tools/**/*scan*.py",
    ],
    "ci_gate_patterns": [
        r"\bnpm\s+run\s+verify\b",
        r"\bnpm\s+run\s+lint\s*&&\s*npm\s+run\s+test\b",
        r"\bmake\s+verify\b",
        _SHELL_COMMAND_PREFIX + r"bash\s+(?:\./)?scripts/run-quality\.sh(?=$|\s|[;&|])",
        _SHELL_COMMAND_PREFIX + r"\./scripts/run-quality\.sh(?=$|\s|[;&|])",
        r"\bbash\s+scripts/run-verify\.(?:mjs|sh)\b",
        r"\bnode\s+scripts/run-verify\.mjs\b",
    ],
    "mutation_pool": [
        "charness",
        "runtime_bootstrap.py",
        "skill_runtime_bootstrap.py",
        "scripts/*.py",
        "scripts/**/*.py",
        "tools/*.py",
        "tools/**/*.py",
        "skills/public/*/scripts/*.py",
        "skills/public/*/scripts/**/*.py",
        "skills/support/*/scripts/*.py",
        "skills/support/*/scripts/**/*.py",
    ],
    "specdown_config": "specdown.json",
    "secrets_config": ".gitleaks.toml",
}

UNIVERSE_KEYS = frozenset(DEFAULT_UNIVERSES)


def validate_universes(value: Any, errors: list[str]) -> dict[str, Any] | None:
    """Validate the adapter block while keeping the schema beside its defaults."""
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("universes must be a mapping")
        return {}
    validated: dict[str, Any] = {}
    for key, raw in value.items():
        if key not in UNIVERSE_KEYS:
            errors.append(f"universes.{key} is not a recognized universe")
            continue
        if key == "artifact_roots":
            if not isinstance(raw, dict):
                errors.append("universes.artifact_roots must be a mapping")
                continue
            roots: dict[str, str] = {}
            for family, path in raw.items():
                if family not in DEFAULT_ARTIFACT_ROOTS:
                    errors.append(f"universes.artifact_roots.{family} is not a recognized family")
                elif not isinstance(path, str) or not path:
                    errors.append(f"universes.artifact_roots.{family} must be a non-empty string")
                else:
                    roots[family] = path
            validated[key] = roots
        elif key.endswith("_config"):
            if not isinstance(raw, str) or not raw:
                errors.append(f"universes.{key} must be a non-empty string")
            else:
                validated[key] = raw
        elif not isinstance(raw, list) or not all(isinstance(item, str) and item for item in raw):
            errors.append(f"universes.{key} must be a list of non-empty strings")
        else:
            validated[key] = list(raw)
    return validated


def _as_patterns(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise TypeError("a universe default must be a string or a sequence of strings")


def _adapter_body(adapter_payload: Any) -> tuple[dict[str, Any], bool]:
    if not isinstance(adapter_payload, dict):
        return {}, False
    body = adapter_payload.get("data")
    if isinstance(body, dict):
        return body, adapter_payload.get("found", True) is True
    return adapter_payload, True


def _lookup(mapping: Any, key: str) -> tuple[bool, Any]:
    current = mapping
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _is_deliberately_absent(body: dict[str, Any], key: str) -> bool:
    declared = body.get("deliberately_absent")
    if not isinstance(declared, dict):
        return False
    return any(
        candidate in declared
        for candidate in ("universes", f"universes.{key}", f"universes.{key.split('.', 1)[0]}")
    )


def resolve_universe(adapter_payload: Any, key: str, *, default: Any) -> Universe:
    """Resolve ``key`` from a quality adapter payload.

    ``artifact_roots`` families are addressed as ``artifact_roots.spec`` (and
    similarly for the other family names). The loader supplies
    ``_universes_declared`` so inferred defaults do not masquerade as adapter
    declarations; raw adapter mappings remain accepted for small consumers and
    tests.
    """
    body, adapter_found = _adapter_body(adapter_payload)
    fallback = _as_patterns(default.patterns if isinstance(default, Universe) else default)
    if _is_deliberately_absent(body, key):
        return Universe(fallback, False, "deliberately-absent")

    sentinel = object()
    declared_block = (
        adapter_payload.get("_universes_declared", sentinel)
        if isinstance(adapter_payload, dict)
        else sentinel
    )
    if declared_block is sentinel:
        declared_block = body.get("universes") if adapter_found else None
    declared, value = _lookup(declared_block, key)
    if not adapter_found or not declared:
        return Universe(fallback, False, "default")
    return Universe(_as_patterns(value), True, "adapter")


def _raw_glob(repo_root: Path, patterns: tuple[str, ...]) -> list[Path]:
    """Fallback used only when `git ls-files --cached --others --exclude-standard`
    is unavailable (no git binary or not a repository); `matching_files` prefers
    the gitignore-aware listing and intersects with these patterns otherwise."""
    matches: set[Path] = set()
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if path.is_dir():
                matches.update(child for child in path.rglob("*") if child.is_file())
            elif path.is_file():
                matches.add(path)
    return sorted(matches)


def _git_listing(repo_root: Path) -> set[Path] | None:
    try:
        result = run_process(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=repo_root,
            timeout_seconds=None,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return {repo_root / relative for relative in result.stdout.split("\0") if relative}


def matching_files(
    repo_root: Path,
    universe: Universe,
    *,
    git_listing: bool = True,
    require_git: bool = False,
) -> list[Path]:
    """Return files matching a universe, filtering Git-ignored files when possible."""
    root = repo_root.resolve()
    raw_matches = _raw_glob(root, universe.patterns)
    if not git_listing:
        return raw_matches
    allowed = _git_listing(root)
    if allowed is None:
        if require_git:
            raise RuntimeError(
                "repo file listing failed\n"
                "command: git ls-files -z --cached --others --exclude-standard\n"
                "exit_code: 128"
            )
        return raw_matches
    return sorted(path for path in raw_matches if path in allowed)


def refuse_if_declared_and_empty(
    universe: Universe, files: list[Path], gate_label: str
) -> str | None:
    if universe.declared and not files:
        patterns = ", ".join(universe.patterns) or "<empty>"
        return f"{gate_label}: refusing empty declared universe (patterns: {patterns})."
    return None


def _cli_payload(repo_root: Path) -> dict[str, Any]:
    carrier_root = Path(__file__).resolve().parent.parent
    if str(carrier_root) not in sys.path:
        sys.path.insert(0, str(carrier_root))
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from scripts.quality_adapter_lib import load_quality_adapter
    except ModuleNotFoundError:
        # The resolver is also a standalone CLI in source and collapsed plugin
        # exports, where the sibling scripts directory—not the consumer root—is
        # the import carrier.
        from quality_adapter_lib import load_quality_adapter

    adapter = load_quality_adapter(repo_root)
    resolved: dict[str, Any] = {}
    for key, default in DEFAULT_UNIVERSES.items():
        if key == "artifact_roots":
            resolved[key] = {
                family: resolve_universe(adapter, f"artifact_roots.{family}", default=path).__dict__
                for family, path in default.items()
            }
        else:
            resolved[key] = resolve_universe(adapter, key, default=default).__dict__
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve quality adapter scan universes.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--key", help="Resolve one universe key to matching repository files.")
    parser.add_argument(
        "--format",
        choices=("yaml", "lines"),
        default="yaml",
        help="Output the resolved universe payload as YAML or its matching paths, one per line.",
    )
    parser.add_argument(
        "--gate-label",
        help="Operator-facing gate label for empty-universe diagnostics (defaults to the key).",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    if args.format == "yaml":
        emit_yaml(_cli_payload(repo_root))
        return 0
    if not args.key:
        parser.error("--key is required with --format lines")
    if args.key == "artifact_roots":
        parser.error(
            "--format lines requires an artifact_roots family, such as artifact_roots.spec"
        )
    default = DEFAULT_UNIVERSES.get(args.key)
    if default is None:
        if args.key.startswith("artifact_roots."):
            family = args.key.split(".", 1)[1]
            default = DEFAULT_ARTIFACT_ROOTS.get(family)
        if default is None:
            parser.error(f"unknown universe key: {args.key}")
    carrier_root = Path(__file__).resolve().parent.parent
    if str(carrier_root) not in sys.path:
        sys.path.insert(0, str(carrier_root))
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from scripts.quality_adapter_lib import load_quality_adapter
    except ModuleNotFoundError:
        # The resolver is also a standalone CLI in source and collapsed plugin
        # exports, where the sibling scripts directory is the import carrier.
        from quality_adapter_lib import load_quality_adapter

    adapter = load_quality_adapter(repo_root)
    if adapter.get("valid") is False:
        errors = "; ".join(str(error) for error in adapter.get("errors", []))
        print(
            f"{args.key}: quality adapter is invalid{f': {errors}' if errors else '.'}",
            file=sys.stderr,
        )
        return 1
    resolved = resolve_universe(
        adapter,
        args.key,
        default=default,
    )
    files = matching_files(repo_root, resolved)
    label = args.gate_label or args.key
    refusal = refuse_if_declared_and_empty(resolved, files, label)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        return 1
    if not files and not resolved.declared:
        patterns = ", ".join(resolved.patterns) or "<empty>"
        print(
            f"{label}: discovered empty {args.key} universe (patterns: {patterns}).",
            file=sys.stderr,
        )
    for path in files:
        print(path.relative_to(repo_root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
