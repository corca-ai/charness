"""JS/TS settlement-seam scanning for the standing-test economics inventory.

Split from ``surface_marker_lib`` along a real seam: that module reads Python through
``ast`` and pytest markers through the same tree, while this one has no parser at all and
scans text with a hand-written delimiter walk. The walk is what the repair to this file
is about -- the predecessor searched a LINE with two regexes, which read `30 * 1000` as
the literal `30`, gave an undeadlined call its neighbour's `timeout:`, and reported a
call whose options object wrapped onto the next line as having none.

Non-claim: this reads visible syntax. It does not evaluate expressions, resolve
identifiers, or observe a child process, so ``unknown`` is a real answer here and not a
placeholder for one.
"""
from __future__ import annotations

import re

_JS_CALL_RE = re.compile(r"\b(spawnSync|execFileSync|execSync|spawn|execa)\s*\(")
_JS_SYNC_CALLS = {"spawnSync", "execFileSync", "execSync"}

# A JS numeric literal, whole. The point of `fullmatch` here is that `30 * 1000` and
# `5 + delay` must NOT reach it -- the predecessor captured only `30` and `5` because
# its value pattern stopped at the first space, so an expression read as a literal.
_JS_NUMBER_RE = re.compile(r"(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")
_JS_NO_DEADLINE_LITERALS = {"undefined", "null"}


def _js_scan_escaped(text: str, index: int, terminates) -> int:
    """Advance past the delimited literal opening at ``index``, honouring ``\\`` escapes.

    ``terminates(char, cursor)`` returns the index just past the literal, or None to keep
    scanning. One escape-aware walk for both literal kinds: strings and regexes differ
    only in what ends them, and writing the walk twice is how one of them later gains an
    escape case the other silently lacks.
    """
    cursor = index + 1
    while cursor < len(text):
        char = text[cursor]
        if char == "\\":
            cursor += 2
            continue
        end = terminates(char, cursor)
        if end is not None:
            return end
        cursor += 1
    return len(text)


def _js_skip_quoted(text: str, index: int) -> int:
    """Return the index just past the string/template literal opening at ``index``."""
    quote = text[index]

    def terminates(char: str, cursor: int) -> int | None:
        if char == quote:
            return cursor + 1
        # A raw newline cannot appear inside a '' or "" string, exactly as it cannot
        # inside a regex literal -- and the regex scanner already bails on one. Without
        # the same bail here, a stray quote (produced by any local mis-parse upstream)
        # runs to the next quote ANYWHERE in the file, and one corrupted line becomes a
        # file-wide desync that fabricates seams out of string contents. This bounds
        # every such mis-parse to a single line. Template literals are genuinely
        # multi-line, so the backtick keeps scanning.
        if char == "\n" and quote != "`":
            return index + 1
        return None

    return _js_scan_escaped(text, index, terminates)


def _js_skip_comment(text: str, index: int) -> int | None:
    """Return the index just past a comment opening at ``index``, or None if not one."""
    if text.startswith("//", index):
        end = text.find("\n", index)
        return len(text) if end == -1 else end
    if text.startswith("/*", index):
        end = text.find("*/", index + 2)
        return len(text) if end == -1 else end + 2
    return None


def _js_skip_regex(text: str, index: int) -> int:
    """Return the index just past the regex literal opening at ``text[index] == '/'``.

    Regex literals are here because of a *balanced but wrong* mis-parse, which is worse
    than an unbalanced one: the unbalanced guard downgrades a call to ``unknown``, while a
    mis-parse that happens to balance publishes a confident verdict about text the walker
    never read. ``/\\//`` is four characters, and its middle two are ``//`` -- so without
    this, the comment rule swallowed the rest of the line and the region ran on into
    unrelated statements, attributing a later `timeout:` to a call that declares none.
    A ``/`` inside a ``[...]`` character class is literal and does not close the literal.
    """
    in_class = [False]

    def terminates(char: str, cursor: int) -> int | None:
        if char == "\n":
            # A regex literal cannot span lines; treat this as "not a regex after all".
            return index + 1
        if char == "[":
            in_class[0] = True
        elif char == "]":
            in_class[0] = False
        elif char == "/" and not in_class[0]:
            return cursor + 1
        return None

    return _js_scan_escaped(text, index, terminates)


# A `/` starts a regex literal only in value position. The preceding significant
# character decides: after a value (identifier, number, `)`, `]`, `}`) a `/` is division.
#
# `}` is deliberately EXCLUDED even though `if (x) {} /re/` is legal, because `.jsx` and
# `.tsx` are in scope and JSX puts `}` immediately before the `/` of a self-closing tag
# on every line like `<App route={r} />`. Treating that as a regex opener made the scan
# run past the tag and terminate on a `/` inside a later string -- after which the walk
# was inside a string literal and minted seams from its contents. A regex directly after
# a block close is rare; a self-closing JSX tag after an expression container is not.
_JS_VALUE_POSITION_BEFORE = set("(,=:[!&|?;+-*/%~^<>{") | {""}
# A character set cannot see keywords, so a genuine regex after `return`/`typeof`/... was
# read as division and its body scanned as code -- and a quote in that body opened a
# phantom string with the same consequence as above.
_JS_VALUE_POSITION_KEYWORDS = {
    "return", "typeof", "case", "throw", "yield", "await", "in", "of", "delete",
    "void", "instanceof", "new", "do", "else",
}
_JS_TRAILING_WORD_RE = re.compile(r"([A-Za-z_$][\w$]*)\s*$")


def _js_opens_regex(text: str, cursor: int, previous: str) -> bool:
    if previous in _JS_VALUE_POSITION_BEFORE:
        return True
    if not (previous.isalnum() or previous in "_$"):
        return False
    word = _JS_TRAILING_WORD_RE.search(text, 0, cursor)
    return bool(word) and word.group(1) in _JS_VALUE_POSITION_KEYWORDS


def _js_code_positions(text: str, start: int = 0):
    """Yield ``(index, char)`` for every position outside a string, comment, or regex.

    One walker, three readers. Each of the three below needs the same "skip what is not
    code" traversal and differs only in the bookkeeping it does per character; writing
    that traversal out three times is how one of them later gains a skip case the others
    silently lack.
    """
    cursor = start
    previous = ""
    while cursor < len(text):
        char = text[cursor]
        if char in "'\"`":
            cursor = _js_skip_quoted(text, cursor)
            previous = "'"
            continue
        if char == "/":
            # Comment first: `foo(); // note` is a comment even though `;` is a value
            # position. A regex opener is never `//` or `/*`, so this order is safe.
            comment_end = _js_skip_comment(text, cursor)
            if comment_end is not None:
                cursor = comment_end
                continue
            if _js_opens_regex(text, cursor, previous):
                cursor = _js_skip_regex(text, cursor)
                previous = "'"
                continue
        if not char.isspace():
            previous = char
        yield cursor, char
        cursor += 1


def _js_code_offsets(text: str) -> set[int]:
    """Offsets that are real code, for filtering call-site matches.

    The call regex runs over raw source, so `// legacy: execSync(cmd, {timeout: 1000})`
    and `const doc = "execSync(cmd, {timeout: 1000})"` each minted a seam with a
    fabricated `present`/`finite` verdict -- the module built a "skip what is not code"
    walker and then did not use it for the one decision that creates a seam.
    """
    return {index for index, _ in _js_code_positions(text)}


def _js_argument_region(text: str, open_paren: int) -> tuple[int, int] | None:
    """Return ``[start, end)`` of the argument list of the call whose ``(`` is at
    ``open_paren``, or None when the delimiters do not balance.

    This exists because the predecessor searched the whole LINE. Two consequences it
    could not distinguish: `execSync(a); spawnSync(b, {timeout: 100})` gave BOTH calls a
    deadline, and a call whose options object wrapped onto the next line was recorded as
    having none. A per-call region answers both, and it follows a call across lines.
    """
    depth = 0
    for cursor, char in _js_code_positions(text, open_paren):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
            if depth == 0:
                return (open_paren + 1, cursor)
            if depth < 0:
                return None
    return None


def _js_slice_value(region: str, start: int) -> str:
    """Slice the WHOLE value expression at ``start``, not its first token.

    The predecessor's value pattern was ``[^,}\\s]+``, which stops at the first space --
    so `timeout: 30 * 1000` yielded `30`, an expression read as a literal.
    """
    depth = 0
    end = len(region)
    for cursor, char in _js_code_positions(region, start):
        if char in "([{":
            depth += 1
            continue
        if depth == 0 and (char in ")]}" or char == ","):
            end = cursor
            break
        if char in ")]}":
            depth -= 1
    return region[start:end].strip()


def _js_option_value(region: str, key: str) -> str | None:
    """Return the raw value of ``key`` declared directly in this call's own arguments.

    Accepted only at brace depth exactly 1 with no enclosing parenthesis or bracket --
    that is, a direct property of an options object this call passes itself. Two nesting
    mechanisms can hide a foreign option, and the first repair caught only one of them:
    a nested CALL raises the parenthesis depth (``spawn(cmd, opts,
    fn(execSync(x, {timeout: 5})))`` declares no timeout of its own), but a nested OBJECT
    or ARRAY did not (``spawnSync(cmd, args, {env: e, child: {timeout: 1000}})`` was read
    as a 1000 ms deadline). Same borrowing defect, one container type over.
    """
    pattern = re.compile(rf"""(?:^|[{{,;\s])(?:{key}|["']{key}["'])\s*:\s*""")
    parens = brackets = braces = 0
    for cursor, char in _js_code_positions(region):
        match = pattern.match(region, cursor)
        if match is not None:
            # The pattern consumes the delimiter before the key, and that delimiter may
            # BE the opening brace, which this loop has not counted yet.
            key_braces = braces + 1 if char == "{" else braces
            if parens == 0 and brackets == 0 and key_braces == 1:
                return _js_slice_value(region, match.end())
        if char == "(":
            parens += 1
        elif char == ")":
            parens -= 1
        elif char == "[":
            brackets += 1
        elif char == "]":
            brackets -= 1
        elif char == "{":
            braces += 1
        elif char == "}":
            braces -= 1
    return None


def _js_deadline_state(region: str) -> str:
    """Classify the deadline a call declares in its own arguments.

    ``0`` is ``absent``, not ``present``: every call family this scanner matches
    (`child_process` sync helpers and `execa`) applies its timeout only when the value is
    greater than zero, so `timeout: 0` is the documented spelling of "no deadline". The
    predecessor read it as a finite deadline, which is the inverse of the truth.
    Anything that is not a whole numeric literal is ``unknown``; this scanner reads
    syntax and cannot evaluate `30 * 1000`.
    """
    value = _js_option_value(region, "timeout")
    if value is None or value in _JS_NO_DEADLINE_LITERALS:
        return "absent"
    if _JS_NUMBER_RE.fullmatch(value) is None:
        return "unknown"
    return "present" if float(value) > 0 else "absent"


def _js_output_bounding(region: str) -> str:
    value = _js_option_value(region, "stdio")
    if value is None:
        return "unknown"
    literal = value[1:-1] if len(value) >= 2 and value[0] in "'\"`" and value[-1] == value[0] else None
    if literal == "ignore":
        return "bounded"
    if literal == "pipe":
        return "unbounded"
    return "unknown"


def js_settlement_seams(rel_path: str, text: str) -> list[dict]:
    seams: list[dict] = []
    code_offsets = _js_code_offsets(text)
    for match in _JS_CALL_RE.finditer(text):
        # A call name inside a comment or a string is not a call site. It used to mint a
        # seam whose verdict was computed from text that never executes.
        if match.start() not in code_offsets:
            continue
        call = match.group(1)
        bounds = _js_argument_region(text, match.end() - 1)
        # Unbalanced source is not an empty argument list. Reading it as one would
        # report `absent`/`unknown` about a call this scanner could not actually read.
        region = text[bounds[0]:bounds[1]] if bounds is not None else None
        deadline = "unknown" if region is None else _js_deadline_state(region)
        seams.append(
            {
                "path": rel_path,
                "line": text.count("\n", 0, match.start()) + 1,
                "call": call,
                "deadline": deadline,
                "lifecycle": "finite"
                if call in _JS_SYNC_CALLS and deadline == "present"
                else "unknown",
                "process_tree_termination": "unknown",
                "output_bounding": "unknown" if region is None else _js_output_bounding(region),
            }
        )
    return seams
