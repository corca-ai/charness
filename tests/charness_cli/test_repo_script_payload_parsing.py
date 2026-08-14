"""`parse_repo_script_payload`'s three fallbacks, and the one that must not crash.

The function exists because `charness init` called `render_skill_routing.py --json`
after the flag stopped being declared -- a double fault, since the flag exited 2 AND
the payload it would have produced was YAML. The replacement tries JSON, falls back to
YAML, and turns a missing PyYAML into a named remedy rather than a traceback, because a
traceback at that point in `init` reads as a broken install rather than a missing
dependency.

Every branch below was a changed line with no coverage: the JSON path, the JSON->YAML
fallback, the ImportError remedy, and the unreadable-YAML refusal.
"""

from __future__ import annotations

import builtins

import pytest

from .test_managed_install import load_charness_module


@pytest.fixture(scope="module")
def charness():
    return load_charness_module("charness_repo_script_payload_under_test")


def test_a_json_payload_is_returned_without_reaching_the_yaml_path(charness) -> None:
    assert charness.parse_repo_script_payload('{"a": 1}', "src") == {"a": 1}


def test_a_yaml_payload_falls_through_json_and_parses(charness) -> None:
    """JSON is valid YAML, so the fallback is what makes both old and new output read."""
    assert charness.parse_repo_script_payload("a: 1\nb:\n  - x\n", "src") == {"a": 1, "b": ["x"]}


def test_a_missing_pyyaml_names_the_remedy_instead_of_raising_importerror(
    charness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one case that must not crash: `init` has already cloned and installed."""
    real_import = builtins.__import__

    def refuse_yaml(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("no yaml here")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", refuse_yaml)

    with pytest.raises(charness.CharnessError) as excinfo:
        charness.parse_repo_script_payload("a: 1\n", "render_skill_routing.py")

    message = str(excinfo.value)
    assert "PyYAML is not importable" in message
    assert "render_skill_routing.py" in message
    # The remedy, not just the diagnosis -- both spellings an operator can act on.
    assert "Install PyYAML" in message
    assert "bootstrap_runtime.py" in message


def test_an_unreadable_yaml_payload_is_refused_with_the_stdout_that_produced_it(
    charness,
) -> None:
    """The refusal carries the payload, because the caller cannot re-run the producer."""
    with pytest.raises(charness.CharnessError) as excinfo:
        charness.parse_repo_script_payload("a: [1,\n  b: {", "src")

    message = str(excinfo.value)
    assert "did not return a readable YAML payload" in message
    assert "STDOUT:" in message
    assert "a: [1," in message
