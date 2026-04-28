from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_discovery_lib() -> Any:
    module_path = Path(__file__).resolve().with_name("standing_gate_discovery_lib.py")
    spec = importlib.util.spec_from_file_location("standing_gate_discovery_lib", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_DISCOVERY = _load_discovery_lib()
RUNNER_REF_RE = _DISCOVERY.RUNNER_REF_RE
discover_surfaces = _DISCOVERY.discover_surfaces
iter_snippets = _DISCOVERY.iter_snippets
VERBOSE_VAR_RE = re.compile(r"\b[A-Z0-9_]*VERBOSE[A-Z0-9_]*\b")
QUIET_SPECDOWN_RE = re.compile(r"\bspecdown\b(?=[^\n]*(?:-q|-quiet|--quiet))", re.IGNORECASE)
QUIET_PYTEST_RE = re.compile(r"\bpytest\b(?=[^\n]*(?:-q|--quiet))", re.IGNORECASE)
SUPPRESSED_OUTPUT_RE = re.compile(r"(?:^|\s)(?:1?>|2>)\s*/dev/null\b|--tb=no\b", re.IGNORECASE)
FAILURE_DETAIL_MARKERS = (
    "print_phase_output",
    "rerun without",
    "rerun once",
    "failure output",
    "actual",
    "expected",
)
QUIET_FAILURE_TOOLS = (
    ("specdown", QUIET_SPECDOWN_RE, "failing spec/case", False),
    ("pytest", QUIET_PYTEST_RE, "failing test/case", True),
)


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


def _failure_detail_axis(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    findings = []
    for surface in surfaces:
        text = surface["text"]
        lower_text = text.lower()
        has_failure_detail = any(marker in lower_text for marker in FAILURE_DETAIL_MARKERS)
        output_suppressed = bool(SUPPRESSED_OUTPUT_RE.search(text))
        for tool, pattern, unit_label, native_detail in QUIET_FAILURE_TOOLS:
            if not pattern.search(text):
                continue
            actionable = has_failure_detail or (native_detail and not output_suppressed)
            findings.append(
                {
                    "type": "quiet_failure_detail",
                    "path": surface["path"],
                    "surface_type": surface["surface_type"],
                    "tool": tool,
                    "state": "actionable" if actionable else "needs_failure_detail",
                    "evidence": "failure detail marker present" if has_failure_detail else ("native failure detail kept" if actionable else ""),
                    "suggestion": ""
                    if actionable
                    else (
                        f"Quiet failure output should name the {unit_label} and include a short "
                        "`actual`/error snippet without requiring a manual verbose rerun."
                    ),
                }
            )
    return {
        "status": _quiet_status(findings, quiet_state="actionable"),
        "findings": findings,
    }


def inventory(repo_root: Path) -> dict[str, Any]:
    surfaces, snippets = discover_surfaces(repo_root), None
    snippets = iter_snippets(surfaces)
    axes = {
        "test_runner_reporter": _runner_axis(snippets),
        "orchestrator_output_mode": _orchestrator_axis(surfaces),
        "per_gate_chatter": _chatter_axis(snippets),
        "phase_level_signal": _phase_axis(surfaces),
        "escape_hatch": _escape_axis(surfaces),
        "failure_detail": _failure_detail_axis(surfaces),
    }
    findings = []
    for axis_name, axis in axes.items():
        for finding in axis["findings"]:
            finding["axis"] = axis_name
            findings.append(finding)
    surface_rows = [{"path": surface["path"], "surface_type": surface["surface_type"], "command_count": len(surface["commands"]), "metadata": surface["metadata"]} for surface in surfaces]
    return {"repo_root": str(repo_root), "surfaces": surface_rows, "axes": axes, "findings": findings}
