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

from .test_managed_install import CLI, load_charness_module

ROOT = CLI.parent


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


def test_repo_onboarding_parses_the_skill_routing_payload_through_the_yaml_fallback(
    charness, tmp_path, monkeypatch
) -> None:
    """The `init`/`doctor` call site, which is where the original break was observed.

    `charness init` passed `--json` to `render_skill_routing.py` after the flag stopped
    being declared and then `json.loads`-ed the result: a double fault, since the flag
    exited 2 AND the payload it would have produced was YAML. Covering
    `parse_repo_script_payload` alone does not pin the caller, so this drives the
    onboarding payload with the routing script answering in YAML -- the format it
    actually speaks -- and asserts the routing block survives into the payload.

    `invoke_repo_script` is replaced rather than spawned: the contract under test is
    the parse-and-embed at the call site, not the subprocess, and this repo's ratchets
    treat a new script spawn as a boundary that needs its own justification.
    """
    target = tmp_path / "consumer"
    (target / ".git").mkdir(parents=True)
    (target / "AGENTS.md").write_text("# consumer\n", encoding="utf-8")

    answers = {
        "skills/public/setup/scripts/inspect_repo.py": '{"repo_mode": "PARTIAL", "agent_docs": {}}',
        "skills/public/setup/scripts/render_skill_routing.py": (
            "recommended_action: adopt\npublic_skills:\n  - setup\n"
        ),
    }

    def fake_invoke(_source_root, script, *args):
        assert "--json" not in args, f"`{script}` must not be asked for a removed flag"
        return answers[script]

    monkeypatch.setattr(charness, "invoke_repo_script", fake_invoke)

    payload = charness.build_repo_onboarding_payload(
        source_repo_root=ROOT, target_repo_root=target
    )

    assert payload["skill_routing"] == {"recommended_action": "adopt", "public_skills": ["setup"]}
    assert payload["inspection"]["repo_mode"] == "PARTIAL"
