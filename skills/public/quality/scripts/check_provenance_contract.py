#!/usr/bin/env python3
"""Check the executable producer-to-final-consumer invariant registry."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from scripts.core import subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    import scripts.core.subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process

subprocess = _subprocess_guard.subprocess


def _load_contract_module(repo_root: Path):
    shared = repo_root / "skills" / "shared" / "scripts"
    if not shared.is_dir():
        shared = repo_root / "shared" / "scripts"
    if str(shared) not in sys.path:
        sys.path.insert(0, str(shared))
    import provenance_contract

    return provenance_contract


def _emit_yaml(payload: dict, repo_root: Path) -> None:
    output_path = repo_root / "scripts" / "yaml_output.py"
    spec = importlib.util.spec_from_file_location("charness_yaml_output", output_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"yaml output helper is not loadable: {output_path}")
    output = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(output)
    output.emit_yaml(payload)


def _junit_fixture_status(xml_path: Path, stdout: str) -> tuple[str, str | None]:
    """Return a proof status, refusing zero-test and non-passed pytest outcomes.

    Pytest's process return code is zero for skips and non-strict xpasses.  The
    contract gate needs an executed passing node, so it reads the structured
    testcase result instead of treating ``returncode == 0`` as proof.
    """
    if "XPASS" in stdout:
        return "xpassed", "pytest reported XPASS"
    try:
        root = ET.parse(xml_path).getroot()
    except (ET.ParseError, OSError) as exc:
        return "missing-result", f"JUnit result is unreadable: {exc}"

    def local(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    cases = [element for element in root.iter() if local(element.tag) == "testcase"]
    if not cases:
        return "zero-tests", "JUnit result contained no testcases"
    for case in cases:
        for child in case:
            tag = local(child.tag)
            if tag == "skipped":
                return "skipped", "pytest marked the fixture skipped"
            if tag == "failure":
                return "failed", "pytest marked the fixture failed"
            if tag == "error":
                return "errored", "pytest marked the fixture errored"
    return "passed", None


def _plugin_relative_path(source_path: str) -> str:
    """Map an authoring-tree anchor to its exported plugin location."""
    mappings = (
        ("skills/shared/", "shared/"),
        ("skills/public/quality/", "skills/quality/"),
    )
    for source_prefix, plugin_prefix in mappings:
        if source_path.startswith(source_prefix):
            return plugin_prefix + source_path[len(source_prefix) :]
    return source_path


def _validate_plugin_anchors(repo_root: Path, contracts) -> list[str]:
    """Check exported consumer anchors without claiming runtime fixture proof."""
    errors: list[str] = []
    for contract in contracts:
        relative = _plugin_relative_path(contract.consumer_path)
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"{contract.contract_id} has unsafe plugin consumer path: {relative}")
            continue
        path = repo_root / relative
        if not path.is_file():
            errors.append(f"{contract.contract_id} references missing plugin consumer: {relative}")
        elif contract.contract_id not in path.read_text(encoding="utf-8"):
            errors.append(f"{contract.contract_id} is not anchored in plugin consumer: {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="Repository or packaged tree to validate"
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    module = _load_contract_module(repo_root)
    errors = module.validate_registry(
        repo_root, require_repo_anchors=(repo_root / "skills" / "shared").is_dir()
    )
    fixture_results = []
    authoring_tree = (repo_root / "tests").is_dir()
    plugin_tree = (repo_root / "shared").is_dir() and not (repo_root / "skills" / "shared").is_dir()
    if not errors and plugin_tree:
        errors.extend(_validate_plugin_anchors(repo_root, module.CONTRACTS))
    # The authoring checkout has the final-consumer tests.  Execute the exact
    # nodes named by the registry so a path/comment marker cannot masquerade as
    # proof.  Exported plugin trees intentionally validate shape and anchors only.
    if not errors and authoring_tree:
        for contract in module.CONTRACTS:
            with tempfile.TemporaryDirectory(prefix="charness-provenance-") as temp_dir:
                junit_path = Path(temp_dir) / "pytest.xml"
                result = run_process(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "-q",
                        "-rxX",
                        f"--junitxml={junit_path}",
                        contract.negative_fixture,
                    ],
                    cwd=repo_root,
                    timeout_seconds=60,
                )
                if result.returncode == 124 and result.stderr.startswith("timed out after "):
                    fixture_results.append(
                        {
                            "contract_id": contract.contract_id,
                            "fixture": contract.negative_fixture,
                            "returncode": None,
                            "status": "timeout",
                        }
                    )
                    errors.append(
                        f"{contract.contract_id} fixture timed out ({contract.negative_fixture}): "
                        f"{result.stderr.strip()}"
                    )
                    continue
                status, detail = _junit_fixture_status(junit_path, result.stdout)
                fixture_results.append(
                    {
                        "contract_id": contract.contract_id,
                        "fixture": contract.negative_fixture,
                        "returncode": result.returncode,
                        "status": status
                        if result.returncode == 0 or status != "passed"
                        else "failed",
                    }
                )
                if result.returncode or status != "passed":
                    reason = detail or result.stdout.strip() or result.stderr.strip()
                    errors.append(
                        f"{contract.contract_id} fixture failed ({contract.negative_fixture}): "
                        f"{reason}"
                    )
    payload = {
        "schema_version": module.SCHEMA_VERSION,
        "contract_count": len(module.CONTRACTS),
        "fixture_results": fixture_results,
        "errors": errors,
        "proof_level": (
            "executable-fixtures"
            if authoring_tree
            else "shape+consumer-anchors"
            if plugin_tree
            else "shape-only"
        ),
        "non_claims": []
        if authoring_tree
        else ["final-consumer pytest fixtures are not packaged in this plugin layout"]
        if plugin_tree
        else ["consumer anchors and final-consumer pytest fixtures are not proven in this layout"],
        "ok": not errors,
    }
    _emit_yaml(payload, repo_root)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
