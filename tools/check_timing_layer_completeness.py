#!/usr/bin/env python3

"""Meta-gate (#368): the validator-timing classification table must stay EXHAUSTIVE.

Every gate `run-quality.sh` runs (every declared row label, read by the shared
`quality_label_universe` reader) must
carry a recorded timing verdict in `docs/validator-timing-layers.md`'s
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
from scripts import quality_label_universe, render_validator_timing_layers

REPO_ROOT = repo_root_from_script(__file__)

RUN_QUALITY_PATH = Path("scripts/run-quality.sh")
TIMING_DOC_PATH = Path("docs/validator-timing-layers.md")
PRE_PUSH_PATH = Path(".githooks/pre-push")
DOCS_ONLY_RE = re.compile(r'^DOCS_ONLY_LABELS="([^"]*)"', re.MULTILINE)
TABLE_HEADING = "## Classification table"


def run_quality_labels(text: str, repo_root: Path | None = None) -> list[str]:
    """The de-duplicated set of queued gate labels, in first-seen order.

    Delegates to `quality_label_universe`, which reads every `queue_*` wrapper
    rather than `queue_selected` alone. This gate's own reader used to see only
    `queue_selected`, so three gates that reach the queue through `queue_timed`
    and `queue_agent_browser_runtime_gate` ran unclassified for as long as they
    have existed -- an exhaustiveness gate that was not exhaustive. One reader,
    because two regexes over the same bash file drift silently and the direction
    of the drift is always "the gate stops seeing something".

    Call-site labels only: the aggregate and startup-probe halves of the universe
    are not `run-quality.sh` gate entries and owe no timing verdict.
    """
    return list(quality_label_universe.queue_call_labels(text, repo_root=repo_root))


def classification_region(doc_text: str) -> str:
    """The classification-table section only, so a label must be recorded as a
    timing verdict — not merely mentioned in unrelated prose elsewhere."""
    start = doc_text.find(TABLE_HEADING)
    if start == -1:
        return ""
    rest = doc_text[start + len(TABLE_HEADING) :]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


# A classification row's FIRST cell is the label list; the remaining cells are the
# verdict and its prose reason. Only the first cell counts as "this label carries a
# recorded verdict".
_ROW_RE = re.compile(r"^\|([^|]*)\|")


def classified_labels(region: str) -> set[str]:
    """Labels recorded in the classification table's FIRST column.

    Substring containment over the whole region was the original test, and it made a
    label classified AT BIRTH if its name happened to appear in another row's prose:
    `check-links`, `check-doc`, and `validate-skill` all read as
    present that way, so adding `queue_selected "check-links"` would have been waved
    through and the shift-left recurrence class (#314/#319/#332/#366/#368) would pass
    silently. A `\b` word boundary does not fix it either -- `-` is a non-word
    character, so `\bcheck-links\b` still matches inside `check-links-internal`.
    Splitting the first cell on commas is the only reading that cannot alias.
    """
    labels: set[str] = set()
    for line in region.splitlines():
        match = _ROW_RE.match(line.strip())
        if match is None:
            continue
        for cell_entry in match.group(1).split(","):
            token = cell_entry.strip().strip("`*_ ")
            if token and token not in {"---", "Check (broad-gate label)"}:
                labels.add(token)
    return labels


def unclassified_labels(repo_root: Path) -> tuple[list[str], list[str]]:
    """Return (missing, checked). `missing` is run-quality labels with no verdict
    recorded in the timing-doc classification table."""
    run_quality = repo_root / RUN_QUALITY_PATH
    timing_doc = repo_root / TIMING_DOC_PATH
    labels = run_quality_labels(
        run_quality.read_text(encoding="utf-8") if run_quality.is_file() else "",
        repo_root,
    )
    if not timing_doc.is_file():
        return [], []
    region = classification_region(timing_doc.read_text(encoding="utf-8"))
    classified = classified_labels(region)
    missing = [label for label in labels if label not in classified]
    return missing, labels


def stale_docs_only_labels(repo_root: Path) -> list[str]:
    """Labels the docs-only pre-push subset names that `run-quality.sh` no longer has.

    Subset direction ONLY. This is not a late verdict, it is a verdict that never
    arrives: `label_is_selected` compares exact names, so a renamed or retired label
    leaves the hook naming something nothing matches, `queue_selected` quietly queues
    nothing, and the docs-only push -- the common path for an artifact
    commit -- reports a clean pass having run one fewer gate than it claims.

    The reverse direction (every run-quality label must appear in the docs-only set)
    is deliberately NOT checked: the subset is a curated judgment about what a pure
    docs change can break, and the timing doc records at least one intentional
    exclusion, so completeness here would be a false refusal.
    """
    run_quality = repo_root / RUN_QUALITY_PATH
    pre_push = repo_root / PRE_PUSH_PATH
    data_file = repo_root / quality_label_universe.QUALITY_GATES_PATH
    if data_file.is_file():
        # `docs_only` moved with the queue declaration. The old hook assignment
        # remains only as migration-era shell input and must not become a second
        # source of truth once the rows are present.
        quality_label_universe.quality_gate_rows(repo_root)
        return []
    if not run_quality.is_file() and not data_file.is_file():
        return []
    known = set(
        run_quality_labels(
            run_quality.read_text(encoding="utf-8") if run_quality.is_file() else "",
            repo_root,
        )
    )
    if not pre_push.is_file():
        return []
    match = DOCS_ONLY_RE.search(pre_push.read_text(encoding="utf-8"))
    if match is None:
        return []
    named = [item.strip() for item in match.group(1).split(",") if item.strip()]
    return [label for label in named if label not in known]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    # Both reads go through ONE guarded call. `stale_docs_only_labels` re-reads the
    # file `unclassified_labels` already parsed, so it cannot raise on its own today
    # -- but leaving a second call to a raising reader outside the guard is exactly
    # how the traceback comes back, and this gate is queued at COMMIT time.
    code, read = quality_label_universe.read_or_refuse(
        "timing-layer completeness",
        lambda: (unclassified_labels(repo_root), stale_docs_only_labels(repo_root)),
    )
    if read is None:
        return code
    (missing, checked), stale = read
    data_file = repo_root / quality_label_universe.QUALITY_GATES_PATH
    timing_doc = repo_root / TIMING_DOC_PATH
    if data_file.is_file() and timing_doc.is_file():
        expected = render_validator_timing_layers.rendered_classification_section(repo_root)
        current = timing_doc.read_text(encoding="utf-8")
        start = current.find(TABLE_HEADING)
        end = current.find("\n## Adding a new timing pull", start + len(TABLE_HEADING))
        actual = current[start:end] + "\n" if start >= 0 and end >= 0 else ""
        if actual != expected:
            print(
                "timing-layer completeness: classification table is stale; run "
                "`python3 scripts/render_validator_timing_layers.py --write`.",
                file=sys.stderr,
            )
            return 1
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

    if stale:
        print(
            f"{len(stale)} label(s) in `{PRE_PUSH_PATH}`'s DOCS_ONLY_LABELS name no "
            "run-quality gate, so the docs-only push silently runs fewer checks than "
            "it claims:",
            file=sys.stderr,
        )
        for label in stale:
            print(f"  - {label}", file=sys.stderr)
        print("Rename or drop each to match a queued gate label.", file=sys.stderr)
        return 1

    print(
        f"timing-layer completeness: all {len(checked)} run-quality validators carry a timing verdict."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
