#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

IGNORED_PARTS = {".git", ".charness", "__pycache__", "node_modules", "plugins", "evals"}
FENCE_RE = re.compile(r"^```(?P<info>[^`]*)$")
SOURCE_GUARD_ROW_RE = re.compile(r"^\|\s*[^|]+?\s*\|\s*(?:fixed|source_guard)\s*\|", re.IGNORECASE)
SOURCE_GUARD_TOKEN_RE = re.compile(r"\bsource_guard\b", re.IGNORECASE)
IMPLEMENTATION_PATH_RE = re.compile(
    r"`?(?:internal|src|scripts|skills|tests|cmd|app|pkg|lib)/[A-Za-z0-9._/\-]+`?"
)
FUTURE_STATE_RE = re.compile(
    r"\b(future|planned|roadmap|next session|later|todo|deferred|defer)\b",
    re.IGNORECASE,
)
RUNNER_DELEGATION_RE = re.compile(
    r"^(pytest|go test|cargo test|npm test|pnpm test|yarn test|bun test|specdown run)\b"
)
COMMAND_START_RE = re.compile(r"^[A-Za-z0-9._/\-]+(?:\s+.+)?$")
SHELL_INFOS = {"bash", "sh", "shell", "console", "zsh", "run:shell"}
REVIEW_PROMPTS = [
    "Keep public executable pages reader-facing: current claims first, internal structure second.",
    "Check whether source inventory or implementation pinning became the main proof surface.",
    "Audit proof layering, not only proof presence: duplicated happy paths at the wrong layer create maintenance drag.",
    "Delete repeated public-spec, smoke, or on-demand E2E proof once a narrower layer owns the claim honestly.",
]


def _iter_public_specs(repo_root: Path) -> list[Path]:
    specs: list[Path] = []
    for path in repo_root.rglob("*.spec.md"):
        if any(part in IGNORED_PARTS for part in path.relative_to(repo_root).parts):
            continue
        specs.append(path)
    return sorted(specs)

def _iter_smoke_like_tests(repo_root: Path) -> tuple[list[str], list[str]]:
    smoke_paths: list[str] = []
    e2e_paths: list[str] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        parts = path.relative_to(repo_root).parts
        if any(part in IGNORED_PARTS for part in parts):
            continue
        rel = path.relative_to(repo_root).as_posix()
        lowered = rel.lower()
        if "smoke" in lowered and rel not in smoke_paths:
            smoke_paths.append(rel)
        if ("e2e" in lowered or "end_to_end" in lowered) and rel not in e2e_paths:
            e2e_paths.append(rel)
    return sorted(smoke_paths), sorted(e2e_paths)


def _split_fences(text: str) -> tuple[list[str], list[dict[str, Any]]]:
    prose_lines: list[str] = []
    blocks: list[dict[str, Any]] = []
    current: list[str] = []
    current_info = ""
    in_fence = False
    for line in text.splitlines():
        match = FENCE_RE.match(line.strip())
        if match:
            if in_fence:
                blocks.append({"info": current_info, "lines": current})
                current = []
                current_info = ""
                in_fence = False
            else:
                in_fence = True
                current_info = (match.group("info") or "").lower()
            continue
        if in_fence:
            current.append(line.rstrip())
        else:
            prose_lines.append(line.rstrip())
    return prose_lines, blocks


def _normalize_command(line: str) -> str:
    command = line.strip()
    if command.startswith("$ "):
        command = command[2:]
    elif command.startswith("$"):
        command = command[1:].lstrip()
    elif command.startswith("! "):
        command = command[2:]
    elif command.startswith("!"):
        command = command[1:].lstrip()
    return " ".join(command.split())

def _normalized_info(info: str) -> str:
    return info.strip().split()[0].lower() if info.strip() else ""


def _command_examples(blocks: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    for block in blocks:
        info = _normalized_info(str(block["info"]))
        if info and info not in SHELL_INFOS:
            continue
        candidate_lines = list(block["lines"])
        if info.startswith("run:"):
            prompted = [raw for raw in candidate_lines if raw.lstrip().startswith(("$", "!"))]
            if prompted:
                candidate_lines = prompted
        for raw in candidate_lines:
            stripped = raw.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith(">"):
                continue
            normalized = _normalize_command(stripped)
            if not COMMAND_START_RE.match(normalized):
                continue
            commands.append(normalized)
    return commands


def _spec_inventory(repo_root: Path, spec_path: Path) -> dict[str, Any]:
    text = spec_path.read_text(encoding="utf-8", errors="replace")
    prose_lines, blocks = _split_fences(text)
    prose = "\n".join(prose_lines)
    commands = _command_examples(blocks)
    source_guard_rows = sum(1 for line in text.splitlines() if SOURCE_GUARD_ROW_RE.match(line))
    source_guard_tokens = len(SOURCE_GUARD_TOKEN_RE.findall(prose))
    implementation_refs = IMPLEMENTATION_PATH_RE.findall(prose)
    future_terms = FUTURE_STATE_RE.findall(prose)
    heuristics: list[str] = []
    if source_guard_rows >= 1 or source_guard_tokens >= 2:
        heuristics.append("source_inventory_pressure")
    if len(implementation_refs) >= 2:
        heuristics.append("implementation_guard_pressure")
    if future_terms:
        heuristics.append("future_state_mixed")
    if not blocks:
        heuristics.append("no_executable_proof_blocks")
    elif not commands:
        heuristics.append("non_command_executable_blocks")
    if any(RUNNER_DELEGATION_RE.match(command) for command in commands):
        heuristics.append("delegated_test_runner_proof")
    return {
        "spec_path": spec_path.relative_to(repo_root).as_posix(),
        "executable_block_count": len(blocks),
        "command_examples": commands,
        "source_guard_row_count": source_guard_rows,
        "source_guard_token_count": source_guard_tokens,
        "implementation_path_ref_count": len(implementation_refs),
        "future_state_term_count": len(future_terms),
        "heuristics": heuristics,
        "review_prompts": REVIEW_PROMPTS,
    }


def inventory(repo_root: Path) -> dict[str, Any]:
    specs = [_spec_inventory(repo_root, path) for path in _iter_public_specs(repo_root)]
    duplicate_map: dict[str, list[str]] = {}
    for spec in specs:
        for command in spec["command_examples"]:
            duplicate_map.setdefault(command, []).append(spec["spec_path"])
    duplicates = [
        {"command": command, "spec_paths": sorted(paths)}
        for command, paths in sorted(duplicate_map.items())
        if len(set(paths)) >= 2
    ]
    smoke_paths, e2e_paths = _iter_smoke_like_tests(repo_root)
    runner_specs = sorted(
        spec["spec_path"] for spec in specs if "delegated_test_runner_proof" in spec["heuristics"]
    )
    recommendations: list[dict[str, Any]] = []
    layering_heuristics: list[str] = []
    if duplicates:
        layering_heuristics.append("duplicate_public_spec_examples")
        recommendations.append(
            {
                "action": "delete_or_merge",
                "scope": "public-spec",
                "target": "duplicate_command_examples",
                "target_items": duplicates,
                "guidance": (
                    "Keep one representative public-spec proof per happy-path command, "
                    "then delete or merge repeated public-spec copies."
                ),
            }
        )
    if runner_specs:
        layering_heuristics.append("delegated_test_runner_inside_public_spec")
        recommendations.append(
            {
                "action": "move_down",
                "scope": "public-spec",
                "target": "delegated_runner_specs",
                "target_items": runner_specs,
                "guidance": (
                    "Replace delegated test-runner proof with direct reader-facing command proof in the public spec, "
                    "and keep detailed assertions in app, unit, or smoke layers."
                ),
            }
        )
    if smoke_paths:
        recommendations.append(
            {
                "action": "keep_if_integration_value",
                "scope": "smoke",
                "target": "smoke_test_paths",
                "target_items": smoke_paths,
                "keep_when": [
                    "the smoke test proves a cross-command flow",
                    "the smoke test mutates a repo or artifact boundary",
                    "a narrower layer cannot own the seam honestly",
                ],
                "delete_when": [
                    "the smoke test only repeats the same happy-path claim already owned by a public spec",
                    "lower-layer tests already own the behavior and the smoke adds no repo-mutation value",
                ],
            }
        )
    if e2e_paths:
        recommendations.append(
            {
                "action": "keep_if_integration_value",
                "scope": "on-demand-e2e",
                "target": "e2e_test_paths",
                "target_items": e2e_paths,
                "keep_when": [
                    "the E2E path proves an external-consumer or environment-heavy seam",
                    "the flow is too expensive or unstable for standing smoke or public-spec ownership",
                ],
                "delete_when": [
                    "the E2E path only repeats a cheap happy-path contract already owned by a public spec or smoke test",
                ],
            }
        )
    if (smoke_paths or e2e_paths) and (duplicates or runner_specs):
        layering_heuristics.append("proof_layering_review_needed")
    return {
        "repo_root": str(repo_root),
        "summary": {
            "public_spec_count": len(specs),
            "flagged_spec_count": sum(1 for spec in specs if spec["heuristics"]),
            "duplicate_command_count": len(duplicates),
            "smoke_test_count": len(smoke_paths),
            "e2e_test_count": len(e2e_paths),
        },
        "public_specs": specs,
        "layering": {
            "duplicate_command_examples": duplicates,
            "smoke_test_paths": smoke_paths,
            "e2e_test_paths": e2e_paths,
            "delegated_runner_specs": runner_specs,
            "heuristics": layering_heuristics,
            "review_prompts": REVIEW_PROMPTS,
            "recommendations": recommendations,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = inventory(args.repo_root.resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for spec in payload["public_specs"]:
            heuristics = ", ".join(spec["heuristics"]) or "none"
            print(f"{spec['spec_path']}: heuristics={heuristics}")
        if payload["layering"]["heuristics"]:
            print(f"layering: {', '.join(payload['layering']['heuristics'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
