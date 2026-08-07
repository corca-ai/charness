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
from pathlib import Path

import pytest

from scripts.capture_issue_source import resolve_adapter_module, run_capture
from scripts.issue_source_capture_lib import (
    CaptureRefusal,
    build_page_argv,
    capture_issue,
    capture_issues,
)
from scripts.issue_source_normalize_lib import (
    build_clause_inventory,
    build_source_document,
    clause_inventory_identity,
    split_clauses,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
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
    return {"id": node_id, "body": body, "createdAt": "2026-01-01T00:00:00Z", "author": {"login": "a"}}


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
            repo="corca-ai/charness", number=514, backend=GH_BACKEND, capability=CAPABILITY,
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
            repo="corca-ai/charness", number=514, backend=GH_BACKEND,
            capability=dict(CAPABILITY, enumeration="page"), runner=_runner([]),
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
        "commands": {"source_capture": ["issues", "read", "{owner}/{name}", "{number}", "--after", "{after}"]},
    }

    argv = build_page_argv(backend, "corca-ai/charness", 518, 50, "CUR")

    assert argv == ["acme", "issues", "read", "corca-ai/charness", "518", "--after", "CUR"]


def test_duplicate_or_empty_issue_number_requests_are_refused() -> None:
    for numbers, reason in (([], "empty_request"), ([514, 514], "duplicate_request")):
        with pytest.raises(CaptureRefusal) as excinfo:
            capture_issues(
                repo="corca-ai/charness", numbers=numbers, backend=GH_BACKEND,
                capability=CAPABILITY, runner=_runner([]),
            )
        assert excinfo.value.reason == reason


def test_resolver_is_loaded_from_the_root_and_installed_plugin_layouts() -> None:
    """The installed copy must resolve its OWN sibling resolver.

    Root layout keeps the resolver under `skills/public/issue/`; the exported plugin
    flattens it to `skills/issue/`. A capture that only knew one layout would either
    fail outright when installed or, worse, reach into a consumer's unrelated
    `skills/` tree and record an adapter identity from somewhere else.
    """
    root_module = resolve_adapter_module(REPO_ROOT)
    assert callable(root_module.load_adapter)

    plugin_root = REPO_ROOT / "plugins" / "charness"
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
        repo_root=tmp_path, repo="corca-ai/charness", numbers=[514], snapshot_path=snapshot,
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
            repo_root=tmp_path, repo="corca-ai/charness", numbers=[514],
            snapshot_path=tmp_path / "source.json", runner=_runner([]),
        )

    assert excinfo.value.reason == "unsupported_capability"
    assert "issue_source_capture" in excinfo.value.detail


def test_clause_ids_move_when_comments_reorder_so_pointers_cannot_be_reassigned() -> None:
    """Reordering must invalidate ids, not silently re-aim them.

    This is the failure the frozen-component derivation exists for: if a clause id
    were positional, swapping two comments would leave every id resolving — to
    different text.
    """
    def inventory(order):
        issues = [
            {
                "number": 1, "title": "t", "state": "OPEN", "body": "body clause",
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
            unit for unit in inv["issues"][0]["source_units"] if unit["source_unit_id"].endswith(unit_suffix)
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
            [{"number": 1, "title": "", "state": "", "body": body, "comment_total_count": 0, "comments": []}],
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
                "number": 1, "title": "", "state": "", "body": "- same words",
                "comment_total_count": 1,
                "comments": [{"id": "c1", "body": "- same words", "created_at": "", "author": ""}],
            }
        ],
    )
    units = build_clause_inventory(document)["issues"][0]["source_units"]

    assert units[0]["clauses"][0]["source_clause_id"] != units[1]["clauses"][0]["source_clause_id"]


def test_fenced_evidence_is_one_clause_so_quoted_bullets_are_not_criteria() -> None:
    clauses = split_clauses("intro line\n\n```\n- not a criterion\n- also not\n```\n\n- a real bullet")

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
            [{"number": 1, "title": "", "state": "", "body": text, "comment_total_count": 0, "comments": []}],
        )
        inventory = build_clause_inventory(document)
        return inventory["issues"][0]["source_units"][0]["clauses"][0]["clause_digest"]

    assert digest("- one long bullet that wraps") == digest("- one long bullet\n  that wraps")
