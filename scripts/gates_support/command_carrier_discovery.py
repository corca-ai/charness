#!/usr/bin/env python3

"""Where this repo STORES an invocation, and what command strings each store yields.

Split out of `check_documented_command_flags.py`, which owns the question that
comes AFTER this one: given a command string, resolve which script it names,
probe that script's real argparse `--help`, and decide whether every flag written
beside it exists. This module owns the question before it -- given a file, which
spans of it could carry an invocation at all -- and the two halves share no
vocabulary. This one knows file shapes (fenced lines, backtick spans that wrap
across a prose line break, `.agents/` config lines, a command quoted inside one of
those lines, and the argv sequences Python source builds) and nothing about
argparse; the gate knows argparse and does not care which shape a string came
from.

That is a concept boundary, not a length boundary, which is what separates it
from the `_lib` spill the file-length cap exists to reject
(the `_lib` spill the file-length cap exists to reject). The seam is the one the widening itself drew.
This gate scanned markdown only, until the `--json` residue class proved markdown
is where a flag claim is WRITTEN and not where it is EXECUTED: seven live callers
passed a flag their callee had stopped accepting, and exactly ONE of them was in
a markdown doc -- the other six were a Python argv list, a `.agents/surfaces.json`
verify command, a `.agents/release-adapter.yaml` RELEASE-phase instruction, and a
`release_only` test. Every one exited 2 while every doc gate was green. Answering
that is what pushed the file over the cap, and every line it added answers "where
is a command stored", never "is this flag real". Nothing here would move back
into the gate to make the gate smaller; moving it back would put two jobs in one
file again.

Carrier scope -- the surfaces below are the places an invocation is STORED in
this repo, not the places it is described: markdown docs, `.agents/` command
configs, and the argv sequences Python source builds. The 2026-07-18 debug
artifact on the first round of this same class recorded the detection gap and
DECLINED to build the guard; the second round is what this scope answers.

The one markdown site among those seven was inside the gate's own scan scope and
still unseen, which is the second hole this module closes: `BACKTICK_CONTENT_RE`
excludes newlines and the fenced multi-line join only fires on a trailing
backslash, so a backtick span WRAPPING across a prose line break formed no
carrier at all -- not checked, and not counted in the `skipped` bucket that exists
to keep a pass from over-claiming coverage. Wrapped inline-code across a prose
line break is exactly that shape.

Non-claims. An argv sequence assembled through a variable, a loop, or a helper
that appends flags after the call site is not reconstructed here; only literal
elements of one list/tuple/call are. A command written as a single shell string
inside a Python variable is likewise invisible. This narrows a blind spot rather
than closing it, and the gate counts each unresolvable carrier as `skipped`
rather than waving it through.

Not to be confused with `portable_command_carrier.py`, which asks a consumer-side
question about EXPORTED skill packages (does the script a command names still
exist once the package is installed somewhere else). This module is repo-side and
stops at "here is a string that looks like a command".
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

# Bound in an order that deliberately does NOT match the order
# `check_documented_subcommands.py` binds the same three helpers in. That gate
# needs `check_doc_links`, `repo_file_listing` and `markdown_doc_scan` too, and
# binding them in its order makes a six-line identical block out of nothing but
# import lines -- past the clone detector's floor, and a new fixable duplicate
# family built from no logic at all. The gate this module was split out of
# carries a comment recording the same trap from the other direction.
_markdown_doc_scan = import_repo_module(__file__, "scripts.core.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
_check_doc_links = import_repo_module(__file__, "scripts.gates.check_doc_links")
BACKTICK_CONTENT_RE = _check_doc_links.BACKTICK_CONTENT_RE
iter_docs = _check_doc_links.iter_docs
_repo_file_listing = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files
RepoFileSnapshot = _repo_file_listing.RepoFileSnapshot

# Defined here rather than in the gate because this is the half that has to
# RECOGNIZE the name as a command token: a `charness tool doctor --json` in a test
# argv is a flag claim with no `.py` anywhere in it. The gate binds this one
# definition instead of repeating the literal.
CLI_NAME = "charness"
# Command-carrying configs. These store an invocation as a plain string the
# adapter/surface runner executes verbatim, so every line is a carrier -- there is
# no fence or backtick convention to key on, and the two live defects
# (`.agents/surfaces.json` verify commands, `.agents/release-adapter.yaml`
# checklist and probe lists) sit in both a JSON array and a YAML list.
COMMAND_CONFIG_GLOBS = (".agents/**/*.json", ".agents/**/*.yaml", ".agents/**/*.yml")
# Python sources that BUILD an argv sequence. Copied from
# `removed_name_consumers.py`'s scan scope, which already answers "where does this
# repo's executable Python live", plus the repo-root CLI itself. `tests/**` is in
# scope deliberately: a `release_only` test carried one of the seven live defects,
# and a test that cannot run is exactly as broken as a doc that cannot run.
ARGV_SOURCE_GLOBS = (
    CLI_NAME,
    "scripts/**/*.py",
    "tools/**/*.py",
    "skills/**/scripts/**/*.py",
    "tests/**/*.py",
)
# What an argv element that is not a literal renders as. Deliberately a plain word
# rather than a flag or a path: it has to hold the POSITION (a `str(repo_root)`
# after `--repo-root` is that option's value, and dropping it re-routes every
# later token) without being read as a flag claim or as the script itself.
ARGV_PLACEHOLDER = "<value>"
# Words that may legitimately precede the command in an argv sequence. Anything
# else before it means the sequence is not argv at all.
ARGV_INTERPRETER_WORDS = frozenset({"python", "python3", "bash", "sh", "zsh", "-u", "-E"})
# Node kinds an argv element is never one of. Rendering them as a placeholder
# without descending keeps the whole-repo scan from re-walking every nested
# literal once per enclosing node.
ARGV_OPAQUE_NODES = (
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Dict,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.Lambda,
)


def iter_scanned_files(
    root: Path, *, require_git: bool = False
) -> Iterator[tuple[Path, Iterator[tuple[int, str]]]]:
    """Yield ``(path, carriers)`` for every surface that STORES an invocation here.

    Three families, and the split is about where the command lives, not about file
    type: markdown describes it, `.agents/` configs execute it through an adapter
    runner, and Python source builds it as argv. Reading only the first is what
    let six of seven `--json` residues survive a clean gate run -- including a
    release-phase instruction and a script whose default mode exited 2.
    """
    snapshot = RepoFileSnapshot(root, require_git=require_git)
    for doc in iter_docs(root, require_git=require_git, snapshot=snapshot):
        yield doc, iter_command_carriers(doc)
    for config in iter_matching_repo_files(
        root, COMMAND_CONFIG_GLOBS, require_git=require_git, snapshot=snapshot
    ):
        yield config, iter_config_carriers(config)
    for source in iter_matching_repo_files(
        root, ARGV_SOURCE_GLOBS, require_git=require_git, snapshot=snapshot
    ):
        yield source, iter_argv_carriers(source)


def iter_command_carriers(doc: Path) -> Iterator[tuple[int, str]]:
    """Yield ``(lineno, text)`` spans that can carry a documented command.

    Fenced lines carry commands directly and join across a trailing backslash;
    prose carries them inside backtick spans, INCLUDING spans that wrap across a
    line break. The reported line is where the invocation *starts*, which is the
    line an author has to edit.

    The wrapping case is why prose is scanned with a tick state machine instead of
    `BACKTICK_CONTENT_RE.finditer(line)`. That regex excludes newlines, so a span
    opened on one prose line and closed on the next produced NO carrier from
    either line -- the invocation was not checked, and it did not land in the
    `skipped` bucket that keeps a pass from over-claiming coverage, so the run
    reported full coverage of a doc it had not read. `docs/deferred-decisions.md`
    wraps a `check_runtime_budget.py --repo-root . --json` instruction exactly
    that way, and the broken flag sat inside this gate's own scan scope unseen.

    A span is closed at a paragraph break, at a fence boundary, and at end of
    file, because markdown inline code cannot cross any of them. An UNCLOSED span
    is still yielded at that point rather than dropped: an odd backtick count is a
    doc typo, and an invocation is only recognized inside the yielded text by
    `INVOCATION_RE`, so yielding errs toward checking rather than toward a silent
    hole -- the failure mode this whole carrier rewrite exists to remove.
    """
    pending_lineno: int | None = None
    pending_text = ""
    span_lineno: int | None = None
    span_text = ""
    previous_lineno = 0
    for lineno, line, in_fence in iter_doc_lines(doc):
        # A continuation only joins the physically next line. `iter_doc_lines`
        # consumes fence delimiters silently, so without this a dangling `\` at
        # the end of one fenced block would swallow the first line of the next.
        if pending_lineno is not None and lineno != previous_lineno + 1:
            yield pending_lineno, pending_text
            pending_lineno = None
        if span_lineno is not None and (
            in_fence or lineno != previous_lineno + 1 or not line.strip()
        ):
            yield span_lineno, span_text
            span_lineno = None
        previous_lineno = lineno
        if not in_fence:
            parts = line.split("`")
            for index, part in enumerate(parts):
                if span_lineno is not None:
                    span_text = f"{span_text} {part.strip()}".strip()
                if index == len(parts) - 1:
                    # No closing tick on this line; carry the span to the next one.
                    break
                if span_lineno is not None:
                    yield span_lineno, span_text
                    span_lineno = None
                else:
                    span_lineno, span_text = lineno, ""
            continue
        if pending_lineno is None:
            pending_lineno, pending_text = lineno, line
        else:
            pending_text = f"{pending_text} {line.strip()}"
        if pending_text.rstrip().endswith("\\"):
            pending_text = pending_text.rstrip()[:-1]
            continue
        yield pending_lineno, pending_text
        pending_lineno = None
    if pending_lineno is not None:
        yield pending_lineno, pending_text
    if span_lineno is not None:
        yield span_lineno, span_text


def iter_config_carriers(path: Path) -> Iterator[tuple[int, str]]:
    """Yield the command-carrying spans of a `.agents/` config, one line at a time.

    A command stored in `verify_commands`, `fresh_checkout_probes`, or a release
    checklist is a string an adapter runner hands to a shell verbatim, so the line
    IS the carrier; `INVOCATION_RE` decides what in it is an invocation, and a line
    that merely lists a script path carries no flags and never reaches a verdict.

    A line that carries backticks is prose, not a command entry -- these adapters
    write adapter instruction items as sentences quoting the command -- so its
    backtick spans are the carriers instead of the whole line. Reading the whole
    line there drops the finding on a technicality: the closing backtick fuses
    onto the last flag (``--json` `` is not a flag token), so the RELEASE-phase
    `inventory_nose_clones.py --repo-root . --json` residue was matched, tokenized,
    and silently judged flagless.
    """
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        spans = [span.group(1) for span in BACKTICK_CONTENT_RE.finditer(line)]
        if spans:
            yield from ((lineno, span) for span in spans)
            continue
        yield lineno, line


def iter_argv_carriers(source: Path) -> Iterator[tuple[int, str]]:
    """Yield ``(lineno, text)`` for each ARGV SEQUENCE a Python file builds.

    The list/tuple handed to the subprocess runner, and the positional arguments of a
    test's `run_script(...)` helper, are the same flag claim a doc makes -- and
    the one this gate could not read. `draft_dup_ratchet_triage.py` builds two
    such lists, both passing a `--json` its callee had stopped accepting, and its
    DEFAULT mode exited 2 on a clean tree with every gate green.

    Every list, tuple, and call argument list is rendered; the ones that do not
    look like argv are dropped by `_render_argv`. Keyword arguments are not
    rendered: a subprocess runner call with `check=True` puts argv in a positional and
    configuration in the keywords, so reading keywords would add noise and no
    claim.
    """
    text = source.read_text(encoding="utf-8", errors="replace")
    # A necessary condition, checked before paying for a parse: a command token is
    # either a string constant ending in `.py` or the constant `charness`, and
    # neither can exist in a file whose TEXT contains neither substring. ~240 of
    # this repo's ~1300 in-scope Python files are excluded here, and this gate
    # carries a runtime budget it now has to fit while parsing all of them.
    # Non-claim: a path assembled by adjacent-literal concatenation across the dot
    # (`"scripts/x." "py"`) would slip through; that is not an idiom here.
    if ".py" not in text and CLI_NAME not in text:
        return
    try:
        tree = ast.parse(text)
    except SyntaxError:  # a generated or templated file is not this gate's to judge
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Tuple)):
            elements = node.elts
        elif isinstance(node, ast.Call):
            elements = node.args
        else:
            continue
        carrier = _render_argv(elements)
        if carrier is not None:
            yield node.lineno, carrier


def _render_argv(elements: list[ast.expr]) -> str | None:
    """One shell-shaped carrier for an argv sequence, or None when this is not argv.

    Three rules, each of which was a measured false positive on this tree before
    it existed. All three come from the same root fact: a Python list of strings
    is only an argv when the command sits at argv[0] and every later element is an
    ARGUMENT, and most string lists in this repo are neither.

    1. The command must be at the head, and the scan STOPS at the first element
       that could not precede it. Only placeholders and interpreter words may,
       because that is what `[sys.executable, "-u", script]` looks like. Without
       this rule, `run_script("scripts/gates/check_doc_links.py", ..., "--paths",
       "charness", ...)` read its `--paths` VALUE as a second command and reported
       five false flag drifts against the CLI. Stopping early is also what keeps
       this affordable: the gate reads every `ast.List`, `ast.Tuple` and
       `ast.Call` in `scripts/`, `skills/**/scripts/` and `tests/` -- ~130k
       sequences, of which ~3k are argv -- and the other 127k are rejected on
       their first or second element, before any subtree is inspected.
    2. `python3` is SYNTHESIZED in front of a `.py` head, because argv spells the
       interpreter as `sys.executable` -- a non-literal that renders as a
       placeholder, leaving `INVOCATION_RE` no prefix to anchor on and the whole
       list unread.
    3. A later element that is itself command-shaped is masked back to a
       placeholder. Nothing after argv[0] can be this command's name, and leaving
       it visible splits the tail: `iter_invocation_tails` cuts one invocation at
       the next match, so the real command lost every flag written after its own
       argument value.
    """
    rendered: list[str] = []
    head: int | None = None
    for index, element in enumerate(elements):
        token = _render_head_element(element)
        if _is_command_token(token):
            head = index
            break
        if token != ARGV_PLACEHOLDER and token not in ARGV_INTERPRETER_WORDS:
            return None
        rendered.append(token)
    if head is None:
        return None
    command = f"python3 {token}" if token.endswith(".py") else token
    # Rule 3 makes the tail cheap as well as correct: a tail element that is not a
    # literal is either a placeholder already or something rule 3 would mask into
    # one, so the tail never needs the subtree inspection the head does.
    tail = [_render_tail_element(element) for element in elements[head + 1 :]]
    return " ".join([command, *rendered, *tail])


def _is_command_token(token: str) -> bool:
    return token.endswith(".py") or token == CLI_NAME


def _render_head_element(element: ast.expr) -> str:
    """One argv element as one shell token, resolving a script path through the element.

    A non-literal element still carries the script path often enough to matter:
    `str(repo_root / "skills/public/quality/scripts/check_dup_ratchet.py")` is how
    this repo names a sibling script, and reading it as an opaque placeholder
    loses the only thing in the sequence worth resolving. So a single `.py` string
    constant anywhere in the element's subtree stands in for the element; two or
    more is ambiguous and stays a placeholder rather than a guess.
    """
    literal = _render_literal_element(element)
    if literal is not None:
        return literal
    # An argv element is never a container or a comprehension, so a `.py` constant
    # inside one is data this sequence passes along, not the command it runs.
    if isinstance(element, ARGV_OPAQUE_NODES):
        return ARGV_PLACEHOLDER
    scripts = {
        node.value
        for node in ast.walk(element)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.endswith(".py")
    }
    return scripts.pop() if len(scripts) == 1 else ARGV_PLACEHOLDER


def _render_tail_element(element: ast.expr) -> str:
    literal = _render_literal_element(element)
    if literal is None or _is_command_token(literal):
        return ARGV_PLACEHOLDER
    return literal


def _render_literal_element(element: ast.expr) -> str | None:
    """A string literal as one shell token, or None when the element is not one.

    A literal containing WHITESPACE renders as a placeholder, which is the rule
    that separates argv from the other thing a list of strings is in this repo:
    the lines of a generated shell script or YAML fixture. An argv element with a
    space is always a value (`--message "two words"`), never a command or a flag,
    so masking it loses no claim -- while reading it as text spliced three
    fixture-built shell scripts into their neighbours and reported nine flag
    drifts that no runnable command carried.
    """
    if not (isinstance(element, ast.Constant) and isinstance(element.value, str)):
        return None
    value = element.value
    return ARGV_PLACEHOLDER if not value or any(char.isspace() for char in value) else value
