"""Call-site accounting and non-claim tests for the mutation sweep.

This module owns the separate question of whether a mutation removed a caller,
because that declaration-driven contract is cohesive but independent from the
sweep runner's baseline, restoration, and verdict mechanics.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .test_mutate_and_restore import (
    GOOD_TEST,
    PYTEST_CMD,
    SCRIPT,
    SUBJECT,
    _plan,
    _repo,
    mar,
)

# --- #564: the call-site question, as tool behaviour rather than a remembered rule ---

CALLER_SUBJECT = (
    "def guard(value):\n"
    "    return value\n"
    "\n"
    "\n"
    "def run(value):\n"
    "    value = guard(value)\n"
    "    return value\n"
)


def test_deleting_a_call_site_is_detected_as_a_removed_call() -> None:
    """`#564`'s whole shape: the callee still exists, the invocation is gone.

    A body-level classifier sees a function that is still defined and still correct and
    reports nothing. The fact that matters is that the CALL disappeared -- three repairs
    in one goal died exactly here with the suite green.
    """
    mutated = CALLER_SUBJECT.replace("    value = guard(value)\n", "    pass\n")

    assert mar.removed_calls(CALLER_SUBJECT.encode(), mutated.encode()) == ("guard",)


def test_a_body_only_mutation_removes_no_call() -> None:
    """The other direction, so the classifier is not just answering "something changed".

    Without this, a classifier that returned every callee in the file would pass the test
    above and be useless -- it would report a call site for every mutant ever run.
    """
    mutated = CALLER_SUBJECT.replace(
        "    return value\n\n\ndef run", "    return value + 1\n\n\ndef run"
    )

    assert mar.removed_calls(CALLER_SUBJECT.encode(), mutated.encode()) == ()


def test_an_attribute_call_is_keyed_by_the_attribute_not_the_dotted_path() -> None:
    """`lib.helper()`, `self.helper()` and `helper()` are the same repair being reached.

    Keying on the spelling would report a REMOVED call every time an import moved, which
    would make the count noise and train a reader to ignore it.
    """
    before = b"import lib\n\n\ndef run(v):\n    return lib.helper(v)\n"
    after = b"import lib\n\n\ndef run(v):\n    return v\n"

    assert mar.removed_calls(before, after) == ("helper",)


def test_an_unparseable_side_is_unclassified_rather_than_reported_as_no_call() -> None:
    """None is not `()`, and the distinction is the point.

    A deliberate syntax-error mutant is a legitimate plan entry. If it classified as
    "removed no call" it would count toward the sweep having looked and found nothing --
    a surface claiming a scope it never read, which is the class this tool serves.
    """
    assert mar.removed_calls(CALLER_SUBJECT.encode(), b"def run(:\n") is None
    assert mar.removed_calls(b"def run(:\n", CALLER_SUBJECT.encode()) is None


def test_a_sweep_with_no_call_site_mutant_states_the_non_claim(tmp_path: Path) -> None:
    """A clean sweep must not read as proof the repair is still reached.

    `1 killed, 0 survived` is exactly what all three of `#564`'s measured instances
    printed while the repair was dead in production.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[{"id": "body", "path": "subject.py", "find": "a + b", "replace": "a * b"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["killed"] == 1
    assert payload["call_site_mutants"] == 0
    assert "says nothing about whether" in payload["call_site_non_claim"]


def test_a_sweep_containing_a_call_site_mutant_makes_no_such_non_claim(tmp_path: Path) -> None:
    """The negative test for the non-claim itself: it must be able to go away.

    A message that is always printed carries no information, and this repo has shipped
    that shape before.
    """
    caller_test = "from subject import run\n\n\ndef test_run():\n    assert run(3) == 3\n    assert run.__name__ == 'run'\n"
    repo = _repo(tmp_path, subject=CALLER_SUBJECT, test_body=caller_test)
    plan = _plan(
        mutants=[
            {
                "id": "call-site",
                "path": "subject.py",
                "find": "    value = guard(value)\n",
                "replace": "    pass\n",
                # The DECLARATION is what silences the non-claim; the removed call is the
                # corroboration. Neither alone is enough.
                "call_site": True,
            }
        ]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["call_site_mutants"] == 1
    assert payload["mutants"][0]["removed_calls"] == ["guard"]
    assert payload["call_site_non_claim"] is None


def test_a_refused_mutant_is_unclassified_rather_than_counted_as_no_call_site(
    tmp_path: Path,
) -> None:
    """A mutant refused before it was ever applied established nothing about calls.

    `None` rather than `()`: the file was never written, so "removed no call" would be a
    verdict about an edit that did not happen.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[{"id": "absent", "path": "subject.py", "find": "not-in-the-file", "replace": "x"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["mutants"][0]["verdict"] == mar.REFUSED
    assert payload["mutants"][0]["removed_calls"] is None
    assert payload["call_site_mutants"] == 0


@pytest.mark.boundary_contract(
    reason="assert the mutation runner's real CLI stdout/stderr contract for the operator non-claim"
)
def test_the_cli_prints_the_call_site_count_and_the_non_claim(tmp_path: Path) -> None:
    """Operator-visible through the real command, not buried in the runner's internals.

    Both halves must survive the trip through the CLI: the count rides in the emitted
    payload on stdout, and the non-claim is ALSO written to stderr so it survives the
    `> file` redirect this repo requires for gates -- a reader who only watches the
    terminal still cannot miss it.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            _plan(
                mutants=[{"id": "body", "path": "subject.py", "find": "a + b", "replace": "a * b"}]
            )
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = yaml.safe_load(completed.stdout)
    assert payload["call_site_mutants"] == 0, completed.stdout
    assert "says nothing about whether" in payload["call_site_non_claim"], completed.stdout
    assert "NON-CLAIM" in completed.stderr, completed.stderr


def test_every_removed_callee_is_reported_including_builtins() -> None:
    """No filtering, and the filter's removal is load-bearing rather than laziness.

    A builtins filter was written while removed calls still DROVE the non-claim. Once the
    declaration replaced that inference, the filter could only produce false negatives,
    and it produced one on this tool's own sweep: a mutant deleting the non-claim's
    `print(...)` call is a genuine call-site deletion, the filter hid it, and an honest
    declaration was REFUSED. `removed_calls` answers the question its name asks; which
    removals matter is the reader's judgement.
    """
    before = b"def run(v):\n    return tuple(sorted(guard(v)))\n"
    after = b"def run(v):\n    return ()\n"

    assert mar.removed_calls(before, after) == ("guard", "sorted", "tuple")


def test_an_undeclared_call_removal_does_not_silence_the_non_claim(tmp_path: Path) -> None:
    """Round 1's blocker: the inferred count silenced the tool's own warning.

    `_called_names` keys attribute calls by attribute, so `.join`, `.get`, `.search`,
    `.elements` all count as removed calls. A pure body mutant that happens to drop one
    was classified as caller-side proof and the `#564` non-claim went silent -- the tool
    suppressing its own finding on evidence that did not mean what it counted. Measured
    inside this very file: `return tuple(sorted(x.elements()))` -> `return ()` reports
    `('elements',)`.

    The removed call is still REPORTED. It just no longer decides.
    """
    subject = "def add(a, b):\n    return ' '.join([str(a)]) and a + b\n"
    test_body = "from subject import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n"
    repo = _repo(tmp_path, subject=subject, test_body=test_body)
    plan = _plan(
        mutants=[
            {
                "id": "drops-join",
                "path": "subject.py",
                "find": "' '.join([str(a)]) and ",
                "replace": "",
            }
        ]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["mutants"][0]["removed_calls"] == ["join", "str"], payload["mutants"][0]
    assert payload["call_site_mutants"] == 0, "an undeclared removal must not count"
    assert payload["call_site_non_claim"] is not None, (
        "the non-claim must survive an incidental removal"
    )
    # Wording: the trigger is "no mutant was DECLARED", not "nothing was deleted".
    assert "DECLARED" in payload["call_site_non_claim"]
    assert "no mutant deleted a call site" not in payload["call_site_non_claim"]


def test_a_false_call_site_declaration_is_refused(tmp_path: Path) -> None:
    """A declaration the edit contradicts is worse than no declaration, because it SILENCES.

    This is the one place the tool has teeth on the call-site axis, and it is a fact the
    tool can actually establish: the author said this mutant deletes a call, and the parse
    of the file it wrote says it deleted none.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[
            {
                "id": "lying",
                "path": "subject.py",
                "find": "a + b",
                "replace": "a * b",
                "call_site": True,
            }
        ]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["mutants"][0]["verdict"] == mar.REFUSED
    assert "removed no call" in payload["mutants"][0]["detail"]
    assert payload["call_site_mutants"] == 0
    assert payload["call_site_non_claim"] is not None


def test_a_super_init_deletion_is_visible_to_the_classifier() -> None:
    """A textbook dead repair, and the filter round 1 found made it invisible.

    The first filter used `hasattr(builtins, name)`; `builtins` is a MODULE OBJECT, so
    dunders resolve through `type(module)` and `__init__` was dropped as a builtin. This
    repo has five `super().__init__()` call sites. The filter is now gone entirely, which
    fixes the class rather than this instance.
    """
    before = (
        b"class C(B):\n    def __init__(self):\n        super().__init__()\n        self.x = 1\n"
    )
    after = b"class C(B):\n    def __init__(self):\n        self.x = 1\n"

    assert mar.removed_calls(before, after) == ("__init__", "super")


def test_the_classification_cannot_leave_the_tree_mutated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 1's second blocker: classification sat OUTSIDE the restoring `finally`.

    `ast.parse` can raise `RecursionError` on deeply nested source and the read can raise
    `OSError`; either escaped with the file still mutated. That is `#573`, re-opened by a
    reporting feature, in a module whose docstring promises the restore covers the write.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    baseline = mar.measure_baseline(PYTEST_CMD, repo)

    def _boom(*_args, **_kwargs):
        raise RecursionError("maximum recursion depth exceeded during compilation")

    monkeypatch.setattr(mar, "removed_calls", _boom)

    with pytest.raises(RecursionError):
        mar.run_mutant(
            {"id": "m", "path": "subject.py", "find": "a + b", "replace": "a * b"},
            PYTEST_CMD,
            repo,
            baseline,
        )

    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


def test_a_declared_call_site_mutant_that_was_refused_does_not_silence_the_non_claim() -> None:
    """Round 2's second blocker: REFUSED is no answer, not a bad answer.

    A declared mutant whose run is refused (scope shrank, collection error, non-zero with
    no reported failure) established nothing about the caller -- no test reached a verdict,
    which is property 2's whole premise. Counting it as "the question was asked" silences
    the warning on a mutant that produced no result.

    SURVIVED is deliberately NOT excluded: there the question was asked and answered
    badly, and the survivor plus the non-zero exit carry that.
    """
    baseline = mar.Baseline(returncode=0, passed=5, output="5 passed in 0.10s")
    refused = mar.MutantResult("m", "subject.py", mar.REFUSED, "scope shrank", 1, ("guard",), True)
    survived = mar.MutantResult("m2", "subject.py", mar.SURVIVED, "", 0, ("guard",), True)

    assert mar.Sweep(baseline=baseline, mutants=[refused]).call_site_mutants == []
    assert mar.call_site_non_claim(mar.Sweep(baseline=baseline, mutants=[refused])) is not None
    assert mar.Sweep(baseline=baseline, mutants=[survived]).call_site_mutants == [survived]


def test_a_declared_mutant_refused_before_it_ran_still_reports_its_declaration() -> None:
    """The field must state what the PLAN said, even for a mutant that never ran.

    It used to be read after the early returns, so a declared mutant with a typo'd `find`
    reported `declared_call_site: false` -- the report contradicting the plan, handed to
    the author who is debugging exactly that typo.
    """
    result = mar.run_mutant(
        {"id": "gone", "path": "nope.py", "find": "x", "replace": "y", "call_site": True},
        PYTEST_CMD,
        Path("/tmp"),
        mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s"),
    )

    assert result.verdict == mar.REFUSED
    assert result.declared_call_site is True


def test_a_non_boolean_call_site_declaration_is_refused() -> None:
    """`bool("false")` is True, and this file refuses every other mis-keyed plan entry.

    A templated plan emitting the string `"false"` would declare the opposite of its
    author's intent and silence the non-claim.
    """
    result = mar.run_mutant(
        {"id": "stringy", "path": "subject.py", "find": "x", "replace": "y", "call_site": "false"},
        PYTEST_CMD,
        Path("/tmp"),
        mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s"),
    )

    assert result.verdict == mar.REFUSED
    assert "must be a boolean" in result.detail


def test_an_empty_plan_still_states_the_non_claim() -> None:
    """The emptiest sweep is the most unearned clean report there is.

    `0 killed, 0 survived, 0 refused`, exit 0, and -- before this repair -- no warning,
    while the module docstring promised a sweep with no declared call-site test says so
    out loud.
    """
    baseline = mar.Baseline(returncode=0, passed=5, output="5 passed in 0.10s")

    assert mar.call_site_non_claim(mar.Sweep(baseline=baseline, mutants=[])) is not None


def test_an_unearned_baseline_makes_no_call_site_claim_either_way() -> None:
    """The one silence that is right: a refused baseline prints no counts to qualify."""
    baseline = mar.Baseline(returncode=1, passed=None, output="", refusal="baseline exited 1")

    assert mar.call_site_non_claim(mar.Sweep(baseline=baseline, mutants=[])) is None


def test_the_human_line_marks_the_declaration_and_the_removals_readably() -> None:
    """The `call_site_mutants` count must be auditable per mutant while the sweep runs.

    The payload carries `declared_call_site` and `removed_calls` on every mutant, but a
    sweep is long and a reader of a truncated or still-running log only ever has the
    streamed progress lines -- so the same pair has to be legible there too. Under the
    declaration design the discriminating fact is the DECLARATION; removals alone
    rendered a declared caller test and an incidental `.join` identically. The first
    attempt at this line mismatched its brackets and printed `[call-site;[removes print]`,
    which the tool's own self-sweep surfaced.

    This reproduces the rendering rule rather than driving `run_sweep`, so it pins the
    shape and not the call site that emits it.
    """
    lines: list[str] = []
    baseline = mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s")
    sweep = mar.Sweep(baseline=baseline)

    for result, expected in (
        (
            mar.MutantResult("a", "s.py", mar.KILLED, "", 1, ("guard",), True),
            " [call-site; removes guard]",
        ),
        (mar.MutantResult("b", "s.py", mar.KILLED, "", 1, ("join",), False), " [removes join]"),
        (mar.MutantResult("c", "s.py", mar.KILLED, "", 1, (), False), ""),
    ):
        sweep.mutants.append(result)
        bits = ["call-site"] if result.declared_call_site else []
        if result.removed_calls:
            bits.append("removes " + ", ".join(result.removed_calls))
        rendered = f" [{'; '.join(bits)}]" if bits else ""
        lines.append(rendered)
        assert rendered == expected, rendered
        assert rendered.count("[") == rendered.count("]"), rendered


def test_a_computed_callee_is_bucketed_rather_than_dropped() -> None:
    """`funcs[0]()` and `factory()()` have no name, and dropping them would be a silent hole.

    A dispatch table is exactly where a repair's only caller tends to live, so a callee the
    classifier cannot name still has to register as a removal -- otherwise deleting the one
    call site that matters would classify as "removed no call" and, on a declared mutant,
    be REFUSED as a false declaration.
    """
    before = b"def run(funcs, v):\n    return funcs[0](v)\n"
    after = b"def run(funcs, v):\n    return v\n"

    assert mar.removed_calls(before, after) == ("<computed>",)

    # And it corroborates a declaration end to end, rather than only existing in the map.
    baseline = mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s")
    declared = mar.MutantResult("m", "s.py", mar.KILLED, "", 1, ("<computed>",), True)
    assert mar.Sweep(baseline=baseline, mutants=[declared]).call_site_mutants == [declared]
