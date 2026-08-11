#!/usr/bin/env python3

"""One fence/HTML-comment walk, and one link-shape vocabulary, for every markdown gate.

Each doc gate needs the same two structural facts before it can classify a line:
whether the line sits inside a fenced block, and whether it sits inside an HTML
comment. Three copies of that walk had drifted into two gates with an
inconsistent single-line-comment rule; this module is their single home.

The link half arrived the same way. `check_doc_links.py` and
`check_plugin_doc_links.py` ask different questions -- one judges a link where it
is authored, the other where a consumer reads it after export -- but both must
first agree on what shape a target has and where a relative one points. Keeping
that agreement in one place is what stops the two gates from disagreeing about
whether `docs/guide.md` is a link at all.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HTML_COMMENT_SPAN_RE = re.compile(r"<!--.*?-->")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

INERT_LINK = "inert"
ABSOLUTE_LINK = "absolute"
BARE_LINK = "bare"
RELATIVE_LINK = "relative"


def classify_link_shape(raw_target: str) -> str:
    """Return the shape of a markdown link target, before any filesystem question.

    - ``INERT_LINK``: empty, a pure anchor, a URL, or a mailto -- carries no
      filesystem claim, so no gate should resolve it.
    - ``ABSOLUTE_LINK``: rooted at ``/``.
    - ``BARE_LINK``: relative but missing the ``./`` / ``../`` prefix that makes a
      file reference distinguishable from a concept token at a glance.
    - ``RELATIVE_LINK``: the only shape ``resolve_relative_link`` accepts.
    """
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return INERT_LINK
    if "://" in target or target.startswith("mailto:"):
        return INERT_LINK
    if target.startswith("/"):
        return ABSOLUTE_LINK
    if target.startswith("./") or target.startswith("../"):
        return RELATIVE_LINK
    return BARE_LINK


def resolve_relative_link(doc: Path, raw_target: str) -> Path:
    """Resolve a ``RELATIVE_LINK`` target from the document that carries it.

    The anchor is stripped first: `./target.md#a-heading` names `./target.md`, and
    a gate that resolves the whole string reports every anchored link as broken.
    """
    relative_target = raw_target.strip().split("#", 1)[0]
    return (doc.parent / relative_target).resolve()


def iter_link_targets(text: str) -> list[str]:
    return LINK_RE.findall(text)


def iter_doc_lines(doc: Path) -> Iterator[tuple[int, str, bool]]:
    """Yield ``(lineno, line, in_fence)`` for every line carrying live content.

    The boolean view of `iter_doc_lines_with_language`, for the callers that only
    need "prose or fenced". See that function for the walk's rules.
    """
    for lineno, line, language in iter_doc_lines_with_language(doc):
        yield lineno, line, language is not None


def iter_doc_lines_with_language(doc: Path) -> Iterator[tuple[int, str, str | None]]:
    """Yield ``(lineno, line, fence_language)`` for every line carrying live content.

    ``fence_language`` is ``None`` in prose and the fence's info string inside a
    fence -- ``""`` when the fence declared none. It is the info string VERBATIM
    (lowercased, first word only): what counts as a shell fence is the caller's
    question, not this walk's.

    Fence delimiters and fully commented lines are consumed here, so callers only
    decide what to do with prose versus fenced content. Two rules the callers
    depend on:

    - A yielded line is VERBATIM. A line whose comment span sits beside live
      content keeps the span, because a trailing `<!-- marker -->` is meaningful
      to the caller.
    - Inside a fence, `<!--` is literal text. Opening a comment there would
      swallow the closing delimiter and leave the rest of the document falsely
      marked as fenced.
    - A fence closes only on its OWN marker character, at least as long as the
      run that opened it -- CommonMark's rule. A plain toggle over `(```|~~~)`
      treats a `~~~` line inside a backtick fence as a delimiter, which inverts
      `in_fence` for the whole rest of the document. That is a false negative for
      any caller that skips fenced lines, and "a doc that teaches fence syntax"
      is exactly the shape that triggers it.
    - When a multi-line HTML comment closes mid-line, the text AFTER `-->` is
      live content and is yielded. Dropping the whole line hides a link that
      renders normally.
    """
    fence_language: str | None = None
    fence_marker = ""
    in_html_comment = False
    for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        if in_html_comment:
            if "-->" not in line:
                continue
            in_html_comment = False
            line = line.split("-->", 1)[1]
            if not line.strip():
                continue
        stripped = line.strip()
        if fence_language is None and stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_html_comment = True
                continue
            if not HTML_COMMENT_SPAN_RE.sub("", stripped).strip():
                continue
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence_language is None:
                info = line[fence_match.end() :].strip().lower().split()
                fence_language, fence_marker = (info[0] if info else ""), marker
                continue
            if marker[0] == fence_marker[0] and len(marker) >= len(fence_marker):
                fence_language, fence_marker = None, ""
                continue
        yield lineno, line, fence_language
