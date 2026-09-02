#!/usr/bin/env python3
"""Count the adapter-YAML lines this repo's own parser cannot interpret.

Sweep row S24 is that a malformed adapter reads as a valid one: the mini parser in
`adapter_lib` drops a line it cannot interpret and keeps going, so `default_org
corca-typo` (no colon) produces a mapping that merely lacks `default_org`, and the
caller's inferred default fills the hole with `valid: true, errors: []`.

Turning those drops into errors is only safe if the corpus has none. That is a number,
not an argument, so this script produces it. It reads files and parses them in memory;
it writes nothing and never mutates the tree.

**What this number does NOT license, stated here because the temptation is to read a
bare 0 as clearance.** The scanned corpus is THIS repo's checked-in YAML. The refusal a
reader might arm on the strength of it would govern a different population: adapters
authored in CONSUMER repos, which this repo has never seen and cannot enumerate. A 0
here is therefore evidence that arming costs this repo nothing, and no evidence at all
about the population the refusal would actually judge. That gap is why the uninterpreted
lines ship as warnings rather than errors because the consumer adapter population is
not measurable from this repository.

Exit codes: 0 clean, 1 the corpus carries uninterpreted lines or files this script could
not read, 2 the roots resolved to no files at all (a clean result over an empty corpus is
not a measurement). The `AssertionError` on parse divergence raises rather than exits.

The identity assertion compares `load_yaml_report` against `load_yaml` — both from the
CURRENT module, so it proves the sink is observation-only. It is NOT evidence that this
parser matches an earlier one; that comparison is a separate run against a checkout.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapter_lib  # noqa: E402

from yaml_output import emit_yaml  # noqa: E402

# Where this repo keeps adapters, presets, and profiles. `plugins/` is absent on purpose:
# it is a generated mirror, so counting it would double every finding. `.` scans the repo
# root's own top-level YAML and nothing deeper.
DEFAULT_ROOTS = (".", ".agents", "presets", "profiles", "skills", "docs", ".claude", ".codex", "integrations")
# Generated mirrors and vendored trees: counting them would double every finding or
# report a dependency's YAML as this repo's.
_EXCLUDED = {"plugins", "node_modules", "mutants", ".git"}


def scan(repo_root: Path, roots: tuple[str, ...]) -> dict[str, object]:
    files: list[Path] = []
    for name in roots:
        root = repo_root / name
        if root.is_dir():
            # `.` means the repo root's OWN top-level YAML, not a recursive walk of the
            # whole tree: recursing there would pull in `node_modules/` and `mutants/`,
            # neither of which any adapter reads.
            walk = root.glob if name == "." else root.rglob
            files += [
                path for pattern in ("*.yaml", "*.yml") for path in walk(pattern)
                if not _EXCLUDED.intersection(path.relative_to(repo_root).parts)
            ]

    findings: list[dict[str, object]] = []
    unreadable: list[dict[str, str]] = []
    scanned = 0
    for path in sorted(set(files)):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            unreadable.append({"path": str(path.relative_to(repo_root)), "error": str(exc)})
            continue
        try:
            parsed, sink = adapter_lib.load_yaml_report(text)
        except ValueError as exc:
            # The parser raises on an unsupported block-scalar header; that is a refusal
            # it already makes loudly, so it is reported rather than counted as a drop.
            unreadable.append({"path": str(path.relative_to(repo_root)), "error": f"parser refused: {exc}"})
            continue
        scanned += 1
        if parsed != adapter_lib.load_yaml(text):
            raise AssertionError(f"load_yaml_report changed the parse result for {path}")
        for entry in sink:
            findings.append({"path": str(path.relative_to(repo_root)), **entry})

    by_reason: dict[str, int] = {}
    for entry in findings:
        reason = str(entry["reason"])
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return {
        "roots": list(roots),
        "scanned_files": scanned,
        "files_with_uninterpreted_lines": len({entry["path"] for entry in findings}),
        "uninterpreted_line_count": len(findings),
        "by_reason": by_reason,
        "findings": findings,
        "unreadable": unreadable,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--roots", nargs="*", default=list(DEFAULT_ROOTS))
    args = parser.parse_args()

    report = scan(args.repo_root.resolve(), tuple(args.roots))
    # A file this script could not read still means the roots resolved to something, so
    # it counts toward "we looked at a corpus" even though it contributes no findings.
    if not report["scanned_files"] and not report["unreadable"]:
        # A PASS over an empty corpus. The whole point of this script is that a 0 means
        # something; a 0 out of 0 files means only that the roots resolved to nothing.
        print(
            f"no adapter YAML files found under {args.repo_root} for roots {list(args.roots)}; "
            "a clean result over an empty corpus is not a measurement.",
            file=sys.stderr,
        )
        return 2
    # Unconditional YAML. The retired summary and per-entry lines were a strict
    # projection of `scanned_files`, `uninterpreted_line_count`,
    # `files_with_uninterpreted_lines`, and each `findings`/`unreadable` entry.
    emit_yaml(report)
    # A file this script could not read, or that the parser refused outright, is exactly
    # the state it exists to make visible — reporting it and then exiting 0 would be this
    # measurement committing the class it measures.
    return 1 if report["uninterpreted_line_count"] or report["unreadable"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
