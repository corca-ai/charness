#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


class ValidationError(Exception):
    pass


FRESHNESS_LABEL = "validate-current-pointer-freshness"
FRESHNESS_SCRIPT = Path("scripts/validate_current_pointer_freshness.py")
RUN_QUALITY_SCRIPT = Path("scripts/run-quality.sh")
CURRENT_POINTERS = (
    Path("docs/handoff.md"),
    Path("charness-artifacts/quality/latest.md"),
)
STALE_POINTER_PHRASES = {
    Path("docs/handoff.md"): (
        "freshness validator를 첫 slice로 잡는다",
        "freshness validator를 첫 slice",
    ),
    Path("charness-artifacts/quality/latest.md"): (
        "No deterministic freshness check yet",
        "add a narrow freshness check so rolling pointers",
    ),
}


def read_text(repo_root: Path, relative_path: Path) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise ValidationError(f"missing current pointer `{relative_path}`")
    return path.read_text(encoding="utf-8")


def validate_gate_is_queued(repo_root: Path) -> None:
    run_quality = read_text(repo_root, RUN_QUALITY_SCRIPT)
    expected_label = f'queue_selected "{FRESHNESS_LABEL}"'
    expected_script = str(FRESHNESS_SCRIPT)
    if expected_label not in run_quality or expected_script not in run_quality:
        raise ValidationError(
            "`scripts/run-quality.sh` must queue "
            f"`{FRESHNESS_LABEL}` via `{FRESHNESS_SCRIPT}`"
        )


def validate_no_stale_claims(repo_root: Path) -> None:
    stale_hits: list[str] = []
    for relative_path in CURRENT_POINTERS:
        text = read_text(repo_root, relative_path)
        for phrase in STALE_POINTER_PHRASES.get(relative_path, ()):
            if phrase in text:
                stale_hits.append(f"{relative_path}: stale phrase `{phrase}`")
    if stale_hits:
        raise ValidationError(
            "rolling current-pointer freshness claims are stale:\n"
            + "\n".join(f"- {hit}" for hit in stale_hits)
        )


def validate_current_pointer_freshness(repo_root: Path) -> None:
    validate_gate_is_queued(repo_root)
    validate_no_stale_claims(repo_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    validate_current_pointer_freshness(repo_root)
    print("Validated rolling current-pointer freshness claims.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
