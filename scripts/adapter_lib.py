#!/usr/bin/env python3

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
            item_body = stripped[2:].strip()
            if not item_body:
                items.append("")
                index += 1
                continue
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


def uninterpreted_warnings(uninterpreted: list[dict[str, Any]]) -> list[str]:
    """One operator-facing line per line the parser could not interpret. Lives here, with
    the producer of the facts, so every adapter resolver words the same finding the same
    way instead of each inventing its own phrasing."""
    return [
        f"line {entry['line']} was not interpreted ({entry['reason']}): {entry['text'].strip()!r}. "
        "Any field it meant to set is serving an inferred default instead."
        for entry in uninterpreted
    ]


def parse_failure_error(exc: Exception) -> str:
    """The message for a construct the parser refuses outright, as opposed to one it
    silently drops. A refusal is not a drop and must not read like one."""
    return f"adapter could not be parsed: {exc}"


# The one adapter schema version every resolver in this repo speaks. It lives here, with
# the loader the resolvers already share, because the alternative was measured: 17 sites
# hand-copied a `version` check and 16 of them only asked "is it an int?", then wrote the
# answer into the resolved payload as authoritative. A repo could declare `version: 9` and
# every one of those 16 echoed 9 back as if it had been honoured. `bool` is excluded
# explicitly because `isinstance(True, int)` is True and this module's own scalar coercion
# turns a bare `true` into `True` -- so `version: true` read as a valid integer version at
# all 17 sites, including the one that did check a supported value.
SUPPORTED_ADAPTER_VERSION = 1


def validate_adapter_version(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str],
    *, supported: int | None = None, field: str = "version", required: bool = False,
) -> None:
    """Reconcile a declared adapter ``version`` against the version this reader speaks.

    Absent is legal by default and leaves the caller's inferred default in place. A
    non-integer and an unsupported integer are both errors, and neither writes
    ``validated[field]``: a version the reader cannot interpret must not come back out as
    authoritative. Message wording is fixed by existing callers' fixtures and is
    deliberately not reworded here.

    ``supported`` resolves at CALL time, not at definition time. As a plain default it
    would bind ``SUPPORTED_ADAPTER_VERSION``'s value once at import, so rebinding the
    module constant -- which is exactly what a bump, or a test proving the bump path,
    would do -- changed nothing while appearing to work.

    ``required`` is a parameter rather than a caller-side pre-check because the
    commit-time gate needs a stricter answer than the resolvers do: it refuses an adapter
    declaring no version at all, while a resolver falls back to its inferred default.
    That difference lives here, with the contract, so the strict site does not hand-roll a
    predicate beside the shared one -- hand-rolled predicates beside a shared check are
    exactly how 18 sites came to disagree in the first place.
    """
    supported = SUPPORTED_ADAPTER_VERSION if supported is None else supported
    value = data.get(field)
    if value is None:
        if required:
            errors.append(f"{field} is required")
        return
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{field} must be an integer")
    elif value != supported:
        errors.append(f"{field} must be {supported}")
    else:
        validated[field] = value


def optional_string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def optional_string_list(value: Any, field: str, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return None
    return list(value)


def optional_bool(value: Any, field: str, errors: list[str]) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        errors.append(f"{field} must be a boolean")
        return None
    return value


def list_field_state(data: dict[str, Any], field: str) -> str:
    if field not in data:
        return "unset"
    value = data.get(field)
    if isinstance(value, list) and len(value) == 0:
        return "explicit-empty"
    return "configured"


def plan_generated_write(
    existing_text: str | None, rendered_text: str, *, also_unchanged_when: bool = False
) -> str:
    """Classify what writing `rendered_text` over `existing_text` would do.

    Returns `absent` (no file yet), `unchanged`, or `differs`. Deciding this BEFORE
    touching the disk is what lets a dry run report the same verdict a real run would
    reach, and what keeps a generator from rewriting a file it has nothing to change in.
    Callers map the three outcomes onto their own status vocabulary and their own policy
    for whether `differs` may overwrite.
    """
    if existing_text is None:
        return "absent"
    return "unchanged" if existing_text == rendered_text or also_unchanged_when else "differs"


def write_adapter_scaffold(repo_root: Path, output: Path, contents: str, force: bool) -> Path:
    resolved_output = output if output.is_absolute() else repo_root / output
    if resolved_output.exists() and not force:
        raise SystemExit(f"Adapter already exists at {resolved_output}. Use --force to overwrite.")

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(contents, encoding="utf-8")
    return resolved_output
