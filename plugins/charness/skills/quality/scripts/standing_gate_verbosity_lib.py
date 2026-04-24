from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCRIPT_REF_RE = re.compile(r"(?:^|\s)(?:bash|sh)?\s*(\./[A-Za-z0-9_./-]+\.sh|[A-Za-z0-9_./-]+\.sh)\b")
RUNNER_REF_RE = re.compile(r"(?:^|[\s&|;(])(?:(?:bash|sh|node|python3?|ruby)\s+|(?:deno|bun)\s+(?:run\s+)?)?(?:\./)?scripts/run-[A-Za-z0-9_-]+(?:\.(?:sh|mjs|cjs|js|ts|py|rb))?\b")
NESTED_SCRIPT_RE = re.compile(r"\b(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?([A-Za-z0-9:_-]+)\b")
VERBOSE_SCRIPT_RE = re.compile(r"\b[A-Za-z0-9:_-]*verbose[A-Za-z0-9:_-]*\b", re.IGNORECASE)
VERBOSE_VAR_RE = re.compile(r"\b[A-Z][A-Z0-9_]*VERBOSE[A-Z0-9_]*\b")
COMMAND_TOKEN_RE = re.compile(r"(^|&&\s*|\|\|\s*|;\s*|\(\s*|\s)(pytest|pylint|specdown|node|go|cargo|npm|pnpm|yarn|bun)\b")
def _split_chunks(command: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\s*(?:&&|\|\||;|\n)\s*", command) if chunk.strip()]

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
def _surface(path: Path, repo_root: Path, surface_type: str, commands: list[dict[str, str]], text: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"path": str(path.relative_to(repo_root)), "surface_type": surface_type, "commands": commands, "metadata": metadata or {}, "text": text}

def _shell_surface(repo_root: Path, rel_path: str, surface_type: str) -> dict[str, Any] | None:
    path = repo_root / rel_path
    if not path.is_file():
        return None
    text, commands = path.read_text(encoding="utf-8"), []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "echo ", "printf ", "if ", "elif ", "else", "fi")):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", stripped):
            continue
        if COMMAND_TOKEN_RE.search(stripped) or 'queue_selected "pytest"' in stripped or SCRIPT_REF_RE.search(stripped):
            commands.append({"origin": surface_type, "snippet": stripped})
    return _surface(path, repo_root, surface_type, commands, text)
def _package_surface(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / "package.json"
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    scripts = payload.get("scripts", {}) if isinstance(payload, dict) else {}
    if not isinstance(scripts, dict):
        return None
    seeds = [name for name in ("pre-push", "prepush", "verify", "verify:local", "quality") if isinstance(scripts.get(name), str)]
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
    metadata = {"seed_scripts": seeds, "verbose_scripts": sorted(name for name in scripts if isinstance(name, str) and VERBOSE_SCRIPT_RE.search(name))}
    return _surface(path, repo_root, "package_json", commands, json.dumps(payload, ensure_ascii=False, indent=2), metadata)
def _lefthook_surface(repo_root: Path) -> dict[str, Any] | None:
    for name in ("lefthook.yml", "lefthook.yaml"):
        path = repo_root / name
        if not path.is_file():
            continue
        block = _yaml_block(path.read_text(encoding="utf-8"), "pre-push")
        if not block.strip():
            return None
        commands = [{"origin": "lefthook:pre-push", "snippet": match.strip()} for match in re.findall(r"(?m)^\s*run:\s*(.+)$", block)]
        metadata = {"parallel": bool(re.search(r"(?m)^\s*parallel:\s*true\s*$", block)), "output_configured": bool(re.search(r"(?m)^\s*(?:output|skip_output):\s*\S", block))}
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
    roots = [surface for surface in (_shell_surface(repo_root, ".githooks/pre-push", "git_hook"), _shell_surface(repo_root, ".husky/pre-push", "husky_hook"), _lefthook_surface(repo_root), _package_surface(repo_root), _make_surface(repo_root)) if surface is not None]
    related, seen = [], {surface["path"] for surface in roots}
    queue = [Path(match.lstrip("./")).as_posix() for surface in roots for command in surface["commands"] for match in SCRIPT_REF_RE.findall(command["snippet"])]
    while queue:
        rel_path = queue.pop(0)
        if rel_path in seen:
            continue
        surface = _shell_surface(repo_root, rel_path, "shell_script")
        if surface is None:
            continue
        seen.add(rel_path)
        related.append(surface)
        queue.extend(Path(match.lstrip("./")).as_posix() for command in surface["commands"] for match in SCRIPT_REF_RE.findall(command["snippet"]))
    return [*roots, *related]


def _iter_snippets(surfaces: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"path": surface["path"], "origin": command["origin"], "snippet": command["snippet"]} for surface in surfaces for command in surface["commands"]]


def _quiet_status(findings: list[dict[str, Any]], quiet_state: str = "quiet") -> str:
    return "not_applicable" if not findings else ("healthy" if all(item["state"] == quiet_state for item in findings) else "weak")


def _runner_axis(snippets: list[dict[str, str]]) -> dict[str, Any]:
    findings, specs = [], [
        ("node --test", lambda s: "node" in s and "--test" in s, lambda s: "--test-reporter=dot" in s and "--test-reporter-destination=stdout" in s, "Pin `node --test --test-reporter=dot --test-reporter-destination=stdout` for standing gates."),
        ("pytest", lambda s: bool(re.search(r"\bpytest\b", s)), lambda s: bool(re.search(r"(^|\s)(-q|--quiet)(\s|$)", s)), "Use `pytest -q` for standing-gate runs; add `--tb=short` if traceback bulk dominates."),
        ("jest", lambda s: bool(re.search(r"\bjest\b", s)), lambda s: "--reporter=dot" in s or "--reporters=dot" in s, "Prefer `jest --reporter=dot` in standing gates."),
        ("vitest", lambda s: bool(re.search(r"\bvitest\b", s)), lambda s: "--reporter=dot" in s, "Prefer `vitest --reporter=dot` in standing gates."),
        ("go test", lambda s: bool(re.search(r"\bgo\s+test\b", s)), lambda s: not bool(re.search(r"(^|\s)-v(\s|$)", s)), "Drop `go test -v` from the standing gate unless the extra stream is required."),
        ("cargo test", lambda s: bool(re.search(r"\bcargo\s+test\b", s)), lambda s: "-- --nocapture" not in s, "Avoid `cargo test -- --nocapture` in the default standing gate."),
    ]
    for item in snippets:
        lowered = item["snippet"].lower()
        for tool, matcher, quiet, suggestion in specs:
            if matcher(lowered):
                is_quiet = quiet(lowered)
                findings.append({"type": "test_runner_reporter", "path": item["path"], "origin": item["origin"], "tool": tool, "state": "quiet" if is_quiet else "loud", "snippet": item["snippet"], "suggestion": "" if is_quiet else suggestion})
                break
    return {"status": _quiet_status(findings), "findings": findings}


def _orchestrator_axis(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    findings = []
    for surface in surfaces:
        if surface["surface_type"] != "lefthook":
            continue
        if surface["commands"] and all(RUNNER_REF_RE.search(command["snippet"]) for command in surface["commands"]):
            findings.append({"type": "lefthook_thin_launcher", "path": surface["path"], "surface_type": surface["surface_type"], "state": "quiet", "suggestion": ""})
            continue
        quiet = not bool(surface["metadata"].get("parallel")) or bool(surface["metadata"].get("output_configured"))
        findings.append({"type": "lefthook_output_mode" if quiet else "lefthook_parallel_output_unconfigured", "path": surface["path"], "surface_type": surface["surface_type"], "state": "quiet" if quiet else "interleaving_risk", "suggestion": "" if quiet else "Prefer delegating `lefthook` `pre-push` to a repo-owned runner (e.g. `scripts/run-pre-push.sh` or `scripts/run-pre-push.mjs`) that owns quiet-default success output, failure replay, and verbose-on-demand. Configuring `lefthook` grouped output (`output:` / `skip_output:`) is an acceptable fallback when the orchestrator still fans out commands directly."})
    return {"status": _quiet_status(findings), "findings": findings}


def _chatter_axis(snippets: list[dict[str, str]]) -> dict[str, Any]:
    findings, specs = [], [
        ("pylint", lambda s: bool(re.search(r"\bpylint\b", s)), lambda s: "--score=n" in s or "--score=no" in s or bool(re.search(r"(^|\s)-sn(\s|$)", s)), "Run `pylint` with `-sn --score=n` or equivalent quiet defaults in the standing gate."),
        ("coverage report", lambda s: "coverage report" in s, lambda s: "--skip-covered" in s or "--skip-empty" in s, "Prefer `coverage report --skip-covered` or another bounded summary in the default gate."),
        ("specdown", lambda s: bool(re.search(r"(^|&&\s*|\|\|\s*|;\s*|\(\s*|\s)specdown\b", s)), lambda s: bool(re.search(r"(^|\s)(-q|-quiet|--quiet)(\s|$)", s)), "Gate `specdown` behind a quieter default or a repo-owned `VERBOSE=1` escape hatch."),
    ]
    for item in snippets:
        lowered = item["snippet"].lower()
        for tool, matcher, quiet, suggestion in specs:
            if matcher(lowered):
                is_quiet = quiet(lowered)
                findings.append({"type": "per_gate_chatter", "path": item["path"], "origin": item["origin"], "tool": tool, "state": "quiet" if is_quiet else "loud", "snippet": item["snippet"], "suggestion": "" if is_quiet else suggestion})
                break
    return {"status": _quiet_status(findings), "findings": findings}


def _phase_axis(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    findings = []
    for surface in surfaces:
        if surface["surface_type"] not in {"git_hook", "husky_hook", "shell_script"}:
            continue
        text = surface["text"]
        structured = any(token in text for token in ("elapsed_ms", "format_elapsed", "date +%s%N")) and any(token in text for token in ("summary", "PASS", "FAIL", "print_phase_output"))
        if structured:
            findings.append({"type": "phase_level_signal", "path": surface["path"], "surface_type": surface["surface_type"], "state": "structured", "suggestion": ""})
        elif surface["commands"]:
            findings.append({"type": "phase_level_signal", "path": surface["path"], "surface_type": surface["surface_type"], "state": "minimal", "suggestion": "Print per-phase labels and elapsed time so success answers which gate ran and failure answers where to look first."})
    return {"status": "not_applicable" if not findings else ("healthy" if any(item["state"] == "structured" for item in findings) else "weak"), "findings": findings}


def _escape_axis(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    findings = []
    for surface in surfaces:
        verbose_vars = sorted(set(VERBOSE_VAR_RE.findall(surface["text"])))
        verbose_scripts = sorted(set(surface["metadata"].get("verbose_scripts", [])))
        if verbose_vars or verbose_scripts:
            findings.append({"type": "escape_hatch", "path": surface["path"], "surface_type": surface["surface_type"], "state": "present", "evidence": ", ".join([*verbose_vars, *verbose_scripts]), "suggestion": ""})
    if findings:
        return {"status": "healthy", "findings": findings}
    if any(surface["commands"] for surface in surfaces):
        return {"status": "missing", "findings": [{"type": "escape_hatch_missing", "path": "", "surface_type": "standing_gate", "state": "missing", "evidence": "", "suggestion": "Keep a verbose-on-demand seam such as `VERBOSE=1`, `CI=1`, or a sibling `*:verbose` script."}]}
    return {"status": "not_applicable", "findings": []}


def inventory(repo_root: Path) -> dict[str, Any]:
    surfaces, snippets = discover_surfaces(repo_root), None
    snippets = _iter_snippets(surfaces)
    axes = {"test_runner_reporter": _runner_axis(snippets), "orchestrator_output_mode": _orchestrator_axis(surfaces), "per_gate_chatter": _chatter_axis(snippets), "phase_level_signal": _phase_axis(surfaces), "escape_hatch": _escape_axis(surfaces)}
    findings = []
    for axis_name, axis in axes.items():
        for finding in axis["findings"]:
            finding["axis"] = axis_name
            findings.append(finding)
    surface_rows = [{"path": surface["path"], "surface_type": surface["surface_type"], "command_count": len(surface["commands"]), "metadata": surface["metadata"]} for surface in surfaces]
    return {"repo_root": str(repo_root), "surfaces": surface_rows, "axes": axes, "findings": findings}
