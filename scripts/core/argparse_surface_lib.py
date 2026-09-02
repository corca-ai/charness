"""Read an argparse `--help` surface, and scope a documented invocation to it.

Split out of `check_documented_command_flags.py`, which owns a different question:
finding documented commands in the docs, resolving which script each names, and
reporting drift. This module owns the argparse side of that check -- what a parser
declares, which of its options consume a value, and which parser would actually
receive a flag written at a given position in a documented command line.

It is one concern, not a length-cap spill: the three parts only make sense
together. Positions are what let a flag be attributed to a parser (argparse hands
everything after a subcommand token to that subparser and nothing before it), and
value-consumption is what keeps a flag VALUE that happens to spell a subcommand
name from re-routing the attribution. Measured on a two-level parser:

    demo --top x resolve --current y   -> ok
    demo resolve --current y --top x   -> error: unrecognized arguments
    demo --current y resolve           -> error: invalid choice 'y'
"""

from __future__ import annotations

import re
import shlex
from collections.abc import Iterator

FLAG_RE = re.compile(r"(?<![\w<-])--[A-Za-z0-9][A-Za-z0-9-]*")
# argparse guarantees two structural homes for a real option name: the `usage:`
# block, and the left column of an option row. Everything else in `--help` is
# prose -- `description=__doc__`, `epilog`, and every `help=` string. Scanning the
# whole render put `--cached`, `--run-checks`, `--body-file`, `--min-confidence`
# and `--mutation-coverage-command` into the accepted sets of parsers that reject
# them: a false green in exactly the direction the gate exists to close.
OPTION_ROW_RE = re.compile(r"^ {1,4}(-[^\s].*)$")
HELP_COLUMN_GAP_RE = re.compile(r"\s{2,}")
# `[--flag METAVAR]` / `[--flag=METAVAR]` in a usage line: the rendering that says
# this option consumes the following word.
USAGE_METAVAR_RE = re.compile(r"(--[A-Za-z0-9][A-Za-z0-9-]*)[ =]([^\s\]|]+)")
# argparse renders any choice set -- a subparsers action or a `choices=`
# positional -- as `{a,b,c}`. See `subcommand_choices` for why WHERE it is read
# from decides whether the read is right.
#
# The member class is "anything argparse can put between the braces", not the
# lowercase-hyphen shape this CLI happens to use. `subcommand_choices` matches
# the WHOLE group, so one member with an underscore or a capital made the match
# fail and blanked the entire parser -- silently, since an empty choice set reads
# as "this parser has no subcommands". A gate widened to REPORT `charness
# a retired command` as drift while its authority reader could not represent that
# name is the exact defect it was widened to fix, one level down.
CHOICES_RE = re.compile(r"\{([^\s,{}]+(?:,[^\s,{}]+)*)\}")
# A documented pipeline's later stage is a different command; its flags are not
# this script's to accept. Matched against whole shell tokens, never against raw
# text -- `--test-pressure "... 23.2% vs 22% gate; +2 tests"` carries a literal
# `;` inside a quoted value, and cutting there strands the quote.
SHELL_OPERATORS = {"|", "||", ";", "&&", "&", ">", ">>", "<"}
MAX_SUBCOMMAND_DEPTH = 4


def iter_option_declarations(help_text: str) -> Iterator[tuple[str, str]]:
    """Yield ``(source, text)`` for each structural home of an option declaration.

    argparse guarantees two: the `usage:` block, where every optional appears, and
    the invocation column of each option row, which is where `--help` itself lives
    since usage renders it as `[-h]`. The row is cut at the two-space gap argparse
    puts between an option and its description, so prose stays out. ``source`` is
    ``"usage"`` or ``"row"`` -- the two spell metavars differently, which is the
    only thing either reader below needs to tell them apart.
    """
    in_usage = False
    for line in help_text.splitlines():
        if line.startswith("usage:"):
            in_usage = True
        elif in_usage and not line.strip():
            in_usage = False
        if in_usage:
            yield "usage", line
            continue
        row = OPTION_ROW_RE.match(line)
        if row:
            yield "row", HELP_COLUMN_GAP_RE.split(row.group(1))[0]


def accepted_options(help_text: str) -> set[str]:
    """Option names argparse actually declares, read from structure not prose."""
    return {
        flag for _source, text in iter_option_declarations(help_text) for flag in FLAG_RE.findall(text)
    }


def subcommand_choices(help_text: str) -> set[str]:
    """The word choices this parser accepts in its next positional slot.

    Read from lines whose first non-space character is `{`, which is where
    argparse renders a choice set that OCCUPIES a positional slot -- the
    subparsers row, the usage line's own wrapped rendering of it, and a plain
    `choices=` positional. The last is deliberately included: argparse rejects an
    unlisted value with the same `invalid choice` error, so it is the same claim.

    What the leading `{` excludes is an OPTION's choices. `charness tool install
    --help` renders `[--recommendation-role {runtime,validation}]` in usage and
    `--recommendation-role {runtime,validation}` as an option row; a scan that
    reads either as a subcommand set gives `charness tool install` subcommands it
    does not have, and every documented `charness tool install <tool_id>` reports
    its tool id as invalid. Measured: three false positives on a clean tree. An
    option always renders its own name first, so its metavar can never be the
    first thing on the line.

    Anchoring on `{` rather than on the `positional arguments:` HEADER is what
    makes this correct for two shapes the header rule got wrong. `add_subparsers`
    only lands in `_positionals` when neither `title` nor `description` is
    passed; with either, argparse moves it to its own argument group under a
    different heading, and a header-keyed reader returns nothing for that parser
    -- silently unproven, no signal. And every argparse section title goes
    through `gettext`, so under a locale with a catalog installed a header-keyed
    reader returns nothing for EVERY parser at once. A brace is not translated.
    """
    choices: set[str] = set()
    for line in help_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        group = CHOICES_RE.match(stripped)
        if group:
            choices.update(group.group(1).split(","))
    return choices


def options_with_values(help_text: str) -> set[str]:
    """Options argparse renders with a metavar, i.e. the ones that consume the next word.

    Read from the same two structural homes as `accepted_options`: `[--flag META]`
    in the usage block and `--flag META, -f META` in an option row's invocation
    column. A `store_true` option renders with no metavar in either, so the split
    is exactly "does the following word belong to this option".
    """
    with_values: set[str] = set()
    for source, text in iter_option_declarations(help_text):
        if source == "usage":
            for match in USAGE_METAVAR_RE.finditer(text):
                if not match.group(2).startswith("-"):
                    with_values.add(match.group(1))
            continue
        for part in text.split(","):
            words = part.split()
            if len(words) > 1 and FLAG_RE.fullmatch(words[0]) and not words[1].startswith("-"):
                with_values.add(words[0])
    return with_values


def normalize_argument_token(token: str) -> str:
    """Strip the doc notation around a flag so a real documented flag is checked.

    `[--converted --durable-kind <kind>]` optional-brackets and `--engine=tokei`
    inline values are both live in this repo. Left unnormalized they fail
    `FLAG_RE.fullmatch`, get dropped, and -- worse than a miss -- the surrounding
    invocation still counts as validated, so the run over-claims coverage without
    even landing in the skipped tail.
    """
    return token.strip("[](),").split("=", 1)[0]


def split_arguments(tail: str) -> tuple[tuple[tuple[str, str], ...], list[str]]:
    """Return ``(ordered_tokens, flags)`` documented for one invocation.

    Tokenized with `shlex` rather than scanned with a regex because a quoted
    argument value legitimately contains flag-shaped text: `--verification "git
    diff --stat ..."` documents `--verification`, not `--stat`, and reading the
    latter as this script's flag is a false positive.

    ``ordered_tokens`` is a positional stream of ``(kind, token)`` pairs, kind
    being ``"flag"`` or ``"word"``. POSITION is kept rather than collapsed into a
    bag of bare words because argparse is not order-symmetric in either
    direction, measured on a two-level parser:

        demo --top x resolve --current y   -> ok
        demo resolve --current y --top x   -> error: unrecognized arguments
        demo --current y resolve           -> error: invalid choice 'y'

    A bag of words cannot express any of that; it also cannot tell a subcommand
    name from a flag VALUE that happens to equal one. Both were recorded as
    deferred findings (F7/F8) of the documented-command-flag critique for exactly
    this reason.
    """
    tokens = _tokenize(tail)
    for index, token in enumerate(tokens):
        if token in SHELL_OPERATORS:
            tokens = tokens[:index]
            break
    ordered: list[tuple[str, str]] = []
    flags: list[str] = []
    for raw in tokens:
        token = normalize_argument_token(raw)
        if FLAG_RE.fullmatch(token):
            ordered.append(("flag", token))
            flags.append(token)
        else:
            # EVERY non-flag token is kept, not just subcommand-shaped ones. Dropping
            # the others loses the positions value consumption counts on: in
            # `--repo-root . resolve-destination`, discarding `.` makes
            # `resolve-destination` look like the value of `--repo-root`, and the probe
            # never enters the subparser that owns the flags after it.
            ordered.append(("word", token))
    return tuple(ordered), list(dict.fromkeys(flags))


def _quoted_spans(carrier: str) -> list[tuple[int, int]]:
    """`(start, end)` of each quoted region, `end` being the closing quote's index.

    Scanned ONCE PER QUOTE CHARACTER and unioned, not as one shell-accurate state
    machine, because the thing that has to be right here is where a NESTED command's
    value ends -- and this repo's live spelling for that is single-inside-double:

        "python3 sample_mutation_files.py --test-command 'python3 run_standing_pytest.py'"

    A single-state scanner ignores the inner `'` while inside `"`, so the inner command
    inherits the OUTER span and its tail runs past its own closing quote, which is the
    exact false attribution this whole boundary exists to stop. Two passes give the
    inner region its own span, and `_enclosing_span` takes the SMALLEST match.

    Backslash escapes are skipped, so `\"` inside a JSON string does not close a span.
    An UNTERMINATED quote yields no span rather than running to end of line -- degrading
    to the old flat behavior is a false red at worst, while a runaway span would
    silently stop checking every command after it.
    """
    spans: list[tuple[int, int]] = []
    for quote in ("\"", "'"):
        open_at: int | None = None
        index = 0
        while index < len(carrier):
            char = carrier[index]
            if char == "\\":
                index += 2
                continue
            if char == quote:
                if open_at is None:
                    open_at = index + 1
                else:
                    spans.append((open_at, index))
                    open_at = None
            index += 1
    return spans


def _enclosing_span(spans: list[tuple[int, int]], position: int) -> tuple[int, int] | None:
    """The SMALLEST span containing `position`, so a nested region wins over its parent."""
    enclosing = [(start, end) for start, end in spans if start <= position < end]
    return min(enclosing, key=lambda span: span[1] - span[0]) if enclosing else None


def _command_position(carrier: str, match: "re.Match[str]") -> int:
    """The index of the command's own first character, skipping a consumed quote.

    `INVOCATION_RE`'s boundary classes include the quote, so a quoted command's match
    STARTS on the opening quote -- one character outside the span it is inside. Keying
    the enclosing test on `match.start()` was therefore false for every quoted command,
    which is the shape the test exists to catch. `match.end() - 1` is not the answer
    either: the same regex CONSUMES the closing quote when the quoted command carries
    no arguments, putting that index ON the closing quote, which `start <= i < end`
    also rejects. The first character of the command itself is inside the span in both
    shapes.
    """
    position = match.start()
    return position + 1 if position < len(carrier) and carrier[position] in "\"'" else position


def iter_invocation_tails(carrier: str, invocation_re) -> Iterator[tuple[re.Match[str], tuple[tuple[str, str], ...], list[str]]]:
    """Yield ``(match, ordered_tokens, flags)`` for each invocation in one carrier.

    One carrier can name two commands (`verify: python3 a.py --x, python3 b.py
    --y`). Reading each match to the END of the carrier hands the second
    command's arguments to the first -- a blocking false red on a correct doc,
    since `,` is not a shell operator for `split_arguments` to cut on. Cutting at
    the next match instead is the fix, and both documented-command gates need it.

    QUOTE-AWARE, because "the next match" is the wrong boundary when one command is
    the VALUE of another's flag. `check_changed_line_mutation_coverage.py ...
    --test-command "python3 run_standing_pytest.py --repo-root ." --write-fresh-marker`
    is one real invocation carrying another, and the flat rule got BOTH commands
    wrong at once: the outer one lost every flag written after `--test-command`, and
    the inner one was handed `--write-fresh-marker`, which it does not accept -- a
    blocking false red on a correct doc, which is what this repo's own command-surface gate hit.
    So a nested invocation's tail stops at its closing quote, and an outer
    invocation's tail skips past nested matches instead of ending at one.

    This is the quote-blind-splitter class a bounded review already found once in the
    command-dominance detector, surviving here in a second splitter. They stay
    separate readers on purpose -- that one cuts a chunk, this one cuts a tail.
    """
    spans = _quoted_spans(carrier)
    matches = list(invocation_re.finditer(carrier))
    positions = [_command_position(carrier, match) for match in matches]
    enclosings = [_enclosing_span(spans, position) for position in positions]

    def _compute_nested(index: int) -> tuple[int, int] | None:
        """The span that makes match `index` a VALUE of another command, if any.

        Being inside quotes is NOT enough, and assuming it was broke the repo's most
        common documented shape at once: `python3 "$SKILL_DIR/scripts/x.py" --flags`
        quotes the PATH, the regex consumes the closing quote, and cutting the tail at
        that quote dropped every flag from ~130 carriers -- a silent coverage loss in a
        blocking gate, which is worse than the false red it was fixing.

        What makes a command nested is that ANOTHER command precedes it from OUTSIDE
        the span it sits in. A quoted path has no such predecessor; a command written
        into `--test-command "..."` always does.
        """
        span = enclosings[index]
        if span is None:
            return None
        start, end = span
        earlier_outside = any(not (start <= positions[j] < end) for j in range(index))
        return span if earlier_outside else None

    # Computed ONCE per match, not per (outer, later) pair. The inner scan below asks
    # `is this nested?` about every following match, so calling the predicate there made
    # the pass quadratic in matches per carrier and pushed this gate's median past its
    # runtime budget -- a real regression measured by `check-runtime-budget`, not a
    # theoretical one, on a gate that reads ~1200 invocations.
    nested_spans = [_compute_nested(index) for index in range(len(matches))]

    for index, match in enumerate(matches):
        nested = nested_spans[index]
        if nested is not None:
            end = nested[1]
        else:
            end = len(carrier)
            for later in range(index + 1, len(matches)):
                # A nested match is not this command's boundary: it lives inside a
                # value this command owns, and cutting there is what dropped the
                # outer command's remaining flags.
                if nested_spans[later] is not None:
                    continue
                end = matches[later].start()
                break
        tokens, flags = split_arguments(carrier[match.end() : end])
        yield match, tokens, flags


def _tokenize(tail: str) -> list[str]:
    """`shlex` tokens, degrading to a whitespace split rather than crashing.

    `comments=True` drops a trailing `# ...` note, which this repo writes beside
    fenced commands -- otherwise its words become arguments, and a comment word
    that happens to name a subcommand re-routes the whole probe.

    `shlex` raises on an unclosed quote AND on a dangling backslash. Only the
    first has a quote-stripping repair, so the fallback chain ends at a plain
    split: a doc typo must not turn a blocking gate into a stack trace.
    """
    for candidate in (tail, tail.replace('"', " ").replace("'", " ")):
        try:
            return shlex.split(candidate, comments=True)
        except ValueError:
            continue
    return tail.split()


def resolve_subcommands(tokens, choices_for, values_for=None) -> tuple[str, ...]:
    """Walk the documented tokens down the subparser tree, keeping positions.

    Still order-tolerant about where the subcommand sits -- `resolve_adapter.py
    --repo-root . resolve-destination --current X` puts a top-level flag first --
    but a word is only a subcommand candidate if it is not already spoken for as
    the VALUE of the option in front of it. Without that, a documented
    `--accept-family record` mis-routes the whole probe into the `record`
    subparser and reports every sibling flag missing: a blocking false red on a
    correct doc, latent only while no option value happens to equal a subcommand
    name.

    ``values_for(path)`` names the options that take a value at that depth; when
    omitted no value consumption is assumed.
    """
    return _descend(tokens, choices_for, values_for, _select_tolerant)[0]


def walk_subcommands(tokens, choices_for, values_for=None) -> tuple[tuple[str, ...], str | None]:
    """Return ``(path, invalid)`` -- the same walk, read for what argparse REJECTS.

    `resolve_subcommands` answers "which parser owns this flag", so it is
    deliberately tolerant: it scans forward for a word that IS a choice and stops
    quietly when none is. That tolerance is exactly wrong for a caller asking
    whether a documented subcommand exists, because the token argparse would
    reject is the one it skips.

    This walk is strict in the one place argparse is: where a parser declares
    subcommands, the FIRST word not already spoken for as an option value is the
    subcommand slot, and argparse exits 2 on `invalid choice` if it is not one of
    them. ``invalid`` is that word, or None when the documented path is clean.

    Depth stops at a parser with no choices, which is what keeps a positional
    argument out of the verdict: `tool install external-tool` walks to
    `install`, sees no subparsers under it, and never judges `external-tool`.
    """
    return _descend(tokens, choices_for, values_for, _select_strict)


def _descend(tokens, choices_for, values_for, select) -> tuple[tuple[str, ...], str | None]:
    """Walk down the subparser tree, one depth per round, under a selection policy.

    The two public walks differ ONLY in `select`: which free word at this depth is
    the subcommand, and whether a word that is not a choice is a stop or a
    verdict. Everything else -- where the walk stops, how an option value is kept
    out of the candidate set, how the next depth's `choices_for` key is built --
    has to agree between them, or a flag gets attributed to a parser the
    subcommand gate says does not exist.

    `select(choices, free_words)` returns ``(index, invalid)``: an index to
    descend on, or ``(None, token)`` to end the walk with a verdict, or
    ``(None, None)`` to end it quietly.
    """
    path: list[str] = []
    start = 0
    for _ in range(MAX_SUBCOMMAND_DEPTH):
        choices = choices_for(tuple(path))
        if not choices:
            break
        free_words = iter_free_words(tokens, start, _takes_value(values_for, path))
        index, invalid = select(choices, free_words)
        if index is None:
            return tuple(path), invalid
        path.append(tokens[index][1])
        start = index + 1
    return tuple(path), None


def _select_tolerant(choices, free_words) -> tuple[int | None, None]:
    """First free word that IS a choice; a documented order this walk tolerates."""
    return next((index for index, token in free_words if token in choices), None), None


def _select_strict(choices, free_words) -> tuple[int | None, str | None]:
    """The subcommand SLOT: the first free word, which argparse requires be a choice."""
    head = next(free_words, None)
    if head is None:
        return None, None
    index, token = head
    return (index, None) if token in choices else (None, token)


def _takes_value(values_for, path: list[str]) -> frozenset[str] | set[str]:
    return values_for(tuple(path)) if values_for is not None else frozenset()


def iter_free_words(tokens, start: int, takes_value) -> Iterator[tuple[int, str]]:
    """Yield ``(index, token)`` for words not consumed as the value of a flag.

    The shared half of both walks above. A documented `--accept-family record`
    must not offer `record` as a subcommand candidate: latent only while no
    option value happens to equal a subcommand name, and a blocking false red on
    a correct doc once one does.
    """
    awaiting_value = False
    for index in range(start, len(tokens)):
        kind, token = tokens[index]
        if kind == "flag":
            awaiting_value = token in takes_value
            continue
        if awaiting_value:
            awaiting_value = False
            continue
        yield index, token


def subcommand_positions(tokens, path: tuple[str, ...]) -> list[int]:
    """Token index of each resolved subcommand, so flags can be scoped by position."""
    positions: list[int] = []
    cursor = 0
    for name in path:
        for index in range(cursor, len(tokens)):
            if tokens[index] == ("word", name):
                positions.append(index)
                cursor = index + 1
                break
        else:  # pragma: no cover - path words come from tokens by construction
            positions.append(len(tokens))
    return positions


def active_depth(tokens, path: tuple[str, ...], flag_index: int) -> int:
    """How many subcommands are already in effect where this flag is documented.

    This is the parser argparse would hand the flag to: everything after a
    subcommand token belongs to that subparser, and nothing before it does.
    """
    return sum(1 for position in subcommand_positions(tokens, path) if position < flag_index)
