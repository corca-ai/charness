from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_attention_state_visibility.py"


def _run(repo: Path, declaration: Path, scan_root: Path) -> subprocess.CompletedProcess[str]:
    return run_script(
        str(SCRIPT),
        "--repo-root",
        str(repo),
        "--declaration-path",
        str(declaration),
        "--scan-root",
        str(scan_root),
        cwd=ROOT,
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
    # The failure list moved from stderr prose into the YAML payload's
    # `failures` key; the intent (name the undeclared file and say why) stands.
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid"
    assert any(
        "scripts/helper.py" in failure and "not declared" in failure
        for failure in payload["failures"]
    ), payload["failures"]


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
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid"
    assert any(
        "do not match detected states" in failure for failure in payload["failures"]
    ), payload["failures"]


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
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid"
    assert any(
        "evidence_terms missing" in failure for failure in payload["failures"]
    ), payload["failures"]


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
    # The "Validated ..." sentence is gone; `status: valid` with an empty
    # `failures` list is the same verdict in the payload.
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "valid"
    assert payload["failures"] == []


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

    result = run_script(str(SCRIPT), "--repo-root", str(repo), cwd=ROOT)

    assert result.returncode == 0, result.stderr
    # The retired sentence carried the detected-file count; `detected_file_count`
    # carries it now, so the exported-layout path resolution is still pinned to
    # all three files being found.
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "valid"
    assert payload["failures"] == []
    assert payload["detected_file_count"] == 3


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


def test_a_term_with_no_token_parts_matches_nothing() -> None:
    # Defensive: a term that tokenizes to nothing (punctuation only) must not
    # match every value. Without the guard, the empty part-list would be found
    # at every index and report every string as that state.
    assert _gate._is_status_value("skipped", "---") is False
    assert _gate._is_status_value("anything at all", "") is False


def test_a_node_with_no_body_is_skipped_when_marking_docstrings(tmp_path: Path) -> None:
    # `ast.Module` for an empty file has an empty body, and a class body cannot
    # be empty without `pass` -- so the empty-body guard is reached by an empty
    # module. It must not raise while collecting docstrings.
    empty = tmp_path / "empty.py"
    empty.write_text("", encoding="utf-8")
    assert _gate._string_constants(empty) == []
