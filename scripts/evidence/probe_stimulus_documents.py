#!/usr/bin/env python3
"""How to READ an adapter document out of a probe record's `## Stimulus`, and how to ablate it.

Split from ``probe_stimulus_replay`` on the concept boundary its siblings already use:
``probe_record_parse`` says of its neighbour that "that module answers 'how do I read a
field out of markdown', and this one answers 'what must the body carry'". Same split, same
reason. This half answers "what document does this shell block write, and what does it
declare"; ``probe_stimulus_replay`` answers "does the reader honor those declarations".

Load-bearing here rather than cosmetic: every defect two bounded review rounds found in the
extraction and text-surgery layer belongs to THIS concern -- six unmatched heredoc
spellings, a `.yml` name no reader opens, a write location no reader looks in, YAML
document markers parsed as declarations, a variant emitted as a flow sequence the reader
cannot parse, a variant that suffixed an inline comment instead of the value, a
block-scalar header whose variant makes the parser raise, and an indent measured with
`str.isspace()` where `adapter_lib` counts spaces. None of them belongs to "is this
declaration honored".

``probe_stimulus_replay`` re-exports this module's public names, so consumers keep one
import site and nothing outside had to learn about the split.

BLIND CLASS of this half specifically: it is a shell-line grammar and a text editor. It
never runs a resolver and knows nothing about verdicts. `with_mutated_value` returns None
whenever it cannot vary a declaration HONESTLY -- a block parent, a block-scalar header --
and the caller must treat that as "no variant was obtained", never as a verdict.
``probe_stimulus_replay``'s module docstring carries the full list.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")

# `cat > <path> <<'DELIM'`. Deliberately WIDE, because a heredoc this regex misses is
# dropped silently and the record then renders `not-configured`, which does not demote --
# so every shape it fails to match is an escape hatch, and a round-1 review enumerated six
# of them. Quoted and unquoted paths, `<<-`, hyphenated delimiters and a trailing comment
# are all accepted now. The quote around the DELIMITER stays significant: unquoted means
# the shell expands the body, so the document on disk is not the document in the record.
_HEREDOC_RE = re.compile(
    r"""^\s*cat\s*>\s*(?P<pathquote>['"]?)(?P<path>[^'"\s]+)(?P=pathquote)\s*"""
    r"""<<-?\s*(?P<quote>['"]?)(?P<delim>[\w-]+)(?P=quote)\s*(?:\#.*)?$"""
)
# `.yaml` ONLY, matching what every reader in this repo opens. Accepting `.yml` here made a
# spelling no resolver reads resolve anyway, and it was refused only by the accident that
# the sandbox then found no file and every declaration read inert -- a right answer with a
# reason that names the wrong defect.
_ADAPTER_NAME_RE = re.compile(r"^(?P<skill>[A-Za-z0-9_-]+)-adapter\.yaml$")
# A heredoc target that LOOKS like an adapter but does not resolve to one. Matched so the
# miss becomes a refusal instead of a silent drop: `${s}-adapter.yaml`, `<skill>-adapter.yaml`,
# `quality-adapter.yml` and `Quality-Adapter.YAML` all read as adapters in the record's prose
# and none reaches a reader. The second alternation this replaced (`adapter\.yml`) was wholly
# subsumed by the first and matched nothing the first did not.
_ADAPTER_ISH_RE = re.compile(r"adapter\.ya?ml", re.IGNORECASE)
# A `cat` line that names an adapter document and does NOT match `_HEREDOC_RE`. Round 2
# enumerated six more spellings the widened regex still misses -- a redirect after the
# heredoc, a `$ ` transcript prompt, a trailing `&& echo ok`, `<<\DELIM`, a path containing
# a space, `cat >>`. Widening again would just move the boundary, so the boundary itself
# reports: an unmatched `cat` line mentioning an adapter is refused, not dropped.
_CAT_LINE_RE = re.compile(r"^\s*\$?\s*cat\b.*adapter\.ya?ml", re.IGNORECASE)
# A skill directory name. Template placeholders and shell expansions fail this deliberately:
# a stimulus nobody can paste is not a reproduction step, which is the whole subject of #674.
_SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_VERSION_LINE_RE = re.compile(r"^version\s*:.*$", re.MULTILINE)
# The ONE directory every adapter reader in this repo looks in. Checked because the module
# writes the document to `.agents/<basename>` in its sandbox, so a stimulus that wrote it
# anywhere else describes a run where NOTHING was read -- and replaying it at the readable
# path would report the declarations live and pass the record.
_ADAPTER_DIRECTORY = ".agents"
_COMMENT_LINE_RE = re.compile(r"^\s*#")
# `adapter_lib._DOCUMENT_MARKERS`, which that parser skips WITHOUT recording as
# uninterpreted. Named here rather than imported because this module is loaded from a
# skill bootstrap in some layouts, and the literal is pinned by test.
_DOCUMENT_MARKERS = frozenset({"---", "..."})
_INT_RE = re.compile(r"-?\d+")
_FLOAT_RE = re.compile(r"-?\d+\.\d+")
_BLOCK_SCALAR_PREFIXES = ("|", ">")

def extract_adapter_documents(stimulus: str) -> list[dict]:
    """Every adapter document the stimulus block writes, in order.

    Returns ``{"filename", "skill", "text", "expanded"}`` per document. Parsing the shell
    rather than executing it is the point: the record's readers are humans and this module,
    and neither should have to run an arbitrary script to learn what the stimulus declares.
    """
    documents: list[dict] = []
    lines = stimulus.splitlines()
    index = 0
    while index < len(lines):
        match = _HEREDOC_RE.match(lines[index])
        if match is None:
            if _CAT_LINE_RE.match(lines[index]):
                documents.append({
                    "filename": lines[index].strip(), "skill": None, "text": "",
                    "expanded": False, "directory": _ADAPTER_DIRECTORY, "unreadable_command": True,
                })
            index += 1
            continue
        delimiter = match.group("delim")
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != delimiter:
            body.append(lines[index])
            index += 1
        index += 1
        written_to = PurePosixPath(match.group("path"))
        filename = written_to.name
        name_match = _ADAPTER_NAME_RE.match(filename)
        if name_match is None:
            # A target that looks like an adapter but does not resolve to one is REPORTED,
            # not dropped. Dropping it renders `not-configured`, which does not demote the
            # record -- so silence here is the cheapest escape in the whole module.
            if _ADAPTER_ISH_RE.search(filename):
                documents.append({"filename": filename, "skill": None, "text": "", "expanded": False, "directory": written_to.parent.name})
            continue
        documents.append(
            {
                "filename": filename,
                "skill": name_match.group("skill"),
                "text": "\n".join(body) + "\n",
                # An unquoted heredoc delimiter lets the shell expand `$VAR` and backticks
                # in the body, so what lands on disk is not what the record shows.
                "expanded": match.group("quote") == "",
                # The DIRECTORY the stimulus wrote to, which decides whether any reader saw
                # the document at all. This module resolves from `.agents/`, so without this
                # a stimulus that wrote elsewhere -- a run in which nothing was read --
                # would have its declarations replayed at the one path that does read them.
                "directory": written_to.parent.name,
            }
        )
    return documents


def declaration_lines(text: str) -> list[dict]:
    """Every line of the document that DECLARES something, with its own indent.

    PER LINE, not per top-level key, and a round-1 bounded review is why. Ablating only
    the outer mapping's keys worked on the four measured records by accident of their
    content: each dead declaration happened to be the sole entry under its key, so the key
    collapsed to its default and the ablation saw it. Add one honest sibling and the dead
    one disappears -- appending `id: probe-one` (the ORIGINAL defect key) to the corrected
    quality probe leaves `startup_probes` live, so the top-level ablation reports the
    document clean while the record's control still cannot fail. The reviewer built that
    input; per-line ablation is the answer to it.

    The version line is excluded because `with_supported_version` already owns it: it is
    the arm being controlled FOR, not a declaration under test. Comments and blank lines
    declare nothing.
    """
    declarations: list[dict] = []
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        # DOCUMENT MARKERS ARE NOT DECLARATIONS. `adapter_lib._parse_block` goes out of its
        # way to accept `---`/`...` without recording them as uninterpreted, because editors
        # and templates emit them by default -- and per-line ablation then called `---` a
        # declaration no value of which changes anything, refusing legal YAML with a
        # nonsensical reason. Worse, a document that is `---` plus a version was refused for
        # the marker instead of for declaring nothing, hiding the correct diagnosis of the
        # maximal defect. Per-KEY ablation could not see `---`; per-line can, so the repair
        # for the nesting hole opened this one.
        if not stripped or stripped in _DOCUMENT_MARKERS:
            continue
        if _COMMENT_LINE_RE.match(line) or _VERSION_LINE_RE.match(line):
            continue
        declarations.append({"index": index, "indent": _indent_of(line), "label": stripped})
    return declarations


def _indent_of(line: str) -> int:
    """Indent width in SPACES ONLY, matching `adapter_lib._line_shape`.

    Not `str.isspace()`. A tab-led line is a top-level key to this repo's parser and an
    indented continuation to anything that asks `isspace()`, so the two disagreed about
    what a block contains -- which made an honestly declared tab-indented key read as
    inert, a false refusal on a proof surface.
    """
    return len(line) - len(line.lstrip(" "))


def uninterpreted_lines(text: str) -> list[str]:
    """The operator-facing warning for every line the reader could not interpret."""
    _parsed, sink = _adapter_lib.load_yaml_report(text)
    return _adapter_lib.uninterpreted_warnings(sink)


def with_supported_version(text: str) -> str:
    """The same document with its `version` made speakable, so the control arm can run.

    A document that declares no version is returned unchanged: there is nothing to make
    speakable, and inventing one would resolve a document the record never wrote.
    """
    return _VERSION_LINE_RE.sub(
        f"version: {_adapter_lib.SUPPORTED_ADAPTER_VERSION}", text, count=1
    )


_MUTATION_TOKEN = "probe-mutation"
# The two reasons a deletion can come back unchanged, kept as distinct words because only
# one of them is a defect. `_UNREAD` refuses; `_RESTATED_DEFAULT` is reported.
_UNREAD = "unread"
_RESTATED_DEFAULT = "restated-default"


def with_mutated_value(text: str, index: int) -> str | None:
    """The document with one declaration's VALUE varied, or None when it owns no scalar.

    This is the discriminator between the two reasons an ablation can come back unchanged,
    and per-line ablation needs it or it refuses honest records. `exemption_globs: []` in
    the prompt-bulk record deletes without effect because the declared value IS the
    reader's default -- a no-op restatement, not a wrong shape. `id: probe-one` deletes
    without effect because no reader reads the key at all. Varying the value separates
    them: the first changes the payload, the second cannot.
    """
    lines = text.splitlines()
    line = lines[index]
    head, separator, value = line.partition(":")
    if not separator:
        stripped = line.strip()
        if not stripped.startswith("- "):
            return None
        item_head, item = line.split("- ", 1)
        varied = _varied_scalar(item.strip())
        if varied is None:
            return None
        replacement = [f"{item_head}- {varied}"]
    else:
        value = value.strip()
        if not value:
            # A block parent owns no scalar to vary. Its liveness is decided by its
            # children, and if deleting the whole block changed nothing then nothing under
            # it was read -- the unread verdict, reached without needing a variant.
            return None
        replacement = _mutated_lines(head, value)
        if replacement is None:
            return None
    return "\n".join(lines[:index] + replacement + lines[index + 1 :]) + "\n"


def _mutated_lines(head: str, value: str) -> list[str] | None:
    """The declaration re-stated with a different value, IN A SHAPE THIS READER PARSES.

    The first cut varied `[]` to the flow sequence `["probe-mutation"]` and measured
    nothing: `adapter_lib._mapping_value` renders a flow sequence as a plain string, the
    validator drops it, and the varied payload came back identical to the whole one -- so
    every empty-list declaration was reported UNREAD when it was merely restating a
    default. The discriminator emitted the exact malformed shape it exists to detect,
    which is this corpus's own defect class reproduced one level up.

    Round 2 found the same class twice more in the repair. The INLINE COMMENT was being
    suffixed instead of the value (`40  # widened` -> `40  # widened-probe-mutation`), and
    `adapter_lib.strip_inline_comment` removes it again -- so the variant was a literal
    no-op for every commented scalar, and every restated default carrying a comment was
    refused as unread. And varying a BLOCK-SCALAR HEADER (`|`, `>`) produced `|-probe-mutation`,
    which `_parse_block_scalar` REFUSES: the resolver tracebacked and the declaration was
    reported "never settled". Neither shape can be varied honestly, so the header returns
    None and the comment is carried across untouched.
    """
    comment_start = _adapter_lib.inline_comment_start(value)
    body = value[:comment_start].strip() if comment_start is not None else value
    trailer = f"  {value[comment_start:].strip()}" if comment_start is not None else ""
    indent = " " * (_indent_of(head) + 2)
    if body == "[]":
        return [f"{head}:{trailer}", f"{indent}- {_MUTATION_TOKEN}"]
    if body == "{}":
        return [f"{head}:{trailer}", f"{indent}{_MUTATION_TOKEN}: 1"]
    varied = _varied_scalar(body)
    return None if varied is None else [f"{head}: {varied}{trailer}"]


def _varied_scalar(body: str) -> str | None:
    """A value of the SAME TYPE, so the reader's own type check does not reject the variant.

    Suffixing everything was the round-2 finding: `strict: false` became the string
    `false-probe-mutation`, `margin: 2.0` became a string, and `"docs/x"` kept its quotes
    INSIDE the suffixed text so `_coerce_scalar` no longer saw a quoted scalar. Each is
    rejected by its validator, which falls back to the reader's default -- so a declaration
    that merely restated that default varied to the same payload and was refused as unread,
    the exact class this discriminator exists to prevent, for the type-checked half of the
    fields.

    WHAT THIS STILL CANNOT DO, and it is the honest residual: a field the reader constrains
    to an ENUM has no type-preserving variant this module can compute -- it would have to
    know the member set. `class: standing` varies to a rejected value. Today no enum field
    in this corpus has a DEFAULT (absence is an error), so the ablation moves the payload
    and returns live before any variant runs; a future enum field with a default would be
    refused wrongly, and `_declaration_verdict`'s caller would need the member set to fix it.
    """
    if body.startswith(_BLOCK_SCALAR_PREFIXES):
        # A BLOCK-SCALAR HEADER cannot be varied at all: `|-probe-mutation` fails
        # `SUPPORTED_BLOCK_SCALAR_RE`, so `_parse_block_scalar` RAISES and the resolver
        # tracebacks -- the declaration then reports "never settled" instead of a verdict.
        # Lives here rather than in `_mutated_lines` so a sequence item (`- |`) is covered
        # by the same rule; keyed only there, the item path had no answer for it.
        return None
    lowered = body.lower()
    if lowered in ("true", "false"):
        return "false" if lowered == "true" else "true"
    if _INT_RE.fullmatch(body):
        return str(int(body) + 1)
    if _FLOAT_RE.fullmatch(body):
        return str(float(body) + 1)
    if len(body) >= 2 and body[0] == body[-1] and body[0] in "\"'":
        return f"{body[0]}{body[1:-1]}-{_MUTATION_TOKEN}{body[0]}"
    return f"{body}-{_MUTATION_TOKEN}"


def without_line(text: str, index: int) -> str:
    """The document with one declaration line, and everything nested under it, removed.

    Text-level rather than parse-and-re-render, because re-rendering would silently repair
    exactly the malformed shapes this module exists to detect -- a flow sequence would come
    back as a block sequence and the inert declaration would resolve as honored.
    """
    lines = text.splitlines()
    indent = _indent_of(lines[index])
    end = index + 1
    while end < len(lines) and (not lines[end].strip() or _indent_of(lines[end]) > indent):
        end += 1
    return "\n".join(lines[:index] + lines[end:]) + "\n"
