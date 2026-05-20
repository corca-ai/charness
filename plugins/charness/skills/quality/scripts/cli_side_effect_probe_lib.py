from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_PATTERNS = [".agents/cli-side-effect-probes.json", "**/cli-side-effect-probes.json", "**/*side-effect-probes*.json"]
DEFAULT_PROBE_TIMEOUT_SECONDS = 20


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_visible_repo_files(repo_root: Path) -> set[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return {repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel}


def _filter_path(repo_root: Path, path: Path, visible: set[Path] | None, seen: set[Path], vendored_filter) -> bool:
    if not path.is_file() or path in seen:
        return False
    if visible is not None and path not in visible:
        return False
    if vendored_filter is not None and vendored_filter(repo_root, path):
        return False
    return True


def default_paths(repo_root: Path, vendored_filter=None) -> list[Path]:
    visible_files = _git_visible_repo_files(repo_root)
    seen: set[Path] = set()
    found: list[Path] = []
    for pattern in DEFAULT_PATTERNS:
        for path in sorted(repo_root.glob(pattern)):
            if _filter_path(repo_root, path, visible_files, seen, vendored_filter):
                seen.add(path)
                found.append(path)
    return found


def _string_list(entry: dict[str, Any], key: str) -> list[str]:
    value = entry.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _non_empty_string(entry: dict[str, Any], key: str) -> str:
    value = entry.get(key)
    return value.strip() if isinstance(value, str) else ""


def _positive_int(entry: dict[str, Any], key: str, default: int) -> int:
    value = entry.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else default


def _finding(
    repo_root: Path,
    path: Path | None,
    index: int,
    command: str,
    finding_type: str,
    suggestion: str,
    **extra: object,
) -> dict[str, object]:
    rendered_path = str(path.relative_to(repo_root)) if path else "<missing>"
    return {"type": finding_type, "path": rendered_path, "entry_index": index, "command": command, "suggestion": suggestion, **extra}


def _resolve_watch_path(repo_root: Path, watch_path: str) -> Path:
    expanded = Path(watch_path).expanduser()
    return expanded if expanded.is_absolute() else repo_root / expanded


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _snapshot_one(path: Path) -> object:
    if not path.exists():
        return {"state": "missing"}
    if path.is_file():
        return {"state": "file", "sha256": _file_hash(path)}
    if path.is_dir():
        entries: dict[str, object] = {}
        for child in sorted(path.rglob("*")):
            rel = str(child.relative_to(path))
            if child.is_file():
                entries[rel] = {"state": "file", "sha256": _file_hash(child)}
            elif child.is_dir():
                entries[rel] = {"state": "dir"}
            else:
                entries[rel] = {"state": "other"}
        return {"state": "dir", "entries": entries}
    return {"state": "other"}


def _snapshot(repo_root: Path, watch_paths: list[str]) -> dict[str, object]:
    return {watch_path: _snapshot_one(_resolve_watch_path(repo_root, watch_path)) for watch_path in watch_paths}


def _probe_commands(entry: dict[str, Any]) -> list[tuple[str, str, bool]]:
    probes: list[tuple[str, str, bool]] = []
    help_probe = _non_empty_string(entry, "help_probe")
    if help_probe:
        probes.append(("help_probe", help_probe, False))
    for command in _string_list(entry, "option_like_positional_probes"):
        probes.append(("option_like_positional_probe", command, True))
    dry_run_probe = _non_empty_string(entry, "dry_run_probe")
    if dry_run_probe:
        probes.append(("dry_run_probe", dry_run_probe, False))
    plan_probe = _non_empty_string(entry, "plan_probe")
    if plan_probe:
        probes.append(("plan_probe", plan_probe, False))
    return probes


def _run_probes(repo_root: Path, path: Path, index: int, entry: dict[str, Any]) -> list[dict[str, object]]:
    command = _non_empty_string(entry, "command")
    watch_paths = _string_list(entry, "side_effect_watch_paths")
    findings: list[dict[str, object]] = []
    timeout_seconds = _positive_int(entry, "probe_timeout_seconds", DEFAULT_PROBE_TIMEOUT_SECONDS)
    if not entry.get("safe_to_execute"):
        return [_finding(repo_root, path, index, command, "mutating_command_execution_not_enabled", "Set safe_to_execute only for sandboxed probe fixtures whose side effects are watched.")]
    for probe_type, probe_command, expect_failure in _probe_commands(entry):
        before = _snapshot(repo_root, watch_paths)
        try:
            result = subprocess.run(
                shlex.split(probe_command),
                cwd=repo_root,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            findings.append(_finding(repo_root, path, index, command, "probe_timed_out", "Give executable CLI side-effect probes a bounded fixture command that returns quickly.", probe_type=probe_type, probe_command=probe_command, timeout_seconds=timeout_seconds))
            continue
        after = _snapshot(repo_root, watch_paths)
        if before != after:
            findings.append(_finding(repo_root, path, index, command, "probe_changed_side_effect_watch", "Fix the probe so it rejects or previews before mutating watched state.", probe_type=probe_type, probe_command=probe_command))
        if expect_failure and result.returncode == 0:
            findings.append(_finding(repo_root, path, index, command, "option_like_positional_probe_did_not_fail", "Option-looking positional probes should reject before mutation.", probe_type=probe_type, probe_command=probe_command))
    return findings


def inspect_command(repo_root: Path, path: Path, index: int, entry: dict[str, Any], *, execute_probes: bool) -> dict[str, object]:
    command = _non_empty_string(entry, "command")
    findings: list[dict[str, object]] = []
    mutating = bool(entry.get("mutating"))
    positional_args = _string_list(entry, "positional_args")
    watch_paths = _string_list(entry, "side_effect_watch_paths")
    help_probe = _non_empty_string(entry, "help_probe")
    dry_run_probe = _non_empty_string(entry, "dry_run_probe")
    plan_probe = _non_empty_string(entry, "plan_probe")
    dry_run_waiver = _non_empty_string(entry, "dry_run_waiver")

    if not command:
        findings.append(_finding(repo_root, path, index, command, "missing_command", "Declare the command string."))
    if mutating and not help_probe:
        findings.append(_finding(repo_root, path, index, command, "mutating_command_missing_help_probe", "Probe `<command> --help` and assert no side effects."))
    if mutating and positional_args and not _string_list(entry, "option_like_positional_probes"):
        findings.append(_finding(repo_root, path, index, command, "mutating_command_missing_option_like_positional_probe", "Probe option-looking positional values and assert rejection before mutation."))
    if mutating and not dry_run_probe and not plan_probe and not dry_run_waiver:
        findings.append(_finding(repo_root, path, index, command, "mutating_command_missing_dry_run_or_plan", "Add a dry-run/plan probe or a concrete waiver."))
    if mutating and not watch_paths:
        findings.append(_finding(repo_root, path, index, command, "mutating_command_missing_side_effect_watch", "Declare filesystem, service, or command-runner side-effect watch points."))
    if mutating and execute_probes and not findings:
        findings.extend(_run_probes(repo_root, path, index, entry))
    return {"command": command, "mutating": mutating, "findings": findings}


def inventory_contract(repo_root: Path, path: Path, *, execute_probes: bool) -> dict[str, object]:
    payload = _load_json(path)
    entries = payload.get("commands", []) if isinstance(payload, dict) else []
    commands = [
        inspect_command(repo_root, path, index, entry, execute_probes=execute_probes)
        for index, entry in enumerate(entries)
        if isinstance(entry, dict)
    ]
    findings = [finding for command in commands for finding in command["findings"]]
    return {"path": str(path.relative_to(repo_root)), "command_count": len(commands), "commands": commands, "findings": findings}


def build_inventory(repo_root: Path, *, contract_paths: list[Path], execute_probes: bool, vendored_filter=None) -> dict[str, object]:
    requested = bool(contract_paths)
    paths = contract_paths if contract_paths else default_paths(repo_root, vendored_filter=vendored_filter)
    contracts = [inventory_contract(repo_root, path, execute_probes=execute_probes) for path in paths]
    findings = [finding for contract in contracts for finding in contract["findings"]]
    if not contracts:
        findings.append(_finding(repo_root, None, -1, "", "cli_side_effect_probe_contract_missing", "Add a cli-side-effect-probes.json contract for mutating operator CLI commands."))
    if contracts:
        status: dict[str, str] = {"status": "clean"}
    elif requested:
        status = {"status": "clean", "reason": "Explicit --contract-file arguments yielded no readable files."}
    else:
        status = {"status": "unconfigured", "reason": "No cli-side-effect-probes.json contract file was discovered. Provide --contract-file or commit a contract under repo-visible paths such as .agents/cli-side-effect-probes.json."}
    return {"repo_root": str(repo_root), "execute_probes": execute_probes, **status, "contracts": contracts, "findings": findings}
