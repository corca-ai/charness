#!/usr/bin/env python3

"""One owner for "is this command dominated, and what replaces it?" (SC14/15/17/19).

A *dominated* command is one that buys the same evidence as a cheaper command the
repo already has. A dominated instruction is not a FALSE one, which is why every
review angle this repo ships passes it: `python3 -m pytest -q ... tests` really
does re-prove the suite. It just costs ~22 minutes where
`python3 scripts/run_standing_pytest.py` costs ~84 seconds over the same scope.
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

import re
import shlex
from typing import NamedTuple

REGISTRY_VERSION = 1

# One or more leading `VAR=value` assignments. Deliberately the same shape
# `standing_gate_discovery_lib.ENV_PREFIX_RE` already uses, so a wrapper-prefixed
# command is classified the same way by both readers.
ENV_PREFIX_RE = re.compile(r'^(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|\'[^\']*\'|\S*)\s+)+')

# Interpreter spellings that carry a program rather than being one. `uv run` and
# `poetry run` take a further token, so they are handled as prefix pairs below.
_INTERPRETERS = frozenset({"python", "python3", "python2"})
_RUNNER_PAIRS = (("uv", "run"), ("poetry", "run"), ("pdm", "run"), ("hatch", "run"))

class RegistryError(ValueError):
    """A registry that cannot be trusted to render a verdict."""


# NamedTuple rather than dataclass, and the reason is not style: this module is
# loaded by `runtime_bootstrap.load_path_module`, which execs a module that is
# never registered in `sys.modules`. `@dataclass` resolves its own annotations
# through `sys.modules[cls.__module__]` and raises `AttributeError: 'NoneType'`
# there. Measured, not assumed -- the first import of this file failed that way.
class DominanceRule(NamedTuple):
    rule_id: str
    program: str
    replacement: str
    reason: str
    broad_targets: tuple[str, ...] = ()
    value_flags: tuple[str, ...] = ()
    focus_flags: tuple[str, ...] = ()
    measured: str = ""


class Exemption(NamedTuple):
    exemption_id: str
    site: str
    rule_id: str
    reason: str


class Wrapper(NamedTuple):
    """A program that RUNS another program, plus how many of its own args to skip.

    Declared rather than inferred, and declared by the CONSUMING repo, because the
    shape is repo-local: charness queues every standing gate as
    `queue_selected "<label>" <command>`, so a resolver that stops at the first
    token resolves every queued command to `queue_selected` and the whole
    standing-gate arm reads clean while a dominated command sits inside it.

    RE-MEASURED 2026-08-16 by running the discovery, after a bounded reviewer
    counted the tree by hand and refuted the figure this docstring first carried:
    14 discovered snippets, 8 wrapped and 6 unwrapped. The original "13 of 14"
    was never counted -- it was inferred from a probe that showed 14 snippets and
    one pytest-bearing line. It is asserted now rather than asserted about, by
    `test_the_wrapped_snippet_ratio_this_repo_documents_is_the_measured_one`,
    so the next drift is a red test rather than a stale sentence.
    """

    program: str
    skip_args: int = 0


class Registry(NamedTuple):
    rules: tuple[DominanceRule, ...] = ()
    exemptions: tuple[Exemption, ...] = ()
    config_literals: tuple[dict[str, str], ...] = ()
    wrappers: tuple[Wrapper, ...] = ()

    def rule(self, rule_id: str) -> DominanceRule | None:
        return next((rule for rule in self.rules if rule.rule_id == rule_id), None)

    def exemption_for(self, site: str, rule_id: str) -> Exemption | None:
        return next(
            (
                item
                for item in self.exemptions
                if item.site == site and item.rule_id == rule_id
            ),
            None,
        )


class Finding(NamedTuple):
    rule_id: str
    site: str
    command: str
    replacement: str
    reason: str
    line: int | None = None
    exempt: bool = False
    exemption_id: str | None = None
    exemption_reason: str | None = None
    context: dict[str, str] | None = None

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "rule_id": self.rule_id,
            "site": self.site,
            "command": self.command,
            "replacement": self.replacement,
            "reason": self.reason,
            "exempt": self.exempt,
        }
        if self.line is not None:
            payload["line"] = self.line
        if self.exempt:
            payload["exemption_id"] = self.exemption_id
            payload["exemption_reason"] = self.exemption_reason
        if self.context:
            payload["context"] = dict(self.context)
        return payload


def _require_text(mapping: dict, key: str, where: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{where}: `{key}` is required and must be non-empty text")
    return value.strip()


def _require_list(mapping: dict, key: str, where: str) -> tuple[str, ...]:
    """A list-valued field must arrive as a LIST, or the registry is refused.

    Not defensive programming — this is the failure that reached a green gate
    during this slice. One of the two readers of this file is a hand-rolled
    block-YAML parser that turns an inline sequence `[tests]` into the STRING
    "[tests]" without complaint. Iterating a string yields its characters, so
    `broad_targets` silently became seven single-character targets, no command
    ever matched, and the gate reported a clean tree over a dominated literal.
    Coercing with `str(item) for item in ...` is what made that silent; refusing
    the shape is what makes it loud.
    """
    value = mapping.get(key)
    if value is None:
        return ()
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise RegistryError(
            f"{where}: `{key}` must be a list, got {type(value).__name__} {value!r}. "
            "Use block-style YAML entries; an inline `[a, b]` sequence is read as a "
            "bare string by this repo's adapter parser and would silently match nothing."
        )
    return tuple(str(item) for item in value)


def _entries(data: dict, key: str) -> list[tuple[str, dict]]:
    """The list under `key`, each entry paired with the label errors will name.

    Every section of this registry validates the same two things before its own
    rules apply -- the section is a list, and each entry is a mapping -- so they
    are checked once here rather than four times with four slightly different
    messages.
    """
    raw = data.get(key) or []
    if not isinstance(raw, list):
        raise RegistryError(f"`{key}` must be a list")
    entries = []
    for index, item in enumerate(raw):
        where = f"{key}[{index}]"
        if not isinstance(item, dict):
            raise RegistryError(f"{where}: entry must be a mapping")
        entries.append((where, item))
    return entries


def _parse_rules(data: dict) -> tuple[DominanceRule, ...]:
    rules: list[DominanceRule] = []
    for where, raw in _entries(data, "dominated_commands"):
        rule = DominanceRule(
            rule_id=_require_text(raw, "id", where),
            program=_require_text(raw, "program", where),
            replacement=_require_text(raw, "replacement", where),
            reason=_require_text(raw, "reason", where),
            broad_targets=_require_list(raw, "broad_targets", where),
            value_flags=_require_list(raw, "value_flags", where),
            focus_flags=_require_list(raw, "focus_flags", where),
            measured=str(raw.get("measured") or "").strip(),
        )
        if any(existing.rule_id == rule.rule_id for existing in rules):
            raise RegistryError(f"{where}: duplicate rule id {rule.rule_id!r}")
        rules.append(rule)
    return tuple(rules)


def _parse_exemptions(data: dict, known_ids: set[str]) -> tuple[Exemption, ...]:
    exemptions: list[Exemption] = []
    for where, raw in _entries(data, "exemptions"):
        rule_id = _require_text(raw, "rule", where)
        if rule_id not in known_ids:
            raise RegistryError(
                f"{where}: exempts unknown rule {rule_id!r}; an exemption naming no "
                "live rule is a hole nothing can close"
            )
        exemptions.append(
            Exemption(
                exemption_id=_require_text(raw, "id", where),
                site=_require_text(raw, "site", where),
                rule_id=rule_id,
                reason=_require_text(raw, "reason", where),
            )
        )
    return tuple(exemptions)


def _parse_config_literals(data: dict) -> tuple[dict[str, str], ...]:
    return tuple(
        {"path": _require_text(raw, "path", where), "key": _require_text(raw, "key", where)}
        for where, raw in _entries(data, "config_literals")
    )


def _parse_wrappers(data: dict) -> tuple[Wrapper, ...]:
    wrappers: list[Wrapper] = []
    for where, raw in _entries(data, "wrapper_programs"):
        skip = raw.get("skip_args", 0)
        if not isinstance(skip, int) or isinstance(skip, bool) or skip < 0:
            raise RegistryError(f"{where}: `skip_args` must be a non-negative integer")
        wrappers.append(Wrapper(program=_require_text(raw, "program", where), skip_args=skip))
    return tuple(wrappers)


def parse_registry(data: object) -> Registry:
    """Turn registry data into rules, refusing anything that cannot render a verdict.

    A reasonless rule or exemption is REFUSED rather than defaulted. An exemption
    is the one place this mechanism accepts "a human decided this is fine", so an
    exemption whose reason is absent is a silent hole in a proof surface, and the
    cheapest possible response to a red gate. It has to cost a sentence.
    """
    if not isinstance(data, dict):
        raise RegistryError("registry must be a mapping")
    version = data.get("version")
    if version != REGISTRY_VERSION:
        raise RegistryError(
            f"registry version {version!r} is not the version this reader "
            f"understands ({REGISTRY_VERSION})"
        )
    rules = _parse_rules(data)
    return Registry(
        rules=rules,
        exemptions=_parse_exemptions(data, {rule.rule_id for rule in rules}),
        config_literals=_parse_config_literals(data),
        wrappers=_parse_wrappers(data),
    )


def split_chunks(command: str) -> list[str]:
    """Split a shell one-liner into the commands it actually runs, QUOTE-AWARE.

    A regex split was quote-blind, and an adversarial round-2 reviewer showed the
    cost: `bash -c "python3 -m pytest -q tests && echo ok"` split mid-quote into
    `bash -c "python3 -m pytest -q tests` and `echo ok"`, both of which then
    failed `shlex.split` with an unterminated quote, so `resolve_invocations`
    returned [] for each and a dominated whole-suite run inside `bash -c` was
    INVISIBLE to a blocking gate. It also made the nested-chunk loop in
    `_resolve_shell_c` unreachable by construction: the outer split had already
    destroyed the string it was written to iterate.

    Operators recognised outside quotes: `&&`, `||`, `;`, `|`, and newline.
    Backslash escapes the next character. What this still does NOT model, and it
    belongs to the blind class rather than to a bigger parser here: parentheses,
    process substitution, heredocs, and `$(...)`.
    """
    chunks: list[str] = []
    buffer: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(command):
        char = command[index]
        if quote is not None:
            buffer.append(char)
            if char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            buffer.append(char)
            index += 1
            continue
        if char == "\\" and index + 1 < len(command):
            buffer.append(char)
            buffer.append(command[index + 1])
            index += 2
            continue
        if command[index : index + 2] in ("&&", "||"):
            chunks.append("".join(buffer))
            buffer = []
            index += 2
            continue
        if char in (";", "|", "\n"):
            chunks.append("".join(buffer))
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1
    chunks.append("".join(buffer))
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def resolve_invocations(
    command: str, wrappers: tuple[Wrapper, ...] = ()
) -> list[tuple[str, list[str]]]:
    """Every `(program, argv-after-program)` a command chunk actually runs.

    The whole point of resolving rather than substring-matching: the REPLACEMENT
    for the bare-pytest rule is `python3 scripts/run_standing_pytest.py`, whose
    text contains `pytest`. A reader that asks "does this mention pytest" reports
    the fix as the defect. This resolves the program to
    `scripts/run_standing_pytest.py` and the rule never fires on it.

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


# A command written in prose is usually fenced or inline-coded. Both are read;
# what is NOT read is a command a document merely alludes to in words, which is
# blind-class item 3.
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")


def iter_document_commands(text: str) -> list[tuple[int, str]]:
    """Every command-looking span in a markdown body, with its 1-based line.

    Fenced blocks contribute their content lines; inline code spans contribute
    their content. Ordinary prose contributes nothing — a sentence naming a
    command in words is invisible here, deliberately, because a reader that
    matched prose would fire on this module's own docstring.
    """
    found: list[tuple[int, str]] = []
    in_fence = False
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            if stripped:
                found.append((number, stripped))
            continue
        for span in _INLINE_CODE_RE.findall(raw):
            if span.strip():
                found.append((number, span.strip()))
    return found


_UNQUOTE_RE = re.compile(r"""^(['"])(.*)\1$""")


def _unquote(value: str) -> str:
    stripped = value.strip()
    match = _UNQUOTE_RE.match(stripped)
    if match:
        return match.group(2)
    # A `#` is only a comment OUTSIDE quotes; one inside the command is part of it.
    return stripped.split(" #", 1)[0].strip()


def read_config_literal(text: str, key: str) -> list[tuple[int, str]]:
    """Every `key = "..."` / `key: "..."` assignment in a config body, with lines.

    Lives here rather than in either caller because both the repo gate and the
    exported consumer inventory need it, and the first draft of this slice wrote
    it twice — where the second copy silently matched the whole
    `test-command = "..."` LINE as if it were the command, resolved the program to
    `test-command`, and reported a clean tree over a dominated literal. Measured,
    not hypothesised.

    Deliberately a line reader rather than a TOML/YAML parser, so one reader
    serves `cosmic-ray.toml`, a YAML adapter, and whatever a consuming repo points
    at. What it gives up: a key is matched by NAME, not by its full table path, and
    a multi-line or computed value is invisible. Both are blind-class item 3.
    """
    pattern = re.compile(rf"^\s*(?:['\"])?{re.escape(key)}(?:['\"])?\s*[=:]\s*(\S.*)$")
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = pattern.match(line)
        if match:
            value = _unquote(match.group(1))
            if value:
                found.append((number, value))
    return found


def scan_document(text: str, registry: Registry, *, site: str) -> list[Finding]:
    """Every dominated command PRESCRIBED by a document body."""
    findings: list[Finding] = []
    for number, command in iter_document_commands(text):
        finding = classify_site(command, registry, site=site, line=number)
        if finding is not None:
            findings.append(finding)
    return findings


def unbudgeted_basis(queue_label: str | None) -> str:
    """Why a discovered command is reported as named by no budgeted label.

    ONE owner for this sentence. It was written twice -- once in the repo gate,
    once in the exported inventory -- and a round-2 reviewer named that as the
    same drift shape this slice consolidated `budgeted_label_union` to avoid. It
    is a verdict sentence on two proof surfaces, so it gets one home.

    The wording is deliberately narrow. "No budgeted label names this command" is
    NOT "nothing bounds its runtime": a config literal can carry no queue label at
    all, so that seam is structurally always-report, and the gate that spawns the
    literal may well carry its own bar.
    """
    if not queue_label:
        return (
            "config literal: carries no queue label by construction, so no budgeted "
            "label can name it. This does NOT establish that nothing bounds its "
            "runtime -- the gate that spawns it may carry its own bar."
        )
    return f"queue label {queue_label!r} has no budget entry"


def finding_message(finding: Finding) -> str:
    """The refusal text. It names the replacement, because a refusal that does not
    say what it wants is one an author routes around rather than obeys."""
    where = f"{finding.site}:{finding.line}" if finding.line is not None else finding.site
    return (
        f"{where}: `{finding.command}` is a dominated command "
        f"({finding.rule_id}). Use `{finding.replacement}` instead. {finding.reason}"
    )
