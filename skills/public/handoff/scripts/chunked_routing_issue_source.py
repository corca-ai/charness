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

# gh default for listing open issues. Mirrors issue_runtime.GH_NEWEST_OPEN_ARGS:
# the only built-in provider literal; non-gh backends declare commands.list_open.
GH_LIST_OPEN_ARGS = [
    "issue", "list", "--repo", "{repo}", "--state", "open",
    "--limit", "{limit}", "--json", "number,title,labels,body",
]

DEFAULT_ISSUE_LIMIT = 50


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
HandoffEntry = _types.HandoffEntry


def _load_issue_module(repo_root: Path, name: str):
    """Import a module from the ``issue`` skill's scripts dir (route reuse).

    Walks up to ``skills/public/issue/scripts/<name>.py``. Read/import across
    skills is allowed (the same pattern draft_goal_from_chunk uses to import
    the achieve goal-artifact lib); only file *mutation* across skills is gated.
    """
    here = Path(__file__).resolve()
    roots = [repo_root, *here.parents]
    for ancestor in roots:
        candidate = ancestor / "skills" / "public" / "issue" / "scripts" / f"{name}.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(f"issue_{name}", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"skills/public/issue/scripts/{name}.py not found")


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


def list_open_issues(
    repo: str,
    *,
    backend: dict[str, Any] | None = None,
    limit: int = DEFAULT_ISSUE_LIMIT,
    runner: Callable[[list[str]], Any] | None = None,
) -> list[dict[str, Any]]:
    """List open issues for ``repo`` via the resolved backend.

    ``runner`` (argv -> parsed JSON) defaults to issue_runtime._backend_json;
    tests inject a stub so no live provider call is made.
    """
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    binary = backend.get("binary") or backend.get("id") or "gh"
    commands = backend.get("commands") or {}
    template = commands.get("list_open")
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise RuntimeError(
                f"issue_backend.id={backend.get('id')} did not declare "
                "commands.list_open; configure the adapter for this host."
            )
        template = GH_LIST_OPEN_ARGS
    argv = [binary] + [
        part.replace("{repo}", repo).replace("{limit}", str(limit))
        for part in template
    ]
    if runner is None:
        issue_runtime = _load_issue_module(Path.cwd(), "issue_runtime")
        runner = issue_runtime._backend_json
    payload = runner(argv)
    if isinstance(payload, dict) and "issues" in payload:
        payload = payload.get("issues")
    return list(payload) if isinstance(payload, list) else []


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
    config = load_issue_source_config(repo_root)
    if not config["enabled"]:
        return []
    try:
        issue_resolver = _load_issue_module(repo_root, "resolve_adapter")
        issue_runtime = _load_issue_module(repo_root, "issue_runtime")
        adapter = issue_resolver.load_adapter(repo_root)
        adapter_data = adapter.get("data", {})
        backend = adapter_data.get("issue_backend") or {"id": "gh", "binary": "gh", "commands": None}
        target = issue_runtime.resolve_target(repo_root, config["repo"], adapter_data)
        repo_full = target["full_name"]
        run = runner if runner is not None else issue_runtime._backend_json
        issues = list_open_issues(
            repo_full, backend=backend, limit=config["limit"], runner=run
        )
    except Exception:
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
    entries are re-indexed after the handoff maximum. Dedup of an issue against
    a handoff entry that already cites it is slice 3, not here.
    """
    if not issue_entries:
        return list(handoff_entries)
    next_index = (max((e.index for e in handoff_entries), default=0)) + 1
    reindexed: list[HandoffEntry] = []
    for offset, entry in enumerate(issue_entries):
        reindexed.append(
            HandoffEntry(
                index=next_index + offset,
                title=entry.title,
                body=entry.body,
                referenced_paths=entry.referenced_paths,
                referenced_issues=entry.referenced_issues,
                referenced_skills=entry.referenced_skills,
                boundary_tokens=entry.boundary_tokens,
            )
        )
    return list(handoff_entries) + reindexed
