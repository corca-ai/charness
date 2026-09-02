#!/usr/bin/env python3
"""Extract the live ``run-quality.sh`` queue into its declarative gate list."""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script
from scripts import quality_label_universe
from yaml_output import render_yaml

REPO_ROOT = repo_root_from_script(__file__)
OUTPUT_PATH = quality_label_universe.QUALITY_GATES_PATH
RUNNER_PATH = quality_label_universe.RUN_QUALITY_PATH
TIMING_PATH = Path("docs/validator-timing-layers.md")
PRE_PUSH_PATH = Path(".githooks/pre-push")

PHASES = (
    (
        "pytest",
        900,
        978,
        "alone",
        True,
        "standing pytest failed; stopping before later quality checks.",
    ),
    ("agent-browser-baseline", 979, 990, "alone", True, None),
    ("main", 991, 1245, "concurrent", False, None),
    ("inventory-declaration", 1246, 1257, "alone", False, None),
    ("post-pytest-tree", 1258, 1305, "concurrent", False, None),
    ("runtime-budget", 1306, 1312, "alone", False, None),
    ("agent-browser-hygiene", 1313, 1323, "alone", False, None),
    ("release-final", 1324, 1350, "alone", False, None),
)

_DOCS_ONLY_RE = re.compile(r'^DOCS_ONLY_LABELS="([^"]*)"', re.MULTILINE)
_CORE_RE = re.compile(r'^RUN_QUALITY_CORE_LABELS="([^"]*)"', re.MULTILINE)
_UNESTABLISHED_RE = re.compile(r'^UNESTABLISHED_CAPABLE_LABELS="([^"]*)"', re.MULTILINE)
_NATIVE_RE = re.compile(r'^NATIVE_GATE_LABELS="([^"]*)"', re.MULTILINE)


def _render_yaml(payload: dict[str, Any]) -> str:
    """Emit block lists without wrapping command scalars into parser gaps."""
    try:
        import yaml
    except ImportError:
        return render_yaml(payload)
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=4096)


def _shell_logical_lines(text: str) -> list[tuple[int, str]]:
    """Join bash continuations and queue payloads that span quoted lines."""
    physical = text.splitlines()
    result: list[tuple[int, str]] = []
    index = 0
    while index < len(physical):
        first = index + 1
        line = physical[index]
        index += 1
        while line.rstrip().endswith("\\") and not line.lstrip().startswith("#"):
            line = line.rstrip()[:-1].rstrip()
            if index >= len(physical):
                break
            line += " " + physical[index].strip()
            index += 1

        match = quality_label_universe._QUEUE_CALL_RE.match(line)
        if match is not None:
            while True:
                try:
                    shlex.split(line[match.end("fn") :].strip(), comments=False, posix=True)
                    break
                except ValueError as error:
                    if "No closing quotation" not in str(error) or index >= len(physical):
                        raise quality_label_universe.UniverseError(
                            f"{RUNNER_PATH}:{first}: queue command cannot be parsed: {error}"
                        ) from error
                    line += "\n" + physical[index]
                    index += 1
        result.append((first, line))
    return result


def _queue_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_function: str | None = None
    for lineno, line in _shell_logical_lines(text):
        opened = quality_label_universe._FUNCTION_OPEN_RE.match(line)
        if opened is not None:
            current_function = opened.group("name")
            continue
        if current_function is not None and quality_label_universe._FUNCTION_CLOSE_RE.match(line):
            current_function = None
            continue
        call = quality_label_universe._QUEUE_CALL_RE.match(line)
        if call is None or current_function in quality_label_universe.QUEUE_FUNCTIONS:
            continue
        literal = quality_label_universe._LITERAL_LABEL_RE.match(call.group("rest"))
        if literal is None:
            raise quality_label_universe.UniverseError(
                f"{RUNNER_PATH}:{lineno}: queue call has a non-literal label {call.group('rest')!r}"
            )
        label = literal.group("label")
        if not quality_label_universe._LABEL_SHAPE_RE.fullmatch(label):
            raise quality_label_universe.UniverseError(
                f"{RUNNER_PATH}:{lineno}: invalid queue label {label!r}"
            )
        command_text = line[call.end("fn") :].strip()
        tokens = shlex.split(command_text, comments=False, posix=True)
        if len(tokens) < 2:
            raise quality_label_universe.UniverseError(
                f"{RUNNER_PATH}:{lineno}: queue label {label!r} has no command"
            )
        rows.append({"label": label, "command": tokens[1:], "line": lineno, "fn": call.group("fn")})
    if not rows:
        raise quality_label_universe.UniverseError(f"{RUNNER_PATH} contains zero queue call sites")
    return rows


def _phase_for(line: int) -> tuple[str, str, bool, str | None]:
    for phase_id, start, end, isolation, fail_fast, fail_message in PHASES:
        if start <= line <= end:
            return phase_id, isolation, fail_fast, fail_message
    raise quality_label_universe.UniverseError(
        f"{RUNNER_PATH}:{line}: queue call is outside the declared phase ranges"
    )


def _first_match(text: str, pattern: re.Pattern[str]) -> set[str]:
    match = pattern.search(text)
    return set(match.group(1).split()) if match else set()


def _timing_layers(repo_root: Path) -> dict[str, str]:
    path = repo_root / TIMING_PATH
    if not path.is_file():
        raise quality_label_universe.UniverseError(f"{TIMING_PATH} is missing")
    text = path.read_text(encoding="utf-8")
    start = text.find("## Classification table")
    if start == -1:
        raise quality_label_universe.UniverseError(f"{TIMING_PATH} has no classification table")
    region = text[start:].split("\n## ", 1)[0]
    layers: dict[str, str] = {}
    for line in region.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].startswith("---") or cells[0] == "Check (broad-gate label)":
            continue
        for label in cells[0].split(","):
            label = label.strip().strip("`*_ ")
            if label:
                layers[label] = cells[2]
    return layers


def _condition(label: str, line: int) -> dict[str, Any] | None:
    if label == "dead-code-advisory":
        return {"env": {"CHARNESS_QUALITY_DEAD_CODE": "1"}}
    if label == "check-supply-chain-online":
        return {"env": {"CHARNESS_SUPPLY_CHAIN_ONLINE": "1"}}
    if label in {"agent-browser-runtime-baseline", "agent-browser-runtime-hygiene"}:
        return {"env": {"CHARNESS_AGENT_BROWSER_RUNTIME_HYGIENE": "1"}}
    if label == "check-coverage":
        return {
            "mode_in": ["full", "read-only"],
            "predicate": "coverage_relevant_changes_present",
        }
    if label == "check-runtime-budget":
        return {
            "predicate": "runtime_profile_present" if line == 1307 else "runtime_profile_absent"
        }
    if label == "check-provenance-contract":
        return {
            "predicate": "provenance_contract_checker_available"
            if line == 1215
            else "provenance_contract_checker_unavailable"
        }
    if label == "inventory-gitignore-scan-hygiene":
        return (
            {"file_exists": "skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py"}
            if line == 1283
            else {"predicate": "inventory_gitignore_scan_hygiene_unavailable"}
        )
    if label == "inventory-cli-ergonomics":
        return (
            {"file_exists": "skills/public/quality/scripts/inventory_cli_ergonomics.py"}
            if line == 1295
            else {"predicate": "inventory_cli_ergonomics_unavailable"}
        )
    if label == "inventory-nose-clones":
        return (
            {"file_exists": "skills/public/quality/scripts/inventory_nose_clones.py"}
            if line == 1300
            else {"predicate": "inventory_nose_clones_unavailable"}
        )
    if label == "release-changed-line-coverage":
        return {
            "predicate": "release_final_base_sha_present"
            if line == 1329
            else "release_final_base_sha_absent"
        }
    return None


def _lane(label: str, core: set[str]) -> str:
    if label in core:
        return "core"
    if label in {
        "pytest-release",
        "validate-packaging-committed",
        "check-command-docs",
        "check-test-production-ratio",
        "release-changed-line-coverage",
    }:
        return "release-only"
    if label in {
        "check-doc-links",
        "docs-graph",
        "check-plugin-doc-links",
        "check-markdown",
        "check-links-internal",
        "check-links-external",
    }:
        return "label-only"
    if label in {
        "dead-code-advisory",
        "check-supply-chain-online",
        "agent-browser-runtime-baseline",
        "agent-browser-runtime-hygiene",
    }:
        return "opt-in"
    return "standard"


def extract(repo_root: Path) -> dict[str, Any]:
    runner = repo_root / RUNNER_PATH
    if not runner.is_file():
        raise quality_label_universe.UniverseError(f"{RUNNER_PATH} is missing")
    runner_text = runner.read_text(encoding="utf-8")
    pre_push = (repo_root / PRE_PUSH_PATH).read_text(encoding="utf-8")
    timing = _timing_layers(repo_root)
    core = _first_match(runner_text, _CORE_RE)
    unestablished = _first_match(runner_text, _UNESTABLISHED_RE)
    native = _first_match(runner_text, _NATIVE_RE)
    docs_only_match = _DOCS_ONLY_RE.search(pre_push)
    docs_only = set(docs_only_match.group(1).split(",")) if docs_only_match else set()

    extracted = _queue_rows(runner_text)
    phases: list[dict[str, Any]] = []
    for phase_id, *_ in PHASES:
        phase_rows = [row for row in extracted if _phase_for(row["line"])[0] == phase_id]
        if not phase_rows:
            continue
        _, isolation, fail_fast, fail_message = _phase_for(phase_rows[0]["line"])
        gates: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in phase_rows:
            label = raw["label"]
            gate: dict[str, Any] = {
                "label": label,
                "command": raw["command"],
                "lane": _lane(label, core),
            }
            condition = _condition(label, raw["line"])
            if condition:
                gate["condition"] = condition
            if label in seen:
                gate["variant_of"] = label
            elif label == "pytest-release":
                gate["variant_of"] = "pytest"
            seen.add(label)
            if label in unestablished:
                gate["unestablished_capable"] = True
            if label in native:
                gate["native_preflight"] = True
            layer = timing.get(label)
            if not layer:
                raise quality_label_universe.UniverseError(
                    f"{TIMING_PATH}: no timing layer for queued label {label!r}"
                )
            gate["timing_layer"] = layer
            if label in docs_only:
                gate["docs_only"] = True
            note = f"src {RUNNER_PATH}:{raw['line']}; labels literal (475-479)."
            if label in {"doc-duplicates", "dup-ratchet"}:
                note = f"src {RUNNER_PATH}:{raw['line']}; phase barrier (1134-1143); labels literal (475-479)."
            if label == "check-seed-fixture-budget":
                note = f"src {RUNNER_PATH}:{raw['line']}; pytest tree barrier (1260-1274); labels literal (475-479)."
            gate["note"] = note
            gates.append(gate)
        phase: dict[str, Any] = {
            "id": phase_id,
            "isolation": isolation,
            "fail_fast": fail_fast,
            "gates": gates,
        }
        if fail_message:
            phase["fail_message"] = fail_message
        phases.append(phase)

    return {
        "schema": quality_label_universe.QUALITY_GATES_SCHEMA,
        "runner_variables": {
            "REPO_ROOT": "absolute repository root resolved by run-quality.sh",
            "PYTEST_FLAGS": "pytest args for mode and release-only selection",
            "STANDING_PYTEST_TARGETS": "expanded pytest targets from run_standing_pytest.py",
            "python_files": "Python files matched by recursive compile globs",
            "seed_budget_args": "seed-budget args, including advisory opt-in",
            "RUN_QUALITY_TMPDIR": "per-run temporary directory for reports and logs",
            "RUN_QUALITY_STATE_ROOT_ARGS": "optional runtime state-root arguments",
            "RUN_QUALITY_RUNTIME_ROOT": "runtime state root for release proof output",
            "RUN_QUALITY_RUNTIME_PROFILE": "selected runtime budget profile",
            "RUN_QUALITY_INCLUDE_RELEASE_ONLY": "release-only flag for inline fallbacks",
            "PROVENANCE_CONTRACT_CHECKER": "first packaged provenance checker path",
            "CRITIQUE_CHANGED_REF": "changed range from the origin/main merge-base",
            "CHANGED_LINE_BASE_SHA": "origin/main merge-base for changed-line proof",
            "release_changed_line_coverage_json": "release changed-line coverage path",
            "specdown_config": "ephemeral specdown config from its inline command",
        },
        "phases": phases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the extracted YAML to .agents/quality-gates.yaml",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the checked-in gate list matches the live runner extraction",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        payload = extract(repo_root)
    except quality_label_universe.UniverseError as error:
        print(f"quality gate extraction: {error}", file=sys.stderr)
        return 1
    output = repo_root / OUTPUT_PATH
    rendered = _render_yaml(payload)
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            print(f"{OUTPUT_PATH} is not the current extraction", file=sys.stderr)
            return 1
        print(f"{OUTPUT_PATH}: current")
        return 0
    if args.write:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"wrote {OUTPUT_PATH}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
