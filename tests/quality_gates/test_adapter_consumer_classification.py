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
from pathlib import Path

import pytest

from tests.script_main import load_script_module

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
