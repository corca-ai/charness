#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib_module.load_yaml_file

ADAPTER_CANDIDATES = (
    Path(".agents/issue-adapter.yaml"),
    Path(".codex/issue-adapter.yaml"),
    Path(".claude/issue-adapter.yaml"),
    Path("docs/issue-adapter.yaml"),
    Path("issue-adapter.yaml"),
)


FEATURE_BRIEF_PAUSE_VALUES = ("on-open-decisions", "always", "never")
DEFAULT_FEATURE_BRIEF_PAUSE = "on-open-decisions"


def infer_defaults() -> dict[str, Any]:
    return {
        "version": 1,
        "default_org": "corca-ai",
        "default_repo": None,
        "remote_name": "origin",
        "issue_backend": default_backend(),
        "feature_brief_pause": DEFAULT_FEATURE_BRIEF_PAUSE,
        "harness_upstream": None,
    }


def default_backend() -> dict[str, Any]:
    return {"id": "gh", "binary": "gh", "commands": None}


def _parse_feature_brief_pause(raw: Any, errors: list[str]) -> str:
    if raw is None:
        return DEFAULT_FEATURE_BRIEF_PAUSE
    if not isinstance(raw, str) or raw not in FEATURE_BRIEF_PAUSE_VALUES:
        errors.append(
            "feature_brief_pause must be one of: "
            + ", ".join(FEATURE_BRIEF_PAUSE_VALUES)
        )
        return DEFAULT_FEATURE_BRIEF_PAUSE
    return raw


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return None
    return value


def _parse_harness_upstream(raw: Any, errors: list[str]) -> str | None:
    """Validate the `org/repo` slug naming the charness upstream repository.

    Optional: absent means the destination split has no configured upstream and
    callers fall back to keeping findings repo-local (see
    ../../shared/references/retro-issue-destination-split.md).
    """
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        errors.append("harness_upstream must be a non-empty 'org/repo' string")
        return None
    parts = raw.strip().split("/")
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        errors.append("harness_upstream must be of the form 'org/repo'")
        return None
    return raw.strip()


def resolve_destination_target(
    current_full_name: str | None, harness_upstream: str | None
) -> dict[str, Any]:
    """Pure resolution of upstream/local issue targets for a retro-derived split.

    Implements the B1 adapter-pointer identity, the E1 current-repo==upstream
    collapse, and the safe "unknown -> keep local" fallback. Targets are returned
    as-given (GitHub slugs compare case-insensitively).
    """
    current = current_full_name.strip() if isinstance(current_full_name, str) and current_full_name.strip() else None
    upstream = harness_upstream.strip() if isinstance(harness_upstream, str) and harness_upstream.strip() else None

    if upstream is None:
        return {
            "ok": True,
            "mode": "unknown",
            "current": current,
            "harness_upstream": None,
            "collapsed": False,
            "ambiguous": True,
            "upstream_target": None,
            "local_target": current,
            "note": (
                "harness_upstream is unset; keep findings repo-local and state the "
                "ambiguity. Never file a harness issue into a guessed upstream repo."
            ),
        }
    if current is None:
        return {
            "ok": True,
            "mode": "unknown",
            "current": None,
            "harness_upstream": upstream,
            "collapsed": False,
            "ambiguous": True,
            "upstream_target": upstream,
            "local_target": None,
            "note": (
                "current repo is unresolved; resolve it before routing repo-local "
                "findings. Upstream-harness findings can target harness_upstream."
            ),
        }
    if current.lower() == upstream.lower():
        return {
            "ok": True,
            "mode": "collapse",
            "current": current,
            "harness_upstream": upstream,
            "collapsed": True,
            "ambiguous": False,
            "upstream_target": current,
            "local_target": current,
            "note": (
                "current repo is the harness; the destination split collapses to one "
                "repo. Distinguish portable skill/harness core vs this repo's own "
                "operating surface by label/section, not by destination repo."
            ),
        }
    return {
        "ok": True,
        "mode": "consumer",
        "current": current,
        "harness_upstream": upstream,
        "collapsed": False,
        "ambiguous": False,
        "upstream_target": upstream,
        "local_target": current,
        "note": (
            "consumer repo; upstream-harness findings -> harness_upstream, "
            "repo-local findings -> the current repo."
        ),
    }


def _parse_backend(raw: Any, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    if raw is None:
        return default_backend()
    if not isinstance(raw, dict):
        errors.append("issue_backend must be a mapping")
        return default_backend()
    backend_id = _string(raw.get("id"), "issue_backend.id", errors) or "gh"
    binary = _string(raw.get("binary"), "issue_backend.binary", errors) or backend_id
    commands: dict[str, list[str]] | None = None
    raw_commands = raw.get("commands")
    if raw_commands is not None:
        if not isinstance(raw_commands, dict):
            errors.append("issue_backend.commands must be a mapping")
        else:
            commands = {}
            for op, argv in raw_commands.items():
                if not isinstance(argv, list) or not all(isinstance(part, str) for part in argv):
                    errors.append(f"issue_backend.commands.{op} must be a list of strings")
                    continue
                commands[op] = list(argv)
    if backend_id != "gh" and not commands:
        warnings.append(
            f"issue_backend.id={backend_id} declared without commands; "
            "agent must follow the host-documented command shape until commands templates are filled in"
        )
    return {"id": backend_id, "binary": binary, "commands": commands}


def find_adapter(repo_root: Path) -> Path | None:
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    defaults = infer_defaults()
    if adapter_path is None:
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": defaults,
            "errors": [],
            "warnings": [
                "No issue adapter found. Using default_org=corca-ai and current-repo inference.",
                "Create .agents/issue-adapter.yaml to change default GitHub ownership, default repo, or labels.",
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    data = dict(defaults)
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")

    version = raw_data.get("version")
    if version is not None:
        if isinstance(version, int):
            data["version"] = version
        else:
            errors.append("version must be an integer")

    for field in ("default_org", "default_repo", "remote_name"):
        value = _string(raw_data.get(field), field, errors)
        if value is not None:
            data[field] = value

    data["issue_backend"] = _parse_backend(raw_data.get("issue_backend"), errors, warnings)
    data["feature_brief_pause"] = _parse_feature_brief_pause(
        raw_data.get("feature_brief_pause"), errors
    )
    data["harness_upstream"] = _parse_harness_upstream(raw_data.get("harness_upstream"), errors)

    canonical_path = repo_root / ".agents" / "issue-adapter.yaml"
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")

    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="issue resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root used to locate the issue adapter")
    sub = parser.add_subparsers(dest="command")
    dest = sub.add_parser(
        "resolve-destination",
        help="Resolve upstream/local issue targets for a retro-derived destination split",
    )
    dest.add_argument(
        "--current",
        type=str,
        default=None,
        help="Current repo as org/repo; omit to leave the local target unresolved",
    )
    try:
        args = parser.parse_args()
        if args.command == "resolve-destination":
            adapter = load_adapter(args.repo_root.resolve())
            payload = resolve_destination_target(args.current, adapter["data"].get("harness_upstream"))
            payload["adapter_found"] = adapter["found"]
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if payload["ok"] else 1
        payload = load_adapter(args.repo_root.resolve())
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if payload["valid"] else 1
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
