#!/usr/bin/env python3
"""Fallback structural classification for malformed source in what_reads_this.

The main reader answers AST-backed questions. This module owns the narrower lexical
fallback used when a source file cannot parse, including multiline string spans and
quoted membership refusals. Keeping that state machine separate prevents the command
from becoming a second parser.
"""
from __future__ import annotations

import io
import re
import tokenize


def lookup_column(line: str, name: str, column: int) -> bool:
    quoted = re.escape(name)
    pattern = re.compile(
        rf"(?:\.\s*(?:get|pop|setdefault)\s*\(\s*|\[\s*)['\"](?P<key>{quoted})['\"]"
    )
    return any(match.start("key") <= column < match.end("key") for match in pattern.finditer(line))


def membership_column(line: str, name: str, column: int) -> bool:
    quoted = re.escape(name)
    pattern = re.compile(rf"['\"](?P<key>{quoted})['\"]\s+(?:not\s+)?in\b")
    return any(match.start("key") <= column < match.end("key") for match in pattern.finditer(line))


def inside_string_literal(line: str, column: int) -> bool:
    """Recognize a quoted occurrence when AST parsing is unavailable."""
    quote: str | None = None
    escaped = False
    for index, character in enumerate(line):
        if quote is None:
            if character in "'\"":
                quote = character
            continue
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == quote:
            quote = None
        elif index == column:
            return True
    return quote is not None and column >= 0


def structural_kind(
    line: str, name: str, column: int, *, inside_string: bool | None = None
) -> str | None:
    """Classify a simple malformed-source occurrence without line-wide promotion."""
    if membership_column(line, name, column) and re.match(r"\s*if\b", line) and re.search(r"\braise\b", line):
        return "value-constraint"
    if lookup_column(line, name, column):
        if re.match(r"\s*assert\b", line) or (
            re.match(r"\s*if\b", line) and re.search(r"\braise\b", line)
        ):
            return "value-constraint"
        return "lookup"
    if inside_string is None:
        inside_string = inside_string_literal(line, column)
    if inside_string:
        return "string-literal"
    if re.match(r"\s*assert\b", line) and "," not in line:
        return "value-constraint"
    if re.match(r"\s*if\b", line) and re.search(r"\braise\b", line):
        return "value-constraint"
    return None


def string_spans(text: str) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Return tokenized string spans even when the surrounding source is malformed."""
    spans: list[tuple[tuple[int, int], tuple[int, int]]] = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.STRING:
                spans.append((token.start, token.end))
    except (IndentationError, tokenize.TokenError):
        pass
    return spans


def position_in_string_span(
    spans: list[tuple[tuple[int, int], tuple[int, int]]], line_no: int, column: int
) -> bool:
    return any(
        (start_line, start_column) <= (line_no, column) < (end_line, end_column)
        for (start_line, start_column), (end_line, end_column) in spans
    )
