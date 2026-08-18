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
        {"scripts/liar.py": {"verdict": "guarded", "reason": "trust me"}},
    )

    problems, _counts = GATE.check(repo)

    assert any("does not reference" in problem for problem in problems), problems


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
    assert "total classified: 1" in result.stdout
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
    assert sum(counts.values()) == len(
        json.loads((ROOT / GATE.MANIFEST_REL).read_text(encoding="utf-8"))["consumers"]
    )
