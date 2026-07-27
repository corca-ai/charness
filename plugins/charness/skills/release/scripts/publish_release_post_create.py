from __future__ import annotations

import runpy
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_observer = runpy.run_path(str(Path(__file__).resolve().with_name("release_observer.py")))
_same_proxy = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_same_proxy_guard.py")))
release_view_shape = _same_proxy["release_view_shape"]
_probe_matches_release_view_shape = _same_proxy["_probe_matches_release_view_shape"]
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


def audit_published_release_body(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    tag_name: str,
    backend: dict[str, Any],
    backend_command,
    run,
    audit_notes_text,
) -> dict[str, Any]:
    """Post-create audit of the PUBLISHED release body for mutable source-tree
    pointers, recorded on ``payload`` as an advisory.

    The pre-publish notes audit only runs when a notes FILE is supplied, so the
    `--generate-notes` path — the default — published a body nothing had ever
    looked at (D2 residual). Auto-generated bodies are commit messages and PR
    text, a prime carrier of `blob/main` links.

    This is post-hoc by construction: `--generate-notes` composes the body at
    creation time, so there is nothing to inspect earlier. It therefore records
    an ADVISORY, never a blocker — the release already exists, and refusing after
    the fact would only strand the publish. The remedy is `gh release edit`.
    """
    record: dict[str, Any] = {"scope": "published-release-body", "tag": tag_name}
    try:
        command = backend_command(
            backend, "release_view_body", ["gh", "release", "view", "{tag}", "--json", "body", "-q", ".body"],
            tag=tag_name,
        )
        result = run(command, cwd=repo_root, check=False)
    # BaseException, not Exception: `backend_command` raises SystemExit for a
    # non-`gh` backend with no template for this op, and SystemExit does not
    # derive from Exception. This runs AFTER the release exists and after the
    # rollback wrapper's scope, so an escaping SystemExit strands the publish
    # before the rung-1 floor, issue closeout, and the final artifact commit —
    # for 100% of non-`gh` adapters, over an advisory that is allowed to fail.
    except BaseException as exc:  # noqa: BLE001 - a stranded publish is worse
        record.update(
            status="not-configured" if isinstance(exc, SystemExit) else "unavailable",
            reason=f"{exc.__class__.__name__}: {exc}",
        )
        payload["published_notes_audit"] = record
        return record
    if getattr(result, "returncode", 1) != 0:
        record.update(
            status="unavailable",
            reason=(getattr(result, "stderr", "") or "release body readback failed").strip()[-500:],
        )
        payload["published_notes_audit"] = record
        return record
    body = getattr(result, "stdout", "") or ""
    if not body.strip():
        # An empty body is what a misrouted, unauthenticated, or wrong-op
        # readback returns. Calling that `clean` is class (a) — a PASS over a
        # scope never established — reintroduced by the fix for class (d).
        record.update(
            status="unestablished", advisories=[], body_len=len(body),
            reason="release body readback returned an empty body; nothing was audited",
        )
        payload["published_notes_audit"] = record
        return record
    advisories = audit_notes_text(body, target_tag=tag_name)
    record.update(
        status="advisory" if advisories else "clean",
        advisories=advisories,
        body_len=len(body),
    )
    payload["published_notes_audit"] = record
    return record


_PROBE_BODY_BYTES = 262144


def _http_release_probe(
    url: str, *, timeout: float = 10.0, expected_content: str | None = None
) -> dict[str, Any]:
    """Default rung-2 distinct channel: an unauthenticated HTTP GET of the PUBLIC
    release URL — a transport/auth path distinct from the ``gh release view`` CLI
    proxy. Never raises: a publish is already an external fact, so a failed probe
    is a recorded disposition, not a fatal error.

    ``confirmed`` requires the response to CONTAIN ``expected_content`` (the
    release tag). Confirming on "HTTP 200 with at least one body byte" made the
    verdict independent of what came back (D4): a captive portal, a rate-limit
    notice, a 404 page served with a 200, or a redirect to the repository root
    all confirmed a release that might not exist. ``urllib`` follows redirects
    silently, so the URL actually fetched is recorded too — the probe must be
    able to say it looked at the page it claims to have looked at.

    **What this channel can and cannot establish, measured 2026-07-27.**
    `github.com/<o>/<r>/releases/tag/<tag>` returns HTTP 200 with the tag in the
    body for a tag that has NO GitHub release (verified against `v0.1.1`, a
    pushed tag with no release: 200, tag present 23 times; both that page and a
    real release page title themselves "Release <tag>"). The publish flow pushes
    the tag BEFORE creating the release, so this probe cannot distinguish "the
    release exists" from "the tag was pushed". The unauthenticated REST API,
    which does distinguish, answered 403 (rate-limited) and is not a dependable
    default. So the record carries ``establishes`` naming the narrower claim,
    rather than letting `confirmed` be read as release existence.
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
            body = response.read(_PROBE_BODY_BYTES)
            status = getattr(response, "status", None) or response.getcode()
            final_url = getattr(response, "url", None) or url
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return {
            "channel": "https-fetch", "observer": observer, "url": url,
            "status": "blocked-needs-capability",
            "reason": f"distinct-channel HTTP fetch of the public release URL failed: {exc}",
        }
    base = {
        "channel": "https-fetch", "observer": observer, "url": url,
        "http_status": status, "evidence_len": len(body), "fetched_url": final_url,
    }
    if status != 200 or not body:
        return {
            **base, "status": "not-confirmed",
            "reason": f"distinct-channel HTTP fetch returned HTTP {status} with {len(body)} body bytes",
        }
    if expected_content is None:
        # No identifying string to look for is an UNESTABLISHED scope, not a
        # confirmation: the fetch proves a page exists, never that it is this
        # release's page.
        return {
            **base, "status": "not-confirmed",
            "reason": (
                "distinct-channel HTTP fetch succeeded but no expected content was supplied, so "
                "the response was never checked against this release"
            ),
        }
    text = body.decode("utf-8", errors="ignore")
    if expected_content not in text:
        return {
            **base, "status": "not-confirmed", "expected_content": expected_content,
            "reason": (
                f"distinct-channel HTTP fetch returned HTTP {status} but the response body does "
                f"not mention `{expected_content}`; the page fetched was `{final_url}`"
            ),
        }
    return {
        **base, "status": "confirmed", "expected_content": expected_content,
        "establishes": "public-page-reachable-and-names-the-tag",
        "does_not_establish": (
            "that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed "
            "tag with no release, and the tag is pushed before the release is created"
        ),
    }


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
        record = http_probe(expected_release_url, expected_content=tag_name)
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
