from __future__ import annotations

import time
from pathlib import Path
from typing import Any


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
