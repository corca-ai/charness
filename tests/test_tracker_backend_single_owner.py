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

import importlib.util
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


# Every root that can hold a module reading the `issue_backend` adapter key. A bounded round
# found the FOURTH copy of this rule in `scripts/`, which the first version of this sweep did
# not look at while its name claimed "no other module" — the guard's own scope was the defect.
_BACKEND_ROOTS = (
    "scripts",
    "skills/public/issue/scripts",
    "skills/public/handoff/scripts",
    "skills/public/release/scripts",
)
# The one module that still derives the rule itself, named with its reason rather than left
# invisible. Its built-in default is not a template at all: it assembles a GraphQL invocation
# with conditional `-F` flags, so the owner's render-a-template contract does not fit it as
# written. Consolidating it needs the default expressed as a template first, which is a
# separate change with its own review — tracked, not hidden. An entry here is a debt record:
# removing one is progress, and adding one requires justifying it in this list.
_KNOWN_UNCONSOLIDATED = {"scripts/issue_source_capture_lib.py"}
_BINARY_DERIVATION = 'backend.get("binary") or backend.get("id")'


def test_no_other_module_re_derives_the_backend_binary_and_template_rule() -> None:
    """The consolidation's guard: a re-grown copy fails here.

    The tell is the expression the issue used as its own evidence — falling back through
    `binary` then `id`. Only the owner may decide that.

    Honest about reach: this is a substring match, so a copy spelled
    `backend.get('binary')` with single quotes, or split across two statements, evades it. It
    is a ratchet against the likely regression, not a proof — and its scope is now every root
    that can hold such a module, because the previous version's two-directory scope was itself
    how the fourth copy stayed green.
    """
    owner_rel = "skills/public/issue/scripts/issue_backend.py"
    owner = (ROOT / owner_rel).read_text(encoding="utf-8")
    assert _BINARY_DERIVATION in owner, "the owner no longer resolves the binary; re-anchor this test"

    modules = sorted(
        path
        for root in _BACKEND_ROOTS
        if (ROOT / root).is_dir()
        for path in (ROOT / root).glob("*.py")
    )
    assert len(modules) >= 100, "the module sweep collapsed; re-anchor its roots"

    offenders = []
    for path in modules:
        relative = str(path.relative_to(ROOT))
        if relative == owner_rel or relative in _KNOWN_UNCONSOLIDATED:
            continue
        if _BINARY_DERIVATION in path.read_text(encoding="utf-8"):
            offenders.append(relative)
    assert offenders == [], (
        f"{offenders} re-derive the backend binary instead of calling "
        "issue_backend.resolve_op / try_resolve_op; that is the copy this slice removed"
    )


def test_every_known_unconsolidated_copy_is_still_really_there() -> None:
    """The exception list cannot rot into a lie.

    A named exception is only honest while the thing it excuses exists. If a copy is
    consolidated and its entry is left behind, the entry silently starts excusing nothing while
    reading as outstanding debt — and the next reader trusts a stale ledger.
    """
    for relative in sorted(_KNOWN_UNCONSOLIDATED):
        path = ROOT / relative
        assert path.is_file(), f"{relative} no longer exists; drop it from _KNOWN_UNCONSOLIDATED"
        assert _BINARY_DERIVATION in path.read_text(encoding="utf-8"), (
            f"{relative} no longer re-derives the rule; drop it from _KNOWN_UNCONSOLIDATED "
            "rather than leaving a stale exemption"
        )


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


def _load_handoff_backend():
    """A real module object, not `runpy.run_path`.

    `run_path` returns a COPY of the executed globals, so assigning into that dict does not
    reach the functions' own `__globals__` — patches silently do nothing and the tests pass for
    the wrong reason. Three of the tests below need to patch the loader or read a module-level
    diagnostic, so they need the real thing. A fresh instance per call also keeps the memo from
    leaking between tests.
    """
    spec = importlib.util.spec_from_file_location("_handoff_backend_under_test", _HANDOFF_BACKEND)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _handoff_state(backend_dict, *, runner):
    return _load_handoff_backend().issue_state("o/r", 7, backend=backend_dict, runner=runner)


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


def test_the_owner_module_is_loaded_once_not_once_per_issue() -> None:
    """Repair #4 asserted, because deleting the memo failed no test.

    `resolve_issue_states` does one state lookup per cited backlog issue, the skill loaders do
    not cache, and `parse_handoff_entries` carries a comment warning that per-issue work blows
    its timeout. Reading and exec'ing the owner per issue would put that cost straight back.
    """
    handoff = _load_handoff_backend()
    loads: list[str] = []
    real = handoff._load_issue_module

    def counting_loader(root, name):
        loads.append(name)
        return real(root, name)

    handoff._load_issue_module = counting_loader
    handoff._ISSUE_BACKEND_OWNER = None

    def runner(argv):
        return {"number": 7, "state": "OPEN"}

    for _ in range(4):
        handoff.issue_state("o/r", 7, backend=dict(_GH_BACKEND), runner=runner)

    assert loads.count("issue_backend") == 1, (
        f"the owner was loaded {loads.count('issue_backend')} times for 4 lookups; the memo is gone"
    )


def test_a_view_state_template_that_omits_the_issue_number_is_refused() -> None:
    """`{number}` is identity-bearing, so an empty required set was the wrong repair.

    A `view_state` template without `{number}` resolves to a listing. Its first row is then
    read as the state of whichever issue was asked about, so a live backlog citation is
    reported CLOSED — silently, with `issue_states_checked: true`. That is the manufactured
    stale verdict this module exists to refuse, so resolution must fail loudly instead.
    """
    handoff = _load_handoff_backend()
    backend = {
        "id": "acme",
        "binary": "acme",
        "commands": {"view_state": ["issue", "list", "--repo", "{repo}", "--json", "number,state"]},
    }

    def runner(argv):  # pragma: no cover - resolution must fail before this
        raise AssertionError("a number-less view_state template must not reach the runner")

    assert handoff.issue_state("o/r", 451, backend=backend, runner=runner) is None
    assert "number" in (handoff.LAST_STATE_RESOLUTION_DIAGNOSTIC or ""), (
        "the reason a state could not be resolved must survive; a broken template and an "
        "unreachable tracker read identically once the message is dropped"
    )


def test_a_payload_describing_a_different_issue_is_not_that_issues_state() -> None:
    """Second guard, for a template that resolves but still answers about the wrong issue."""
    handoff = _load_handoff_backend()

    def runner(argv):
        return {"number": 999, "state": "CLOSED"}

    assert handoff.issue_state("o/r", 451, backend=dict(_GH_BACKEND), runner=runner) is None


def test_a_missing_issue_backend_module_reports_UNKNOWN_rather_than_aborting_the_pickup() -> None:
    """The escape this slice CREATED: handoff now needs a module older installs may not carry.

    `_load_issue_module` raises ImportError, not RuntimeError, so the first version of the
    guard let it through — and `issue_state`'s callers have no handler up to an `except`-less
    `main()`, so one partially-synced install aborted the entire chunked-routing run.
    """
    handoff = _load_handoff_backend()

    def missing(root, name):
        raise ImportError(f"issue skill script {name}.py not found")

    handoff._load_issue_module = missing
    handoff._ISSUE_BACKEND_OWNER = None

    def runner(argv):  # pragma: no cover - resolution must fail before this
        raise AssertionError("resolution should have failed")

    assert handoff.issue_state("o/r", 7, backend=dict(_GH_BACKEND), runner=runner) is None
    assert "ImportError" in (handoff.LAST_STATE_RESOLUTION_DIAGNOSTIC or "")


def _load_issue_runtime():
    spec = importlib.util.spec_from_file_location(
        "_issue_runtime_under_test", _ISSUE_SCRIPTS / "issue_runtime.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_newest_open_issue_resolves_through_the_owner_for_both_backend_shapes() -> None:
    """The other delegation site, which no test reached.

    The changed-line mutation gate flagged this call as uncovered: `newest_open_issue` was
    rewritten to delegate and nothing exercised it, so the delegation was asserted only by the
    structural sweep. Both shapes matter — the built-in `gh` default and a host template.
    """
    runtime = _load_issue_runtime()
    seen: dict[str, list[str]] = {}

    def fake_backend_json(argv):
        seen["argv"] = argv
        return [{"number": 12, "title": "newest", "url": "u", "state": "OPEN"}]

    runtime._backend_json = fake_backend_json

    assert runtime.newest_open_issue("o/r")["number"] == 12
    assert seen["argv"][0] == "gh"
    assert "o/r" in seen["argv"]

    host = {"id": "acme", "binary": "acme", "commands": {"search_newest_open": ["newest", "{repo}"]}}
    assert runtime.newest_open_issue("o/r", host)["number"] == 12
    assert seen["argv"] == ["acme", "newest", "o/r"]


def test_newest_open_issue_refuses_a_search_template_that_omits_the_repo() -> None:
    """`{repo}` is REQUIRED for a SEARCH, unlike a listing's page size.

    A search template without the repo returns another repository's newest issue, which the
    caller then acts on as if it were this one. The two delegation sites make opposite
    `required` choices on purpose, and this pins the reason rather than leaving it to a comment.
    """
    runtime = _load_issue_runtime()

    def fake_backend_json(argv):  # pragma: no cover - resolution must fail first
        raise AssertionError("a repo-less search template must not reach the backend")

    runtime._backend_json = fake_backend_json
    host = {"id": "acme", "binary": "acme", "commands": {"search_newest_open": ["newest", "--all"]}}

    with pytest.raises(RuntimeError, match="missing required placeholders"):
        runtime.newest_open_issue("o/r", host)

