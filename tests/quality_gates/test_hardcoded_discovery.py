"""The hardcoded polyglot-discovery advisory inventory.

Guards the narrow high-signal contract: flag portable constants that hardcode a
multi-language (2+ code-language-family) test/source discovery list, stay silent
on single-purpose globs (docs/config) and single-language selectors, and honor
the inline `# discovery-boundary:` silencing marker.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

SCAN_LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "discovery_filter_scan_lib.py"
INVENTORY = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_hardcoded_discovery.py"


def _load_scan_lib() -> ModuleType:
    spec = importlib.util.spec_from_file_location("discovery_filter_scan_lib_for_test", SCAN_LIB)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _repo_with(script_body: str, tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "sample.py").write_text(script_body, encoding="utf-8")
    return repo


def test_flags_unmarked_polyglot_discovery_constant(tmp_path: Path) -> None:
    lib = _load_scan_lib()
    repo = _repo_with(
        'TEST_FILE_PATTERNS = ("test_*.py", "*.test.js", "*.test.mjs")\n',
        tmp_path,
    )
    findings = lib.scan(repo, ["scripts"])
    assert len(findings) == 1
    assert findings[0]["constant"] == "TEST_FILE_PATTERNS"
    assert set(findings[0]["code_families"]) == {"python", "javascript"}
    assert findings[0]["marked_boundary"] is False


def test_ignores_single_purpose_and_single_language_selectors(tmp_path: Path) -> None:
    lib = _load_scan_lib()
    repo = _repo_with(
        "\n".join(
            [
                'DOC_GLOBS = ("docs/**/*.md", "*.md")',       # docs — not a code surface
                'CONFIG_GLOBS = ("*.json", "*.yaml")',         # config — not a code surface
                'PY_PATTERNS = ("test_*.py", "*_test.py")',    # single language family
                'MIXED_DOC_SUFFIXES = (".md", ".txt", ".bash")',  # docs/shell, no code family span
                "",
            ]
        ),
        tmp_path,
    )
    assert lib.scan(repo, ["scripts"]) == []


def test_intra_family_omission_is_out_of_scope(tmp_path: Path) -> None:
    # Disclosed blind spot: a single-family list that omits a sibling extension
    # (a JS-only list missing .mjs — the founding-bug shape at finer grain) reads
    # as non-polyglot and is intentionally NOT flagged, to keep the gate narrow.
    lib = _load_scan_lib()
    repo = _repo_with('JS_TEST_PATTERNS = ("*.test.js", "*.test.jsx")\n', tmp_path)
    assert lib.scan(repo, ["scripts"]) == []


def test_boundary_marker_silences_a_site(tmp_path: Path) -> None:
    lib = _load_scan_lib()
    repo = _repo_with(
        "# discovery-boundary: adapter-owned default, consumers override\n"
        'CODE_EXTENSIONS = {".py", ".ts", ".go"}\n',
        tmp_path,
    )
    findings = lib.scan(repo, ["scripts"])
    assert len(findings) == 1
    assert findings[0]["marked_boundary"] is True
    assert "adapter-owned" in findings[0]["boundary_reason"]


def test_inventory_cli_reports_unmarked_advisory(tmp_path: Path) -> None:
    repo = _repo_with('SPEC_PATTERNS = ("*.spec.ts", "*.spec.go", "test_*.py")\n', tmp_path)
    result = run_loaded_script_main(
        "inventory_hardcoded_discovery.py",
        load_script_module("inventory_hardcoded_discovery_for_test", INVENTORY),
        "--repo-root", str(repo), "--scan-root", "scripts", "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["summary"]["polyglot_discovery_sites"] == 1
    assert payload["summary"]["unmarked_count"] == 1
    assert payload["unmarked_findings"][0]["type"] == "unowned_polyglot_discovery"
    assert payload["unmarked_findings"][0]["severity"] == "advisory"
    assert set(payload["unmarked_findings"][0]["code_families"]) == {"typescript", "go", "python"}
    interpretation = payload["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)
    # blind_spots must honestly disclose the narrow-scope limits (single-family
    # omission and the fixed family map), not just the marker trust caveat.
    assert "single-family" in interpretation["blind_spots"]
    assert "trusted, never verified" in interpretation["blind_spots"]


def test_charness_known_polyglot_sites_are_all_marked() -> None:
    # Regression: the two live polyglot discovery lists in charness (the adapter
    # test-discovery default and the language-scoped lint-ignore suffixes) must
    # stay classified, so the standing gate reads 0 unmarked on this repo.
    lib = _load_scan_lib()
    findings = lib.scan(ROOT)
    unmarked = [finding for finding in findings if not finding["marked_boundary"]]
    assert unmarked == [], f"unmarked polyglot discovery sites introduced: {unmarked}"
    constants = {finding["constant"] for finding in findings}
    assert {"TEST_FILE_PATTERNS", "TEXT_SUFFIXES"}.issubset(constants)
