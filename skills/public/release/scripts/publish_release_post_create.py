from __future__ import annotations

import runpy
import shlex
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

_observer = runpy.run_path(str(Path(__file__).resolve().with_name("release_observer.py")))
collect_installed_readback = _observer["collect_installed_readback"]
write_release_observer = _observer["write_release_observer"]
safe_write_release_observer = _observer["safe_write_release_observer"]
validate_release_observer_record = _observer["validate_release_observer_record"]


def run_post_publish_install_refresh(
    repo_root: Path, *, command: str, run_shell
) -> dict[str, Any]:
    """Auto-run the adapter-declared post-publish install-refresh on the authoring
    machine after a verified publish, so the maintainer's managed install ends
    ``== repo`` without a manual step (closing the installed-vs-repo skew class).

    Opt-in and portable: a repo that declares no ``post_publish_install_refresh``
    skips it (``not_configured``), so a consumer repo's publish never auto-mutates a
    host cache it did not ask for. Never raises — the release is already published
    and verified, so a failed refresh is recorded as a closeout risk for the
    maintainer to re-run, not a release abort.
    """
    command = (command or "").strip()
    if not command:
        return {"status": "not_configured", "command": None}
    start = time.perf_counter()
    result = run_shell(command, cwd=repo_root, check=False)
    ok = result.returncode == 0
    return {
        "status": "refreshed" if ok else "failed",
        "command": command,
        "returncode": result.returncode,
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "stdout_tail": (result.stdout or "").strip()[-1500:],
        "stderr_tail": (result.stderr or "").strip()[-1500:],
    }


def release_view_result(repo_root: Path, tag_name: str, backend: dict[str, Any], *, backend_command, run):
    command = backend_command(backend, "release_view", ["gh", "release", "view", "{tag}"], tag=tag_name)
    return run(command, cwd=repo_root, check=False)


def verify_release_visible(
    repo_root: Path,
    tag_name: str,
    backend: dict[str, Any],
    *,
    backend_command,
    run,
    attempts: int = 3,
    initial_delay_seconds: float = 0.25,
):
    last_result = release_view_result(repo_root, tag_name, backend, backend_command=backend_command, run=run)
    delay = initial_delay_seconds
    for _attempt in range(1, max(attempts, 1)):
        if last_result.returncode == 0:
            return last_result
        time.sleep(delay)
        delay *= 2
        last_result = release_view_result(repo_root, tag_name, backend, backend_command=backend_command, run=run)
    return last_result


def _http_release_probe(url: str, *, timeout: float = 10.0) -> dict[str, Any]:
    """Default rung-2 distinct channel: an unauthenticated HTTP GET of the PUBLIC
    release URL — a transport/auth path distinct from the ``gh release view`` CLI
    proxy. Returns a ``confirmed`` verdict on HTTP 200 with a body, otherwise a
    typed non-``verified`` disposition. Never raises: a publish is already an
    external fact, so a failed probe is a recorded disposition, not a fatal error.
    """
    # Observer identity is a recorded observable, additive to the channel: the
    # rung-2 audit must be able to SEE how distinct the observer was, not only
    # the transport. This probe is credential-distinct (no auth) but shares the
    # publisher's host and process; a machine-distinct observer is a separate
    # surface, never claimed here.
    observer = "unauthenticated-http (credential-free; same host/process as publisher)"
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "charness-release-distinct-channel"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (public release URL)
            body = response.read(4096)
            status = getattr(response, "status", None) or response.getcode()
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return {
            "channel": "https-fetch", "observer": observer, "url": url,
            "status": "blocked-needs-capability",
            "reason": f"distinct-channel HTTP fetch of the public release URL failed: {exc}",
        }
    if status == 200 and body:
        return {
            "channel": "https-fetch", "observer": observer, "url": url, "status": "confirmed",
            "http_status": status, "evidence_len": len(body),
        }
    return {
        "channel": "https-fetch", "observer": observer, "url": url,
        "status": "not-confirmed", "http_status": status,
        "reason": f"distinct-channel HTTP fetch returned HTTP {status} with {len(body)} body bytes",
    }


# Executables that run ANOTHER command rather than being the command, so the
# same-proxy check must look through them instead of at them.
_COMMAND_WRAPPERS = frozenset(
    {"sh", "bash", "zsh", "dash", "env", "command", "nohup", "time", "stdbuf", "nice", "setsid"}
)
_WRAPPER_INLINE_FLAGS = frozenset({"-c", "-lc", "-cl", "-ic"})


_UNWRAP_BUDGET = 32


def _normalize_tokens(tokens: list[str], *, drop: set[str] | None = None) -> set[str]:
    """Tokens as a comparison set: EVERY token reduced to its path basename, not
    only the executable. Basenaming just the first token let a wrapper and an
    absolute path compose into an escape (`sudo /usr/bin/gh release view v1`),
    even though each half alone was caught."""
    dropped = drop or set()
    return {PurePosixPath(token).name for token in tokens if token and token not in dropped}


def _unwrap_command_tokens(tokens: list[str], *, depth: int = _UNWRAP_BUDGET) -> tuple[list[str], bool]:
    """``(tokens, exhausted)`` after stripping leading env assignments and wrapper
    executables and descending into a wrapper's inline `-c "<command>"` payload.

    ``exhausted`` is True when the budget ran out with unwrapping still to do.
    The caller treats that as same-proxy: a probe nested past the budget is one
    this check could not establish anything about, and at a publish boundary an
    unestablished scope must not read as a clean pass.
    """
    while tokens:
        if depth <= 0:
            return tokens, True
        head = tokens[0]
        # `FOO=bar gh ...`
        if "=" in head and not head.startswith("-") and "/" not in head.split("=", 1)[0]:
            tokens, depth = tokens[1:], depth - 1
            continue
        if PurePosixPath(head).name in _COMMAND_WRAPPERS:
            rest = tokens[1:]
            if rest and rest[0] in _WRAPPER_INLINE_FLAGS:
                try:
                    tokens = shlex.split(rest[1], comments=True) if len(rest) > 1 else []
                except ValueError:
                    return tokens, True
            else:
                tokens = rest
            depth -= 1
            continue
        break
    return tokens, False


def release_view_shape(backend: dict[str, Any], backend_command, tag_name: str) -> set[str] | None:
    """The backend's own ``release_view`` command as a tag-free comparison set,
    or ``None`` when the template cannot discriminate.

    A degenerate template — empty, or a single generic token like ``gh`` — makes
    subset matching meaningless in both directions: it would refuse every probe
    sharing an executable, or pass everything. ``None`` says the guard could not
    be evaluated, which the caller records rather than silently reading as
    "distinct" (the class-(a) shape this audit tracks).
    """
    view_tokens = backend_command(backend, "release_view", ["gh", "release", "view", "{tag}"], tag=tag_name)
    shape = _normalize_tokens(view_tokens, drop={tag_name})
    return shape if len(shape) >= 2 else None


def _probe_matches_release_view_shape(
    rendered_command: str, *, backend: dict[str, Any], backend_command, tag_name: str
) -> bool:
    """Data-driven same-proxy check (P4): True when the rendered probe command IS
    the backend's own ``release_view`` command -- the exact command
    ``verify_release_visible`` already used for tag/version visibility -- derived
    from the backend config via ``backend_command``, never an enumerated list of
    forbidden command strings.

    Matching is by NORMALIZED TOKEN CONTAINMENT, not by positional prefix. A
    prefix comparison was defeated by everything that does not change what runs
    (D3): moving a flag ahead of the tag, `sh -c "..."`, `env`, or an absolute
    `/usr/bin/gh` path all slipped through while running the identical query.
    Wrappers are unwrapped, the executable is reduced to its basename, and the
    probe matches when it contains every token of the view command in any order.

    Deliberately biased toward FLAGGING at this boundary: a probe wrongly called
    same-proxy costs the operator one genuinely distinct probe, while a same-proxy
    probe wrongly called distinct is a release confirming itself through the
    channel it was supposed to be checked against. Every branch that cannot
    ESTABLISH distinctness therefore returns True, including an unparseable
    command and an unwrap budget exhausted mid-descent.

    The TAG is excluded from the comparison. `gh release view` with no tag
    defaults to the latest release — which, moments after publish, is the release
    being confirmed — so requiring the tag to appear let the same query through
    by omitting an argument.
    """
    view_shape = release_view_shape(backend, backend_command, tag_name)
    if view_shape is None:
        # A degenerate `release_view` template (empty, or a single generic token
        # like `gh`) cannot discriminate: subset-matching against it would either
        # refuse every probe sharing an executable or silently pass everything.
        # Neither verdict is established, so do not render one.
        return False
    try:
        raw_tokens = shlex.split(rendered_command, comments=True)
    except ValueError:
        return True
    probe_tokens, exhausted = _unwrap_command_tokens(raw_tokens)
    if exhausted:
        return True
    if not probe_tokens:
        return False
    return view_shape.issubset(_normalize_tokens(probe_tokens))


def confirm_release_via_distinct_channel(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    adapter_data: dict[str, Any],
    run_shell,
    tag_name: str,
    expected_release_url: str | None,
    http_probe=_http_release_probe,
    backend: dict[str, Any] | None = None,
    backend_command=None,
) -> dict[str, Any]:
    """Rung-2 distinct-channel observer (P4): confirm the PUBLISHED release through
    a channel DISTINCT FROM ``gh release view``, recording the verdict on the
    payload BEFORE issue closeout. An adapter-declared
    ``post_publish_distinct_channel_probe`` shell command runs when present
    (``{tag}``/``{url}`` substituted); otherwise the default is an HTTP fetch of the
    public release URL. The verdict is a recorded observable the human rung-2 audit
    reads at closeout — **never an automated proceed-gate (F2a)**.

    When ``backend``/``backend_command`` are supplied, a configured probe that
    matches the backend's own ``release_view`` command shape is mechanically
    flagged ``same-proxy-flagged`` and never run — prose alone let this same-proxy
    probe masquerade as a distinct channel (design-north-star.md P4).
    """
    probe_command = str(adapter_data.get("post_publish_distinct_channel_probe", "") or "").strip()
    if probe_command:
        rendered = probe_command.replace("{tag}", tag_name).replace("{url}", expected_release_url or "")
        if backend is not None and backend_command is not None and _probe_matches_release_view_shape(
            rendered, backend=backend, backend_command=backend_command, tag_name=tag_name
        ):
            record = {
                "channel": "adapter-probe",
                "observer": "same-proxy (backend release_view shape; not a distinct observer)",
                "command": rendered, "status": "same-proxy-flagged",
                "reason": (
                    "configured post_publish_distinct_channel_probe matches this backend's own "
                    "`release_view` command -- the SAME proxy `verify_release_visible` already used, "
                    "not a channel distinct from it. Point the probe at a genuinely distinct channel "
                    "(deploy readback, artifact download, consumer-side check)."
                ),
            }
        else:
            result = run_shell(rendered, cwd=repo_root, check=False)
            # Whether the same-proxy guard could be EVALUATED at all is part of
            # the record. A degenerate `release_view` template makes the guard
            # inconclusive, and an unevaluated guard must not read as a probe
            # that passed one.
            guard_scope = "not-configured"
            if backend is not None and backend_command is not None:
                guard_scope = (
                    "evaluated"
                    if release_view_shape(backend, backend_command, tag_name) is not None
                    else "inconclusive-degenerate-release-view-template"
                )
            record: dict[str, Any] = {
                "channel": "adapter-probe",
                "observer": (
                    "adapter-probe-shell (operator-configured; same host/process as publisher)"
                ),
                "same_proxy_guard": guard_scope,
                "command": rendered,
                "status": "confirmed" if result.returncode == 0 else "not-confirmed",
                "returncode": result.returncode,
            }
            if result.returncode != 0:
                tail = (result.stderr or result.stdout or "").strip()[-1500:]
                record["reason"] = tail or "distinct-channel probe returned a nonzero exit"
    elif expected_release_url:
        record = http_probe(expected_release_url)
    else:
        record = {
            "channel": "none", "observer": "none", "status": "skipped",
            "reason": (
                "no published release URL and no adapter `post_publish_distinct_channel_probe` "
                "declared; declare a distinct channel (e.g. an HTTP fetch of the public release "
                "URL) so rung-2 confirms through a channel distinct from `gh release view`"
            ),
        }
    payload["distinct_channel_verification"] = record
    return record


def evaluate_release_distinct_channel(payload: dict[str, Any]) -> dict[str, Any]:
    """Rung-1 presence floor (P5): refuse advancing to issue closeout when the
    payload is SILENT on the per-surface distinct-channel verdict. Presence/form
    only — a ``confirmed`` OR a typed non-``verified`` disposition passes it
    EQUALLY (render-not-declare, F2a). It NEVER declares the release confirmed and
    is NEVER an automated ``confirmed ⇒ proceed`` gate; only a missing/empty
    record fails.
    """
    record = payload.get("distinct_channel_verification")
    ok = isinstance(record, dict) and bool(str(record.get("status", "")).strip())
    return {"ok": ok, "missing": not ok, "record": record if ok else None}


def fail_release_distinct_channel_floor(payload: dict[str, Any]) -> None:
    raise SystemExit(
        "release rung-1 floor refused issue closeout: no per-surface distinct-channel "
        "verdict was recorded before `ensure_release_issues_closed`.\n"
        f"tag: {payload.get('tag_name')}\n"
        f"release_url: {payload.get('release_url') or 'unavailable'}\n"
        "wire `confirm_release_via_distinct_channel` (the rung-2 observer) so a confirmation "
        "or a typed non-`verified` disposition is recorded before the irreversible issue close."
    )


def fail_after_post_create_verification(payload: dict[str, Any], *, verification_result) -> None:
    command = " ".join(str(part) for part in verification_result.args)
    raise SystemExit(
        "release post-create verification failed after external mutation\n"
        f"tag: {payload['tag_name']}\n"
        f"command: {command}\n"
        f"exit_code: {verification_result.returncode}\n"
        f"release_url: {payload.get('release_url') or 'unavailable'}\n"
        f"artifact_path: {payload.get('artifact_path')}\n"
        f"post_publish_artifact_commit_sha: {payload.get('post_publish_artifact_commit_sha') or 'not_committed'}\n"
        f"STDOUT:\n{verification_result.stdout}\n"
        f"STDERR:\n{verification_result.stderr}"
    )
