"""Portable support helpers for the issue critique observer.

This module keeps date grandfathering and delegation-contract resolution out of
the verdict reader.  They are policy/authorization helpers, not evidence
parsing, and keeping that boundary explicit makes both sides easier to test.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    from scripts.core import subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:
    _scripts_dir = next(
        (
            ancestor / "scripts"
            for ancestor in (Path(__file__).resolve(), *Path(__file__).resolve().parents)
            if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
        ),
        None,
    )
    if _scripts_dir is None:
        raise
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    import scripts.core.subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process

subprocess = _subprocess_guard.subprocess

OBSERVER_RULE_DATE = date(2026, 7, 5)
_DATE_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})")
_DATE_LINE_RE = re.compile(
    r"^\s*[-*]?\s*date\s*:\s*(?P<date>\d{4}-\d{2}-\d{2})",
    re.IGNORECASE | re.MULTILINE,
)
DELEGATION_CONTRACT_MARKERS = (
    "subagent delegation",
    "repo-mandated bounded fresh-eye subagent reviews are already delegated",
)


def artifact_observed_date(path: Path, text: str) -> date | None:
    """Read the artifact date from its body, then from its filename."""
    match = _DATE_LINE_RE.search(text) or _DATE_RE.match(Path(path).name)
    if match is None:
        return None
    try:
        return date.fromisoformat(match.group("date"))
    except ValueError:
        return None


def _path_is_tracked(root: Path, relative: str) -> bool:
    try:
        from scripts.core.repo_file_listing import RepoFileSnapshot
    except ModuleNotFoundError:
        from scripts.core.repo_file_listing import RepoFileSnapshot
    listed = RepoFileSnapshot(root).list_files(include_untracked=False)
    return listed is not None and (root / relative) in listed


def _tracked_before_rule(path: Path, repo_root: Path) -> bool:
    """Require committed pre-rule bytes before trusting an old self-date."""
    try:
        root = repo_root.resolve()
        candidate = path.resolve()
        relative = candidate.relative_to(root)
        if not _path_is_tracked(root, relative.as_posix()):
            return False
        result = run_process(
            ["git", "log", "-1", "--format=%cI", "--", relative.as_posix()],
            cwd=root,
            timeout_seconds=None,
        )
        if result.returncode != 0:
            return False
        committed = result.stdout.strip()[:10]
        if not committed or date.fromisoformat(committed) >= OBSERVER_RULE_DATE:
            return False
        committed_result = run_process(
            ["git", "show", f"HEAD:{relative.as_posix()}"],
            cwd=root,
            timeout_seconds=None,
        )
        if committed_result.returncode != 0:
            return False
        return candidate.read_bytes() == committed_result.stdout.encode("utf-8")
    except (OSError, ValueError):
        return False


def predates_typed_contract(path: Path, text: str, *, repo_root: Path | None = None) -> bool:
    """Whether an unchanged tracked artifact predates the typed contract."""
    observed = artifact_observed_date(path, text)
    if observed is None or observed >= OBSERVER_RULE_DATE:
        return False
    return repo_root is None or _tracked_before_rule(path, repo_root)


def _normalize_contract_text(text: str) -> str:
    """Flatten markup and whitespace while ignoring Markdown code examples."""
    kept: list[str] = []
    pending: list[str] = []
    opener: str | None = None
    indented_code = False
    for line in text.splitlines():
        leading = len(line) - len(line.lstrip(" "))
        if opener is None:
            if leading >= 4:
                indented_code = True
                continue
            if indented_code and not line.strip():
                continue
            indented_code = False
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if opener is None:
                opener = marker
                pending = []
                continue
            if marker[0] == opener[0] and len(marker) >= len(opener):
                opener = None
                pending = []
                continue
        if opener is None:
            kept.append(line)
        else:
            pending.append(line)
    kept.extend(pending)
    flattened = re.sub(r"[`*_]+", "", "\n".join(kept).lower())
    return re.sub(r"\s+", " ", flattened)


def _delegation_record_state(repo_root: Path) -> tuple[str | None, list[str] | None]:
    """Read the optional explicit delegation decision and its scope list."""
    path = Path(repo_root) / ".agents/subagent-delegation.json"
    if not path.is_file():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, None
    if not isinstance(data, dict):
        return None, None
    value = data.get("bounded_review_delegation")
    if not isinstance(value, str):
        return None, None
    decision = value.strip().lower()
    if decision not in ("granted", "declined"):
        return None, None
    scopes: list[str] | None = None
    if "scopes" in data:
        raw_scopes = data.get("scopes")
        if (
            not isinstance(raw_scopes, list)
            or not raw_scopes
            or not all(isinstance(scope, str) for scope in raw_scopes)
        ):
            return None, None
        scopes = [scope.strip().lower() for scope in raw_scopes]
    return decision, scopes


def _record_grants_scope(decision: str | None, scopes: list[str] | None, scope: str) -> bool:
    if decision != "granted":
        return False
    return scopes is None or scope.strip().lower() in scopes


def repo_requires_delegated_observer(repo_root: Path, *, scope: str = "issue") -> bool:
    """Whether the consuming repo authorizes bounded review for ``scope``."""
    record_decision, record_scopes = _delegation_record_state(repo_root)
    if record_decision == "declined":
        return False
    agents_path = Path(repo_root) / "AGENTS.md"
    if not agents_path.is_file():
        return _record_grants_scope(record_decision, record_scopes, scope)
    try:
        text = agents_path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return _record_grants_scope(record_decision, record_scopes, scope)
    if all(marker in _normalize_contract_text(text) for marker in DELEGATION_CONTRACT_MARKERS):
        return True
    return _record_grants_scope(record_decision, record_scopes, scope)
