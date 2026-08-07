"""Complete, provably-enumerated issue source capture.

`gh issue view --comments` is not a capture. It returns whatever one response
carries and reports nothing about whether more exists, so a truncated comment set
and a complete one are byte-identical in every field a caller can inspect. Freezing
an acceptance matrix on top of that means the matrix can be missing a criterion
that is sitting in comment 101 and nothing anywhere will say so.

This module captures through the adapter's declared `issue_source_capture`
capability and refuses anything it cannot prove complete: a page that does not
report whether a next page exists, a final page still claiming `hasNextPage`, a
collected comment set whose size disagrees with the server's `totalCount`,
duplicate node ids, or a requested issue the backend did not return. Refusal is the
feature. A capture that cannot prove completeness is worth less than no capture,
because it looks exactly like one that can.

The receipt records every page's command, args, and raw response digest, so the
freeze validator can re-derive the snapshot from captured evidence rather than
trusting a hand-authored summary of it.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any, Callable

from scripts.closeout_refusal_lib import RefusalError
from scripts.issue_source_normalize_lib import (
    build_clause_inventory,
    build_source_document,
    clause_inventory_identity,
    sha256_payload,
    sha256_text,
)

CAPTURE_TOOL = "scripts/capture_issue_source.py"
CAPTURE_TIMEOUT_SECONDS = 120

GRAPHQL_QUERY = """
query($owner:String!,$name:String!,$number:Int!,$first:Int!,$after:String){
  repository(owner:$owner,name:$name){
    issue(number:$number){
      number title body state url createdAt
      author{login}
      comments(first:$first, after:$after){
        totalCount
        pageInfo{hasNextPage endCursor}
        nodes{id body createdAt author{login}}
      }
    }
  }
}
"""


class CaptureRefusal(RefusalError):
    """A capture that cannot be proven complete. Never downgraded to a warning."""

    @property
    def reason(self) -> str:
        """Lane-local alias for `code`; a capture refusal reads as a *reason*."""
        return self.code


def run_gh(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv, check=False, capture_output=True, text=True, timeout=CAPTURE_TIMEOUT_SECONDS
    )


def build_page_argv(
    backend: dict[str, Any], repo: str, number: int, page_size: int, after: str | None
) -> list[str]:
    """Render one page request.

    A non-`gh` backend must supply `commands.source_capture`; there is no fallback,
    for the same reason the capability itself has none — this repo cannot guess
    another backend's enumeration shape, and guessing wrong produces a capture that
    claims completeness it never checked.
    """
    binary = backend.get("binary") or backend.get("id") or "gh"
    template = (backend.get("commands") or {}).get("source_capture")
    owner, _, name = repo.partition("/")
    if not owner or not name:
        raise CaptureRefusal("invalid_repo", f"repo must be 'owner/name', got {repo!r}")
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise CaptureRefusal(
                "undeclared_capture_command",
                f"issue_backend.id={backend.get('id')} has no commands.source_capture template",
            )
        argv = [
            binary, "api", "graphql",
            "-f", f"query={GRAPHQL_QUERY}",
            "-F", f"owner={owner}", "-F", f"name={name}",
            "-F", f"number={number}", "-F", f"first={page_size}",
        ]
        if after is not None:
            argv.extend(["-F", f"after={after}"])
        return argv
    subs = {
        "repo": repo, "owner": owner, "name": name, "number": str(number),
        "page_size": str(page_size), "after": after or "", "query": GRAPHQL_QUERY,
    }
    return [binary, *(part.format(**subs) if "{" in part else part for part in template)]


def _require(payload: Any, path: str, page_index: int) -> Any:
    node: Any = payload
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            raise CaptureRefusal(
                "unknown_enumeration",
                f"page {page_index} response has no {path!r}; the backend cannot report "
                "whether more source exists, so completeness is unprovable",
            )
        node = node[key]
    return node


def _page_comments(payload: Any, page_index: int, capability: dict[str, Any]) -> dict[str, Any]:
    comments = _require(payload, "data.repository.issue.comments", page_index)
    page_info = _require(payload, "data.repository.issue.comments.pageInfo", page_index)
    has_next_field = capability["has_next_field"]
    cursor_field = capability["cursor_field"]
    total_field = capability["total_count_field"]
    for field in (has_next_field, cursor_field):
        if field not in page_info:
            raise CaptureRefusal(
                "unknown_enumeration",
                f"page {page_index} pageInfo has no {field!r} declared by the capability",
            )
    if total_field not in comments:
        raise CaptureRefusal(
            "unknown_enumeration",
            f"page {page_index} comments has no {total_field!r}; the total is unknown",
        )
    nodes = comments.get("nodes")
    if not isinstance(nodes, list):
        raise CaptureRefusal("unknown_enumeration", f"page {page_index} returned no comment nodes list")
    return {
        "nodes": nodes,
        "has_next": bool(page_info[has_next_field]),
        "cursor": page_info[cursor_field],
        "total_count": comments[total_field],
    }


def capture_issue(
    *,
    repo: str,
    number: int,
    backend: dict[str, Any],
    capability: dict[str, Any],
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] = run_gh,
    max_pages: int = 200,
) -> dict[str, Any]:
    """Enumerate one issue to proven completion, or refuse."""
    if capability.get("enumeration") != "cursor":
        raise CaptureRefusal(
            "unsupported_enumeration",
            f"issue_source_capture.enumeration={capability.get('enumeration')!r} is not "
            "implemented by this capture adapter; only 'cursor' proves completeness here",
        )
    page_size = capability["page_size"]
    pages: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    issue_payload: dict[str, Any] | None = None
    after: str | None = None
    total_count: int | None = None

    for page_index in range(max_pages):
        argv = build_page_argv(backend, repo, number, page_size, after)
        result = runner(argv)
        if result.returncode != 0:
            raise CaptureRefusal(
                "backend_error",
                f"page {page_index} exited {result.returncode}: {(result.stderr or '').strip()!r}",
            )
        raw = result.stdout
        payload = _parse_json(raw, page_index)
        issue = _require(payload, "data.repository.issue", page_index)
        if issue is None:
            raise CaptureRefusal("missing_issue", f"{repo}#{number} was not returned by the backend")
        # The backend's OWN number, not the one we asked for. Without this the returned
        # payload is stamped with the REQUESTED number at the bottom of this function, so a
        # backend that answers #999 to a request for #514 yields a snapshot labelled #514
        # carrying #999's title, body and comments -- and the freeze receipt binds its
        # digest, which is what closeout authorization reads. The escape is concrete rather
        # than theoretical: the query already selects `number`, so the disagreement is
        # observable and was simply discarded.
        returned_number = issue.get("number")
        if returned_number is not None and returned_number != number:
            raise CaptureRefusal(
                "wrong_issue",
                f"asked {repo}#{number}, backend returned #{returned_number}",
            )
        issue_payload = issue
        page = _page_comments(payload, page_index, capability)
        total_count = page["total_count"]
        for node in page["nodes"]:
            node_id = node.get("id")
            if not isinstance(node_id, str) or not node_id:
                raise CaptureRefusal("unidentified_comment", f"page {page_index} node has no id")
            if node_id in seen_ids:
                raise CaptureRefusal(
                    "duplicate_comment",
                    f"comment node {node_id} returned twice; the enumeration is not a partition",
                )
            seen_ids.add(node_id)
            comments.append(
                {
                    "id": node_id,
                    "body": node.get("body") or "",
                    "created_at": node.get("createdAt") or "",
                    "author": ((node.get("author") or {}).get("login")) or "",
                }
            )
        pages.append(
            {
                "page_index": page_index,
                "command": argv[0],
                "args": argv[1:],
                "after": after,
                "returned": len(page["nodes"]),
                "has_next_page": page["has_next"],
                "end_cursor": page["cursor"],
                "total_count": page["total_count"],
                "raw_response_sha256": sha256_text(raw),
                "raw_response": raw,
            }
        )
        if not page["has_next"]:
            break
        if page["cursor"] is None:
            raise CaptureRefusal(
                "unknown_enumeration",
                f"page {page_index} claims a next page but returned no cursor to resume from",
            )
        after = page["cursor"]
    else:
        raise CaptureRefusal(
            "pagination_unterminated",
            f"{repo}#{number} still reported more pages after {max_pages} requests",
        )

    if issue_payload is None or total_count is None:
        raise CaptureRefusal("empty_capture", f"{repo}#{number} produced no page")
    if len(comments) != total_count:
        raise CaptureRefusal(
            "count_mismatch",
            f"{repo}#{number} collected {len(comments)} comments but the backend reports "
            f"totalCount={total_count}",
        )
    return {
        "number": number,
        "title": issue_payload.get("title") or "",
        "state": issue_payload.get("state") or "",
        "url": issue_payload.get("url") or "",
        "body": issue_payload.get("body") or "",
        "comment_total_count": total_count,
        "comments": comments,
        "pages": pages,
        "pagination_complete": True,
    }


def _parse_json(raw: str, page_index: int) -> Any:
    try:
        return json.loads(raw)
    except ValueError as exc:
        raise CaptureRefusal("invalid_json", f"page {page_index} response was not JSON: {exc}") from exc


def capture_issues(
    *,
    repo: str,
    numbers: list[int],
    backend: dict[str, Any],
    capability: dict[str, Any],
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] = run_gh,
) -> list[dict[str, Any]]:
    if not numbers:
        raise CaptureRefusal("empty_request", "no issue numbers were requested")
    if len(set(numbers)) != len(numbers):
        raise CaptureRefusal("duplicate_request", f"issue numbers repeat: {numbers}")
    captured = [
        capture_issue(
            repo=repo, number=number, backend=backend, capability=capability, runner=runner
        )
        for number in sorted(numbers)
    ]
    # No cross-check of `numbers` against the captured numbers here on purpose. The one
    # that used to sit at this spot could not fail: `capture_issue(number=number)` always
    # returns a dict carrying that same `number`, so the difference was always empty. It
    # read as defence in depth and provided none. `capture_issue` owns both real refusals:
    # `missing_issue` when the backend returns no issue, and `wrong_issue` when it returns
    # a DIFFERENT one than was asked for -- the second added here, because the first
    # version of this very comment claimed a backend-answer comparison that did not exist,
    # which is the defect this issue was filed about, re-created in its own fix.
    return captured


def build_snapshot_and_receipt(
    *,
    repo: str,
    numbers: list[int],
    adapter: dict[str, Any],
    capability: dict[str, Any],
    captured: list[dict[str, Any]],
    raw_dir_rel: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    """Fold captured pages into the frozen snapshot plus its capture receipt.

    Returns `(snapshot, receipt, raw_files)`. The raw page bodies leave the receipt
    and land on disk under `raw_dir_rel`, addressed by digest: the receipt asserts
    a digest, the file carries the bytes, and the validator recomputes one from the
    other. A receipt that merely restated the bodies it also summarizes could not
    catch a summary that drifted from them.
    """
    document = build_source_document(repo, captured)
    inventory = build_clause_inventory(document)
    snapshot = {
        "schema": "issue-source-snapshot/v1",
        "repository": repo,
        "requested_numbers": sorted(numbers),
        "capture_tool": CAPTURE_TOOL,
        "adapter": _adapter_identity(adapter, capability),
        "source_document": document,
        "source_snapshot_sha256": inventory["source_snapshot_sha256"],
        "clause_inventory_identity": clause_inventory_identity(inventory),
        "clause_inventory": inventory,
    }
    raw_files: dict[str, str] = {}
    issue_receipts: list[dict[str, Any]] = []
    for issue in captured:
        pages = []
        for page in issue["pages"]:
            rel = f"{raw_dir_rel}/issue-{issue['number']}-page-{page['page_index']}.json"
            raw_files[rel] = page["raw_response"]
            pages.append({key: value for key, value in page.items() if key != "raw_response"} | {"raw_response_path": rel})
        issue_receipts.append(
            {
                "number": issue["number"],
                "comment_total_count": issue["comment_total_count"],
                "captured_comment_count": len(issue["comments"]),
                "comment_node_ids": [comment["id"] for comment in issue["comments"]],
                "body_present": bool(issue["body"]),
                "raw_response_dir": raw_dir_rel,
                "pagination_complete": True,
                "pages": pages,
            }
        )
    receipt = {
        "schema": "issue-source-capture-receipt/v1",
        "repository": repo,
        "requested_numbers": sorted(numbers),
        "capture_tool": CAPTURE_TOOL,
        "adapter": _adapter_identity(adapter, capability),
        "normalization_policy": document["normalization_policy"],
        "source_snapshot_sha256": snapshot["source_snapshot_sha256"],
        "clause_inventory_identity": snapshot["clause_inventory_identity"],
        "issues": issue_receipts,
        "pagination_complete": True,
        "hand_authored": False,
    }
    receipt["receipt_identity"] = sha256_payload(
        {key: value for key, value in receipt.items() if key != "receipt_identity"}
    )
    return snapshot, receipt, raw_files


def _adapter_identity(adapter: dict[str, Any], capability: dict[str, Any]) -> dict[str, Any]:
    data = adapter.get("data", {})
    backend = data.get("issue_backend", {})
    return {
        "adapter_path": adapter.get("path"),
        "adapter_found": adapter.get("found"),
        "backend_id": backend.get("id"),
        "backend_binary": backend.get("binary"),
        "command_template_declared": bool((backend.get("commands") or {}).get("source_capture")),
        "capability": dict(capability),
    }
