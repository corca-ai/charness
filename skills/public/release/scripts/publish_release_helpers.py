from __future__ import annotations

import re
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.subprocess_guard import (
        heartbeat_interval_from_env,
        run_monitored_phase,
        run_process,
    )
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from subprocess_guard import heartbeat_interval_from_env, run_monitored_phase, run_process

RELEASE_VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"tag"})
RELEASE_CREATE_PLACEHOLDERS: frozenset[str] = frozenset({"tag", "title"})

_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")
SEMVER_TAG_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")

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
_RELEASE_DELTA = runpy.run_path(str(Path(__file__).with_name("release_delta.py")))
# Read from the module that WRITES the field, never re-spelled here: the two readers of
# `release_observer.path` disagreed about `None` once already.
observer_path = runpy.run_path(str(Path(__file__).with_name("release_observer.py")))[
    "observer_path"
]
collect_release_delta = _RELEASE_DELTA["collect_release_delta"]
path_list_sha256 = _RELEASE_DELTA["path_list_sha256"]
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


def _semver_tuple(version: str) -> tuple[int, int, int] | None:
    tag = version if version.startswith("v") else f"v{version}"
    match = SEMVER_TAG_RE.fullmatch(tag)
    if match is None:
        return None
    return tuple(int(match.group(name)) for name in ("major", "minor", "patch"))


def _tag_version(tag_ref: str) -> str | None:
    tag = tag_ref.rsplit("/", 1)[-1]
    return tag.removeprefix("v") if SEMVER_TAG_RE.fullmatch(tag) else None


def _release_tag_versions(repo_root: Path, *, remote: str) -> set[str]:
    versions: set[str] = set()
    local = run(["git", "tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"], cwd=repo_root, check=False)
    if local.returncode != 0:
        raise SystemExit(
            "release tag discovery failed while resolving previous release version\n"
            "source: local tags\n"
            f"command: git tag --list v[0-9]*.[0-9]*.[0-9]*\nexit_code: {local.returncode}\n"
            f"STDOUT:\n{local.stdout}\nSTDERR:\n{local.stderr}"
        )
    versions.update(
        filter(None, (_tag_version(line.strip()) for line in local.stdout.splitlines()))
    )
    remote_result = run(
        ["git", "ls-remote", "--tags", remote, "refs/tags/v[0-9]*"], cwd=repo_root, check=False
    )
    if remote_result.returncode != 0:
        raise SystemExit(
            "release tag discovery failed while resolving previous release version\n"
            "source: remote tags\n"
            f"command: git ls-remote --tags {remote} refs/tags/v[0-9]*\nexit_code: {remote_result.returncode}\n"
            f"STDOUT:\n{remote_result.stdout}\nSTDERR:\n{remote_result.stderr}"
        )
    for line in remote_result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and not parts[1].endswith("^{}"):
            version = _tag_version(parts[1])
            if version:
                versions.add(version)
    return versions


def latest_previous_release_version(
    repo_root: Path, *, target_version: str, remote: str
) -> str | None:
    target = _semver_tuple(target_version)
    if target is None:
        return None
    candidates: list[tuple[tuple[int, int, int], str]] = []
    for version in _release_tag_versions(repo_root, remote=remote):
        parsed = _semver_tuple(version)
        if parsed is not None and parsed < target:
            candidates.append((parsed, version))
    return max(candidates)[1] if candidates else None


def release_previous_version(
    repo_root: Path,
    publish_current: bool,
    current_version: str,
    target_version: str,
    remote: str,
) -> str:
    if not publish_current:
        return current_version
    return (
        latest_previous_release_version(repo_root, target_version=target_version, remote=remote)
        or current_version
    )


def ensure_release_target_available(
    repo_root: Path, *, tag_name: str, remote: str, backend: dict[str, Any]
) -> None:
    tag_state = tag_exists(repo_root, tag_name, remote=remote)
    if tag_state["local"] or tag_state["remote"]:
        raise SystemExit(f"tag `{tag_name}` already exists locally or on `{remote}`")
    if release_exists(repo_root, tag_name, backend):
        raise SystemExit(f"GitHub release `{tag_name}` already exists")


def changed_paths(repo_root: Path) -> list[str]:
    return [line[3:] for line in git_status(repo_root) if len(line) >= 4]


def _release_base_ref(
    repo_root: Path,
    *,
    previous_version: str | None,
    remote: str,
    branch: str,
) -> str:
    if previous_version:
        tag_ref = f"refs/tags/v{previous_version}"
        tag_result = run(
            ["git", "rev-parse", "--verify", "--quiet", tag_ref],
            cwd=repo_root,
            check=False,
        )
        if tag_result.returncode == 0:
            return tag_ref
        remote_tag_result = run(
            ["git", "ls-remote", "--tags", remote, tag_ref],
            cwd=repo_root,
            check=False,
        )
        if remote_tag_result.returncode != 0:
            raise SystemExit(
                "release base ref lookup failed while computing unreleased paths\n"
                f"tag_ref: {tag_ref}\n"
                f"command: git ls-remote --tags {remote} {tag_ref}\n"
                f"exit_code: {remote_tag_result.returncode}\n"
                f"STDOUT:\n{remote_tag_result.stdout}\n"
                f"STDERR:\n{remote_tag_result.stderr}"
            )
        if remote_tag_result.returncode == 0 and remote_tag_result.stdout.strip():
            fetch_result = run(
                ["git", "fetch", "--quiet", remote, f"{tag_ref}:{tag_ref}"],
                cwd=repo_root,
                check=False,
            )
            if fetch_result.returncode == 0:
                return tag_ref
            raise SystemExit(
                "release base ref fetch failed while computing unreleased paths\n"
                f"tag_ref: {tag_ref}\n"
                f"command: git fetch --quiet {remote} {tag_ref}:{tag_ref}\n"
                f"exit_code: {fetch_result.returncode}\n"
                f"STDOUT:\n{fetch_result.stdout}\n"
                f"STDERR:\n{fetch_result.stderr}"
            )
    return f"{remote}/{branch}"


def unreleased_paths(
    repo_root: Path,
    *,
    remote: str,
    branch: str,
    previous_version: str | None = None,
) -> list[str]:
    return unreleased_scope(
        repo_root,
        remote=remote,
        branch=branch,
        previous_version=previous_version,
    )["changed_paths"]


def unreleased_scope(
    repo_root: Path,
    *,
    remote: str,
    branch: str,
    previous_version: str | None = None,
) -> dict[str, Any]:
    base_ref = _release_base_ref(
        repo_root,
        previous_version=previous_version,
        remote=remote,
        branch=branch,
    )
    try:
        delta = collect_release_delta(repo_root, base_ref)
    except ValueError as exc:
        raise SystemExit(
            "release diff failed while computing unreleased paths\n"
            f"base_ref: {base_ref}\n"
            f"error: {exc}"
        ) from exc
    return {
        "base_ref": base_ref,
        **delta,
    }


def amend_fresh_checkout_artifact(
    repo_root: Path,
    *,
    write_artifact,
    fresh_checkout_payload: dict[str, Any],
    release_url: str | None,
    artifact_relpath: str,
    tag_name: str,
    notes_file: Path | None,
    run_narrative_audit,
    run_command=run,
) -> None:
    write_artifact(fresh_checkout_payload=fresh_checkout_payload, release_url=release_url)
    run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    run_command(["git", "add", artifact_relpath], cwd=repo_root)
    run_command(["git", "commit", "--amend", "--no-edit"], cwd=repo_root)


def commit_post_publish_artifact(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    run_command=run,
) -> None:
    write_artifact(
        fresh_checkout_payload=fresh_checkout_payload,
        release_url=payload.get("release_url") or expected_release_url,
        issue_closeout=payload.get("issue_closeout"),
    )
    observer = observer_path(payload)
    tracked_paths = [artifact_relpath, *([observer] if observer else [])]
    diff_result = run_command(
        ["git", "diff", "--quiet", "--", *tracked_paths], cwd=repo_root, check=False
    )
    if diff_result.returncode == 0 and observer:
        untracked = run_command(
            ["git", "ls-files", "--error-unmatch", observer], cwd=repo_root, check=False
        )
        if untracked.returncode != 0:
            diff_result = untracked
    if diff_result.returncode == 0:
        return
    run_command(["git", "add", *tracked_paths], cwd=repo_root)
    run_command(
        ["git", "commit", "-m", f"Record release verification for {payload['tag_name']}"],
        cwd=repo_root,
    )
    run_command(["git", "push", remote, branch], cwd=repo_root)
    payload["post_publish_artifact_commit_sha"] = run_command(
        ["git", "rev-parse", "HEAD"], cwd=repo_root
    ).stdout.strip()
