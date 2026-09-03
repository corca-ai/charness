#!/usr/bin/env python3
"""Refuse a `docs/` page over its word budget, and let the recorded ones only shrink.

A docs page grows only by displacing something. The operator's rule on
2026-09-03 came from one page: `docs/development.md` was 415 words at v8.0.0
and 1,929 words one day later, after a run of lesson graduations and the #775
prose each landed as a new paragraph on the page that already answered the
nearest question. Nothing refused it, because every gate on `docs/` reads
links, headings, and flags, and none of them reads size. A page that long is
no longer one owning question; it is a second operating manual that the next
reader skims, and the sentence they needed is the one they skipped.

The rule: every tracked Markdown page under `docs/` has a word count, measured
as whitespace-split tokens after fenced code blocks are stripped (a command
block is quoted evidence, not prose the reader has to hold). A page over
`WORD_BUDGET` (1000) is red unless the record names it; the record,
`charness-artifacts/quality/docs-length-baseline.json`, maps page path to its
recorded count and has the wall-clock record's semantics: a page above its
recorded count is red, a page below its count is a prompt to lower the record,
a recorded page now under budget is a prompt to drop it, and `--write-baseline`
refuses to raise any count. The move when red is one of three: split the page
along one owning question, move dated evidence to `charness-artifacts/`, or
fold prose into a table.

What this rule is deliberately blind to, stated so nobody reads a green as
"the docs are short": `README.md`, `AGENTS.md`, and every page under `skills/`
are outside the universe, so prose can grow there unmeasured; a page can hide
words in a linked page, and the budget is per page, not per reader path; a
table row counts the same as a sentence, so folding prose into a table lowers
the count only when it also deletes words; words inside fenced code are not
counted, so a page can carry an unbounded transcript as long as it is fenced.
An empty matched universe is a refusal (S40), never a pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_repo_file_listing_module = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _repo_file_listing_module.iter_matching_repo_files

DEFAULT_SCAN_GLOBS = ("docs/*.md", "docs/**/*.md")
DEFAULT_BASELINE_REL = "charness-artifacts/quality/docs-length-baseline.json"
BASELINE_SCHEMA = "charness.docs-length-baseline/v1"
WORD_BUDGET = 1000
FENCE_MARKERS = ("```", "~~~")
MOVE = (
    "split the page along one owning question, move dated evidence to "
    "charness-artifacts/, or fold prose into a table"
)


def word_count(text: str) -> int:
    """Whitespace-split tokens of one page with every fenced code block removed.

    A fence opens on a line whose stripped form starts with ``` or ~~~ and
    closes on the next line starting with the same marker; the fence lines and
    everything between them are not words. An unclosed fence runs to the end.
    """
    words = 0
    open_marker: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if open_marker is None:
            marker = next((m for m in FENCE_MARKERS if stripped.startswith(m)), None)
            if marker is not None:
                open_marker = marker
                continue
            words += len(stripped.split())
        elif stripped.startswith(open_marker):
            open_marker = None
    return words


def measure(repo_root: Path, *, require_git: bool) -> dict[str, int]:
    """Word count per tracked `docs/` page, keyed by repo-relative path."""
    paths = iter_matching_repo_files(repo_root, DEFAULT_SCAN_GLOBS, require_git=require_git)
    return {
        path.relative_to(repo_root).as_posix(): word_count(path.read_text(encoding="utf-8"))
        for path in paths
    }


def load_baseline(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != BASELINE_SCHEMA:
        raise SystemExit(f"{path}: not a {BASELINE_SCHEMA} record")
    pages = payload.get("pages")
    if not isinstance(pages, dict) or not all(
        isinstance(k, str) and isinstance(v, int) and v > 0 for k, v in pages.items()
    ):
        raise SystemExit(f"{path}: `pages` must map docs paths to positive word counts")
    return dict(pages)


def judge(counts: dict[str, int], baseline: dict[str, int]) -> tuple[list[str], list[str]]:
    """`(failures, shrink_prompts)` for the measured tree against the record."""
    failures: list[str] = []
    prompts: list[str] = []
    for relative, words in sorted(counts.items()):
        allowed = baseline.get(relative)
        if allowed is None:
            if words > WORD_BUDGET:
                failures.append(
                    f"{relative}: {words} words, budget {WORD_BUDGET} and not in the record; "
                    f"a docs page grows only by displacing something -- {MOVE}"
                )
        elif words > allowed:
            failures.append(
                f"{relative}: {words} words, recorded {allowed}; "
                f"a docs page grows only by displacing something -- {MOVE}"
            )
        elif words <= WORD_BUDGET:
            prompts.append(
                f"{relative}: {words} words is under budget {WORD_BUDGET}; drop it from the record"
            )
        elif words < allowed:
            prompts.append(f"{relative}: {words} < recorded {allowed}; lower the record")
    for relative, allowed in sorted(baseline.items()):
        if relative not in counts:
            prompts.append(f"{relative}: page gone, recorded {allowed}; drop it from the record")
    return failures, prompts


def write_baseline(path: Path, counts: dict[str, int], previous: dict[str, int]) -> None:
    pages = {rel: words for rel, words in sorted(counts.items()) if words > WORD_BUDGET}
    raised = [rel for rel, words in pages.items() if words > previous.get(rel, 0) and previous]
    if raised:
        raise SystemExit(
            "refusing to raise the docs-length baseline for: " + ", ".join(raised) + "; "
            "the record only shrinks"
        )
    payload = {
        "schema": BASELINE_SCHEMA,
        "budget": WORD_BUDGET,
        "pages": pages,
        "total": sum(pages.values()),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    baseline_path = args.baseline or (repo_root / DEFAULT_BASELINE_REL)
    counts = measure(repo_root, require_git=args.require_git_file_listing)
    if not counts:
        raise SystemExit(
            "refusing empty matched universe for check_docs_length "
            f"(scan globs: {', '.join(DEFAULT_SCAN_GLOBS)})."
        )
    previous = load_baseline(baseline_path)
    if args.write_baseline:
        write_baseline(baseline_path, counts, previous)
        over = {rel: words for rel, words in counts.items() if words > WORD_BUDGET}
        print(
            f"Wrote docs-length baseline: {len(over)} page(s) over budget {WORD_BUDGET} "
            f"of {len(counts)} scanned."
        )
        return 0
    failures, prompts = judge(counts, previous)
    for prompt in prompts:
        print(f"ADVISORY: {prompt}", file=sys.stderr)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    over = sum(1 for words in counts.values() if words > WORD_BUDGET)
    print(
        f"Validated docs length: {len(counts)} page(s) scanned, budget {WORD_BUDGET} words, "
        f"{over} recorded page(s) over budget, none new."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
