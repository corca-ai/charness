from __future__ import annotations

import importlib
import importlib.util
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

SCRIPT_REF_RE = re.compile(
    r"(?:^|\s)(?:bash|sh)?\s*(\./[A-Za-z0-9_./-]+\.sh|[A-Za-z0-9_./-]+\.sh)\b"
)
# One or more leading `VAR=value` env assignments on a command line.
ENV_PREFIX_RE = re.compile(r'^(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|\'[^\']*\'|\S*)\s+)+')
RUNNER_REF_RE = re.compile(
    r"(?:^|[\s&|;(])(?:(?:bash|sh|node|python3?|ruby)\s+|(?:deno|bun)\s+(?:run\s+)?)?(?:\./)?scripts/run-[A-Za-z0-9_-]+(?:\.(?:sh|mjs|cjs|js|ts|py|rb))?\b"
)
NESTED_SCRIPT_RE = re.compile(r"\b(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?([A-Za-z0-9:_-]+)\b")
VERBOSE_SCRIPT_RE = re.compile(r"\b[A-Za-z0-9:_-]*verbose[A-Za-z0-9:_-]*\b", re.IGNORECASE)
COMMAND_TOKEN_RE = re.compile(
    r"(^|&&\s*|\|\|\s*|;\s*|\(\s*|\s)(pytest|pylint|specdown|node|go|cargo|npm|pnpm|yarn|bun)\b"
)
QUALITY_GATES_PATH = ".agents/quality-gates.yaml"
_QUALITY_UNIVERSE_CACHE: dict[str, Any] = {}


def _split_chunks(command: str) -> list[str]:
    return [
        chunk.strip() for chunk in re.split(r"\s*(?:&&|\|\||;|\n)\s*", command) if chunk.strip()
    ]


def _yaml_block(text: str, key: str) -> str:
    block, started, indent = [], False, 0
    for line in text.splitlines():
        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip(" "))
        if not started:
            if stripped == f"{key}:":
                started, indent = True, current_indent
                block.append(line)
            continue
        if stripped and current_indent <= indent and re.match(r"[A-Za-z0-9_-]+:\s*$", stripped):
            break
        block.append(line)
    return "\n".join(block)


def _quality_gate_rows(repo_root: Path) -> list[dict[str, Any]] | None:
    """Read declared runner rows when present; absence keeps consumer fallback."""
    declaration = repo_root / QUALITY_GATES_PATH
    if not declaration.is_file():
        return None
    reader_path = repo_root / "scripts" / "quality_label_universe.py"
    if not reader_path.is_file():
        try:
            reader = importlib.import_module("scripts.quality_label_universe")
        except Exception as error:
            raise ValueError(
                f"{QUALITY_GATES_PATH} is present but {reader_path} is absent; "
                "the gate declaration cannot be read"
            ) from error
        return reader.quality_gate_rows(repo_root)
    cache_key = str(reader_path.resolve())
    reader = _QUALITY_UNIVERSE_CACHE.get(cache_key)
    if reader is None:
        scripts_dir = str(reader_path.parent)
        sys.path.insert(0, scripts_dir)
        try:
            module_name = f"charness_quality_label_universe_{abs(hash(cache_key))}"
            spec = importlib.util.spec_from_file_location(module_name, reader_path)
            if spec is None or spec.loader is None:
                raise ValueError(f"could not load {reader_path}")
            reader = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(reader)
            _QUALITY_UNIVERSE_CACHE[cache_key] = reader
        finally:
            if sys.path[0] == scripts_dir:
                sys.path.pop(0)
    return reader.quality_gate_rows(repo_root)


def _surface(
    path: Path,
    repo_root: Path,
    surface_type: str,
    commands: list[dict[str, str]],
    text: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(repo_root)),
        "surface_type": surface_type,
        "commands": commands,
        "metadata": metadata or {},
        "text": text,
    }


def _shell_surface(repo_root: Path, rel_path: str, surface_type: str) -> dict[str, Any] | None:
    path = repo_root / rel_path
    if not path.is_file():
        return None
    text, commands = path.read_text(encoding="utf-8"), []
    quality_rows = _quality_gate_rows(repo_root) if rel_path == "scripts/run-quality.sh" else None
    if quality_rows is not None:
        commands = [
            {
                "origin": "quality-gate-declaration",
                "snippet": shlex.join(row["command"]),
            }
            for row in quality_rows
        ]
        return _surface(
            path,
            repo_root,
            surface_type,
            commands,
            text,
            {"quality_gate_declaration": True},
        )
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(
            ("#", "echo ", "printf ", "if ", "elif ", "else", "fi")
        ):
            continue
        # `VAR=1 some-command` is a COMMAND with an env prefix, not an assignment.
        # Matching the prefix and skipping dropped the line entirely, so a runner
        # invoked with an environment prefix became invisible and the surface it
        # references was never discovered at all -- a silent loss of the whole
        # downstream inventory, not a missing snippet.
        stripped = ENV_PREFIX_RE.sub("", stripped)
        if not stripped or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$", stripped):
            continue
        if (
            COMMAND_TOKEN_RE.search(stripped)
            or 'queue_selected "pytest"' in stripped
            or SCRIPT_REF_RE.search(stripped)
        ):
            # `line` is additive: existing consumers read `origin`/`snippet` and
            # are unaffected. It exists so a dominated-command finding can name
            # WHICH line in a runner was judged -- without it an exemption keyed
            # to the file reads as a verdict about the whole file.
            commands.append({"origin": surface_type, "snippet": stripped, "line": line_number})
    return _surface(path, repo_root, surface_type, commands, text)


def _package_surface(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / "package.json"
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    scripts = payload.get("scripts", {}) if isinstance(payload, dict) else {}
    if not isinstance(scripts, dict):
        return None
    seeds = [
        name
        for name in ("pre-push", "prepush", "verify", "verify:local", "quality")
        if isinstance(scripts.get(name), str)
    ]
    if not seeds:
        return None
    commands, visited = [], set()

    def walk(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        raw = scripts.get(name)
        if not isinstance(raw, str):
            return
        for chunk in _split_chunks(raw):
            commands.append({"origin": f"script:{name}", "snippet": chunk})
            for nested in NESTED_SCRIPT_RE.findall(chunk):
                if nested in scripts:
                    walk(nested)

    for seed in seeds:
        walk(seed)
    metadata = {
        "seed_scripts": seeds,
        "verbose_scripts": sorted(
            name for name in scripts if isinstance(name, str) and VERBOSE_SCRIPT_RE.search(name)
        ),
    }
    return _surface(
        path,
        repo_root,
        "package_json",
        commands,
        json.dumps(payload, ensure_ascii=False, indent=2),
        metadata,
    )


def _lefthook_surface(repo_root: Path) -> dict[str, Any] | None:
    for name in ("lefthook.yml", "lefthook.yaml"):
        path = repo_root / name
        if not path.is_file():
            continue
        block = _yaml_block(path.read_text(encoding="utf-8"), "pre-push")
        if not block.strip():
            return None
        commands = [
            {"origin": "lefthook:pre-push", "snippet": match.strip()}
            for match in re.findall(r"(?m)^\s*run:\s*(.+)$", block)
        ]
        metadata = {
            "parallel": bool(re.search(r"(?m)^\s*parallel:\s*true\s*$", block)),
            "output_configured": bool(re.search(r"(?m)^\s*(?:output|skip_output):\s*\S", block)),
        }
        return _surface(path, repo_root, "lefthook", commands, block, metadata)
    return None


def _make_surface(repo_root: Path) -> dict[str, Any] | None:
    for name in ("Makefile", "GNUmakefile", "makefile"):
        path = repo_root / name
        if not path.is_file():
            continue
        commands, current, text = [], None, path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if re.match(r"^[A-Za-z0-9_.-]+:\s*(?:#.*)?$", line):
                target = line.split(":", 1)[0]
                current = target if target in {"pre-push", "prepush", "verify"} else None
            elif current and line.startswith("\t"):
                commands.append({"origin": f"make:{current}", "snippet": line.strip()})
        if commands:
            return _surface(path, repo_root, "makefile", commands, text)
    return None


def discover_surfaces(repo_root: Path) -> list[dict[str, Any]]:
    roots = [
        surface
        for surface in (
            _shell_surface(repo_root, ".githooks/pre-push", "git_hook"),
            _shell_surface(repo_root, ".husky/pre-push", "husky_hook"),
            _lefthook_surface(repo_root),
            _package_surface(repo_root),
            _make_surface(repo_root),
        )
        if surface is not None
    ]
    related, seen = [], {surface["path"] for surface in roots}
    queue = [
        Path(match.lstrip("./")).as_posix()
        for surface in roots
        for command in surface["commands"]
        for match in SCRIPT_REF_RE.findall(command["snippet"])
    ]
    while queue:
        rel_path = queue.pop(0)
        if rel_path in seen:
            continue
        surface = _shell_surface(repo_root, rel_path, "shell_script")
        if surface is None:
            continue
        seen.add(rel_path)
        related.append(surface)
        queue.extend(
            Path(match.lstrip("./")).as_posix()
            for command in surface["commands"]
            for match in SCRIPT_REF_RE.findall(command["snippet"])
        )
    return [*roots, *related]


def iter_snippets(surfaces: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "path": surface["path"],
            "origin": command["origin"],
            "snippet": command["snippet"],
            "line": command.get("line"),
        }
        for surface in surfaces
        for command in surface["commands"]
    ]
