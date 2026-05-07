from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

MANIFEST_RELATIVE_PATH = Path(".agents/worktree-adapter.yaml")
SCHEMA_RELATIVE_PATH = Path("integrations/worktree/manifest.schema.json")
EXAMPLE_RELATIVE_PATH = Path("integrations/worktree/adapter.example.yaml")
CANONICAL_CHECK_IDS = ("git_common_dir", "hooks_path", "lefthook_shim", "husky_dir")
PASS = "pass"
FAIL = "fail"
SKIPPED = "skipped"
DEFAULT_DOCTOR_TIMEOUT_SECONDS = 10
DEFAULT_PREPARE_TIMEOUT_SECONDS = 600


@dataclass
class CheckResult:
    id: str
    status: str
    detail: str
    next_action: str | None = None
    source: str = "canonical"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommandResult:
    id: str
    argv: list[str]
    exit_code: int | None
    duration_ms: int
    stdout_tail: str
    stderr_tail: str
    timed_out: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ManifestState:
    found: bool
    path: str | None
    valid: bool
    errors: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "found": self.found,
            "path": self.path,
            "valid": self.valid,
            "errors": list(self.errors),
        }


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tail(text: str, *, max_chars: int = 2000) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def aggregate_status(results: Iterable[CheckResult]) -> str:
    saw_check = False
    for result in results:
        saw_check = True
        if result.status == FAIL:
            return FAIL
    if not saw_check:
        return PASS
    return PASS
