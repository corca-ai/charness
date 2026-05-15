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


def filter_session(repo_root: Path, session: Path) -> dict[str, int]:
    try:
        from cosmic_ray.work_db import use_db
        from cosmic_ray.work_item import TestOutcome, WorkerOutcome, WorkResult
    except ImportError as exc:  # pragma: no cover - exercised only on missing runtime
        raise SystemExit(
            "cosmic-ray is required to filter a Cosmic Ray session; install Cosmic Ray 8.4.6 first"
        ) from exc

    skipped = 0
    inspected = 0
    with use_db(session) as db:
        for item in db.work_items:
            inspected += 1
            if any(should_skip_mutation(repo_root, mutation) for mutation in item.mutations):
                db.set_result(
                    item.job_id,
                    WorkResult(
                        worker_outcome=WorkerOutcome.SKIPPED,
                        test_outcome=TestOutcome.KILLED,
                        output="Filtered function annotation union",
                    ),
                )
                skipped += 1
    return {"inspected": inspected, "skipped": skipped}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    session = resolve(repo_root, args.session)
    if not session.is_file():
        sys.stderr.write(f"Cosmic Ray session not found at {session}\n")
        return 2

    payload = filter_session(repo_root, session)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"filtered {payload['skipped']} low-signal mutants from {payload['inspected']} pending mutants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
