"""Create a GitHub issue with the body delivered via ``--body-file``.

Issue bodies were getting corrupted because creation flows built a backend
command with an inline shell-quoted ``--body`` string.
Multi-line Korean/English, Markdown, fenced code, backticks, quotes, dollar
signs, and URLs all survive only if the body never passes through a shell
quoting layer. This helper writes the body to a file and hands the backend
``--body-file``, then reads the created issue back and reports whether the
stored body is byte-identical to the input — so the agent can distinguish a
confirmed write from an unverified one.
"""

from __future__ import annotations

import argparse
import json
import re
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BACKEND = _load_local("issue_backend", "issue_create_backend")
_ADAPTER = _load_local("resolve_adapter", "issue_create_adapter")
run_backend = _BACKEND.run_backend
resolve_op = _BACKEND.resolve_op

GH_CREATE_DEFAULT = [
    "issue",
    "create",
    "--repo",
    "{repo}",
    "--title",
    "{title}",
    "--body-file",
    "{body_file}",
]
# View the just-created issue to read its stored body back for verification.
GH_VIEW_BODY_DEFAULT = [
    "issue",
    "view",
    "--repo",
    "{repo}",
    "{number}",
    "--json",
    "{json_fields}",
]
# Labels and milestone are appended as flags after the rendered base command,
# so they are not template placeholders — only repo/title/body_file are.
CREATE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "title", "body_file"})
VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "json_fields"})

_ISSUE_NUMBER_RE = re.compile(r"/issues/(\d+)\b")


def _parse_created_number(stdout: str) -> int | None:
    """Pull the issue number from a backend's create output.

    `gh issue create` prints the new issue URL (``.../issues/123``). Fall back
    to a trailing integer on the last non-empty line for backends that print a
    bare number instead of a URL.
    """
    match = _ISSUE_NUMBER_RE.search(stdout)
    if match:
        return int(match.group(1))
    for line in reversed(stdout.splitlines()):
        token = line.strip().rstrip("/").rsplit("/", 1)[-1]
        if token.isdigit():
            return int(token)
    return None


def create_issue(
    repo: str,
    title: str,
    body_file: Path,
    *,
    backend: dict[str, Any] | None = None,
    labels: list[str] | None = None,
    milestone: str | None = None,
    verify: bool = True,
) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    if not body_file.is_file():
        raise RuntimeError(f"create body file not found: {body_file}")
    body_text = body_file.read_text(encoding="utf-8")

    create_argv = resolve_op(
        backend,
        "create",
        GH_CREATE_DEFAULT,
        CREATE_PLACEHOLDERS,
        repo=repo,
        title=title,
        body_file=str(body_file),
    )
    for label in labels or []:
        create_argv += ["--label", label]
    if milestone:
        create_argv += ["--milestone", milestone]

    create_result = run_backend(create_argv)
    if create_result.returncode != 0:
        raise RuntimeError(
            f"create failed: exit={create_result.returncode} "
            f"stderr={create_result.stderr.strip()!r}"
        )
    created_stdout = create_result.stdout.strip()
    created_number = _parse_created_number(created_stdout)

    payload: dict[str, Any] = {
        "ok": True,
        "repo": repo,
        "title": title,
        "labels": list(labels or []),
        "milestone": milestone,
        "body_bytes": len(body_text.encode("utf-8")),
        "created_url": created_stdout or None,
        "created_number": created_number,
        "create_argv": create_argv,
        "body_verified": None,
        "view_argv": None,
    }

    if not verify:
        payload["verify_skipped"] = "verification disabled by caller"
        return payload
    if created_number is None:
        payload["verify_error"] = (
            "could not parse the created issue number from backend output; "
            "body write is unverified — read the issue back manually before "
            "reporting success"
        )
        return payload

    view_argv = resolve_op(
        backend,
        "view",
        GH_VIEW_BODY_DEFAULT,
        VIEW_PLACEHOLDERS,
        repo=repo,
        number=str(created_number),
        json_fields="body",
    )
    payload["view_argv"] = view_argv
    view_result = run_backend(view_argv)
    if view_result.returncode != 0:
        payload["verify_error"] = (
            f"created {repo}#{created_number} but read-back failed: "
            f"exit={view_result.returncode} stderr={view_result.stderr.strip()!r}"
        )
        return payload
    try:
        stored = json.loads(view_result.stdout)
    except Exception as exc:  # noqa: BLE001 - surface any decode failure as unverified
        payload["verify_error"] = f"read-back returned invalid JSON: {exc}"
        return payload
    stored_body = stored.get("body", "")
    payload["body_verified"] = stored_body == body_text
    if not payload["body_verified"]:
        payload["stored_body_bytes"] = len(str(stored_body).encode("utf-8"))
    return payload


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _resolve_backend(repo_root: Path) -> dict[str, Any]:
    adapter = _ADAPTER.load_adapter(repo_root)
    if not adapter["valid"]:
        return {"adapter": adapter, "backend": _ADAPTER.default_backend(), "adapter_ok": False}
    backend = dict(adapter["data"].get("issue_backend") or _ADAPTER.default_backend())
    return {"adapter": adapter, "backend": backend, "adapter_ok": True}


def command_create(args: argparse.Namespace) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    if not resolved["adapter_ok"]:
        _emit({"ok": False, "adapter": resolved["adapter"]})
        return 1
    try:
        result = create_issue(
            args.repo,
            args.title,
            args.body_file.resolve(),
            backend=resolved["backend"],
            labels=args.label,
            milestone=args.milestone,
            verify=not args.no_verify,
        )
    except RuntimeError as exc:
        _emit({"ok": False, "error": str(exc), "selected_backend": resolved["backend"]})
        return 2
    result["selected_backend"] = resolved["backend"]
    _emit(result)
    return 0


def register_create_subparser(subparsers: Any, cwd_default: Path) -> None:
    create = subparsers.add_parser(
        "create",
        help="Create an issue with the body sourced from --body-file (never inline shell-quoted)",
    )
    create.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    create.add_argument("--title", required=True, help="Issue title (short, single-line)")
    create.add_argument("--body-file", type=Path, required=True, help="Path to the issue body file (UTF-8)")
    create.add_argument("--label", action="append", help="Existing repository label to apply; repeat per label")
    create.add_argument("--milestone", help="Existing repository milestone title to assign")
    create.add_argument("--no-verify", action="store_true", help="Skip reading the created issue body back")
    create.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    create.set_defaults(func=command_create)
