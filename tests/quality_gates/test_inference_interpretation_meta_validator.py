"""Tests for the #330 advisory-interpretation meta-validator.

Driven in-process (importlib + evaluate()/main()) rather than via subprocess so a
new boundary-spawning candidate key is not introduced (check_boundary_bypass_ratchet;
the #322 in-process convention). The negative guards are the load-bearing part:
they prove that removing a declaration field, dropping the consumer pairing, or
leaking a declaration onto an unregistered surface each turns the gate red.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import sys
from pathlib import Path

import pytest

from .support import ROOT

META = importlib.import_module("scripts.validate_inference_interpretation")
FIELDS = META.CONTRACT_FIELDS


def _decl(symbol: str = "INTERPRETATION", *, measures: str = "literal clone families") -> str:
    return (
        f"{symbol} = {{\n"
        f'    "measures": {measures!r},\n'
        '    "proxy_for": "the real concern it stands in for",\n'
        '    "blind_spots": "where proxy and reality diverge",\n'
        '    "interpretation_question": "the question only judgment can answer?",\n'
        "}\n"
    )


def _registry(surfaces: list[dict], *, excludes: list[str] | None = None) -> dict:
    return {
        "version": 1,
        "contract_reference": "skills/shared/references/advisory-interpretation-contract.md",
        "declaration_fields": list(FIELDS),
        "leak_scan": {"exclude_prefixes": excludes or ["plugins/", "mutants/", "tests/"]},
        "surfaces": surfaces,
    }


def _python_surface(decl_file: str, consumer_ref: str, anchor: str) -> dict:
    return {
        "surface_id": "demo-python",
        "kind": "python",
        "declaration_file": decl_file,
        "declaration_symbol": "INTERPRETATION",
        "consumer_reference": consumer_ref,
        "consumer_anchor": anchor,
    }


def _make_repo(tmp_path: Path) -> tuple[Path, dict]:
    """A minimal repo: one python surface declaration + its consumer reference."""
    repo = tmp_path / "repo"
    decl_rel = "scripts/inventory_demo.py"
    consumer_rel = "skills/public/quality/references/automation-promotion.md"
    (repo / "scripts").mkdir(parents=True)
    (repo / decl_rel).write_text(_decl(), encoding="utf-8")
    (repo / "skills/public/quality/references").mkdir(parents=True)
    anchor = "which families are intentional"
    (repo / consumer_rel).write_text(
        f"# consumer\n\nThe consumer must answer first: {anchor} vs extractable debt?\n",
        encoding="utf-8",
    )
    registry = _registry([_python_surface(decl_rel, consumer_rel, anchor)])
    return repo, registry


def _evaluate(repo: Path, registry: dict | None) -> tuple[int, list[str]]:
    return META.evaluate(
        repo.resolve(), registry, repo / ".agents/registry.json", require_git=False
    )


# --- unit: declaration detection -------------------------------------------------


def test_find_declaration_dicts_detects_four_field_dict() -> None:
    found = META.find_declaration_dicts(_decl("RECOMMENDATION_INTERPRETATION"))
    assert len(found) == 1
    symbol, values = found[0]
    assert symbol == "RECOMMENDATION_INTERPRETATION"
    assert set(values) == set(FIELDS)
    assert all(values[field] for field in FIELDS)


def test_find_declaration_dicts_ignores_three_field_dict() -> None:
    source = 'X = {"measures": "a", "proxy_for": "b", "blind_spots": "c"}\n'
    assert META.find_declaration_dicts(source) == []


def test_find_declaration_dicts_detects_superset_keys() -> None:
    source = _decl().rstrip()[:-1] + '    "extra": "y",\n}\n'
    assert len(META.find_declaration_dicts(source)) == 1


def test_find_declaration_dicts_detects_annotated_assignment() -> None:
    # `X: dict = {...}` is as idiomatic as `X = {...}`; an annotated declaration
    # must NOT slip past the leak scan (fresh-eye review NIT, #330).
    source = "INTERPRETATION: dict = " + _decl().split("= ", 1)[1]
    found = META.find_declaration_dicts(source)
    assert len(found) == 1
    assert found[0][0] == "INTERPRETATION"


# --- happy path ------------------------------------------------------------------


def test_valid_repo_passes(tmp_path: Path) -> None:
    repo, registry = _make_repo(tmp_path)
    code, messages = _evaluate(repo, registry)
    assert code == 0, messages
    assert any("Validated advisory-interpretation contract" in m for m in messages)


# --- negative guards (the cardinal value of #330) --------------------------------


def test_empty_declaration_field_fails(tmp_path: Path) -> None:
    repo, registry = _make_repo(tmp_path)
    (repo / "scripts/inventory_demo.py").write_text(_decl(measures="   "), encoding="utf-8")
    code, messages = _evaluate(repo, registry)
    assert code == 1
    assert any("`measures` must be a non-empty static string" in m for m in messages)


def test_removed_declaration_symbol_fails(tmp_path: Path) -> None:
    repo, registry = _make_repo(tmp_path)
    # Symbol renamed away — the registered symbol no longer resolves to a 4-field dict.
    (repo / "scripts/inventory_demo.py").write_text(_decl("OTHER_NAME"), encoding="utf-8")
    code, messages = _evaluate(repo, registry)
    assert code == 1
    assert any("declaration_symbol `INTERPRETATION`" in m and "drift" in m for m in messages)


def test_missing_consumer_pairing_fails(tmp_path: Path) -> None:
    repo, registry = _make_repo(tmp_path)
    consumer = repo / "skills/public/quality/references/automation-promotion.md"
    consumer.write_text("# consumer\n\nNo paired interpretation line here.\n", encoding="utf-8")
    code, messages = _evaluate(repo, registry)
    assert code == 1
    assert any("paired consumer-must-answer line missing" in m for m in messages)


def test_unregistered_declaration_is_a_leak(tmp_path: Path) -> None:
    repo, registry = _make_repo(tmp_path)
    # A second declaration appears in a file NOT registered — the cardinal error:
    # a verified fact (or a new inference surface) carrying the declaration unregistered.
    (repo / "scripts/check_exact_counts.py").write_text(_decl(), encoding="utf-8")
    code, messages = _evaluate(repo, registry)
    assert code == 1
    assert any("LEAK" in m and "scripts/check_exact_counts.py" in m for m in messages)


def test_annotated_unregistered_declaration_is_a_leak(tmp_path: Path) -> None:
    # The hardened form: an annotated declaration on an unregistered file is still
    # the cardinal error and must fail closed (fresh-eye review NIT, #330).
    repo, registry = _make_repo(tmp_path)
    annotated = "INTERPRETATION: dict = " + _decl().split("= ", 1)[1]
    (repo / "scripts/check_exact_counts.py").write_text(annotated, encoding="utf-8")
    code, messages = _evaluate(repo, registry)
    assert code == 1
    assert any("LEAK" in m and "scripts/check_exact_counts.py" in m for m in messages)


def test_leak_scan_respects_exclude_prefixes(tmp_path: Path) -> None:
    repo, registry = _make_repo(tmp_path)
    # A declaration inside an excluded tree (a test fixture) is not a live surface.
    (repo / "tests").mkdir(parents=True, exist_ok=True)
    (repo / "tests/test_fixture.py").write_text(_decl(), encoding="utf-8")
    (repo / "plugins/charness/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "plugins/charness/scripts/inventory_demo.py").write_text(_decl(), encoding="utf-8")
    code, messages = _evaluate(repo, registry)
    assert code == 0, messages


# --- prose surface ---------------------------------------------------------------


def test_prose_surface_missing_anchor_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    prose_rel = "skills/public/quality/references/gate-classification.md"
    (repo / "skills/public/quality/references").mkdir(parents=True)
    (repo / prose_rel).write_text(
        "It measures judged leverage; it proxies for the next move; "
        "answer its interpretation question first: does the top-ranked gate genuinely fit?\n",
        encoding="utf-8",
    )
    surface = {
        "surface_id": "prose-demo",
        "kind": "prose",
        "declaration_file": prose_rel,
        "prose_anchors": ["It measures", "it proxies for", "blind to maintenance burden", "answer its interpretation question"],
        "consumer_reference": prose_rel,
        "consumer_anchor": "does the top-ranked gate genuinely",
    }
    code, messages = _evaluate(repo, _registry([surface]))
    assert code == 1
    assert any("prose declaration anchor `blind to maintenance burden` missing" in m for m in messages)


# --- portability + registry validation -------------------------------------------


def test_absent_registry_with_declarations_fails(tmp_path: Path) -> None:
    repo, _ = _make_repo(tmp_path)
    code, messages = _evaluate(repo, None)
    assert code == 1
    assert any("found but no registry" in m for m in messages)


def test_absent_registry_without_declarations_passes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts/plain.py").write_text("X = 1\n", encoding="utf-8")
    code, messages = _evaluate(repo, None)
    assert code == 0, messages


def test_malformed_registry_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"version": 2, "surfaces": []}), encoding="utf-8")
    with pytest.raises(META.InterpretationContractError):
        META.load_registry(bad)


def test_registry_field_drift_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(_registry([])  # empty surfaces is itself invalid
        ),
        encoding="utf-8",
    )
    with pytest.raises(META.InterpretationContractError):
        META.load_registry(bad)


# --- live: the real repo registry validates --------------------------------------


def _run_main(*args: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    saved = sys.argv
    sys.argv = ["validate_inference_interpretation.py", *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = META.main()
    finally:
        sys.argv = saved
    return code, out.getvalue(), err.getvalue()


def test_live_repo_contract_holds() -> None:
    code, stdout, stderr = _run_main("--repo-root", str(ROOT), "--require-git-file-listing")
    assert code == 0, stderr
    assert "Validated advisory-interpretation contract across 8 inference-layer surface(s)" in stdout


def test_live_registry_is_structurally_valid() -> None:
    registry = META.load_registry(ROOT / ".agents/inference-interpretation-surfaces.json")
    assert registry is not None
    ids = {s["surface_id"] for s in registry["surfaces"]}
    # the 7 python declarations enumerated empirically + the 1 prose ranking
    assert "find-skills-recommendation" in ids
    assert "quality-next-gates-ranking" in ids
    assert sum(1 for s in registry["surfaces"] if s["kind"] == "python") == 7
