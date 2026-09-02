#!/usr/bin/env python3

"""One owner for "is this command dominated, and what replaces it?" (SC14/15/17/19).

A *dominated* command is one that buys the same evidence as a cheaper command the
repo already has. A dominated instruction is not a FALSE one, which is why every
review angle this repo ships passes it: `python3 -m pytest -q ... tests` really
does re-prove the suite. It just costs ~22 minutes where
`python3 scripts/gates_support/run_standing_pytest.py` costs ~84 seconds over the same scope.
Review is aimed at falsity, so cost needs a deterministic reader instead.

WHAT THIS MECHANISM CANNOT SEE, stated before the detector rather than after a
reviewer asks. Every item below is outside the one question this module answers,
and a green result never means "no dominated command in this repo".

1. **It is a DENYLIST, so it cannot DISCOVER dominance.** An expensive command
   nobody registered passes, silently and forever. The registry is authored
   memory, not measurement.
2. **It never runs anything and never compares two costs.** `replacement` is an
   authored claim. A registry entry whose replacement is actually SLOWER is
   accepted without a murmur, and so is one whose replacement no longer exists.
   The `measured` field exists to carry the evidence a human collected; nothing
   here checks it.
3. **It reads the tokens of a command written at a site it was handed.** A
   command assembled at runtime from variables, built by concatenation, or
   reached one indirection deeper — a document naming a shell script that itself
   spawns the dominated command — is invisible. Callers own which sites are
   scanned; an unscanned site is not a clean site.
4. **It cannot tell "dominated" from "deliberately different evidence".** Two
   spellings of the same test run can mean different things: one full parallel
   run, versus a per-mutant isolated run where the parallel runner's startup is
   paid thousands of times. That discrimination lives in operator intent, which
   this module has no access to. It is why an exemption is keyed to a SITE and
   must carry a reason — and why an exempt site stays IN the report instead of
   disappearing from it.
5. **It can report a command that never RUNS.** Every item above is a false
   NEGATIVE; this one is the false POSITIVE the first version of this paragraph
   had no room for, and it is live. The standing-gate reader is a line scanner
   with no heredoc, quoting, or reachability awareness, so a command inside a
   usage heredoc or a comment block is discovered and classified like any other.
   Measured on this repo: two `cargo install lychee` lines inside `cat >&2
   <<'EOF'` help blocks are among the discovered snippets. A reader who assumes
   every finding is a command that executes will mis-triage those. Found by a
   bounded reviewer, after the paragraph claiming to state the blind class had
   already shipped.
6. **Registering a command silences nothing by itself.** Declaring the fast
   runner as a `replacement` does not make a document prescribing the slow one
   pass, and declaring an exemption does not remove a site from the report. Both
   are pinned by acceptance tests, because "declaration satisfies the criterion"
   is the exact way the sibling export gate was falsified one slice ago.

Deliberately dependency-free: stdlib only, and it parses no files. Callers hand
in already-parsed registry data and already-read text. That keeps the module
export-safe under `check_export_self_sufficiency.py` and keeps the policy in one
place while each caller owns its own site discovery.
"""

from __future__ import annotations

import importlib.util as _importlib_util
import re
import shlex
from pathlib import Path as _Path


# Sibling modules, loaded by path rather than imported by name. These scripts ship
# inside an exported plugin where `skills/public/quality/scripts` is not a package
# on `sys.path`, and consumers load THIS file by path too -- so an ordinary import
# would resolve in the source tree and fail in the export, which is the class
# `check_export_self_sufficiency.py` exists to refuse. `importlib` is stdlib, so the
# module's dependency-free promise still holds.
def _sibling(name: str):
    spec = _importlib_util.spec_from_file_location(
        f"command_dominance_{name}", _Path(__file__).resolve().with_name(f"command_dominance_{name}.py")
    )
    if spec is None or spec.loader is None:  # pragma: no cover - unreachable for a shipped sibling
        raise ImportError(f"cannot load command_dominance_{name}.py beside {__file__}")
    module = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# `carriers` loads `registry` and re-exports its types, and the lib reads the registry
# THROUGH it. Loading registry twice would give the family two structurally-identical
# `Finding` classes from two independent execs -- harmless today because nothing does
# an isinstance across them, which is exactly the kind of "harmless today" this repo
# keeps finding on the other side of a refactor.
_carriers = _sibling("carriers")
_registry = _carriers.registry_module

# Re-exported so every existing consumer keeps loading ONE module by path. The split
# is internal to this family; `check_command_dominance`, the artifact validators,
# `check_runtime_budget_universe` and the exported inventory are unchanged.
REGISTRY_VERSION = _registry.REGISTRY_VERSION
RegistryError = _registry.RegistryError
DominanceRule = _registry.DominanceRule
Exemption = _registry.Exemption
Wrapper = _registry.Wrapper
Registry = _registry.Registry
Finding = _registry.Finding
parse_registry = _registry.parse_registry
split_chunks = _carriers.split_chunks
iter_document_commands = _carriers.iter_document_commands
read_config_literal = _carriers.read_config_literal
unbudgeted_basis = _carriers.unbudgeted_basis
finding_message = _carriers.finding_message


# One or more leading `VAR=value` assignments. Deliberately the same shape
# `standing_gate_discovery_lib.ENV_PREFIX_RE` already uses, so a wrapper-prefixed
# command is classified the same way by both readers.
ENV_PREFIX_RE = re.compile(r'^(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|\'[^\']*\'|\S*)\s+)+')

# Interpreter spellings that carry a program rather than being one. `uv run` and
# `poetry run` take a further token, so they are handled as prefix pairs below.
_INTERPRETERS = frozenset({"python", "python3", "python2"})
_RUNNER_PAIRS = (("uv", "run"), ("poetry", "run"), ("pdm", "run"), ("hatch", "run"))


def resolve_invocations(
    command: str, wrappers: tuple[Wrapper, ...] = ()
) -> list[tuple[str, list[str]]]:
    """Every `(program, argv-after-program)` a command chunk actually runs.

    The whole point of resolving rather than substring-matching: the REPLACEMENT
    for the bare-pytest rule is `python3 scripts/gates_support/run_standing_pytest.py`, whose
    text contains `pytest`. A reader that asks "does this mention pytest" reports
    the fix as the defect. This resolves the program to
    `scripts/gates_support/run_standing_pytest.py` and the rule never fires on it.

    A LIST rather than one result, because `bash -c '<command>'` runs a command
    this reader can still see -- the inner text is a token, not an indirection
    through a file. One level of `-c` is unwrapped; a deeper nesting is not, and
    lands in blind-class item 3 with everything else it cannot follow.

    Returns an empty list when the chunk cannot be tokenized. Callers report an
    unparseable command as unparsed; it is never folded into "clean".
    """
    stripped = ENV_PREFIX_RE.sub("", command.strip())
    if not stripped:
        return []
    try:
        tokens = shlex.split(stripped)
    except ValueError:
        return []
    # No `if not tokens` guard: `stripped` is non-empty by the check above, and a
    # non-empty stripped string always tokenizes to at least one token. The
    # changed-line proof reported that branch as never executed, and trying to
    # write the test that reaches it is what showed there is no such input. The
    # empty result still has a path -- the loop below exhausts its tokens without
    # finding a program (`python3` alone) and returns [] at the end.

    wrapper_by_name = {wrapper.program: wrapper for wrapper in wrappers}
    index = 0
    while index < len(tokens):
        head = tokens[index].rsplit("/", 1)[-1]
        skipped = _skip_prefix(tokens, index, head, wrapper_by_name)
        if skipped is not None:
            if isinstance(skipped, list):
                return skipped
            index = skipped
            continue
        if head in {"bash", "sh"}:
            return _resolve_shell_c(tokens, index, wrappers)
        return [(tokens[index], list(tokens[index + 1 :]))]
    return []


def _skip_prefix(
    tokens: list[str], index: int, head: str, wrapper_by_name: dict[str, Wrapper]
) -> int | list[tuple[str, list[str]]] | None:
    """How far past a prefix that CARRIES a program, or the resolution it forces.

    Returns the next index to look at, a finished resolution when the prefix
    names its program outright (`python3 -m pytest`), or None when `tokens[index]`
    is the program itself.
    """
    # A bare `VAR=value` token. `ENV_PREFIX_RE` only strips assignments FOLLOWED
    # by whitespace, so the last one on a line survives and used to resolve as a
    # program literally named `BAR=2`. Harmless in practice -- no rule names such
    # a program -- but it is a wrong answer from a resolver whose whole job is
    # naming the program, and the acceptance test that asserted otherwise is what
    # surfaced it.
    if "=" in head and "/" not in head and not head.startswith("-"):
        return index + 1
    if head in _INTERPRETERS:
        after = index + 1
        # `python3 -m pytest` names its program in the -m argument.
        if after < len(tokens) and tokens[after] == "-m" and after + 1 < len(tokens):
            return [(tokens[after + 1], list(tokens[after + 2 :]))]
        return after
    # `env` as a PROGRAM, not as the `VAR=value` prefix `ENV_PREFIX_RE` strips.
    # This repo's own queued pytest gate is spelled `env CHARNESS_...=python3
    # python3 scripts/...`, so missing it would blind the arm to its own runner.
    if head == "env":
        after = index + 1
        while after < len(tokens) and "=" in tokens[after] and not tokens[after].startswith("-"):
            after += 1
        return after
    wrapper = wrapper_by_name.get(head)
    if wrapper is not None:
        return index + 1 + wrapper.skip_args
    if index + 1 < len(tokens) and (head, tokens[index + 1]) in _RUNNER_PAIRS:
        return index + 2
    return None


def _resolve_shell_c(
    tokens: list[str], index: int, wrappers: tuple[Wrapper, ...]
) -> list[tuple[str, list[str]]]:
    """`bash -c '<command>'` runs a command this reader can still see."""
    rest = tokens[index + 1 :]
    if "-c" in rest:
        inner_index = rest.index("-c") + 1
        if inner_index < len(rest):
            nested: list[tuple[str, list[str]]] = []
            for inner_chunk in split_chunks(rest[inner_index]):
                nested.extend(resolve_invocations(inner_chunk, wrappers))
            if nested:
                return nested
    return [(tokens[index], list(rest))]


def positional_targets(argv: list[str], value_flags: tuple[str, ...]) -> list[str]:
    """Positional arguments, with the values of value-taking flags removed.

    `-m 'not release_only'` must not read as a positional target, or
    `python3 -m pytest -q -m 'not release_only' tests` looks like it targets two
    things and no `broad_targets` entry matches it.
    """
    targets: list[str] = []
    skip_next = False
    for token in argv:
        if skip_next:
            skip_next = False
            continue
        if token == "--":
            continue
        if token.startswith("-"):
            if "=" not in token and token in value_flags:
                skip_next = True
            continue
        targets.append(token)
    return targets


def match_command(command: str, registry: Registry) -> DominanceRule | None:
    """The first registered rule this command matches, or None.

    Matching is on the resolved program plus the breadth of its positional
    targets, never on a substring. A focused run
    (`python3 -m pytest -q tests/quality_gates/test_x.py`) is NOT dominated: the
    parallel runner's startup is not worth paying for one file, and this repo's
    own `.agents/surfaces.json` carries a dozen such commands that must stay
    green or the gate is noise on arrival.
    """
    for chunk in split_chunks(command):
        for program, argv in resolve_invocations(chunk, registry.wrappers):
            program_name = program.rsplit("/", 1)[-1]
            for rule in registry.rules:
                if program_name != rule.program and program != rule.program:
                    continue
                targets = positional_targets(argv, rule.value_flags)
                if not targets:
                    # No path target. That means "everything" ONLY if nothing else
                    # narrowed the run. The first version of this function skipped
                    # that question and reported `pytest -k smoke` as DOMINATED --
                    # a gate blocking a one-test command and telling the author to
                    # run the whole suite instead, while this function's own
                    # docstring and the exported reference both promised focused
                    # runs were safe. Found by a bounded reviewer.
                    #
                    # Checked HERE and not before the target lookup, which is the
                    # second version of the same mistake: `-m 'not release_only'
                    # tests` carries a focus flag AND names the whole tree, and an
                    # early return would have retired SC17's own live instance.
                    if _selects_a_subset(argv, rule.focus_flags):
                        continue
                    return rule
                normalized = {target.rstrip("/") for target in targets}
                broad = {target.rstrip("/") for target in rule.broad_targets}
                if normalized and normalized <= broad:
                    return rule
    return None


def _selects_a_subset(argv: list[str], focus_flags: tuple[str, ...]) -> bool:
    """Whether a focusing flag narrows this run below its positional targets.

    Consulted ONLY when there is no positional target, so it cannot excuse a
    command that names the whole tree: `-m 'not release_only' tests` carries a
    focus flag and stays dominated because `tests` is still a broad target. What
    this stops is the no-target case, where "no positional targets" was being read
    as "everything" for a command that had already been narrowed by `-k`.

    The residual, stated rather than implied away: `pytest -m 'not release_only'`
    with NO target is close to a whole-suite run and is now read as focused. That
    is a false negative in a mechanism whose blind class already opens with "it is
    a denylist", and it is the right direction to be wrong in -- a false positive
    here blocks a legitimate one-test command and gets the gate switched off.
    """
    for token in argv:
        name = token.split("=", 1)[0]
        if name in focus_flags:
            return True
    return False


def wrapper_label(command: str, wrappers: tuple[Wrapper, ...]) -> str | None:
    """The label a queue wrapper carries, e.g. `pytest` in `queue_selected "pytest" ...`.

    Exists because the runtime-budget seam needs the REAL label to ask whether a
    spawned command sits under a budget. The first version of that seam derived a
    "label" from the tail of the site string -- a config key or a file path -- and
    compared it against the runner universe rather than the budgeted set, so it
    computed something entirely different from the sentence it printed. Two
    independent bounded reviewers found it. The label is right here, in the token
    the wrapper skips, and it was being thrown away.

    Returns None when no wrapper matched or the wrapper carries no argument; a
    command with no queue label has no budget by construction, which is a
    different fact from "its label is not budgeted" and the caller distinguishes
    them.
    """
    for chunk in split_chunks(command):
        stripped = ENV_PREFIX_RE.sub("", chunk.strip())
        try:
            tokens = shlex.split(stripped)
        except ValueError:
            continue
        # `tokens and` rather than a separate `if not tokens: continue` line. That
        # guard was unreachable and the changed-line proof reported it as never
        # executed. The reason it holds, corrected after a round-2 reviewer found
        # the first statement of it over-stated: `ENV_PREFIX_RE` CAN strip a
        # leading `FOO=1 `, but `split_chunks` strips the chunk, so the final
        # assignment has no trailing whitespace and always survives -- `stripped`
        # therefore stays non-empty and always yields at least one token.
        # Kept as an expression so the index stays safe without a dead statement.
        for wrapper in wrappers:
            if (
                tokens
                and tokens[0].rsplit("/", 1)[-1] == wrapper.program
                and wrapper.skip_args >= 1
                and len(tokens) > 1
            ):
                return tokens[1]
    return None


def classify_site(
    command: str,
    registry: Registry,
    *,
    site: str,
    line: int | None = None,
    context: dict[str, str] | None = None,
) -> Finding | None:
    """Classify one command at one site, applying any site-keyed exemption.

    An exemption changes `exempt`, never presence. The finding is returned either
    way so a caller can report it; only blocking reads `exempt`.

    EXEMPTION GRANULARITY, stated because a bounded reviewer measured that the
    two seams differ and nothing said so. An exemption matches on
    `(site, rule_id)`. For the config seam the site is `path:key`, so it names one
    literal. For the standing-gate seam the site is the FILE, so exempting one
    dominated command in a runner exempts every present and future dominated
    command in that file for that rule. That is deliberate -- a line-keyed
    exemption goes stale the moment anything above it moves -- but it is a real
    widening, so findings now carry `line` to show which command was actually
    judged, and the reason is expected to name it.
    """
    rule = match_command(command, registry)
    if rule is None:
        return None
    exemption = registry.exemption_for(site, rule.rule_id)
    return Finding(
        rule_id=rule.rule_id,
        site=site,
        command=command.strip(),
        replacement=rule.replacement,
        reason=rule.reason,
        line=line,
        exempt=exemption is not None,
        exemption_id=exemption.exemption_id if exemption else None,
        exemption_reason=exemption.reason if exemption else None,
        context=dict(context or {}),
    )


def scan_document(text: str, registry: Registry, *, site: str) -> list[Finding]:
    """Every dominated command PRESCRIBED by a document body."""
    findings: list[Finding] = []
    for number, command in iter_document_commands(text):
        finding = classify_site(command, registry, site=site, line=number)
        if finding is not None:
            findings.append(finding)
    return findings
