#!/usr/bin/env python3
"""Support functions for the semantic critique review command."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class RunReviewError(ValueError):
    """A typed refusal before or during the convenience boundary."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


def find_shared_scripts(script_dir: Path) -> Path:
    """Locate the source or installed-plugin shared reviewer scripts."""
    for ancestor in (script_dir, *script_dir.parents):
        for candidate in (ancestor / "shared/scripts", ancestor / "skills/shared/scripts"):
            if (candidate / "run_reviewer_worker.py").is_file():
                return candidate
    raise RunReviewError("runtime-unavailable", "cannot locate Charness shared reviewer scripts")


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RunReviewError("runtime-unavailable", f"cannot load package helper: {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
        raise
    if previous is not None:
        sys.modules[name] = previous
    return module


def package_paths(script_dir: Path) -> dict[str, Path]:
    shared = find_shared_scripts(script_dir)
    schema_candidates = (
        shared.parent / "references/bounded-review-result.schema.json",
        shared.parent.parent / "shared/references/bounded-review-result.schema.json",
    )
    schema = next((path for path in schema_candidates if path.is_file()), None)
    if schema is None:
        raise RunReviewError("runtime-unavailable", "cannot locate canonical reviewer result schema")
    return {
        "runner": shared / "run_reviewer_worker.py",
        "capability": shared / "reviewer_capability.py",
        "lifecycle": shared / "reviewer_lifecycle.py",
        "schema": schema,
        "prepare": script_dir / "prepare_packet.py",
        "verify_packet": script_dir / "verify_packet.py",
        "resolve_adapter": script_dir / "resolve_adapter.py",
    }


def load_runtime(paths: dict[str, Path]) -> tuple[Any, Any]:
    lifecycle = load_module(paths["lifecycle"], "charness_run_review_lifecycle")
    capability = load_module(paths["capability"], "charness_run_review_capability")
    return lifecycle, capability


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_yaml(path: Path, payload: object) -> None:
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def emit(payload: dict[str, Any]) -> None:
    print(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), end="")


def yaml_payload(raw: str, *, label: str) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(raw) if raw.strip() else None
    except yaml.YAMLError as exc:
        raise RunReviewError("carrier-invalid", f"{label} did not emit valid YAML: {exc}") from exc
    if not isinstance(payload, dict):
        raise RunReviewError("carrier-invalid", f"{label} did not emit a YAML mapping")
    return payload


def repo_path(
    root: Path,
    value: str,
    *,
    label: str,
    require_file: bool = False,
    allow_symlink: bool = False,
) -> Path:
    """Resolve a repo-relative path this runner will OPEN, or (with
    `allow_symlink`) one it merely declares.

    The symlink refusal is right for files the runner reads or writes — a packet
    or manifest behind a link could be swapped underneath it. It is wrong for a
    DECLARED reviewed path, whose symlink policy belongs to
    `scripts/reviewed_input_identity.py`: that owner binds a current pointer by
    link payload and refuses every other symlink. Applying this rule there made
    the runner refuse inputs the identity had just been taught to bind, which is
    the same two-owners-one-question shape the identity repairs were about.

    The repo-root boundary below still applies either way, and `.resolve()`
    follows the link, so a symlink escaping the root is still refused.
    """
    raw = Path(value).expanduser()
    if raw.is_absolute() or ".." in raw.parts:
        raise RunReviewError("path-invalid", f"{label} must be repository-relative: {value}")
    lexical = root / raw
    if lexical.is_symlink() and not allow_symlink:
        raise RunReviewError("path-invalid", f"{label} must not be a symlink: {value}")
    candidate = lexical.resolve(strict=False)
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise RunReviewError("path-invalid", f"{label} resolves outside --repo-root: {value}") from exc
    if require_file and not candidate.is_file():
        raise RunReviewError("path-missing", f"{label} does not point to a file: {value}")
    # An allowed symlink is returned UNRESOLVED. `.resolve()` follows the link, so
    # returning `candidate` renamed a declared `latest.md` to whatever record it
    # points at -- and a declared set carrying the target instead of the pointer
    # no longer matches the range that listed the pointer. The resolved form is
    # still what the boundary check above ran against.
    return lexical if lexical.is_symlink() else candidate


def relative(root: Path, path: Path) -> str:
    """Repo-relative spelling of a path, WITHOUT following a symlink.

    `.resolve()` here renamed a declared `latest.md` to whatever record it points
    at, so the declared set carried the target while the range carried the
    pointer and the two could never match. `repo_path` has already proven the
    path lies inside the root, so resolving again buys nothing and costs the
    caller's own name for it.
    """
    absolute = path if path.is_absolute() else root / path
    try:
        return absolute.relative_to(root.resolve()).as_posix()
    except ValueError:
        return absolute.resolve().relative_to(root.resolve()).as_posix()


def load_goal_lineage(root: Path, path_value: str | None, *, reason: str) -> dict[str, Any]:
    """Load one full evidence identity, or record an explicit standalone run."""
    candidates: list[Path] = [root / "scripts" / "goal_lineage.py"]
    here = Path(__file__).resolve()
    candidates.extend(ancestor / "scripts" / "goal_lineage.py" for ancestor in (here, *here.parents))
    lineage_path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if lineage_path is None:
        raise RunReviewError("runtime-unavailable", "scripts/goal_lineage.py is not available")
    module = load_module(lineage_path, "charness_run_review_goal_lineage")
    try:
        if path_value is None:
            return module.not_goal_bound_lineage(reason)
        loaded = module.load_goal_lineage_file(root, Path(path_value))
        return module.require_goal_execution_identity(loaded)
    except module.LineageError as exc:
        raise RunReviewError("invalid-lineage", str(exc), details=exc.as_dict()) from exc


ATTEMPT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def attempt_id(value: str | None) -> str:
    candidate = value or f"review-{datetime.now().strftime('%Y%m%dT%H%M%SZ')}-{os.getpid()}"
    if not ATTEMPT_RE.fullmatch(candidate):
        raise RunReviewError("input-invalid", "attempt-id must be a short path-safe identifier")
    return candidate


def run_command(command: list[str], *, root: Path, timeout: float = 60.0) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunReviewError("runner-invalid", f"command could not complete: {' '.join(command)}: {exc}") from exc
    return result.returncode, result.stdout, result.stderr


def resolve_adapter(root: Path, resolver: Path) -> dict[str, Any]:
    code, stdout, stderr = run_command([sys.executable, str(resolver), "--repo-root", str(root)], root=root)
    payload = yaml_payload(stdout, label="critique adapter resolver")
    if code != 0 or payload.get("valid") is not True:
        raise RunReviewError("adapter-invalid", "critique adapter is invalid", details={"adapter": payload, "stderr": stderr})
    return payload


def select_backend(adapter: dict[str, Any], requested: str | None, *, dry_run: bool) -> tuple[str | None, int]:
    data = adapter.get("data")
    runner = data.get("reviewer_runner") if isinstance(data, dict) else None
    runner = runner if isinstance(runner, dict) else {}
    if runner.get("mode", "file-backed-worker") != "file-backed-worker":
        raise RunReviewError("typed-subagent-selected", "adapter selected typed-subagent; use the host spawn branch")
    configured = runner.get("backend", "host-defaulted")
    if requested is not None and configured != "host-defaulted" and requested != configured:
        raise RunReviewError("runner-invalid", f"adapter backend {configured!r} is authoritative")
    if configured != "host-defaulted":
        backend = requested or configured
    elif requested:
        backend = requested
    elif dry_run:
        backend = None
    elif shutil.which("codex"):
        backend = "codex_exec"
    elif shutil.which("claude"):
        backend = "claude_p"
    else:
        raise RunReviewError("backend-unavailable", "host-defaulted adapter has no codex or claude executable")
    timeout = runner.get("timeout_seconds", 900)
    if type(timeout) is not int or timeout <= 0:
        raise RunReviewError("adapter-invalid", "reviewer_runner.timeout_seconds must be a positive integer")
    return backend, timeout


def new_run_dir(root: Path, attempt: str) -> Path:
    run_dir = (root / ".charness" / f"reviewer-round-{attempt}").resolve()
    try:
        run_dir.relative_to(root.resolve())
    except ValueError as exc:
        raise RunReviewError("path-invalid", "derived reviewer run directory escaped repository root") from exc
    if run_dir.exists() or run_dir.is_symlink():
        raise RunReviewError("stale-artifact-refused", f"refusing to overwrite existing reviewer run: {run_dir}")
    run_dir.mkdir(parents=True)
    return run_dir


def stop_group(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        if os.name == "posix":
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def install_runner_handlers(process: subprocess.Popen[Any]) -> dict[int, Any]:
    """Make an interrupted wrapper reap its canonical runner process group."""
    previous: dict[int, Any] = {}

    def interrupt(_signum: int, _frame: Any) -> None:
        raise KeyboardInterrupt

    for signum in (signal.SIGTERM, signal.SIGINT):
        try:
            previous[signum] = signal.signal(signum, interrupt)
        except (ValueError, OSError):
            continue
    return previous


def restore_runner_handlers(previous: dict[int, Any]) -> None:
    for signum, handler in previous.items():
        try:
            signal.signal(signum, handler)
        except (ValueError, OSError):
            pass


def run_runner(
    command: list[str], *, root: Path, stdout_path: Path, stderr_path: Path, timeout: int
) -> tuple[int | None, str, bool, str | None]:
    grace = max(2.0, min(30.0, timeout * 0.25))
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(
                command,
                cwd=root,
                stdout=stdout,
                stderr=stderr,
                start_new_session=(os.name == "posix"),
                creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0,
            )
            previous_handlers = install_runner_handlers(process)
            try:
                returncode = process.wait(timeout=timeout + grace)
                return returncode, "runner-completed", True, None
            except subprocess.TimeoutExpired:
                stop_group(process)
                return 124, "runner-timeout", True, f"canonical runner exceeded {timeout + grace:g} seconds"
            except KeyboardInterrupt:
                stop_group(process)
                return 130, "runner-interrupted", True, "canonical runner interrupted; worker group terminated"
            finally:
                restore_runner_handlers(previous_handlers)
    except OSError as exc:
        return None, "runner-invalid", False, str(exc)


def load_mapping(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    return payload if isinstance(payload, dict) else None


def compare_report_stream(stream_path: Path, report_path: Path) -> dict[str, Any]:
    """Record whether stdout and the durable report carry the same mapping."""
    stream = load_mapping(stream_path)
    report = load_mapping(report_path)
    if stream is None or report is None:
        reason = "runner stdout or canonical report is missing or unreadable"
        consistent = False
    elif stream != report:
        reason = "runner stdout differs from the canonical report carrier"
        consistent = False
    else:
        reason = None
        consistent = True
    return {
        "consistent": consistent,
        "reason": reason,
        "runner_stdout_sha256": sha256(stream_path) if stream_path.is_file() else None,
        "canonical_report_sha256": sha256(report_path) if report_path.is_file() else None,
    }


def classify_runner_output(
    path: Path, *, returncode: int | None, status: str, started: bool, error: str | None
) -> tuple[int | None, str, bool, str | None]:
    payload = load_mapping(path)
    if isinstance(payload, dict) and payload.get("status") == "runner-invalid":
        return returncode, "runner-invalid", False, str(payload.get("error") or error or "canonical runner refused the run")
    return returncode, status, started, error
