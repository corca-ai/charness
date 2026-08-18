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

VERDICTS = {
    # Calls into `adapter_version_verdict` and refuses.
    "guarded": "adapter_version_verdict",
    # Reads `errors`/`valid` itself and refuses or degrades deliberately.
    "safe-checks-errors": None,
    # Reads a payload but nothing it reads can mis-steer anything.
    "safe-not-consequential": None,
    # Would use a charness default where the repo declared otherwise. Known and accepted.
    "accepted-risk-unguarded": None,
    # Never reads a version at all -- a different defect wearing the same symptom.
    "no-version-validation": None,
}


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
        verdict = entry.get("verdict")
        if verdict not in VERDICTS:
            problems.append(f"{rel}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
            continue
        if not (entry.get("reason") or "").strip():
            problems.append(f"{rel}: verdict `{verdict}` carries no reason")
        marker = VERDICTS[verdict]
        if marker and marker not in (repo_root / rel).read_text(encoding="utf-8"):
            problems.append(
                f"{rel}: classified `{verdict}` but does not reference `{marker}`. "
                "This is the one verdict with a structural witness; the others are prose."
            )

    for rel in sorted(set(declared) - set(live)):
        problems.append(
            f"{rel}: classified in {MANIFEST_REL} but has no adapter call site. "
            "A stale row makes the census report coverage it no longer has."
        )

    counts: dict[str, int] = {}
    for rel in live:
        verdict = (declared.get(rel) or {}).get("verdict", "UNCLASSIFIED")
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
    "a consumer added since the last scan of a path outside SCAN_ROOTS is invisible",
)


def _list_consumers(repo_root: Path) -> int:
    """Answer "who reads this producer" for the adapter-loader SHAPE, in one call.

    `#599`'s question has two halves and they belong to two surfaces. `what_reads_this.py`
    owns a LITERAL name and answers it well. It cannot express a shape, and the gap is not
    a matter of taste: measured on this tree, `_is_adapter_loader_name` matches 27 distinct
    loader names, so the shape question via `--symbol` is 27 calls -- and one of them,
    `load_adapter`, returns 443 references across 5970 files, overwhelmingly prose in
    artifacts. The same question here is one call returning 121 files, every one holding a
    real adapter-payload call site.

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
    for verdict in sorted(counts):
        print(f"  {verdict}: {counts[verdict]}")
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
    print(f"  total classified: {sum(counts.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
