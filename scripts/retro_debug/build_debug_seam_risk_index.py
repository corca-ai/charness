#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


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

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    load_path_module,
    repo_root_from_script,
    require_repo_local_helper,
)
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
INDEX_FILENAME = "seam-risk-index.json"

_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.gates_support.risk_interrupt_lib")
ValidationError = _scripts_risk_interrupt_lib_module.ValidationError
parse_debug_interrupt = _scripts_risk_interrupt_lib_module.parse_debug_interrupt


def _resolver_path(repo_root: Path) -> Path | None:
    candidates = (
        repo_root / "skills" / "public" / "debug" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "debug" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _load_debug_output_dir(repo_root: Path) -> Path:
    resolver_path = _resolver_path(repo_root)
    if resolver_path is not None:
        module = load_path_module("debug_seam_index_resolve_adapter", resolver_path)
        adapter = module.load_adapter(repo_root)
        data = adapter.get("data") if isinstance(adapter.get("data"), dict) else {}
    else:
        data = {}
        adapter_path = repo_root / ".agents" / "debug-adapter.yaml"
        if adapter_path.is_file():
            for raw_line in adapter_path.read_text(encoding="utf-8").splitlines():
                if raw_line.startswith("output_dir:"):
                    data["output_dir"] = raw_line.split(":", 1)[1].strip()
                    break
    output_dir = data.get("output_dir")
    if not isinstance(output_dir, str) or not output_dir:
        raise ValidationError("debug adapter must define `output_dir`")
    return repo_root / output_dir


def _increment(mapping: dict[str, int], value: str) -> None:
    mapping[value] = mapping.get(value, 0) + 1


def _relative(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root))


def _artifact_read_error(exc: OSError | UnicodeError) -> str:
    """Stable reason text; the outer diagnostic already carries the bound path."""
    if isinstance(exc, UnicodeError):
        return f"{type(exc).__name__}: artifact is not valid UTF-8"
    return f"{type(exc).__name__}: artifact metadata or content could not be read"


def _copied_pointer_target(identity_paths: list[Path]) -> Path | None:
    pointer = next((path for path in identity_paths if path.name == "latest.md"), None)
    if pointer is None or pointer.is_symlink():
        return None
    try:
        pointer_bytes = pointer.read_bytes()
    except OSError:
        return None

    matches: list[Path] = []
    for path in identity_paths:
        if path == pointer:
            continue
        try:
            equal = path.read_bytes() == pointer_bytes
        except OSError:
            equal = False
        if equal:
            matches.append(path)
    return max(matches, key=lambda path: path.name) if matches else None


def _discover_artifact_paths(
    repo_root: Path,
    output_dir: Path,
    invalid: list[tuple[str, str]],
) -> list[Path]:
    """Return one path per artifact identity, with the current-pointer role preserved."""
    by_identity: dict[tuple[int, int], Path] = {}
    for path in sorted(output_dir.glob("*.md")):
        if path.name == "seam-risk-index.md":
            continue
        try:
            stat = path.stat()
        except OSError as exc:
            invalid.append((_relative(repo_root, path), _artifact_read_error(exc)))
            continue
        key = (stat.st_dev, stat.st_ino)
        existing = by_identity.get(key)
        if existing is None or (existing.name != "latest.md" and path.name == "latest.md"):
            by_identity[key] = path

    identity_paths = sorted(by_identity.values())
    copied_target = _copied_pointer_target(identity_paths)
    return [path for path in identity_paths if path != copied_target]


def build_index(repo_root: Path) -> dict[str, Any]:
    output_dir = _load_debug_output_dir(repo_root)
    if not output_dir.is_dir():
        raise ValidationError(f"debug output directory does not exist: `{_relative(repo_root, output_dir)}`")

    entries: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    invalid: list[tuple[str, str]] = []
    risk_class_counts: dict[str, int] = {}
    generalization_pressure_counts: dict[str, int] = {}

    # Deduplicated by filesystem identity first, and the pointer's name wins. That covers
    # symlink and hard-link pointer layouts. A byte-copy pointer has a different inode, so
    # a second pass substitutes `latest.md` for the newest equal-content dated record.
    # Only the role-bearing pointer gets content dedupe: two dated records with equal bytes
    # are still two records, and collapsing them would invent identity from content alone.
    artifact_paths = _discover_artifact_paths(repo_root, output_dir, invalid)
    for artifact_path in artifact_paths:
        rel_path = _relative(repo_root, artifact_path)
        try:
            interrupt = parse_debug_interrupt(artifact_path)
        except ValidationError as exc:
            invalid.append((rel_path, str(exc)))
            continue
        except (OSError, UnicodeError) as exc:
            invalid.append((rel_path, _artifact_read_error(exc)))
            continue
        if not interrupt.get("present"):
            skipped.append(
                {
                    "artifact_path": rel_path,
                    "reason": str(interrupt.get("reason", "no seam risk section")),
                }
            )
            continue

        risk_classes = [str(value) for value in interrupt["risk_classes"]]
        generalization_pressure = str(interrupt["generalization_pressure"])
        for risk_class in risk_classes:
            _increment(risk_class_counts, risk_class)
        _increment(generalization_pressure_counts, generalization_pressure)

        entries.append(
            {
                "artifact_path": rel_path,
                "is_current_pointer": artifact_path.name == "latest.md",
                "interrupt_id": interrupt["interrupt_id"],
                "risk_classes": risk_classes,
                "seam": interrupt["seam"],
                "generalization_pressure": generalization_pressure,
                "critique_required": interrupt["critique_required"],
                "next_step": interrupt["next_step"],
                "handoff_artifact": interrupt["handoff_artifact"],
                "forced": interrupt["forced"],
            }
        )

    if invalid:
        details = "\n".join(f"- `{path}`: {reason}" for path, reason in invalid)
        raise ValidationError(
            f"{len(invalid)} invalid debug seam-risk artifact(s):\n{details}"
        )

    return {
        "schema_version": 1,
        "kind": "debug-seam-risk-index",
        "source": "charness-artifacts/debug/*.md ## Seam Risk",
        "score_policy": "none: source-linked index only; do not collapse incidents into a single score",
        "source_artifact_count": len(artifact_paths),
        "indexed_artifact_count": len(entries),
        "risk_class_counts": dict(sorted(risk_class_counts.items())),
        "generalization_pressure_counts": dict(sorted(generalization_pressure_counts.items())),
        "entries": entries,
        "skipped_artifacts": skipped,
    }


def _json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_index(repo_root: Path, payload: dict[str, Any]) -> Path:
    # Same write-boundary placement as the retro lesson index: a drifted copy of this
    # module run against the charness source tree writes a schema that tree's own gate
    # rejects, and re-running the same copy overwrites the fix.
    require_repo_local_helper(__file__, repo_root)
    output_dir = _load_debug_output_dir(repo_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / INDEX_FILENAME
    index_path.write_text(_json_text(payload), encoding="utf-8")
    return index_path


def check_index(repo_root: Path, payload: dict[str, Any]) -> None:
    index_path = _load_debug_output_dir(repo_root) / INDEX_FILENAME
    expected = _json_text(payload)
    if not index_path.is_file():
        raise ValidationError(
            f"missing debug seam-risk index `{_relative(repo_root, index_path)}`; "
            "run `python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write`"
        )
    actual = index_path.read_text(encoding="utf-8")
    if actual != expected:
        raise ValidationError(
            f"debug seam-risk index `{_relative(repo_root, index_path)}` is stale; "
            "run `python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write`"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    payload = build_index(repo_root)
    def _index_result(status: str, index_path: Path) -> dict[str, Any]:
        """One shape for both verdicts of one command.

        `status` carries what the dropped "Wrote <path>." line said and the bare path
        does not: whether the index was REWRITTEN or only validated on this run.
        Unlike its retro sibling this one takes the path, because the --check arm has
        no written path to reuse and resolves its own.
        """
        return {
            "status": status,
            "index_path": _relative(repo_root, index_path),
            "indexed_artifact_count": payload["indexed_artifact_count"],
            "source_artifact_count": payload["source_artifact_count"],
        }

    if args.write:
        emit_yaml(_index_result("written", write_index(repo_root, payload)))
        return 0
    if args.check:
        check_index(repo_root, payload)
        emit_yaml(
            _index_result("validated", _load_debug_output_dir(repo_root) / INDEX_FILENAME)
        )
        return 0
    emit_yaml(payload)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
