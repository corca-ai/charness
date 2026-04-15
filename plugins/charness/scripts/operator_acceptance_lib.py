from __future__ import annotations

import re
from pathlib import Path
from typing import Any

EXCLUDED_DIRS = {".git", ".codex", ".claude", ".charness", "node_modules", "plugins", "charness-artifacts", ".venv", "venv"}
FUNCTIONAL_HEADING_RE = re.compile(r"^#{2,6}\s+.*functional check", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
FENCE_RE = re.compile(r"^```([A-Za-z0-9_-]+)?\s*$")
EXTERNAL_HINT_RE = re.compile(
    r"\b(gh|gws|slack|curl|wget|docker|podman|ssh|scp|codex|claude|cautilus|openai)\b|https?://"
)
RUNTIME_SIGNALS = (
    ("python", ("pyproject.toml", "requirements.txt", "uv.lock", "poetry.lock")),
    ("node", ("package.json", "pnpm-workspace.yaml", "package-lock.json", "yarn.lock")),
    ("go", ("go.mod",)),
)
SHARED_START_CANDIDATES = (
    ("git status --short", None),
    ("sed -n '1,220p' docs/handoff.md", "docs/handoff.md"),
    ("sed -n '1,260p' docs/roadmap.md 2>/dev/null || true", "docs/roadmap.md"),
    ("./scripts/run-quality.sh", "scripts/run-quality.sh"),
)


def _iter_markdown_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*.md"):
        relative = path.relative_to(repo_root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        files.append(relative)
    return sorted(files)


def _relative_link(path: str) -> str:
    return f"[{path}]({path})"


def _extract_functional_checks(repo_root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for relative in _iter_markdown_files(repo_root):
        lines = (repo_root / relative).read_text(encoding="utf-8", errors="replace").splitlines()
        context_heading = relative.name
        in_functional = False
        collecting = False
        skip_block = False
        buffer: list[str] = []

        for raw in lines:
            stripped = raw.strip()
            heading_match = HEADING_RE.match(stripped)
            if heading_match:
                heading_text = heading_match.group(2).strip()
                if FUNCTIONAL_HEADING_RE.match(stripped):
                    in_functional = True
                else:
                    context_heading = heading_text
                    in_functional = False
                continue

            fence_match = FENCE_RE.match(stripped)
            if fence_match:
                if not collecting and not skip_block:
                    language = (fence_match.group(1) or "").lower()
                    if in_functional and language in {"bash", "sh", "shell"}:
                        collecting = True
                        buffer = []
                    else:
                        skip_block = True
                    continue
                if collecting:
                    code = "\n".join(buffer).strip()
                    if code:
                        checks.append(
                            {
                                "label": context_heading,
                                "source_path": str(relative),
                                "commands": code,
                                "bucket": "external_or_costly" if EXTERNAL_HINT_RE.search(code) else "cheap_first",
                                "classification": "machine-external"
                                if EXTERNAL_HINT_RE.search(code)
                                else "machine-local",
                                "pass_criteria": ["exit_code:0"],
                            }
                        )
                    collecting = False
                    buffer = []
                    continue
                skip_block = False
                continue

            if collecting:
                buffer.append(raw.rstrip())
    return checks


def _detect_environment_prerequisites(repo_root: Path, checks: list[dict[str, Any]]) -> list[str]:
    prerequisites: list[str] = []
    for runtime_name, signals in RUNTIME_SIGNALS:
        if any((repo_root / signal).exists() for signal in signals):
            if runtime_name == "python":
                prerequisites.append("Ensure Python is available before running repo-owned Python helpers and checks.")
            elif runtime_name == "node":
                prerequisites.append("Ensure Node.js is available before running repo-owned package or workflow checks.")
            else:
                prerequisites.append("Ensure Go is available before running repo-owned Go build or test commands.")

    external_tools = sorted(
        {
            tool
            for item in checks
            for tool in ("gh", "gws", "slack", "curl", "docker", "codex", "claude", "cautilus")
            if tool in item["commands"]
        }
    )
    if external_tools:
        prerequisites.append(
            "External or account-bound checks reference these tools or services: "
            + ", ".join(f"`{tool}`" for tool in external_tools)
            + ". Verify the binary, auth, and network access before running those checks."
        )
    if (repo_root / "docs" / "control-plane.md").is_file():
        prerequisites.append(
            "Read " + _relative_link("docs/control-plane.md") + " before external or credentialed acceptance steps."
        )
    return prerequisites


def _shared_start_commands(repo_root: Path) -> list[str]:
    commands: list[str] = []
    for command, required_path in SHARED_START_CANDIDATES:
        if required_path is None or (repo_root / required_path).exists():
            commands.append(command)
    return commands


def _human_judgment_items(repo_root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for path, summary in (
        ("docs/handoff.md", "Review current repo state, recent decisions, and open coordination edges."),
        ("docs/roadmap.md", "Review remaining work ordering and confirm which items are still operator-owned."),
        ("docs/deferred-decisions.md", "Review reopen triggers or unresolved boundary decisions before deeper acceptance work."),
    ):
        if (repo_root / path).is_file():
            items.append({"source_path": path, "summary": summary})
    return items


def _render_check_section(title: str, items: list[dict[str, Any]]) -> str:
    lines = [f"## {title}", ""]
    if not items:
        lines.extend(["- none detected from current repo-owned checks", ""])
        return "\n".join(lines)
    for item in items:
        lines.extend(
            [
                f"### {item['label']}",
                "",
                f"Source: {_relative_link(item['source_path'])}",
                f"Type: `{item['classification']}`",
                "Pass when:",
                "- command exits 0",
                "",
                "```bash",
                item["commands"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def _render_human_section(items: list[dict[str, str]]) -> str:
    lines = ["## Human Judgment", ""]
    if not items:
        lines.extend(["- none detected from current repo docs", ""])
        return "\n".join(lines)
    for item in items:
        lines.append(f"- Review {_relative_link(item['source_path'])}: {item['summary']}")
    lines.append("")
    return "\n".join(lines)


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Operator Acceptance",
        "",
        "This document translates current repo-owned checks and takeover steps into operator-owned acceptance runs.",
        "",
        "## Shared Start",
        "",
        "Run these first at the repo root:",
        "",
        "```bash",
        *payload["shared_start_commands"],
        "```",
        "",
        "## Environment Prerequisites",
        "",
    ]
    prerequisites = payload["environment_prerequisites"]
    if prerequisites:
        lines.extend(f"- {item}" for item in prerequisites)
    else:
        lines.append("- No explicit environment prerequisites were inferred from the current repo surface.")
    lines.extend(
        [
            "",
            _render_check_section("Cheap First", payload["acceptance_buckets"]["cheap_first"]),
            _render_check_section("External Or Costly Checks", payload["acceptance_buckets"]["external_or_costly"]),
            _render_human_section(payload["acceptance_buckets"]["human_judgment"]),
            "## Closeout Rule",
            "",
            "- keep machine-local, external-or-costly, and human-judgment items distinct",
            "- update this doc when standing repo-owned checks or takeover steps change",
            "- prefer repo-owned commands over handwritten ritual whenever the repo already exposes one",
            "",
        ]
    )
    return "\n".join(lines)


def synthesize_operator_acceptance(
    *, repo_root: Path, output_path: Path, write: bool, force: bool
) -> dict[str, Any]:
    checks = _extract_functional_checks(repo_root)
    payload = {
        "repo": repo_root.name,
        "output_path": str(output_path if output_path.is_absolute() else repo_root / output_path),
        "shared_start_commands": _shared_start_commands(repo_root),
        "environment_prerequisites": _detect_environment_prerequisites(repo_root, checks),
        "acceptance_buckets": {
            "cheap_first": [item for item in checks if item["bucket"] == "cheap_first"],
            "external_or_costly": [item for item in checks if item["bucket"] == "external_or_costly"],
            "human_judgment": _human_judgment_items(repo_root),
        },
        "sources": sorted({item["source_path"] for item in checks}),
    }
    payload["markdown"] = _render_markdown(payload)

    resolved_output = output_path if output_path.is_absolute() else repo_root / output_path
    if write:
        if resolved_output.exists() and not force:
            raise SystemExit(f"Output already exists at {resolved_output}. Use --force to overwrite.")
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(payload["markdown"], encoding="utf-8")

    return payload
