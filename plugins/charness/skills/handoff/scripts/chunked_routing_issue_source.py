"""#249 issue-backed source for the handoff chunker.

Lets a pickup reason over the live open-issue backlog, not only the
hand-maintained ``## Next Session`` list. Each open issue becomes the same
``HandoffEntry`` shape the parser emits, so ``propose_merges`` clusters
same-surface issues by their shared path-like boundary tokens (e.g. two issues
that both name ``scripts/host_hook_install_lib.py``, or two issues sharing a
specific label like ``mutation-test``).

Boundaries this module keeps:

- **No new hardcoded provider CLI literal.** Provider access reuses the
  ``issue`` skill seam: target resolution + a backend dict whose ``commands``
  can be overridden per host (``gh`` is only the built-in default template,
  exactly as ``issue_runtime`` already does). A non-``gh`` backend must declare
  ``commands.list_open``.
- **Gated behind the handoff adapter.** An optional ``issue_source:`` block in
  the handoff adapter carries enable/limit/repo/label-include/label-exclude/
  exclusions. The block is read directly (the shared simple-adapter loader
  drops unknown keys), so this stays local to the chunker.
- **Trackerless fallback.** Any resolution/listing failure degrades to an empty
  issue-entry list, so the pickup still chunks the handoff doc.
"""
from __future__ import annotations

import importlib.util
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

# Generic labels that must not become merge boundaries — they would cluster
# unrelated issues. Specific labels (e.g. `mutation-test`) still synthesize a
# `label/<slug>` boundary token so same-surface issues group.
GENERIC_LABELS = frozenset(
    {
        "bug",
        "enhancement",
        "feature request",
        "feature-request",
        "documentation",
        "docs",
        "question",
        "good first issue",
        "help wanted",
        "wontfix",
        "duplicate",
        "invalid",
    }
)

def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).resolve().parent / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside chunked_routing_issue_source.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_types = _load_sibling("chunked_routing_types")
_parser = _load_sibling("chunked_routing_parser")
_backend = _load_sibling("chunked_routing_issue_backend")
HandoffEntry = _types.HandoffEntry

# Provider-routing layer lives in chunked_routing_issue_backend (length budget).
# Re-export as module globals so build_issue_entries resolves them at call time
# (and test monkeypatching of these names on this module still takes effect).
DEFAULT_ISSUE_LIMIT = _backend.DEFAULT_ISSUE_LIMIT
GH_LIST_OPEN_ARGS = _backend.GH_LIST_OPEN_ARGS
_load_issue_module = _backend._load_issue_module
list_open_issues = _backend.list_open_issues
LAST_ISSUE_SOURCE_DIAGNOSTIC: dict[str, Any] | None = None


def _label_slug(name: str) -> str:
    return "-".join(name.strip().lower().split())


def _label_names(issue: dict[str, Any]) -> tuple[str, ...]:
    labels = issue.get("labels") or []
    names: list[str] = []
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
        else:
            name = label
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return tuple(names)


def _normalized_paths(text: str) -> tuple[str, ...]:
    link_paths, bare_paths = _parser._collect_paths(text)
    out: list[str] = []
    seen: set[str] = set()
    for token in list(link_paths) + list(bare_paths):
        canonical = _parser._normalize_path(token)
        if canonical not in seen:
            seen.add(canonical)
            out.append(canonical)
    return tuple(out)


def issue_to_handoff_entry(issue: dict[str, Any], index: int) -> HandoffEntry:
    """Convert one open-issue dict into a HandoffEntry.

    boundary_tokens are deliberately PRECISE: path-like tokens from the issue
    **title** plus a synthetic ``label/<slug>`` token for each non-generic
    label. Issue *bodies* cite many incidental paths (a mutation-regression
    body lists mutant paths across many skills, a process issue cites several
    skill dirs); merging on those over-clusters unrelated issues — observed
    directly in the slice-2 live dogfood. The same-surface signal #249 wants
    ("several Slack-rendering bugs") lives in the title and labels. ``referenced_*``
    still capture the full issue for display and slice-3 dedup; only the merge
    boundary is narrowed.
    """
    number = int(issue["number"])
    title = str(issue.get("title", "")).strip()
    body = str(issue.get("body") or "")
    haystack = f"{title}\n{body}"

    # referenced_* — full-issue richness (display + slice-3 dedup key).
    referenced_paths = _normalized_paths(haystack)
    referenced_skills = _parser._collect_skills(referenced_paths)
    body_refs = [n for n in _parser._collect_issues(haystack) if n != number]
    referenced_issues = (number, *body_refs)

    # boundary_tokens — title paths + specific labels only (precision).
    title_paths = _normalized_paths(title)
    title_skills = _parser._collect_skills(title_paths)
    path_tokens = list(_parser._build_boundary_tokens(title_paths, title_skills))
    label_tokens = [
        f"label/{_label_slug(name)}"
        for name in _label_names(issue)
        if name.lower() not in GENERIC_LABELS
    ]
    boundary_tokens: list[str] = []
    for token in path_tokens + label_tokens:
        if token not in boundary_tokens:
            boundary_tokens.append(token)

    return HandoffEntry(
        index=index,
        title=f"#{number}: {title}" if title else f"#{number}",
        body=body.strip(),
        referenced_paths=referenced_paths,
        referenced_issues=referenced_issues,
        referenced_skills=referenced_skills,
        boundary_tokens=tuple(boundary_tokens),
    )


def load_issue_source_config(repo_root: Path) -> dict[str, Any]:
    """Read the handoff adapter's optional ``issue_source:`` block.

    Returns a normalized config. ``enabled`` defaults to True (opt-out) so a
    pickup reasons over the live backlog by default; a host disables it with
    ``issue_source: {enabled: false}`` or simply has no resolvable tracker.
    """
    config = {
        "enabled": True,
        "limit": DEFAULT_ISSUE_LIMIT,
        "repo": None,
        "labels_include": (),
        "labels_exclude": (),
        "exclude_numbers": (),
    }
    try:
        resolve = _load_sibling("resolve_adapter")
        adapter = resolve.load_adapter(repo_root)
        adapter_path = adapter.get("path")
        if not adapter_path:
            return config
        bootstrap_dir = Path(__file__).resolve()
        adapter_lib = None
        for ancestor in bootstrap_dir.parents:
            cand = ancestor / "scripts" / "adapter_lib.py"
            if cand.is_file():
                spec = importlib.util.spec_from_file_location("handoff_adapter_lib", cand)
                adapter_lib = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(adapter_lib)
                break
        if adapter_lib is None:
            return config
        raw = adapter_lib.load_yaml_file(Path(adapter_path))
        block = raw.get("issue_source") if isinstance(raw, dict) else None
        if not isinstance(block, dict):
            return config
    except Exception:
        return config

    if isinstance(block.get("enabled"), bool):
        config["enabled"] = block["enabled"]
    if isinstance(block.get("limit"), int) and block["limit"] > 0:
        config["limit"] = block["limit"]
    if isinstance(block.get("repo"), str) and block["repo"].strip():
        config["repo"] = block["repo"].strip()
    for key in ("labels_include", "labels_exclude"):
        value = block.get(key)
        if isinstance(value, list):
            config[key] = tuple(str(v) for v in value if isinstance(v, str))
    nums = block.get("exclude_numbers")
    if isinstance(nums, list):
        config["exclude_numbers"] = tuple(int(n) for n in nums if isinstance(n, int))
    return config


def _passes_filters(
    issue: dict[str, Any],
    *,
    labels_include: tuple[str, ...],
    labels_exclude: tuple[str, ...],
    exclude_numbers: tuple[int, ...],
) -> bool:
    if int(issue.get("number", 0)) in exclude_numbers:
        return False
    names = {n.lower() for n in _label_names(issue)}
    if labels_include and not (names & {s.lower() for s in labels_include}):
        return False
    if labels_exclude and (names & {s.lower() for s in labels_exclude}):
        return False
    return True


def build_issue_entries(
    repo_root: Path,
    *,
    start_index: int,
    runner: Callable[[list[str]], Any] | None = None,
) -> list[HandoffEntry]:
    """Resolve + list + filter + convert open issues to HandoffEntry records.

    Returns ``[]`` (doc-only fallback) when the issue source is disabled or any
    resolution/listing step fails. Indices start at ``start_index`` so the
    union with handoff entries stays collision-free.
    """
    global LAST_ISSUE_SOURCE_DIAGNOSTIC
    LAST_ISSUE_SOURCE_DIAGNOSTIC = None
    config = load_issue_source_config(repo_root)
    if not config["enabled"]:
        return []
    stage = "load_issue_modules"
    provider_attempted = False
    try:
        issue_resolver = _load_issue_module(repo_root, "resolve_adapter")
        issue_runtime = _load_issue_module(repo_root, "issue_runtime")
        stage = "load_issue_adapter"
        adapter = issue_resolver.load_adapter(repo_root)
        adapter_data = adapter.get("data", {})
        backend = adapter_data.get("issue_backend") or {"id": "gh", "binary": "gh", "commands": None}
        stage = "resolve_target"
        target = issue_runtime.resolve_target(repo_root, config["repo"], adapter_data)
        repo_full = target["full_name"]
        run = runner if runner is not None else issue_runtime._backend_json
        stage = "list_open_issues"
        provider_attempted = True
        issues = list_open_issues(
            repo_full, backend=backend, limit=config["limit"], runner=run
        )
    except Exception as exc:
        LAST_ISSUE_SOURCE_DIAGNOSTIC = {
            "stage": stage,
            "provider_attempted": provider_attempted,
            "type": type(exc).__name__,
            "message": str(exc),
        }
        return []

    entries: list[HandoffEntry] = []
    index = start_index
    for issue in issues:
        if not isinstance(issue, dict) or "number" not in issue:
            continue
        if not _passes_filters(
            issue,
            labels_include=config["labels_include"],
            labels_exclude=config["labels_exclude"],
            exclude_numbers=config["exclude_numbers"],
        ):
            continue
        entries.append(issue_to_handoff_entry(issue, index))
        index += 1
    return entries


def union_entries(
    handoff_entries: list[HandoffEntry],
    issue_entries: list[HandoffEntry],
) -> list[HandoffEntry]:
    """Concatenate handoff and issue entries with collision-free indices.

    Handoff entries keep their parser-assigned indices (stable labels); issue
    entries are re-indexed after the handoff maximum. Pure concat — dedup of an
    issue against a handoff entry that cites it lives in ``dedup_and_union``.
    """
    if not issue_entries:
        return list(handoff_entries)
    next_index = (max((e.index for e in handoff_entries), default=0)) + 1
    reindexed = [
        replace(entry, index=next_index + offset)
        for offset, entry in enumerate(issue_entries)
    ]
    return list(handoff_entries) + reindexed


def dedup_and_union(
    handoff_entries: list[HandoffEntry],
    issue_entries: list[HandoffEntry],
) -> list[HandoffEntry]:
    """Union handoff + issue entries, merging an issue into a handoff entry
    that already cites it (#249 dedup) instead of double-counting.

    A handoff entry that cites ``#X`` and the issue entry whose own number is
    ``X`` are the same work. The issue is merged INTO the citing handoff entry —
    its surface boundary tokens (labels, title paths) enrich the handoff entry
    so the merged entry can still cluster by surface — and the standalone issue
    entry is dropped. Issues no handoff entry cites stay as fresh chunks (the
    backlog the stale ``## Next Session`` omitted).
    """
    # issue_number -> index of the first handoff entry that cites it
    cited_by: dict[int, int] = {}
    for he in handoff_entries:
        for num in he.referenced_issues:
            cited_by.setdefault(num, he.index)

    extra_tokens: dict[int, list[str]] = {}
    consumed: set[int] = set()
    for ie in issue_entries:
        own = ie.referenced_issues[0] if ie.referenced_issues else None
        if own is not None and own in cited_by:
            consumed.add(own)
            extra_tokens.setdefault(cited_by[own], []).extend(ie.boundary_tokens)

    enriched_handoff: list[HandoffEntry] = []
    for he in handoff_entries:
        extra = extra_tokens.get(he.index)
        if extra:
            merged = list(he.boundary_tokens) + [
                t for t in extra if t not in he.boundary_tokens
            ]
            he = replace(he, boundary_tokens=tuple(merged))
        enriched_handoff.append(he)

    remaining = [
        ie for ie in issue_entries
        if (ie.referenced_issues[0] if ie.referenced_issues else None) not in consumed
    ]
    return union_entries(enriched_handoff, remaining)
