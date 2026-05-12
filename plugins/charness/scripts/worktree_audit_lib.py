from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_doctor_lib = import_repo_module(__file__, "scripts.worktree_doctor_lib")

PASS = "pass"
WARN = "warn"
FAIL = "fail"

CLASSIFICATION_PRIMARY = "primary"
CLASSIFICATION_ACTIVE = "active"
CLASSIFICATION_PRUNABLE = "prunable"
CLASSIFICATION_STALE = "stale"

DEFAULT_STALE_DAYS = 14


def _run_git_worktree_list(repo_root: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def parse_porcelain(text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            if current:
                entries.append(current)
                current = {}
            current["worktree"] = line[len("worktree ") :]
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD ") :]
        elif line.startswith("branch "):
            current["branch"] = line[len("branch ") :]
        elif line == "detached":
            current["detached"] = True
        elif line == "prunable":
            current["prunable"] = True
            current.setdefault("prunable_reason", "")
        elif line.startswith("prunable "):
            current["prunable"] = True
            current["prunable_reason"] = line[len("prunable ") :]
        elif line == "bare":
            current["bare"] = True
        elif line == "locked":
            current["locked"] = True
        elif line.startswith("locked "):
            current["locked"] = True
            current["locked_reason"] = line[len("locked ") :]
    if current:
        entries.append(current)
    return entries


def _resolve_age_days(path: Path, now: datetime) -> float | None:
    try:
        mtime = path.stat().st_mtime
    except (FileNotFoundError, PermissionError):
        return None
    moment = datetime.fromtimestamp(mtime, tz=timezone.utc)
    return (now - moment).total_seconds() / 86400.0


def classify(entry: dict[str, Any], *, primary_path: Path, stale_days: int, now: datetime) -> dict[str, Any]:
    path = Path(entry["worktree"])
    classification: str
    reasons: list[str] = []
    age_days = _resolve_age_days(path, now)

    if path == primary_path:
        classification = CLASSIFICATION_PRIMARY
    elif entry.get("prunable"):
        classification = CLASSIFICATION_PRUNABLE
        reason = entry.get("prunable_reason") or "git reports the worktree directory is missing"
        reasons.append(reason)
    elif entry.get("locked"):
        classification = CLASSIFICATION_ACTIVE
        lock_reason = entry.get("locked_reason")
        reasons.append(f"locked: {lock_reason}" if lock_reason else "locked")
    elif entry.get("detached") and age_days is not None and age_days >= stale_days:
        classification = CLASSIFICATION_STALE
        reasons.append(f"detached HEAD older than {stale_days} days (age={age_days:.1f}d)")
    else:
        classification = CLASSIFICATION_ACTIVE

    return {
        "path": str(path),
        "head": entry.get("head"),
        "branch": entry.get("branch"),
        "detached": bool(entry.get("detached")),
        "locked": bool(entry.get("locked")),
        "prunable": bool(entry.get("prunable")),
        "age_days": age_days,
        "classification": classification,
        "reasons": reasons,
    }


def _doctor_summary(path: Path) -> dict[str, Any]:
    payload = _doctor_lib.run_doctor(path)
    failed_checks = [
        {
            "id": check.get("id"),
            "detail": check.get("detail"),
            "next_action": check.get("next_action"),
            "source": check.get("source"),
        }
        for check in payload.get("checks", [])
        if check.get("status") == FAIL
    ]
    return {
        "status": payload.get("status"),
        "checked_at": payload.get("checked_at"),
        "manifest": payload.get("manifest"),
        "check_count": len(payload.get("checks", [])),
        "failed_checks": failed_checks,
        "next_action": payload.get("next_action"),
    }


def _attach_doctor_summaries(entries: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"pass": 0, "fail": 0, "skipped": 0}
    for entry in entries:
        path = Path(entry["path"])
        if entry["classification"] == CLASSIFICATION_PRUNABLE or not path.exists():
            entry["doctor"] = {
                "status": "skipped",
                "reason": "worktree path is missing or prunable",
            }
            summary["skipped"] += 1
            continue
        doctor = _doctor_summary(path)
        entry["doctor"] = doctor
        if doctor.get("status") == FAIL:
            summary["fail"] += 1
        elif doctor.get("status") == PASS:
            summary["pass"] += 1
        else:
            summary["skipped"] += 1
    return summary


def _git_common_dir(repo_root: Path) -> Path | None:
    proc = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    common = Path(proc.stdout.strip())
    if not common.is_absolute():
        common = (repo_root / common).resolve()
    return common.resolve()


def _primary_worktree_path(repo_root: Path, entries: list[dict[str, Any]]) -> Path:
    common = _git_common_dir(repo_root)
    if common is None:
        return repo_root.resolve()
    if common.name == ".git":
        return common.parent.resolve()
    for entry in entries:
        path = Path(entry["worktree"]).resolve()
        git_target = path / ".git"
        if git_target.is_dir() and git_target.resolve() == common:
            return path
        if git_target.is_file():
            try:
                content = git_target.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if content.startswith("gitdir:"):
                gitdir_value = content[len("gitdir:") :].strip()
                gitdir_path = Path(gitdir_value)
                if not gitdir_path.is_absolute():
                    gitdir_path = (path / gitdir_path).resolve()
                else:
                    gitdir_path = gitdir_path.resolve()
                if common in gitdir_path.parents and gitdir_path.parent.name == "worktrees":
                    continue
                if gitdir_path == common:
                    return path
    return repo_root.resolve()


def run_audit(repo_root: Path, *, stale_days: int = DEFAULT_STALE_DAYS, include_doctor: bool = False) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    rc, stdout, stderr = _run_git_worktree_list(repo_root)
    if rc != 0:
        return {
            "status": FAIL,
            "repo_root": str(repo_root),
            "error": stderr.strip() or "git worktree list failed",
            "entries": [],
            "summary": {"primary": 0, "active": 0, "prunable": 0, "stale": 0, "total": 0},
        }

    raw_entries = parse_porcelain(stdout)
    primary_path = _primary_worktree_path(repo_root, raw_entries)
    now = datetime.now(tz=timezone.utc)

    classified = [classify(entry, primary_path=primary_path, stale_days=stale_days, now=now) for entry in raw_entries]
    doctor_summary = _attach_doctor_summaries(classified) if include_doctor else None

    summary = {
        "primary": sum(1 for c in classified if c["classification"] == CLASSIFICATION_PRIMARY),
        "active": sum(1 for c in classified if c["classification"] == CLASSIFICATION_ACTIVE),
        "prunable": sum(1 for c in classified if c["classification"] == CLASSIFICATION_PRUNABLE),
        "stale": sum(1 for c in classified if c["classification"] == CLASSIFICATION_STALE),
        "total": len(classified),
    }

    doctor_failures = doctor_summary["fail"] if doctor_summary is not None else 0
    if summary["prunable"] > 0 or summary["stale"] > 0 or doctor_failures > 0:
        status = WARN
    else:
        status = PASS

    next_actions: list[str] = []
    if summary["prunable"] > 0:
        next_actions.append(
            "Run `charness worktree audit --prune` to drop prunable git metadata."
        )
    elif summary["stale"] > 0:
        next_actions.append(
            "Inspect stale worktrees and remove them with `git worktree remove --force <path>` if no longer needed."
        )
    if doctor_failures > 0:
        next_actions.append(
            "Inspect entries with `doctor.status=fail`; run `charness worktree prepare --repo-root <path>` where preparation is appropriate."
        )
    next_action = " ".join(next_actions) if next_actions else None

    return {
        "status": status,
        "repo_root": str(repo_root),
        "primary_worktree": str(primary_path),
        "stale_days": stale_days,
        "doctor_enabled": include_doctor,
        "entries": classified,
        "summary": summary,
        "doctor_summary": doctor_summary,
        "next_action": next_action,
    }


def run_prune(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    before = run_audit(repo_root)
    proc = subprocess.run(
        ["git", "worktree", "prune", "--verbose"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    after = run_audit(repo_root)
    delta = max(0, before["summary"].get("prunable", 0) - after["summary"].get("prunable", 0))
    parsed_names: list[str] = []
    for line in proc.stdout.splitlines():
        m = re.match(r"^Removing worktrees/(?P<name>[^:]+):", line)
        if m:
            parsed_names.append(m.group("name"))
    return {
        "status": PASS if proc.returncode == 0 else FAIL,
        "repo_root": str(repo_root),
        "pruned_count": delta,
        "pruned": parsed_names,
        "remaining_after_prune": after["summary"],
        "stderr": proc.stderr.strip() if proc.returncode != 0 else "",
    }


def render_audit_text(payload: dict[str, Any]) -> str:
    if payload.get("error"):
        return f"audit failed: {payload['error']}"
    summary = payload["summary"]
    lines = [
        f"repo: {payload['repo_root']}",
        f"primary: {payload['primary_worktree']}",
        (
            f"summary: {summary['total']} total "
            f"(primary={summary['primary']}, active={summary['active']}, "
            f"prunable={summary['prunable']}, stale={summary['stale']})"
        ),
    ]
    if payload.get("doctor_enabled"):
        doctor = payload.get("doctor_summary") or {}
        lines.append(
            "readiness: "
            f"pass={doctor.get('pass', 0)}, fail={doctor.get('fail', 0)}, skipped={doctor.get('skipped', 0)}"
        )
    for entry in payload["entries"]:
        cls = entry["classification"]
        doctor = entry.get("doctor") or {}
        if cls == CLASSIFICATION_PRIMARY and doctor.get("status") != FAIL:
            continue
        age_part = f" age={entry['age_days']:.1f}d" if entry.get("age_days") is not None else ""
        reasons = "; ".join(entry["reasons"]) if entry["reasons"] else ""
        if doctor:
            doctor_status = doctor.get("status")
            doctor_part = f" readiness={doctor_status}"
            if doctor_status == FAIL and doctor.get("next_action"):
                doctor_part += f" next={doctor['next_action']}"
            reasons = "; ".join(part for part in (reasons, doctor_part.strip()) if part)
        suffix = f" — {reasons}" if reasons else ""
        lines.append(f"  [{cls}] {entry['path']}{age_part}{suffix}")
    if payload.get("next_action"):
        lines.append(f"next: {payload['next_action']}")
    return "\n".join(lines)


def render_prune_text(payload: dict[str, Any]) -> str:
    if payload["status"] != PASS:
        return f"prune failed: {payload.get('stderr', 'unknown error')}"
    if payload["pruned_count"] == 0:
        return "no prunable worktrees"
    lines = [f"pruned {payload['pruned_count']} worktree metadata entries:"]
    lines.extend(f"  - {name}" for name in payload["pruned"])
    return "\n".join(lines)


def emit_payload(payload: dict[str, Any], *, json_mode: bool, renderer) -> None:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(renderer(payload))
