#!/usr/bin/env python3

"""Meta-gate (#368): the validator-timing classification table must stay EXHAUSTIVE.

Every gate `run-quality.sh` runs (each `queue_selected "<label>"`) must carry a
recorded timing verdict in `docs/conventions/validator-timing-layers.md`'s
classification table — either pulled to the commit boundary or an explicit
"stays" reason. This closes the recurring shift-left class structurally
(#314/#319/#332/#366/#368): each prior instance was a cheap, deterministic,
offline check that nobody had classified, so it sat broad-only until it bit
someone at the ~4-min gate. Hand-pulling one more validator per recurrence does
not stop the class; forcing every new run-quality entrant to declare its timing
verdict here does.

It is itself the cheap/deterministic/offline kind it enforces: it reads two
checked-in files and flips only when `run-quality.sh` or the timing doc changes.
It degrades (exit 0) when either file is absent (a consumer/tmp repo that does
not vendor the run-quality surface).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

RUN_QUALITY_PATH = Path("scripts/run-quality.sh")
TIMING_DOC_PATH = Path("docs/conventions/validator-timing-layers.md")
QUEUE_SELECTED_RE = re.compile(r'queue_selected\s+"([^"]+)"')
TABLE_HEADING = "## Classification table"


def run_quality_labels(text: str) -> list[str]:
    """The de-duplicated set of `queue_selected` labels, in first-seen order."""
    seen: dict[str, None] = {}
    for match in QUEUE_SELECTED_RE.finditer(text):
        seen.setdefault(match.group(1), None)
    return list(seen)


def classification_region(doc_text: str) -> str:
    """The classification-table section only, so a label must be recorded as a
    timing verdict — not merely mentioned in unrelated prose elsewhere."""
    start = doc_text.find(TABLE_HEADING)
    if start == -1:
        return ""
    rest = doc_text[start + len(TABLE_HEADING):]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


def unclassified_labels(repo_root: Path) -> tuple[list[str], list[str]]:
    """Return (missing, checked). `missing` is run-quality labels with no verdict
    recorded in the timing-doc classification table."""
    run_quality = repo_root / RUN_QUALITY_PATH
    timing_doc = repo_root / TIMING_DOC_PATH
    if not run_quality.is_file() or not timing_doc.is_file():
        return [], []
    labels = run_quality_labels(run_quality.read_text(encoding="utf-8"))
    region = classification_region(timing_doc.read_text(encoding="utf-8"))
    missing = [label for label in labels if label not in region]
    return missing, labels


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    missing, checked = unclassified_labels(repo_root)
    if not checked:
        print("timing-layer completeness: run-quality.sh or timing doc absent; no gate.")
        return 0
    if missing:
        print(
            f"{len(missing)} run-quality validator(s) have NO timing verdict in "
            f"`{TIMING_DOC_PATH}` classification table:",
            file=sys.stderr,
        )
        for label in missing:
            print(f"  - {label}", file=sys.stderr)
        print(
            "Record each in the classification table (pulled -> commit-time, or an "
            "explicit 'stays' reason) so the shift-left class cannot silently recur.",
            file=sys.stderr,
        )
        return 1
    print(f"timing-layer completeness: all {len(checked)} run-quality validators carry a timing verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
