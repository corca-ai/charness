#!/usr/bin/env python3

r"""Documented `charness <subcommand>` invocations must name subcommands argparse declares.

`check_documented_command_flags.py` closed the rung below this one for scripts --
a documented flag must be a flag the named script's own argparse accepts, read
from `--help` rather than from a literal -- and it argues the general case in its
own words: "an argparse contract rather than another literal". It stops one rung
short, because the CLI's SUBCOMMAND names were never derived from anything. The
repo's only guard over them was `domain_language_contract`'s hand-declared
`deprecated_aliases` list, and a hand-declared list cannot catch a rename nobody
declared -- which is the only failure that actually reaches a consumer.

Derivation catches it and needs no list. `charness --help` is the authority;
this gate asks argparse what it would reject.

Scope, stated in both directions because the deletion this enables depends on
it. The FILE set is a superset of the retired contract's: every one of its
`surface_globs` (README, `docs/**`, `skills/public/**`, `skills/shared/**`,
`charness`, `scripts/**/*.py`) plus `specs/**/*.md`, whose specdown fences are
executed rather than read.

The CONTENT read inside those files is NARROWER, and that is a real trade, not
an oversight. The retired contract matched three literal strings case-insensitively
anywhere in the raw bytes of a file. This gate reads only carriers -- a shell
fence line, a prose backtick span, a backtick span inside a runtime string --
because it judges any subcommand rather than three known strings, and bare prose
is where an author writes the product name. Measured on this tree: scanning all
prose gives 72 non-subcommand hits across 36 tokens (`charness itself`,
`charness ships`, ...), code contexts give 27 across 10, and the carrier rule
gives 3.

What that costs, exactly: those three retired strings written in a Python
comment, in a non-operator-facing docstring, or in unbackticked markdown prose
are no longer caught by anything. What it buys: every OTHER rename, in every
carrier, without anyone declaring it -- which is the failure that actually
reaches a consumer, and the one a declared list structurally cannot see.

floor-addition-restraint: blocking, not advisory, and it REPLACES a capability
rather than adding one. The 2026-08-11 operator ruling binds the order -- this
check landed and worked BEFORE `domain_language_contract` was deleted, so no
interval existed in which a retired command could ship unchallenged.

Three limits on the word "replaces", all of them real:

1. IN THIS REPO ONLY. The retired validator lived inside the portable quality
   skill package (`$SKILL_DIR/scripts/`), so a consumer could run it through the
   quality catalog. This gate lives in repo `scripts/` and is not in that
   package. It cannot be: it derives from `charness --help`, and a consumer's CLI
   is not charness. A consuming repo wanting this guarantee needs the same
   derivation against its own CLI. For consumers the capability is REMOVED, not
   replaced -- say that in the release note rather than letting "replaced" carry
   it.
2. ONE TERM OF THREE. The retired contract declared `external-tool-cli` (the
   retired CLI names, which this gate subsumes), plus `support-capability-taxonomy`
   and `repo-initialization-skill` -- pure vocabulary with no invocation in them,
   which this gate is structurally incapable of seeing. The ruling routed those
   to #599 deliberately; they are not lost, they are moved.
3. NO DECLARED-SCOPE REFUSALS. The retired validator also refused a term whose
   declared `surface_globs` matched no file, a `surface_globs: []`, and a
   non-mapping `terms` entry -- "a clean verdict over an unread scope is not a
   clean verdict". That whole class disappears here by construction, because this
   gate has no operator-declared scope to get wrong. Correct for this repo; a
   removed affordance for a consumer.

On the ruling's sizing. It recorded (`charness-artifacts/spec/
2026-08-11-six-operator-rulings.md:168`) that the check "finds two live defects
on its first run", and its own non-claims already flagged that no consumer repo
was observed. Executing it split that two into one and one.

`charness verify` was real, and deeper than the doc line the measurement saw:
`DEFAULT_CANONICAL_GATE_PATTERNS` in `ci_local_gate_parity_lib.py` carried
`\bcharness\s+verify\b`, and the doc was faithfully describing it. Two
independent reads -- the live CLI and a stale in-tree snapshot under `mutants/`
-- plus the retirement list itself show no such subcommand, so the alternative
was dead; whether an older installed consumer copy ever had one is unobservable
here, exactly as the ruling said.

`charness propose` was a FALSE POSITIVE. It names the stage inside the marker
`# >>> mutation_testing (charness propose) >>>` -- a literal
`propose_mutation_testing.py` writes into consumer adapters AND uses as its
idempotence key, so treating it as drift would have bought a duplicate
`mutation_testing:` block in a consumer's config to satisfy a gate. It is
excluded by the comment rule in `iter_command_carriers`, not by a carve-out in
`INVOCATION_RE`; the first design tried the carve-out and blinded the gate to
every subshell-leading invocation.
"""

from __future__ import annotations

import argparse
import ast
import re
from collections import Counter
from collections.abc import Iterator
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_argparse_surface = import_repo_module(__file__, "scripts.argparse_surface_lib")
iter_invocation_tails = _argparse_surface.iter_invocation_tails
walk_subcommands = _argparse_surface.walk_subcommands
MAX_SUBCOMMAND_DEPTH = _argparse_surface.MAX_SUBCOMMAND_DEPTH
_argparse_help_probe = import_repo_module(__file__, "scripts.argparse_help_probe")
HelpProbe = _argparse_help_probe.HelpProbe
HelpRunner = _argparse_help_probe.HelpRunner
_check_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
iter_docs = _check_doc_links.iter_docs
BACKTICK_CONTENT_RE = _check_doc_links.BACKTICK_CONTENT_RE
_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files
RepoFileSnapshot = _repo_file_listing.RepoFileSnapshot
_markdown_doc_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")
iter_doc_lines_with_language = _markdown_doc_scan.iter_doc_lines_with_language
_gate_report_emit = import_repo_module(__file__, "scripts.gate_report_emit")
# Findings still go to stderr so a green run's stdout stays quotable; only the
# FORMAT changed here, never the stream this gate writes a verdict on.
emit_findings_report = _gate_report_emit.emit_findings_report

CLI_NAME = "charness"
# The info strings that mean "the lines below are shell commands, and `#` starts
# a comment". That second half is load-bearing, which is why `console`,
# `shell-session`, and `sh-session` are NOT here even though they are ordinary
# spellings: in a session transcript `#` is the ROOT PROMPT, so the comment rule
# below would silently skip every privileged invocation in the fence. Adding them
# speculatively would have widened the scope and blinded it in the same line.
# `run:shell` is specdown's, and those fences are EXECUTED -- the strongest
# carrier in the tree. An undeclared fence (`""`) stays out: this repo's bare
# fences carry sample output, as do `text`/`markdown`/`json`/`yaml`.
SHELL_FENCE_LANGUAGES = frozenset({"bash", "run:shell", "sh", "shell", "zsh"})
# `charness` followed by a word. A leading boundary class keeps the tail of
# another word out. `--help`, a bare `charness`, and a `<placeholder>` do not
# match by construction: none of them is a subcommand claim to check. A `./`
# or interpreter prefix is allowed because this repo documents both the installed
# `charness ...` and the source-tree `python3 charness ...`.
#
# `(` IS a boundary. An earlier design excluded it to keep the marker
# `# >>> mutation_testing (charness propose) >>>` from reading as an invocation,
# and justified that as "shell's own distinction between `(` and `$(`" -- which
# is backwards: `(cmd)` opens a subshell, so `(charness verify --repo-root .)`
# is an ordinary invocation and excluding `(` silently blinded the gate to every
# subshell-leading one. A bounded review caught it. The marker is excluded by
# the comment rule in `iter_command_carriers` instead, which is where it belongs:
# the marker starts with `#`.
INVOCATION_RE = re.compile(
    rf"(?:^|[\s|(\"'=&;])(?:(?:python3?|bash|sh)\s+|\./)?{CLI_NAME}\s+(?=[A-Za-z0-9])"
)
# A token that COULD be a single `add_parser(name)` argument. Anything else is
# shorthand for several commands -- `charness tool install/update/doctor` names
# three in one prose span -- or a `<placeholder>` for an argument value; those are
# counted as skipped, never guessed at.
#
# Deliberately wider than the names this CLI actually declares (all lowercase and
# hyphenated). Narrowing it to that shape routes the two most likely REAL drift
# forms into the skipped bucket instead of reporting them: `charness
# a retired command`, written from the code identifier rather than the
# hyphenated command, and `charness Doctor`. Both are single tokens argparse
# rejects, so both are this gate's to report -- a skip bucket that swallows the
# likeliest defect is a gate that passes on it.
SUBCOMMAND_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
# specdown specs are markdown, and `check_doc_links.DOC_GLOBS` does not reach
# them. Their fences are RUN, so drift there breaks a proof rather than a doc.
SPEC_DOC_GLOBS = ("specs/**/*.md",)
# The retired `domain_language_contract`'s own non-markdown `surface_globs`,
# carried over verbatim so the replacement is a superset of what it scanned.
SOURCE_GLOBS = (CLI_NAME, "scripts/**/*.py", "tools/**/*.py")


def iter_command_carriers(doc: Path) -> Iterator[tuple[int, str]]:
    """Yield ``(lineno, text)`` spans in a MARKDOWN doc that can carry an invocation.

    Two carriers, matching where an author writes a runnable command: a line
    inside a shell-language fence, and a backtick span in prose. A fenced line
    whose first non-space character is `#` is a shell comment in every language
    this scans -- the one that triggered the rule reads `# charness ...` inside a
    `bash` fence and is narrating, not invoking.

    A backtick span takes the same comment rule, and that is what excludes
    `` `# >>> mutation_testing (charness propose) >>>` `` -- a marker naming the
    STAGE that wrote an adapter block, quoted in prose. Excluding it by carving
    `(` out of the invocation boundary instead, as an earlier design did, blinded
    the gate to every subshell-leading invocation to spare one comment.
    """
    for lineno, line, language in iter_doc_lines_with_language(doc):
        if language is None:
            for span in BACKTICK_CONTENT_RE.finditer(line):
                if not span.group(1).lstrip().startswith("#"):
                    yield lineno, span.group(1)
            continue
        if language not in SHELL_FENCE_LANGUAGES or line.lstrip().startswith("#"):
            continue
        yield lineno, line


def iter_source_carriers(source: Path) -> Iterator[tuple[int, str]]:
    """Yield backtick spans from the RUNTIME string literals of a Python source file.

    The retired `domain_language_contract` scanned `charness` and
    `scripts/**/*.py` alongside the markdown surfaces, so a replacement that read
    markdown only would delete coverage rather than replace it.

    Backticks are the carrier for the same reason they are in prose: this repo
    writes operator-facing next actions as ``f"Run `charness capability init
    ...` to scaffold"``, so the convention that marks a command in a sentence
    marks it inside a string too. 35 such spans are live in `charness` alone, and
    a rename turns every one into a lie the CLI prints at runtime.

    Docstrings and comments are excluded, which is the whole reason this parses
    rather than scans lines. A docstring is prose ABOUT the code -- this module's
    own explains why `charness verify` was a defect -- while a runtime string is
    text handed to an operator. A line scan cannot tell them apart and reports
    every design note that quotes a retired name, which teaches authors to stop
    quoting. Comments never reach the AST at all.

    The MODULE docstring is the exception, and it has to be derived rather than
    assumed: 62 scripts here pass `description=__doc__` to their parser, so for
    those files the module docstring is exactly what argparse prints on `--help`
    -- the same operator-facing channel this gate's own probe reads. Excluding it
    on the flat rule "a docstring is prose" would answer "nothing here" for the
    one docstring that is not.
    """
    try:
        tree = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:  # a generated or templated file is not this gate's to judge
        return
    for lineno, text in _iter_runtime_strings(tree):
        for span in BACKTICK_CONTENT_RE.finditer(text):
            yield lineno, span.group(1)


def _reads_module_docstring(tree: ast.Module) -> bool:
    """Whether this module hands `__doc__` to something -- `description=__doc__`.

    Derived, not declared: the question is whether the module docstring reaches
    an operator, and the module itself already answers it.
    """
    return any(
        isinstance(node, ast.Name) and node.id == "__doc__" and isinstance(node.ctx, ast.Load)
        for node in ast.walk(tree)
    )


def _iter_runtime_strings(tree: ast.Module) -> Iterator[tuple[int, str]]:
    """Yield ``(lineno, text)`` for every string literal that is not a docstring.

    An f-string is reassembled from its literal parts with each `{...}` replaced
    by a placeholder, because the span this gate reads is routinely split by one:
    ``f"Run `charness task status {task_id}`"`` puts the subcommand
    before the placeholder and the closing backtick after it, so a reader that
    only sees the parts separately never closes the span.
    """
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    }
    if _reads_module_docstring(tree) and isinstance(tree.body[0], ast.Expr):
        docstrings.discard(id(tree.body[0].value))
    joined: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.JoinedStr):
            continue
        joined.update(id(part) for part in node.values)
        yield (
            node.lineno,
            "".join(
                part.value
                if isinstance(part, ast.Constant) and isinstance(part.value, str)
                else " <value> "
                for part in node.values
            ),
        )
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
            and id(node) not in joined
        ):
            yield node.lineno, node.value


def iter_documented_invocations(
    carriers: Iterator[tuple[int, str]],
) -> Iterator[tuple[int, tuple[tuple[str, str], ...]]]:
    """Yield ``(lineno, ordered_tokens)`` for each documented `charness` invocation."""
    for lineno, carrier in carriers:
        for _match, tokens, _flags in iter_invocation_tails(carrier, INVOCATION_RE):
            if tokens:
                yield lineno, tokens


def _choices_for(probe: HelpProbe):
    return lambda path: probe.subcommand_choices((CLI_NAME, *path))


def _values_for(probe: HelpProbe):
    return lambda path: probe.options_with_values((CLI_NAME, *path))


def _walk_all(
    probe: HelpProbe, invocations: list[tuple]
) -> list[tuple[tuple[str, ...], str | None]]:
    """Walk every invocation down the subcommand tree, one probe round per depth.

    An unprobed depth answers "no subcommands here", so each round descends
    exactly one level and the next round primes what it revealed. The loop runs
    until nothing moves rather than a fixed count, which is what keeps a shallow
    tree from paying for the deepest one.
    """
    walked: list[tuple[tuple[str, ...], str | None]] = [((), None) for _ in invocations]
    for _ in range(MAX_SUBCOMMAND_DEPTH + 1):
        probe.prime({(CLI_NAME, *path) for path, _ in walked})
        changed = False
        for index, (_doc, _lineno, tokens) in enumerate(invocations):
            result = walk_subcommands(tokens, _choices_for(probe), _values_for(probe))
            if result != walked[index]:
                walked[index] = result
                changed = True
        if not changed:
            break
    return walked


def iter_scanned_files(
    root: Path, *, require_git: bool = False
) -> Iterator[tuple[Path, Iterator[tuple[int, str]]]]:
    """Yield ``(path, carriers)`` for every surface this gate reads.

    Markdown comes from `check_doc_links.DOC_GLOBS` plus `specs/**/*.md`, which
    that glob set omits and which carries the strongest evidence in the tree:
    specdown fences are EXECUTED, so a stale `charness` invocation there is not
    documentation drift but a broken proof. The source globs are the retired
    `domain_language_contract`'s own, so the replacement is a superset of what it
    scanned rather than a narrowing.
    """
    snapshot = RepoFileSnapshot(root, require_git=require_git)
    for doc in iter_docs(root, require_git=require_git, snapshot=snapshot):
        yield doc, iter_command_carriers(doc)
    for spec in iter_matching_repo_files(
        root, SPEC_DOC_GLOBS, require_git=require_git, snapshot=snapshot
    ):
        yield spec, iter_command_carriers(spec)
    for source in iter_matching_repo_files(
        root, SOURCE_GLOBS, require_git=require_git, snapshot=snapshot
    ):
        yield source, iter_source_carriers(source)


def build_report(
    root: Path,
    *,
    require_git: bool = False,
    help_runner: HelpRunner | None = None,
) -> dict[str, object]:
    invocations: list[tuple] = []
    for path, carriers in iter_scanned_files(root, require_git=require_git):
        invocations.extend(
            (path, lineno, tokens) for lineno, tokens in iter_documented_invocations(carriers)
        )

    probe = HelpProbe(root, runner=help_runner)
    probe.prime({(CLI_NAME,)})
    if not probe.subcommand_choices((CLI_NAME,)):
        # No derivable authority means no verdict. Reporting "0 findings" here
        # would be the false green this gate exists to close.
        return {
            "status": "error",
            "invocations": len(invocations),
            "validated": 0,
            "probes": probe.clean_count(),
            "skipped": {},
            "findings": [
                f"`{CLI_NAME} --help` declares no subcommands; the derived surface is unreadable"
            ],
        }
    walked = _walk_all(probe, invocations)

    findings: list[str] = []
    skipped: Counter[str] = Counter()
    for index, (doc, lineno, _tokens) in enumerate(invocations):
        path, invalid = walked[index]
        # A walk stops at a parser with no choices, and a BROKEN probe reports no
        # choices too. Without this the two are one answer: if `charness worktree
        # --help` fails to run, every documented `charness worktree <anything>`
        # goes unchecked, the gate exits 0, and the receipt still says it
        # validated them. The root has always been guarded; this guards the rest.
        if not probe.probed_clean((CLI_NAME, *path)):
            skipped["subcommand-help-probe-failed"] += 1
            continue
        if invalid is None:
            skipped["no-subcommand-token-documented"] += not path
            continue
        if not SUBCOMMAND_TOKEN_RE.match(invalid):
            skipped["not-a-single-subcommand-token"] += 1
            continue
        where = f"{doc.relative_to(root).as_posix()}:{lineno}"
        documented = " ".join([CLI_NAME, *path])
        findings.append(f"{where}: `{documented}` has no subcommand `{invalid}`")

    # `validated` is what the receipt may claim: the total MINUS everything that
    # landed in a skip bucket. The sibling gate builds the same sentence from a
    # count that never included its skips, so rendering `invocations` here would
    # give two gates the identical wording and opposite arithmetic -- "N proven,
    # M also unproven" versus "N total, M of them unproven" -- with nothing
    # saying which one a reader is holding.
    return {
        "status": "fail" if findings else "pass",
        "invocations": len(invocations),
        "validated": len(invocations) - sum(skipped.values()),
        "probes": probe.clean_count(),
        "skipped": {key: value for key, value in sorted(skipped.items()) if value},
        "findings": sorted(set(findings)),
    }


def report_payload(report: dict[str, object]) -> dict[str, object]:
    return _gate_report_emit.findings_payload(
        report,
        fix_hint=(
            f"Fix the doc or restore the subcommand; `{CLI_NAME} --help` is the authority, not a "
            "declared alias list. A retired name being DISCUSSED belongs in prose, not in a code "
            "span that reads as a runnable command."
        ),
        skipped_noun="documented invocation(s)",
        skipped_note=" (already excluded from `validated`)",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root.resolve(), require_git=args.require_git_file_listing)
    emit_findings_report(report_payload(report))
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
