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
import re
import runpy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)


_emit_yaml = _load_local("issue_yaml_output", "issue_create_yaml_output").emit_yaml
_BACKEND = _load_local("issue_backend", "issue_create_backend")
_ADAPTER = _load_local("resolve_adapter", "issue_create_adapter")
_VERIFY = _load_local("issue_create_verify", "issue_create_verify")
run_backend = _BACKEND.run_backend
resolve_op = _BACKEND.resolve_op
verify_created_issue = _VERIFY.verify_created_issue
_http_url = _VERIFY._http_url

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
BODY_PREVIEW_CHARS = 1200
PLACEHOLDER_TITLES: frozenset[str] = frozenset({"x", "test"})
# Labels and milestone are appended as flags after the rendered base command,
# so they are not template placeholders — only repo/title/body_file are.
CREATE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "title", "body_file"})

_ISSUE_NUMBER_RE = re.compile(r"/issues/(\d+)\b")
_MARKDOWN_IMAGE_RE = re.compile(r"(?<!\\)!\[[^\]]*\]\(\s*<?(https?://[^\s)>]+)>?", re.IGNORECASE)
_MARKDOWN_IMAGE_REFERENCE_RE = re.compile(
    r"(?<!\\)!\[([^\]]+)\]\[([^\]]*)\]", re.IGNORECASE
)
_MARKDOWN_IMAGE_SHORTCUT_RE = re.compile(
    r"(?<!\\)!\[([^\]]+)\](?![ \t]*[\[(])", re.IGNORECASE
)
_MARKDOWN_REFERENCE_DEFINITION_RE = re.compile(
    r"^\s*\[([^\]]+)\]:\s*<?(https?://[^\s>]+)>?", re.IGNORECASE | re.MULTILINE
)
_HTML_IMAGE_RE = re.compile(
    r"<img\b[^>]*\bsrc\s*=\s*(?:['\"](https?://[^'\"]+)['\"]|(https?://[^\s>]+))[^>]*>",
    re.IGNORECASE,
)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"(?P<ticks>`+).*?(?P=ticks)", re.DOTALL)


class IssuePreparationError(RuntimeError):
    """Typed refusal raised before an issue backend can mutate state."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class IssueMutationError(RuntimeError):
    """A create command was invoked but its provider outcome is not verified."""

    def __init__(self, message: str, *, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.mutation_invoked = True


def _outside_fenced_code(text: str) -> str:
    text = _HTML_COMMENT_RE.sub("", text)
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in {"```", "~~~"}:
            fence = None if fence == marker else marker if fence is None else fence
            kept.append("\n" if line.endswith("\n") else "")
        elif fence is None and not line.startswith(("    ", "\t")):
            kept.append(line)
        else:
            kept.append("\n" if line.endswith("\n") else "")
    return _INLINE_CODE_RE.sub("", "".join(kept))


def _is_private_provider_media_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold()
    path = parsed.path.casefold()
    return (host == "files.slack.com" or host.endswith(".slack.com")) and any(
        marker in path for marker in ("/files/", "/files-pri/", "/files-tmb/")
    )


def _private_provider_image_urls(body_text: str) -> list[str]:
    prose = _outside_fenced_code(body_text)
    urls = [match.group(1) for match in _MARKDOWN_IMAGE_RE.finditer(prose)]
    urls.extend(match.group(1) or match.group(2) for match in _HTML_IMAGE_RE.finditer(prose))
    definitions = {
        match.group(1).strip().casefold(): match.group(2)
        for match in _MARKDOWN_REFERENCE_DEFINITION_RE.finditer(prose)
    }
    for match in _MARKDOWN_IMAGE_REFERENCE_RE.finditer(prose):
        label = match.group(2).strip() or match.group(1).strip()
        if url := definitions.get(label.casefold()):
            urls.append(url)
    for match in _MARKDOWN_IMAGE_SHORTCUT_RE.finditer(prose):
        if url := definitions.get(match.group(1).strip().casefold()):
            urls.append(url)
    return sorted({url for url in urls if _is_private_provider_media_url(url)})


def _parse_created_number(stdout: str) -> int | None:
    """Pull the issue number from a backend's create output.

    `gh issue create` prints the new issue URL (``.../issues/123``). Fall back
    to a trailing integer on the last non-empty line for backends that print a
    bare number instead of a URL.
    """
    match = _ISSUE_NUMBER_RE.search(stdout)
    if match:
        number = int(match.group(1))
        return number if number > 0 else None
    for line in reversed(stdout.splitlines()):
        token = line.strip().rstrip("/").rsplit("/", 1)[-1]
        if token.isdigit():
            number = int(token)
            return number if number > 0 else None
    return None


def _positive_issue_number(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("issue number must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("issue number must be a positive integer")
    return number


def create_issue(
    repo: str,
    title: str,
    body_file: Path,
    *,
    backend: dict[str, Any] | None = None,
    labels: list[str] | None = None,
    milestone: str | None = None,
    skip_readback: bool = False,
    allow_placeholder_title: bool = False,
) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    normalized_title = title.strip().casefold()
    if normalized_title in PLACEHOLDER_TITLES and not allow_placeholder_title:
        raise RuntimeError(
            f"placeholder title {title.strip()!r} refused before issue creation; "
            "pass --allow-placeholder-title to create it intentionally"
        )
    if not body_file.is_file():
        raise RuntimeError(f"create body file not found: {body_file}")
    body_text = body_file.read_text(encoding="utf-8")
    private_media = _private_provider_image_urls(body_text)
    if private_media:
        raise IssuePreparationError(
            "private_provider_media_unpublished",
            "private provider image reference refused before issue creation; "
            "materialize it at a durable URL the target audience can read, or replace "
            "the image syntax with an explicit `Media evidence unavailable:` disposition",
        )

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
        raise IssueMutationError(
            f"create failed: exit={create_result.returncode} "
            f"stderr={create_result.stderr.strip()!r}",
            exit_code=create_result.returncode,
        )
    created_stdout = create_result.stdout.strip()
    created_number = _parse_created_number(created_stdout)
    created_url = _http_url(created_stdout)

    payload: dict[str, Any] = {
        "ok": True,
        "repo": repo,
        "title": title,
        "labels": list(labels or []),
        "milestone": milestone,
        "body_bytes": len(body_text.encode("utf-8")),
        "body_preview": body_text[:BODY_PREVIEW_CHARS],
        # `number` and `url` match `issue_read.py` and the verified ledger contract.
        "number": created_number,
        "url": created_url,
        "body_verified": None,
        "verification": None,
    }

    if created_number is not None:
        payload["verification"] = {
            "command": "verify-create",
            "repo": repo,
            "number": created_number,
            "body_file": str(body_file),
        }

    if skip_readback:
        payload["readback_skipped"] = True
        payload["verify_skipped"] = "issue created; post-create readback skipped by caller"
        return payload
    if created_number is None:
        payload["verify_error"] = (
            "could not parse the created issue number from backend output; "
            "body write is unverified — read the issue back manually before "
            "reporting success"
        )
        return payload

    try:
        verified = verify_created_issue(repo, created_number, body_file=body_file, backend=backend)
    except RuntimeError as exc:
        payload["verify_error"] = str(exc)
        return payload
    if payload["url"] is None:
        readback_url = verified["url"]
        payload["url"] = readback_url
    payload["body_verified"] = verified["body_verified"]
    if not payload["body_verified"]:
        payload["stored_body_bytes"] = verified["stored_body_bytes"]
    return payload


def _emit(payload: dict[str, Any]) -> None:
    _emit_yaml(payload)


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
            skip_readback=args.skip_readback,
            allow_placeholder_title=args.allow_placeholder_title,
        )
    except IssuePreparationError as exc:
        _emit(
            {
                "ok": False,
                "error": str(exc),
                "error_code": exc.code,
                "selected_backend": resolved["backend"],
            }
        )
        return 2
    except RuntimeError as exc:
        _emit({"ok": False, "error": str(exc), "selected_backend": resolved["backend"]})
        return 2
    result["selected_backend"] = resolved["backend"]
    _emit(result)
    return 0


def command_verify_create(args: argparse.Namespace) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    if not resolved["adapter_ok"]:
        _emit({"ok": False, "adapter": resolved["adapter"]})
        return 1
    try:
        result = verify_created_issue(
            args.repo,
            args.number,
            body_file=args.body_file.resolve() if args.body_file else None,
            backend=resolved["backend"],
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
    create.add_argument(
        "--skip-readback",
        action="store_true",
        help="Creation still occurs; skip only post-create readback verification",
    )
    create.add_argument(
        "--allow-placeholder-title",
        action="store_true",
        help="Allow a known placeholder title intentionally",
    )
    create.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    create.set_defaults(func=command_create)

    verify = subparsers.add_parser(
        "verify-create",
        help="Read back a created issue through this tool; add --body-file for byte verification",
    )
    verify.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    verify.add_argument("--number", type=_positive_issue_number, required=True, help="Created issue number to read back")
    verify.add_argument("--body-file", type=Path, help="Original issue body file for byte-for-byte verification")
    verify.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    verify.set_defaults(func=command_verify_create)
