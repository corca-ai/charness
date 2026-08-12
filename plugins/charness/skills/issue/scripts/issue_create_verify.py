"""Target-bound readback verification for the issue-create lifecycle."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BACKEND = _load_local("issue_backend", "issue_create_verify_backend")
run_backend = _BACKEND.run_backend
resolve_op = _BACKEND.resolve_op
answer_repo = _BACKEND.answer_repo

GH_VIEW_BODY_DEFAULT = [
    "issue",
    "view",
    "--repo",
    "{repo}",
    "{number}",
    "--json",
    "{json_fields}",
]
VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "json_fields"})


def _http_url(value: object) -> str | None:
    """Return a complete HTTP(S) URL, never backend diagnostic text."""
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if not candidate or "\\" in candidate or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in candidate):
        return None
    try:
        parsed = urlparse(candidate)
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError:
        return None
    if parsed.scheme in {"http", "https"} and hostname:
        return candidate
    return None


def verify_created_issue(
    repo: str,
    number: int,
    *,
    body_file: Path | None = None,
    backend: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Read a created issue through the issue-tool grammar.

    A local body file upgrades this from identity readback to byte-for-byte body
    verification. Omitting it is useful after a caller deliberately skipped
    create's automatic readback, but must not be presented as body fidelity.
    """
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    if type(number) is not int or number <= 0:
        raise RuntimeError("create verification requires a positive integer issue number")
    expected_body: str | None = None
    if body_file is not None:
        if not body_file.is_file():
            raise RuntimeError(f"verification body file not found: {body_file}")
        expected_body = body_file.read_text(encoding="utf-8")
    view_argv = resolve_op(
        backend,
        "view",
        GH_VIEW_BODY_DEFAULT,
        VIEW_PLACEHOLDERS,
        required=frozenset({"repo", "number", "json_fields"}),
        repo=repo,
        number=str(number),
        json_fields="number,body,url",
    )
    result = run_backend(view_argv)
    if result.returncode != 0:
        raise RuntimeError(
            f"create verification read-back failed: exit={result.returncode} "
            f"stderr={result.stderr.strip()!r}"
        )
    try:
        stored = json.loads(result.stdout)
    except Exception as exc:  # noqa: BLE001 - surface any decode failure as unverified
        raise RuntimeError(f"create verification read-back returned invalid JSON: {exc}") from exc
    if not isinstance(stored, dict):
        raise RuntimeError("create verification read-back returned a non-object JSON payload")
    reported_number = stored.get("number")
    if type(reported_number) is not int or reported_number != number:
        raise RuntimeError(
            "create verification answered about a different or unidentifiable issue: asked "
            f"{repo}#{number}, backend reported #{reported_number!r}"
        )
    answered_repo = answer_repo(stored)
    if answered_repo is None:
        raise RuntimeError(
            "create verification read-back did not identify its repository; "
            f"cannot verify {repo}#{number}"
        )
    if answered_repo.lower() != repo.strip().lower():
        raise RuntimeError(
            "create verification answered about a different repository: asked "
            f"{repo}#{number}, backend reported {answered_repo}#{reported_number}"
        )
    stored_body = stored.get("body")
    if expected_body is not None and not isinstance(stored_body, str):
        raise RuntimeError("create verification read-back did not return a string body")
    body_verified = expected_body is not None and stored_body == expected_body
    payload: dict[str, Any] = {
        "ok": True,
        "repo": repo,
        "number": number,
        "url": _http_url(stored.get("url")),
        "readback_verified": True,
        "body_verified": body_verified if expected_body is not None else None,
        "body_verification": "byte-identical" if expected_body is not None else "not-requested",
    }
    if expected_body is not None and not body_verified:
        payload["stored_body_bytes"] = len(stored_body.encode("utf-8"))
    return payload
