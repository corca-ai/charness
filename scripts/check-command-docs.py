#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.adapter_lib import load_yaml_file

DEFAULT_CONTRACT = Path(".agents/command-docs.yaml")


class ValidationError(Exception):
    pass


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def require_string(value: Any, field: str, errors: list[str]) -> str:
    if isinstance(value, str) and value:
        return value
    errors.append(f"{field} must be a non-empty string")
    return ""


def optional_string_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return []
    return list(value)


def load_contract(path: Path) -> dict[str, dict[str, object]]:
    raw = load_yaml_file(path)
    commands = raw.get("commands")
    errors: list[str] = []
    if not isinstance(commands, dict) or not commands:
        raise ValidationError(f"{path}: commands must be a non-empty mapping")

    parsed: dict[str, dict[str, object]] = {}
    for command_id, raw_command in commands.items():
        if not isinstance(command_id, str):
            errors.append(f"{path}: command ids must be strings")
            continue
        if not isinstance(raw_command, dict):
            errors.append(f"{path}: commands.{command_id} must be a mapping")
            continue
        parsed[command_id] = {
            "help_command": require_string(raw_command.get("help_command"), f"commands.{command_id}.help_command", errors),
            "doc_paths": optional_string_list(raw_command.get("doc_paths"), f"commands.{command_id}.doc_paths", errors),
            "required_help_contains": optional_string_list(
                raw_command.get("required_help_contains"),
                f"commands.{command_id}.required_help_contains",
                errors,
            ),
            "required_doc_contains": optional_string_list(
                raw_command.get("required_doc_contains"),
                f"commands.{command_id}.required_doc_contains",
                errors,
            ),
            "forbidden_doc_contains": optional_string_list(
                raw_command.get("forbidden_doc_contains"),
                f"commands.{command_id}.forbidden_doc_contains",
                errors,
            ),
        }
    if errors:
        raise ValidationError("\n".join(errors))
    return parsed


def run_help(repo_root: Path, command: str) -> str:
    result = subprocess.run(
        shlex.split(command),
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValidationError(
            f"help command `{command}` failed with exit {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout + result.stderr


def read_docs(repo_root: Path, doc_paths: list[str], command_id: str) -> str:
    if not doc_paths:
        raise ValidationError(f"{command_id}: doc_paths must contain at least one path")
    contents: list[str] = []
    for doc_path in doc_paths:
        path = repo_root / doc_path
        if not path.is_file():
            raise ValidationError(f"{command_id}: documented path is missing: {doc_path}")
        contents.append(path.read_text(encoding="utf-8"))
    return "\n".join(contents)


def assert_contains(haystack: str, needle: str, *, context: str) -> str | None:
    if normalize_text(needle) not in normalize_text(haystack):
        return f"{context} missing `{needle}`"
    return None


def assert_absent(haystack: str, needle: str, *, context: str) -> str | None:
    if normalize_text(needle) in normalize_text(haystack):
        return f"{context} must not contain `{needle}`"
    return None


def check_command(repo_root: Path, command_id: str, config: dict[str, object]) -> list[str]:
    help_command = str(config["help_command"])
    help_output = run_help(repo_root, help_command)
    doc_paths = list(config["doc_paths"])
    docs = read_docs(repo_root, doc_paths, command_id)
    findings: list[str] = []

    for needle in config["required_help_contains"]:
        finding = assert_contains(help_output, needle, context=f"{command_id}: help `{help_command}`")
        if finding:
            findings.append(finding)
    doc_context = f"{command_id}: docs {', '.join(doc_paths)}"
    for needle in config["required_doc_contains"]:
        finding = assert_contains(docs, needle, context=doc_context)
        if finding:
            findings.append(finding)
    for needle in config["forbidden_doc_contains"]:
        finding = assert_absent(docs, needle, context=doc_context)
        if finding:
            findings.append(finding)
    return findings


def build_report(repo_root: Path, contract_path: Path) -> dict[str, object]:
    if not contract_path.is_absolute():
        contract_path = repo_root / contract_path
    if not contract_path.is_file():
        return {"status": "skipped", "reason": "missing-contract", "commands": [], "findings": []}

    commands = load_contract(contract_path)
    findings: list[str] = []
    for command_id, config in commands.items():
        findings.extend(check_command(repo_root, command_id, config))
    return {
        "status": "fail" if findings else "pass",
        "contract_path": str(contract_path.relative_to(repo_root)),
        "commands": sorted(commands),
        "findings": findings,
    }


def render_report(report: dict[str, object]) -> str:
    if report["status"] == "skipped":
        return "No command-docs contract found; skipping command docs drift check."
    if not report["findings"]:
        return f"Validated command docs for {len(report['commands'])} command surface(s)."
    lines = ["Command docs drift detected:"]
    lines.extend(f"- {finding}" for finding in report["findings"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root.resolve(), args.contract)
    stream = sys.stderr if report["findings"] else sys.stdout
    if args.json:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    else:
        stream.write(render_report(report) + "\n")
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
