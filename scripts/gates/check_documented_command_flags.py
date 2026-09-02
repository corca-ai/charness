#!/usr/bin/env python3

"""Documented command flags must be flags the named script actually accepts.

`check_doc_links.py` closed the rung below this one: a documented command must
name a script that exists. That still leaves the proxy one level down --
`scripts/gates/check_skill_surface_preflight.py --path X --run-checks` keeps resolving
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

Carrier scope is NOT owned here. Markdown is where a flag claim is WRITTEN, not
where it is EXECUTED, and answering that widened this gate from one carrier shape
to three families -- so "which files store an invocation, and which spans of them
could be one" now lives in `command_carrier_discovery.py`, along with the
`--json` residue class that forced it and the non-claims that come with
reconstructing an argv sequence from source. This file takes carrier strings and
judges them; it does not know where they came from.

Non-claims. Each carrier this gate cannot resolve to a runnable script is counted
as `skipped` rather than waved through, so a pass never over-claims its own
coverage; the carrier-side blind spots are listed with the carriers.
"""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from collections.abc import Iterator
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

# The argparse side of this check -- what a parser declares, which options consume a
# value, and which parser a flag written at a given position would reach.
_argparse_surface = import_repo_module(__file__, "scripts.core.argparse_surface_lib")
iter_invocation_tails = _argparse_surface.iter_invocation_tails
resolve_subcommands = _argparse_surface.resolve_subcommands
active_depth = _argparse_surface.active_depth
MAX_SUBCOMMAND_DEPTH = _argparse_surface.MAX_SUBCOMMAND_DEPTH
_argparse_help_probe = import_repo_module(__file__, "scripts.core.argparse_help_probe")
HelpProbe = _argparse_help_probe.HelpProbe
HelpRunner = _argparse_help_probe.HelpRunner
_check_doc_links = import_repo_module(__file__, "scripts.gates.check_doc_links")
iter_known_repo_paths = _check_doc_links.iter_known_repo_paths
looks_like_repo_reference = _check_doc_links.looks_like_repo_reference
build_unique_basename_index = _check_doc_links.build_unique_basename_index
portable_skill_package_root = _check_doc_links.portable_skill_package_root
_gate_report_emit = import_repo_module(__file__, "scripts.core.gate_report_emit")
# Findings still go to stderr so a green run's stdout stays quotable; only the
# FORMAT changed here, never the stream this gate writes a verdict on.
emit_findings_report = _gate_report_emit.emit_findings_report
# The carrier side of this check -- which files store an invocation, and which
# spans of one could be a command string. `CLI_NAME` is bound from there rather
# than redeclared: the carrier scan is what has to recognize the bare name as a
# command token, and two copies of the literal would drift apart silently.
_command_carrier_discovery = import_repo_module(__file__, "scripts.gates_support.command_carrier_discovery")
iter_scanned_files = _command_carrier_discovery.iter_scanned_files
iter_command_carriers = _command_carrier_discovery.iter_command_carriers
CLI_NAME = _command_carrier_discovery.CLI_NAME
# Four documented shapes, all live. The leading boundary class matters: without
# it `sh\s+` matches the tail of any word ending in "sh" (`publish scripts/x.py`).
# A path form needs an interpreter/`./` prefix so a bare markdown path token is
# not read as a command; `$SKILL_DIR/` is self-identifying; and a bare
# `issue_tool.py read --repo X` (dense in the `issue` skill's docs) is matched on
# its basename and resolved only when that basename is unique in the repo.
#
# The repo's own CLI is the fourth, and it is the one shape with no `.py` to
# match on: the highest-consequence flag claims in this tree are written
# `charness tool doctor --json`, not `python3 charness ...`. `check_documented_
# subcommands.py` already probes that argv prefix, so the authority exists; only
# the FLAG half was unowned. `charness-artifacts/...`, the densest
# `charness`-prefixed token in these docs, cannot match: a subcommand word must
# follow.
#
# Requiring that word is deliberately the SAME boundary
# `check_documented_subcommands.INVOCATION_RE` draws, and it means a top-level
# option written with no subcommand (`charness --version`, `charness --help`) is
# not judged here. That is a real limit, and it currently hides one true finding:
# `charness --version` is accepted only through an exact-argv alias in `main()`
# that rewrites it to the `version` subcommand BEFORE argparse sees it, so
# `--help` -- this gate's whole authority -- does not declare it. Two adapters
# probe the CLI with it. The honest repair is to declare the option so the help
# surface stops lying, which also regenerates `docs/cli-reference.md`;
# widening this regex instead would make the gate report an option the CLI really
# does accept.
INVOCATION_RE = re.compile(
    r"(?:^|[\s|(\"'=&;])"
    r"(?:(?:(?:python3?|bash|sh)\s+|\./)[\"']?(?P<repo>[A-Za-z0-9._<>/-]+\.py)"
    r"|\$SKILL_DIR/[\"']?(?P<skill>[A-Za-z0-9._<>/-]+\.py)"
    rf"|(?:(?:python3?|bash|sh)\s+|\./)?(?P<cli>{CLI_NAME})(?=\s+[A-Za-z0-9])"
    r"|(?P<bare>[A-Za-z0-9_-]+\.py))"
    r"[\"']?(?=\s|$)"
)
# Generated copies of a canonical script; a doc never means these.
MIRROR_PREFIXES = ("plugins/", "mutants/")
# A flag literally named for the thing it is NOT: the repo's convention for a
# token argparse must REJECT. `.agents/cli-side-effect-probes.json` probes
# option-like positionals with `./charness tool install --not-a-tool`, asserting
# an exit 2. Read as a flag CLAIM that inverts the assertion -- the gate would
# demand the CLI accept the very flag the probe exists to prove it rejects,
# thirteen times on a clean tree.
#
# Keyed on the FLAG rather than on the config key that holds it, which was the
# first attempt and was both leakier and blunter: the same file writes
# `"dry_run_probe": "./charness tool install --dry-run --not-a-tool"`, so a
# key-shaped rule missed three of the thirteen AND would have had to throw away
# the real `--dry-run` claim beside them to catch the rest.
NEGATIVE_PROBE_FLAG_RE = re.compile(r"--not-an?-")


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
    if match.group("cli") is not None:
        # The repo's own CLI is a repo-root executable with no extension, so no
        # path resolution applies -- it either exists in this tree or the
        # invocation is describing the INSTALLED command, which is not this
        # tree's to prove. `HelpProbe` runs `python3 charness --help`, the same
        # argv prefix `check_documented_subcommands.py` already probes.
        if known_repo_paths is None:
            return (CLI_NAME, None) if (root / CLI_NAME).is_file() else (None, "cli-not-in-this-tree")
        return (CLI_NAME, None) if CLI_NAME in known_repo_paths else (None, "cli-not-in-this-tree")
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
        is_shared_doc = doc.relative_to(root).parts[:2] == ("skills", "shared")
        anchor = shared_reference_anchor(root, doc) if is_shared_doc else package_root
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
    carriers: Iterator[tuple[int, str]] | None = None,
) -> tuple[list[tuple[int, str, tuple[str, ...], tuple[str, ...]]], list[str]]:
    """``(invocations, skipped)`` -- ``(lineno, script, bare_words, flags)`` and skip reasons.

    Only flag-bearing invocations are collected; a bare `python3 scripts/x.py`
    has no flag claim to check and is `check_doc_links.py`'s to resolve.

    ``carriers`` is threaded rather than derived so the three carrier families
    (markdown spans, `.agents/` config lines, Python argv sequences) share one
    resolution and reporting path. `doc` is still needed by resolution itself: a
    package-relative `scripts/x.py` means the enclosing skill package's scripts/.
    """
    found: list[tuple[int, str, tuple[str, ...], tuple[str, ...]]] = []
    skipped: list[str] = []
    for lineno, carrier in iter_command_carriers(doc) if carriers is None else carriers:
        previous_end: int | None = None
        for match, tokens, flags in iter_invocation_tails(carrier, INVOCATION_RE):
            reason = _cli_name_used_as_a_value(carrier, match, previous_end)
            previous_end = match.end()
            script = None
            if reason is None:
                script, reason = resolve_script(root, doc, match, known_repo_paths, basename_index)
            # A rejection probe's own token is not a flag claim, so an invocation
            # that carries nothing else has no claim left to check. Counted rather
            # than dropped: it is a real stored invocation this gate declines to
            # judge, and a pass that hides it over-claims its coverage.
            claimed = [flag for flag in flags if not NEGATIVE_PROBE_FLAG_RE.match(flag)]
            if not claimed:
                if flags:
                    skipped.append(reason or "negative-probe-invocation")
                continue
            if script is None:
                skipped.append(reason)
                continue
            found.append((lineno, script, tokens, tuple(claimed)))
    return found, skipped


def _cli_name_used_as_a_value(carrier: str, match: re.Match[str], previous_end: int | None) -> str | None:
    """Reject a bare `charness` that is an ARGUMENT of the command in front of it.

    `charness` is this repo's product name as well as its CLI, so it is a live
    option value in a producer command is one command, and reading the value as a second
    invocation cut six real flags off the first and reported all six as drift.

    That exact case is now excluded one level earlier -- `INVOCATION_RE` requires a
    subcommand WORD after the CLI name, and a flag follows `charness` there -- so
    this rule covers what survives it: a value followed by another bare word
    (`--path charness doctor --flag`). Kept rather than deleted with its
    motivating instance, because the regex boundary is about the CLI's own shape
    and this is about which token in a command line can be the program name.

    One shell command has one program name, so a `charness` match that follows an
    earlier invocation on the same carrier is a value -- UNLESS a shell operator
    separates them, which starts a genuinely new command (`python3 a.py && charness
    doctor`). Counted as skipped rather than dropped, because a second command
    after an operator is a real invocation this rule declines to attribute.
    """
    if match.group("cli") is None or previous_end is None:
        return None
    between = carrier[previous_end : match.start()]
    return None if any(char in between for char in "|;&") else "cli-name-as-an-argument-value"


def _resolve_paths(probe, invocations: list[tuple]) -> list[tuple[str, ...]]:
    """Walk every invocation down the subparser tree, one probe round per depth."""
    paths = [() for _ in invocations]
    for _ in range(MAX_SUBCOMMAND_DEPTH):
        probe.prime({(script, *paths[index]) for index, (_, _, script, _, _) in enumerate(invocations)})
        changed = False
        for index, (_, _, script, tokens, _) in enumerate(invocations):
            resolved = resolve_subcommands(
                tokens,
                lambda path, s=script: probe.subcommand_choices((s, *path)),
                lambda path, s=script: probe.options_with_values((s, *path)),
            )
            if resolved != paths[index]:
                paths[index] = resolved
                changed = True
        if not changed:
            break
    probe.prime({(invocations[index][2], *paths[index]) for index in range(len(invocations))})
    # `{one-choice}` in a usage line is indistinguishable from any other braced
    # token, so a resolved path is only trusted while it still reports help. Trim
    # back to the deepest path that does, instead of reporting a false
    # "not runnable" on a brace the gate misread.
    for index, (_, _, script, _, _) in enumerate(invocations):
        while paths[index] and probe.result((script, *paths[index])).returncode != 0:
            paths[index] = paths[index][:-1]
    return paths


def build_report(
    root: Path,
    *,
    require_git: bool = False,
    help_runner: HelpRunner | None = None,
) -> dict[str, object]:
    known_repo_paths = iter_known_repo_paths(root, require_git=require_git)
    basename_index = build_canonical_basename_index(known_repo_paths)
    invocations: list[tuple] = []
    skipped: Counter[str] = Counter()
    for doc, carriers in iter_scanned_files(root, require_git=require_git):
        found, doc_skipped = iter_documented_invocations(
            root, doc, known_repo_paths, basename_index, carriers=carriers
        )
        invocations.extend((doc, lineno, script, bare, flags) for lineno, script, bare, flags in found)
        skipped.update(doc_skipped)

    probe = HelpProbe(root, runner=help_runner)
    paths = _resolve_paths(probe, invocations)

    findings: list[str] = []
    for index, (doc, lineno, script, tokens, flags) in enumerate(invocations):
        path = paths[index]
        where = f"{doc.relative_to(root).as_posix()}:{lineno}"
        documented = " ".join([script, *path])
        result = probe.result((script, *path))
        if result.returncode != 0:
            findings.append(f"{where}: `{documented} --help` exits {result.returncode}; the documented command is not runnable")
            continue
        # Scoped by POSITION, not unioned along the path. Measured on a two-level
        # parser: argparse hands everything after a subcommand token to that
        # subparser and nothing before it, so `demo resolve --top x` and
        # `demo --current y resolve` both exit 2 while a union call them fine.
        # A flag is checked against the parser active where it is documented, plus
        # that parser's ancestors -- an ancestor's option really is accepted at
        # depth 0..n when the subparser was built with `parents=`, since it then
        # appears in that depth's own `--help`.
        accepted_by_depth = [
            probe.accepted_options((script, *path[:depth])) for depth in range(len(path) + 1)
        ]
        missing: list[str] = []
        for flag_index, (kind, token) in enumerate(tokens):
            # `--not-a-tool` beside a real `--dry-run` on the same probe line: the
            # rejection token is excluded here rather than at collection, so the
            # claim written next to it is still checked.
            if kind != "flag" or token in missing or NEGATIVE_PROBE_FLAG_RE.match(token):
                continue
            depth = active_depth(tokens, path, flag_index)
            if token not in accepted_by_depth[depth]:
                missing.append(token)
        if missing:
            findings.append(f"{where}: `{documented}` does not accept documented flag(s) {', '.join(f'`{flag}`' for flag in missing)}")

    return {
        "status": "fail" if findings else "pass",
        "invocations": len(invocations),
        "probes": probe.clean_count(),
        "skipped": dict(sorted(skipped.items())),
        "findings": sorted(set(findings)),
    }


def report_payload(report: dict[str, object]) -> dict[str, object]:
    return _gate_report_emit.findings_payload(
        report,
        fix_hint=(
            "Fix the doc or restore the flag; use a `<placeholder>` path when the command "
            "only resolves in a consuming repo."
        ),
        skipped_noun="flag-bearing invocation(s)",
    )


def main(*, help_runner: HelpRunner | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    report = build_report(
        args.repo_root.resolve(),
        require_git=args.require_git_file_listing,
        help_runner=help_runner,
    )
    emit_findings_report(report_payload(report))
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
