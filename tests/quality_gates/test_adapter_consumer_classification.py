"""The adapter-consumer census must fail on an UNCLASSIFIED consumer, not merely count.

The gate's claim is a completeness property: every file that reads a resolved adapter
payload carries a written verdict about what it does when the version was refused. A
census that only reports counts would render green forever while new consumers accrete,
which is the shape it exists to replace.

Each test below builds the failure it names in a temp tree and asserts the gate refuses.
The polarity control at the end runs it against the real repo, because a gate that refuses
everything satisfies every refusal test here.

Blind class, inherited from the gate and not fixed by these tests: a `safe-checks-errors`
row is verified by the file MENTIONING `errors`/`valid`, never by that mention being
load-bearing. Nothing here can tell a real refusal from an echoed field.
"""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

GATE = load_script_module(
    "check_adapter_consumer_classification", ROOT / "scripts/check_adapter_consumer_classification.py"
)


def _tree(tmp_path: Path, sources: dict[str, str], consumers: dict[str, dict]) -> Path:
    repo = tmp_path / "repo"
    for rel, text in sources.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    manifest = repo / GATE.MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps({"schemaVersion": 1, "consumers": consumers}, indent=2) + "\n", encoding="utf-8"
    )
    return repo


CALLS_LOADER = "def go(root):\n    return load_adapter(root)\n"


def test_an_unclassified_consumer_fails(tmp_path: Path) -> None:
    repo = _tree(tmp_path, {"scripts/new_consumer.py": CALLS_LOADER}, {})

    problems, counts = GATE.check(repo)

    assert any("not classified" in problem for problem in problems), problems
    assert counts.get("UNCLASSIFIED") == 1


def test_a_stale_row_fails(tmp_path: Path) -> None:
    """A row naming a file that no longer reads an adapter is the other half of the
    property. Without it the manifest reports coverage of consumers that stopped existing,
    which reads as a larger denominator than the repo actually has."""
    repo = _tree(
        tmp_path,
        {"scripts/plain.py": "def go():\n    return 1\n"},
        {"scripts/gone.py": {"verdict": "safe-checks-errors", "reason": "was one once"}},
    )

    problems, _counts = GATE.check(repo)

    assert any("has no adapter call site" in problem for problem in problems), problems


def test_a_guarded_row_must_carry_its_structural_witness(tmp_path: Path) -> None:
    """`guarded` is the one verdict with a checkable witness, so it is checked. The other
    verdicts are prose and say so; claiming the strongest one without referencing the
    guard helper is the cheapest way to launder an unguarded consumer."""
    repo = _tree(
        tmp_path,
        {"scripts/liar.py": CALLS_LOADER},
        {"scripts/liar.py": {"verdict": "guarded-all-doors", "reason": "trust me"}},
    )

    problems, _counts = GATE.check(repo)

    assert any("references none of" in problem for problem in problems), problems


def test_a_reasonless_row_fails(tmp_path: Path) -> None:
    repo = _tree(
        tmp_path,
        {"scripts/bare.py": CALLS_LOADER},
        {"scripts/bare.py": {"verdict": "accepted-risk-unguarded", "reason": "  "}},
    )

    problems, _counts = GATE.check(repo)

    assert any("carries no reason" in problem for problem in problems), problems


def test_an_unknown_verdict_fails(tmp_path: Path) -> None:
    repo = _tree(
        tmp_path,
        {"scripts/odd.py": CALLS_LOADER},
        {"scripts/odd.py": {"verdict": "probably-fine", "reason": "a word not in the vocabulary"}},
    )

    problems, _counts = GATE.check(repo)

    assert any("is not one of" in problem for problem in problems), problems


def test_a_loader_passed_as_a_value_is_still_enumerated(tmp_path: Path) -> None:
    """The regression that widened the rule from calls to references.

    `validate_retro_artifact.py` never CALLS its loader — it hands
    `_output_dir.load_retro_adapter` to the verdict helper — so a call-only rule left the
    repo's own guarded consumer out of its own census. A census blind to the example it
    was built from is not a census.
    """
    repo = _tree(
        tmp_path,
        {"scripts/passes_it.py": "def go(helper, root):\n    return helper(load_retro_adapter, root)\n"},
        {},
    )

    problems, _counts = GATE.check(repo)

    assert any("passes_it.py" in problem for problem in problems), problems


@pytest.mark.parametrize(
    ("source", "enumerated"),
    [
        ('P = ".agents/x-adapter.yaml"\nimport yaml\nd = yaml.safe_load(open(P).read())\n', True),
        ('MSG = "fix .agents/x-adapter.yaml"\ndef go():\n    print(MSG)\n', False),
    ],
    ids=["raw-read", "message-only"],
)
def test_the_raw_yaml_rule_needs_both_witnesses(tmp_path: Path, source: str, enumerated: bool) -> None:
    """Both halves, because either alone is wrong in a different direction.

    The literal alone matched 48 files that only NAME an adapter in a message — including
    the version guard's own refusal text, which names the file it wants fixed. The YAML
    call alone would match every YAML reader in the repo. Paired, the rule is about
    reading an adapter rather than about a string.
    """
    repo = _tree(tmp_path, {"scripts/probe.py": source}, {})

    problems, counts = GATE.check(repo)

    assert (counts.get("UNCLASSIFIED", 0) == 1) is enumerated, (problems, counts)


def test_an_absent_manifest_is_an_empty_one_not_a_hard_error(tmp_path: Path) -> None:
    """A tree with no consumers and no manifest PASSES, and a tree with consumers and no
    manifest fails once per consumer -- naming them, where a `missing manifest` refusal
    would name only the file. Raising instead broke every fixture repo that runs the
    broad lane without carrying charness's own manifest."""
    empty = tmp_path / "empty"
    (empty / "scripts").mkdir(parents=True)
    (empty / "scripts" / "plain.py").write_text("def go():\n    return 1\n", encoding="utf-8")

    problems, counts = GATE.check(empty)

    assert problems == []
    assert counts == {}

    populated = tmp_path / "populated"
    (populated / "scripts").mkdir(parents=True)
    (populated / "scripts" / "reader.py").write_text(CALLS_LOADER, encoding="utf-8")

    problems, _counts = GATE.check(populated)

    assert any("reader.py" in problem for problem in problems), problems


def test_an_unparseable_file_is_a_hard_error_not_a_skip(tmp_path: Path) -> None:
    """Skipping it would shrink the denominator, which is the one thing a completeness
    census must never do: an unreadable file would render as "no consumers here"."""
    repo = _tree(tmp_path, {"scripts/broken.py": "def (\n"}, {})

    with pytest.raises(SystemExit, match="could not be parsed"):
        GATE.check(repo)


def test_the_module_runs_as_a_script(tmp_path: Path) -> None:
    """Covers the `__main__` block in-process rather than through a subprocess.

    The line is one `sys.exit(main())`, and it is the only thing standing between a
    correct `main()` and a gate that cannot be invoked. `runpy` with `run_name="__main__"`
    executes it without adding a process boundary the bypass ratchet would rightly count.
    """
    repo = _tree(
        tmp_path,
        {"scripts/known.py": CALLS_LOADER},
        {"scripts/known.py": {"verdict": "safe-checks-errors", "reason": "checks errors at L1"}},
    )
    argv = ["check_adapter_consumer_classification.py", "--repo-root", str(repo)]

    with mock.patch.object(sys, "argv", argv), pytest.raises(SystemExit) as excinfo:
        runpy.run_path(
            str(ROOT / "scripts/check_adapter_consumer_classification.py"), run_name="__main__"
        )

    assert excinfo.value.code == 0


def test_a_call_whose_target_is_not_a_name_is_not_a_loader(tmp_path: Path) -> None:
    """A call through a subscript or a call result has no static name to match. It must
    answer False rather than raise -- the enumerator walks every call in the repo, and one
    exotic call shape must not take the census down."""
    repo = _tree(tmp_path, {"scripts/exotic.py": "HANDLERS = {}\n\ndef go(root):\n    return HANDLERS['x'](root)\n"}, {})

    problems, counts = GATE.check(repo)

    assert problems == []
    assert counts == {}


def test_the_cli_reports_counts_and_exits_non_zero_on_an_unclassified_consumer(tmp_path: Path) -> None:
    """Drives `main()`, because the counts print and the exit code ARE the gate's operator
    surface: a check() that returns problems nobody prints is not a gate."""
    repo = _tree(
        tmp_path,
        {"scripts/reader.py": CALLS_LOADER, "scripts/known.py": CALLS_LOADER},
        {"scripts/known.py": {"verdict": "accepted-risk-unguarded", "reason": "declared risk"}},
    )
    module = load_script_module("gate_cli_fail", ROOT / "scripts/check_adapter_consumer_classification.py")

    result = run_loaded_script_main(
        "scripts/check_adapter_consumer_classification.py", module, "--repo-root", str(repo)
    )

    assert result.returncode == 1
    assert "UNCLASSIFIED: 1" in result.stdout
    # The accepted-risk line is printed on every run, passing or failing. An accepted risk
    # that stops being counted is an accepted risk that stops being decided.
    assert "ACCEPTED RISK: 1" in result.stdout
    assert "not classified" in result.stderr


def test_the_cli_exits_zero_and_totals_when_everything_is_classified(tmp_path: Path) -> None:
    repo = _tree(
        tmp_path,
        {"scripts/known.py": CALLS_LOADER},
        {"scripts/known.py": {"verdict": "safe-checks-errors", "reason": "checks errors at L1"}},
    )
    module = load_script_module("gate_cli_pass", ROOT / "scripts/check_adapter_consumer_classification.py")

    result = run_loaded_script_main(
        "scripts/check_adapter_consumer_classification.py", module, "--repo-root", str(repo)
    )

    assert result.returncode == 0
    assert "total classifications: 1 across 1 file(s)" in result.stdout
    # No accepted-risk rows here, so the line must be absent rather than printed as zero:
    # a standing "ACCEPTED RISK: 0" trains the reader to skip the line that matters.
    assert "ACCEPTED RISK" not in result.stdout


def test_the_real_repo_is_fully_classified() -> None:
    """The polarity control. Every test above is satisfied by a gate that refuses
    everything; this is the one that would catch it — and it is also the live assertion
    that this repo has no unclassified consumer right now."""
    problems, counts = GATE.check(ROOT)

    assert problems == [], problems
    assert counts.get("UNCLASSIFIED", 0) == 0
    # The accepted-risk count is REPORTED, never asserted at a number: pinning it here
    # would make paying the debt down fail this test, and pinning it as a ceiling would
    # invite raising the ceiling. The gate prints it on every run instead.
    #
    # The invariant is per-CLASSIFICATION now, not per-file: a row may declare more than
    # one defect class, so the vector sums to the number of declared classifications and
    # sits at or above the file count. Asserting equality with the file count was right
    # under one-verdict-per-file and would now silently forbid the multi-class row.
    rows = json.loads((ROOT / GATE.MANIFEST_REL).read_text(encoding="utf-8"))["consumers"]
    declared_classifications = sum(len(GATE.row_verdicts(entry)) for entry in rows.values())
    assert sum(counts.values()) == declared_classifications
    assert declared_classifications >= len(rows)


# --- `--list-consumers`: the enumeration that PREVENTS (#599) --------------------


def test_list_consumers_answers_the_shape_question_in_one_call() -> None:
    """`#599` asks "who reads this producer" for the adapter-loader SHAPE.

    Two surfaces own two halves of that question and this is the shape half.
    `what_reads_this.py` owns a LITERAL name and cannot express a shape -- measured on
    this tree, `_is_adapter_loader_name` matches ~27 distinct loader names, so asking it
    literally is many calls, one of which (`load_adapter`) alone returns 446 references
    across 157 files, dominated by SOURCE rather than prose (96 source, 38 test, 19 doc).
    This is one call over the classified files, and it is not a new capability:
    `consumer_files()` already did the work and simply had no command surface.
    """
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_adapter_consumer_classification.py"),
         "--repo-root", str(ROOT), "--list-consumers"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    listed = [line.strip() for line in result.stdout.splitlines() if line.startswith("  scripts/")]
    assert listed, result.stdout
    assert set(listed) <= set(GATE.consumer_files(ROOT))


def test_list_consumers_carries_its_blind_class_in_its_own_output() -> None:
    """An enumeration that LOOKS complete is worse than none, because the reader stops
    looking. The limits travel with the answer, not only in the module docstring."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_adapter_consumer_classification.py"),
         "--repo-root", str(ROOT), "--list-consumers"],
        capture_output=True, text=True,
    )
    assert "BLIND CLASS" in result.stdout
    for line in GATE.LIST_CONSUMERS_BLIND_CLASS:
        assert line in result.stdout
    # The two the goal's acceptance names explicitly.
    assert "HELPER in another module" in result.stdout
    assert "FILES, not call sites" in result.stdout


def test_list_consumers_is_read_only_and_does_not_run_the_gate() -> None:
    # The query must be safe to run BEFORE a change, including on a tree the gate would
    # currently refuse; a preventing query that first fails the thing it precedes is one
    # nobody runs.
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_adapter_consumer_classification.py"),
         "--repo-root", str(ROOT), "--list-consumers"],
        capture_output=True, text=True,
    )
    assert "adapter consumer classification:" not in result.stdout
    assert "ACCEPTED RISK" not in result.stdout


# --- multi-class rows: a file may carry more than one defect class ---------------


def test_a_file_may_carry_two_defect_classes(tmp_path: Path) -> None:
    """The measured instance this schema exists for.

    `build_retro_lesson_selection_index.py` calls the loader unguarded AND separately
    reads an adapter yaml raw with no version reconciliation. Under one-verdict-per-file
    it was filed as the first only, and paying that down would have left the second half
    live under a row reading `done` -- the two classes need different repairs.
    """
    repo = _tree(
        tmp_path,
        {"scripts/two_classes.py": CALLS_LOADER},
        {"scripts/two_classes.py": {"verdicts": [
            {"verdict": "accepted-risk-unguarded", "reason": "unguarded loader call at line 2"},
            {"verdict": "no-version-validation", "reason": "also reads the yaml raw elsewhere"},
        ]}},
    )
    problems, counts = GATE.check(repo)
    assert problems == [], problems
    assert counts["accepted-risk-unguarded"] == 1
    assert counts["no-version-validation"] == 1
    # Counted PER VERDICT, so the vector sums above the file count rather than hiding one.
    assert sum(counts.values()) == 2


def test_the_single_verdict_shape_still_works_unchanged(tmp_path: Path) -> None:
    # Almost every row uses it and this change deliberately does not churn them.
    repo = _tree(
        tmp_path,
        {"scripts/one_class.py": CALLS_LOADER},
        {"scripts/one_class.py": {"verdict": "accepted-risk-unguarded", "reason": "unguarded"}},
    )
    problems, counts = GATE.check(repo)
    assert problems == []
    assert counts == {"accepted-risk-unguarded": 1}


def test_a_repeated_class_in_one_row_is_refused(tmp_path: Path) -> None:
    # Saying the same thing twice inflates the count vector the gate reports as its
    # running measure, which is the one number slice 5 is judged against.
    repo = _tree(
        tmp_path,
        {"scripts/dup.py": CALLS_LOADER},
        {"scripts/dup.py": {"verdicts": [
            {"verdict": "accepted-risk-unguarded", "reason": "one"},
            {"verdict": "accepted-risk-unguarded", "reason": "two"},
        ]}},
    )
    problems, _ = GATE.check(repo)
    assert any("more than once" in p for p in problems), problems


def test_each_class_in_a_multi_class_row_owes_its_own_reason(tmp_path: Path) -> None:
    # A shared reason would describe at most half the row.
    repo = _tree(
        tmp_path,
        {"scripts/thin.py": CALLS_LOADER},
        {"scripts/thin.py": {"verdicts": [
            {"verdict": "accepted-risk-unguarded", "reason": "unguarded"},
            {"verdict": "no-version-validation", "reason": "  "},
        ]}},
    )
    problems, _ = GATE.check(repo)
    assert any("carries no reason" in p for p in problems), problems


def test_an_empty_verdicts_list_is_refused(tmp_path: Path) -> None:
    repo = _tree(
        tmp_path,
        {"scripts/empty.py": CALLS_LOADER},
        {"scripts/empty.py": {"verdicts": []}},
    )
    problems, _ = GATE.check(repo)
    assert any("non-empty list" in p for p in problems), problems


def test_the_real_repo_carries_the_measured_multi_class_row() -> None:
    """The live assertion. `build_retro_lesson_selection_index.py` was verified against the
    file before the schema changed: line 55 calls `load_adapter` with no `errors` check, and
    line 33 reads `.agents/retro-adapter.yaml` raw. Both classes, one file."""
    rows = json.loads((ROOT / GATE.MANIFEST_REL).read_text(encoding="utf-8"))["consumers"]
    entry = rows["scripts/build_retro_lesson_selection_index.py"]
    classes = {row["verdict"] for row in GATE.row_verdicts(entry)}
    assert classes == {"accepted-risk-unguarded", "no-version-validation"}


def test_the_cli_names_how_many_files_carry_more_than_one_class(tmp_path: Path) -> None:
    # The line that makes a moved count vector legible. Without it a reader seeing
    # `122 across 121` has to work out where the extra classification came from, and the
    # most available wrong answer is "the debt grew".
    repo = _tree(
        tmp_path,
        {"scripts/two.py": CALLS_LOADER},
        {"scripts/two.py": {"verdicts": [
            {"verdict": "accepted-risk-unguarded", "reason": "unguarded loader call"},
            {"verdict": "no-version-validation", "reason": "also reads the yaml raw"},
        ]}},
    )
    result = run_loaded_script_main(
        "check_adapter_consumer_classification.py", GATE, "--repo-root", str(repo)
    )
    assert result.returncode == 0, result.stderr
    assert "total classifications: 2 across 1 file(s)" in result.stdout
    assert "1 file(s) carry more than one defect class" in result.stdout


def test_the_guarded_witness_refuses_a_comment_and_the_narrow_predicate(tmp_path: Path) -> None:
    """Round 2 of the slice-5 review found this gate's `guarded` witness unable to
    witness the property it names, TWICE, at two depths.

    The first witness was the bare module name `adapter_version_verdict`. Three files were
    passing as `guarded` while asking `version_refused`, which answers False for a parser
    refusal — so the same "nothing declared is honored" state walked past them, and one of
    the three wrote two durable files to a directory the repo never named at exit 0.

    Tightening it to the widened names as a SUBSTRING of the file text was the same defect
    one layer up: the repair's own explanatory comment contained the name, so a revert to
    `version_refused` left this gate green. Mutation-tested rather than assumed, which is
    how that was found. It now asks whether the file CALLS one of them.
    """
    narrow = "def go(root):\n    p = load_adapter(root)\n    return version_refused(p['errors'])\n"
    repo = _tree(
        tmp_path / "a",
        {"scripts/narrow.py": narrow},
        {"scripts/narrow.py": {"verdict": "guarded-all-doors", "reason": "asks the narrow predicate"}},
    )
    problems, _ = GATE.check(repo)
    assert any("references none of" in p for p in problems), problems

    commented = (
        "def go(root):\n"
        "    # widened to declarations_unhonored, see the slice-5 round-2 review\n"
        "    p = load_adapter(root)\n"
        "    return version_refused(p['errors'])\n"
    )
    repo = _tree(
        tmp_path / "b",
        {"scripts/commented.py": commented},
        {"scripts/commented.py": {"verdict": "guarded-all-doors", "reason": "names it in a comment only"}},
    )
    problems, _ = GATE.check(repo)
    assert any("references none of" in p for p in problems), problems

    real = "def go(root):\n    p = load_adapter(root)\n    return declarations_unhonored(p['errors'])\n"
    repo = _tree(
        tmp_path / "c",
        {"scripts/real.py": real},
        # `declarations_unhonored` ALONE is a predicate over `errors`, so this file is
        # `guarded-errors-only` — the level `#675` split out. Claiming all-doors for it is
        # refused below.
        {"scripts/real.py": {"verdict": "guarded-errors-only", "reason": "asks the condition"}},
    )
    problems, _ = GATE.check(repo)
    assert problems == [], problems


def test_the_witness_refuses_a_row_that_claims_a_level_its_calls_do_not_hold(tmp_path: Path) -> None:
    """`#675`'s whole point: one `guarded` token covered materially different coverage, and
    the witness saw membership only. A file asking `declarations_unhonored` cannot see a
    line the parser silently DROPPED — `errors: []`, `valid: True`, declaration gone — so
    recording it beside a file that routes through `unspeakable_version_message` made two
    rows with the same token differ by whether a one-character typo bypassed them."""
    errors_only = "def go(root):\n    p = load_adapter(root)\n    return declarations_unhonored(p['errors'])\n"
    repo = _tree(
        tmp_path / "over",
        {"scripts/over.py": errors_only},
        {"scripts/over.py": {"verdict": "guarded-all-doors", "reason": "claims more than it holds"}},
    )
    problems, _ = GATE.check(repo)
    assert any("its own calls establish `guarded-errors-only`" in p for p in problems), problems

    all_doors = "def go(root):\n    return refuse_unspeakable_version(load_adapter, root, adapter_name='x')\n"
    repo = _tree(
        tmp_path / "under",
        {"scripts/under.py": all_doors},
        {"scripts/under.py": {"verdict": "guarded-errors-only", "reason": "claims less than it holds"}},
    )
    problems, _ = GATE.check(repo)
    # BOTH DIRECTIONS. The previous witness checked membership, so an over-conservative row
    # was never checked at all — and one sat wrong through an entire slice.
    assert any("its own calls establish `guarded-all-doors`" in p for p in problems), problems


def test_upstream_coverage_must_name_rows_that_are_themselves_guarded(tmp_path: Path) -> None:
    """"Every caller is guarded" is a claim about an ENUMERATED set, and this census's own
    blind class is that it classifies files rather than call sites. A chain of
    caller-coverage ending in nothing is not coverage."""
    unguarded = "def go(root):\n    p = load_adapter(root)\n    return p['data']\n"
    repo = _tree(
        tmp_path / "chain",
        {"scripts/leaf.py": unguarded, "scripts/mid.py": unguarded},
        {
            "scripts/leaf.py": {
                "verdict": "guarded-upstream",
                "reason": "covered upstream",
                "covering_rows": ["scripts/mid.py"],
            },
            "scripts/mid.py": {"verdict": "accepted-risk-unguarded", "reason": "not guarded at all"},
        },
    )
    problems, _ = GATE.check(repo)
    assert any("is not itself guarded" in p for p in problems), problems

    repo = _tree(
        tmp_path / "bare",
        {"scripts/leaf.py": unguarded},
        {"scripts/leaf.py": {"verdict": "guarded-upstream", "reason": "covered, somehow"}},
    )
    problems, _ = GATE.check(repo)
    assert any("covering_rows" in p for p in problems), problems

    # A named caller with NO row at all. Distinct from a caller whose row is unguarded: the
    # first is a claim about a file the census never saw, and reporting it as "not guarded"
    # would tell the author to fix a row that does not exist.
    repo = _tree(
        tmp_path / "phantom",
        {"scripts/leaf.py": unguarded},
        {
            "scripts/leaf.py": {
                "verdict": "guarded-upstream",
                "reason": "covered by a file nobody classified",
                "covering_rows": ["scripts/nowhere.py"],
            }
        },
    )
    problems, _ = GATE.check(repo)
    assert any("carries no census row" in p for p in problems), problems


def test_the_counts_name_the_errors_only_bypass_and_print_in_coverage_order(tmp_path: Path) -> None:
    """The class this vocabulary created to make a live bypass legible printed as a bare
    number, sorted alphabetically into the middle. `accepted-risk-unguarded` has carried a
    callout sentence since it existed, for the same reason: a risk that stops being named
    stops being decided."""
    errors_only = "def go(root):\n    p = load_adapter(root)\n    return declarations_unhonored(p['errors'])\n"
    all_doors = "def go(root):\n    return refuse_unspeakable_version(load_adapter, root, adapter_name='x')\n"
    repo = _tree(
        tmp_path / "counts",
        {"scripts/weak.py": errors_only, "scripts/strong.py": all_doors},
        {
            "scripts/weak.py": {"verdict": "guarded-errors-only", "reason": "errors channel only"},
            "scripts/strong.py": {"verdict": "guarded-all-doors", "reason": "all three"},
        },
    )
    module = load_script_module("gate_cli_counts", ROOT / "scripts/check_adapter_consumer_classification.py")
    result = run_loaded_script_main(
        "scripts/check_adapter_consumer_classification.py", module, "--repo-root", str(repo)
    )
    assert result.returncode == 0, result.stderr
    assert "ERRORS-ONLY: 1 consumer(s)" in result.stdout
    assert "one-typo bypass" in result.stdout
    # Coverage order, strongest first — not the alphabetical order that sorts the weakest
    # level into the middle.
    assert result.stdout.index("guarded-all-doors") < result.stdout.index("guarded-errors-only")


def test_a_malformed_verdicts_list_is_refused_rather_than_read_as_empty(tmp_path: Path) -> None:
    """`verdicts` that is not a list yields no rows, and the entry then falls to the
    non-empty check that names it — rather than being read as a file with nothing declared,
    which is how an unclassified consumer would look."""
    repo = _tree(
        tmp_path / "shape",
        {"scripts/leaf.py": CALLS_LOADER},
        {"scripts/leaf.py": {"verdicts": {"verdict": "guarded-all-doors", "reason": "a mapping, not a list"}}},
    )
    problems, _ = GATE.check(repo)
    assert any("must be a non-empty list" in p for p in problems), problems


def test_covering_rows_entries_must_be_paths_and_a_malformed_one_refuses(tmp_path: Path) -> None:
    """A non-string entry made `caller not in declared` raise `TypeError: unhashable type`
    — an uncaught traceback out of a proof surface, where a named refusal belongs."""
    unguarded = "def go(root):\n    p = load_adapter(root)\n    return p['data']\n"
    repo = _tree(
        tmp_path / "malformed",
        {"scripts/leaf.py": unguarded},
        {
            "scripts/leaf.py": {
                "verdict": "guarded-upstream",
                "reason": "covered, allegedly",
                "covering_rows": [["scripts/nested.py"]],
            }
        },
    )
    problems, _ = GATE.check(repo)
    assert any("must be repo-relative paths" in p for p in problems), problems


def test_a_multi_verdict_row_keeps_the_entrys_covering_rows(tmp_path: Path) -> None:
    """The first fix was ONE-SIDED: only the single-verdict branch carried the entry's extra
    keys, so an entry-level `covering_rows` beside a `verdicts` list was dropped and the gate
    reported a row owing a list it plainly carried — a checker losing evidence rather than a
    row lacking it, in the shape the first fix did not touch."""
    both = (
        "def go(root):\n    p = load_adapter(root)\n    return p['data']\n"
        "def raw(root):\n    return load_yaml_file(root / '.agents/x.yaml')\n"
    )
    guard = "def go(root):\n    return refuse_unspeakable_version(load_adapter, root, adapter_name='x')\n"
    repo = _tree(
        tmp_path / "multi",
        {"scripts/leaf.py": both, "scripts/up.py": guard},
        {
            "scripts/leaf.py": {
                "covering_rows": ["scripts/up.py"],
                "verdicts": [
                    {"verdict": "guarded-upstream", "reason": "covered upstream"},
                    {"verdict": "no-version-validation", "reason": "second call site reads raw"},
                ],
            },
            "scripts/up.py": {"verdict": "guarded-all-doors", "reason": "real"},
        },
    )
    problems, _ = GATE.check(repo)
    assert problems == [], problems


def test_a_file_that_guards_itself_may_not_claim_upstream_coverage(tmp_path: Path) -> None:
    """The token means "cannot guard itself". A file that asks the condition and records
    caller coverage hides its own level behind someone else's."""
    guards = "def go(root):\n    return refuse_unspeakable_version(load_adapter, root, adapter_name='x')\n"
    repo = _tree(
        tmp_path / "self",
        {"scripts/self.py": guards, "scripts/caller.py": guards},
        {
            "scripts/self.py": {
                "verdict": "guarded-upstream",
                "reason": "hiding its own level",
                "covering_rows": ["scripts/caller.py"],
            },
            "scripts/caller.py": {"verdict": "guarded-all-doors", "reason": "real"},
        },
    )
    problems, _ = GATE.check(repo)
    assert any("guards ITSELF" in p for p in problems), problems
