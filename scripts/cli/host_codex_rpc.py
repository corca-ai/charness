"""Codex app-server JSON-RPC cache refresh (#873).

Split from host_codex.py: stdio JSON-RPC send/wait helpers and the
`codex app-server` cache-refresh driver.
"""

from __future__ import annotations

import json
import os
import shutil
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
    CharnessError,
)
from scripts.cli.install_delivery import (  # noqa: E402
    read_jsonrpc_line_before,
)


def wait_for_jsonrpc_response(
    stream: subprocess.Popen[str],
    *,
    expected_id: int,
    deadline: float,
) -> dict[str, object]:
    while True:
        message = read_jsonrpc_line_before(stream, deadline=deadline)
        if message.get("id") == expected_id:
            return message


def send_jsonrpc_message(stream: subprocess.Popen[str], payload: dict[str, object]) -> None:
    if stream.stdin is None:
        raise CharnessError("Codex app-server stdin is not available")
    stream.stdin.write(json.dumps(payload) + "\n")
    stream.stdin.flush()


def refresh_codex_cache_via_app_server(
    *,
    home_root: Path,
    codex_marketplace_path: Path,
    plugin_name: str,
    timeout_seconds: float = 10.0,
) -> dict[str, object]:
    codex_binary = shutil.which("codex")
    if codex_binary is None:
        return {
            "status": "skipped",
            "reason": "codex-cli-missing",
            "method": "codex-app-server-plugin-install",
        }
    if not codex_marketplace_path.is_file():
        return {
            "status": "skipped",
            "reason": "missing-marketplace",
            "method": "codex-app-server-plugin-install",
        }

    env = os.environ.copy()
    env["CODEX_HOME"] = str(home_root / ".codex")
    proc = subprocess.Popen(
        [codex_binary, "app-server", "--listen", "stdio://"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=home_root,
        env=env,
    )
    try:
        initialize_deadline = time.monotonic() + timeout_seconds
        send_jsonrpc_message(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {"name": "charness", "version": "0.1.0"},
                    "capabilities": {"experimentalApi": True},
                },
            },
        )
        message = wait_for_jsonrpc_response(proc, expected_id=1, deadline=initialize_deadline)
        if isinstance(message.get("error"), dict):
            raise CharnessError(
                f"Codex app-server initialize failed: {message['error'].get('message')}"
            )
        send_jsonrpc_message(
            proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        )
        install_deadline = time.monotonic() + timeout_seconds
        send_jsonrpc_message(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "plugin/install",
                "params": {
                    "marketplacePath": str(codex_marketplace_path),
                    "pluginName": plugin_name,
                    "forceRemoteSync": False,
                },
            },
        )
        message = wait_for_jsonrpc_response(proc, expected_id=2, deadline=install_deadline)
        if isinstance(message.get("error"), dict):
            error_message = message["error"].get("message")
            return {
                "status": "failed",
                "reason": "plugin-install-error",
                "method": "codex-app-server-plugin-install",
                "error": error_message if isinstance(error_message, str) else str(message["error"]),
            }
        result = message.get("result")
        return {
            "status": "attempted",
            "reason": "plugin-install-succeeded",
            "method": "codex-app-server-plugin-install",
            "response": result if isinstance(result, dict) else {},
        }
    except CharnessError as exc:
        return {
            "status": "failed",
            "reason": "app-server-error",
            "method": "codex-app-server-plugin-install",
            "error": str(exc),
        }
    finally:
        if proc.stdin is not None:
            proc.stdin.close()
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
