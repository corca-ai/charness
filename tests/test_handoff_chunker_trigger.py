"""Slice 7 trigger-detection fixture.

Pins the deterministic trigger rule from the spec's 7-row table at
``docs/handoff-chunked-routing.md#trigger-fixture``. Any divergence
between the spec table, the SKILL.md prose at
``skills/public/handoff/references/chunked-routing.md``, and the
implementation in
``skills/public/handoff/scripts/chunked_routing_lib.should_fire_chunker``
must surface as a test failure here.

When any of rows 3, 4, or 6 (the no-chunk cases) flips to chunk, the
"Trigger detection over-fires" Stop Condition from the goal artifact
activates: stop and re-anchor the rule.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_PATH = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "chunked_routing_lib.py"
)


def _load_lib():
    spec = importlib.util.spec_from_file_location("chunked_routing_lib", LIB_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load_lib()


TRIGGER_FIXTURE = (
    # (row_number, message, expected_decision, why)
    (1, "read docs/handoff.md", "chunk", "Handoff mention + no other directive."),
    (2, "what's next in the handoff?", "chunk", "Handoff mention via prose + question form, no directive."),
    (3, "read handoff and start slice 7", "no-chunk", "Handoff mention + explicit directive `start slice 7`."),
    (4, "push the slice 7 commits", "no-chunk", "No handoff mention."),
    (5, "핸드오프 봐", "chunk", "Korean handoff mention, no directive."),
    (6, "read handoff.md and fix #233", "no-chunk", "Handoff mention + issue id directive `fix #233`."),
    (7, "pick up from handoff", "chunk", "Handoff pickup phrase, no other noun."),
    (8, "/handoff", "chunk", "Bare slash invocation of the handoff skill, no task (#249)."),
    (9, "/handoff fix #233", "no-chunk", "Skill invocation + explicit issue directive bypasses."),
    (10, "/charness:handoff", "chunk", "Plugin-namespaced bare invocation IS the handoff command, not another slash command."),
    (11, "/charness:handoff fix #233", "no-chunk", "Namespaced invocation + explicit issue directive bypasses."),
)


@pytest.mark.parametrize("row,message,expected,why", TRIGGER_FIXTURE)
def test_trigger_detection_matches_spec_fixture(lib, row, message, expected, why):
    """Each row of the spec's 7-row trigger fixture maps deterministically
    to a chunk/no-chunk decision. Failures on rows 3, 4, or 6 activate
    the 'Trigger detection over-fires' Stop Condition."""
    decision = "chunk" if lib.should_fire_chunker(message) else "no-chunk"
    assert decision == expected, (
        f"row {row}: message={message!r} expected={expected!r} got={decision!r}; "
        f"why: {why}"
    )


def test_empty_or_whitespace_only_message_does_not_fire(lib):
    assert lib.should_fire_chunker("") is False
    assert lib.should_fire_chunker("   \n\t   ") is False


def test_polite_interrogative_handoff_phrasing_fires(lib):
    """Slice-1 critique valid-but-defer: 'could you check the handoff?'
    should fire (handoff mention + no directive). Pinning here keeps
    the imperative-vs-interrogative coverage honest."""
    assert lib.should_fire_chunker("could you check the handoff?") is True


def test_handoff_mention_with_implementation_verb_does_not_fire(lib):
    """Sanity: a clearly task-directed message mentioning the handoff
    must not fire (over-fire guard)."""
    assert lib.should_fire_chunker("read handoff.md then implement #225") is False


def test_direct_invocation_fires_without_a_mention(lib):
    """#249 trigger widening: the handoff skill launched directly (no task)
    fires even with an empty/mention-less message, but a task directive in the
    invocation args still bypasses."""
    assert lib.should_fire_chunker("", invoked_directly=True) is True
    assert lib.should_fire_chunker("please continue", invoked_directly=True) is True
    # an explicit task directive bypasses even on direct invocation
    assert lib.should_fire_chunker("work on the slack bug", invoked_directly=True) is False
    assert lib.should_fire_chunker("fix #233", invoked_directly=True) is False
    # default (not invoked directly) is unchanged: empty does not fire
    assert lib.should_fire_chunker("", invoked_directly=False) is False
