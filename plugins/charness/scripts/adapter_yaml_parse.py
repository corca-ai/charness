#!/usr/bin/env python3

"""This repo's own YAML dialect: how an adapter document is READ, and what it drops.

Split from ``adapter_lib`` when that module crossed its length cap. The boundary is the one
its two halves already had: this answers "what does this repo's parser make of these bytes",
and ``adapter_lib`` answers "what does an adapter resolver owe once it has them" -- version
reconciliation, field validators, the declared-document read, and the seven-key payload.
The second half grew a hundred lines in one slice while this one did not move, which is the
usual shape of a file that is two files.

WHY A HAND-ROLLED PARSER AT ALL, stated because the first question anyone asks is why not
PyYAML: charness adapters must be readable with no third-party dependency in a repo that has
not installed one, and the dialect is deliberately small. The cost is that the dialect is
NARROWER than YAML and the difference is what the uninterpreted-line sink exists to report:
a flow sequence is a plain string here, an anchor or a tag is REFUSED outright, and an
over-indented line is silently dropped. Every one of those has produced a measured defect in
this repo, so each is reported through a channel a consumer guard can read rather than
absorbed.

``adapter_lib`` re-exports every public name here, so consumers keep one import site and no
call site outside had to change.

BLIND CLASS: it reports what it could not interpret, never what the document MEANT. A
document that parses cleanly into the wrong shape -- the mapping-vs-list confusion this repo
has shipped twice -- is invisible here and belongs to the validators.
"""

from __future__ import annotations

import contextvars
import re
from pathlib import Path
from typing import Any

SUPPORTED_BLOCK_SCALAR_RE = re.compile(r"^[|>](-)?$")


def strip_inline_comment(value: str) -> str:
    """Drop a trailing ` # ...` comment from an unquoted scalar.

    Without this the comment text is swallowed into the value, so
    ``margin: 2.0  # widened`` parses as the string ``"2.0  # widened"``. A caller
    type-checking for a number then rejects it and silently falls back to a default,
    while still reporting the field as preserved — the operator's value is lost and
    the report says it was kept. Only space-hash starts a YAML comment, so a value
    like ``a#b`` is left alone.
    """
    if (index := inline_comment_start(value)) is not None:
        return value[:index].strip()
    return value


def inline_comment_start(value: str) -> int | None:
    """Return the first YAML comment marker outside a leading quoted scalar.

    A quoted scalar may be followed by a valid trailing comment, for example
    ``"https://example.test/a # fragment" # annotation``. The previous
    space-hash scan treated the hash inside the scalar as the comment and
    truncated the value before bootstrap or resolution could inspect it.
    Plain scalars may contain apostrophes, so quote tracking begins only when
    the value itself begins with a quote.
    """
    leading = len(value) - len(value.lstrip())
    candidate = value[leading:]
    quote = candidate[0] if candidate[:1] in {"'", '"'} else None
    escaped = False
    index = leading + 1 if quote is not None else leading
    while index < len(value):
        char = value[index]
        if quote is not None:
            if quote == '"' and escaped:
                escaped = False
                index += 1
                continue
            if quote == '"' and char == "\\":
                escaped = True
                index += 1
                continue
            if char == quote:
                if quote == "'" and index + 1 < len(value) and value[index + 1] == "'":
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if char == "#" and (index == 0 or value[index - 1] in " \t"):
            return index
        index += 1
    return None


def _coerce_scalar(value: str) -> Any:
    value = strip_inline_comment(value)
    _reject_unsupported_scalar(value)
    if value == "":
        return ""
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in ("null", "~"):
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.startswith('"') and value.endswith('"'):
        return _decode_double_quoted(value[1:-1])
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def _is_quoted_scalar(value: str) -> bool:
    return (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))


def _decode_double_quoted(value: str) -> str:
    decoded: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char != "\\" or index + 1 >= len(value):
            decoded.append(char)
            index += 1
            continue
        escaped = value[index + 1]
        if escaped == "n":
            decoded.append("\n")
        elif escaped == "r":
            decoded.append("\r")
        elif escaped in {'"', "\\"}:
            decoded.append(escaped)
        else:
            decoded.append("\\")
            decoded.append(escaped)
        index += 2
    return "".join(decoded)


def _reject_unsupported_scalar(value: str) -> None:
    stripped = value.strip()
    if not stripped or _is_quoted_scalar(stripped):
        return
    if stripped.startswith(("*", "&", "!")):
        raise ValueError(f"unsupported YAML construct in scalar: {value!r}")


def _find_mapping_separator(value: str) -> int:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote == '"' and char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char == ":":
            return index
    return -1


def _split_mapping_entry(value: str) -> tuple[str, str] | None:
    separator = _find_mapping_separator(value)
    if separator < 0:
        return None
    key = _coerce_scalar(value[:separator].strip())
    if not isinstance(key, str):
        key = str(key)
    return key, value[separator + 1 :].strip()


def _next_meaningful_line(lines: list[str], start: int) -> tuple[int, str] | None:
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return index, lines[index]
    return None


# The parser drops a line it cannot interpret and keeps going, which is what lets a
# malformed adapter read as a valid one (sweep row S24): `default_org corca-typo` with
# no colon parses to a mapping that simply lacks `default_org`, and the caller's
# inferred default fills the hole silently. The sink below records those drops WITHOUT
# changing what the parser returns, so a caller can distinguish "the file did not say
# this" from "the file said something the parser threw away". Collection is off unless
# a `load_yaml_report` call is on the stack: existing `load_yaml` callers are
# byte-identical.
# A ContextVar rather than a module global: the sink is per-parse state, and a plain
# global would let a future nested or threaded `load_yaml` leak one file's dropped lines
# into another file's report — an unrelated input's evidence read as this input's, which
# is the class this collector exists to close.
_UNINTERPRETED_SINK: contextvars.ContextVar[list[dict[str, Any]] | None] = contextvars.ContextVar(
    "adapter_lib_uninterpreted_sink", default=None
)
# YAML document markers carry no mapping content, so dropping them loses nothing. They
# are skipped rather than recorded: reporting them would refuse legal YAML that many
# editors and templates emit by default.
_DOCUMENT_MARKERS = ("---", "...")


def _record_uninterpreted(lines: list[str], index: int, reason: str) -> None:
    sink = _UNINTERPRETED_SINK.get()
    if sink is None:
        return
    sink.append({"line": index + 1, "reason": reason, "text": lines[index].rstrip()})


def _line_shape(lines: list[str], index: int) -> tuple[str, str, int]:
    """`(raw, stripped, indent)` for one line — the preamble both parser loops share."""
    raw = lines[index]
    return raw, raw.strip(), len(raw) - len(raw.lstrip(" "))


def _is_ignorable(stripped: str) -> bool:
    """Blank or comment: carries no content, so skipping it loses nothing.

    Document markers are deliberately NOT included. Skipping them here would be safe in
    the mapping loop and wrong in the list loop, where `---` ENDS the list: treating it as
    ignorable merged a second document's items into the first document's list and changed
    what `load_yaml` returns. The mapping loop tests for them at its own call site.
    """
    return not stripped or stripped.startswith("#")


def _mapping_value(
    lines: list[str], index: int, indent: int, value: str
) -> tuple[Any, int, bool]:
    """Parse the text after `key:` — the three-way dispatch both parser loops need.

    Returns `(parsed, next_index, consumed_block)`; `consumed_block` is True when a block
    scalar swallowed the following lines, which is the one case a caller must not treat
    as a single-line advance.
    """
    # Strip before the dispatch below, not only inside `_coerce_scalar`. Every branch
    # here compares the raw post-colon text, so a trailing comment made `[]`, `{}`, a
    # block-scalar header, and "empty, value is on the following lines" all fall through
    # to the scalar branch — turning a nested block into the empty string and dropping
    # its children silently, while the field still counted as explicitly set.
    value = strip_inline_comment(value)
    if not value:
        parsed, next_index = _parse_empty_value(lines, index, indent)
        return parsed, next_index, False
    if value == "[]":
        return [], index + 1, False
    if value == "{}":
        return {}, index + 1, False
    if value.startswith(("|", ">")):
        parsed, next_index = _parse_block_scalar(lines, index, indent, value)
        return parsed, next_index, True
    return _coerce_scalar(value), index + 1, False


def _parse_list_items(lines: list[str], start: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    index = start
    while index < len(lines):
        raw, stripped, current_indent = _line_shape(lines, index)
        if _is_ignorable(stripped):
            index += 1
            continue
        if current_indent < indent:
            break
        if current_indent == indent:
            if not stripped.startswith("- "):
                break
            # `item_body` cannot be empty here, and the empty-item branch that used to
            # follow was dead. `stripped` is `raw.strip()`, so if it starts with `- ` there
            # is a non-space character after that space -- a trailing one would have been
            # stripped. A bare `-` therefore fails `startswith("- ")` and ENDS the list at
            # the check above, which is the real behavior and is pinned by
            # `test_a_bare_dash_ends_the_list_rather_than_adding_an_empty_item`. Found when
            # the module split made the changed-line gate read these lines as new.
            item_body = stripped[2:].strip()
            if _is_quoted_scalar(item_body):
                items.append(_coerce_scalar(item_body))
                index += 1
                continue
            separator = _find_mapping_separator(item_body)
            mapping_entry = _split_mapping_entry(item_body)
            has_mapping_separator = separator == len(item_body) - 1 or (
                separator >= 0 and item_body[separator + 1].isspace()
            )
            if mapping_entry is not None and has_mapping_separator and " " not in mapping_entry[0]:
                key, value = mapping_entry
                item: dict[str, Any] = {}
                item[key], index, consumed_block = _mapping_value(lines, index, indent + 2, value)
                if consumed_block:
                    items.append(item)
                    continue
                nested, index = _parse_block(lines, index, indent + 2)
                item.update(nested)
                items.append(item)
                continue
            items.append(_coerce_scalar(item_body))
            index += 1
            continue
        # The fourth drop site, and the one the first instrumentation pass missed: a line
        # more indented than the list it sits under is discarded here. That eats a nested
        # `  - item` and a wrapped plain-scalar continuation alike.
        _record_uninterpreted(lines, index, "over-indented line in list")
        index += 1
    return items, index


def _parse_empty_value(lines: list[str], index: int, current_indent: int) -> tuple[Any, int]:
    next_item = _next_meaningful_line(lines, index + 1)
    if next_item is None:
        return {}, index + 1
    next_index, next_raw = next_item
    next_stripped = next_raw.strip()
    next_indent = len(next_raw) - len(next_raw.lstrip(" "))
    if next_stripped.startswith("- "):
        if next_indent < current_indent:
            return {}, index + 1
        return _parse_list_items(lines, next_index, next_indent)
    if next_indent <= current_indent:
        return {}, index + 1
    return _parse_block(lines, index + 1, current_indent + 2)


def _parse_block_scalar(lines: list[str], start: int, current_indent: int, header: str) -> tuple[str, int]:
    if SUPPORTED_BLOCK_SCALAR_RE.fullmatch(header) is None:
        raise ValueError(f"unsupported YAML construct in block scalar header: {header!r}")
    style = header[0]
    strip_final = header.endswith("-")
    index = start + 1
    block_indent: int | None = None
    collected: list[str] = []
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))
        if stripped and indent <= current_indent:
            break
        if block_indent is None and stripped:
            block_indent = indent
        trim = block_indent if block_indent is not None else current_indent + 2
        collected.append(raw[trim:] if len(raw) >= trim else "")
        index += 1
    if style == ">":
        rendered = " ".join(line.strip() for line in collected if line.strip())
    else:
        rendered = "\n".join(collected)
    if not strip_final:
        rendered += "\n"
    return rendered, index


def _parse_block(lines: list[str], start: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    index = start

    while index < len(lines):
        raw, stripped, current_indent = _line_shape(lines, index)

        if _is_ignorable(stripped) or stripped in _DOCUMENT_MARKERS:
            index += 1
            continue
        if current_indent < indent:
            break
        if current_indent > indent:
            _record_uninterpreted(lines, index, "over-indented line")
            index += 1
            continue
        if stripped.startswith("- "):
            _record_uninterpreted(lines, index, "list item with no owning key")
            index += 1
            continue

        mapping_entry = _split_mapping_entry(stripped)
        if mapping_entry is None:
            _record_uninterpreted(lines, index, "no mapping separator")
            index += 1
            continue
        key, value = mapping_entry
        result[key], index, _ = _mapping_value(lines, index, current_indent, value)

    return result, index


def load_yaml(text: str) -> dict[str, Any]:
    parsed, _ = _parse_block(text.splitlines(), 0, 0)
    return parsed


def load_yaml_file(path: Path) -> dict[str, Any]:
    return load_yaml(path.read_text(encoding="utf-8"))


def load_yaml_report(text: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Parse ``text`` exactly as ``load_yaml`` does, and also return the lines the
    parser could not interpret. The parsed value is identical to ``load_yaml(text)``;
    the second element is the evidence a caller needs before reporting the file valid."""
    sink: list[dict[str, Any]] = []
    token = _UNINTERPRETED_SINK.set(sink)
    try:
        parsed, _ = _parse_block(text.splitlines(), 0, 0)
    finally:
        _UNINTERPRETED_SINK.reset(token)
    return parsed, sink


def load_yaml_file_report(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    return load_yaml_report(path.read_text(encoding="utf-8"))
