#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import re
import runpy
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

_summary_output = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).with_name("summary_output_lib.py")))
)

DEFAULT_PATHS = ("runtime_bootstrap.py", "skill_runtime_bootstrap.py", "scripts", "skills", "tests")
FINDING_RE = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+): (?P<message>.+?) "
    r"\((?P<confidence>\d+)% confidence, (?P<size>\d+) lines?\)$"
)
UNUSED_NAME_RE = re.compile(r"unused (?P<kind>\w+) '(?P<name>[^']+)'")
LIKELY_CONVENTION_NAMES = ("pytest_plugins", "pytestmark")
MOCK_PROTOCOL_NAMES = ("side_effect", "return_value", "call_args", "mock_calls")
TEST_PROTOCOL_TERMS = ("fake", "mock", "stub", "driver", "protocol")
STRUCTURED_OUTPUT_NAMES = ("rss_kib",)
SOURCE_SCANNED_CONTRACTS = {
    "scripts/report_usage_product_review.py": {"ATTENTION_STATES", "ATTENTION_EVIDENCE_TERMS"},
}
GIT_LIST_TIMEOUT_SECONDS = 30
VULTURE_TIMEOUT_SECONDS = 120


def git_visible_python_paths(repo_root: Path, roots: tuple[str, ...]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.py"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            timeout=GIT_LIST_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return [root for root in roots if (repo_root / root).exists()]
    if result.returncode != 0:
        return [root for root in roots if (repo_root / root).exists()]
    selected: list[str] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8")
        path = repo_root / rel
        if not path.is_file():
            continue
        if any(rel == root or rel.startswith(f"{root}/") for root in roots):
            selected.append(rel)
    return sorted(selected)


def _is_dataclass_decorator(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return getattr(target, "id", None) == "dataclass" or getattr(target, "attr", None) == "dataclass"


def _import_bindings(tree: ast.AST, module: str, name: str | None = None) -> set[str]:
    bindings: set[str] = set()
    for node in ast.walk(tree):
        if name is None and isinstance(node, ast.Import):
            bindings.update(alias.asname or alias.name for alias in node.names if alias.name == module)
        elif name is not None and isinstance(node, ast.ImportFrom) and node.module == module:
            bindings.update(alias.asname or alias.name for alias in node.names if alias.name == name)
    return bindings


def _is_bound_attribute(expression: ast.expr, bindings: set[str], attribute: str) -> bool:
    target = expression.func if isinstance(expression, ast.Call) else expression
    return (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id in bindings
        and target.attr == attribute
    )


def _is_bound_name(expression: ast.expr, bindings: set[str]) -> bool:
    target = expression.func if isinstance(expression, ast.Call) else expression
    return isinstance(target, ast.Name) and target.id in bindings


def _source_role_locations(path: Path) -> dict[str, set[tuple[int, str]]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {"dataclass_fields": set(), "pytest_fixtures": set(), "visitor_methods": set()}
    pytest_modules = _import_bindings(tree, "pytest")
    fixture_names = _import_bindings(tree, "pytest", "fixture")
    ast_modules = _import_bindings(tree, "ast")
    node_visitor_names = _import_bindings(tree, "ast", "NodeVisitor")
    dataclass_fields = {
        (statement.lineno, statement.target.id)
        for class_node in ast.walk(tree)
        if isinstance(class_node, ast.ClassDef)
        and any(_is_dataclass_decorator(decorator) for decorator in class_node.decorator_list)
        for statement in class_node.body
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name)
    }
    fixture_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            _is_bound_attribute(decorator, pytest_modules, "fixture")
            or _is_bound_name(decorator, fixture_names)
            for decorator in node.decorator_list
        )
    ]
    pytest_fixtures = {
        (line, node.name)
        for node in fixture_nodes
        for line in {node.lineno, *(decorator.lineno for decorator in node.decorator_list)}
    }
    visitor_methods = {
        (method.lineno, method.name)
        for class_node in ast.walk(tree)
        if isinstance(class_node, ast.ClassDef)
        and any(
            _is_bound_attribute(base, ast_modules, "NodeVisitor")
            or _is_bound_name(base, node_visitor_names)
            for base in class_node.bases
        )
        for method in class_node.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        and method.name.startswith("visit_")
    }
    return {
        "dataclass_fields": dataclass_fields,
        "pytest_fixtures": pytest_fixtures,
        "visitor_methods": visitor_methods,
    }


def _dataclass_field_locations(path: Path) -> set[tuple[int, str]]:
    return _source_role_locations(path)["dataclass_fields"]


def classify_finding(
    path: str,
    message: str,
    *,
    line: int | None = None,
    dataclass_fields: set[tuple[int, str]] | None = None,
    source_roles: dict[str, set[tuple[int, str]]] | None = None,
) -> str:
    name_match = UNUSED_NAME_RE.search(message)
    unused_kind = name_match.group("kind") if name_match else ""
    unused_name = name_match.group("name") if name_match else ""
    lower_path = path.lower()
    lower_name = unused_name.lower()
    in_tests = lower_path.startswith("tests/") or "/tests/" in lower_path or lower_path.endswith("conftest.py")
    if unused_name in LIKELY_CONVENTION_NAMES:
        return "likely_framework_convention"
    roles = source_roles or {}
    location = (line, unused_name) if line is not None else None
    if location in roles.get("pytest_fixtures", set()):
        return "likely_pytest_fixture"
    if location in roles.get("visitor_methods", set()):
        return "likely_framework_convention"
    if in_tests and lower_path.endswith("conftest.py") and unused_kind == "function":
        return "likely_pytest_fixture"
    if unused_name in MOCK_PROTOCOL_NAMES:
        return "likely_mock_protocol"
    if in_tests and unused_kind in {"attribute", "method", "property"}:
        return "likely_test_protocol"
    if any(term in lower_name or term in lower_path for term in TEST_PROTOCOL_TERMS) and unused_kind in {
        "attribute",
        "method",
        "property",
    }:
        return "likely_test_protocol"
    fields = dataclass_fields if dataclass_fields is not None else set()
    if unused_kind == "variable" and line is not None and (line, unused_name) in (fields or set()):
        return "structured_output_field"
    if unused_kind == "variable" and unused_name in SOURCE_SCANNED_CONTRACTS.get(path, set()):
        return "source_scanned_contract"
    # Preserve context-free direct-call compatibility without affecting AST-aware scans.
    if dataclass_fields is None and unused_name in STRUCTURED_OUTPUT_NAMES:
        return "structured_output_field"
    if "unused attribute" in message:
        return "low_confidence_attribute"
    return "review_candidate"


def parse_findings(stdout: str, *, repo_root: Path | None = None) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    role_cache: dict[str, dict[str, set[tuple[int, str]]]] = {}
    for line in stdout.splitlines():
        match = FINDING_RE.match(line)
        if not match:
            continue
        path = match.group("path")
        message = match.group("message")
        finding_line = int(match.group("line"))
        if repo_root is not None and path not in role_cache:
            role_cache[path] = _source_role_locations(repo_root / path)
        roles = role_cache.get(path)
        fields = roles.get("dataclass_fields") if roles is not None else None
        findings.append(
            {
                "path": path,
                "line": finding_line,
                "message": message,
                "confidence": int(match.group("confidence")),
                "size": int(match.group("size")),
                "classification": classify_finding(
                    path,
                    message,
                    line=finding_line,
                    dataclass_fields=fields,
                    source_roles=roles,
                ),
            }
        )
    return findings


def classification_counts(findings: list[dict[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(str(finding["classification"]) for finding in findings).items()))


def summarize_run(run: dict[str, object], *, sample_limit: int) -> dict[str, object]:
    findings = list(run.get("findings", []))
    review_candidates = [
        finding for finding in findings if isinstance(finding, dict) and finding.get("classification") == "review_candidate"
    ][:sample_limit]
    return {
        "confidence": run.get("confidence"),
        "status": run.get("status"),
        "exit_code": run.get("exit_code"),
        "finding_count": len(findings),
        "classification_counts": run.get("classification_counts", {}),
        "review_candidate_sample": review_candidates,
        "stderr_present": bool(run.get("stderr")),
    }


def summarize(payload: dict[str, object], *, sample_limit: int = 10) -> dict[str, object]:
    return {
        "summary_note": "summary is triage output; use --detail for full vulture command and findings",
        "repo_root": payload["repo_root"],
        "paths": payload["paths"],
        "git_visible_python_file_count": payload["git_visible_python_file_count"],
        "primary": summarize_run(payload["primary"], sample_limit=sample_limit),
        "sweep": summarize_run(payload["sweep"], sample_limit=sample_limit),
        "notes": payload["notes"],
    }


def run_vulture(repo_root: Path, paths: list[str], *, confidence: int) -> dict[str, object]:
    if shutil.which("vulture") is None:
        return {
            "confidence": confidence,
            "status": "missing",
            "command": "vulture",
            "exit_code": None,
            "findings": [],
            "stderr": "vulture is not installed",
        }
    command = ["vulture", *paths, "--min-confidence", str(confidence), "--sort-by-size"]
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=VULTURE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        completed = subprocess.CompletedProcess(
            command,
            124,
            str(exc.stdout or ""),
            f"timed out after {VULTURE_TIMEOUT_SECONDS}s",
        )
    findings = parse_findings(completed.stdout, repo_root=repo_root)
    return {
        "confidence": confidence,
        "status": "findings" if completed.returncode == 3 else "clean" if completed.returncode == 0 else "error",
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "findings": findings,
        "classification_counts": classification_counts(findings),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the vulture-backed dead-code advisory scan")
    parser.add_argument("--path", action="append", default=[], help="Repo-relative path to scan for dead code (repeatable; defaults applied if omitted)")
    parser.add_argument("--primary-confidence", type=int, default=80, help="vulture --min-confidence for the high-confidence primary pass")
    parser.add_argument("--sweep-confidence", type=int, default=60, help="vulture --min-confidence for the lower-confidence sweep pass")
    _summary_output.add_output_args(
        parser,
        summary_help="Emit compact YAML counts and samples instead of full vulture commands",
        detail_help="Emit the full advisory payload as YAML",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    roots = tuple(args.path or DEFAULT_PATHS)
    paths = git_visible_python_paths(repo_root, roots)
    primary = run_vulture(repo_root, paths, confidence=args.primary_confidence)
    sweep = run_vulture(repo_root, paths, confidence=args.sweep_confidence)
    payload = {
        "repo_root": str(repo_root),
        "paths": roots,
        "git_visible_python_file_count": len(paths),
        "primary": primary,
        "sweep": sweep,
        "notes": [
            "Vulture is advisory here; do not treat a clean primary pass as proof that no dead files exist.",
            "The lower-confidence sweep is for cleanup review and will include framework conventions and dynamic-use false positives.",
        ],
    }
    if _summary_output.emit_selected(payload, args, summarize=summarize):
        return 0
    review_candidates = [
        finding for finding in sweep["findings"] if finding["classification"] == "review_candidate"
    ]
    if review_candidates:
        # Surface through run-quality.sh's ADVISORY attention filter so the opt-in
        # gate's findings are visible without --verbose. This never blocks: the gate
        # always exits 0. Only the review_candidate class is called out here; the
        # framework-convention / test-protocol noise classes stay in the detail below.
        print(
            f"ADVISORY: vulture flagged {len(review_candidates)} dead-code review_candidate "
            f"finding(s) of {len(sweep['findings'])} total for separate triage (advisory only, never blocks)."
        )
    print(f"Primary ({args.primary_confidence}%): {primary['status']} ({len(primary['findings'])} findings)")
    print(f"Sweep ({args.sweep_confidence}%): {sweep['status']} ({len(sweep['findings'])} findings)")
    # `.get`: the vulture-missing run dict has no `classification_counts` key (only
    # the ran-clean/findings/error dicts do). Keying it directly here crashed the human
    # path (exit 1) when vulture was absent, so an opted-in advisory gate falsely turned
    # the run red — the gate must stay exit-0 advisory even with the tool missing.
    classification_counts = sweep.get("classification_counts") or {}
    if classification_counts:
        counts = ", ".join(f"{name}={count}" for name, count in classification_counts.items())
        print(f"Sweep classifications: {counts}")
    ordered = sorted(
        sweep["findings"],
        key=lambda finding: (0 if finding["classification"] == "review_candidate" else 1, str(finding["classification"])),
    )
    for finding in ordered:
        print(f"{finding['path']}:{finding['line']} {finding['message']} [{finding['classification']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
