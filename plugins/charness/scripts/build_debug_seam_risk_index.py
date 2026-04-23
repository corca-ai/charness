#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
INDEX_FILENAME = "seam-risk-index.json"

_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.risk_interrupt_lib")
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


def build_index(repo_root: Path) -> dict[str, Any]:
    output_dir = _load_debug_output_dir(repo_root)
    if not output_dir.is_dir():
        raise ValidationError(f"debug output directory does not exist: `{_relative(repo_root, output_dir)}`")

    entries: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    risk_class_counts: dict[str, int] = {}
    generalization_pressure_counts: dict[str, int] = {}

    artifact_paths = sorted(
        path for path in output_dir.glob("*.md") if path.name != "seam-risk-index.md"
    )
    for artifact_path in artifact_paths:
        interrupt = parse_debug_interrupt(artifact_path)
        rel_path = _relative(repo_root, artifact_path)
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
                "premortem_required": interrupt["premortem_required"],
                "next_step": interrupt["next_step"],
                "handoff_artifact": interrupt["handoff_artifact"],
                "forced": interrupt["forced"],
            }
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
            "run `python3 scripts/build_debug_seam_risk_index.py --repo-root . --write`"
        )
    actual = index_path.read_text(encoding="utf-8")
    if actual != expected:
        raise ValidationError(
            f"debug seam-risk index `{_relative(repo_root, index_path)}` is stale; "
            "run `python3 scripts/build_debug_seam_risk_index.py --repo-root . --write`"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    payload = build_index(repo_root)
    if args.write:
        index_path = write_index(repo_root, payload)
        result: dict[str, Any] = {
            "index_path": _relative(repo_root, index_path),
            "indexed_artifact_count": payload["indexed_artifact_count"],
            "source_artifact_count": payload["source_artifact_count"],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"Wrote {result['index_path']}.")
        return 0
    if args.check:
        check_index(repo_root, payload)
        print("Validated debug seam-risk index.")
        return 0
    print(_json_text(payload), end="")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
