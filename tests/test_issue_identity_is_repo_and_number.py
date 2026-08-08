"""`(repo, number)` names an issue; half of it names a different repo's issue with the same number.

A `view_state` adapter template that omits `{repo}` was ACCEPTED, and the caller's repo was then
dropped without comment: `resolve_op` validates that every placeholder the template uses is
allowed and that every required one is used, but never that a substitution the caller SUPPLIED
was consumed. Against a host binary whose default repository differs from the one being asked
about, the answer is about that binary's issue N — and the existing number guard cannot see it,
because the wrong repository's issue N also has number N. The observed result is a live backlog
citation reported CLOSED with `issue_states_checked: true`, which is the manufactured stale
verdict the staleness reader exists to refuse.

These tests prove the closure BY CONSTRUCTION rather than by a passing suite: each one builds an
input that produced the wrong verdict and asserts it is now refused. Two layers are proven
separately, because they fail independently:

1. the TEMPLATE layer — `{repo}` is required, and a repo-scoped host declares a waiver instead
   of omitting it silently;
2. the ANSWER layer — a backend that is TOLD the repo and ignores it is caught by checking the
   repository the payload says it describes.

Layer 2 exists because layer 1 cannot see a disobedient binary, and layer 1 exists because
layer 2 is silent whenever a payload names no repository at all.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "corca-ai/charness"
OTHER = "someone-else/charness"


def _module(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BACKEND = _module("skills/public/handoff/scripts/chunked_routing_issue_backend.py", "crib_identity")
OWNER = _module("skills/public/issue/scripts/issue_backend.py", "owner_identity")
RESOLVE = _module("skills/public/issue/scripts/resolve_adapter.py", "resolve_adapter_identity")


def parsed_backend(**adapter_block):
    """A backend dict built the way the RUNTIME builds one: through the adapter parser.

    Round 1 caught every waiver test here hand-building this dict, which meant they proved the
    waiver against a shape no caller ever receives. `_parse_backend` returns a fixed key set,
    so a key it does not parse is a key the runtime never sees no matter what the YAML says --
    and the first version of this slice added `repo_scoped` to the reader and not to the
    parser, leaving the escape hatch inert and repo-scoped hosts hard-broken with no
    configuration able to restore them. A test that skips the parser cannot fail for that.
    """
    errors: list[str] = []
    warnings: list[str] = []
    backend = RESOLVE._parse_backend(adapter_block, errors, warnings)
    return backend, errors, warnings


def _runner(payload: dict):
    """A backend that answers with `payload` regardless of what it was asked."""

    def run(argv: list[str]) -> dict:
        run.argv = argv
        return json.loads(json.dumps(payload))

    run.argv = []
    return run


def test_a_view_state_template_that_omits_repo_is_refused_not_silently_accepted() -> None:
    """The reported defect, constructed: it used to return CLOSED for a live citation."""
    backend = {"id": "acme", "binary": "acme", "commands": {"view_state": ["view", "{number}"]}}
    runner = _runner({"number": 558, "state": "CLOSED"})

    assert BACKEND.issue_state(REPO, 558, backend=backend, runner=runner) is None
    # UNKNOWN is not enough on its own: the module's whole diagnostic contract is that a broken
    # template and an unreachable tracker must not read identically. Before this repair the
    # diagnostic stayed None, which is the worst of both — a wrong answer with no signal.
    diagnostic = BACKEND.LAST_STATE_RESOLUTION_DIAGNOSTIC
    assert diagnostic is not None
    assert "repo" in diagnostic and "missing required placeholders" in diagnostic
    # And it never reached the backend at all, so no wrong answer was even available to report.
    assert runner.argv == []


def test_a_repo_scoped_host_declares_the_waiver_instead_of_omitting_the_placeholder() -> None:
    """The reason `{repo}` was optional was real, so the waiver has to keep working.

    This is the half that makes the requirement affordable: a binary genuinely bound to one
    repository still resolves, but now because its adapter SAYS SO, not because the omission
    was read as consent. Declared, defaulted and absent are three states.
    """
    backend, errors, _ = parsed_backend(
        id="acme", binary="acme", repo_scoped=REPO, commands={"view_state": ["view", "{number}"]}
    )
    assert errors == []
    assert backend["repo_scoped"] == REPO, "the parser dropped the key; the waiver is inert"
    runner = _runner({"number": 558, "state": "OPEN"})

    assert BACKEND.issue_state(REPO, 558, backend=backend, runner=runner) == "OPEN"
    assert runner.argv == ["acme", "view", "558"]

    # And the declaration covers ONE repository. This skill routes to two targets, so a waiver
    # that applied to every repo would drop the identity for the target the binary is not
    # bound to -- the defect returning through the escape hatch built to make the fix
    # affordable.
    other = _runner({"number": 558, "state": "OPEN"})
    assert BACKEND.issue_state(OTHER, 558, backend=backend, runner=other) is None
    assert "repo" in (BACKEND.LAST_STATE_RESOLUTION_DIAGNOSTIC or "")
    assert other.argv == []


def test_the_waiver_does_not_extend_to_the_number() -> None:
    """`repo_scoped` waives the repository only. No binary carries the issue number implicitly.

    Without this, the waiver would be a way to re-open the defect a prior round closed: a
    `view_state` template omitting `{number}` resolves to a listing, whose first row is then
    read as the asked-about issue's state.
    """
    backend, errors, _ = parsed_backend(
        id="acme", binary="acme", repo_scoped=REPO, commands={"view_state": ["list"]}
    )
    assert errors == []
    runner = _runner({"number": 1, "state": "CLOSED"})

    assert BACKEND.issue_state(REPO, 558, backend=backend, runner=runner) is None
    assert "number" in (BACKEND.LAST_STATE_RESOLUTION_DIAGNOSTIC or "")


def test_a_backend_that_ignores_the_repo_it_was_given_is_caught_by_the_answer() -> None:
    """Layer 2, constructed. The template is CORRECT here; the binary disobeys it.

    No template rule can catch this, which is why the answer is checked too — and why the gh
    default requests `url`: without a repo-bearing field the payload never names a repository
    and this guard would be a check that can never fire on the path most installs take.
    """
    backend = {
        "id": "acme",
        "binary": "acme",
        "commands": {"view_state": ["view", "{number}", "--repo", "{repo}"]},
    }
    payload = {
        "number": 558,
        "state": "CLOSED",
        "url": f"https://github.com/{OTHER}/issues/558",
    }

    assert BACKEND.issue_state(REPO, 558, backend=backend, runner=_runner(payload)) is None
    # Same payload, same number, same state — asked about the repo it actually answered for.
    assert BACKEND.issue_state(OTHER, 558, backend=backend, runner=_runner(payload)) == "CLOSED"


def test_a_payload_that_names_no_repository_is_unknown_silence_not_a_mismatch() -> None:
    """Silence must not read as a wrong answer, or every repo-scoped host becomes UNKNOWN.

    This is the boundary the guard's usefulness depends on, and it is asserted rather than
    assumed: `answer_repo` returning None means "the payload does not say", which is a
    different fact from "the payload says something else".
    """
    backend, errors, _ = parsed_backend(
        id="acme", binary="acme", repo_scoped=REPO, commands={"view_state": ["view", "{number}"]}
    )
    assert errors == []
    runner = _runner({"number": 558, "state": "CLOSED"})

    assert BACKEND.issue_state(REPO, 558, backend=backend, runner=runner) == "CLOSED"
    assert OWNER.answer_repo({"number": 558, "state": "CLOSED"}) is None


def test_the_gh_default_requests_a_field_that_names_the_answers_repository() -> None:
    """Without this the answer-layer guard is inert on the default path.

    Pinned as a PAIRING rather than as a substring: the field list must carry a key
    `answer_repo` can actually read. `gh` has no `repository` JSON field — it exits with
    `Unknown JSON field` — so `url` is the only one available, and dropping it would silently
    disarm layer 2 while every other assertion here stayed green.
    """
    args = BACKEND.GH_VIEW_STATE_ARGS
    assert "{repo}" in args, "the default template must spell the repo it is asked about"
    assert "{number}" in args
    fields = args[args.index("--json") + 1].split(",")
    assert "url" in fields, f"no repo-bearing field in the default view_state payload: {fields}"
    # And the field it names must genuinely resolve through the owner's parse.
    sample = {field: "" for field in fields}
    sample["url"] = f"https://github.com/{REPO}/issues/1"
    assert OWNER.answer_repo(sample) == REPO


def test_one_identity_rule_has_one_owner() -> None:
    """The handoff reader and the closeout verifier must not answer this differently again.

    The premise check found the two callers of one identity rule disagreeing — handoff required
    `{number}` alone while the closeout verifier already required both halves. That is the
    duplicate-rule shape this backend was consolidated to remove, so the parse has ONE home and
    both consumers reach it from there.
    """
    assert BACKEND.VIEW_STATE_REQUIRED == frozenset({"repo", "number"})
    # handoff does not implement the parse; it delegates to the owner.
    assert BACKEND.answer_repo({"url": f"https://github.com/{REPO}/issues/9"}) == REPO
    handoff_source = (
        ROOT / "skills/public/handoff/scripts/chunked_routing_issue_backend.py"
    ).read_text(encoding="utf-8")
    assert "_issue_backend_owner().answer_repo" in handoff_source, (
        "handoff grew its own copy of the identity parse again"
    )
    verifier_source = (
        ROOT / "skills/public/issue/scripts/issue_verify_closeout.py"
    ).read_text(encoding="utf-8")
    # NOT `'"repository"' in source`: that literal already existed in an unrelated
    # authorization record, so the assertion could not fail for the reason its message gave.
    assert "_ANSWER_REPO(state_payload)" in verifier_source, (
        "the closeout verifier stopped reading the repository its payload reports"
    )
    assert 'field="repository"' in verifier_source, (
        "the closeout verifier stopped RECORDING a repository mismatch"
    )


def test_answer_repo_reads_both_payload_shapes_and_a_self_hosted_url() -> None:
    """Host-mediated backends emit a repository object; gh emits only a URL.

    The URL parse is POSITIONAL from the end (`.../owner/repo/issues/N`) rather than anchored on
    `github.com`, because an enterprise or self-hosted host is the case where a wrong-repo answer
    is most likely and least visible.
    """
    assert OWNER.answer_repo({"repository": {"nameWithOwner": REPO}}) == REPO
    assert OWNER.answer_repo({"repository": {"owner": {"login": "corca-ai"}, "name": "charness"}}) == REPO
    assert OWNER.answer_repo({"repository": REPO}) == REPO
    assert OWNER.answer_repo({"url": f"https://ghe.example.com/{REPO}/issues/558"}) == REPO
    assert OWNER.answer_repo({"url": f"https://github.com/{REPO}/pull/558"}) == REPO
    # Not an issue URL, and not guessed at.
    assert OWNER.answer_repo({"url": "https://example.com/thing"}) is None
    assert OWNER.answer_repo({"url": ""}) is None


def test_the_waiver_must_name_a_repository_rather_than_being_a_bare_true() -> None:
    """A bare `true` cannot answer "scoped to WHICH repository", so it is refused at parse time.

    The `issue` skill routes to two targets — an upstream harness repo and the local one — so an
    unqualified waiver would drop the identity for whichever target the binary is not bound to.
    That is the reported defect returning through the escape hatch built to make the fix
    affordable, and it would be invisible in any single-repo test.
    """
    # WARN and ignore, not invalidate: this adapter's own norm is that a consumer-authored
    # mistake warns rather than refusing, and ignoring is the FAIL-CLOSED direction anyway --
    # no scope declared means no waiver means `{repo}` stays required. What must NOT happen is
    # the bare `true` being honoured.
    bare, errors, warnings = parsed_backend(id="acme", binary="acme", repo_scoped=True)
    assert errors == [], errors
    assert bare["repo_scoped"] is None, "a bare `true` was honoured as a waiver"
    assert any("which repository" in message for message in warnings), warnings

    half, _, half_warnings = parsed_backend(id="acme", binary="acme", repo_scoped="charness")
    assert half["repo_scoped"] is None
    assert any("owner/repo" in message for message in half_warnings), half_warnings

    # A nested namespace IS a repository path; refusing it would leave that host class unable
    # to declare its scope at all.
    nested, ok, _ = parsed_backend(id="acme", binary="acme", repo_scoped="group/sub/project")
    assert ok == [] and nested["repo_scoped"] == "group/sub/project"

    backend, ok, _ = parsed_backend(id="acme", binary="acme", repo_scoped=REPO)
    assert ok == [] and backend["repo_scoped"] == REPO


def test_the_default_backend_declares_no_scope_so_the_waiver_is_off_unless_asked_for() -> None:
    """Absent is a state, and it must not read as waived."""
    assert RESOLVE.default_backend()["repo_scoped"] is None
    backend, errors, _ = parsed_backend(id="acme", binary="acme", commands={"view_state": ["view"]})
    assert errors == [] and backend["repo_scoped"] is None


def test_the_irreversible_boundary_does_not_opt_into_the_waiver() -> None:
    """A staleness reader may waive the repo; a closeout verifier may not.

    The waiver was first subtracted GLOBALLY inside the owner, which silently loosened the
    closeout verifier — a surface that had required both halves absolutely — in order to fix a
    reader. A bounded round caught it. The waiver is now opt-in per call site, so the default
    is the strict behaviour every existing caller already had.
    """
    backend, errors, _ = parsed_backend(
        id="acme",
        binary="acme",
        repo_scoped=REPO,
        commands={"view": ["view", "{number}", "--json", "{json_fields}"]},
    )
    assert errors == [] and backend["repo_scoped"] == REPO
    close = _module("skills/public/issue/scripts/issue_close.py", "issue_close_identity")

    # No `waivable` argument: the declaration is present and must NOT be honoured here.
    try:
        close._resolve_op(
            backend,
            "view",
            close.GH_VIEW_DEFAULT,
            close.VIEW_PLACEHOLDERS,
            required=frozenset({"repo", "number"}),
            repo=REPO,
            number="1",
            json_fields="number,state,url",
        )
    except RuntimeError as exc:
        # The SPECIFIC refusal, not any error mentioning "repo": the unknown-placeholder
        # message renders the allowlist, which contains `repo`, so a looser match would pass
        # for a completely different reason.
        assert "missing required placeholders" in str(exc) and "repo" in str(exc), exc
    else:  # pragma: no cover - the assertion below reports the failure
        raise AssertionError("the closeout path honoured a waiver it never opted into")

    # And the reader DOES opt in, so the two differ by the call site rather than by the backend.
    assert BACKEND.VIEW_STATE_WAIVABLE == frozenset({"repo"})


def test_answer_repo_returns_silence_rather_than_a_wrong_repository() -> None:
    """Wrong is worse than silent here, because silence is accepted and a wrong value REFUSES.

    A first version matched the last four path segments positionally, which turns
    `/orgs/foo/projects/1/issues/2` into `projects/1` — a value that would refuse a correct
    closeout. The path is now required to be exactly `<owner>/<repo>/issues/<number>` after the
    host, and a `repository` string with no owner is half an identity rather than an answer.
    """
    assert OWNER.answer_repo({"url": "https://github.com/orgs/foo/projects/1/issues/2"}) is None
    assert OWNER.answer_repo({"repository": "charness"}) is None
    assert OWNER.answer_repo({"url": "https://github.com/corca-ai/charness/issues"}) is None
    # Still resolves the shapes that genuinely name a repository, including query and fragment.
    assert OWNER.answer_repo({"url": f"https://github.com/{REPO}/issues/558?x=1#note"}) == REPO
    assert OWNER.answer_repo({"url": f"https://ghe.example.com/{REPO}/issues/558/"}) == REPO


def test_a_half_identity_is_silence_in_every_payload_shape_not_just_the_string_one() -> None:
    """Round 2's blocker: the owner-shape rule was applied to one branch and not the other.

    `{"repository": "charness"}` was correctly refused, while
    `{"repository": {"nameWithOwner": "charness"}}` still returned a bare `charness` — which
    compares unequal to `corca-ai/charness` and REFUSES a correct verdict. Wrong is worse than
    silent here, and the shape that carried it is the one a host-mediated backend most
    naturally emits. Every branch now goes through the same rule.
    """
    assert OWNER.answer_repo({"repository": {"nameWithOwner": "charness"}}) is None
    assert OWNER.answer_repo({"repository": {"full_name": "charness"}}) is None
    assert OWNER.answer_repo({"repository": "charness"}) is None
    # A slash inside a half makes a slug that names nothing; each half must be one segment.
    assert OWNER.answer_repo({"repository": {"owner": {"login": "a/b"}, "name": "c"}}) is None
    # And the qualified forms all still resolve.
    assert OWNER.answer_repo({"repository": {"nameWithOwner": REPO}}) == REPO
    assert OWNER.answer_repo({"repository": {"owner": {"login": "corca-ai"}, "name": "charness"}}) == REPO
    assert OWNER.answer_repo({"url": f"https://api.github.com/repos/{REPO}/issues/1"}) == REPO


def test_the_post_close_readback_owes_the_same_identity_floor_as_the_verifier() -> None:
    """Round 2's other blocker: the CLOSE path's own readback required nothing.

    `close_with_comment` runs its own post-close `view` to prove the mutation landed — it is
    the evidence that an irreversible boundary was crossed correctly — and it passed no
    `required` set at all, so a `view` template spelling only `{number}` was accepted. It also
    already fetched `url` and never read it. Both halves are checked now.
    """
    source = (ROOT / "skills/public/issue/scripts/issue_close.py").read_text(encoding="utf-8")
    assert 'required=frozenset({"repo", "number"})' in source, (
        "the post-close readback stopped requiring both halves of the issue's identity"
    )
    assert "answer_repo(verified_state)" in source, (
        "the post-close readback stopped checking the repository it read back"
    )
    # No waiver is offered on this path: `waivable` must not be threaded into the close-side
    # resolve, or a repo-scoped declaration would loosen the irreversible boundary.
    close_calls = source.count("waivable")
    assert close_calls == 0, "the close path opted into the repo-scope waiver"


def test_the_waiver_fails_closed_when_no_repo_was_supplied_to_compare_against() -> None:
    """A waiver that cannot compare is a waiver that cannot say which repository it covers.

    The first version skipped the comparison whenever `repo` was absent from the substitutions,
    which waived unconditionally — the defect the named value was introduced to remove,
    reachable by any future caller that opts in without passing a repo.
    """
    backend = {"id": "acme", "binary": "acme", "repo_scoped": REPO, "commands": None}
    assert OWNER._scope_waived(backend, {}, waivable=frozenset({"repo"})) == frozenset()
    assert OWNER._scope_waived(backend, {"repo": ""}, waivable=frozenset({"repo"})) == frozenset()
    assert OWNER._scope_waived(backend, {"repo": OTHER}, waivable=frozenset({"repo"})) == frozenset()
    assert OWNER._scope_waived(
        backend, {"repo": REPO}, waivable=frozenset({"repo"})
    ) == frozenset({"repo"})
    # And an opt-out call site is never waived, whatever the backend declares.
    assert OWNER._scope_waived(backend, {"repo": REPO}, waivable=frozenset()) == frozenset()
