"""The repo-wide standalone-import check, proven against the REAL cycle.

A guard that only passes on a healthy tree has established nothing. The measured
instance is `scripts/quality_policy_merge.py`, extracted from
`quality_policy_defaults.py` on 2026-08-06 with a module-level import in both
directions: a cycle that resolves in exactly ONE order, invisible to 4979 passing
tests because every existing importer reached `defaults` first.

That pre-fix version was never committed — the cycle was found by a bounded reviewer
and fixed inside the same commit that created the file — so `_reconstruct_the_cycle`
rebuilds it the one way the defect is defined: hoist the two function-level sibling
imports back to module scope. The reconstruction is verified to produce the exact
`ImportError: ... partially initialized module` from the issue, so it is the defect and
not a lookalike.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.repo_copy import clone_seeded_charness_repo

ROOT = Path(__file__).resolve().parents[2]
MERGE_REL = "scripts/quality_policy_merge.py"


def _reconstruct_the_cycle(source: str) -> str:
    """Hoist the sibling imports out of the functions — the pre-fix shape, exactly."""
    names = sorted(set(re.findall(r"from scripts\.quality_policy_defaults import (\w+)", source)))
    assert names, "the function-level sibling imports are what break the cycle; they are gone"
    hoisted = re.sub(r"[ \t]+from scripts\.quality_policy_defaults import \w+\n", "", source)
    return hoisted.replace(
        "from __future__ import annotations",
        "from __future__ import annotations\n\nfrom scripts.quality_policy_defaults import "
        + ", ".join(names),
        1,
    )


@pytest.fixture
def clean_repo(tmp_path: Path, seeded_charness_repo: Path) -> Path:
    """An isolated copy of this repo. The whole package is copied, not just the module:
    the cycle exists only in relation to `quality_policy_defaults`'s re-export, so a
    module copied on its own would not reproduce it and a check that passed on that copy
    would prove nothing.

    Isolated rather than in-tree because mutating the real checkout lets an xdist worker
    observe a transiently broken module — `check_test_repo_copy_invariants` refuses it,
    and it was right to: the first cut of this file did exactly that.
    """
    return clone_seeded_charness_repo(tmp_path, seeded_charness_repo)


@pytest.fixture
def repo_with_the_real_cycle(clean_repo: Path) -> Path:
    """Reintroduce the defect in the isolated copy."""
    merge = clean_repo / MERGE_REL
    merge.write_text(_reconstruct_the_cycle(merge.read_text(encoding="utf-8")), encoding="utf-8")
    return clean_repo


def _load_check_module():
    import importlib.util

    check = ROOT / "scripts" / "check_standalone_imports.py"
    spec = importlib.util.spec_from_file_location("check_standalone_imports", check)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def _run_check_at(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the REAL check against a throwaway package root."""
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_standalone_imports.py"),
         "--repo-root", str(repo), *args],
        capture_output=True, text=True,
    )


def _run_check(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / "check_standalone_imports.py"),
         "--repo-root", str(repo), *args],
        capture_output=True, text=True,
    )


def _report(result: subprocess.CompletedProcess) -> dict:
    """The check's stdout is unconditionally YAML since the `--json` removal.

    Parsed rather than grepped: the emitter wraps long scalars, so `scope_note` — the
    field carrying the PARTIAL/denominator claim — is split across lines and a substring
    search over raw stdout silently stops matching.
    """
    payload = yaml.safe_load(result.stdout)
    assert isinstance(payload, dict), f"stdout was not a YAML mapping: {result.stdout[:400]!r}"
    return payload


def test_the_reconstruction_really_is_the_issues_cycle(repo_with_the_real_cycle: Path) -> None:
    """Before asking whether the check catches it, prove the fixture reproduces the
    defect and not something that merely fails to import."""
    result = subprocess.run(
        [sys.executable, "-c", "import scripts.quality_policy_merge"],
        cwd=repo_with_the_real_cycle, capture_output=True, text=True,
    )

    assert result.returncode != 0
    assert "partially initialized module 'scripts.quality_policy_merge'" in result.stderr
    assert "circular import" in result.stderr


def test_the_check_catches_the_real_cycle(repo_with_the_real_cycle: Path) -> None:
    """The acceptance criterion: it FAILS on the pre-fix module, not merely passes on a
    clean tree."""
    result = _run_check(repo_with_the_real_cycle)

    assert result.returncode == 1
    payload = _report(result)
    assert payload["verdict"] == "BLOCKED"
    # Membership, not equality: every module that reaches the cycling one fails through
    # the same cycle, so the collateral entries are the defect too. The claim is that
    # the module carrying the defect is named as a CYCLE, with the issue's own text.
    cycles = {item["path"]: item["detail"] for item in payload["cycles"]}
    assert "scripts/quality_policy_merge.py" in cycles, payload
    assert "partially initialized" in cycles["scripts/quality_policy_merge.py"]


def test_a_changed_scope_run_catches_the_cycle_in_the_module_it_was_given(
    repo_with_the_real_cycle: Path,
) -> None:
    """The pre-push lane is where this check will actually run, and the first cut FAILED
    here while passing the full sweep.

    Two load shapes exist in this repo and the check tries both, because a module built
    for direct execution raises a sibling `ModuleNotFoundError` when imported as a
    package member — a wrong-shape error, not a defect. But falling through to the
    `direct` shape after a CYCLE masks it: that shape loads the file as a top-level
    module under a different name, which is not the module the cycle runs through. So
    `--changed` on the one module carrying the defect reported `ok`. A cycle now stops
    the fallback.
    """
    result = _run_check(repo_with_the_real_cycle, "--changed", MERGE_REL)

    assert result.returncode == 1, result.stdout
    assert [item["path"] for item in _report(result)["cycles"]] == [
        "scripts/quality_policy_merge.py"
    ]


def test_a_partial_run_says_so_in_its_own_output(clean_repo: Path) -> None:
    """A partial run must never read as a whole-package verdict — this repo's own
    `partial` lesson, applied to the gate it produced. The scope travels WITH the
    verdict, not in a comment somewhere the reader has to go find."""
    partial = _run_check(clean_repo, "--changed", MERGE_REL)

    assert partial.returncode == 0, partial.stdout
    payload = _report(partial)
    assert payload["scope"] == "partial"
    assert "PARTIAL: checked 1 of" in payload["scope_note"]
    assert "UNCHECKED, not proven clean" in payload["scope_note"]


@pytest.mark.slow_corpus
def test_the_clean_tree_passes_and_says_what_it_covered(clean_repo: Path) -> None:
    """The other half of the same rule: a FULL run states its denominator too, so `ok`
    is a claim about a number rather than an unqualified all-clear."""
    result = _run_check(clean_repo)

    assert result.returncode == 0, result.stdout
    payload = _report(result)
    assert payload["verdict"] == "ok"
    assert re.search(r"checked all \d+ discovered module\(s\)", payload["scope_note"]), payload


def test_the_enumeration_reaches_both_module_families() -> None:
    """The check can only establish what it enumerated, so the enumeration is itself
    load-bearing: a family it misses is unchecked, not clean. Both families are named
    here so a pattern change that silently drops one fails."""
    module = _load_check_module()

    discovered = {path.relative_to(ROOT).as_posix() for path in module.discover_modules(ROOT)}

    assert "scripts/quality_policy_merge.py" in discovered
    assert "skills/public/achieve/scripts/upsert_goal.py" in discovered
    assert not [name for name in discovered if name.endswith("__init__.py")]


def test_an_empty_changed_scope_says_nothing_was_checked(clean_repo: Path) -> None:
    """An empty scope that prints a bare `ok` is a green nobody earned.

    It does not BLOCK — a commit touching only non-module Python legitimately matches
    nothing — but it must say so, and name what matched nothing, so a caller passing
    paths in the wrong shape finds out here instead of reading a pass. This is also the
    regression pin for the resolution bug that produced it: `--changed` paths were
    resolved against the process CWD rather than `--repo-root`, so they matched by luck
    in the real checkout and matched NOTHING anywhere else.
    """
    result = _run_check(clean_repo, "--changed", "docs/index.md")

    assert result.returncode == 0
    payload = _report(result)
    assert "NOTHING WAS CHECKED" in payload["scope_note"]
    assert "unmatched: docs/index.md" in payload["scope_note"]
    assert payload["unmatched_changed"] == ["docs/index.md"]


def test_changed_paths_resolve_against_the_repo_root_not_the_cwd(clean_repo: Path) -> None:
    """The same bug from the other side: a relative `--changed` path must name a module
    in the repo being CHECKED, whatever directory the process happens to start in."""
    result = subprocess.run(
        [sys.executable, str(clean_repo / "scripts" / "check_standalone_imports.py"),
         "--repo-root", str(clean_repo), "--changed", MERGE_REL],
        cwd=ROOT, capture_output=True, text=True,
    )

    assert result.returncode == 0, result.stdout
    assert _report(result)["checked"] == 1, result.stdout


def _mini_repo(root: Path, files: dict[str, str]) -> Path:
    """A throwaway package, for cycle shapes that do not exist in this repo."""
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "__init__.py").write_text("", encoding="utf-8")
    for name, body in files.items():
        (root / "scripts" / name).write_text(body, encoding="utf-8")
    return root


def test_a_cycle_a_module_turns_into_a_missing_sibling_is_still_caught(tmp_path: Path) -> None:
    """The shape fallback must not become a mask, and this is the input that made it one.

    This repo's dominant preamble is `try: from scripts import x / except ImportError:
    import x`. Under a real cycle the first arm raises `partially initialized`, the
    `except` swallows it, and the second arm fails with a plain missing-sibling
    `ModuleNotFoundError` — which is ALSO the legitimate wrong-shape signal the fallback
    exists for. Testing wrong-shape alone therefore let the `direct` shape clear it, and
    `direct` loads the file as a top-level module under a different name, through which
    the cycle does not run. CPython's exception chaining keeps the original text in the
    same stderr, so a cycle marker anywhere vetoes the fallback.
    """
    repo = _mini_repo(tmp_path, {
        "lib_x.py": "from scripts.entry_y import NAME\nVALUE = 'lib'\n",
        "entry_y.py": "try:\n    from scripts import lib_x as lib\nexcept ImportError:\n"
                      "    import lib_x as lib\nNAME = 'entry'\n",
    })

    result = _run_check_at(repo)

    assert result.returncode == 1, result.stdout
    assert [item["path"] for item in _report(result)["cycles"]], result.stdout


def test_a_module_that_imports_in_no_shape_blocks(tmp_path: Path) -> None:
    """Splitting cycle from import-error is worth doing in the OUTPUT — a missing
    dependency has a different fix — but making only one half blocking left the other as
    a hole: the gate held the evidence that a changed module could not be imported at
    all, printed it as a note, and exited 0."""
    repo = _mini_repo(tmp_path, {"broken.py": "import a_dependency_that_is_not_installed\n"})

    result = _run_check_at(repo)

    assert result.returncode == 1, result.stdout
    payload = _report(result)
    assert payload["verdict"] == "BLOCKED"
    assert [item["path"] for item in payload["other_failures"]] == ["scripts/broken.py"]
    # The two classes must stay split in the OUTPUT: this is not a cycle, and nothing in
    # the payload may call it one (a missing dependency has a different fix).
    assert payload["cycles"] == [], "a missing dependency is not a cycle"
    assert "cycle_meaning" not in payload, "a missing dependency is not a cycle"
    assert "not a cycle" in payload["other_failure_meaning"]


def test_a_wrong_shape_sibling_error_still_falls_through(tmp_path: Path) -> None:
    """The false-positive control for the two tests above. Narrowing the fallback must
    not break the case it exists for: 35 healthy modules in this repo use the
    sibling-import preamble and fail the package shape by design."""
    repo = _mini_repo(tmp_path, {
        "helper.py": "VALUE = 'helper'\n",
        "entry.py": "import helper\nNAME = helper.VALUE\n",
    })

    result = _run_check_at(repo)

    assert result.returncode == 0, result.stdout


def test_every_tracked_module_is_either_discovered_or_deliberately_excluded() -> None:
    """The inversion. A test naming the families the pattern already matches is a pin
    against removal, not a completeness check — it cannot fail for a family nobody thought
    of, which is exactly how `skills/shared/scripts/` (10 modules, including the
    extraction PAIRS this gate exists for) went unenumerated in the first cut.

    This fails when a new Python family appears anywhere the gate does not reach, and the
    exclusions are listed here so each is a decision on the record rather than an
    accident.
    """
    module = _load_check_module()
    root = ROOT
    tracked = {
        path.relative_to(root).as_posix()
        # TRACKED only. With the default `include_untracked=True` an untracked scratch
        # file turns this red, and — worse — an untracked `scripts/scratch.py` gets swept
        # and can BLOCK an unrelated commit.
        for path in module.iter_matching_repo_files(root, ("**/*.py",), include_untracked=False)
        if path.name != "__init__.py"
    }
    discovered = {path.relative_to(root).as_posix() for path in module.discover_modules(root)}

    excluded_prefixes = (
        "tests/",          # the suite imports its own helpers every run; a cycle there fails loudly
        # The mirror has its OWN inversion test below. Excluding it here without that
        # would re-hide the exact tree whose enumeration was found broken: the export
        # flattens paths, so a pattern that covers the source can match nothing in the
        # mirror while still printing `checked all N`.
        "plugins/",
        "docs/",           # illustrative snippets, not importable repo modules
        # Rust-crate fixture/parity corpus; not standalone-importable repo modules; owned by the repograph test suite.
        "native/",
        # Evaluator OUTPUT fixtures: files a delegated run produced as its artifact, not
        # repo modules anything imports. They are checked-in evidence, not code.
        "charness-artifacts/",
    )
    unreachable = sorted(
        name for name in tracked - discovered
        if not name.startswith(excluded_prefixes)
    )

    assert not unreachable, (
        "these Python modules are reached by no SCAN_PATTERN and by no recorded exclusion; "
        f"extend one or the other: {unreachable}"
    )


def test_the_exported_mirror_enumerates_its_own_modules() -> None:
    """The mirror is what a CONSUMING repo runs, and its layout is not the source layout.

    The export flattens `skills/public/<skill>/` to `skills/<skill>/` AND hoists support
    out of `skills/` entirely to `support/<skill>/scripts/`. A pattern set written for the
    authoring tree matched ZERO skill modules in the mirror while printing
    `checked all N` — a full-scope verdict over a silently collapsed denominator, which is
    the one thing this gate's own docstring forbids. The first repair covered one
    flattening and left 27 modules, including the `acquire_public_url` and
    `route_public_fetch` extraction PAIRS this gate exists for.

    This inverts against the mirror so the `plugins/` exclusion above is a delegation
    rather than a hole. It checks ENUMERATION only: the mirror currently carries a real
    import failure (tracked separately) that is a defect of the exported package, not of
    this gate's coverage.
    """
    module = _load_check_module()
    mirror = ROOT / "plugins" / "charness"
    tracked = {
        path.relative_to(mirror).as_posix()
        for path in module.iter_matching_repo_files(mirror, ("**/*.py",), include_untracked=False)
        if path.name != "__init__.py"
    }
    discovered = {path.relative_to(mirror).as_posix() for path in module.discover_modules(mirror)}

    assert not sorted(tracked - discovered), (
        "these modules ship in the plugin and are reached by no SCAN_PATTERN; the mirrored "
        f"gate would report `checked all N` over them: {sorted(tracked - discovered)}"
    )


def test_a_partial_run_names_unmatched_paths_even_when_something_matched() -> None:
    """The case B5 actually repaired, and the one its first test could not reach.

    Both existing scope tests have zero unmatched or zero matched, so reverting the fix to
    "name unmatched only when NOTHING matched" left them green. The pre-push lane produces
    this shape routinely: a rename stages one path that resolves and one that does not, and
    the silent-about-the-other behaviour is exactly what B5 removed.
    """
    result = _run_check(ROOT, "--changed", MERGE_REL, "docs/index.md")

    payload = _report(result)
    assert "PARTIAL: checked 1 of" in payload["scope_note"]
    assert "unmatched: docs/index.md" in payload["scope_note"]
