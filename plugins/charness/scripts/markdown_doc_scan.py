#!/usr/bin/env python3

"""One fence/HTML-comment walk for every markdown-scanning gate.

Each doc gate needs the same two structural facts before it can classify a line:
whether the line sits inside a fenced block, and whether it sits inside an HTML
comment. Three copies of that walk had drifted into two gates with an
inconsistent single-line-comment rule; this module is their single home.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HTML_COMMENT_SPAN_RE = re.compile(r"<!--.*?-->")


def iter_doc_lines(doc: Path) -> Iterator[tuple[int, str, bool]]:
    """Yield ``(lineno, line, in_fence)`` for every line carrying live content.

    Fence delimiters and fully commented lines are consumed here, so callers only
    decide what to do with prose versus fenced content. Two rules the callers
    depend on:

    - A yielded line is VERBATIM. A line whose comment span sits beside live
      content keeps the span, because a trailing `<!-- marker -->` is meaningful
      to the caller.
    - Inside a fence, `<!--` is literal text. Opening a comment there would
      swallow the closing delimiter and leave the rest of the document falsely
      marked as fenced.
    """
    in_fence = False
    in_html_comment = False
    for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if in_html_comment:
            if "-->" in stripped:
                in_html_comment = False
            continue
        if not in_fence and stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_html_comment = True
                continue
            if not HTML_COMMENT_SPAN_RE.sub("", stripped).strip():
                continue
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        yield lineno, line, in_fence
