"""Shared error, emit, path, resolve, and version helpers."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable


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
    default_state_root,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)


def parse_repo_script_payload(stdout: str, source: str) -> object:
    """Read one repo-script `--detail` payload -- JSON fast path first, then YAML.

    The mirror image of `render_yaml` above, and it has to be, for the reason that
    function has its own ImportError branch: a producer without PyYAML emits
    COMPACT JSON, and JSON is valid YAML, so the JSON attempt is both the common
    case and the only one this deliberately standalone-copyable CLI can serve when
    PyYAML is absent from ITS interpreter. `invoke_repo_script` runs the producer
    under `resolve_repo_python(repo_root)`, which normally has PyYAML, so the
    payload usually IS real YAML while this process may be a bare system python3.

    That crossing is the one case that must not crash: a real YAML payload with no
    PyYAML here raises a CharnessError naming the remedy, because `charness init`
    reaching this line has already cloned and installed, and a parse traceback
    would read as a broken install rather than a missing dependency.

    This function keeps the standalone CLI tolerant of either JSON or YAML
    emitted by a repo-owned inspection command.
    """
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        pass
    try:
        import yaml
    except ImportError as exc:
        raise CharnessError(
            f"`{source}` returned a YAML payload and PyYAML is not importable by this interpreter "
            f"({sys.executable}).\nInstall PyYAML for it, or run the command through the managed "
            "runtime (`python3 scripts/core/bootstrap_runtime.py --repo-root . --print-python`)."
        ) from exc
    try:
        return yaml.safe_load(stdout)
    except yaml.YAMLError as exc:
        raise CharnessError(
            f"`{source}` did not return a readable YAML payload\nSTDOUT:\n{stdout}"
        ) from exc


def resolve_config_home(home_root: Path) -> Path:
    override = os.environ.get("CHARNESS_CONFIG_HOME")
    if override:
        return Path(override).expanduser().resolve()
    xdg_root = os.environ.get("XDG_CONFIG_HOME")
    if xdg_root:
        return Path(xdg_root).expanduser().resolve()
    return home_root / ".config"


def default_config_root(home_root: Path) -> Path:
    return resolve_config_home(home_root) / PACKAGE_ID


def default_grok_plugin_root(home_root: Path) -> Path:
    return home_root / ".grok" / "plugins" / PACKAGE_ID


def default_codex_config_path(home_root: Path) -> Path:
    return home_root / ".codex" / "config.toml"


def default_claude_plugins_root(home_root: Path) -> Path:
    return home_root / ".claude" / "plugins"


def default_claude_known_marketplaces_path(home_root: Path) -> Path:
    return default_claude_plugins_root(home_root) / "known_marketplaces.json"


def default_claude_installed_plugins_path(home_root: Path) -> Path:
    return default_claude_plugins_root(home_root) / "installed_plugins.json"


def default_host_state_path(home_root: Path) -> Path:
    return default_state_root(home_root) / "host-state.json"


def repo_capability_local_path(target_repo_root: Path) -> Path:
    return target_repo_root / ".charness" / "local" / "capability.json"


def repo_capability_example_path(target_repo_root: Path) -> Path:
    return target_repo_root / ".charness" / "capability.example.json"


def repo_gitignore_path(target_repo_root: Path) -> Path:
    return target_repo_root / ".gitignore"


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def emit_operational_response(
    args: argparse.Namespace,
    payload: dict[str, object],
    *,
    event: str,
    projector: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    if getattr(args, "detail", False):
        emit_yaml({"event": event, "response_level": "detail", **payload})
        return
    emit_yaml(projector(payload))
