"""Tracker backend resolution has ONE owner, and the two refusal contracts both survive.

#555. Resolving a GitHub tracker command — pick the binary, look up the adapter's
`commands.<op>` template, fall back to the built-in `gh` default, substitute placeholders —
had FOUR implementations: the owner plus THREE private copies. Two copies were removed by this
slice; the third could not be and is named in `_KNOWN_UNCONSOLIDATED` below.

- `skills/public/issue/scripts/issue_backend.py::resolve_op` — the owner, and the only
  implementation that validated placeholders against an allowlist.
- `skills/public/issue/scripts/issue_runtime.py::newest_open_issue` — a copy inside the same
  skill as the owner, without that validation. REMOVED.
- `skills/public/handoff/scripts/chunked_routing_issue_backend.py::_resolve_command` — a copy
  in another skill, also without it. REMOVED.
- `scripts/issue_source_capture_lib.py::build_page_argv` — found by bounded review, outside the
  first version of this guard's scope. NOW REMOVED. The reason it was deferred covered only ONE
  of its two branches: its built-in gh default really is a conditionally assembled GraphQL
  invocation rather than a template, and that branch stays local — but the adapter-TEMPLATE
  branch was exactly the owner's rule, missing the owner's allowlist, and it delegates now.

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


# Every root that can hold a module resolving a backend command. `skills/shared` and
# `skills/support` are included because this repo's older sibling gate records that omitting
# `skills/shared` once produced a clean report over a scope that excluded a real violation — a
# lesson a bounded round pointed out this test had not carried across.
_BACKEND_ROOTS = (
    "scripts",
    "skills/shared/scripts",
    "skills/public",
    "skills/support",
)
# Two tells, because a bounded round found the first one anchored on the CHEAPEST half of the
# rule. Binary derivation is the line a re-grown copy most readily delegates; the parts that
# carry the verdict are the template lookup, the built-in default, and the undeclared-op policy.
# A live instance proved it: `publish_release_helpers.backend_command` re-derives the whole rule
# and is invisible to the binary tell, because it takes the binary from the template.
_BINARY_DERIVATION = 'backend.get("binary") or backend.get("id")'
# Rendering a template into argv IS the rule, so this is the verdict-bearing tell. A first
# attempt used the bare undeclared-op condition instead and false-positived on three modules
# that check it as a PRECONDITION and then correctly call the owner — a tell that flags correct
# callers trains people to widen the exemption list, which is worse than no tell.
_TEMPLATE_RENDERING = "part.format("
_TELLS = (_BINARY_DERIVATION, _TEMPLATE_RENDERING)
# Modules that still resolve a backend command themselves, each with its reason. An entry is a
# DEBT RECORD: removing one is progress, adding one requires justifying it here, and the test
# below asserts every entry still describes something real so the list cannot rot into an
# excuse for nothing.
_KNOWN_UNCONSOLIDATED = {
    # A DIFFERENT adapter key (`release_backend`), and the reason it stays is now MEASURED
    # rather than asserted. The filed reason was "unifying two adapter keys is a contract
    # decision", which turned out to be the wrong blocker: `resolve_op` reads only `binary`,
    # `id` and `commands` and was already adapter-key agnostic, so the keys never needed
    # unifying. The real blocker is where the BINARY lives. `issue_backend` templates exclude
    # it and the owner prepends `backend["binary"]`; `release_backend` templates INCLUDE it and
    # `backend_command` never reads `backend["binary"]` at all. Delegating would hand every
    # existing release adapter its binary twice, on the least reversible surface in this repo.
    # That is executed, not argued, in
    # `tests/quality_gates/test_release_backend_agrees_with_the_owner.py`, which also pins the
    # parts that MUST still agree so the pair cannot drift again silently.
    "skills/public/release/scripts/publish_release_helpers.py",
}


def _code_only(source: str) -> str:
    """Source with whole-line comments dropped.

    A tell that matches prose matches the comment EXPLAINING the tell, which is how this test
    first flagged the very module it exists to certify as delegating.
    """
    return "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))


def _backend_modules() -> dict[str, str]:
    """Every candidate module, per root, with a per-root floor.

    The floor used to be one aggregate count. `scripts/` alone holds hundreds of files, so
    deleting or typo-ing every skill root left the aggregate green — the floor could not detect
    the loss of the roots it existed to protect. Per-root floors can.
    """
    found: dict[str, str] = {}
    for root in _BACKEND_ROOTS:
        root_path = ROOT / root
        assert root_path.is_dir(), f"backend sweep root {root} is gone; re-anchor this test"
        # Recursive: a future `scripts/tracker/backend.py` was invisible to a flat glob.
        paths = sorted(root_path.rglob("*.py"))
        assert len(paths) >= 5, f"backend sweep root {root} collapsed to {len(paths)} modules"
        for path in paths:
            found[str(path.relative_to(ROOT))] = _code_only(path.read_text(encoding="utf-8"))
    return found


def test_no_other_module_re_derives_the_backend_binary_and_template_rule() -> None:
    """The consolidation's guard: a re-grown copy fails here.

    Two tells, both taken from the rule's verdict-bearing half as well as its cheap half. Honest
    about reach: these are substring matches, so a copy spelled with single quotes or split
    across statements evades them. It is a ratchet against the likely regression, not a proof.
    """
    owner_rel = "skills/public/issue/scripts/issue_backend.py"
    owner = _code_only((ROOT / owner_rel).read_text(encoding="utf-8"))
    for tell in _TELLS:
        assert tell in owner, f"the owner no longer contains {tell!r}; re-anchor this test"

    offenders: dict[str, list[str]] = {}
    for relative, source in _backend_modules().items():
        if relative == owner_rel or relative in _KNOWN_UNCONSOLIDATED:
            continue
        hits = [tell for tell in _TELLS if tell in source]
        if hits:
            offenders[relative] = hits
    assert offenders == {}, (
        f"{offenders} resolve a backend command themselves instead of calling "
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
        source = _code_only(path.read_text(encoding="utf-8"))
        assert any(tell in source for tell in _TELLS), (
            f"{relative} no longer matches either tell. If it genuinely delegates to "
            "issue_backend now, drop it from _KNOWN_UNCONSOLIDATED. If it still resolves a "
            "backend command by hand and was only RESPELLED, add the new spelling to _TELLS "
            "instead of deleting a live debt record"
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
    # Per-op required sets, asserted by NAME rather than by the substring `frozenset()`, which
    # matched `LIST_OPEN_REQUIRED` regardless of what `view_state` required — so the assertion
    # could not fail for the choice its own message was about. The behavioural test below is
    # what actually catches a regression here; this keeps the two constants from being merged
    # back into one all-or-nothing value.
    assert 'VIEW_STATE_REQUIRED: frozenset[str] = frozenset({"repo", "number"})' in source, (
        "`view_state` must REQUIRE BOTH halves of an issue's identity. Without `{number}` a "
        "template resolves to a listing whose first row is read as the asked-about issue's "
        "state; without `{repo}` the caller's repository is dropped silently and a "
        "repo-agnostic binary answers about ITS default repo's issue N, which the number "
        "guard cannot see because that issue's number is also N. A host genuinely bound to "
        "one repository declares `repo_scoped: <owner/repo>` instead of omitting the placeholder."
    )
    assert "LIST_OPEN_REQUIRED: frozenset[str] = frozenset()" in source, (
        "`list_open` must require nothing: a host paging internally declares no `{limit}`, and "
        "equating required with the allowlist invalidated templates that were valid before"
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

    A host whose listing pages internally declares no `{limit}`. That was valid before,
    requiring every allowed placeholder would have rejected it, and no fixture in the
    originating slice would have noticed because each one happens to spell every placeholder.

    This test USED to make the same claim about `{repo}` on `view_state`, and that half was a
    defect rather than a protection: an omitted `{repo}` is not a host declaring it has none,
    it is the caller's repository being dropped silently, and the answer can then be a
    different repository's issue with the same number. The identity case moved to
    `test_a_repo_scoped_host_declares_the_waiver_instead_of_omitting_the_placeholder` in
    `tests/test_issue_identity_is_repo_and_number.py`, where the host DECLARES the waiver. The
    non-identity case below is the part that was always right.
    """
    backend = {
        "id": "acme",
        "binary": "acme",
        "commands": {"list_open": ["issue", "list", "--repo", "{repo}"]},
    }

    seen: dict[str, list[str]] = {}

    def runner(argv):
        seen["argv"] = argv
        return [{"number": 7, "title": "t", "labels": [], "body": ""}]

    issues = _load_handoff_backend().list_open_issues(
        "corca-ai/charness", backend=backend, runner=runner
    )

    assert [issue["number"] for issue in issues] == [7]
    assert seen["argv"] == ["acme", "issue", "list", "--repo", "corca-ai/charness"]


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
    handoff._MEMOIZED_ISSUE_MODULES.clear()

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
    handoff._MEMOIZED_ISSUE_MODULES.clear()

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


def test_a_listing_shaped_answer_whose_first_row_is_another_issue_is_not_that_issues_state() -> None:
    """The wrong-verdict path in its most realistic shape, and the changed line that covers it.

    A `view_state` template can resolve to a LISTING rather than a single view, in which case the
    backend returns a list and this module reads its first row. That row is not necessarily the
    issue asked about — it is simply the newest — so reading its state is precisely how a live
    backlog citation becomes a CLOSED verdict. Requiring `{number}` makes the common case
    impossible; this covers the case where a template still yields a list.
    """
    handoff = _load_handoff_backend()

    def listing_runner(argv):
        return [{"number": 999, "state": "CLOSED"}, {"number": 451, "state": "OPEN"}]

    assert handoff.issue_state("o/r", 451, backend=dict(_GH_BACKEND), runner=listing_runner) is None

    def matching_listing_runner(argv):
        return [{"number": 451, "state": "OPEN"}]

    assert handoff.issue_state("o/r", 451, backend=dict(_GH_BACKEND), runner=matching_listing_runner) == "OPEN"

    def empty_listing_runner(argv):
        return []

    assert handoff.issue_state("o/r", 451, backend=dict(_GH_BACKEND), runner=empty_listing_runner) is None

