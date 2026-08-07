"""Tracker backend resolution has ONE owner, and the two refusal contracts both survive.

#555. Resolving a GitHub tracker command — pick the binary, look up the adapter's
`commands.<op>` template, fall back to the built-in `gh` default, substitute placeholders —
was implemented THREE times:

- `skills/public/issue/scripts/issue_backend.py::resolve_op` — the owner, and the only one
  that validated placeholders against an allowlist.
- `skills/public/issue/scripts/issue_runtime.py::newest_open_issue` — a copy inside the same
  skill as the owner, without that validation.
- `skills/public/handoff/scripts/chunked_routing_issue_backend.py::_resolve_command` — a copy
  in another skill, also without it.

The premise check found why the copies existed, and it was not laziness: the two callers need
OPPOSITE answers to one question. An op a non-`gh` backend never declared is a configuration
error to `issue` (raise) and an UNKNOWN to `handoff` (return None, because
`chunked_routing_staleness` consumes it and a guess there manufactures a stale verdict). So
the consolidation keeps one implementation of the mechanical part and gives the differing
policy its own entry point, `try_resolve_op`.

That is the trade this repo's boundary rule names — consolidation creates a shared surface
that can drift — so what is pinned here is that neither refusal contract can be quietly
swapped for the other, and that no module re-derives the mechanical part.
"""

from __future__ import annotations

import runpy

import pytest

from tests.quality_gates.support import ROOT

_ISSUE_SCRIPTS = ROOT / "skills/public/issue/scripts"
_BACKEND = runpy.run_path(str(_ISSUE_SCRIPTS / "issue_backend.py"))
_resolve_op = _BACKEND["resolve_op"]
_try_resolve_op = _BACKEND["try_resolve_op"]

_HANDOFF_BACKEND = ROOT / "skills/public/handoff/scripts/chunked_routing_issue_backend.py"

_GH_BACKEND = {"id": "gh", "binary": "gh", "commands": None}
_HOST_BACKEND_WITHOUT_OP = {"id": "acme", "binary": "acme", "commands": {"other_op": ["x"]}}
_HOST_BACKEND_WITH_OP = {"id": "acme", "binary": "acme", "commands": {"list_open": ["ls", "{repo}"]}}


def test_the_owner_and_its_non_raising_variant_agree_whenever_the_op_resolves() -> None:
    """`try_resolve_op` differs from `resolve_op` in exactly one answer, not in rendering."""
    for backend in (_GH_BACKEND, _HOST_BACKEND_WITH_OP):
        strict = _resolve_op(
            backend, "list_open", ["issue", "list", "--repo", "{repo}"], frozenset({"repo"}), repo="o/r"
        )
        lenient = _try_resolve_op(
            backend, "list_open", ["issue", "list", "--repo", "{repo}"], frozenset({"repo"}), repo="o/r"
        )
        assert lenient == strict, f"the two entry points rendered differently for {backend['id']}"


def test_an_undeclared_op_raises_for_the_actor_and_returns_None_for_the_reader() -> None:
    """The one difference, asserted in both directions.

    Collapsing these two into one function is the repair #555's own suggested direction
    implied, and it would have converted a staleness reader's UNKNOWN into an exception.
    """
    args = (_HOST_BACKEND_WITHOUT_OP, "list_open", ["issue", "list", "--repo", "{repo}"], frozenset({"repo"}))

    with pytest.raises(RuntimeError, match="did not declare commands.list_open"):
        _resolve_op(*args, repo="o/r")

    assert _try_resolve_op(*args, repo="o/r") is None


def test_the_non_raising_variant_still_raises_on_a_caller_or_adapter_bug() -> None:
    """`try_resolve_op` must not become a blanket exception swallower.

    Only the undeclared-op answer changes. A bad placeholder is a bug in both worlds, and
    turning it into a silent None would hide an adapter smuggling an unknown substitution —
    which is the validation the two copies lacked and the reason delegating to the owner is an
    improvement rather than a lateral move.
    """
    with pytest.raises(RuntimeError, match="not in op's allowlist"):
        _try_resolve_op(
            _GH_BACKEND, "list_open", ["issue", "list"], frozenset({"repo"}), repo="o/r", sneaky="x"
        )

    with pytest.raises(RuntimeError, match="unknown placeholders"):
        _try_resolve_op(
            _GH_BACKEND, "list_open", ["issue", "list", "{not_allowed}"], frozenset({"repo"}), repo="o/r"
        )


def test_no_other_module_re_derives_the_backend_binary_and_template_rule() -> None:
    """The consolidation's guard: a re-grown copy fails here.

    The tell is the expression the issue used as its own evidence — falling back through
    `binary` then `id` then a hardcoded `"gh"`. Only the owner may decide that. Scoped to the
    tracker-backend modules rather than the whole tree, because unrelated code may legitimately
    read a `binary` key.
    """
    owner_rel = "skills/public/issue/scripts/issue_backend.py"
    owner = (ROOT / owner_rel).read_text(encoding="utf-8")
    assert 'backend.get("binary") or backend.get("id")' in owner, (
        "the owner no longer resolves the binary; re-anchor this test"
    )

    tracker_modules = sorted(
        path
        for root in ("skills/public/issue/scripts", "skills/public/handoff/scripts")
        for path in (ROOT / root).glob("*.py")
    )
    assert len(tracker_modules) >= 20, "the tracker-module sweep collapsed; re-anchor it"

    for path in tracker_modules:
        relative = str(path.relative_to(ROOT))
        if relative == owner_rel:
            continue
        source = path.read_text(encoding="utf-8")
        assert 'backend.get("binary") or backend.get("id")' not in source, (
            f"{relative} re-derives the backend binary instead of calling "
            "issue_backend.resolve_op / try_resolve_op; that is the copy #555 removed"
        )
        # Deliberately NOT asserting the absence of a `gh` fallback generally: the adapter
        # RESOLVER's job is to supply the default backend id when a repo declares none, and
        # a first draft of this guard flagged it. The tell for the removed copy is the
        # binary-derivation expression above, not the presence of the string "gh".


def test_handoff_resolves_through_the_issue_owner_rather_than_its_own_copy() -> None:
    """Direction matters: `issue` is the contractual owner of tracker access and is a leaf.

    `handoff` already imported `issue` modules for its runner, so the route existed; it just
    was not used for the resolution half. Pinned structurally because the alternative — an
    extract to `skills/shared/` — would move the surface away from its contractual owner, and
    a future refactor should have to argue with a failing test rather than a comment.
    """
    source = _HANDOFF_BACKEND.read_text(encoding="utf-8")
    assert "try_resolve_op(" in source, "handoff no longer delegates to the issue owner"
    assert '_load_issue_module(' in source and '"issue_backend"' in source, (
        "handoff must reach the owner through the route-reuse loader it already had"
    )
    assert "frozenset()" in source, (
        "handoff must pass an EMPTY required set: equating it with the allowlist makes every "
        "placeholder mandatory and invalidates adapter templates that were valid before"
    )

    issue_sources = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "skills/public/issue/scripts").glob("*.py")
    )
    assert "chunked_routing" not in issue_sources, (
        "the `issue` skill imported `handoff`; the dependency direction that makes this "
        "consolidation safe is `handoff` -> `issue`, and `issue` must stay a leaf"
    )


_HANDOFF = runpy.run_path(str(_HANDOFF_BACKEND))


def _handoff_state(backend_dict, *, runner):
    return _HANDOFF["issue_state"]("o/r", 7, backend=backend_dict, runner=runner)


def test_handoff_accepts_an_adapter_template_that_omits_an_allowed_placeholder() -> None:
    """The one shape the delegation narrowed, asserted through the PUBLIC caller.

    A host whose binary carries the repo declares no `{repo}`; one whose listing pages
    internally declares no `{limit}`. Both were valid before. Requiring every allowed
    placeholder would have rejected them, and no fixture in the slice would have noticed
    because each one happens to spell every placeholder.
    """
    backend = {"id": "acme", "binary": "acme", "commands": {"view_state": ["issue", "view", "{number}"]}}

    seen: dict[str, list[str]] = {}

    def runner(argv):
        seen["argv"] = argv
        return {"number": 7, "state": "OPEN"}

    assert _handoff_state(backend, runner=runner) == "OPEN"
    assert seen["argv"] == ["acme", "issue", "view", "7"]


def test_handoff_reports_UNKNOWN_rather_than_crashing_on_a_misconfigured_adapter() -> None:
    """An adapter bug must not abort the pickup.

    `issue_state`'s callers have no handler up to an `except`-less `main()`, so a raise here
    kills the whole chunked-routing run over one bad key. The owner raises for these — rightly,
    for callers that ACT on the tracker — and this reader converts them to UNKNOWN, which is
    what its contract promises. Both templates below are accepted by the adapter parser and
    refused by the owner.
    """
    unknown_placeholder = {
        "id": "acme", "binary": "acme", "commands": {"view_state": ["view", "{not_a_placeholder}"]}
    }
    no_usable_binary = {"commands": {"view_state": ["view", "{number}"]}}

    def runner(argv):  # pragma: no cover - must not be reached
        raise AssertionError("resolution should have failed before the runner ran")

    assert _handoff_state(unknown_placeholder, runner=runner) is None
    assert _handoff_state(no_usable_binary, runner=runner) is None


def test_handoff_still_reports_UNKNOWN_for_an_undeclared_op() -> None:
    """The original contract, unchanged by the consolidation."""

    def runner(argv):  # pragma: no cover - must not be reached
        raise AssertionError("an undeclared op should not reach the runner")

    assert _handoff_state({"id": "acme", "binary": "acme", "commands": {"other": ["x"]}}, runner=runner) is None

