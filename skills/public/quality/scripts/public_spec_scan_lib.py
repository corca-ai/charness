from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import public_spec_quality_lib as qlib
from public_spec_adapter_policy import (
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR,
    DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS,
    DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS,
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
    option,
)

FENCE_RE = re.compile(r"^```(?P<info>[^`]*)$")
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*#*\s*$")
SOURCE_GUARD_ROW_RE = re.compile(r"^\|\s*[^|]+?\s*\|\s*(?:fixed|source_guard)\s*\|", re.IGNORECASE)
SOURCE_GUARD_TOKEN_RE = re.compile(r"\bsource_guard\b", re.IGNORECASE)
IMPLEMENTATION_PATH_RE = re.compile(r"`?(?:internal|src|scripts|skills|tests|cmd|app|pkg|lib)/[A-Za-z0-9._/\-]+`?")
PYTEST_REFERENCE_CONTINUATION_RE = re.compile(r"^\s*`tests/[^`]+`(?:,\s*`tests/[^`]+`)*[,.]?\s*$")
FUTURE_STATE_RE = re.compile(r"\b(future|planned|roadmap|next session|later|todo|deferred|defer)\b", re.IGNORECASE)
RUNNER_DELEGATION_RE = re.compile(r"^(pytest|go test|cargo test|npm test|pnpm test|yarn test|bun test|specdown run)\b")
COMMAND_START_RE = re.compile(r"^[A-Za-z0-9._/\-]+(?:\s+.+)?$")
SHELL_INFOS = {"bash", "sh", "shell", "console", "zsh", "run:shell"}


def _normalize_heading(title: str) -> str:
    return " ".join(title.strip().strip("#").split()).casefold()


def _split_markdown(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    prose: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    current: list[str] = []
    current_info = ""
    heading_stack: list[tuple[int, str]] = []
    in_fence = False
    for line in text.splitlines():
        match = FENCE_RE.match(line.strip())
        if match:
            if in_fence:
                blocks.append({"info": current_info, "lines": current})
                current, current_info, in_fence = [], "", False
            else:
                in_fence, current_info = True, (match.group("info") or "").lower()
            continue
        if in_fence:
            current.append(line.rstrip())
            continue
        stripped = line.rstrip()
        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group("marks"))
            title = " ".join(heading_match.group("title").strip().split())
            heading_stack = [item for item in heading_stack if item[0] < level]
            heading_stack.append((level, title))
            prose.append({"line": stripped, "headings": [item[1] for item in heading_stack], "is_heading": True})
        else:
            prose.append({"line": stripped, "headings": [item[1] for item in heading_stack], "is_heading": False})
    return prose, blocks


def _front_matter_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    front_matter: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            return front_matter
        front_matter.append(line.rstrip())
    return []


def _is_exempt(record: dict[str, Any], exemptions: set[str]) -> bool:
    return any(_normalize_heading(heading) in exemptions for heading in record["headings"])


def _regex_count(pattern: str, lines: list[str]) -> int:
    if not pattern:
        return 0
    try:
        compiled = re.compile(pattern)
    except re.error:
        return 0
    return sum(1 for line in lines if compiled.search(line))


def _implementation_scan_lines(lines: list[str], spec_ref_re: re.Pattern[str] | None) -> list[str]:
    if spec_ref_re is None:
        return lines
    excluded: set[int] = set()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not spec_ref_re.search(line):
            index += 1
            continue
        excluded.add(index)
        continuation = index + 1
        while continuation < len(lines):
            candidate = lines[continuation]
            if not candidate.strip():
                break
            if not PYTEST_REFERENCE_CONTINUATION_RE.match(candidate):
                break
            excluded.add(continuation)
            continuation += 1
        index = continuation
    return [line for line_index, line in enumerate(lines) if line_index not in excluded]


def _pointer_proof_info(text: str, body_lines: list[str], data: dict[str, Any]) -> dict[str, Any]:
    spec_format = option(data, "spec_pytest_reference_format", DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT)
    pytest_count = _regex_count(str(spec_format or ""), body_lines)
    markers = option(data, "public_spec_pointer_proof_markers", DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS)
    marker_set = {str(item).strip().casefold() for item in markers if str(item).strip()} if isinstance(markers, list) else set()
    marker_count = sum(1 for line in _front_matter_lines(text) if line.strip().casefold() in marker_set)
    return {"has_pointer_proof": pytest_count > 0 or marker_count > 0, "pytest_reference_count": pytest_count, "front_matter_marker_count": marker_count, "spec_pytest_reference_format": spec_format}


def _normalize_command(line: str) -> str:
    command = line.strip()
    for prefix in ("$ ", "$", "! ", "!"):
        if command.startswith(prefix):
            command = command[len(prefix):].lstrip()
            break
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
            candidate_lines = prompted or candidate_lines
        for raw in candidate_lines:
            stripped = raw.strip()
            normalized = _normalize_command(stripped)
            if stripped and not stripped.startswith(("#", ">")) and COMMAND_START_RE.match(normalized):
                commands.append(normalized)
    return commands


def _scan_prose(prose_records: list[dict[str, Any]], body_records: list[dict[str, Any]], text: str, data: dict[str, Any]) -> dict[str, Any]:
    section_exemptions = option(data, "public_spec_section_exemptions", DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS)
    exemptions = {_normalize_heading(str(item)) for item in section_exemptions if str(item).strip()} if isinstance(section_exemptions, list) else set()
    scan_lines = [record["line"] for record in prose_records if not _is_exempt(record, exemptions)]
    pointer = _pointer_proof_info(text, [record["line"] for record in body_records], data)
    try:
        spec_ref_re = re.compile(str(pointer["spec_pytest_reference_format"] or ""))
    except re.error:
        spec_ref_re = None
    impl_lines = _implementation_scan_lines(scan_lines, spec_ref_re)
    impl_refs = [ref for line in impl_lines for ref in IMPLEMENTATION_PATH_RE.findall(line)]
    total_impl = len(IMPLEMENTATION_PATH_RE.findall("\n".join(record["line"] for record in prose_records)))
    density_floor = option(data, "public_spec_implementation_ref_density_floor", DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR)
    density_floor = float(density_floor) if isinstance(density_floor, (int, float)) else DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR
    line_count = sum(1 for line in impl_lines if line.strip())
    density = len(impl_refs) / line_count if line_count else 0.0
    future_terms = [term for line in scan_lines for term in FUTURE_STATE_RE.findall(line)]
    total_future = len(FUTURE_STATE_RE.findall("\n".join(record["line"] for record in prose_records)))
    return {"impl_refs": impl_refs, "impl_total": total_impl, "impl_density": density, "density_floor": density_floor, "future_terms": future_terms, "future_total": total_future, "pointer": pointer}


def spec_inventory(repo_root: Path, spec_path: Path, data: dict[str, Any]) -> dict[str, Any]:
    text = spec_path.read_text(encoding="utf-8", errors="replace")
    prose_records, blocks = _split_markdown(text)
    prose_lines = [record["line"] for record in prose_records]
    body_records = [record for record in prose_records if not record["is_heading"]]
    commands = _command_examples(blocks)
    source_guard_rows = sum(1 for line in text.splitlines() if SOURCE_GUARD_ROW_RE.match(line))
    source_guard_tokens = len(SOURCE_GUARD_TOKEN_RE.findall("\n".join(prose_lines)))
    scan = _scan_prose(prose_records, body_records, text, data)
    heuristics: list[str] = []
    if source_guard_rows >= 1 or source_guard_tokens >= 2:
        heuristics.append("source_inventory_pressure")
    if len(scan["impl_refs"]) >= 2 and scan["impl_density"] > scan["density_floor"]:
        heuristics.append("implementation_guard_pressure")
    if scan["future_terms"]:
        heuristics.append("future_state_mixed")
    if not blocks:
        if not scan["pointer"]["has_pointer_proof"]:
            heuristics.append("no_executable_proof_blocks")
    elif not commands:
        heuristics.append("non_command_executable_blocks")
    if any(RUNNER_DELEGATION_RE.match(command) for command in commands):
        heuristics.append("delegated_test_runner_proof")
    return _spec_payload(repo_root, spec_path, blocks, commands, source_guard_rows, source_guard_tokens, scan, heuristics)


def _spec_payload(repo_root: Path, spec_path: Path, blocks: list[dict[str, Any]], commands: list[str], source_guard_rows: int, source_guard_tokens: int, scan: dict[str, Any], heuristics: list[str]) -> dict[str, Any]:
    return {
        "spec_path": spec_path.relative_to(repo_root).as_posix(),
        "executable_block_count": len(blocks),
        "command_examples": commands,
        "source_guard_row_count": source_guard_rows,
        "source_guard_token_count": source_guard_tokens,
        "implementation_path_ref_count": len(scan["impl_refs"]),
        "implementation_path_ref_total_count": scan["impl_total"],
        "implementation_path_ref_exempt_count": max(0, scan["impl_total"] - len(scan["impl_refs"])),
        "implementation_path_ref_density": round(scan["impl_density"], 4),
        "implementation_path_ref_density_floor": scan["density_floor"],
        "future_state_term_count": len(scan["future_terms"]),
        "future_state_term_total_count": scan["future_total"],
        "future_state_term_exempt_count": max(0, scan["future_total"] - len(scan["future_terms"])),
        "pointer_proof_reference_count": scan["pointer"]["pytest_reference_count"],
        "pointer_proof_marker_count": scan["pointer"]["front_matter_marker_count"],
        "heuristics": heuristics,
        "review_prompts": qlib.REVIEW_PROMPTS,
    }
