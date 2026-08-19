#!/usr/bin/env python3

"""Every file that reads a resolved adapter payload must be classified, once, in writing.

A reader that cannot speak an adapter's `version` honors NOTHING the repo declared
(`adapter_lib.declared_fields_after_version_check`), so the resolved payload is this
reader's inferred defaults with the refusal in `errors`. Any surface that then acts on
that payload without checking is substituting a charness default for the repo's
declaration -- silently. Measured instances before this gate existed: a release gate
reported a declared mandatory review as `not_configured` and downgraded enforcement to
advisory; the retro gate printed `Validated 0 retro artifact(s).` exit 0 over an artifact
it was handed by name; the debug gate enforced its shipped 180-line ceiling over a repo
that had declared 60.

A census of the consumer set found roughly four in five acting consequentially with no
check. That ratio is why this is a GATE and not a batch of patches: the defect is not any
one file, it is that nothing required a new `load_adapter(...)` caller to say what it does
when the answer is "your declaration was not read". Patching today's list leaves
tomorrow's consumer exactly as unclassified as today's were. The live counts are printed
on every run and live in the manifest, not in this sentence, so they cannot go stale here.

WHAT THIS PROVES: every file containing an adapter-payload call site appears in the
classification manifest with a verdict and a reason, and no manifest row names a file
that no longer has one. That is a completeness property, and it is the whole point --
an unclassified consumer fails here rather than being discovered by a consuming repo.

BLIND CLASS -- what this mechanism CANNOT see, stated before its first acceptance test:

* It cannot tell a load-bearing check from a mention. `safe-checks-errors` is verified by
  the file referencing `errors`/`valid` at all; a file that echoes `errors` into an unused
  output field while continuing to act on defaulted data passes. That is a real pattern in
  this repo (`survey_verification.py` echoes `adapter_valid` and never branches on it), and
  distinguishing it from a deliberate disclosed-degradation design is a human judgment --
  which is what the manifest's `reason` exists to record.
* Enumeration has two rules -- a resolver call site, and an adapter-file literal paired
  with a YAML-parsing call -- and a consumer that matches NEITHER is invisible. The gap
  that remains after both: a file that reads an adapter through a helper in another
  module, holding no literal and parsing no YAML itself. Nothing here can see that.
* It classifies FILES, not call sites. A file with one guarded and one unguarded call site
  renders as whatever its row says.
* `accepted-risk-unguarded` is an accepted state, not a fixed one. The count of those rows
  is the honest measure of remaining debt, and it is reported on every run.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_REL = "scripts/adapter-consumer-classification.json"

# Roots scanned. `plugins/` is a generated mirror of these, so scanning it would double
# every row and make the manifest drift on every export.
SCAN_ROOTS = ("scripts", "skills")

# A call obtains an adapter payload when its name mentions an adapter and it reads or
# resolves one. Matched on SHAPE rather than an enumerated name list, because the list was
# measured against a grep census and lost eight real consumers to spellings nobody thought
# to enumerate -- `load_quality_adapter_strict` is a `load_*_adapter*` that a
# `startswith/endswith` pair does not catch. `resolve_adapter_line_budget` qualifies for
# the same reason its callers do: it reads a payload on the caller's behalf and returns a
# ceiling, which is the same consequential act one layer down.
CALL_PREFIXES = ("load_", "resolve_")
CALL_TOKEN = "adapter"
# The second enumeration rule's two witnesses; see `_reads_adapter_file_directly`.
ADAPTER_FILE_SUFFIX = "-adapter.yaml"
YAML_CALLS = frozenset({"safe_load", "load_yaml", "load_yaml_file", "load_yaml_file_report", "full_load"})

# Files that DEFINE the resolver surface rather than consume it. A resolver classifying
# itself would be circular, and the version contract they implement is covered by
# `tests/quality_gates/test_adapter_version_reconciliation.py` instead.
#
# `_adapter_policy.py` is deliberately NOT excluded: achieve's defines a resolver AND
# consumes its own payload in `release_surface_tokens`, and excluding it would have hidden
# a consumer the census independently found acting on defaults.
EXCLUDED_NAMES = (
    "resolve_adapter.py",
    "adapter_lib.py",
    "adapter_field_application.py",
    "adapter_validators.py",
    "adapter_version_verdict.py",
    "simple_skill_adapter_lib.py",
)
EXCLUDED_SUFFIXES = ("_adapter_lib.py",)

# The `guarded` witness. Round 2 of the slice-5 review found the previous witness --
# the bare module name `adapter_version_verdict` -- unable to distinguish a file that asks
# the RIGHT question from one that merely imports the module. Three files were passing as
# `guarded` while asking `version_refused`, which answers False for a parser refusal, so
# the same "nothing declared is honored" state walked past them; one of the three wrote two
# durable files to a directory the repo never named, exit 0. A witness that a verdict can
# satisfy without holding the property is not a witness.
#
# Any ONE of these is sufficient, and a bare `version_refused` is deliberately not among
# them: `declarations_unhonored` is the condition, and the two message entrypoints ask it.
GUARDED_WITNESSES = (
    "declarations_unhonored",
    "unspeakable_version_message",
    "refuse_unspeakable_version",
)

# THE COVERAGE LEVEL, which one `guarded` token could not say (#675). The predecessor's own
# measurement: by the end of its slice 5 the single token covered four materially different
# states, and this gate saw one of them -- so "how much of this debt is actually closed" was
# only answerable by reading paragraphs, and two rows with the same token could differ by
# whether a one-character typo bypassed them.
#
# The axis is what the CONSUMER asks, not what its resolver reports. `#673` made all
# sixteen PUBLIC resolvers report all three doors, so that axis is uniform across every
# guarded row -- traced, not assumed. It is NOT uniform repo-wide: `cautilus_adapter_lib`
# and `proof_semantics_adapter_lib` still call `load_yaml_file` bare, and four consumers
# read through them. Those four are `safe-checks-errors`, so no guarded row loses a level
# here -- but 55 `safe-checks-errors` classifications now carry one token over materially
# different coverage, which is this same defect standing on the largest class. Recorded in
# the goal's decision queue rather than silently split here.
#
# Keyed on the consumer the level is real and was measured before this vocabulary was
# written -- 32 rows cover all three doors, three cover only the ERROR channel and are blind
# to a silently dropped line, which is a live one-typo bypass.
#
# `unspeakable_version_message` and `refuse_unspeakable_version` check `declarations_dropped`
# themselves, so calling either covers all three doors. `declarations_unhonored` ALONE is a
# predicate over `errors` and cannot see the third.
ALL_DOOR_ENTRYPOINTS = ("unspeakable_version_message", "refuse_unspeakable_version")
DROPPED_DOOR_WITNESS = "declarations_dropped"
CONDITION_WITNESS = "declarations_unhonored"

GUARDED_ALL_DOORS = "guarded-all-doors"
GUARDED_ERRORS_ONLY = "guarded-errors-only"
GUARDED_UPSTREAM = "guarded-upstream"
GUARDED_LEVELS = (GUARDED_ALL_DOORS, GUARDED_ERRORS_ONLY, GUARDED_UPSTREAM)


def measured_guard_level(called: set[str]) -> str | None:
    """The level a file's own calls establish, or None when it guards nothing itself.

    Returned rather than compared so the gate can refuse a row that claims MORE than it
    holds AND one that claims less -- the previous witness only checked membership, so an
    over-conservative row was never checked at all and one sat wrong through a whole slice.

    BLIND CLASS OF THE LEVEL ITSELF, which the module's list above did not cover and a round-1
    review enumerated. This is CALL PRESENCE, not load-bearing-ness: a witness called in dead
    code, inside a never-called helper, with the wrong argument, with its result discarded, or
    shadowed by a local function of the same name all read as guarded. That is not
    hypothetical -- `refresh_current_pointer` carried an unreachable `refuse_unspeakable_version`
    block whose AST call satisfied this witness, and deleting it left every assertion green.
    It is also ALIAS-BLIND: `import declarations_unhonored as du` then `du(errors)` reads as
    unguarded and forces a wrong row. And a guard behind a runtime `if` (`find_inline_prompt_bulk`
    returns None when the module is absent) is recorded unconditionally.

    `unspeakable_version_message` covering all three doors is true on its RETURNING path only;
    its `except Exception` swallow arm answers None with every door dead, so `guarded-all-doors`
    is precise about which predicate is asked and not about whether a raising loader bypasses it.

    THREE MORE LIMITS, added after a round-2 review pointed out that an enumeration reading
    complete is the failure this paragraph exists to prevent:

    - ORDERING is invisible. A file that guards AFTER acting on `data` measures the same as
      one that guards before. That is not the dead-code case -- the guard is live and
      load-bearing, just late -- and this repo already argues position matters
      (`scaffold_quality_artifact`'s row: "guarded at the READ SITE, not `main()`").
    - `covering_rows` IS UNVERIFIED IN BOTH DIRECTIONS. The gate checks each named row exists
      and holds a guard, directly or up its own chain. It never checks the named row actually
      CALLS the covered symbol, nor that the list is COMPLETE. Two of the first five lists
      shipped wrong, both derived from prose rather than the call graph.
    - A covering row's guard may sit in an ENTRYPOINT the real caller bypasses. `guarded` is
      file-granular; coverage is call-site-granular. A caller importing a re-exported helper
      never reaches the `main()` the covering row was credited for.
    """
    if set(ALL_DOOR_ENTRYPOINTS) & called:
        return GUARDED_ALL_DOORS
    if CONDITION_WITNESS in called:
        return GUARDED_ALL_DOORS if DROPPED_DOOR_WITNESS in called else GUARDED_ERRORS_ONLY
    return None


VERDICTS = {
    # Refuses on the CONDITION and covers all three doors -- a refused version, a refused
    # parse, and a silently DROPPED line.
    GUARDED_ALL_DOORS: GUARDED_WITNESSES,
    # Refuses on the condition through `errors` only, so a line the parser silently drops
    # walks past it. A real level, not a courtesy: `declarations_unhonored` is a predicate
    # over `errors` and answers False while `errors: []`, `valid: True`, and the repo's
    # declaration is gone.
    GUARDED_ERRORS_ONLY: GUARDED_WITNESSES,
    # Cannot guard itself -- an injected loader, or a loader that refuses upstream -- and
    # every production caller is guarded. Owes `covering_rows`, because "every caller"
    # is a claim about an enumerated set and the census's own blind class is that it
    # classifies FILES, not call sites.
    GUARDED_UPSTREAM: None,
    # Reads `errors`/`valid` itself and refuses or degrades deliberately.
    "safe-checks-errors": None,
    # Reads a payload but nothing it reads can mis-steer anything.
    "safe-not-consequential": None,
    # Would use a charness default where the repo declared otherwise. Known and accepted.
    "accepted-risk-unguarded": None,
    # Never reads a version at all -- a different defect wearing the same symptom.
    "no-version-validation": None,
}


def _covers(rel: str, declared: dict, seen: set[str]) -> bool:
    """Does this row hold a guard, directly or through its OWN upstream rows?

    TWO HOPS ARE LEGITIMATE and the first cut forbade them, which is worse than a missing
    check: a round-2 review found the manifest had OMITTED a real caller
    (`scaffold_artifact_lib`, itself `guarded-upstream` and chaining to two guarded
    scaffolds) because naming it would have tripped the gate. The enumerated set was being
    shaped by what the checker accepts rather than by the call graph -- which is the
    measurement distortion `#675` exists to stop, reproduced one level up by its own gate.

    `seen` closes the cycle A-covers-B-covers-A, which would otherwise recurse forever or,
    read charitably, let two unguarded rows vouch for each other.
    """
    if rel in seen or rel not in declared:
        return False
    seen = seen | {rel}
    for row in row_verdicts(declared[rel]):
        verdict = row.get("verdict")
        if verdict in (GUARDED_ALL_DOORS, GUARDED_ERRORS_ONLY):
            return True
        if verdict == GUARDED_UPSTREAM:
            upstream = row.get("covering_rows")
            if isinstance(upstream, list) and any(
                isinstance(item, str) and _covers(item, declared, seen) for item in upstream
            ):
                return True
    return False


def _guard_level_problems(
    rel: str, verdict: str, row: dict, called: set[str], declared: dict
) -> list[str]:
    """Refuse a guarded row whose declared LEVEL is not the level its own calls establish.

    BOTH DIRECTIONS, and the second is why this replaces a membership check. The previous
    witness asked only "does this file call one of three names", so it could not tell an
    all-doors guard from an errors-only one -- the state `#675` reports -- and it never
    checked a non-`guarded` row at all, so an OVER-conservative row was invisible. One sat
    wrong through an entire slice: `resolve_artifact_path` was recorded
    `accepted-risk-unguarded` with a reason asserting the file references no verdict
    predicate, while the file imported the module and called two of them.
    """
    problems: list[str] = []
    measured = measured_guard_level(called)
    if verdict == GUARDED_UPSTREAM:
        if measured is not None:
            problems.append(
                f"{rel}: classified `{GUARDED_UPSTREAM}` but guards ITSELF ({measured}). "
                "A file that asks the condition is not upstream-covered; record the level it holds."
            )
        callers = row.get("covering_rows")
        if not isinstance(callers, list) or not callers:
            problems.append(
                f"{rel}: `{GUARDED_UPSTREAM}` owes a non-empty `covering_rows` list. "
                "\"Every caller is guarded\" is a claim about an ENUMERATED set, and this "
                "census's own blind class is that it classifies files rather than call sites."
            )
            return problems
        for caller in callers:
            if not isinstance(caller, str):
                # A non-string entry made `caller not in declared` raise `TypeError:
                # unhashable type` -- an uncaught traceback out of a proof surface where a
                # named refusal belongs.
                problems.append(
                    f"{rel}: `covering_rows` entries must be repo-relative paths; got {caller!r}"
                )
                continue
            if caller not in declared:
                problems.append(
                    f"{rel}: names `{caller}` as a covering row, but it carries no census row"
                )
            elif not _covers(caller, declared, seen={rel}):
                problems.append(
                    f"{rel}: names `{caller}` as a covering row, but that row is not itself "
                    "guarded -- a chain of upstream coverage ending in nothing is not coverage"
                )
        return problems
    if measured is None:
        dropped_only = DROPPED_DOOR_WITNESS in called
        problems.append(
            f"{rel}: classified `{verdict}` but asks only `{DROPPED_DOOR_WITNESS}`, which sees "
            "the dropped-line door and neither of the other two. There is no level for that "
            "alone; ask the condition too."
            if dropped_only else
            f"{rel}: classified `{verdict}` but references none of "
            f"{', '.join(f'`{m}`' for m in GUARDED_WITNESSES)}. A bare `version_refused` does "
            "NOT satisfy it: it answers False for a parser refusal, which leaves the same "
            f"charness defaults in `data`. If the property comes from upstream, say "
            f"`{GUARDED_UPSTREAM}` and name the rows. If the witness IS called but under an "
            "alias, this check cannot see it -- import the name directly."
        )
    elif measured != verdict:
        problems.append(
            f"{rel}: classified `{verdict}` but its own calls establish `{measured}`. "
            f"`{GUARDED_ERRORS_ONLY}` asks a predicate over `errors` and cannot see a line the "
            f"parser silently DROPPED; `{GUARDED_ALL_DOORS}` covers that door too, through "
            f"`{'` or `'.join(ALL_DOOR_ENTRYPOINTS)}` or an explicit `{DROPPED_DOOR_WITNESS}`."
        )
    return problems


def _is_adapter_loader_name(name: str) -> bool:
    # A leading underscore is a visibility marker, not a different act: eight consumers
    # were lost to `_load_adapter` / `_load_quality_adapter` before this strip.
    name = name.lstrip("_")
    return CALL_TOKEN in name and name.startswith(CALL_PREFIXES)


def _references_adapter_loader(node: ast.AST) -> bool:
    """A loader NAMED anywhere, not merely called.

    Calls alone missed a guarded consumer: `validate_retro_artifact.py` never calls its
    loader, it PASSES it -- `unspeakable_version_message(_output_dir.load_retro_adapter,
    ...)` -- so the loader appears only in reference position and the file was absent from
    its own census. A rule that cannot see the repo's own guarded example is not a census.

    Matching references over-matches by design: a file that merely re-exports a loader now
    needs a row. That direction is the safe one -- an extra row costs a sentence, a missing
    row costs a consumer nobody classified.
    """
    if isinstance(node, ast.Attribute):
        return _is_adapter_loader_name(node.attr)
    if isinstance(node, ast.Name):
        return _is_adapter_loader_name(node.id)
    return False


def _excluded(path: Path) -> bool:
    return path.name in EXCLUDED_NAMES or path.name.endswith(EXCLUDED_SUFFIXES)


def _call_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if isinstance(name, str):
                names.add(name)
    return names


def _reads_adapter_file_directly(tree: ast.AST) -> bool:
    """Names an adapter file AND parses YAML itself -- a raw read that bypasses a resolver.

    The second enumeration rule, and the one that closes this gate's sharpest blind spot.
    Keying only on the resolver symbol made every consumer that reads
    `.agents/<x>-adapter.yaml` through a raw YAML load invisible -- and those are worse
    than the ones that miss a check, because they never read a `version` at all, so there
    is no `errors` for anyone to check. Two were found by hand; being found by hand is
    exactly what this rule replaces.

    BOTH conditions, because the literal alone does not work: measured, an
    `-adapter.yaml` literal appears in 48 files that only NAME one in a message or a
    registry -- including this gate's own refusal text. Requiring a YAML-parsing call in
    the same file cuts that to the files that actually read one, and the pairing is what
    makes the rule about behavior rather than about a string.

    The cost is stated rather than hidden: a file that reads an adapter through a helper
    in ANOTHER module, with no literal and no yaml call of its own, is invisible to both
    rules. Nothing here can see that, and no amount of narrowing this rule would.
    """
    named = any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.endswith(ADAPTER_FILE_SUFFIX)
        for node in ast.walk(tree)
    )
    return named and bool(_call_names(tree) & YAML_CALLS)


def row_verdicts(entry: dict) -> list[dict]:
    """The (verdict, reason) pairs a row declares, as a list of ONE OR MORE.

    A FILE MAY CARRY MORE THAN ONE DEFECT CLASS, and the single-verdict schema this
    replaces could not say so. Measured instance:
    `scripts/build_retro_lesson_selection_index.py` calls `load_adapter` at line 55 and
    reads the payload with no `errors` check (`accepted-risk-unguarded`) AND separately
    reads `.agents/retro-adapter.yaml` raw at line 33 with no version reconciliation
    (`no-version-validation`). Under one-verdict-per-file it was filed as the first only,
    which would have paid it down under the wrong remedy -- the two classes need
    different repairs, and the row would have read "done" with half of it live.

    Two shapes, one normalized answer. `{"verdict", "reason"}` stays the form for the
    single-class rows, which is almost all of them and which this change deliberately does
    not churn; `{"verdicts": [{"verdict", "reason"}, ...]}` is the multi-class form. Each
    class carries its OWN reason, because the reasons differ per class and a shared one
    would describe at most half the row.
    """
    if not isinstance(entry, dict):
        # A hand-edited manifest entry that is a string or a list used to reach `{**entry}`
        # and raise `TypeError` uncaught -- the same class the `covering_rows` element check
        # repaired, one level out, on the same proof surface.
        return []
    if "verdicts" in entry and "verdict" in entry:
        # BOTH SHAPES is a row declaring a class the checker would silently drop: the
        # `verdicts` branch wins and the top-level `verdict` vanishes from the problems loop
        # AND from the count vector. On a census whose stated purpose is that a file may
        # carry more than one defect class, a silently ignored declared class is the exact
        # failure mode. Surfaced as a sentinel the caller refuses.
        return [{"verdict": None, "reason": None, "__shape_error__": "declares both `verdict` and `verdicts`"}]
    if "verdicts" in entry:
        rows = entry["verdicts"]
        if not isinstance(rows, list):
            return []
        # THE ENTRY'S extra keys reach each sub-row here too. The first fix was one-sided --
        # only the single-verdict branch spread them -- so an entry-level `covering_rows`
        # beside a `verdicts` list was still dropped and the gate reported a row owing a
        # list it plainly carried. The identical defect, unfixed, in the other shape. A
        # sub-row's own keys win, so a per-verdict `covering_rows` still overrides.
        extra = {k: v for k, v in entry.items() if k not in ("verdicts", "verdict", "reason")}
        # A non-dict ELEMENT is refused, not filtered. Filtering it was asymmetric with the
        # `covering_rows` element check added in the same fold, which refuses by name for
        # exactly the reason this one was silently lossy.
        return [
            {**extra, **row} if isinstance(row, dict)
            else {"verdict": None, "reason": None, "__shape_error__": f"verdict entry {row!r} is not a mapping"}
            for row in rows
        ]
    # CARRIES THE WHOLE ENTRY's extra keys, not just verdict+reason. `guarded-upstream`
    # owes `covering_rows`, and rebuilding a two-key dict here dropped it -- the row was
    # written correctly and the gate reported it missing, which is a checker losing evidence
    # rather than a row lacking it.
    return [{**entry, "verdict": entry.get("verdict"), "reason": entry.get("reason")}]


def consumer_files(repo_root: Path) -> list[str]:
    """Files with at least one adapter-payload call site, as repo-relative posix paths."""
    found: set[str] = set()
    for root in SCAN_ROOTS:
        for path in sorted((repo_root / root).rglob("*.py")):
            if _excluded(path):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                # A file this gate cannot parse is reported as a hard error rather than
                # skipped: silently dropping it would shrink the denominator, which is
                # the one thing a completeness census must never do.
                raise SystemExit(f"{path}: could not be parsed for adapter call sites")
            if any(_references_adapter_loader(node) for node in ast.walk(tree)) or _reads_adapter_file_directly(tree):
                found.add(path.relative_to(repo_root).as_posix())
    return sorted(found)


def load_manifest(path: Path) -> dict:
    """An ABSENT manifest is an empty one, not a hard error.

    The refusal has to come from the consumers, not from the file: a tree with no adapter
    consumer has nothing to classify and must pass, and a tree WITH consumers and no
    manifest already fails once per unclassified consumer -- which names them, where
    `missing manifest` would name only the file. Raising here also broke every fixture
    repo that runs the broad lane without carrying charness's own manifest.
    """
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def check(repo_root: Path) -> tuple[list[str], dict[str, int]]:
    """Return (problems, verdict counts)."""
    manifest = load_manifest(repo_root / MANIFEST_REL)
    declared: dict = manifest.get("consumers") or {}
    live = consumer_files(repo_root)
    problems: list[str] = []

    for rel in live:
        entry = declared.get(rel)
        if entry is None:
            problems.append(
                f"{rel}: reads an adapter payload but is not classified in {MANIFEST_REL}. "
                "Add a row saying what it does when the adapter's version was refused."
            )
            continue
        declared_rows = row_verdicts(entry)
        if not declared_rows:
            problems.append(f"{rel}: `verdicts` must be a non-empty list of {{verdict, reason}}")
            continue
        seen: set[str] = set()
        for row in declared_rows:
            if shape_error := row.get("__shape_error__"):
                problems.append(f"{rel}: {shape_error}")
                continue
            verdict = row.get("verdict")
            if verdict not in VERDICTS:
                problems.append(f"{rel}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
                continue
            if verdict in seen:
                # A repeated class is a row saying the same thing twice, which inflates the
                # count vector this gate reports as its running measure.
                problems.append(f"{rel}: declares verdict `{verdict}` more than once")
            seen.add(verdict)
            if not (row.get("reason") or "").strip():
                problems.append(f"{rel}: verdict `{verdict}` carries no reason")
            if verdict in GUARDED_LEVELS:
                # AST, not a substring of the file text. The first cut of this tightening
                # was a substring check and it was mutation-tested: reverting a consumer to
                # the narrow `version_refused` left the gate GREEN, because the repair's own
                # explanatory COMMENT contained the widened name. A witness that a comment
                # can satisfy is the same defect one layer up, so this asks whether the
                # file CALLS one of them.
                called = _call_names(ast.parse((repo_root / rel).read_text(encoding="utf-8")))
                problems.extend(_guard_level_problems(rel, verdict, row, called, declared))

    for rel in sorted(set(declared) - set(live)):
        problems.append(
            f"{rel}: classified in {MANIFEST_REL} but has no adapter call site. "
            "A stale row makes the census report coverage it no longer has."
        )

    # COUNTED PER VERDICT, not per file, now that a file may carry more than one class.
    # So the vector sums to at least the file count and the two numbers are reported
    # separately -- collapsing them would hide exactly the multi-class row this schema
    # exists to make sayable.
    counts: dict[str, int] = {}
    for rel in live:
        entry = declared.get(rel)
        rows = row_verdicts(entry) if entry else [{"verdict": "UNCLASSIFIED"}]
        for row in rows or [{"verdict": "UNCLASSIFIED"}]:
            verdict = row.get("verdict") or "UNCLASSIFIED"
            counts[verdict] = counts.get(verdict, 0) + 1
    return problems, counts


# The blind class travels WITH the answer, never only in this module's docstring. A reader
# who runs the query and gets a list has to be told, at that moment, what the list cannot
# contain -- an enumeration that looks complete is worse than no enumeration, because the
# reader stops looking.
LIST_CONSUMERS_BLIND_CLASS = (
    "a file that reads an adapter through a HELPER in another module, holding no adapter-file "
    "literal and parsing no YAML itself, is invisible here",
    "this enumerates FILES, not call sites: a file with one guarded and one unguarded call "
    "site appears once, and which of its sites are guarded is not answered",
    f"only {' and '.join(SCAN_ROOTS)}/ are scanned, and only *.py within them: a consumer "
    "elsewhere in the repo, or a non-Python one (a shell gate reading an adapter) inside "
    "them, is invisible",
    "rule 2 requires a YAML call from a hand-enumerated name list, so a file holding an "
    "adapter-file literal and parsing it under any other spelling (`yaml.load(...)`, a "
    "module-local reader) is invisible -- the same enumerate-the-names shape rule 1 "
    "deliberately avoids",
    "files matching EXCLUDED_NAMES/EXCLUDED_SUFFIXES are unclassified BY CONSTRUCTION and "
    "never appear here; the compensating control is "
    "tests/quality_gates/test_adapter_version_reconciliation.py",
    "a loader reached through an ALIASED import or getattr does not match the AST rule, so "
    "its file can be absent from this list entirely",
)


def _list_consumers(repo_root: Path) -> int:
    """Answer "who reads this producer" for the adapter-loader SHAPE, in one call.

    `#599`'s question has two halves and they belong to two surfaces. `what_reads_this.py`
    owns a LITERAL name and answers it well. It cannot express a shape, and the gap is not
    a matter of taste: measured on this tree, `_is_adapter_loader_name` matches ~27 distinct
    loader names -- the predicate over-matches deliberately, so a human guessing spellings
    would try fewer -- and one of them, `load_adapter`, returns 446 references across 157
    files (96 source, 38 test, 19 doc, 4 config). That is a real answer and a wide one, for
    one name of ~27. The same question here is one call returning 121 files, each holding at
    least one adapter-payload call site.

    A first version of this docstring said those references were "overwhelmingly prose in
    artifacts". That was false -- they are dominated by source -- and it had been forwarded
    into a convention doc, a test, and the goal artifact before a bounded review recounted
    it. Corrected here rather than quietly dropped, because publishing an unverified
    measurement is the exact class the goal that produced this command exists to stop.

    So this is not a new capability. `consumer_files()` already did the work; it had no
    command surface, which is why the question kept being answered by grep.
    """
    files = consumer_files(repo_root)
    print(f"adapter-payload consumers ({len(files)}):")
    for rel in files:
        print(f"  {rel}")
    print("")
    print("BLIND CLASS -- what this enumeration CANNOT see:")
    for line in LIST_CONSUMERS_BLIND_CLASS:
        print(f"  - {line}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--list-consumers",
        action="store_true",
        help="Read-only: list every file holding an adapter-payload call site, plus what the "
        "enumeration cannot see. Run this BEFORE changing a shared adapter output contract -- "
        "enumeration is cheap and prevents, refusal is expensive and only detects.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    if args.list_consumers:
        return _list_consumers(repo_root)

    problems, counts = check(repo_root)
    print("adapter consumer classification:")
    # ALPHABETICAL, and the ordering code that used to sit here is GONE. It claimed
    # "coverage order, not alphabetical" and for the current token set the two are the SAME
    # order -- `guarded-all-doors` < `guarded-errors-only` < `guarded-upstream` either way --
    # so the code was unobservable and the test asserting it passed with the ordering deleted.
    # A round-2 review named the ordering as untested and proposed the errors-only/upstream
    # pair as the discriminating one; that pair does not discriminate either. What carries the
    # meaning is the callouts below, which do fail when removed.
    for verdict in sorted(counts):
        print(f"  {verdict}: {counts[verdict]}")
    if counts.get(GUARDED_UPSTREAM):
        print(
            f"  UPSTREAM: {counts[GUARDED_UPSTREAM]} consumer(s) hold no guard of their own -- the "
            "property is their enumerated `covering_rows`, and a future caller that forgets is "
            "unguarded again with nothing structural to stop it. NOT a rank on the doors axis."
        )
    if counts.get(GUARDED_ERRORS_ONLY):
        print(
            f"  ERRORS-ONLY: {counts[GUARDED_ERRORS_ONLY]} consumer(s) refuse on `errors` and "
            "cannot see a line the parser silently DROPPED -- a one-typo bypass"
        )
    accepted = counts.get("accepted-risk-unguarded", 0)
    if accepted:
        # Reported on every run, passing or failing. An accepted risk that stops being
        # counted is an accepted risk that stops being decided.
        print(f"  ACCEPTED RISK: {accepted} consumer(s) would use a charness default on a refused version")
    if problems:
        print("", file=sys.stderr)
        for problem in problems:
            print(f"FAIL {problem}", file=sys.stderr)
        return 1
    live_files = len(consumer_files(repo_root))
    print(f"  total classifications: {sum(counts.values())} across {live_files} file(s)")
    if sum(counts.values()) != live_files:
        print(f"  ({sum(counts.values()) - live_files} file(s) carry more than one defect class)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
