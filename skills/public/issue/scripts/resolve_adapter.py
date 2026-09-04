#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
_yaml_output_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
emit_yaml = _yaml_output_module.emit_yaml
load_yaml_file = _adapter_lib_module.load_yaml_file
load_yaml_file_report = _adapter_lib_module.load_yaml_file_report
uninterpreted_warnings = _adapter_lib_module.uninterpreted_warnings
parse_failure_error = _adapter_lib_module.parse_failure_error
read_failure_error = _adapter_lib_module.read_failure_error
normalize_adapter_result = _adapter_lib_module.normalize_adapter_result
validate_adapter_version = _adapter_lib_module.validate_adapter_version

def _load_capture_capability():
    """Load the sibling capability module from either the source or installed layout.

    Loaded by path rather than imported by package name because this file has no stable
    package identity: the source tree puts it under `skills/public/issue/scripts/` and
    the exported plugin under `skills/issue/scripts/`, and it is also loaded directly by
    file path from several callers.
    """
    return SKILL_RUNTIME.load_local_skill_module(__file__, "issue_source_capture_capability")


_CAPTURE_CAPABILITY = _load_capture_capability()

ADAPTER_CANDIDATES = (
    Path(".agents/issue-adapter.yaml"),
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
        "issue_source_capture": _CAPTURE_CAPABILITY.default_source_capture(),
        "feature_brief_pause": DEFAULT_FEATURE_BRIEF_PAUSE,
        "harness_upstream": None,
    }


def default_backend() -> dict[str, Any]:
    return {"id": "gh", "binary": "gh", "commands": None, "repo_scoped": None}


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
    ../../../shared/references/retro-issue-destination-split.md).
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
    # A binary genuinely bound to ONE repository declares which one, as `owner/repo`. It is
    # parsed here or it does not exist: every real caller receives its backend from this
    # function, so a key the parser drops is a key the runtime never sees no matter what the
    # adapter says. A bare `true` is refused deliberately -- it cannot answer "scoped to
    # WHICH repository", and this skill routes to two targets (upstream and local), so an
    # unqualified waiver would drop the repo on the target the binary is NOT bound to.
    repo_scoped = raw.get("repo_scoped")
    scoped_repo: str | None = None
    if repo_scoped is not None:
        # WARN and ignore rather than invalidate the adapter. This file's own norm is that a
        # consumer-authored adapter mistake warns instead of refusing (see the note on the
        # deferred arming decision below), and ignoring is also the FAIL-CLOSED direction here:
        # no scope declared means no waiver, which means a template omitting `{repo}` gets a
        # loud placeholder error rather than a silent drop. Refusing the whole adapter would
        # take the entire issue lane red over an optional key.
        if isinstance(repo_scoped, bool):
            warnings.append(
                "issue_backend.repo_scoped must be the `owner/repo` the binary is bound to, "
                "not a boolean; an unqualified waiver cannot say which repository it covers. "
                "Ignoring it: `{repo}` stays required."
            )
        else:
            value = _string(repo_scoped, "issue_backend.repo_scoped", errors)
            if value is not None:
                candidate = value.strip().strip("/")
                parts = candidate.split("/")
                # `>= 2` segments rather than exactly two: a nested namespace (a GitLab
                # group/subgroup/project, a nested org) is a real repository path, and refusing
                # it would leave that host class unable to declare its scope at all.
                if len(parts) < 2 or not all(part.strip() for part in parts):
                    warnings.append(
                        "issue_backend.repo_scoped must be a repository path such as "
                        f"`owner/repo`; got {value!r}. Ignoring it: `{{repo}}` stays required."
                    )
                else:
                    scoped_repo = candidate
    return {
        "id": backend_id,
        "binary": binary,
        "commands": commands,
        "repo_scoped": scoped_repo,
    }


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
        payload = {
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
        return normalize_adapter_result(payload, skill_id="issue")

    # `load_yaml_file_report` parses exactly as `load_yaml_file` does and additionally
    # returns the lines the parser could not interpret. Reading them is what separates
    # "the adapter did not set this field" from "the adapter tried to set it and the
    # parser threw the line away" (sweep row S24): the second used to be indistinguishable
    # from the first, so `default_org corca-typo` with a missing colon reported
    # `valid: true, errors: [], warnings: []` while silently serving the inferred default.
    # The old `isinstance(raw, dict)` guard below could never fire — `load_yaml` always
    # returns a dict — so a top-level YAML list produced no warning either; it now
    # surfaces as one uninterpreted line per item.
    #
    # These are WARNINGS, not errors, and that is a deliberate stop rather than a shrug.
    # This file is consumer-authored, so refusing it would turn a consumer's whole issue
    # lane red for a typo, and the only corpus that could justify arming the refusal —
    # consumer `.agents/issue-adapter.yaml` files — is one this repo cannot enumerate.
    # Arming is declined (archive D46); uninterpreted lines stay warnings.
    data = dict(defaults)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        raw, uninterpreted = load_yaml_file_report(adapter_path)
    except (OSError, UnicodeError, ValueError) as exc:
        # An unsupported construct used to escape as a traceback, which is neither a
        # refusal nor a pass — callers branching on `valid` never saw it at all.
        error = read_failure_error(exc) if isinstance(exc, (OSError, UnicodeError)) else parse_failure_error(exc)
        payload = {
            "found": True,
            "valid": False,
            "path": str(adapter_path),
            "data": data,
            "errors": [error],
            "warnings": [],
            "searched_paths": searched_paths,
        }
        return normalize_adapter_result(payload, skill_id="issue")
    raw_data = raw if isinstance(raw, dict) else {}
    warnings.extend(
        f"{line} This is reported, not refused: the consumer adapter population is not measurable here."
        for line in uninterpreted_warnings(uninterpreted)
    )

    validate_adapter_version(raw_data, data, errors)
    if errors:
        payload = {
            "found": True,
            "valid": False,
            "path": str(adapter_path),
            "data": data,
            "errors": errors,
            "warnings": warnings,
            "searched_paths": searched_paths,
        }
        return normalize_adapter_result(payload, skill_id="issue")

    for field in ("default_org", "default_repo", "remote_name"):
        value = _string(raw_data.get(field), field, errors)
        if value is not None:
            data[field] = value

    data["issue_backend"] = _parse_backend(raw_data.get("issue_backend"), errors, warnings)
    data["issue_source_capture"] = _CAPTURE_CAPABILITY.parse_source_capture(
        raw_data.get("issue_source_capture"), data["issue_backend"], errors, warnings, _string
    )
    data["feature_brief_pause"] = _parse_feature_brief_pause(
        raw_data.get("feature_brief_pause"), errors
    )
    data["harness_upstream"] = _parse_harness_upstream(raw_data.get("harness_upstream"), errors)

    payload = {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }
    return normalize_adapter_result(payload, skill_id="issue")


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
            emit_yaml(payload)
            return 0 if payload["ok"] else 1
        payload = load_adapter(args.repo_root.resolve())
        emit_yaml(payload)
        return 0 if payload["valid"] else 1
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
