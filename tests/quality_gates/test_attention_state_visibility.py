from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_attention_state_visibility.py"


def _run(repo: Path, declaration: Path, scan_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repo-root",
            str(repo),
            "--declaration-path",
            str(declaration),
            "--scan-root",
            str(scan_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _write_declaration(path: Path, files: dict[str, object]) -> None:
    path.write_text(json.dumps({"files": files}, indent=2), encoding="utf-8")


def test_fails_when_attention_state_file_is_undeclared(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('no_adapter')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(declaration, {})

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 1
    assert "scripts/helper.py" in result.stderr
    assert "not declared" in result.stderr


def test_fails_when_declared_states_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('disabled')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(
        declaration,
        {
            "scripts/helper.py": {
                "states": ["skipped"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["disabled"],
                "rationale": "demo",
            }
        },
    )

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 1
    assert "do not match detected states" in result.stderr


def test_fails_when_evidence_terms_are_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('skipped')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(
        declaration,
        {
            "scripts/helper.py": {
                "states": ["skipped"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["WARNING:"],
                "rationale": "demo",
            }
        },
    )

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 1
    assert "evidence_terms missing" in result.stderr


def test_passes_with_declared_visibility(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scan_root = repo / "scripts"
    scan_root.mkdir(parents=True)
    (scan_root / "helper.py").write_text("print('WARNING: skipped')\n", encoding="utf-8")
    declaration = repo / "attention.json"
    _write_declaration(
        declaration,
        {
            "scripts/helper.py": {
                "states": ["skipped"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["WARNING:"],
                "rationale": "demo",
            }
        },
    )

    result = _run(repo, declaration, scan_root)

    assert result.returncode == 0, result.stderr
    assert "Validated attention-state visibility declarations" in result.stdout


def test_default_paths_support_exported_plugin_layout(tmp_path: Path) -> None:
    repo = tmp_path / "plugin"
    script_dir = repo / "scripts"
    quality_dir = repo / "skills" / "quality" / "scripts"
    support_dir = repo / "support" / "markdown-preview" / "scripts"
    declaration_dir = repo / "skills" / "quality" / "references"
    script_dir.mkdir(parents=True)
    quality_dir.mkdir(parents=True)
    support_dir.mkdir(parents=True)
    declaration_dir.mkdir(parents=True)
    (script_dir / "root_helper.py").write_text("print('WARNING: no_adapter')\n", encoding="utf-8")
    (quality_dir / "skill_helper.py").write_text("print('ADVISORY: prose_review_status')\n", encoding="utf-8")
    # A real status VALUE, not the phrase "disabled by config": this test is about
    # path resolution in the exported layout, and its fixture should carry the
    # thing the gate looks for rather than prose that happens to use the word.
    (support_dir / "support_helper.py").write_text("print('WARNING: disabled')\n", encoding="utf-8")
    _write_declaration(
        declaration_dir / "attention-state-visibility.json",
        {
            "scripts/root_helper.py": {
                "states": ["no_adapter"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["WARNING:"],
                "rationale": "demo",
            },
            "skills/public/quality/scripts/skill_helper.py": {
                "states": ["prose_review_status"],
                "visibility": ["stdout_attention"],
                "evidence_terms": ["ADVISORY:"],
                "rationale": "demo",
            },
            "skills/support/markdown-preview/scripts/support_helper.py": {
                "states": ["disabled"],
                "visibility": ["terminal_payload"],
                "evidence_terms": ["disabled"],
                "rationale": "demo",
            },
        },
    )

    result = subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Validated attention-state visibility declarations for 3 file(s)." in result.stdout


# --- a status VALUE is not an English word in a sentence ---------------------
#
# The gate scanned every string constant for the term as a SUBSTRING, so prose
# about an exit-zero state tripped a check about exit-zero states. Two recorded
# false positives: #302's `silently-skipped` docstring, and a parsing docstring.
# Both are pinned below, alongside the genuine statuses that must still fire --
# because a gate that stopped refusing anything would pass these too.

import importlib.util  # noqa: E402
import sys  # noqa: E402

# Registered in sys.modules before exec: the module defines a dataclass, and
# @dataclass resolves its owner through sys.modules, which fails for a module
# loaded purely by path.
_spec = importlib.util.spec_from_file_location("attention_state_module", SCRIPT)
_gate = importlib.util.module_from_spec(_spec)
sys.modules["attention_state_module"] = _gate
_spec.loader.exec_module(_gate)


def test_english_prose_using_a_banned_word_is_not_a_status() -> None:
    for prose in (
        "detect failed; healthcheck skipped",
        "Codex marketplace update skipped.",
        "is advisory-only and no skill structure heuristics are enforced.",
        "an absent / disabled baseline is reported rather than assumed",
        "the entry is skipped when its paths no longer resolve",
    ):
        hits = [term for term in _gate.ATTENTION_TERMS if _gate._is_status_value(prose, term)]
        assert hits == [], f"prose read as a status: {prose!r} -> {hits}"


def test_a_genuine_exit_zero_status_still_fires() -> None:
    for value, expected in (
        ("skipped", "skipped"),
        ("WARNING: skipped", "skipped"),
        ("silently-skipped", "skipped"),
        ("status=not_configured", "not_configured"),
        ("no_adapter: no adapter at ", "no_adapter"),
    ):
        hits = [term for term in _gate.ATTENTION_TERMS if _gate._is_status_value(value, term)]
        assert expected in hits, f"real status missed: {value!r} -> {hits}"


def test_a_separator_variant_status_is_caught_that_the_substring_scan_missed() -> None:
    # The narrowing came with a widening: a substring scan could not match a state
    # spelled with a different separator, so `advisory_only_*` and `not-configured`
    # escaped entirely. Two real files in this repo were undeclared because of it.
    assert _gate._is_status_value("advisory_only_no_cli_surface", "advisory-only")
    assert _gate._is_status_value("not-configured", "not_configured")


def test_a_docstring_is_never_a_status(tmp_path: Path) -> None:
    # The #302 shape, at the source: a module docstring explaining that something
    # may be skipped is documentation, and nothing reads it as a state.
    module = tmp_path / "helper.py"
    module.write_text(
        '"""Explains the silently-skipped case and when a run is skipped."""\n\n'
        "def f():\n"
        '    """A parsing helper; malformed rows are skipped."""\n'
        "    return 1\n",
        encoding="utf-8",
    )
    assert _gate._string_constants(module) == []


def test_a_status_next_to_a_docstring_still_fires(tmp_path: Path) -> None:
    # Control, so the docstring exclusion cannot be read as "this file is exempt".
    module = tmp_path / "helper.py"
    module.write_text(
        '"""Rows are skipped when malformed."""\n\n'
        'STATE = "skipped"\n',
        encoding="utf-8",
    )
    constants = _gate._string_constants(module)
    assert constants == ["skipped"]
