#!/usr/bin/env python3
"""The ARMED tier: which declared adapter keys reach an operator, and when it may speak.

Split out of `adapter_key_registry.py` when that module crossed the length cap. The seam
is a concept boundary, not a line-count spill (D33): the registry CLASSIFIES a declared
key against the readers it can find, and reports every gap state. This module decides
which of those states an operator is warned about, and -- the part that had to be built --
refuses to render the verdict at all when the corpus behind it is not visible.

WHY THE PRECONDITION IS THE POINT. `find_readers` scans `<repo_root>/scripts` and
`<repo_root>/skills`. In THIS tree those hold the adapter readers, so an empty parse list
means the key is genuinely unread and `unknown` is sound. Ship the same code to a consumer
and the premise inverts: the readers are in the installed plugin, `_is_reader_file`
excludes `plugins`, the corpus is empty, and every non-shared-core key resolves `unknown`.
Measured through the shipped mirror at three-for-three on `gate_commands`,
`product_surfaces`, `startup_probes` -- correct, documented, required keys, all warned.

Note what the repo did to itself: it refused to arm `reader-elsewhere` at a measured 13%
false-positive rate for being a wolf-crier, then shipped `unknown` at ~100% in the
population the arming was justified by -- because the rate was measured in the only tree
where it was low. `reader_corpus_established` is the missing precondition.

THIS MODULE IS NOT A READER, and the exclusion is load-bearing rather than tidy. The prose
above quotes real adapter key names, and `find_readers` counts any string constant equal to
a key as a parse -- so without an `EXCLUDED_READERS` entry this file would report itself as
the owner of `gate_commands`, and the instrument would manufacture the evidence it then
reports. `adapter_key_registry.py` learned this from its own first run; the split inherited
the hazard along with the prose.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple

from scripts.adapter_key_registry import (
    SHARED_CORE_OWNER,
    _adapter_lib,
    _is_reader_file,
    iter_reader_files,
    resolve_key,
)


def _load_yaml_file_report(path: Path) -> tuple[Any, list[str]]:
    """Parse ``path`` and also return the operator-facing lines the parser could not read.

    `load_yaml_file` alone was the whole of `#530`'s blind spot on the indent axis: the
    loader ALREADY records every line it dropped, and this module threw that evidence away
    at the call site, then reported `0 unreconciled declared key(s)` over a file whose key
    it had never seen. One stray leading space is the commonest YAML typo there is, and it
    does not reach `declared` at all -- so the key-state tier cannot reach it by any
    widening of `WARN_STATES`. It is a different fact and it needs a different channel.
    """
    lib = _adapter_lib()
    parsed, uninterpreted = lib.load_yaml_file_report(path)
    return parsed, lib.uninterpreted_warnings(uninterpreted)



WARN_STATES = ("unknown",)


class WarnTierResult(NamedTuple):
    """What the tier ESTABLISHED, kept separate from what it FOUND.

    Two facts that an operator reads identically as a bare empty list, and must not:
    "I read the readers and none of them owns this key" and "I never had the readers".
    `scope_established` is the discriminator, and it is in the return type rather than a
    sibling predicate so a caller cannot render the verdict without having been handed the
    reason it is renderable.
    """

    findings: list[dict[str, str]]
    uninterpreted: list[dict[str, str]]
    scope_established: bool


def reader_corpus_established(repo_root: Path) -> bool:
    """Can this tree answer "which module reads this key?" at all?

    `find_readers` scans `repo_root/scripts` and `repo_root/skills`. In THIS repo those
    hold the adapter readers, so an empty parse list means the key is genuinely unread. In
    a CONSUMER repo they hold the consumer's own code -- the readers live in the installed
    plugin, which `_is_reader_file` excludes by design -- so the parse list is empty for
    every key and `unknown` fires on correct, documented, required declarations. Measured
    at exactly that: a fixture declaring `gate_commands`, `product_surfaces` and
    `startup_probes` -- three correct charness keys -- drew three `is unknown` warnings
    from the SHIPPED mirror. The tier's own design memo refused to arm `reader-elsewhere`
    at a 13% false-positive rate for being a wolf-crier; this is ~100% in the population
    the warn tier ships to.

    The predicate is the shared core's own owner, not a file count. A count would answer
    "is there Python here", which any consumer satisfies while owning none of these
    readers. `SHARED_CORE_OWNER` is the module that DEFINES the adapter contract whose keys
    this tier adjudicates, and `shared-core` already names it as owner -- so its presence is
    the same claim the tier already makes elsewhere, checked instead of assumed.

    NECESSARY, NOT SUFFICIENT, and this function must not be read as more. What it proves is
    narrow and exact: the shared core is INSIDE the corpus this tier is about to scan. It
    does not prove the corpus can answer any particular key -- a tree holding that one file
    and nothing else satisfies it while every non-shared-core key still resolves `unknown`.
    This slice's own test helper builds exactly that tree, which is why two tests had to
    write a REAL reader before they could claim discrimination. The guard removes a
    ~100%-false-positive population; it does not certify the remainder, and no caller should
    read `scope_established` as "the verdicts that follow are trustworthy".

    ASKED OF `iter_reader_files`, NOT OF `Path.is_file`, and the difference is a measured
    blocker rather than a preference. The first cut of this function tested
    `(repo_root / SHARED_CORE_OWNER).is_file()` -- a PROXY for corpus membership, and one
    that disagrees with the corpus builder on the tree most like what consumers receive.
    `_is_reader_file` drops any path containing a `plugins` component, so with
    `--repo-root plugins/charness` the shared core is `is_file()` while EVERY candidate
    reader is excluded: corpus empty, `established` true, and the tier warned over the 19
    correct shipped examples that root exposes (16 `skills/*` + 3 `integrations/*`; there is
    no `plugins/charness/.agents/`). Measured at 126 false WARNINGs with
    `126 unreconciled declared key(s) across 19 declaring file(s)` -- the repair reproducing
    the defect it was written to remove, at a larger scale than the original. Asking the
    corpus builder makes the predicate answer the question its own name asks.

    Through `iter_reader_files` rather than the `_reader_literals` CACHE, deliberately. The
    cache is keyed by `repo_root` and populated once, so reading the corpus through it makes
    this answer depend on whether something else scanned the same root earlier in the
    process -- a predicate whose value changes with call order, inside the module that
    exists to stop order-dependent verdicts. Production calls this once per run and would
    never have noticed; a test caught it immediately. `iter_reader_files` is an `rglob` with
    no parsing, and the key pass dominates it.
    """
    return any(str(path.relative_to(repo_root)) == SHARED_CORE_OWNER for path in iter_reader_files(repo_root))


def unestablished_corpus_reason(repo_root: Path) -> str:
    """The operator-facing reason, owned BY the predicate rather than by its caller.

    Round 2 caught the first version of this sentence living in `validate_adapters.py` and
    saying `SHARED_CORE_OWNER is not readable from <root>` -- which is FALSE in the one tree
    the whole guard was written for. Under `--repo-root plugins/charness` the shared core is
    present and perfectly readable (packaging REQUIRES it there); it is excluded from the
    corpus by `_is_reader_file`'s `plugins` clause. An operator acting on "not readable"
    would go looking for a missing file or a permission bit and find neither, so the tier
    would have been emitting exactly the unactionable warning its design memo refuses.

    Two failures, one cause: the message stated a fact the predicate never checked, and it
    lived in a different module from the predicate -- a second declaration of the guard's
    meaning, reconciled by nobody, which is this module's own named anti-pattern. Keeping
    the reason next to `reader_corpus_established` is what stops them drifting apart again.
    """
    owner = repo_root / SHARED_CORE_OWNER
    if owner.exists() and not _is_reader_file(owner):
        excluded = ", ".join(part for part in ("plugins", "__pycache__") if part in owner.parts)
        return (
            f"{SHARED_CORE_OWNER} exists at {repo_root} but is excluded from the reader corpus "
            f"(path component: {excluded}); a generated mirror is not scanned, so no reader is visible here"
        )
    return (
        f"{SHARED_CORE_OWNER} is not inside the scanned reader corpus at {repo_root}; the readers this "
        "tier reasons about are not visible from this root"
    )


def unreconciled_keys(repo_root: Path, paths: list[Path]) -> WarnTierResult:
    """Declared keys that reach an ARMED state, for the operator-visible warn tier.

    Renders the key verdict ONLY when `reader_corpus_established` says the readers are
    visible from `repo_root`; that function owns why, and `WarnTierResult` owns why the
    answer travels in the return type instead of being left for a caller to remember. The
    uninterpreted-line channel is unconditional.

    Only `WARN_STATES` -- `unknown` -- reaches `findings`; `uninterpreted` and
    `scope_established` are separate channels and are not key states. The module docstring owns why
    `reader-elsewhere` is excluded (measured 13% association residue, one instance inside
    a shipped example); this function is where that decision is executable rather than
    prose, so widening the tier means editing `WARN_STATES` and re-measuring, not quietly
    adding a state at a call site.

    NO `associated` ARGUMENT, AND THAT IS NOT A WEAKENING. `resolve_key` reaches `unknown`
    only when `parsing` is empty, and `scoped` is a subset of `parsing` -- so the scoped
    and unscoped verdicts are identical for exactly this state, and only for it. Skipping
    it also skips `associated_modules`/`_reference_edges`, the whole import-graph closure,
    which is the expensive half: over `survey`'s full 37-adapter / 445-key population the
    same walk costs 4.6s with the closure and 3.1s without it. That
    matters because `validate_adapters.py` runs at commit time, and a gate that gets slow
    is a gate that gets moved somewhere it stops running. The equivalence is pinned by
    test, not left to this comment: a future state added to `WARN_STATES` would NOT
    inherit it.
    """
    established = reader_corpus_established(repo_root)
    findings: list[dict[str, str]] = []
    uninterpreted: list[dict[str, str]] = []
    for path in paths:
        # No `relative_to` fallback and no `isinstance(key, str)` guard. Both were written,
        # both SURVIVED the mutation check, and reading why killed them instead: the only
        # caller (`validate_adapters.iter_warn_scope_adapters`) lists paths rooted at this
        # same `repo_root`, so the ValueError branch is unreachable, and this repo's minimal loader coerces every
        # key to `str` (`1:` parses to `"1"`), so the type guard is unreachable too. A
        # branch that cannot run still reads as though a real hazard were handled -- the
        # same false claim this tier exists to warn about, one layer down.
        relative = str(path.relative_to(repo_root))
        declared, dropped_lines = _load_yaml_file_report(path)
        # Unconditional, and deliberately ABOVE the `established` guard: a line the parser
        # could not read is a fact about the FILE, established by the parse itself, and it
        # needs no reader corpus to be true. So this is the one verdict the tier can still
        # honestly render in a consumer repo -- and it is the commonest real typo, which
        # means the scope repair below costs a consumer no coverage it actually had.
        uninterpreted.extend({"adapter": relative, "detail": detail} for detail in dropped_lines)
        if not established:
            continue
        for key in declared:
            resolution = resolve_key(repo_root, key)
            if resolution.state in WARN_STATES:
                findings.append(
                    {"adapter": relative, "key": key, "state": resolution.state, "detail": resolution.detail}
                )
    return WarnTierResult(findings, uninterpreted, established)
