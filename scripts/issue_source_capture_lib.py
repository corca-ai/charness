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
from pathlib import Path
from typing import Any, Callable

from runtime_bootstrap import import_repo_module
from scripts.closeout_refusal_lib import RefusalError
from scripts.issue_source_normalize_lib import (
    build_clause_inventory,
    build_source_document,
    clause_inventory_identity,
    sha256_payload,
    sha256_text,
)

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

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


def capture_subs(
    repo: str, owner: str, name: str, number: int, page_size: int, after: str | None
) -> dict[str, str]:
    """Every substitution this lane offers a `source_capture` template.

    ONE declaration, because the allowlist below is derived from it. A separate hand-written
    allowlist would be two statements of one set: a missing entry silently REFUSES a template
    that was valid before, an extra one re-opens the hole the allowlist closes, and neither is
    visible from either site alone.
    """
    return {
        "repo": repo,
        "owner": owner,
        "name": name,
        "number": str(number),
        "page_size": str(page_size),
        "after": after or "",
        "query": GRAPHQL_QUERY,
    }


# The owner refuses a template naming anything outside this set, and refuses a caller passing
# anything outside it -- the validation this copy of the rule never had, and the reason a host
# declaring an unknown placeholder used to get a raw `KeyError` out of `format` inside a lane
# whose refusals are otherwise typed.
SOURCE_CAPTURE_PLACEHOLDERS: frozenset[str] = frozenset(capture_subs("", "", "", 0, 0, None))
# The identity-bearing placeholders the owner can require directly. `{number}` is flat, so it
# lives here.
SOURCE_CAPTURE_REQUIRED: frozenset[str] = frozenset({"number"})
# The repository half is an OR — `{repo}`, or the `{owner}` + `{name}` pair — because both
# spellings genuinely name it and this lane offers both. The owner's `required` is a flat set
# and cannot express that, so it is checked here, where the vocabulary lives, rather than by
# widening a proof surface to carry one caller's disjunction.
SOURCE_CAPTURE_REPO_IDENTITY: tuple[frozenset[str], ...] = (
    frozenset({"repo"}),
    frozenset({"owner", "name"}),
)

_ISSUE_BACKEND_OWNER: Any = None


def _issue_backend_owner():
    """The `issue` skill's backend owner, loaded once, in BOTH layouts.

    Repo-owned `scripts/` reading a public skill package is a cross-skill READ, which is
    allowed; only file mutation across skills is gated. Memoized because `build_page_argv`
    runs once per page inside a timed capture lane.

    BOTH layouts, and that is not defensive padding. This module is exported to
    `plugins/charness/scripts/`, where the sibling skills sit at `skills/issue/...` rather than
    `skills/public/issue/...`. A first version knew only the source tree, and the failure was
    worse than a missing feature: `spec_from_file_location` returns a spec WITH a loader for a
    path that does not exist, so the shape guard below cannot fire and `exec_module` raises
    `FileNotFoundError` — an untyped exception escaping a lane whose entire contract is typed
    `CaptureRefusal` codes. It also fires before the built-in GraphQL default returns, so every
    installed capture would have died, not only templated ones. This repo already owns the
    two-layout pattern in `commit_msg_closeout_authorization`; this is that pattern,
    not a third rule.
    """
    global _ISSUE_BACKEND_OWNER
    if _ISSUE_BACKEND_OWNER is None:
        import importlib.util
        from pathlib import Path as _Path

        package_root = _Path(__file__).resolve().parent.parent
        candidates = [
            package_root / "skills/public/issue/scripts/issue_backend.py",
            package_root / "skills/issue/scripts/issue_backend.py",
        ]
        source = next((c for c in candidates if c.is_file()), None)
        if source is None:
            raise CaptureRefusal(
                "issue_backend_owner_missing",
                f"cannot load the tracker backend owner; looked in {[str(c) for c in candidates]}",
            )
        spec = importlib.util.spec_from_file_location("_capture_issue_backend", source)
        if spec is None or spec.loader is None:  # pragma: no cover - import machinery guard
            raise CaptureRefusal(
                "issue_backend_owner_missing",
                f"cannot build an import spec for the tracker backend owner at {source}",
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _ISSUE_BACKEND_OWNER = module
    return _ISSUE_BACKEND_OWNER


class CaptureRefusal(RefusalError):
    """A capture that cannot be proven complete. Never downgraded to a warning."""

    @property
    def reason(self) -> str:
        """Lane-local alias for `code`; a capture refusal reads as a *reason*."""
        return self.code


def run_gh(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return run_process(
        argv,
        cwd=Path.cwd(),
        timeout_seconds=CAPTURE_TIMEOUT_SECONDS,
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
    # The binary rule comes from the owner too. Only the built-in GraphQL default below is
    # local, because it is not a template; deriving the binary for it was the cheapest half of
    # the rule and the half a re-grown copy reaches for first.
    try:
        binary = _issue_backend_owner().backend_binary(backend)
    except CaptureRefusal:
        # The loader's own refusal is already typed and already correct. Re-wrapping it as
        # `invalid_capture_command` would send an operator to `.agents/issue-adapter.yaml` for
        # what is a broken or partial INSTALL — `CaptureRefusal` subclasses `RuntimeError`, so
        # the broad `except` below silently swallowed the code this repair added.
        raise
    except RuntimeError as exc:
        raise CaptureRefusal("invalid_capture_command", str(exc)) from exc
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
            binary,
            "api",
            "graphql",
            "-f",
            f"query={GRAPHQL_QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={number}",
            "-F",
            f"first={page_size}",
        ]
        if after is not None:
            argv.extend(["-F", f"after={after}"])
        return argv
    # The TEMPLATE branch is the owner's rule and delegates to it. Only the built-in default
    # above stays local, because it is not a template at all -- it is a conditionally assembled
    # GraphQL invocation (`after` is appended only when a cursor exists), which the owner's
    # render-a-template contract genuinely cannot express. The issue that filed this copy
    # concluded from that one branch that the whole function could not be consolidated; the
    # branch that needs the owner's placeholder ALLOWLIST is exactly the branch that fits it.
    #
    # The refusal TYPE stays local too. This capture lane's refusals are typed
    # (`CaptureRefusal` with a reason code) and its callers read those codes, so the owner's
    # `RuntimeError` is translated rather than allowed to escape -- the same
    # mechanical-part/policy split the tracker-backend consolidation already established.
    # A template that names the repository in NEITHER spelling drops it silently: the owner
    # renders only what the template spells, so a repo-agnostic binary then enumerates ITS
    # default repo's issue N. The wrong-issue guard downstream cannot catch that, because the
    # other repository's issue N also has number N. This capture feeds the freeze receipt that
    # closeout authorization reads, so it is the same severity class as the tracker's own state
    # lookup, and the same rule: `(repo, number)` is the identity.
    spelled = {
        match for part in template for match in _issue_backend_owner().PLACEHOLDER_RE.findall(part)
    }
    if not any(required <= spelled for required in SOURCE_CAPTURE_REPO_IDENTITY):
        raise CaptureRefusal(
            "invalid_capture_command",
            f"source_capture template {template!r} names no repository: spell `{{repo}}`, or "
            "`{owner}` and `{name}` together. Without it the caller's repository is dropped "
            "and the backend answers about whichever repository it defaults to.",
        )
    subs = capture_subs(repo, owner, name, number, page_size, after)
    try:
        return _issue_backend_owner().resolve_op(
            backend,
            "source_capture",
            [],
            SOURCE_CAPTURE_PLACEHOLDERS,
            SOURCE_CAPTURE_REQUIRED,
            frozenset(),
            "issue_backend",
            **subs,
        )
    except CaptureRefusal:
        raise
    except RuntimeError as exc:
        raise CaptureRefusal("invalid_capture_command", str(exc)) from exc
    except (KeyError, ValueError, IndexError) as exc:
        # `PLACEHOLDER_RE` matches only `{lower_snake}`, so a part carrying `{"q":1}`, `{0}` or
        # `{Q}` clears the allowlist and then raises inside `str.format`. A `source_capture`
        # template is GraphQL/JSON-shaped by nature, so brace-bearing parts are the EXPECTED
        # case here rather than the exotic one, and an untyped escape from this lane is the
        # exact defect this consolidation was filed to remove.
        raise CaptureRefusal(
            "invalid_capture_command",
            f"source_capture template {template!r} could not be rendered with "
            f"{sorted(subs)!r}: {type(exc).__name__}: {exc}. A literal brace that is not a "
            "placeholder must be doubled (`{{`/`}}`).",
        ) from exc


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
        raise CaptureRefusal(
            "unknown_enumeration", f"page {page_index} returned no comment nodes list"
        )
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
            raise CaptureRefusal(
                "missing_issue", f"{repo}#{number} was not returned by the backend"
            )
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
        raise CaptureRefusal(
            "invalid_json", f"page {page_index} response was not JSON: {exc}"
        ) from exc


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
            pages.append(
                {key: value for key, value in page.items() if key != "raw_response"}
                | {"raw_response_path": rel}
            )
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
