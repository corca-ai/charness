#!/usr/bin/env python3
"""Re-verify an open backlog: render a typed premise state per issue, then stop.

Answers "is this issue still true?" in one command instead of a reading session. It emits
evidence and a typed state; it never closes an issue and never recommends closing one.
The verdict logic lives in `recount_premise_lib`; this file is the tracker seam and the
report envelope.

ONE TRACKER OWNER, NOT A THIRD. The `issue` skill owns backend resolution and op
rendering. This module calls `issue_backend.resolve_op` with its own `list_open` /
`view_issue` defaults, which buys that owner's placeholder validation. It deliberately does
NOT import `handoff`'s listing helper: that helper is gated behind the handoff adapter's
optional `issue_source:` block, so a host disabling handoff's pickup listing would silently
disable this re-verification too, and a floor another skill's adapter can switch off is not
a floor. Reading across skills is allowed; the direction matters, and `issue` is a leaf
that imports neither `achieve` nor `handoff`, so this stays acyclic.

WHY THE CALLER SUPPLIES THE PREMISE JUDGEMENT. See `recount_premise_lib`'s module
docstring. In short: whether an issue still describes the tree is not decidable from prose
from prose, so the machine renders only what it can STRUCTURALLY read -- typed
`Premise-residue:` markers in durable records, and unchecked `- [ ]` items in the issue
body -- and refuses to invent the rest. Run with no `--premise-file` to get the evidence
sweep; supply one to type the states.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_MODULES: dict[str, Any] = {}


def _load_first(cache_key: str, candidates: tuple[Path, ...], missing: str):
    """Exec the first candidate path that exists, memoized.

    ONE loader for both the sibling module and the cross-skill `issue` module, rather than
    the two near-identical copies this file first carried. The repo's duplicate ratchet
    named that pair immediately, and it was right: the only thing that differed between
    them was the candidate list, which is now the argument.

    Memoized because the CLI resolves the backend once per issue when bodies are fetched,
    and re-exec'ing a module per issue inside a timeout-armed command is the cost a sibling
    helper already had to go back and fix.
    """
    if cache_key in _MODULES:
        return _MODULES[cache_key]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(cache_key, candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[cache_key] = module
        return module
    raise ImportError(missing)


def sibling(module_name: str):
    """A module beside this file: `recount_premise_lib` (verdicts) or `recount_residue_lib`.

    One accessor rather than one wrapper per module -- the two wrappers this file briefly
    carried differed only in a string, and the duplicate ratchet named them immediately.
    """
    here = Path(__file__).resolve().parent
    return _load_first(
        module_name,
        (here / f"{module_name}.py",),
        f"{module_name}.py not found beside recount_premise_state.py",
    )


def lib():
    """The verdict logic. Kept as a named accessor because it is called from three sites."""
    return sibling("recount_premise_lib")


def load_issue_module(repo_root: Path, name: str):
    """Import from the `issue` skill's scripts dir (route reuse, established in this repo).

    Both layouts are tried because the source tree nests skills under `public/` and the
    export flattens it, and this file runs in both.
    """
    here = Path(__file__).resolve()
    return _load_first(
        f"issue_owner_{name}",
        (
            repo_root / "skills" / "public" / "issue" / "scripts" / f"{name}.py",
            repo_root / "skills" / "issue" / "scripts" / f"{name}.py",
            here.parents[2] / "issue" / "scripts" / f"{name}.py",
            here.parents[3] / "public" / "issue" / "scripts" / f"{name}.py",
        ),
        f"issue skill script {name}.py not found in source-tree skills/public/issue/scripts "
        "or installed skills/issue/scripts layout",
    )


DEFAULT_BACKEND = {"id": "gh", "binary": "gh", "commands": None}

# `{repo}` is NOT required on the listing op. `gh` scoped to a repo checkout resolves the
# repository itself, and demanding the placeholder would refuse a working default. That is
# the opposite of the search op, where a missing scope silently answers about another
# repository -- a benign omission versus a wrong answer.
GH_LIST_OPEN_ARGS = [
    "issue", "list", "--state", "open", "--limit", "{limit}",
    "--json", "number,title,url,state",
]
LIST_OPEN_PLACEHOLDERS = frozenset({"repo", "limit"})

GH_VIEW_ISSUE_ARGS = ["issue", "view", "{number}", "--json", "number,title,body,state,url"]
VIEW_ISSUE_PLACEHOLDERS = frozenset({"repo", "number"})


def backend_json(repo_root: Path, argv: list[str]) -> Any:
    """Run a backend argv through the `issue` skill's own runner and parse its JSON.

    Deliberately `issue_backend.run_backend` rather than a local `subprocess.run` block:
    that owner already fixes the timeout, refuses a shell, and captures text, and a private
    copy here would be the second implementation of the thing this slice exists to avoid
    multiplying. Only the JSON parsing and the error shape are this file's.
    """
    result = load_issue_module(repo_root, "issue_backend").run_backend(argv)
    if result.returncode != 0:
        raise RuntimeError(
            (result.stderr or "").strip() or (result.stdout or "").strip() or f"{argv[0]} failed"
        )
    return json.loads(result.stdout or "null")


def list_open_issues(
    repo_root: Path, *, repo: str | None, limit: int, backend: dict | None = None, runner=None
) -> list[dict]:
    resolve_op = load_issue_module(repo_root, "issue_backend").resolve_op
    argv = resolve_op(
        backend or DEFAULT_BACKEND,
        "list_open",
        GH_LIST_OPEN_ARGS,
        LIST_OPEN_PLACEHOLDERS,
        adapter_key="issue_backend",
        repo=repo or "",
        limit=str(limit),
    )
    payload = runner(argv) if runner else backend_json(repo_root, argv)
    if not isinstance(payload, list):
        raise RuntimeError("issue list did not return a list")
    return [item for item in payload if isinstance(item, dict) and "number" in item]


def view_issue(
    repo_root: Path, number: int, *, repo: str | None, backend: dict | None = None, runner=None
) -> dict:
    resolve_op = load_issue_module(repo_root, "issue_backend").resolve_op
    argv = resolve_op(
        backend or DEFAULT_BACKEND,
        "view_issue",
        GH_VIEW_ISSUE_ARGS,
        VIEW_ISSUE_PLACEHOLDERS,
        adapter_key="issue_backend",
        repo=repo or "",
        number=str(number),
    )
    payload = runner(argv) if runner else backend_json(repo_root, argv)
    return payload if isinstance(payload, dict) else {}


def load_premise_verdicts(path: Path | None) -> dict[int, dict]:
    """Caller-supplied premise judgements: `{"554": {"verdict": "refuted", "evidence": "..."}}`.

    A plain string value is accepted as the verdict, so a caller with nothing to say beyond
    the judgement is not forced into an object. An unrecognised verdict is NOT an error and
    NOT silently coerced: it flows into `classify`, which renders `unverifiable-by-machine`.
    Rejecting the file would push a caller toward removing the entry, which records less.
    """
    if path is None:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError("--premise-file must hold a JSON object keyed by issue number")
    verdicts: dict[int, dict] = {}
    for key, value in raw.items():
        try:
            number = int(str(key).lstrip("#"))
        except ValueError:
            continue
        if isinstance(value, str):
            entry = {"verdict": value}
        elif isinstance(value, dict):
            entry = dict(value)
        else:
            # A list or number here is a malformed entry, not a judgement. Round 1 found
            # `dict(value)` raising TypeError straight past `main`'s handler as a traceback.
            # Degrading to an empty entry renders `unverifiable-by-machine`, which is the
            # honest reading of "the caller wrote something that says nothing".
            entry = {}
        verdicts[number] = entry
    return verdicts


def evaluate_issue(
    repo_root: Path,
    issue: dict,
    *,
    verdicts: dict[int, dict],
    exclude: tuple[Path, ...],
    body: str | None,
) -> dict:
    module = lib()
    number = int(issue["number"])
    entry = verdicts.get(number) or {}
    caller_verdict = entry.get("verdict")
    residue = sibling("recount_residue_lib").scan_residue(repo_root, number, exclude=exclude)
    open_tasks = module.body_open_task_items(body or "")
    # `body_read` is threaded into the verdict, not merely reported. Round 1 found the
    # reporting-only version let `classify` read an unread body as "no further ask" while
    # the reason string asserted the body was clear -- a protection described in a comment
    # and absent from the verdict.
    verdict = module.classify(
        caller_verdict=caller_verdict,
        residue=residue,
        open_tasks=open_tasks,
        body_read=body is not None,
    )
    return {
        "number": number,
        "title": issue.get("title"),
        "url": issue.get("url"),
        "state": verdict["state"],
        "reason": verdict["reason"],
        "caller_verdict": caller_verdict,
        "caller_evidence": entry.get("evidence"),
        "residue_declining": residue["declining"],
        "residue_provenance": residue["provenance"],
        "body_open_tasks": open_tasks,
        "body_read": body is not None,
    }


def build_report(
    repo_root: Path,
    *,
    repo: str | None,
    limit: int,
    premise_file: Path | None,
    exclude: tuple[Path, ...],
    with_bodies: bool,
    backend: dict | None = None,
    runner=None,
) -> dict:
    verdicts = load_premise_verdicts(premise_file)
    issues = list_open_issues(repo_root, repo=repo, limit=limit, backend=backend, runner=runner)
    results = []
    for issue in issues:
        body = None
        if with_bodies:
            try:
                payload = view_issue(
                    repo_root, int(issue["number"]), repo=repo, backend=backend, runner=runner
                )
                # `.get("body") or ""` was the F4 defect one layer up: `view_issue` already
                # degrades a non-dict payload to `{}`, so a backend that answered `null`, a
                # list, or a dict without `body` -- reachable whenever a host adapter
                # overrides the `view_issue` command template -- yielded `""`, which is not
                # None, which `evaluate_issue` reads as a body that WAS read and came back
                # with no further ask. A missing key is an unread body.
                raw = payload.get("body")
                body = raw if isinstance(raw, str) else None
            except (RuntimeError, ValueError, TypeError, json.JSONDecodeError):
                # A body that cannot be read is recorded as unread rather than as empty.
                # Empty would silently mean "no further ask", turning a fetch failure into
                # evidence FOR closing -- the one direction this tool must never drift.
                body = None
        results.append(
            evaluate_issue(
                repo_root, issue, verdicts=verdicts, exclude=exclude, body=body
            )
        )
    counts: dict[str, int] = {state: 0 for state in lib().STATES}
    for result in results:
        counts[result["state"]] = counts.get(result["state"], 0) + 1
    return {
        "counted": len(results),
        "counts": counts,
        "bodies_read": with_bodies,
        # Every knob that can SUPPRESS residue is echoed. Round 1's point: `--exclude` can
        # delete the exact record that would have produced a refusal, and `--limit` can
        # truncate the backlog so a re-verification tool silently answers about a subset,
        # and the JSON gave a downstream reader no way to see either.
        "scan_scope": {
            "limit": limit,
            "list_truncated": len(issues) >= limit,
            "excluded": [str(path) for path in exclude],
            "premise_file": str(premise_file) if premise_file else None,
            "premise_verdicts_supplied": len(verdicts),
        },
        "close_recommendation": (
            "none by design -- this tool renders premise state and stops; deciding to close "
            "an issue is a human's call and keeps its own closeout floor"
        ),
        "issues": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".", help="Repo root holding charness-artifacts/")
    parser.add_argument("--repo", default=None, help="owner/repo when the backend needs it")
    parser.add_argument("--limit", type=int, default=100, help="Max open issues to list")
    parser.add_argument(
        "--premise-file",
        default=None,
        help="JSON object of issue number -> {verdict: holds|refuted, evidence: ...}. "
        "Without it every issue renders `unverifiable-by-machine`.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Durable record to skip when scanning residue; pass the goal artifact being "
        "shaped so it cannot manufacture its own residue. Repeatable.",
    )
    parser.add_argument(
        "--with-bodies",
        action="store_true",
        help="Fetch each issue body for the further-ask and path-citation checks (one "
        "backend call per issue).",
    )
    parser.add_argument("--state", default=None, help="Only report issues in this premise state")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    try:
        report = build_report(
            repo_root,
            repo=args.repo,
            limit=args.limit,
            premise_file=Path(args.premise_file) if args.premise_file else None,
            exclude=tuple(Path(value) for value in args.exclude),
            with_bodies=args.with_bodies,
        )
    # `TypeError`/`ValueError` are caught too: round 1 found a malformed `--premise-file`
    # escaping as a traceback rather than as the `{"ok": false}` envelope callers parse.
    except (RuntimeError, OSError, ImportError, TypeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    if args.state:
        # Filtering happens AFTER counts, so `counts` stays a whole-backlog denominator.
        # `counted` and `len(issues)` then disagree by design, so the filter is recorded.
        report["issues"] = [item for item in report["issues"] if item["state"] == args.state]
        report["scan_scope"]["state_filter"] = args.state
    print(json.dumps({"ok": True, **report}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
