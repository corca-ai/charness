from __future__ import annotations

import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Rung-2 distinct-channel verdict vocabulary. A `confirmed`, or a typed
# non-`verified` disposition — never a `gh release view` re-read standing in for
# confirmation (the same-proxy re-examination P4 of design-north-star.md forbids).
DISTINCT_CHANNEL_STATUSES = ("confirmed", "not-confirmed", "blocked-needs-capability", "skipped")


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
    result = run_shell(command, cwd=repo_root, check=False)
    ok = result.returncode == 0
    return {
        "status": "refreshed" if ok else "failed",
        "command": command,
        "returncode": result.returncode,
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
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "charness-release-distinct-channel"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (public release URL)
            body = response.read(4096)
            status = getattr(response, "status", None) or response.getcode()
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return {
            "channel": "https-fetch", "url": url, "status": "blocked-needs-capability",
            "reason": f"distinct-channel HTTP fetch of the public release URL failed: {exc}",
        }
    if status == 200 and body:
        return {
            "channel": "https-fetch", "url": url, "status": "confirmed",
            "http_status": status, "evidence_len": len(body),
        }
    return {
        "channel": "https-fetch", "url": url, "status": "not-confirmed", "http_status": status,
        "reason": f"distinct-channel HTTP fetch returned HTTP {status} with {len(body)} body bytes",
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
) -> dict[str, Any]:
    """Rung-2 distinct-channel observer (P4): confirm the PUBLISHED release through
    a channel DISTINCT FROM ``gh release view``, recording the verdict on the
    payload BEFORE issue closeout. An adapter-declared
    ``post_publish_distinct_channel_probe`` shell command runs when present
    (``{tag}``/``{url}`` substituted); otherwise the default is an HTTP fetch of the
    public release URL. The verdict is a recorded observable the human rung-2 audit
    reads at closeout — **never an automated proceed-gate (F2a)**.
    """
    probe_command = str(adapter_data.get("post_publish_distinct_channel_probe", "") or "").strip()
    if probe_command:
        rendered = probe_command.replace("{tag}", tag_name).replace("{url}", expected_release_url or "")
        result = run_shell(rendered, cwd=repo_root, check=False)
        record: dict[str, Any] = {
            "channel": "adapter-probe", "command": rendered,
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
            "channel": "none", "status": "skipped",
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
