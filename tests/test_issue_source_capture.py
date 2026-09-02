"""What the source-capture adapter must refuse.

Every test here is a shape where a naive capture returns a plausible-looking
result that is silently incomplete. That is the whole risk: a capture that dropped
half an issue's comments is indistinguishable, field by field, from one that did
not — unless the adapter checks the enumeration and refuses. The success cases are
short because they are not where the danger lives.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.issue.capture_issue_source import resolve_adapter_module, run_capture
from scripts.issue.issue_source_capture_lib import (
    CaptureRefusal,
    build_page_argv,
    capture_issue,
    capture_issues,
    run_gh,
)
from scripts.issue.issue_source_normalize_lib import (
    build_clause_inventory,
    build_source_document,
    clause_inventory_identity,
    split_clauses,
)
from scripts.plugin_export import packaging_lib
from tests.script_main import load_script_module

REPO_ROOT = Path(__file__).resolve().parent.parent
capture_module = load_script_module(
    "capture_issue_source_under_test",
    REPO_ROOT / "scripts" / "issue" / "capture_issue_source.py",
)
GH_BACKEND = {"id": "gh", "binary": "gh", "commands": None}
CAPABILITY = {
    "enumeration": "cursor",
    "page_size": 2,
    "has_next_field": "hasNextPage",
    "cursor_field": "endCursor",
    "total_count_field": "totalCount",
    "normalization": "github-issue-v1",
    "declared": False,
}


def _export_plugin(tmp_path: Path) -> Path:
    plugin = tmp_path / "plugin"
    manifest = packaging_lib.load_manifest(REPO_ROOT, "charness")
    packaging_lib.export_plugin_tree(REPO_ROOT, plugin, manifest)
    return plugin


def _page(nodes, *, total, has_next, cursor, issue=True):
    payload = {
        "data": {
            "repository": {
                "issue": {
                    "number": 514,
                    "title": "t",
                    "body": "b",
                    "state": "OPEN",
                    "url": "u",
                    "comments": {
                        "totalCount": total,
                        "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
                        "nodes": nodes,
                    },
                }
                if issue
                else None
            }
        }
    }
    return json.dumps(payload)


def _node(node_id: str, body: str = "text"):
    return {
        "id": node_id,
        "body": body,
        "createdAt": "2026-01-01T00:00:00Z",
        "author": {"login": "a"},
    }


def _runner(responses, *, exit_code: int = 0, calls: list | None = None):
    queue = list(responses)

    def run(argv):
        if calls is not None:
            calls.append(argv)
        return subprocess.CompletedProcess(argv, exit_code, queue.pop(0) if queue else "", "boom")

    return run


def _capture(responses, **kwargs):
    return capture_issue(
        repo="corca-ai/charness",
        number=514,
        backend=GH_BACKEND,
        capability=CAPABILITY,
        runner=_runner(responses),
        **kwargs,
    )


def test_cursor_enumeration_collects_every_page_and_marks_completeness() -> None:
    calls: list = []
    result = capture_issue(
        repo="corca-ai/charness",
        number=514,
        backend=GH_BACKEND,
        capability=CAPABILITY,
        runner=_runner(
            [
                _page([_node("c1"), _node("c2")], total=3, has_next=True, cursor="CUR1"),
                _page([_node("c3")], total=3, has_next=False, cursor="CUR2"),
            ],
            calls=calls,
        ),
    )

    assert [comment["id"] for comment in result["comments"]] == ["c1", "c2", "c3"]
    assert result["comment_total_count"] == 3
    assert result["pagination_complete"] is True
    # The second request must resume from the first page's cursor. Without this the
    # loop re-requests page 1 forever or silently returns page 1 twice.
    assert "after=CUR1" in calls[1]
    assert not any(arg.startswith("after=") for arg in calls[0])


def test_page_without_has_next_field_is_refused_as_unknown_enumeration() -> None:
    payload = json.loads(_page([_node("c1")], total=1, has_next=False, cursor=None))
    del payload["data"]["repository"]["issue"]["comments"]["pageInfo"]["hasNextPage"]

    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([json.dumps(payload)])

    assert excinfo.value.reason == "unknown_enumeration"


def test_missing_total_count_is_refused_because_completeness_is_uncheckable() -> None:
    payload = json.loads(_page([_node("c1")], total=1, has_next=False, cursor=None))
    del payload["data"]["repository"]["issue"]["comments"]["totalCount"]

    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([json.dumps(payload)])

    assert excinfo.value.reason == "unknown_enumeration"


def test_collected_count_disagreeing_with_server_total_is_refused() -> None:
    """The single most dangerous shape: a terminated enumeration that is short.

    `hasNextPage` is False, every page parsed, no error anywhere — and one comment
    is missing. Only the totalCount cross-check catches it.
    """
    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([_page([_node("c1")], total=4, has_next=False, cursor=None)])

    assert excinfo.value.reason == "count_mismatch"
    assert "totalCount=4" in excinfo.value.detail


def test_duplicate_comment_node_across_pages_is_refused() -> None:
    with pytest.raises(CaptureRefusal) as excinfo:
        _capture(
            [
                _page([_node("c1")], total=2, has_next=True, cursor="CUR1"),
                _page([_node("c1")], total=2, has_next=False, cursor="CUR2"),
            ]
        )

    assert excinfo.value.reason == "duplicate_comment"


def test_claimed_next_page_without_a_cursor_is_refused() -> None:
    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([_page([_node("c1")], total=2, has_next=True, cursor=None)])

    assert excinfo.value.reason == "unknown_enumeration"


def test_enumeration_that_never_terminates_is_refused_not_truncated() -> None:
    endless = [
        _page([_node(f"c{index}")], total=99, has_next=True, cursor=f"CUR{index}")
        for index in range(10)
    ]

    with pytest.raises(CaptureRefusal) as excinfo:
        _capture(endless, max_pages=3)

    assert excinfo.value.reason == "pagination_unterminated"


def test_absent_issue_is_refused_rather_than_captured_as_empty() -> None:
    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([_page([], total=0, has_next=False, cursor=None, issue=False)])

    assert excinfo.value.reason == "missing_issue"


def test_backend_failure_and_non_json_are_refusals() -> None:
    with pytest.raises(CaptureRefusal) as failure:
        capture_issue(
            repo="corca-ai/charness",
            number=514,
            backend=GH_BACKEND,
            capability=CAPABILITY,
            runner=_runner([""], exit_code=1),
        )
    assert failure.value.reason == "backend_error"

    with pytest.raises(CaptureRefusal) as invalid:
        _capture(["not json"])
    assert invalid.value.reason == "invalid_json"


def test_comment_node_without_an_id_is_refused() -> None:
    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([_page([{"body": "x"}], total=1, has_next=False, cursor=None)])

    assert excinfo.value.reason == "unidentified_comment"


def test_non_cursor_enumeration_is_refused_rather_than_approximated() -> None:
    with pytest.raises(CaptureRefusal) as excinfo:
        capture_issue(
            repo="corca-ai/charness",
            number=514,
            backend=GH_BACKEND,
            capability=dict(CAPABILITY, enumeration="page"),
            runner=_runner([]),
        )

    assert excinfo.value.reason == "unsupported_enumeration"


def test_non_gh_backend_without_a_command_template_cannot_capture() -> None:
    with pytest.raises(CaptureRefusal) as excinfo:
        build_page_argv({"id": "acme", "binary": "acme", "commands": {}}, "o/n", 1, 10, None)

    assert excinfo.value.reason == "undeclared_capture_command"


def test_declared_command_template_is_rendered_with_capture_placeholders() -> None:
    backend = {
        "id": "acme",
        "binary": "acme",
        "commands": {
            "source_capture": ["issues", "read", "{owner}/{name}", "{number}", "--after", "{after}"]
        },
    }

    argv = build_page_argv(backend, "corca-ai/charness", 518, 50, "CUR")

    assert argv == ["acme", "issues", "read", "corca-ai/charness", "518", "--after", "CUR"]


def test_duplicate_or_empty_issue_number_requests_are_refused() -> None:
    for numbers, reason in (([], "empty_request"), ([514, 514], "duplicate_request")):
        with pytest.raises(CaptureRefusal) as excinfo:
            capture_issues(
                repo="corca-ai/charness",
                numbers=numbers,
                backend=GH_BACKEND,
                capability=CAPABILITY,
                runner=_runner([]),
            )
        assert excinfo.value.reason == reason


def test_resolver_is_loaded_from_the_root_and_installed_plugin_layouts(tmp_path: Path) -> None:
    """The installed copy must resolve its OWN sibling resolver.

    Root layout keeps the resolver under `skills/public/issue/`; the exported plugin
    flattens it to `skills/issue/`. A capture that only knew one layout would either
    fail outright when installed or, worse, reach into a consumer's unrelated
    `skills/` tree and record an adapter identity from somewhere else.
    """
    root_module = resolve_adapter_module(REPO_ROOT)
    assert callable(root_module.load_adapter)

    plugin_root = _export_plugin(tmp_path)
    assert (plugin_root / "skills" / "issue" / "scripts" / "resolve_adapter.py").is_file()
    assert callable(resolve_adapter_module(plugin_root).load_adapter)


def test_run_capture_writes_snapshot_receipt_and_digest_addressed_raw_pages(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text("version: 1\n", encoding="utf-8")
    snapshot = tmp_path / "spec" / "source.json"

    payload = run_capture(
        repo_root=tmp_path,
        repo="corca-ai/charness",
        numbers=[514],
        snapshot_path=snapshot,
        runner=_runner([_page([_node("c1")], total=1, has_next=False, cursor=None)]),
    )

    assert payload["ok"] is True
    assert payload["raw_response_dir"] == "spec/source-raw"
    receipt = json.loads((tmp_path / "spec" / "source-capture-receipt.json").read_text())
    assert receipt["hand_authored"] is False
    assert receipt["pagination_complete"] is True
    assert receipt["issues"][0]["comment_node_ids"] == ["c1"]
    raw_rel = receipt["issues"][0]["pages"][0]["raw_response_path"]
    # The receipt asserts a digest and the file carries the bytes; a receipt that
    # merely restated its own summary could not catch the two drifting apart.
    assert (tmp_path / raw_rel).is_file()
    assert "raw_response" not in receipt["issues"][0]["pages"][0]


def test_adapter_identity_records_which_backend_produced_the_capture(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text("version: 1\n", encoding="utf-8")
    snapshot = tmp_path / "source.json"

    run_capture(
        repo_root=tmp_path,
        repo="corca-ai/charness",
        numbers=[514],
        snapshot_path=snapshot,
        runner=_runner([_page([], total=0, has_next=False, cursor=None)]),
    )

    adapter = json.loads(snapshot.read_text())["adapter"]
    assert adapter["backend_id"] == "gh"
    assert adapter["capability"]["normalization"] == "github-issue-v1"


def test_a_backend_that_cannot_declare_its_enumeration_refuses_only_capture(tmp_path: Path) -> None:
    """The refusal is scoped to the operation that needs the guarantee.

    A non-`gh` backend with no declared `issue_source_capture` must not be able to
    produce a snapshot whose completeness nobody checked — but the adapter stays
    VALID, so `read`/`close`/`verify` keep working for consumers who never capture.
    Widening this to an adapter-level error broke four unrelated close/verify tests,
    which is precisely the blast radius the scoping avoids.
    """
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text(
        "issue_backend:\n  id: acme\n  binary: acme\n", encoding="utf-8"
    )
    adapter = resolve_adapter_module(REPO_ROOT).load_adapter(tmp_path)
    assert adapter["valid"] is True
    assert adapter["data"]["issue_source_capture"]["supported"] is False

    with pytest.raises(CaptureRefusal) as excinfo:
        run_capture(
            repo_root=tmp_path,
            repo="corca-ai/charness",
            numbers=[514],
            snapshot_path=tmp_path / "source.json",
            runner=_runner([]),
        )

    assert excinfo.value.reason == "unsupported_capability"
    assert "issue_source_capture" in excinfo.value.detail


def _adapter_repo(tmp_path: Path, body: str = "version: 1\n") -> Path:
    (tmp_path / ".agents").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text(body, encoding="utf-8")
    return tmp_path


def test_a_tree_with_no_resolver_refuses_instead_of_capturing_with_an_unknown_adapter(
    tmp_path: Path,
) -> None:
    """No resolver means no provable adapter identity, so there is nothing to record.

    Capturing anyway would write a snapshot whose `adapter` block was invented here
    rather than resolved by the issue lane, and every criterion id later derived from
    it would inherit that fiction.
    """
    with pytest.raises(CaptureRefusal) as excinfo:
        resolve_adapter_module(tmp_path)

    assert excinfo.value.reason == "resolver_missing"
    assert str(tmp_path) in excinfo.value.detail


def test_an_invalid_adapter_refuses_before_any_backend_request(tmp_path: Path) -> None:
    """A malformed adapter is refused, not silently replaced by the inferred defaults.

    `load_adapter` still returns a usable `data` block when it reports errors. Reading
    that block anyway would capture against defaults the operator never chose while the
    receipt recorded the adapter file as its authority.
    """
    repo_root = _adapter_repo(tmp_path, "version: not-an-integer\n")

    with pytest.raises(CaptureRefusal) as excinfo:
        run_capture(
            repo_root=repo_root,
            repo="corca-ai/charness",
            numbers=[514],
            snapshot_path=repo_root / "source.json",
            runner=_runner([]),
        )

    assert excinfo.value.reason == "invalid_adapter"
    assert "version must be an integer" in excinfo.value.detail
    assert not (repo_root / "source.json").exists()


def test_a_resolver_that_reports_no_capture_capability_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The capability block is required, not optional-with-a-fallback.

    This repo's own resolver always populates it, so the guard only fires against an
    older or foreign installed `resolve_adapter.py` — exactly the case where guessing a
    default enumeration would let a stale resolver produce a snapshot claiming a
    completeness contract it never had. Stubbed here because that is the only way to
    present a resolver that omits the block.
    """
    stub = SimpleNamespace(
        load_adapter=lambda repo_root: {
            "valid": True,
            "errors": [],
            "path": None,
            "found": True,
            "data": {"issue_backend": GH_BACKEND},
        }
    )
    monkeypatch.setattr(capture_module, "resolve_adapter_module", lambda *_, **__: stub)

    with pytest.raises(CaptureRefusal) as excinfo:
        capture_module.run_capture(
            repo_root=tmp_path,
            repo="corca-ai/charness",
            numbers=[514],
            snapshot_path=tmp_path / "source.json",
            runner=_runner([]),
        )

    assert excinfo.value.reason == "missing_capability"
    assert "issue_source_capture" in excinfo.value.detail


def _run_main(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> int:
    """Drive the CLI entrypoint in-process through the canonical script loader."""
    monkeypatch.setattr(sys, "argv", ["capture_issue_source.py", *argv])
    return capture_module.main()


def test_cli_resolves_a_relative_snapshot_against_the_repo_root_it_was_given(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--snapshot` is relative to `--repo-root`, never to the process cwd.

    Joining against cwd would write the frozen snapshot outside the repo whose adapter
    authorized the capture, and the receipt's `snapshot_path` — computed relative to the
    repo root — would then name a file that is not there.
    """
    repo_root = _adapter_repo(tmp_path)
    # The CLI resolves its runner from ITS module's `run_gh`, so that is the object
    # to control; patching the lib left the real `gh` in place (#779).
    monkeypatch.setattr(
        capture_module,
        "run_gh",
        _runner([_page([_node("c1")], total=1, has_next=False, cursor=None)]),
    )

    code = _run_main(
        [
            "--repo-root",
            str(repo_root),
            "--repo",
            "corca-ai/charness",
            "--numbers",
            "514",
            "--snapshot",
            "spec/source.json",
        ],
        monkeypatch,
    )

    assert code == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["snapshot_path"] == "spec/source.json"
    assert payload["per_issue"] == [
        {"number": 514, "comment_total_count": 1, "captured_comment_count": 1, "pages": 1}
    ]
    assert (repo_root / "spec" / "source.json").is_file()
    assert (repo_root / "spec" / "source-capture-receipt.json").is_file()


def test_cli_renders_a_refusal_as_nonzero_json_and_writes_no_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A refused capture must exit nonzero and leave nothing behind.

    A refusal that still wrote a partial snapshot, or that exited 0 with the refusal
    only on stderr, is how an unprovable capture gets frozen by the next step in a
    script that checked the exit code.
    """
    repo_root = _adapter_repo(tmp_path, "issue_backend:\n  id: acme\n  binary: acme\n")

    code = _run_main(
        [
            "--repo-root",
            str(repo_root),
            "--repo",
            "corca-ai/charness",
            "--numbers",
            "514",
            "515",
            "--snapshot",
            str(repo_root / "spec" / "source.json"),
        ],
        monkeypatch,
    )

    assert code == 1
    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert payload["ok"] is False
    assert payload["refusal"] == "unsupported_capability"
    assert "capture_issue_source: REFUSED (unsupported_capability)" in captured.err
    assert not (repo_root / "spec").exists()


@pytest.mark.boundary_contract(
    reason="prove the issue backend runner preserves a child process exit and text output"
)
def test_run_gh_reports_the_exit_code_and_output_instead_of_raising() -> None:
    """The default runner must hand a failing backend call back as data.

    Every completeness refusal in this lane branches on `returncode`/`stdout`; a runner
    that raised on a nonzero exit would turn a backend error into a traceback, which
    `run_cli` deliberately does not render as a refusal.
    """
    ok = run_gh([sys.executable, "-c", "print('hello')"])
    assert ok.returncode == 0
    assert ok.stdout == "hello\n"

    failed = run_gh([sys.executable, "-c", "import sys; sys.stderr.write('nope'); sys.exit(3)"])
    assert failed.returncode == 3
    assert failed.stderr == "nope"


def test_a_repo_that_is_not_owner_slash_name_is_refused_before_any_request() -> None:
    """`owner`/`name` are separate GraphQL variables, so a bare name has no query.

    Without this the partition yields an empty owner and the request is sent anyway,
    coming back as an absent issue — a refusal that blames the backend for the caller's
    malformed argument.
    """
    for repo in ("charness", "", "corca-ai/"):
        with pytest.raises(CaptureRefusal) as excinfo:
            build_page_argv(GH_BACKEND, repo, 514, 10, None)
        assert excinfo.value.reason == "invalid_repo"
        assert repr(repo) in excinfo.value.detail


def test_a_response_missing_the_issue_path_entirely_is_refused() -> None:
    """A backend answering with an unrelated shape cannot be read as "no comments".

    `{"data": {}}` has no `repository`, so nothing in it reports whether more source
    exists; treating the absent path as empty would capture a zero-comment issue and
    call it complete.
    """
    with pytest.raises(CaptureRefusal) as excinfo:
        _capture(['{"data": {}}'])

    assert excinfo.value.reason == "unknown_enumeration"
    assert "data.repository.issue" in excinfo.value.detail


def test_a_comments_block_whose_nodes_are_not_a_list_is_refused() -> None:
    """`nodes: null` is not an empty page.

    Iterating it would raise, and defaulting it to `[]` would silently collect nothing
    from a page the backend said existed — which the totalCount cross-check only catches
    when the total happens to disagree.
    """
    payload = json.loads(_page([], total=0, has_next=False, cursor=None))
    payload["data"]["repository"]["issue"]["comments"]["nodes"] = None

    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([json.dumps(payload)])

    assert excinfo.value.reason == "unknown_enumeration"
    assert "comment nodes list" in excinfo.value.detail


def test_a_null_total_count_is_refused_rather_than_compared_against() -> None:
    """`totalCount: null` is present but unknown, and unknown fails no cross-check.

    The field-presence check passes, so without this guard the capture reaches the
    count comparison with `None`, where `0 != None` would refuse for the wrong reason
    and any nonzero page would crash instead of refusing.
    """
    payload = json.loads(_page([], total=0, has_next=False, cursor=None))
    payload["data"]["repository"]["issue"]["comments"]["totalCount"] = None

    with pytest.raises(CaptureRefusal) as excinfo:
        _capture([json.dumps(payload)])

    assert excinfo.value.reason == "empty_capture"
    assert "corca-ai/charness#514" in excinfo.value.detail


def test_a_declared_capability_is_parsed_field_by_field_and_warns_without_a_command(
    tmp_path: Path,
) -> None:
    """A non-`gh` backend that names its enumeration keeps the adapter valid.

    Every field is asserted individually because a parser that dropped one would fall
    back to the `gh` default and capture against a contract the backend never declared.
    The missing `commands.source_capture` is a warning, not an error: the declaration is
    well-formed, and it is `capture_issue_source.py` that refuses when the template is
    needed.
    """
    repo_root = _adapter_repo(
        tmp_path,
        "issue_backend:\n  id: acme\n  binary: acme\n"
        "issue_source_capture:\n"
        "  enumeration: page\n"
        "  page_size: 25\n"
        "  has_next_field: more\n"
        "  cursor_field: next\n"
        "  total_count_field: total\n"
        "  normalization: github-issue-v1\n",
    )

    adapter = resolve_adapter_module(REPO_ROOT).load_adapter(repo_root)

    assert adapter["valid"] is True
    assert adapter["data"]["issue_source_capture"] == {
        "enumeration": "page",
        "page_size": 25,
        "has_next_field": "more",
        "cursor_field": "next",
        "total_count_field": "total",
        "normalization": "github-issue-v1",
        "declared": True,
        "supported": True,
        "unsupported_reason": None,
    }
    assert any(
        "declared issue_source_capture without commands.source_capture" in warning
        for warning in adapter["warnings"]
    )


def test_a_backend_that_declares_both_the_capability_and_its_command_is_not_warned(
    tmp_path: Path,
) -> None:
    """The warning must name a real gap, not fire on every non-`gh` backend.

    A warning that cannot be silenced by fixing exactly what it describes gets tuned
    out, and with it the one that says the capture will refuse.
    """
    repo_root = _adapter_repo(
        tmp_path,
        "issue_backend:\n  id: acme\n  binary: acme\n"
        "  commands:\n    source_capture:\n      - issues\n      - read\n"
        "issue_source_capture:\n  page_size: 10\n",
    )

    adapter = resolve_adapter_module(REPO_ROOT).load_adapter(repo_root)

    assert adapter["valid"] is True
    assert adapter["data"]["issue_source_capture"]["page_size"] == 10
    assert adapter["data"]["issue_source_capture"]["declared"] is True
    assert not any("commands.source_capture" in warning for warning in adapter["warnings"])


def test_every_malformed_capability_field_is_reported_and_the_default_is_kept(
    tmp_path: Path,
) -> None:
    """One bad field must not be rounded off to the built-in `gh` contract silently.

    Each error names its field so the operator repairs the declaration; the adapter is
    invalid, so `capture_issue_source.py` refuses rather than capturing against a
    contract that was half-understood. `page_size: true` is included because `True` is
    an `int` in Python and would otherwise parse as page size 1.

    Rejected values fall back to the default EXCEPT `normalization`, which is a plain
    string field and is kept as written before the policy check reports it. That is only
    safe because `valid` is False: the errors are the gate, not the returned block.
    """
    repo_root = _adapter_repo(
        tmp_path,
        "issue_source_capture:\n"
        "  enumeration: firehose\n"
        "  page_size: true\n"
        "  has_next_field: ''\n"
        "  normalization: bespoke-v9\n",
    )

    adapter = resolve_adapter_module(REPO_ROOT).load_adapter(repo_root)

    assert adapter["valid"] is False
    assert adapter["errors"] == [
        "issue_source_capture.enumeration must be one of: cursor, page",
        "issue_source_capture.page_size must be a positive integer",
        "issue_source_capture.has_next_field must be a non-empty string",
        "issue_source_capture.normalization must be one of: github-issue-v1",
    ]
    capability = adapter["data"]["issue_source_capture"]
    assert capability["enumeration"] == "cursor"
    assert capability["page_size"] == 100
    assert capability["has_next_field"] == "hasNextPage"
    assert capability["normalization"] == "bespoke-v9"


def test_a_zero_page_size_and_a_non_mapping_capability_are_both_refused(tmp_path: Path) -> None:
    """A scalar `issue_source_capture:` is a declaration nobody can read.

    It must land as an adapter error rather than being ignored as absent: ignored, a
    `gh` backend would silently serve the built-in default and the operator's attempted
    override would vanish without a word.
    """
    scalar_root = _adapter_repo(tmp_path / "scalar", "issue_source_capture: yes-please\n")
    adapter = resolve_adapter_module(REPO_ROOT).load_adapter(scalar_root)

    assert adapter["valid"] is False
    assert adapter["errors"] == ["issue_source_capture must be a mapping"]
    # The returned block is the untouched default, marked undeclared -- so nothing
    # downstream can read the unparsable scalar as a declared contract.
    assert adapter["data"]["issue_source_capture"]["declared"] is False
    assert adapter["data"]["issue_source_capture"]["page_size"] == 100

    zero_root = _adapter_repo(tmp_path / "zero", "issue_source_capture:\n  page_size: 0\n")
    zero = resolve_adapter_module(REPO_ROOT).load_adapter(zero_root)

    assert zero["errors"] == ["issue_source_capture.page_size must be a positive integer"]


def test_clause_ids_move_when_comments_reorder_so_pointers_cannot_be_reassigned() -> None:
    """Reordering must invalidate ids, not silently re-aim them.

    This is the failure the frozen-component derivation exists for: if a clause id
    were positional, swapping two comments would leave every id resolving — to
    different text.
    """

    def inventory(order):
        issues = [
            {
                "number": 1,
                "title": "t",
                "state": "OPEN",
                "body": "body clause",
                "comment_total_count": 2,
                "comments": [
                    {"id": node, "body": f"clause from {node}", "created_at": "", "author": ""}
                    for node in order
                ],
            }
        ]
        return build_clause_inventory(build_source_document("o/n", issues))

    forward = inventory(["c1", "c2"])
    reversed_order = inventory(["c2", "c1"])

    assert clause_inventory_identity(forward) != clause_inventory_identity(reversed_order)
    assert forward["source_snapshot_sha256"] != reversed_order["source_snapshot_sha256"]
    # Same content, same clause id is NOT the guarantee: the snapshot digest is a
    # frozen component, so every id in a re-captured changed source is different.
    assert clause_inventory_identity(forward) == clause_inventory_identity(inventory(["c1", "c2"]))

    # Assert on the INDIVIDUAL ids, not only the aggregate identity. The aggregate
    # differs under reordering even for a purely positional `unit|ordinal` scheme,
    # because the unit list itself reorders — so the aggregate assertion alone would
    # still pass if the derivation were gutted. `c1`'s clause sits at ordinal 0 of its
    # own unit in both orders; only a derivation that folds in content can tell them
    # apart from `c2`'s.
    def clause_id(inv, unit_suffix):
        unit = next(
            unit
            for unit in inv["issues"][0]["source_units"]
            if unit["source_unit_id"].endswith(unit_suffix)
        )
        return unit["clauses"][0]["source_clause_id"]

    assert clause_id(forward, "c1") != clause_id(forward, "c2")


def test_editing_one_clause_changes_its_id_at_a_fixed_unit_and_ordinal() -> None:
    """The derivation must be content-sensitive, not positional.

    Unit and ordinal are held constant and only the text changes. A positional scheme
    would return the same id for both and this is the assertion that catches it.
    """

    def first_clause_id(body: str) -> str:
        document = build_source_document(
            "o/n",
            [
                {
                    "number": 1,
                    "title": "",
                    "state": "",
                    "body": body,
                    "comment_total_count": 0,
                    "comments": [],
                }
            ],
        )
        inventory = build_clause_inventory(document)
        return inventory["issues"][0]["source_units"][0]["clauses"][0]["source_clause_id"]

    assert first_clause_id("- the original criterion") != first_clause_id("- the edited criterion")


def test_identical_text_in_two_different_units_gets_different_ids() -> None:
    """A criterion pointer must name WHICH occurrence it means."""
    document = build_source_document(
        "o/n",
        [
            {
                "number": 1,
                "title": "",
                "state": "",
                "body": "- same words",
                "comment_total_count": 1,
                "comments": [{"id": "c1", "body": "- same words", "created_at": "", "author": ""}],
            }
        ],
    )
    units = build_clause_inventory(document)["issues"][0]["source_units"]

    assert units[0]["clauses"][0]["source_clause_id"] != units[1]["clauses"][0]["source_clause_id"]


def test_fenced_evidence_is_one_clause_so_quoted_bullets_are_not_criteria() -> None:
    clauses = split_clauses(
        "intro line\n\n```\n- not a criterion\n- also not\n```\n\n- a real bullet"
    )

    assert len(clauses) == 3
    assert clauses[1].startswith("```")
    assert "- not a criterion" in clauses[1]
    assert clauses[2] == "- a real bullet"


def test_wrapped_bullets_and_headings_split_the_way_criteria_are_written() -> None:
    clauses = split_clauses("## Head\n- first bullet\n  wrapped continuation\n- second bullet")

    assert clauses[0] == "## Head"
    assert clauses[1] == "- first bullet\n  wrapped continuation"
    assert clauses[2] == "- second bullet"


def test_a_blockquoted_fence_is_still_one_clause_of_evidence() -> None:
    """Issue bodies routinely quote a prior comment wholesale.

    The original fence pattern only matched at ≤3 leading spaces with no quote marker,
    so quoted evidence parsed as ordinary markdown and its `- ` lines became criteria.
    """
    clauses = split_clauses("> ```\n> - quoted log line\n> ```\n\n- a real criterion")

    assert len(clauses) == 2
    assert "- quoted log line" in clauses[0]
    assert clauses[1] == "- a real criterion"


def test_a_deeply_nested_bullet_gets_its_own_clause() -> None:
    """An under-split bullet can never carry a disposition, so it never fails anything.

    The original 7-space indent ceiling folded 8+-space bullets into their parent; a
    later repair briefly made it worse by treating any 4+-space line as indented code,
    which ate 4-7-space bullets too.
    """
    clauses = split_clauses("- top level\n    - nested once\n        - nested twice")

    assert clauses == ["- top level", "- nested once", "- nested twice"]


def test_a_line_initial_inline_code_span_does_not_open_a_fence() -> None:
    """CommonMark: a backtick fence's info string may not contain a backtick.

    Without that rule this line reads as a fence opener and swallows every following
    bullet into one clause — hiding criteria that GitHub renders as ordinary bullets.
    """
    clauses = split_clauses("```make test``` fails\n\n- a real criterion")

    assert clauses[-1] == "- a real criterion"
    assert len(clauses) == 2


def test_an_unterminated_fence_runs_to_the_end_and_does_not_raise() -> None:
    """Matching GitHub beats second-guessing it.

    Those bullets ARE inside a code block for every human reading the issue, so they are
    not criteria. An earlier revision raised instead, which made a stray fence in someone
    else's comment a hard failure of this repo's capture.
    """
    clauses = split_clauses("intro paragraph\n\n```\n- inside the block\n- also inside")

    assert clauses[0] == "intro paragraph"
    assert len(clauses) == 2
    assert "- inside the block" in clauses[1]


def test_rewrapping_a_bullet_does_not_change_its_clause_digest() -> None:
    """Whitespace-insensitive digests keep a criterion mapping alive across a rewrap.

    If every reflow invalidated the inventory, operators would re-freeze reflexively
    and the staleness check would stop meaning anything.
    """

    def digest(text: str) -> str:
        document = build_source_document(
            "o/n",
            [
                {
                    "number": 1,
                    "title": "",
                    "state": "",
                    "body": text,
                    "comment_total_count": 0,
                    "comments": [],
                }
            ],
        )
        inventory = build_clause_inventory(document)
        return inventory["issues"][0]["source_units"][0]["clauses"][0]["clause_digest"]

    assert digest("- one long bullet that wraps") == digest("- one long bullet\n  that wraps")


def test_a_backend_that_returns_a_different_issue_is_refused(tmp_path: Path) -> None:
    """The escape: the payload is stamped with the REQUESTED number, not the returned one.

    Without this refusal a backend answering #999 to a request for #514 produces a
    snapshot labelled #514 carrying #999's title, body and comments — and the freeze
    receipt binds its digest, which is what closeout authorization reads. The query
    already selects `number`, so the disagreement was observable and simply discarded.

    Found by the delegated resolution critique of the fix for the unreachable
    `missing_issue` guard: the comment left behind claimed this comparison existed.
    """
    payload = json.dumps(
        {
            "data": {
                "repository": {
                    "issue": {
                        "number": 999,
                        "title": "other",
                        "body": "- a criterion",
                        "state": "OPEN",
                        "url": "u",
                        "comments": {
                            "totalCount": 0,
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                            "nodes": [],
                        },
                    }
                }
            }
        }
    )
    with pytest.raises(CaptureRefusal) as excinfo:
        capture_issue(
            repo="corca-ai/charness",
            number=514,
            backend={"id": "gh", "binary": "gh", "commands": None},
            capability=CAPABILITY,
            runner=lambda argv: subprocess.CompletedProcess(argv, 0, payload, ""),
        )
    assert excinfo.value.code == "wrong_issue"
    assert "514" in str(excinfo.value) and "999" in str(excinfo.value)
