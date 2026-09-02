#!/usr/bin/env python3
"""One reader for this repo's `#`-commented waiver and allowlist files.

Two parsers had converged on the same four lines -- read the file, number the lines
from 1, strip each, skip blanks and comments -- and the dup ratchet formed a family from
them. They are validator reference waivers and
`check_skill_ownership_overlap`'s ownership allowlist.

Deliberately does NOT parse or validate. The three callers disagree about what a
malformed entry means -- two raise, one collects the line numbers and publishes them --
and that disagreement is a real design difference, not duplication. Folding it in here
would force one of those behaviours onto all three.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path


def iter_waiver_lines(path: Path) -> Iterator[tuple[int, str]]:
    """`(line_number, stripped_line)` for each entry line, blanks and comments skipped.

    Line numbers are 1-based and count the file's own lines, so a caller can name the
    offending line in a message an operator will `grep` for.

    Raises `FileNotFoundError` on FIRST ITERATION over a missing path, not at call
    time -- this is a generator function, so `iter_waiver_lines(missing)` returns
    normally and a `try` around the call alone catches nothing.

    It does not return empty. A caller that skips its own existence guard gets the
    OSError rather than that caller's own error type, which is the point: the callers
    that have a guard keep it, and one that forgets gets a loud failure instead of a
    silent empty result. (An earlier draft justified this by saying each caller wants a
    different empty value. Two of them return `{}`; that reason was not true.)
    """
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        yield number, line
