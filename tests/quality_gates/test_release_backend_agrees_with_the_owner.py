"""Two implementations of one command-resolution rule, pinned to agree where they can.

`publish_release_helpers.backend_command` and `issue_backend.resolve_op` implement the same
rule over two different adapter keys. A prior slice consolidated the tracker-side copies onto
the owner; this pair was NOT consolidated, and this file is the measured reason plus the guard
that keeps the reason honest.

WHY THEY ARE NOT ONE FUNCTION, measured rather than asserted: the two adapter contracts differ
in where the BINARY lives. `issue_backend` templates exclude it and `resolve_op` prepends
`backend["binary"]`; `release_backend` templates INCLUDE it, and `backend_command` never reads
`backend["binary"]` at all. Delegating the release path to the owner therefore doubles the
binary for every existing release adapter — proven below. That is a contract change to a
consumer-facing adapter on the least reversible surface in this repo, so it is a deliberate
decision rather than a refactor, and it is recorded here instead of being discovered by a
release that published the wrong command.

WHAT MUST STILL AGREE is everything else, and the drift that prompted this was in exactly that
part: the release copy rendered `part.format(...)` only `if subs and "{" in part`, so a
brace-bearing template invoked with no substitutions passed through VERBATIM here and raised in
the owner. On a release surface that means running against a literal `{tag}`.
"""

from __future__ import annotations

import runpy

import pytest

from tests.quality_gates.support import ROOT
from tests.quality_gates.seeding_support import load_module

HELPERS = runpy.run_path(str(ROOT / "skills/public/release/scripts/publish_release_helpers.py"))
backend_command = HELPERS["backend_command"]


def _owner():
    source = ROOT / "skills/public/issue/scripts/issue_backend.py"
    return load_module("_owner_for_release_parity", source, register=True)


OWNER = _owner()
TAG = frozenset({"tag"})


def test_the_two_implementations_render_the_same_template_the_same_way() -> None:
    """The shared part, differentially. `binary` is the ONLY documented difference."""
    backend = {"id": "acme", "binary": "acme", "commands": {"release_view": ["rel", "show", "{tag}"]}}

    release = backend_command(backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3")
    owner = OWNER.resolve_op(
        backend, "release_view", ["release", "view", "{tag}"], TAG, tag="v1.2.3"
    )

    # Same rendering; the owner additionally prepends the binary, which is the contract split.
    assert release == ["rel", "show", "v1.2.3"]
    assert owner == ["acme", "rel", "show", "v1.2.3"]
    assert owner[1:] == release, "the two implementations diverged on rendering"


def test_the_binary_contract_is_why_they_are_not_one_function() -> None:
    """The measured blocker, executed rather than asserted in prose.

    If the release path delegated to the owner, every existing release adapter would get its
    binary twice — the template already carries it. This test is the evidence for that
    decision, so a future consolidation has to argue with a failing test rather than a comment.
    """
    gh_default = ["gh", "release", "view", "{tag}"]
    backend = {"id": "gh", "binary": "gh", "commands": None}

    assert backend_command(backend, "release_view", gh_default, tag="v1") == [
        "gh", "release", "view", "v1",
    ]
    # The same default through the owner, which prepends the binary the template already spells.
    doubled = OWNER.resolve_op(backend, "release_view", gh_default, TAG, tag="v1")
    assert doubled == ["gh", "gh", "release", "view", "v1"], (
        "if this stops doubling, the two adapter contracts have converged and the release copy "
        "should be reconsidered for consolidation"
    )
    # And the release path genuinely never reads `binary`: changing it changes nothing.
    other = {"id": "gh", "binary": "something-else", "commands": None}
    assert backend_command(other, "release_view", gh_default, tag="v1") == [
        "gh", "release", "view", "v1",
    ]


def test_a_brace_bearing_template_with_no_substitutions_refuses_in_both() -> None:
    """The measured DRIFT, in the direction it actually mattered.

    Before this repair the release copy passed `{tag}` through verbatim and the command ran
    against a literal brace; the owner raised. Both refuse now. The refusal TYPE stays each
    caller's own policy — `SystemExit` for a CLI, the raw error for a library caller — which is
    the same mechanical-part/policy split the tracker-backend consolidation established.
    """
    backend = {"id": "gh", "binary": "gh", "commands": {"release_view": ["gh", "release", "view", "{tag}"]}}

    with pytest.raises(SystemExit) as release_refusal:
        backend_command(backend, "release_view", ["gh", "release", "view", "{tag}"])
    assert "could not be rendered" in str(release_refusal.value)

    # `(KeyError, RuntimeError)`: what must agree is that BOTH refuse, not which exception the
    # owner happens to raise today. Pinning the raw type would fail this test if the owner
    # later wrapped it — an improvement — for a reason that has nothing to do with drift.
    with pytest.raises((KeyError, RuntimeError)):
        OWNER.resolve_op(backend, "release_view", ["release", "view", "{tag}"], TAG)


@pytest.mark.parametrize(
    ("op", "template", "default", "subs"),
    [
        ("release_view", ["rel", "show", "{tag}"], ["gh", "release", "view", "{tag}"], {"tag": "v1"}),
        (
            "release_view_body",
            ["rel", "body", "{tag}"],
            ["gh", "release", "view", "{tag}"],
            {"tag": "v1"},
        ),
        (
            "release_create",
            ["rel", "new", "{tag}", "--name", "{title}"],
            ["gh", "release", "create", "{tag}", "--title", "{title}"],
            {"tag": "v1", "title": "T"},
        ),
        ("auth_check", ["rel", "whoami"], ["gh", "auth", "status"], {}),
    ],
)
def test_every_declared_op_renders_identically_in_both_implementations(op, template, default, subs) -> None:
    """The differential covered only one op, so a divergence reachable through another was
    untested. Every op in `OP_PLACEHOLDERS` is exercised, since the allowlist is per-op and a
    drift can hide behind whichever op nobody compared."""
    backend = {"id": "acme", "binary": "acme", "commands": {op: template}}
    allowed = HELPERS["OP_PLACEHOLDERS"][op]

    release = backend_command(backend, op, default, **subs)
    owner = OWNER.resolve_op(backend, op, default[1:], allowed, **subs)

    assert owner[1:] == release, f"{op} rendered differently in the two implementations"
    assert owner[0] == "acme"


def test_both_refuse_an_unknown_placeholder_and_an_unknown_caller_substitution() -> None:
    """The validation the release copy already had, pinned against the owner so it stays."""
    unknown_template = {
        "id": "gh", "binary": "gh", "commands": {"release_view": ["gh", "release", "{nope}"]},
    }
    with pytest.raises(SystemExit, match="unknown placeholders"):
        backend_command(unknown_template, "release_view", ["gh", "release", "view", "{tag}"], tag="v1")
    with pytest.raises(RuntimeError, match="unknown placeholders"):
        OWNER.resolve_op(unknown_template, "release_view", ["release", "view", "{tag}"], TAG, tag="v1")

    plain = {"id": "gh", "binary": "gh", "commands": None}
    with pytest.raises(SystemExit, match="not in op's allowlist"):
        backend_command(plain, "release_view", ["gh", "release", "view", "{tag}"], tag="v1", sneaky="x")
    with pytest.raises(RuntimeError, match="not in op's allowlist"):
        OWNER.resolve_op(plain, "release_view", ["release", "view", "{tag}"], TAG, tag="v1", sneaky="x")
