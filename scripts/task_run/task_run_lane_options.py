"""Lane launch options: standing rules by reference and writable grants.

Standing material (lane rules, decision ledgers) is passed by reference so
scope evidence keeps reading only the task prompt, and host-state writable
grants stay narrow, recorded, and refused for executors that cannot honor
them. Both are validated before any launch work; dry-run reports the same
scope refusal the real launch would end on.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run.task_run_contract import TaskRunError  # noqa: E402

#: The standing-rules prompt section names this sentence; scope evidence
#: never sees it because rules files are listed here, never inlined.
RULES_SECTION_TITLE = "Read these in full before any edit; they bind this lane:"


def resolve_rules_files(raw: Sequence[str | Path]) -> list[str]:
    """Resolve standing-rule references to absolute file paths.

    The executor reads each file by reference; the content is never merged
    into the task prompt, so scope evidence keeps reading only the prompt.
    """
    resolved: list[str] = []
    for entry in raw or ():
        path = Path(str(entry)).expanduser().resolve()
        if not path.is_file():
            raise TaskRunError(f"--rules-file is not a file: {entry}")
        resolved.append(str(path))
    return resolved


def standing_rules_section(rules_files: Sequence[str | Path]) -> str | None:
    """Render the by-reference rules section, or None when no files are given."""
    listed = [str(path) for path in rules_files or ()]
    if not listed:
        return None
    return RULES_SECTION_TITLE + "\n" + "\n".join(f"- {path}" for path in listed)


def append_rules_section(
    injections: list[str], rules_files: Sequence[str | Path]
) -> None:
    """Append the by-reference rules section when files are given."""
    section = standing_rules_section(rules_files)
    if section is not None:
        injections.append(section)


def apply_granted_writable(
    writable_dirs: list[Path],
    payload: dict[str, Any],
    granted: Sequence[str | Path],
) -> None:
    """Record explicit grants on the receipt and join them to the grant list."""
    granted_paths = [str(path) for path in granted or ()]
    payload["granted_writable_dirs"] = granted_paths
    writable_dirs.extend(Path(path) for path in granted_paths)


def _grant_covers(path: Path, ancestor: Path) -> bool:
    return path == ancestor or ancestor in path.parents


def resolve_granted_writable(
    repo_root: Path,
    raw: Sequence[str | Path],
    *,
    executor: str | None,
) -> list[str]:
    """Validate per-lane codex `--add-dir` grants before any launch work.

    Muse roots a single `--workspace` and takes no extra grant, so a lane
    that may fall through to muse refuses the flag loudly instead of
    silently dropping it. Grants covering the repo root, $HOME, or `/`
    are refused: the flag must stay a narrow host-state grant, never an
    escape hatch.
    """
    entries = [str(entry) for entry in raw or ()]
    if entries and executor is not None and "muse" in [
        part.strip() for part in executor.split(",")
    ]:
        raise TaskRunError(
            "--grant-writable needs the codex executor; muse roots a single "
            "--workspace and takes no extra writable grant (#814)"
        )
    home = Path.home()
    resolved: list[str] = []
    for entry in entries:
        candidate = Path(entry).expanduser()
        if not candidate.is_absolute():
            raise TaskRunError(f"--grant-writable must be an absolute directory: {entry}")
        path = candidate.resolve()
        if not path.is_dir():
            raise TaskRunError(f"--grant-writable is not a directory: {entry}")
        if path == Path("/"):
            raise TaskRunError("--grant-writable must not grant /")
        if _grant_covers(home, path):
            raise TaskRunError(f"--grant-writable must not cover $HOME: {entry}")
        if _grant_covers(repo_root, path):
            raise TaskRunError(f"--grant-writable must not cover the repo root: {entry}")
        resolved.append(str(path))
    return resolved


def resolve_launch_options(
    resolved: dict[str, Any],
    repo_root: Path,
    rules_files: Sequence[str | Path],
    grant_writable: Sequence[str | Path],
    *,
    executor: str | None,
) -> None:
    """Validate lane options before any launch work and stash them on `resolved`.

    `resolved` is the single channel downstream preparation reads: prompt
    shaping, sandbox grants, and the executor-fallback context all follow
    these keys, so no parallel parameter plumbing can drift apart.
    """
    resolved["rules_files"] = resolve_rules_files(rules_files)
    resolved["granted_writable_dirs"] = resolve_granted_writable(
        repo_root, grant_writable, executor=executor
    )


def record_launch_options(payload: dict[str, Any], resolved: Mapping[str, Any]) -> None:
    """Record launch options and the scope preflight on the receipt."""
    payload["scope_preflight"] = resolved["scope_preflight"]
    payload["rules_files"] = resolved["rules_files"]
    payload["granted_writable_dirs"] = resolved["granted_writable_dirs"]


def apply_dry_run_refusal(
    payload: dict[str, Any], scope_preflight: Mapping[str, Any]
) -> bool:
    """Deny a dry-run on the would-touch refusal; True when refused."""
    refusal = dry_run_scope_refusal(scope_preflight)
    if refusal is None:
        return False
    payload["status"] = "premise-blocked"
    payload["error"] = refusal["error"]
    payload["next_step"] = refusal["next_step"]
    return True


def plan_dry_run(
    payload: dict[str, Any],
    resolved: Mapping[str, Any],
    resolved_executor: str,
    resolved_target: Path,
    pass_value: str,
) -> None:
    """Fill a dry-run receipt: refusal wins, else the planned lane.

    The whole dry-run outcome lives here so the run orchestrator keeps one
    branch for \"plan only, never create\".
    """
    if apply_dry_run_refusal(payload, resolved["scope_preflight"]):
        return
    payload["status"] = pass_value
    payload["approval_eligibility"] = "not-applicable"
    payload["next_step"] = (
        "Re-run without --dry-run to create the named worktree and execute "
        f"{resolved_executor}."
    )
    payload["actions"] = [
        {"id": "create-worktree", "status": "planned"},
        {
            "id": f"{resolved_executor}-exec",
            "status": "planned",
            "cwd": str(resolved_target),
        },
    ]


def dry_run_scope_refusal(
    scope_preflight: Mapping[str, Any],
) -> dict[str, str] | None:
    """Report the would-touch refusal a real launch would end on.

    `--dry-run` must exit with the launch's own refusal code on the same
    findings, so no caller needs a private preflight probe.
    """
    outside = sorted(
        {
            finding["path"]
            for finding in scope_preflight.get("would_touch_outside_declared", [])
            if isinstance(finding, Mapping) and finding.get("path")
        }
    )
    if not outside:
        return None
    refusal = (
        "scope mismatch: brief evidence names repository paths outside "
        "declared --scope: " + ", ".join(outside)
    )
    return {
        "error": refusal,
        "next_step": (
            refusal + "; extend --scope or narrow the prompt, then re-run --dry-run. "
            "No worktree was created."
        ),
    }
