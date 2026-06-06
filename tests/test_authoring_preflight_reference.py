from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_DOC = ROOT / "docs" / "conventions" / "authoring-preflight.md"
DISCIPLINE_DOC = ROOT / "docs" / "conventions" / "implementation-discipline.md"


def _attention_terms() -> tuple[str, ...]:
    path = ROOT / "scripts" / "validate_attention_state_visibility.py"
    spec = importlib.util.spec_from_file_location("validate_attention_state_visibility", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.ATTENTION_TERMS


def test_authoring_preflight_reference_exists_and_is_discoverable() -> None:
    # #308: the authoring-preflight reference exists and is reachable from the
    # read-before-authoring path (implementation-discipline.md).
    assert PREFLIGHT_DOC.is_file()
    assert "authoring-preflight.md" in DISCIPLINE_DOC.read_text(encoding="utf-8")


def test_authoring_preflight_lists_current_attention_vocabulary() -> None:
    # #308 drift guard: the reference must list every banned attention-state term
    # the gate actually checks, so the preflight cannot silently go stale when the
    # validator's ATTENTION_TERMS changes.
    text = PREFLIGHT_DOC.read_text(encoding="utf-8")
    missing = [term for term in _attention_terms() if f"`{term}`" not in text]
    assert not missing, f"authoring-preflight.md is missing banned terms: {missing}"


# The headroom affordance the reference points at (check_python_lengths --headroom)
# is exercised by tests/quality_gates/test_closeout_headroom_and_mirror_gate.py, so
# it is not re-driven here (avoids a duplicate subprocess boundary-bypass candidate).


def test_authoring_preflight_names_skill_core_headroom_buffer() -> None:
    # #319 drift guard: the reference must name the SKILL.md core-headroom buffer
    # and the commit-boundary checker, so the preflight list does not silently
    # omit the trap that the new ratchet now enforces.
    text = PREFLIGHT_DOC.read_text(encoding="utf-8")
    assert "SKILL.md core headroom" in text
    assert "check_skill_surface_preflight.py" in text
