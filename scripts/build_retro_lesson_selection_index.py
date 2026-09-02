#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_recent_lessons_module = import_repo_module(__file__, "scripts.recent_lessons_lib")
build_lesson_selection_index = _recent_lessons_module.build_lesson_selection_index
check_lesson_selection_index = _recent_lessons_module.check_lesson_selection_index
lesson_selection_index_path = _recent_lessons_module.lesson_selection_index_path
write_lesson_selection_index = _recent_lessons_module.write_lesson_selection_index
_lesson_ledger_module = import_repo_module(__file__, "scripts.lesson_ledger_lib")
validate_lesson_ledger = _lesson_ledger_module.validate_lesson_ledger


def _resolver_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "retro" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "retro" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("retro resolve_adapter.py not found")


def _load_yamlish_retro_paths(repo_root: Path) -> tuple[Path, Path | None]:
    adapter_path = repo_root / ".agents" / "retro-adapter.yaml"
    if not adapter_path.is_file():
        raise FileNotFoundError("retro resolve_adapter.py not found")
    data: dict[str, str] = {}
    for raw_line in adapter_path.read_text(encoding="utf-8").splitlines():
        if ":" not in raw_line or raw_line.startswith(" "):
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip()
    output_dir = data.get("output_dir") or "charness-artifacts/retro"
    summary_path = data.get("summary_path", "charness-artifacts/retro/recent-lessons.md")
    if summary_path == "null":
        summary_path = None
    if not output_dir:
        raise FileNotFoundError("retro adapter must define `output_dir` and `summary_path`")
    return repo_root / output_dir, None if summary_path is None else repo_root / summary_path


def _load_retro_paths(repo_root: Path) -> tuple[Path, Path | None]:
    try:
        resolver_path = _resolver_path(repo_root)
    except FileNotFoundError:
        return _load_yamlish_retro_paths(repo_root)
    module = load_path_module("retro_lesson_index_resolve_adapter", resolver_path)
    adapter = module.load_adapter(repo_root)
    data = adapter["data"]
    summary_rel = data.get("summary_path")
    return repo_root / data["output_dir"], repo_root / summary_rel if isinstance(
        summary_rel, str
    ) else None


def _relative(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir, summary_path = _load_retro_paths(repo_root)
    index_path = lesson_selection_index_path(output_dir)
    payload = build_lesson_selection_index(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )

    def _index_result(status: str) -> dict:
        """One shape for both verdicts of one command.

        `status` carries what the dropped "Wrote <path>." line said and the bare path
        does not: whether the index was REWRITTEN or only validated on this run. Both
        arms were copied from each other when the --check arm gained a payload in this
        slice, which is how the two verdicts of a single command become free to report
        different fields.
        """
        return {
            "status": status,
            "index_path": _relative(repo_root, index_path),
            "source_artifact_count": payload["source_artifact_count"],
            "candidate_count": payload["candidate_count"],
            # `summary_path: null` is a declared state, not a silent skip: the digest
            # comparison did not run because the adapter names no digest.
            "summary_projection": "not_configured" if summary_path is None else "compared",
        }

    if args.write:
        # Through the library writer, not a local `write_text`: that writer owns the
        # helper-provenance refusal, and hand-writing the same bytes here bypassed it
        # (verified: a drifted installed copy wrote the index anyway).
        write_lesson_selection_index(repo_root, output_dir, summary_path)
        emit_yaml(_index_result("written"))
        return 0
    if args.check:
        if summary_path is None:
            validate_lesson_ledger(
                repo_root=repo_root,
                output_dir=output_dir,
                summary_path=None,
            )
        check_lesson_selection_index(repo_root, output_dir, summary_path)
        emit_yaml(_index_result("validated"))
        return 0

    emit_yaml(payload)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
