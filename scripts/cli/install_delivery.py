"""Install/update delivery machinery."""

from __future__ import annotations

import json
import select
import subprocess
import time
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    PACKAGE_ID,
    CharnessError,
    default_install_state_path,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    now_iso,
)
from scripts.cli.common import (  # noqa: E402
    default_host_state_path,
)
from scripts.cli.tool_response import (  # noqa: E402
    _compact_mapping,
)


def repo_candidate_markers() -> tuple[Path, ...]:
    return (
        Path(".git"),
        Path("README.md"),
        Path("AGENTS.md"),
        Path("CLAUDE.md"),
        Path(".agents"),
        Path("docs"),
        Path("skills"),
        Path("pyproject.toml"),
        Path("package.json"),
        Path("go.mod"),
        Path("Cargo.toml"),
    )


def looks_like_repo_root(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    return any(
        (path / marker).exists() or (path / marker).is_symlink()
        for marker in repo_candidate_markers()
    )


def write_install_state(home_root: Path, *, repo_root: Path, managed_checkout: bool) -> None:
    path = default_install_state_path(home_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_host_state(home_root: Path) -> dict[str, object]:
    path = default_host_state_path(home_root)
    if not path.is_file():
        return {"state_version": 1}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"state_version": 1}
    if not isinstance(payload, dict):
        return {"state_version": 1}
    payload.setdefault("state_version", 1)
    return payload


def write_host_state(
    home_root: Path,
    *,
    key: str,
    payload: dict[str, object],
    delivery: dict[str, object] | None = None,
    operation_status: str | None = None,
    operation_scope: str | None = None,
) -> None:
    path = default_host_state_path(home_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = read_host_state(home_root)
    entry: dict[str, object] = {
        "recorded_at": now_iso(),
        "doctor": payload,
    }
    if delivery is not None:
        status = delivery.get("status")
        entry["delivery"] = delivery
        entry["delivery_status"] = status if isinstance(status, str) else "unknown"
        explicit_verified = delivery.get("delivery_verified")
        entry["delivery_verified"] = (
            explicit_verified
            if isinstance(explicit_verified, bool)
            else status in {"installed", "refreshed"}
        )
    if operation_status is not None:
        entry["operation_status"] = operation_status
    if operation_scope is not None:
        entry["operation_scope"] = operation_scope
    state[key] = entry
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_packaging(path: Path) -> dict[str, object]:
    return load_json(path / "packaging" / f"{PACKAGE_ID}.json")


def read_jsonrpc_line_before(
    stream: subprocess.Popen[str], *, deadline: float
) -> dict[str, object]:
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise CharnessError("timed out while waiting for Codex app-server response")
        ready, _, _ = select.select([stream.stdout], [], [], remaining)
        if not ready:
            raise CharnessError("timed out while waiting for Codex app-server response")
        line = stream.stdout.readline()
        if not line:
            stderr_output = stream.stderr.read() if stream.stderr is not None else ""
            raise CharnessError(
                "Codex app-server exited before returning a response"
                + (f"\nSTDERR:\n{stderr_output}" if stderr_output else "")
            )
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CharnessError(
                f"Codex app-server returned invalid JSON-RPC payload: {line.strip()}"
            ) from exc
        if isinstance(payload, dict):
            return payload


def build_host_next_steps(doctor_payload: dict[str, object]) -> dict[str, str]:
    host_next_steps: dict[str, str] = {}
    for host in ("codex", "claude", "grok"):
        guidance = doctor_payload.get(f"{host}_host_guidance")
        if not isinstance(guidance, dict):
            continue
        message = guidance.get("message")
        if isinstance(message, str) and message:
            host_next_steps[host] = message
    repo_onboarding = doctor_payload.get("repo_onboarding")
    if isinstance(repo_onboarding, dict):
        message = repo_onboarding.get("message")
        if isinstance(message, str) and message:
            host_next_steps["repo"] = message
    return host_next_steps


def _latest_host_operation(home_root: Path) -> tuple[str, dict[str, object]] | None:
    state = read_host_state(home_root)
    entries = [
        (key, value)
        for key in ("last_update", "last_init")
        if isinstance(value := state.get(key), dict)
    ]
    if not entries:
        return None
    key_order = {"last_init": 0, "last_update": 1}
    key, entry = max(
        entries,
        key=lambda item: (
            item[1].get("recorded_at", ""),
            key_order.get(item[0], -1),
        ),
    )
    return key, entry


def _compact_guidance(payload: object) -> dict[str, object] | None:
    return _compact_mapping(payload, ("status", "manual_action_required", "message", "reason"))


def _compact_next_action(payload: object) -> dict[str, object] | None:
    return _compact_mapping(
        payload,
        (
            "kind",
            "host",
            "status",
            "manual_action_required",
            "message",
            "source",
            "scope",
            "recovery_command",
            "failed_tool_ids",
            "recovery_command_args",
            "recovery_context",
        ),
    )


def _compact_release_check(payload: object) -> dict[str, object] | None:
    return _compact_mapping(
        payload, ("status", "latest_tag", "latest_version", "update_available", "checked_at")
    )


def _compact_host_refresh(payload: object) -> dict[str, object] | None:
    return _compact_mapping(
        payload,
        (
            "status",
            "action",
            "method",
            "reason",
            "error",
            "delivery_verified",
            "verification",
            "source_content_sha256",
            "cache_content_sha256",
            "post_refresh_cache_manifest_version",
            "post_refresh_drift",
            "post_refresh_host_status",
        ),
    )


def _compact_session_staleness(payload: object) -> dict[str, object] | None:
    compact = _compact_mapping(payload, ("status", "message"))
    if compact is None:
        return None
    if isinstance(payload, dict) and isinstance(payload.get("affected"), list):
        compact["affected_count"] = len(payload["affected"])
    return compact


def _host_delivery_failed(payload: object) -> bool:
    """Promote only an explicit host-delivery readback failure to exit 1."""
    return isinstance(payload, dict) and payload.get("status") == "failed"
