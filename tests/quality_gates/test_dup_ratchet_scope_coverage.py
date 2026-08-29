"""Slice 4 ("gate by property, not by enumeration"): dup_ratchet names its own
uncovered set (tracked files outside `scope_paths`) as a computed number, in its
own output, alongside the pre-existing `degraded_reasons` axis becoming legible
as a plain boolean (`degraded`).

Covers:
- `dup_ratchet_scope.scope_coverage` (pure, path-segment-aware diff of tracked
  files against scope_paths).
- `dup_ratchet_git.tracked_files` (the git seam: `git ls-files`, or `None` when
  git cannot answer).
- `dup_ratchet_lib.evaluate`'s new `degraded` boolean.
- `check_dup_ratchet`'s CLI-layer wiring: `scope_paths`, `scope_coverage`, and
  `did_not_judge` on the real verdict payload, additive only.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from .seeding_support import load_module
from .support import ROOT, run_script

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
CHECK_SCRIPT = SCRIPTS / "check_dup_ratchet.py"


def _load(name: str):
    return load_module(f"{name}_scope_coverage_inproc", SCRIPTS / f"{name}.py")


lib = _load("dup_ratchet_lib")
baseline_lib = _load("dup_ratchet_baseline_lib")
gitmod = _load("dup_ratchet_git")
# `scope_coverage` and the scope half of `did_not_judge` moved together into
# `dup_ratchet_scope` when both host files crossed the length cap.
scope = _load("dup_ratchet_scope")


def _evaluate(**over):
    base = dict(
        code_family_ids=set(), gate_baseline_ids=set(), doc_drift_signatures=set(),
        intentional_code_ids=set(), intentional_doc_signatures=set(),
        fixable_ceiling=0, floor_F=0, escalation_K=3,
        stagnation=0, anchor="anchorsha", anchor_is_ancestor=True, degraded_reasons=None,
    )
    base.update(over)
    return lib.evaluate(**base)


# Imported from the sibling module, NOT copied. The first cut of this file carried
# byte-identical copies of all four helpers, and a fresh-eye round pointed out the
# irony precisely: this is the slice that makes the ratchet report `tests/` as scope it
# never judges, and it shipped fresh copy-paste INTO that blind spot in the same
# change. The ratchet cannot see it, so the discipline has to.
from tests.quality_gates.test_dup_ratchet import (  # noqa: E402
    _code_inventory,
    _doc_inventory,
    _git,
    _write_json,
)


def _consumer_repo(tmp_path: Path, *, scope_paths: tuple[str, ...] = ("src",)) -> Path:
    """A minimal consumer-style fixture repo: adapter + review + baseline, no
    charness internals -- matching the shape `_consumer_repo` in test_dup_ratchet.py
    builds, scoped down to what this file's tests need."""
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    _write_json(repo / "q" / "dup-review.json", {
        "schemaVersion": "charness.quality.dup_review.v1",
        "fixable_ceiling": 0, "entries": [],
    })
    _write_json(
        repo / "q" / "dup-ratchet-baseline.json",
        baseline_lib.build_gate_baseline({"known1": ["known1"]}),
    )
    lines = [
        "version: 1", "repo: consumer", "dup_ratchet:", "  enabled: true",
        "  floor_F: 0", "  escalation_K: 10", "  scope_paths:",
    ]
    lines.extend(f"    - {path}" for path in scope_paths)
    lines.extend([
        "  review_artifact_path: q/dup-review.json",
        "  gate_baseline_path: q/dup-ratchet-baseline.json", "",
    ])
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(lines), encoding="utf-8")
    return repo


def _run_gate(repo: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    code_json = _code_inventory(tmp_path / "code.json", ["known1"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    return run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--detail", cwd=ROOT,
    )


# --------------------------------------------------------------------------- #
# dup_ratchet_scope.scope_coverage — pure
# --------------------------------------------------------------------------- #
def test_scope_coverage_counts_uncovered_files_and_respects_path_segments() -> None:
    tracked = {
        "scripts/a.py", "skills/public/x.py", "skills/public-2/y.py",
        "tests/test_a.py", "skills/shared/z.py",
    }
    coverage = scope.scope_coverage(tracked, ["scripts", "skills/public"])
    assert coverage == {
        "tracked_file_count": 5,
        "uncovered_file_count": 3,
        "uncovered_top_level": ["skills", "tests"],
    }


def test_scope_coverage_returns_none_when_tracked_files_unknown() -> None:
    assert scope.scope_coverage(None, ["scripts"]) is None


# --------------------------------------------------------------------------- #
# dup_ratchet_git.tracked_files — git seam
# --------------------------------------------------------------------------- #
def test_git_tracked_files_reads_committed_paths(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init")
    (repo / "a.py").write_text("a = 1\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "seed")
    assert gitmod.tracked_files(repo) == {"a.py"}


def test_git_tracked_files_none_outside_a_repo(tmp_path: Path) -> None:
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    assert gitmod.tracked_files(not_a_repo) is None


# --------------------------------------------------------------------------- #
# dup_ratchet_lib.evaluate — the fail-open branch's own state, legible
# --------------------------------------------------------------------------- #
def test_evaluate_verdict_carries_degraded_boolean() -> None:
    clean = _evaluate()
    assert clean["degraded"] is False

    degraded = _evaluate(degraded_reasons=["overlay missing"])
    assert degraded["degraded"] is True
    assert degraded["status"] == "degraded"
    assert degraded["ok"] is True and degraded["block"] is False


# --------------------------------------------------------------------------- #
# check_dup_ratchet CLI — additive-only wiring on a real verdict
# --------------------------------------------------------------------------- #
def test_cli_echoes_scope_paths_and_computes_uncovered_count(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "a.py").write_text("a = 1\n", encoding="utf-8")
    (repo / "tests").mkdir(parents=True, exist_ok=True)
    (repo / "tests" / "b.py").write_text("b = 1\n", encoding="utf-8")
    (repo / "docs").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "c.md").write_text("# c\n", encoding="utf-8")
    _git(repo, "init")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "seed")

    result = _run_gate(repo, tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = yaml.safe_load(result.stdout)

    assert verdict["scope_paths"] == ["src"]
    coverage = verdict["scope_coverage"]
    assert coverage["tracked_file_count"] == 6
    assert coverage["uncovered_file_count"] == 5
    assert coverage["uncovered_top_level"] == [".agents", "docs", "q", "tests"]
    assert any("5 tracked file" in entry for entry in verdict["did_not_judge"])
    # Additive only: the real verdict is untouched by sizing the gap.
    assert result.returncode == 0


def test_cli_scope_coverage_unknown_without_git_stays_honest(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    result = _run_gate(repo, tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = yaml.safe_load(result.stdout)

    assert verdict["scope_paths"] == ["src"]
    assert verdict["scope_coverage"] is None
    assert any("git could not be asked" in entry for entry in verdict["did_not_judge"])


def test_empty_scope_paths_does_not_claim_the_whole_tree_was_never_judged() -> None:
    """The branch that repaired a FALSE claim, and had no test until the gate said so.

    With `scope_paths` empty, `scope_coverage` marks every tracked file uncovered.
    Rendering that as "N files this scan never formed a family from" is a gate added to
    report its gap honestly overstating it.

    The changed-line coverage gate named these exact lines as unproven, which is how
    the omission surfaced rather than by anyone noticing.

    This test used to also assert `"scanner defaults" in joined` -- it PINNED the
    provenance claim a later round proved false, so the falsehood had a passing test
    guarding it. The sibling above now covers what this function must not claim; this
    one keeps its own subject, which is the overstatement.
    """
    module = _load("check_dup_ratchet")
    coverage = {
        "tracked_file_count": 7785,
        "uncovered_file_count": 7785,
        "uncovered_top_level": ["scripts", "docs"],
    }

    entries, messages = module._scope_did_not_judge([], coverage, tracked_known=True)

    joined = " ".join(entries) + " " + " ".join(messages)
    # It must NOT report the whole tree as never-judged, which is the false claim.
    assert "7785 tracked file(s)" not in joined
    assert "never forms a CODE family" not in joined

    # Control: with a real scope, the count IS reported and is scoped to CODE families.
    entries, messages = module._scope_did_not_judge(["scripts"], coverage, tracked_known=True)
    joined = " ".join(entries) + " " + " ".join(messages)
    assert "7785 tracked file(s)" in joined
    assert "never forms a CODE family" in joined
    assert "the doc arm scans the repo root" in joined


def test_a_degrade_that_did_not_stop_the_code_scan_still_reports_its_true_scope(
    tmp_path: Path,
) -> None:
    """The SCOPE line is keyed on the CODE SCAN, never on the whole-gate `degraded`.

    This branch shipped saying "this run degraded before any family was formed" for
    EVERY degrade cause. `code_family_members` runs unconditionally, before any cause
    can short-circuit, so on a missing overlay -- the state of a consumer repo
    mid-adoption -- families are formed and that sentence is false. `evaluate`'s early
    return skips the HARD ARM, not family formation: it computes `new_code_families`
    first, so the false line sat beside a populated list denying those families existed.

    A gate added to stop greens over-claiming coverage was UNDER-claiming it, and
    contradicting its own `did_not_judge` (scoped to files OUTSIDE scope_paths, which
    reads as "everything inside was judged") in the same payload.
    """
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    (repo / "q" / "dup-review.json").unlink()
    _git(repo, "init")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "seed")

    verdict = yaml.safe_load(_run_gate(repo, tmp_path).stdout)
    joined = " ".join(verdict["messages"])

    assert verdict["degraded"] is True
    assert any("overlay missing" in reason for reason in verdict["degraded_reasons"])
    # The scan ran despite the degrade, so the scope statement is true and must print.
    assert "SCOPE: scope_paths=['src'] admits" in joined
    assert "degraded before any family was formed" not in joined
    assert "SCOPE: not reported" not in joined


def test_a_failed_code_scan_suppresses_the_scope_line_and_names_the_in_scope_gap(
    tmp_path: Path,
) -> None:
    """The other side: when the CODE SCAN itself produced nothing, suppression is right.

    This is the one degrade cause that empties the in-scope judgment, so the human line
    must not read as a coverage statement -- and `did_not_judge` must say the in-scope
    files went unjudged too. Without that entry the payload publishes a gap scoped
    entirely to files OUTSIDE scope_paths, which is the "I judged everything inside"
    reassurance on precisely the run where nothing was judged.
    """
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    _git(repo, "init")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "seed")
    broken = tmp_path / "broken-code.json"
    broken.write_text("", encoding="utf-8")
    doc_json = _doc_inventory(tmp_path / "doc.json", [])

    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(broken), "--doc-inventory", str(doc_json),
        "--detail", cwd=ROOT,
    )
    verdict = yaml.safe_load(result.stdout)
    joined = " ".join(verdict["messages"])

    assert any("unreadable" in reason for reason in verdict["degraded_reasons"])
    assert "SCOPE: not reported -- the code scan produced no result" in joined
    assert "SCOPE: scope_paths=['src'] admits" not in joined
    assert any(
        "whether any in-scope file carries a code clone family" in entry
        for entry in verdict["did_not_judge"]
    ), "a run whose code scan produced nothing must say the in-scope files went unjudged"


def test_scope_coverage_normalizes_before_comparing_and_refuses_shapes_it_cannot_resolve() -> None:
    """A whole-tree scope reported the whole tree as UNJUDGED, having scanned it.

    `_covered` is a literal path-segment test and `rstrip("/")` was its only
    normalization, so `scope_paths: ["."]` matched nothing: `uncovered_file_count`
    equalled `tracked_file_count` and `did_not_judge` said the scan never formed a
    family from any of them. `dup_ratchet_scan` passes that same `"."` to nose as
    `--root .`, which scans everything. The gate published "I judged none of these"
    about files it had fully scanned — the overstatement the empty-scope arm refuses
    to make, arriving through the arm that looked resolvable.

    `./src` failed identically. A glob cannot be resolved by a prefix test at all, and
    the adapter validator's docstring calls this field a "glob/path list", so that
    shape returns the unknown state rather than a number invented for it.

    The first repair listed the shapes to REJECT (`*?[` and a leading `..`) and missed
    four more that kept producing the same wrong number: an absolute path, `~/...`, a
    backslash separator, and `//` — all of which survived `normpath`, then `lstrip("/")`
    turned into a relative path matching nothing, so `uncovered_file_count` equalled
    `tracked_file_count` again. `_is_literal_relative_prefix` states what the literal
    comparison REQUIRES instead, so an unlisted shape is refused by default rather than
    admitted by default.
    """
    tracked = {"src/a.py", "docs/c.md", "README.md"}

    for whole_tree in (".", "./", "", "/", "src/.."):
        coverage = scope.scope_coverage(tracked, [whole_tree])
        assert coverage is not None, whole_tree
        assert coverage["uncovered_file_count"] == 0, (whole_tree, coverage)
        assert coverage["uncovered_top_level"] == []

    # Normalized, not compared raw.
    assert scope.scope_coverage(tracked, ["./src"]) == scope.scope_coverage(tracked, ["src"])
    assert scope.scope_coverage(tracked, ["src/"]) == scope.scope_coverage(tracked, ["src"])
    assert scope.scope_coverage(tracked, ["  src  "]) == scope.scope_coverage(tracked, ["src"])

    # Unresolvable by a literal prefix test -> the unknown state, never a fabricated
    # count. Asserted by VALUE against the number the old shapes produced: `is None`
    # alone would also hold for a function that returned None for everything.
    wrong_number = {
        "tracked_file_count": 3,
        "uncovered_file_count": 3,
        "uncovered_top_level": ["docs", "src"],
    }
    for unresolvable in (
        "src/**/*.py",
        "src/*",
        "src/[ab]",
        "/abs/repo/src",
        "~/repo/src",
        "src\\lib",
        "//",
        "../sibling",
    ):
        result = scope.scope_coverage(tracked, [unresolvable])
        assert result is None, (unresolvable, result)
        assert result != wrong_number, unresolvable

    # A whole-tree entry settles the count regardless of an unresolvable sibling:
    # nothing sits outside "everything", whatever the other entry turns out to mean.
    assert scope.scope_coverage(tracked, [".", "src/*"])["uncovered_file_count"] == 0

    # Controls: ordinary prefix scopes still measure, including a non-ASCII segment
    # and an interior `.` the normalizer collapses.
    assert scope.scope_coverage(tracked, ["src"])["uncovered_file_count"] == 2
    assert scope.scope_coverage(tracked, ["src/./x"]) == scope.scope_coverage(tracked, ["src/x"])
    assert scope.scope_coverage({"문서/a.py"}, ["문서"])["uncovered_file_count"] == 0


def test_unknown_coverage_names_the_cause_that_actually_applied() -> None:
    """`scope_coverage` returning None has two causes, and they are not the same claim.

    The arm was added for unresolvable scope shapes and reused the existing unknown
    state, whose only renderer said "git could not be asked this run". A consumer
    scoped with a glob — legal per the adapter validator's own docstring — then got a
    `did_not_judge` entry and a human `SCOPE:` line blaming git, on a run where git had
    answered fine. A gate stating a false cause about its own environment sends an
    operator to debug their checkout instead of their config, in the very field added
    so gates stop over-claiming.

    Each cause is asked for independently and every true one is named, so a third cause
    added to `scope_coverage` later cannot inherit a sentence written for the first.
    """
    check = _load("check_dup_ratchet")

    glob_only = check._scope_did_not_judge(["src/**/*.py"], None, tracked_known=True)[0][0]
    assert "git could not be asked" not in glob_only, glob_only
    assert "'src/**/*.py'" in glob_only, glob_only

    git_only = check._scope_did_not_judge(["src"], None, tracked_known=False)[0][0]
    assert "git could not be asked" in git_only, git_only
    assert "scope_paths carries" not in git_only, git_only

    both = check._scope_did_not_judge(["src/*"], None, tracked_known=False)[0][0]
    assert "git could not be asked" in both, both
    assert "'src/*'" in both, both

    # The human line carries the same cause, not a second story.
    _, messages = check._scope_did_not_judge(["src/**/*.py"], None, tracked_known=True)
    assert "git could not be asked" not in messages[0], messages


def test_an_unknown_with_no_recognized_cause_still_names_one() -> None:
    """The guard for a cause this function does not yet know about.

    `coverage is None` with git answered AND every scope entry resolvable is
    unreachable against today's `scope_coverage`, which returns None only for those
    two causes. It is reachable the moment a third cause is added, and the failure
    mode then is an EMPTY `" and ".join(causes)` -- a sentence that names no cause at
    all, which reads as a formatting bug rather than as the unknown it is. Asserted by
    calling the state directly, because a branch nothing exercises is a rule written
    in prose, not a guard.
    """
    check = _load("check_dup_ratchet")

    entry = check._scope_did_not_judge(["src"], None, tracked_known=True)[0][0]
    assert "could not resolve the question this run" in entry, entry
    # The specific failure this guards: a dangling "--  , so even that count".
    assert "--  ," not in entry, entry
    assert "outside scope_paths --  " not in entry, entry


def test_empty_scope_claims_nothing_about_whether_the_scanner_fell_back() -> None:
    """This function must not claim scan PROVENANCE, in either direction.

    Two drafts did. The first asserted the scanner fell back to its DEFAULT_PATHS
    whenever `scope_paths` was empty. The second flipped that on `code_reason` being
    set. Both were false, because `code_reason` is a FAILURE STRING and its four
    producers sit on both sides of the fallback line in `dup_ratchet_scan`:

      - `nose binary not found`      -> returns BEFORE `scope_paths or DEFAULT_PATHS`
      - `nose code scan error`       -> returns AFTER it, having resolved and scanned
      - `unreadable member span`     -> after a scan that FORMED families
      - `injected code inventory ...`-> never reaches that line at all

    and a READABLE injected inventory produces no `code_reason` while running no scan,
    so the "it fell back" arm was false there too.

    There is no per-reason loop here and there cannot be: the parameter is gone, which
    is what the signature assertion at the end pins. An earlier version of this
    docstring claimed the test asserted "over all four reasons", which the body never
    did -- the sentence described the round-3 draft and survived its rewrite. That is
    the same test-prose-over-assertions defect this file already carries a note about.
    """
    module = _load("check_dup_ratchet")
    coverage = {
        "tracked_file_count": 100,
        "uncovered_file_count": 100,
        "uncovered_top_level": ["scripts"],
    }

    entries, messages = module._scope_did_not_judge([], coverage, tracked_known=True)
    joined = " ".join(entries) + " " + " ".join(messages)

    assert "cannot name the set" in joined
    # Neither provenance claim, and not in the message prefix either -- the prefix
    # said "(scanner defaults used)" unconditionally while the body denied it.
    assert "fell back" not in joined
    assert "scanner defaults used" not in joined
    assert "never resolved a path set" not in joined
    # It must still refuse to call the whole tree unjudged, which is the original job.
    assert "100 tracked file(s)" not in joined

    # The signature carries no scan-outcome parameter at all: a third draft cannot
    # reintroduce the inference without changing this call.
    #
    # `tracked_known` is admitted here and is not that parameter. Scan outcome is a
    # thing this function would have to INFER from a failure string whose producers sit
    # on both sides of the line it was inferring about; `tracked_known` is a fact the
    # caller holds directly (`tracked is not None`) and passes down, so it cannot be
    # wrong the way the two withdrawn drafts were. What the pin forbids is a parameter
    # this function reasons FROM, not one it is told.
    import inspect

    params = list(inspect.signature(module._scope_did_not_judge).parameters)
    assert params == ["scope_paths", "coverage", "tracked_known"], params
    assert not any(
        "reason" in name or "scan" in name or "degraded" in name for name in params
    ), params


def test_empty_scope_without_git_does_not_frame_the_whole_tree_as_unjudged() -> None:
    """Guard ORDER decided which claim got made, and the unreachable order was wrong.

    `coverage is None` is checked before `not scope_paths`, so an empty scope with no
    readable git fell into the git-unavailable arm, whose text names "files outside
    scope_paths" -- which, with an empty scope, is the entire repo. That is the
    overstatement the empty-scope arm's own comment says this field must never make.
    """
    module = _load("check_dup_ratchet")

    entries, _ = module._scope_did_not_judge([], None, tracked_known=False)
    joined = " ".join(entries)
    assert "neither the scanned set nor the tracked set is known" in joined
    assert "outside scope_paths" not in joined

    # Control: with a real scope, the git-unavailable text is correct and must stay.
    entries, _ = module._scope_did_not_judge(["src"], None, tracked_known=False)
    assert "outside scope_paths" in " ".join(entries)


@pytest.mark.skipif(
    shutil.which("nose") is None and not os.environ.get("NOSE_BIN"),
    reason="nose binary required for the real-scan zero-families backstop",
)
def test_a_zero_family_scan_against_a_live_baseline_says_it_did_not_judge_in_scope(
    tmp_path: Path,
) -> None:
    """`degraded_reasons` calls this scan probably broken; `did_not_judge` must agree.

    The scan RAN and returned zero, so there is no `code_reason` and the true SCOPE
    line prints. Read as a payload that said: the gap is entirely outside scope_paths,
    the in-scope files were judged and found clean -- an in-scope all-clear on a run
    the gate itself does not believe. Two fields of one payload disagreeing again.
    """
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    # `src/` must EXIST and hold something clone-free. A missing scope root makes the
    # scanner error out into `code_reason`, which is the OTHER branch -- the first cut
    # of this test skipped for exactly that reason, and a test that always skips is not
    # proof of anything.
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    _git(repo, "init")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "seed")
    # No --code-inventory: the zero-families backstop is keyed on a REAL scan.
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--doc-inventory", str(doc_json), "--detail", cwd=ROOT,
    )
    verdict = yaml.safe_load(result.stdout)
    assert any(
        "returned 0 families" in reason for reason in verdict["degraded_reasons"]
    ), f"fixture did not reach the backstop: {verdict['degraded_reasons']}"

    assert any(
        "more likely a broken scan than a cleared repo" in entry
        for entry in verdict["did_not_judge"]
    ), "a run the gate calls probably-broken must not imply an in-scope all-clear"


def test_summary_reports_the_new_family_count_by_value_on_a_blocking_run(tmp_path: Path) -> None:
    """`--summary` had NO test on a hard-blocking run, so its counts were unpinned.

    Grepping the suite for `new_code_family_count` returned nothing. The only two tests
    touching `summarize()` drove an inert run and a CLEAN armed run — neither of which
    can distinguish a correct count from a constant zero. Mistype the key in that
    projection and every consumer's summary reports zero new families on a real block,
    with the suite green.

    This is the shape that let a sibling gate publish a NEGATIVE count for a release:
    the assertion checked that the key was present, not what it said.
    """
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    _git(repo, "init")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "seed")
    # Two families the baseline does not carry: a real hard block.
    code_json = _code_inventory(tmp_path / "code.json", ["known1", "newfam1", "newfam2"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--summary", cwd=ROOT,
    )
    payload = yaml.safe_load(result.stdout)

    assert payload["hard_block"] is True, payload
    assert payload["new_code_family_count"] == 2, payload
    assert len(payload["new_code_families_sample"]) == 2
    assert payload["new_doc_family_count"] == 0


def test_summary_publishes_a_nonzero_doc_family_count(tmp_path: Path) -> None:
    """#709: the doc projection was pinned ONLY on the arm that returns zero.

    `summarize()` is the only place the doc family list becomes a count for
    `--summary` consumers, and the sibling above is the repo's only assertion on
    it -- at the value 0. A projection that returned zero for every input, or read
    a mistyped key, published "no new doc families" on a run that hard-blocks on
    doc drift, with the suite green. The summary is what an operator reads first,
    so it would disagree with the exit code and win.

    The code arm is already pinned nonzero above; this is the doc arm, which the
    shared projection loop does NOT get for free -- a wrong key in its `new_doc`
    tuple entry drops these fields entirely while every code assertion still passes.
    """

    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    _git(repo, "init")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "seed")
    code_json = _code_inventory(tmp_path / "code.json", ["known1"])
    doc_json = _doc_inventory(tmp_path / "doc.json", ["docs/a.md#one", "docs/b.md#two"])
    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--summary", cwd=ROOT,
    )
    payload = yaml.safe_load(result.stdout)

    assert payload["new_doc_family_count"] == 2, payload
    assert sorted(payload["new_doc_families_sample"]) == ["docs/a.md#one", "docs/b.md#two"], payload
    # The count is a projection OF the sample's source list, so a count that
    # ignored its input would still have to disagree with the names here.
    assert payload["new_doc_family_count"] == len(payload["new_doc_families_sample"])


def test_summary_withholds_unobserved_verdict_fields_on_non_scan_paths() -> None:
    """Inert, invalid, and maintenance responses must not manufacture clean zeros."""
    check = _load("check_dup_ratchet")
    absent = {
        "ok": True,
        "status": "inert",
        "inert": True,
        "messages": ["gate inert"],
    }
    invalid = {
        "ok": False,
        "status": "adapter-invalid",
        "adapter_errors": ["bad enabled"],
        "messages": ["adapter invalid"],
    }
    maintenance = {
        "ok": True,
        "status": "baseline-written",
        "code_family_count": 4,
        "messages": ["baseline written"],
    }

    for report in (absent, invalid, maintenance):
        summary = check.summarize(report)
        assert summary["message_count"] == 1
        for key in (
            "hard_block",
            "boy_scout_block",
            "new_code_family_count",
            "new_code_families_sample",
            "new_doc_family_count",
            "new_doc_families_sample",
            "degraded_reasons",
        ):
            assert key not in summary, (report, key, summary)


def test_an_armed_run_still_publishes_the_scope_fields_in_summary(tmp_path: Path) -> None:
    """The other half of the withhold guard: it must not OVER-fire.

    The inert case is pinned in test_dup_ratchet.py. This pins the publishing branch,
    which was equally untested: mistype the projection's key tuple and every armed
    consumer silently loses `did_not_judge` from its summary with the suite green.
    The changed-line gate cannot catch that, because the line executes on the inert
    path and so reads as covered while nothing asserts the behaviour.

    `--summary`, not `--detail`: `emit_selected` returns the raw report for `--detail`
    and bypasses `summarize()` entirely, which is why the existing CLI tests here
    could not have caught it.
    """
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    code_json = _code_inventory(tmp_path / "code.json", ["known1"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--summary", cwd=ROOT,
    )

    payload = yaml.safe_load(result.stdout)
    assert payload["scope_paths"] == ["src"]
    assert "scope_coverage" in payload
    assert payload["did_not_judge"], "an armed run must say what it did not judge"
