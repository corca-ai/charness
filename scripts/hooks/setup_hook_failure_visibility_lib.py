from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

LEFTHOOK_CANDIDATES = (Path("lefthook.yml"), Path("lefthook.yaml"))
HOOK_STAGES = ("pre-commit", "pre-push")
_READ_PATH_RE = re.compile(
    r"\bread\s+(?!output\s+above\b)(?:\"([^\"]+)\"|'([^']+)'|([^\s,;]+))",
    re.IGNORECASE,
)
_REDIRECT_TOKEN_RE = re.compile(
    r"(?P<dup>[12])>&(?P<dup_target>[12])"
    r"|(?P<both>&>>?)\s*(?:\"(?P<both_dq>[^\"]+)\"|'(?P<both_sq>[^']+)'|(?P<both_plain>[^\s;&]+))"
    r"|(?P<fd>[12])?(?P<op>>>?)\s*(?:\"(?P<dq>[^\"]+)\"|'(?P<sq>[^']+)'|(?P<plain>[^\s;&]+))"
)
_PIPELINE_RE = re.compile(r"(?<!\|)\|&?(?!\|)")
_TEMP_PATH_RE = re.compile(r"^(?:/tmp/|\$\{?TMPDIR\}?/)", re.IGNORECASE)
_QUOTED_TOKEN_PREFIX = "__CHARNESS_QUOTED_"


def _relative(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _config_path(repo_root: Path) -> Path | None:
    return next(
        (
            repo_root / candidate
            for candidate in LEFTHOOK_CANDIDATES
            if (repo_root / candidate).is_file()
        ),
        None,
    )


def _match_values(pattern: re.Pattern[str], text: str) -> list[str]:
    values: list[str] = []
    for match in pattern.finditer(text):
        value = next((group for group in match.groups() if group is not None), "")
        value = value.rstrip(".:")
        if value and value not in values:
            values.append(value)
    return values


def _normalized_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _shell_code_view(command: str) -> tuple[str, dict[str, str], bool]:
    output: list[str] = []
    quoted: dict[str, str] = {}
    index = 0
    valid = True
    while index < len(command):
        char = command[index]
        if char == "#" and (index == 0 or command[index - 1].isspace()):
            newline = command.find("\n", index)
            if newline < 0:
                break
            output.append("\n")
            index = newline + 1
            continue
        if char not in {"'", '"'}:
            output.append(char)
            index += 1
            continue
        quote = char
        index += 1
        value: list[str] = []
        closed = False
        while index < len(command):
            char = command[index]
            if char == quote:
                closed = True
                index += 1
                break
            if quote == '"' and char == "\\" and index + 1 < len(command):
                value.append(command[index + 1])
                index += 2
                continue
            value.append(char)
            index += 1
        if not closed:
            valid = False
        token = f"{_QUOTED_TOKEN_PREFIX}{len(quoted)}__"
        quoted[token] = "".join(value)
        output.append(token)
    return "".join(output), quoted, valid


def _shell_constructs(view: str, quoted: dict[str, str], valid: bool) -> list[str]:
    constructs: list[str] = []
    if not valid:
        constructs.append("unclosed-quote")
    if "\n" in view or ";" in view or "&&" in view or "||" in view:
        constructs.append("compound-command")
    if _PIPELINE_RE.search(view):
        constructs.append("pipeline")
    if re.search(r"(?<![|&>])&(?![&>])", view):
        constructs.append("background-command")
    if "$(" in view or "`" in view:
        constructs.append("command-substitution")
    for token, value in quoted.items():
        if re.search(rf"(?:^|\s)(?:ba|z|fi|da)?sh\b[^;\n]*\s-c\s+{re.escape(token)}", view):
            inner_view, inner_quoted, inner_valid = _shell_code_view(value)
            if _shell_constructs(inner_view, inner_quoted, inner_valid):
                constructs.append("embedded-shell-command")
                break
    return list(dict.fromkeys(constructs))


def _redirect_state(
    command: str, quoted: dict[str, str]
) -> tuple[str | None, str | None, list[str]]:
    streams: dict[str, str | None] = {"1": None, "2": None}
    paths: list[str] = []
    for match in _REDIRECT_TOKEN_RE.finditer(command):
        if match.group("dup") is not None:
            streams[match.group("dup")] = streams[match.group("dup_target")]
            continue
        if match.group("both") is not None:
            path = next(
                value
                for value in (
                    match.group("both_dq"),
                    match.group("both_sq"),
                    match.group("both_plain"),
                )
                if value is not None
            )
            path = quoted.get(path, path)
            streams["1"] = path
            streams["2"] = path
        else:
            path = next(
                value
                for value in (match.group("dq"), match.group("sq"), match.group("plain"))
                if value is not None
            )
            path = quoted.get(path, path)
            streams[match.group("fd") or "1"] = path
        if path not in paths:
            paths.append(path)
    return streams["1"], streams["2"], paths


def _stage_is_named(stage: str, fail_text: str) -> bool:
    lowered = fail_text.lower().replace("_", "-")
    alternatives = (stage, stage.replace("-", " "), stage.removeprefix("pre-"))
    return any(re.search(rf"\b{re.escape(candidate)}\b", lowered) for candidate in alternatives)


def _command_row(stage: str, command_id: str, raw: Any) -> dict[str, object]:
    gaps: list[str] = []
    if not isinstance(raw, dict):
        return {
            "stage": stage,
            "command_id": command_id,
            "run": None,
            "fail_text": None,
            "advertised_log_paths": [],
            "redirected_output_paths": [],
            "manual_reconciliation": [],
            "gaps": ["command-entry-not-mapping"],
        }

    raw_run = raw.get("run")
    run = raw_run if isinstance(raw_run, str) else None
    if raw_run is None:
        gaps.append("run-missing")
    elif run is None:
        gaps.append("run-not-string")

    raw_fail_text = raw.get("fail_text")
    fail_text = raw_fail_text.strip() if isinstance(raw_fail_text, str) else None
    if raw_fail_text is None:
        gaps.append("fail-text-missing")
    elif not fail_text:
        gaps.append("fail-text-blank" if isinstance(raw_fail_text, str) else "fail-text-not-string")

    advertised = _match_values(_READ_PATH_RE, fail_text or "")
    shell_view, quoted, shell_valid = _shell_code_view(run or "")
    manual_reconciliation = _shell_constructs(shell_view, quoted, shell_valid) if run else []
    if run and not manual_reconciliation:
        stdout_path, stderr_path, redirected = _redirect_state(shell_view, quoted)
    else:
        stdout_path, stderr_path, redirected = None, None, []
    advertised_normalized = {_normalized_path(path) for path in advertised}
    stdout_normalized = _normalized_path(stdout_path) if stdout_path else None
    stderr_normalized = _normalized_path(stderr_path) if stderr_path else None

    if fail_text:
        if not _stage_is_named(stage, fail_text):
            gaps.append("fail-text-does-not-name-stage")
        fallback = bool(
            re.search(r"\bread output above;\s*do not retry blind\b", fail_text, re.IGNORECASE)
        )
        if not advertised and not fallback:
            gaps.append("fail-text-has-no-next-evidence-action")
        if (
            not manual_reconciliation
            and advertised_normalized
            and stdout_normalized not in advertised_normalized
        ):
            gaps.append("advertised-log-not-redirected-by-command")
        if advertised and any(_TEMP_PATH_RE.search(_normalized_path(path)) for path in advertised):
            gaps.append("advertised-log-is-temporary")

    if (
        advertised
        and run
        and not manual_reconciliation
        and stderr_normalized not in advertised_normalized
    ):
        gaps.append("stderr-not-redirected-to-advertised-log")

    return {
        "stage": stage,
        "command_id": command_id,
        "run": run,
        "fail_text": fail_text,
        "advertised_log_paths": advertised,
        "redirected_output_paths": redirected,
        "manual_reconciliation": manual_reconciliation,
        "gaps": gaps,
    }


def inspect_hook_failure_visibility(repo_root: Path) -> dict[str, object]:
    repo_root = repo_root.resolve()
    config_path = _config_path(repo_root)
    manual_checks = [
        "fail_text names the actual blocking gate",
        "advertised log directories are provisioned before the hook runs",
        "the hook runner leaves the failure pointer finally visible",
        "any allowed pipeline retains unfiltered diagnostics",
        "an intentional failing hook preserves its non-zero exit and diagnostics",
    ]
    if config_path is None:
        return {
            "state": "no-lefthook-config",
            "config_path": None,
            "commands": [],
            "summary": {"command_count": 0, "commands_with_gaps": 0, "gap_count": 0},
            "live_verification": {"required": False, "checks": manual_checks},
            "non_claims": [
                "Husky and simple-git-hooks, pre-commit, and Overcommit configurations were not inspected"
            ],
        }

    try:
        parsed = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return {
            "state": "invalid-config",
            "config_path": _relative(config_path, repo_root),
            "config_errors": [str(exc)],
            "commands": [],
            "summary": {"command_count": 0, "commands_with_gaps": 0, "gap_count": 0},
            "live_verification": {"required": False, "checks": manual_checks},
            "non_claims": ["No command verdict was rendered from an invalid Lefthook config"],
        }
    if not isinstance(parsed, dict):
        return {
            "state": "invalid-config",
            "config_path": _relative(config_path, repo_root),
            "config_errors": ["Lefthook config root must be a mapping"],
            "commands": [],
            "summary": {"command_count": 0, "commands_with_gaps": 0, "gap_count": 0},
            "live_verification": {"required": False, "checks": manual_checks},
            "non_claims": ["No command verdict was rendered from an invalid Lefthook config"],
        }

    commands: list[dict[str, object]] = []
    config_errors: list[str] = []
    for stage in HOOK_STAGES:
        stage_data = parsed.get(stage)
        if stage_data is None:
            continue
        if not isinstance(stage_data, dict):
            config_errors.append(f"{stage} must be a mapping")
            continue
        raw_commands = stage_data.get("commands")
        if raw_commands is None:
            continue
        if not isinstance(raw_commands, dict):
            config_errors.append(f"{stage}.commands must be a mapping")
            continue
        commands.extend(
            _command_row(stage, str(command_id), raw)
            for command_id, raw in sorted(raw_commands.items(), key=lambda item: str(item[0]))
        )

    gap_count = sum(len(row["gaps"]) for row in commands)
    commands_with_gaps = sum(bool(row["gaps"]) for row in commands)
    if config_errors:
        state = "invalid-config"
    elif not commands:
        state = "no-applicable-hook-commands"
    elif gap_count:
        state = "action-required"
    elif any(row["manual_reconciliation"] for row in commands):
        state = "manual-reconciliation-required"
    else:
        state = "live-verification-required"
    return {
        "state": state,
        "config_path": _relative(config_path, repo_root),
        "config_errors": config_errors,
        "commands": commands,
        "summary": {
            "command_count": len(commands),
            "commands_with_gaps": commands_with_gaps,
            "gap_count": gap_count,
        },
        "live_verification": {"required": bool(commands), "checks": manual_checks},
        "non_claims": [
            "Static inspection does not prove final terminal ordering, log provisioning, or a real failing hook"
        ],
    }
