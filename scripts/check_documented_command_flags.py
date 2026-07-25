#!/usr/bin/env python3

"""Documented command flags must be flags the named script actually accepts.

`check_doc_links.py` closed the rung below this one: a documented command must
name a script that exists. That still leaves the proxy one level down --
`scripts/check_skill_surface_preflight.py --path X --run-checks` keeps resolving
after `--run-checks` is deleted from its own argparse, so every drift guard stays
green while the documented command exits 2. Reproduced before this gate was
written: removing that one `add_argument` line left `check_command_docs`,
`check_doc_authoring_preflight`, `check_doc_links`, and both preflight test files
passing.

Closing it needs an argparse contract rather than another literal, so the accepted
option set comes from running the command's own ``--help``. Static source scanning
cannot answer it: this repo builds `--repo-root`/`--summary`/`--detail` through
shared parser helpers, so a source scan of the named file reports 34 false
missing flags on a clean tree.

floor-addition-restraint: blocking, not advisory. The recurrence is recorded, not
first-sighted -- the 2026-07-25 documented-command-resolution critique filed this
as F8 (valid-but-defer) after the rung below it shipped, the violation was
reproduced against the live tree before this file was written, and the first
clean run found two live broken commands (a critique adapter-contract example and
an `achieve` reference pointing `$SKILL_DIR/scripts/` at a script owned by
`retro`). An advisory cannot hold that line: the failure mode is silence, and the
four guards that already cover this surface were all green while the command
exited 2. The describe-first preflight cannot absorb it either -- it flips on a
`scripts/*.py` argparse edit that touches no doc.

Scope note -- this gate owns "does the documented invocation parse", which is why
it carries its own invocation regex instead of reusing `COMMAND_TARGET_RE`: it
needs the arguments after the script, the `$SKILL_DIR/` form the quality skill's
dispatch references use, and backslash continuations. Whether a named path
resolves at all stays owned by `check_doc_links.py`.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_check_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
iter_docs = _check_doc_links.iter_docs
iter_known_repo_paths = _check_doc_links.iter_known_repo_paths
looks_like_repo_reference = _check_doc_links.looks_like_repo_reference
build_unique_basename_index = _check_doc_links.build_unique_basename_index
portable_skill_package_root = _check_doc_links.portable_skill_package_root
BACKTICK_CONTENT_RE = _check_doc_links.BACKTICK_CONTENT_RE
_markdown_doc_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_processes_in_order = _subprocess_guard.run_processes_in_order
_gate_report_emit = import_repo_module(__file__, "scripts.gate_report_emit")
emit_findings_report = _gate_report_emit.emit_findings_report

# Three documented shapes, all live. The leading boundary class matters: without
# it `sh\s+` matches the tail of any word ending in "sh" (`publish scripts/x.py`).
# A path form needs an interpreter/`./` prefix so a bare markdown path token is
# not read as a command; `$SKILL_DIR/` is self-identifying; and a bare
# `issue_tool.py read --repo X` (dense in the `issue` skill's docs) is matched on
# its basename and resolved only when that basename is unique in the repo.
INVOCATION_RE = re.compile(
    r"(?:^|[\s|(\"'=&;])"
    r"(?:(?:(?:python3?|bash|sh)\s+|\./)[\"']?(?P<repo>[A-Za-z0-9._<>/-]+\.py)"
    r"|\$SKILL_DIR/[\"']?(?P<skill>[A-Za-z0-9._<>/-]+\.py)"
    r"|(?P<bare>[A-Za-z0-9_-]+\.py))"
    r"[\"']?(?=\s|$)"
)
FLAG_RE = re.compile(r"(?<![\w<-])--[A-Za-z0-9][A-Za-z0-9-]*")
# argparse guarantees two structural homes for a real option name: the `usage:`
# block, and the left column of an option row. Everything else in `--help` is
# prose -- `description=__doc__`, `epilog`, and every `help=` string. Scanning the
# whole render put `--cached`, `--run-checks`, `--body-file`, `--min-confidence`
# and `--mutation-coverage-command` into the accepted sets of parsers that reject
# them: a false green in exactly the direction this gate exists to close.
OPTION_ROW_RE = re.compile(r"^ {1,4}(-[^\s].*)$")
HELP_COLUMN_GAP_RE = re.compile(r"\s{2,}")
# Generated copies of a canonical script; a doc never means these.
MIRROR_PREFIXES = ("plugins/", "mutants/")
SUBCOMMAND_RE = re.compile(r"^[a-z][a-z0-9-]*$")
# argparse renders a subparser's choices as `{a,b,c}` in its usage line. Reading
# them back is what lets a flag be attributed to the parser that owns it.
CHOICES_RE = re.compile(r"\{([a-z0-9-]+(?:,[a-z0-9-]+)*)\}")
# A documented pipeline's later stage is a different command; its flags are not
# this script's to accept. Matched against whole shell tokens, never against raw
# text -- `--test-pressure "... 23.2% vs 22% gate; +2 tests"` carries a literal
# `;` inside a quoted value, and cutting there strands the quote.
SHELL_OPERATORS = {"|", "||", ";", "&&", "&", ">", ">>", "<"}
HELP_COLUMNS = "200"
MAX_SUBCOMMAND_DEPTH = 4


def accepted_options(help_text: str) -> set[str]:
    """Option names argparse actually declares, read from structure not prose.

    Two sources, both structural: the `usage:` block (every optional appears
    there) and the invocation column of each option row (which is where `--help`
    itself lives, since usage renders it as `[-h]`). The help column is cut at the
    two-space gap argparse puts between an option and its description.
    """
    accepted: set[str] = set()
    in_usage = False
    for line in help_text.splitlines():
        if line.startswith("usage:"):
            in_usage = True
        elif in_usage and not line.strip():
            in_usage = False
        if in_usage:
            accepted.update(FLAG_RE.findall(line))
            continue
        row = OPTION_ROW_RE.match(line)
        if row:
            accepted.update(FLAG_RE.findall(HELP_COLUMN_GAP_RE.split(row.group(1))[0]))
    return accepted


def build_canonical_basename_index(known_repo_paths: set[str]) -> dict[str, str]:
    """Basename -> canonical script path, for the prefix-free documented form.

    `check_doc_links`'s repo-wide index cannot answer this: every canonical script
    is mirrored into `plugins/charness/scripts/` (and `mutants/`), so EVERY
    basename is non-unique and all 40 live bare invocations resolve to nothing.
    Mirrors are excluded because they are generated copies of the path a doc
    means. A name still shared by several skill packages (`resolve_adapter.py`)
    stays genuinely ambiguous and is counted as skipped, never guessed.
    """
    return build_unique_basename_index(known_repo_paths, keep=_is_canonical_script)


def _is_canonical_script(rel_path: str) -> bool:
    return rel_path.endswith(".py") and not rel_path.startswith(MIRROR_PREFIXES)


def normalize_argument_token(token: str) -> str:
    """Strip the doc notation around a flag so a real documented flag is checked.

    `[--converted --durable-kind <kind>]` optional-brackets and `--engine=tokei`
    inline values are both live in this repo. Left unnormalized they fail
    `FLAG_RE.fullmatch`, get dropped, and -- worse than a miss -- the surrounding
    invocation still counts as validated, so the run over-claims coverage without
    even landing in the skipped tail.
    """
    return token.strip("[](),").split("=", 1)[0]


def iter_command_carriers(doc: Path) -> Iterator[tuple[int, str]]:
    """Yield ``(lineno, text)`` spans that can carry a documented command.

    Fenced lines carry commands directly and join across a trailing backslash;
    prose carries them inside backtick spans. The reported line is where the
    invocation *starts*, which is the line an author has to edit.
    """
    pending_lineno: int | None = None
    pending_text = ""
    previous_lineno = 0
    for lineno, line, in_fence in iter_doc_lines(doc):
        # A continuation only joins the physically next line. `iter_doc_lines`
        # consumes fence delimiters silently, so without this a dangling `\` at
        # the end of one fenced block would swallow the first line of the next.
        if pending_lineno is not None and lineno != previous_lineno + 1:
            yield pending_lineno, pending_text
            pending_lineno = None
        previous_lineno = lineno
        if not in_fence:
            if pending_lineno is not None:
                yield pending_lineno, pending_text
                pending_lineno = None
            for span in BACKTICK_CONTENT_RE.finditer(line):
                yield lineno, span.group(1)
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


def split_arguments(tail: str) -> tuple[list[str], list[str]]:
    """Return ``(bare_words, flags)`` documented for one invocation.

    Tokenized with `shlex` rather than scanned with a regex because a quoted
    argument value legitimately contains flag-shaped text: `--verification "git
    diff --stat ..."` documents `--verification`, not `--stat`, and reading the
    latter as this script's flag is a false positive.

    Bare words are returned unclassified -- which of them is a subcommand and
    which is a flag's value cannot be known until argparse says what subcommands
    exist. `resolve_subcommands` answers that from the probed usage line.
    """
    tokens = _tokenize(tail)
    for index, token in enumerate(tokens):
        if token in SHELL_OPERATORS:
            tokens = tokens[:index]
            break
    normalized = [normalize_argument_token(token) for token in tokens]
    bare = [token for token in normalized if SUBCOMMAND_RE.match(token)]
    flags = [token for token in normalized if FLAG_RE.fullmatch(token)]
    return bare, list(dict.fromkeys(flags))


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


def resolve_subcommands(bare: list[str], choices_for) -> tuple[str, ...]:
    """Walk the documented bare words down the subparser tree.

    Order-independent by design: `resolve_adapter.py --repo-root . resolve-destination
    --current X` puts a top-level flag before the subcommand, so a "leading words
    only" read attributes `--current` to the parser that never declares it.
    """
    path: list[str] = []
    remaining = list(bare)
    for _ in range(MAX_SUBCOMMAND_DEPTH):
        choices = choices_for(tuple(path))
        nxt = next((word for word in remaining if word in choices), None)
        if nxt is None:
            break
        path.append(nxt)
        remaining = remaining[remaining.index(nxt) + 1 :]
    return tuple(path)


def _repo_relative(root: Path, path: Path) -> str | None:
    """Normalized repo-relative posix path, or None when it escapes the repo.

    Normalization is textual (`os.path.normpath`) rather than `Path.resolve()`:
    the `..` segments in `$SKILL_DIR/../quality/scripts/x.py` have to collapse
    against the *documented* anchor, not against symlink-resolved reality.
    """
    normalized = os.path.normpath(str(path))
    try:
        return Path(normalized).relative_to(root).as_posix()
    except ValueError:
        return None


def shared_reference_anchor(root: Path, doc: Path) -> Path | None:
    """Stand-in `$SKILL_DIR` for a `skills/shared/**` reference."""
    try:
        parts = doc.relative_to(root).parts
    except ValueError:
        return None
    return root / "skills" / "public" / "_" if parts[:2] == ("skills", "shared") else None


def resolve_script(
    root: Path,
    doc: Path,
    match: re.Match[str],
    known_repo_paths: set[str] | None,
    basename_index: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """``(script, skip_reason)`` -- exactly one of the two is set.

    A placeholder-bearing path is the documented escape for a command that only
    resolves in a consuming repo. An unresolvable path is skipped rather than
    reported: `check_doc_links.py` already owns that finding, and duplicating it
    would make one doc typo fail two gates with different wording.

    The reason is returned rather than swallowed because every skip is a
    documented command this gate did NOT prove. Counting them in the report keeps
    a pass from over-claiming its own coverage.
    """
    package_root = portable_skill_package_root(root, doc)
    skill_relative = match.group("skill")
    bare = match.group("bare")
    candidate = skill_relative or bare or match.group("repo")
    if "<" in candidate or ">" in candidate:
        return None, "placeholder-path"

    if bare is not None:
        # `issue_tool.py verify-closeout --expect-state CLOSED` -- prefix-free and
        # dense in the issue skill's docs. Neither this gate's path forms nor
        # check_doc_links' matcher saw it, so it was unowned by both. Resolved
        # only when the basename is unique repo-wide; an ambiguous one is counted,
        # never guessed.
        resolved = (basename_index or {}).get(bare)
        return (resolved, None) if resolved else (None, "ambiguous-or-unknown-script-basename")

    if skill_relative is not None:
        # In a `skills/shared/**` reference `$SKILL_DIR` is the *consuming* skill's
        # directory, which always sits at `skills/<kind>/<name>`. Only the depth
        # matters for the `../../shared/scripts/...` form these references use.
        anchor = package_root or shared_reference_anchor(root, doc)
        if anchor is None:
            return None, "skill-dir-outside-a-skill-package"
        options = [_repo_relative(root, anchor / skill_relative)]
    else:
        if not looks_like_repo_reference(candidate):
            return None, "not-a-repo-owned-path"
        options = [candidate]
        if package_root is not None:
            options.append(_repo_relative(root, package_root / candidate))
    options = [option for option in options if option is not None]

    for option in options:
        if known_repo_paths is not None:
            if option in known_repo_paths:
                return option, None
        elif (root / option).exists():
            return option, None
    return None, "unresolved-path-owned-by-check-doc-links"


def iter_documented_invocations(
    root: Path,
    doc: Path,
    known_repo_paths: set[str] | None = None,
    basename_index: dict[str, str] | None = None,
) -> tuple[list[tuple[int, str, tuple[str, ...], tuple[str, ...]]], list[str]]:
    """``(invocations, skipped)`` -- ``(lineno, script, bare_words, flags)`` and skip reasons.

    Only flag-bearing invocations are collected; a bare `python3 scripts/x.py`
    has no flag claim to check and is `check_doc_links.py`'s to resolve.
    """
    found: list[tuple[int, str, tuple[str, ...], tuple[str, ...]]] = []
    skipped: list[str] = []
    for lineno, carrier in iter_command_carriers(doc):
        matches = list(INVOCATION_RE.finditer(carrier))
        for index, match in enumerate(matches):
            # One carrier can name two commands (`verify: python3 a.py --x,
            # python3 b.py --y`). Reading to the end of the carrier hands the
            # second command's flags to the first -- a blocking false red on a
            # correct doc, since `,` is not a shell operator to cut on.
            end = matches[index + 1].start() if index + 1 < len(matches) else len(carrier)
            script, reason = resolve_script(root, doc, match, known_repo_paths, basename_index)
            bare, flags = split_arguments(carrier[match.end() : end])
            if not flags:
                continue
            if script is None:
                skipped.append(reason)
                continue
            found.append((lineno, script, tuple(bare), tuple(flags)))
    return found, skipped


class HelpProbe:
    """Cached, batched ``<script> <path> --help`` results.

    A wide ``COLUMNS`` keeps argparse from wrapping an option name out of reach of
    the scanner. Probes run one round per subparser depth, batched in parallel:
    the whole 300-script tree costs ~1.2s wall, so the documented subset over two
    rounds stays comfortably inside a cheap gate.
    """

    def __init__(self, root: Path) -> None:
        self._root = root
        self._results: dict[tuple[str, tuple[str, ...]], object] = {}

    def prime(self, targets: set[tuple[str, tuple[str, ...]]]) -> None:
        pending = sorted(targets - self._results.keys())
        if not pending:
            return
        env = dict(os.environ, COLUMNS=HELP_COLUMNS)
        commands = [["python3", script, *path, "--help"] for script, path in pending]
        results = run_processes_in_order(commands, cwd=self._root, env=env, timeout_seconds=120)
        self._results.update(zip(pending, results, strict=True))

    def result(self, script: str, path: tuple[str, ...]):
        return self._results[(script, path)]

    def text(self, script: str, path: tuple[str, ...]) -> str:
        result = self.result(script, path)
        return result.stdout + result.stderr

    def choices(self, script: str, path: tuple[str, ...]) -> set[str]:
        # Unprobed depths report "no subcommands here", so each resolution round
        # descends exactly one level and the next round primes what it revealed.
        result = self._results.get((script, path))
        if result is None or result.returncode != 0:
            return set()
        return {
            choice
            for group in CHOICES_RE.findall(self.text(script, path))
            for choice in group.split(",")
        }

    def count(self) -> int:
        return len(self._results)


def _resolve_paths(probe: HelpProbe, invocations: list[tuple]) -> list[tuple[str, ...]]:
    """Walk every invocation down the subparser tree, one probe round per depth."""
    paths = [() for _ in invocations]
    for _ in range(MAX_SUBCOMMAND_DEPTH):
        probe.prime({(script, paths[index]) for index, (_, _, script, _, _) in enumerate(invocations)})
        changed = False
        for index, (_, _, script, bare, _) in enumerate(invocations):
            resolved = resolve_subcommands(list(bare), lambda path, s=script: probe.choices(s, path))
            if resolved != paths[index]:
                paths[index] = resolved
                changed = True
        if not changed:
            break
    probe.prime({(invocations[index][2], paths[index]) for index in range(len(invocations))})
    # `{one-choice}` in a usage line is indistinguishable from any other braced
    # token, so a resolved path is only trusted while it still reports help. Trim
    # back to the deepest path that does, instead of reporting a false
    # "not runnable" on a brace the gate misread.
    for index, (_, _, script, _, _) in enumerate(invocations):
        while paths[index] and probe.result(script, paths[index]).returncode != 0:
            paths[index] = paths[index][:-1]
    return paths


def build_report(root: Path, *, require_git: bool = False) -> dict[str, object]:
    known_repo_paths = iter_known_repo_paths(root, require_git=require_git)
    basename_index = build_canonical_basename_index(known_repo_paths)
    invocations: list[tuple] = []
    skipped: Counter[str] = Counter()
    for doc in iter_docs(root, require_git=require_git):
        found, doc_skipped = iter_documented_invocations(root, doc, known_repo_paths, basename_index)
        invocations.extend((doc, lineno, script, bare, flags) for lineno, script, bare, flags in found)
        skipped.update(doc_skipped)

    probe = HelpProbe(root)
    paths = _resolve_paths(probe, invocations)

    findings: list[str] = []
    for index, (doc, lineno, script, _bare, flags) in enumerate(invocations):
        path = paths[index]
        where = f"{doc.relative_to(root).as_posix()}:{lineno}"
        documented = " ".join([script, *path])
        result = probe.result(script, path)
        if result.returncode != 0:
            findings.append(f"{where}: `{documented} --help` exits {result.returncode}; the documented command is not runnable")
            continue
        # Union along the resolved path: a top-level flag documented after the
        # subcommand is still accepted by the top-level parser.
        accepted = {
            flag
            for depth in range(len(path) + 1)
            for flag in accepted_options(probe.text(script, path[:depth]))
        }
        missing = [flag for flag in flags if flag not in accepted]
        if missing:
            findings.append(f"{where}: `{documented}` does not accept documented flag(s) {', '.join(f'`{flag}`' for flag in missing)}")

    return {
        "status": "fail" if findings else "pass",
        "invocations": len(invocations),
        "probes": probe.count(),
        "skipped": dict(sorted(skipped.items())),
        "findings": sorted(set(findings)),
    }


def render_report(report: dict[str, object]) -> str:
    """Render findings and, on every run, the surface that was NOT proven.

    The skipped tail rides on the pass output too: a bare "validated N
    invocations" reads as full coverage of the documented command surface, and it
    is not -- each skip is a documented invocation whose flags went unchecked.
    """
    if report["findings"]:
        lines = ["Documented command flag drift detected:"]
        lines.extend(f"- {finding}" for finding in report["findings"])
        lines.append(
            "Fix the doc or restore the flag; use a `<placeholder>` path when the command only resolves in a consuming repo."
        )
    else:
        lines = [
            f"Validated {report['invocations']} documented command invocation(s) "
            f"against {report['probes']} argparse surface(s)."
        ]
    skipped = report["skipped"]
    if skipped:
        detail = ", ".join(f"{reason}: {count}" for reason, count in skipped.items())
        lines.append(f"Not proven ({sum(skipped.values())} flag-bearing invocation(s) skipped) — {detail}.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root.resolve(), require_git=args.require_git_file_listing)
    emit_findings_report(report, as_json=args.json, render=render_report)
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
