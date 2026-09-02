"""Own release command execution, backend templates, and live release probes.

These helpers form the command boundary for publishing: they decide how a
release operation is rendered and how its subprocess is observed. Version
history and unreleased-scope arithmetic are a separate release concept.
"""

from __future__ import annotations

import re
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.core.subprocess_guard import (
        heartbeat_interval_from_env,
        run_monitored_phase,
        run_process,
    )
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from scripts.core.subprocess_guard import heartbeat_interval_from_env, run_monitored_phase, run_process

RELEASE_VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"tag"})
RELEASE_CREATE_PLACEHOLDERS: frozenset[str] = frozenset({"tag", "title"})

_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")

OP_PLACEHOLDERS: dict[str, frozenset[str]] = {
    "release_view": RELEASE_VIEW_PLACEHOLDERS,
    # Reads the PUBLISHED release body back for the post-create notes audit.
    # Same placeholders as `release_view`; a distinct op so an adapter can point
    # it at a backend whose body readback is not a `--json` flag.
    "release_view_body": RELEASE_VIEW_PLACEHOLDERS,
    "release_create": RELEASE_CREATE_PLACEHOLDERS,
    "auth_check": frozenset(),
}
COMMAND_TIMEOUT_SECONDS = 1800
PROGRESS_INTERVAL_ENV = "CHARNESS_RELEASE_PROGRESS_INTERVAL_SECONDS"
_TAG_IDENTITY = runpy.run_path(str(Path(__file__).with_name("release_tag_identity.py")))
_single_remote_object_id = _TAG_IDENTITY["single_remote_object_id"]


def _refuse(rendered: str, result: subprocess.CompletedProcess[str]) -> None:
    raise SystemExit(
        f"command failed: {rendered}\n"
        f"exit_code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def run(command: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Quiet, buffered probe: `git` queries, backend reads, tag lookups.

    These finish in milliseconds and their body is only interesting when they
    fail, so `run_process`'s quiet shape is the correct one. Use `run_phase` for
    anything an operator could end up waiting on.
    """
    result = run_process(command, cwd=cwd, timeout_seconds=COMMAND_TIMEOUT_SECONDS)
    if check and result.returncode != 0:
        _refuse(" ".join(command), result)
    return result


def run_shell(command: str, *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    """The shell-string form of `run`, with the same quiet-probe contract."""
    result = run_process(
        command,
        cwd=cwd,
        timeout_seconds=COMMAND_TIMEOUT_SECONDS,
        shell=True,
        executable="/bin/bash",
    )
    if check and result.returncode != 0:
        _refuse(command, result)
    return result


def run_phase(
    command: str, *, cwd: Path, phase: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """`run_shell` for a command an operator is WAITING on, not merely reading.

    Same refusal contract; the difference is that start, a bounded heartbeat, and
    the terminal status reach stderr while the child runs. The standing quality
    runner is the reason this exists: it streams its own per-check lifecycle, and
    routing it through `run_shell` bounded at 1800s turned an observable gate into
    a half-hour of silence with no way to tell "still working" from "hung".
    """
    outcome = run_monitored_phase(
        command,
        cwd=cwd,
        phase=phase,
        timeout_seconds=COMMAND_TIMEOUT_SECONDS,
        heartbeat_seconds=heartbeat_interval_from_env(PROGRESS_INTERVAL_ENV),
        shell=True,
        executable="/bin/bash",
    )
    result = outcome.completed_process()
    if check and result.returncode != 0:
        _refuse(command, result)
    return result


def git_status(repo_root: Path) -> list[str]:
    result = run(["git", "status", "--short"], cwd=repo_root)
    return [line for line in result.stdout.splitlines() if line.strip()]


def current_branch(repo_root: Path) -> str:
    branch = run(["git", "branch", "--show-current"], cwd=repo_root).stdout.strip()
    if not branch:
        raise SystemExit("publish_release requires a named branch; detached HEAD is not supported")
    return branch


def tag_exists(repo_root: Path, tag_name: str, *, remote: str) -> dict[str, Any]:
    local = run(["git", "tag", "--list", tag_name], cwd=repo_root).stdout.strip() == tag_name
    tag_ref = f"refs/tags/{tag_name}"
    remote_result = run(["git", "ls-remote", "--tags", remote, tag_ref], cwd=repo_root)
    remote_tag_sha = _single_remote_object_id(remote_result.stdout, expected_ref=tag_ref)
    if remote_tag_sha:
        peeled_ref = f"{tag_ref}^{{}}"
        peeled_result = run(
            ["git", "ls-remote", "--tags", remote, peeled_ref],
            cwd=repo_root,
        )
        peeled_sha = _single_remote_object_id(peeled_result.stdout, expected_ref=peeled_ref)
        if peeled_sha:
            remote_tag_sha = peeled_sha
    return {"local": local, "remote": bool(remote_tag_sha), "remote_tag_sha": remote_tag_sha}


def backend_command(
    backend: dict[str, Any],
    op: str,
    default: list[str],
    **subs: str,
) -> list[str]:
    allowed = OP_PLACEHOLDERS.get(op)
    if allowed is None:
        raise SystemExit(
            f"backend_command({op}): unknown op; declare a placeholder allowlist in OP_PLACEHOLDERS"
        )
    extra_subs = sorted(set(subs) - allowed)
    if extra_subs:
        raise SystemExit(
            f"backend_command({op}): caller passed placeholders {extra_subs!r} "
            f"not in op's allowlist {sorted(allowed)!r}"
        )
    commands = backend.get("commands") or {}
    template = commands.get(op)
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise SystemExit(
                f"release_backend `{backend.get('id')}` did not declare a `{op}` command template"
            )
        template = default
    used = {match for part in template for match in _PLACEHOLDER_RE.findall(part)}
    unknown = sorted(used - allowed)
    if unknown:
        raise SystemExit(
            f"backend_command({op}): adapter template uses unknown placeholders {unknown!r}; "
            f"allowed for {op}: {sorted(allowed)!r}"
        )
    # `if "{" in part`, NOT `if subs and "{" in part`. The `subs and` guard was the measured
    # DRIFT from `issue_backend.resolve_op`, which owns this rule: with an empty `subs`, a
    # brace-bearing template passed through VERBATIM here and raised in the owner. Reachable
    # whenever every placeholder a template spells is in the op's allowlist but the caller
    # supplies none -- the command then runs with a literal `{tag}` in its argv instead of
    # failing, which on a release surface means publishing against a tag that does not exist.
    # Loud is correct, and it is what the owner already did.
    try:
        return [part.format(**subs) if "{" in part else part for part in template]
    except (KeyError, ValueError, IndexError) as exc:
        # The refusal TYPE is this module's policy, not the owner's: release helpers run as a
        # CLI whose callers expect a message and a status, so a raw `KeyError` from `format`
        # would surface as a traceback naming only the placeholder. The owner raises the raw
        # error for callers that handle it; both REFUSE, which is the part that must agree.
        raise SystemExit(
            f"backend_command({op}): template {template!r} could not be rendered with "
            f"{sorted(subs)!r}: {type(exc).__name__}: {exc}"
        ) from exc


def release_exists(repo_root: Path, tag_name: str, backend: dict[str, Any] | None = None) -> bool:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    command = backend_command(
        backend, "release_view", ["gh", "release", "view", "{tag}"], tag=tag_name
    )
    return run(command, cwd=repo_root, check=False).returncode == 0


def create_release(
    repo_root: Path, backend: dict[str, Any], *, tag_name: str, title: str, notes_file: Path | None
):
    release_command = backend_command(
        backend,
        "release_create",
        ["gh", "release", "create", "{tag}", "--verify-tag", "--title", "{title}"],
        tag=tag_name,
        title=title,
    )
    release_command.extend(
        ["--notes-file", str(notes_file.resolve())] if notes_file else ["--generate-notes"]
    )
    return run(release_command, cwd=repo_root)


def expected_github_release_url(
    repo_root: Path, backend: dict[str, Any], tag_name: str
) -> str | None:
    if backend.get("id", "gh") != "gh":
        return None
    result = run(
        ["gh", "repo", "view", "--json", "url", "--jq", ".url"], cwd=repo_root, check=False
    )
    if result.returncode != 0:
        return None
    repo_url = result.stdout.strip().rstrip("/")
    return f"{repo_url}/releases/tag/{tag_name}" if repo_url else None
