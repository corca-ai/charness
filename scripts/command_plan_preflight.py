#!/usr/bin/env python3

"""Preflight a repo-local command fan-out before any child command runs.

This is deliberately a plan checker, not a command runner.  A plan names the
repo-owned targets it will use, git refs it will inspect, and the commands whose
help surfaces will own the planned flags.  The checker resolves targets from
the same ``rg --files`` inventory an operator can inspect, verifies refs with
``git rev-parse --verify``, and runs only ``--help`` probes.  A failed preflight
returns non-zero, so callers must repair the plan before fanning out.

The explicit ``{target:<id>}`` token keeps a resolved path from being copied
into several command strings.  Missing or ambiguous targets are refusals, not
permission to guess a sibling path.  The plan is required to stay under the
repo root so a temporary or foreign file cannot silently become the evidence
source for a repo-owned fan-out.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
TARGET_TOKEN_PREFIX = "{target:"
TARGET_TOKEN_SUFFIX = "}"
HELP_TIMEOUT_SECONDS = 15
SHORT_FLAG_RE = re.compile(r"(?<![\w-])-[A-Za-z](?![A-Za-z0-9-])")

_plan_inputs = import_repo_module(__file__, "scripts.command_plan_inputs")
PLAN_VERSION = _plan_inputs.PLAN_VERSION
_repo_relative = _plan_inputs._repo_relative
_error = _plan_inputs._error
_load_plan = _plan_inputs._load_plan
_repo_files = _plan_inputs._repo_files
_target_matches = _plan_inputs._target_matches
_resolve_targets = _plan_inputs._resolve_targets
_verify_refs = _plan_inputs._verify_refs


def _expand_token(token: str, targets: dict[str, str]) -> tuple[str | None, dict[str, Any] | None]:
    if TARGET_TOKEN_PREFIX not in token:
        return token, None
    start = token.find(TARGET_TOKEN_PREFIX)
    end = token.find(TARGET_TOKEN_SUFFIX, start + len(TARGET_TOKEN_PREFIX))
    if end < 0:
        return None, _error("target-token", f"unterminated target token: {token}")
    target_id = token[start + len(TARGET_TOKEN_PREFIX) : end]
    if target_id not in targets:
        return None, _error("target-token", f"command references unresolved target: {target_id}")
    expanded = token[:start] + targets[target_id] + token[end + 1 :]
    if TARGET_TOKEN_PREFIX in expanded:
        return _expand_token(expanded, targets)
    return expanded, None


def _expand_argv(
    raw_argv: Any, targets: dict[str, str]
) -> tuple[list[str] | None, list[dict[str, Any]]]:
    if (
        not isinstance(raw_argv, list)
        or not raw_argv
        or not all(isinstance(token, str) for token in raw_argv)
    ):
        return None, [_error("command-shape", "argv must be a non-empty list of strings")]
    expanded: list[str] = []
    errors: list[dict[str, Any]] = []
    for token in raw_argv:
        value, error = _expand_token(token, targets)
        if error:
            errors.append(error)
        elif value is not None:
            expanded.append(value)
    return (expanded if not errors else None), errors


def _target_tokens(raw_argv: Any) -> list[str]:
    if not isinstance(raw_argv, list):
        return []
    return [
        token[len(TARGET_TOKEN_PREFIX) : -len(TARGET_TOKEN_SUFFIX)]
        for token in raw_argv
        if isinstance(token, str)
        and token.startswith(TARGET_TOKEN_PREFIX)
        and token.endswith(TARGET_TOKEN_SUFFIX)
    ]


def _standalone_target_token_errors(
    command_id: str, surface: str, raw_argv: Any
) -> list[dict[str, Any]]:
    if not isinstance(raw_argv, list):
        return []
    for token in raw_argv:
        if not isinstance(token, str) or TARGET_TOKEN_PREFIX not in token:
            continue
        if not (token.startswith(TARGET_TOKEN_PREFIX) and token.endswith(TARGET_TOKEN_SUFFIX)):
            return [
                _error(
                    "target-token",
                    f"{command_id}: {surface} target tokens must be standalone argv entries",
                    token=token,
                )
            ]
        inner = token[len(TARGET_TOKEN_PREFIX) : -len(TARGET_TOKEN_SUFFIX)]
        if TARGET_TOKEN_PREFIX in inner or TARGET_TOKEN_SUFFIX in inner:
            return [
                _error(
                    "target-token",
                    f"{command_id}: {surface} target tokens must contain one target id",
                    token=token,
                )
            ]
    return []


def _validate_owner_binding(
    command_id: str,
    owner_target: Any,
    raw_argv: Any,
    raw_help_argv: Any,
    targets: dict[str, str],
) -> list[dict[str, Any]]:
    """Require both command surfaces to name the same resolved owner target.

    A help probe is evidence about the command that actually receives the
    planned flags. Letting it be an independently copied path recreates the
    original wrong-owner smell: a healthy parser can make an unrelated command
    look like the planned command passed. The token is intentionally exact and
    singular for this plan format; a future wrapper contract must name its own
    target explicitly rather than quietly weakening this binding.
    """
    if not isinstance(owner_target, str) or not owner_target:
        return [
            _error("owner-binding", f"{command_id}: owner_target must be a non-empty target id")
        ]
    if owner_target not in targets:
        return [
            _error("owner-binding", f"{command_id}: owner_target is unresolved: {owner_target}")
        ]
    argv_token_errors = _standalone_target_token_errors(command_id, "argv", raw_argv)
    if argv_token_errors:
        return argv_token_errors
    expected = [owner_target]
    argv_targets = _target_tokens(raw_argv)
    if argv_targets != expected:
        return [
            _error(
                "owner-binding",
                f"{command_id}: argv must contain exactly {{target:{owner_target}}}",
                owner_target=owner_target,
                argv_targets=argv_targets,
            )
        ]
    if raw_help_argv is not None:
        help_token_errors = _standalone_target_token_errors(command_id, "help_argv", raw_help_argv)
        if help_token_errors:
            return help_token_errors
        help_targets = _target_tokens(raw_help_argv)
        if help_targets != expected:
            return [
                _error(
                    "owner-binding",
                    f"{command_id}: help_argv must contain exactly {{target:{owner_target}}}",
                    owner_target=owner_target,
                    help_targets=help_targets,
                )
            ]
    return []


def _derived_help_argv(argv: list[str]) -> list[str]:
    for index, token in enumerate(argv):
        if token.startswith("-"):
            return [*argv[:index], "--help"]
    return [*argv, "--help"]


def _planned_flags(argv: list[str]) -> list[str]:
    flags: list[str] = []
    for token in argv:
        if token.startswith("--") and token != "--":
            flags.append(token.split("=", 1)[0])
        elif token.startswith("-") and token != "-":
            flags.append(token)
    return list(dict.fromkeys(flags))


def _probe_command(
    root: Path, item: Any, targets: dict[str, str]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(item, dict):
        return {}, [_error("command-shape", "each command must be an object")]
    command_id = item.get("id")
    if not isinstance(command_id, str) or not command_id:
        return {}, [_error("command-shape", "command id must be a non-empty string")]
    raw_argv = item.get("argv")
    raw_help = item.get("help_argv")
    binding_errors = _validate_owner_binding(
        command_id, item.get("owner_target"), raw_argv, raw_help, targets
    )
    if binding_errors:
        return {"id": command_id, "status": "fail"}, binding_errors
    argv, errors = _expand_argv(raw_argv, targets)
    if errors or argv is None:
        return {"id": command_id, "status": "fail"}, errors
    help_argv, help_errors = _expand_argv(raw_help, targets) if raw_help is not None else (None, [])
    if help_errors:
        return {"id": command_id, "status": "fail", "argv": argv}, help_errors
    if help_argv is None:
        help_argv = _derived_help_argv(argv)
    if "--help" not in help_argv:
        return {"id": command_id, "status": "fail", "argv": argv}, [
            _error("help-probe-shape", f"{command_id}: help_argv must include --help")
        ]
    try:
        result = run_process(
            help_argv,
            cwd=root,
            env={**os.environ, "COLUMNS": "200", "LC_ALL": "C", "LANG": "C"},
            timeout_seconds=HELP_TIMEOUT_SECONDS,
        )
    except OSError as exc:
        return {"id": command_id, "status": "fail", "argv": argv, "help_argv": help_argv}, [
            _error("help-probe-failed", f"{command_id}: --help probe failed: {exc}")
        ]
    output = result.stdout + result.stderr
    observation: dict[str, Any] = {
        "id": command_id,
        "status": "pass" if result.returncode == 0 else "fail",
        "argv": argv,
        "help_argv": help_argv,
        "help_exit_code": result.returncode,
    }
    if result.returncode != 0:
        return observation, [
            _error(
                "help-probe-failed",
                f"{command_id}: --help exited {result.returncode}",
                stderr=result.stderr.strip()[-800:],
            )
        ]
    from scripts.core.argparse_surface_lib import accepted_options, iter_option_declarations

    accepted = sorted(accepted_options(output))
    accepted.extend(
        sorted(
            {
                flag
                for _source, declaration in iter_option_declarations(output)
                for flag in SHORT_FLAG_RE.findall(declaration)
            }
        )
    )
    planned = _planned_flags(argv)
    missing = sorted(set(planned) - set(accepted))
    observation["planned_flags"] = planned
    observation["accepted_flags"] = accepted
    if missing:
        observation["status"] = "fail"
        return observation, [
            _error(
                "flag-unresolved",
                f"{command_id}: planned flag(s) are absent from the owner --help surface",
                missing=missing,
                help_argv=help_argv,
            )
        ]
    return observation, []


def build_report(root: Path, plan_path: Path) -> dict[str, Any]:
    plan, errors = _load_plan(root, plan_path)
    if plan is None:
        return {"status": "refused", "exit_code": 2, "errors": errors}
    if errors:
        return {
            "status": "refused",
            "exit_code": 2,
            "plan": _repo_relative(root, plan_path),
            "errors": errors,
        }
    resolved_targets, target_errors = _resolve_targets(root, plan.get("targets"))
    ref_observations, ref_errors = _verify_refs(root, plan.get("refs"))
    errors.extend(target_errors)
    errors.extend(ref_errors)
    command_observations: list[dict[str, Any]] = []
    if not target_errors and not ref_errors:
        for item in plan.get("commands", []):
            observation, command_errors = _probe_command(root, item, resolved_targets)
            if observation:
                command_observations.append(observation)
            errors.extend(command_errors)
            if command_errors:
                errors.append(
                    _error(
                        "fanout-stopped",
                        "later command help probes were not run after the first preflight failure",
                    )
                )
                break
    else:
        errors.append(
            _error(
                "fanout-stopped",
                "command help probes were not run because target or git ref resolution failed",
            )
        )
    return {
        "status": "pass" if not errors else "refused",
        "exit_code": 0 if not errors else 2,
        "plan": _repo_relative(root, plan_path),
        "schema_version": plan.get("schema_version"),
        "targets": resolved_targets,
        "refs": ref_observations,
        "commands": command_observations,
        "errors": errors,
        "non_claims": [
            "This preflight does not run the planned commands or prove their runtime behavior.",
            "A passing --help probe does not establish installed, hosted, or external truth.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve command-plan targets, verify git refs, and probe owner --help "
            "before a repo-local fan-out. Does not run planned commands."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--plan", type=Path, required=True, help="Repo-relative JSON command plan")
    args = parser.parse_args(argv)
    try:
        root = args.repo_root.resolve()
        plan_path = args.plan if args.plan.is_absolute() else root / args.plan
        report = build_report(root, plan_path)
    except (OSError, ValueError) as exc:
        report = {
            "status": "refused",
            "exit_code": 2,
            "errors": [_error("preflight-error", str(exc))],
        }
    emit_yaml(report)
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
