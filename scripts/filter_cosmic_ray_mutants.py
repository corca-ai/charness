#!/usr/bin/env python3
"""Filter low-signal Cosmic Ray work items from a session database.

Cosmic Ray 8.4.6 sees the PEP 604 union operator in function annotations as a
binary ``|`` mutation point. With ``from __future__ import annotations`` those
mutants are behavior-equivalent for this repo and can dominate the score. This
filter marks those work items as skipped after ``cosmic-ray init`` and before
``cosmic-ray exec``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BITOR_OPERATOR_PREFIX = "core/ReplaceBinaryOperator_BitOr_"
ANNOTATION_UNION_SKIP_OUTPUT = "Filtered function annotation union"
UNCOVERED_MUTATION_SKIP_OUTPUT = "Filtered uncovered mutation line"


def resolve(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def source_line(repo_root: Path, module_path: Path, line_number: int) -> str:
    path = resolve(repo_root, module_path)
    try:
        return path.read_text(encoding="utf-8").splitlines()[line_number - 1]
    except (OSError, IndexError):
        return ""


def is_function_annotation_union(line: str, start_col: int) -> bool:
    stripped = line.lstrip()
    if not stripped.startswith("def "):
        return False
    prefix = line[:start_col]
    return "|" in line and ("->" in line or ":" in prefix)


def should_skip_mutation(repo_root: Path, mutation: object) -> bool:
    operator_name = getattr(mutation, "operator_name", "")
    if not operator_name.startswith(BITOR_OPERATOR_PREFIX):
        return False
    line_number, start_col = getattr(mutation, "start_pos", (0, 0))
    line = source_line(repo_root, getattr(mutation, "module_path", Path()), line_number)
    return is_function_annotation_union(line, start_col)


def load_coverage_lines(repo_root: Path, coverage_json: Path) -> dict[str, set[int]]:
    if not coverage_json.is_file():
        return {}
    data = json.loads(coverage_json.read_text(encoding="utf-8"))
    files = data.get("files") or {}
    covered: dict[str, set[int]] = {}
    for raw_path, payload in files.items():
        path = Path(raw_path)
        if path.is_absolute():
            try:
                rel = path.resolve().relative_to(repo_root).as_posix()
            except ValueError:
                continue
        else:
            rel = path.as_posix()
        covered[rel] = {int(line) for line in payload.get("executed_lines") or []}
    return covered


def coverage_skip_reason(mutation: object, covered_lines: dict[str, set[int]]) -> str | None:
    if not covered_lines:
        return None
    module_path = getattr(mutation, "module_path", Path()).as_posix()
    line_number, _start_col = getattr(mutation, "start_pos", (0, 0))
    if line_number not in covered_lines.get(module_path, set()):
        return UNCOVERED_MUTATION_SKIP_OUTPUT
    return None


def skip_reason(repo_root: Path, mutation: object, covered_lines: dict[str, set[int]]) -> str | None:
    if should_skip_mutation(repo_root, mutation):
        return ANNOTATION_UNION_SKIP_OUTPUT
    return coverage_skip_reason(mutation, covered_lines)


def filter_session(repo_root: Path, session: Path, coverage_json: Path | None = None) -> dict[str, int]:
    try:
        from cosmic_ray.work_db import use_db
        from cosmic_ray.work_item import TestOutcome, WorkerOutcome, WorkResult
    except ImportError as exc:  # pragma: no cover - exercised only on missing runtime
        raise SystemExit(
            "cosmic-ray is required to filter a Cosmic Ray session; install Cosmic Ray 8.4.6 first"
        ) from exc

    coverage_path = resolve(repo_root, coverage_json) if coverage_json else None
    covered_lines = load_coverage_lines(repo_root, coverage_path) if coverage_path else {}
    skipped = 0
    skipped_uncovered = 0
    skipped_annotation = 0
    inspected = 0
    with use_db(session) as db:
        for item in db.work_items:
            inspected += 1
            reasons = [
                reason
                for mutation in item.mutations
                if (reason := skip_reason(repo_root, mutation, covered_lines))
            ]
            if reasons:
                output = reasons[0]
                db.set_result(
                    item.job_id,
                    WorkResult(
                        worker_outcome=WorkerOutcome.SKIPPED,
                        test_outcome=TestOutcome.KILLED,
                        output=output,
                    ),
                )
                skipped += 1
                if output == UNCOVERED_MUTATION_SKIP_OUTPUT:
                    skipped_uncovered += 1
                elif output == ANNOTATION_UNION_SKIP_OUTPUT:
                    skipped_annotation += 1
    return {
        "inspected": inspected,
        "skipped": skipped,
        "skipped_uncovered": skipped_uncovered,
        "skipped_annotation": skipped_annotation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--coverage-json", type=Path, default=Path("reports/mutation/test-coverage.json"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    session = resolve(repo_root, args.session)
    if not session.is_file():
        sys.stderr.write(f"Cosmic Ray session not found at {session}\n")
        return 2

    coverage_json = resolve(repo_root, args.coverage_json)
    payload = filter_session(repo_root, session, coverage_json if coverage_json.is_file() else None)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"filtered {payload['skipped']} mutants from {payload['inspected']} pending mutants "
            f"({payload['skipped_annotation']} annotation unions, "
            f"{payload['skipped_uncovered']} uncovered lines)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
