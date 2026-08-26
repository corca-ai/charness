from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from .support import ADAPTER_LIB, ADAPTER_RENDER_LIB, ROOT

VALIDATORS_SPEC = importlib.util.spec_from_file_location(
    "adapter_validators_under_test",
    ROOT / "skills" / "public" / "quality" / "scripts" / "adapter_validators.py",
)
assert VALIDATORS_SPEC is not None and VALIDATORS_SPEC.loader is not None
ADAPTER_VALIDATORS = importlib.util.module_from_spec(VALIDATORS_SPEC)
VALIDATORS_SPEC.loader.exec_module(ADAPTER_VALIDATORS)


def test_adapter_lib_renders_and_loads_simple_yaml_mapping() -> None:
    rendered = ADAPTER_RENDER_LIB.render_yaml_mapping(
        [
            ("version", 1),
            ("repo", "demo"),
            ("output_dir", "charness-artifacts/demo"),
            ("policy", {"glob": "*-quality-gate.sh", "threshold": 30}),
            ("commands", ["pytest -q", "ruff check ."]),
            ("empty", []),
        ]
    )
    assert ADAPTER_LIB.load_yaml(rendered) == {
        "version": 1,
        "repo": "demo",
        "output_dir": "charness-artifacts/demo",
        "policy": {"glob": "*-quality-gate.sh", "threshold": 30},
        "commands": ["pytest -q", "ruff check ."],
        "empty": [],
    }


def test_adapter_lib_renders_and_loads_list_of_mappings() -> None:
    rendered = ADAPTER_RENDER_LIB.render_yaml_mapping(
        [
            (
                "startup_probes",
                [
                    {
                        "label": "demo-version",
                        "command": ["python3", "demo.py", "--version"],
                        "class": "standing",
                        "startup_mode": "warm",
                        "surface": "direct",
                        "samples": 2,
                    }
                ],
            )
        ]
    )
    assert ADAPTER_LIB.load_yaml(rendered) == {
        "startup_probes": [
            {
                "label": "demo-version",
                "command": ["python3", "demo.py", "--version"],
                "class": "standing",
                "startup_mode": "warm",
                "surface": "direct",
                "samples": 2,
            }
        ]
    }


def test_startup_probe_validator_rejects_invalid_timeout_seconds() -> None:
    errors: list[str] = []
    result = ADAPTER_VALIDATORS.startup_probes(
        [
            {
                "label": "demo",
                "command": ["demo"],
                "class": "standing",
                "startup_mode": "warm",
                "surface": "direct",
                "samples": 1,
                "timeout_seconds": 0,
            }
        ],
        errors,
    )

    assert result == []
    assert errors == ["startup_probes[0].timeout_seconds must be a positive number"]


def test_runtime_budget_intent_validates_always_conditional_and_external_groups() -> None:
    errors: list[str] = []
    result = ADAPTER_VALIDATORS.runtime_budget_intent(
        {
            "always": ["pytest"],
            "conditional": {"dead-code": "QUALITY_DEAD_CODE=1"},
            "external": {"consumer-gate": "runs in the consumer"},
        },
        errors,
    )

    assert errors == []
    assert result == {
        "always": ["pytest"],
        "conditional": {"dead-code": "QUALITY_DEAD_CODE=1"},
        "external": {"consumer-gate": "runs in the consumer"},
    }


def test_runtime_budget_intent_rejects_duplicate_and_unknown_groups() -> None:
    errors: list[str] = []
    result = ADAPTER_VALIDATORS.runtime_budget_intent(
        {
            "always": ["pytest", "pytest"],
            "conditional": {"pytest": "--release", "other": "trigger"},
            "unexpected": {},
        },
        errors,
    )

    assert result is not None
    assert any("unexpected is not a recognized key" in error for error in errors)
    assert any("declared more than once" in error for error in errors)


def test_runtime_budget_intent_helper_handles_none_and_malformed_groups() -> None:
    from skills.public.quality.scripts import runtime_budget_intent as helper

    assert helper.runtime_budget_intent(None, []) is None
    top_level_errors: list[str] = []
    assert helper.runtime_budget_intent("broken", top_level_errors) is None
    assert top_level_errors == ["runtime_budget_intent must be a mapping"]
    assert helper.runtime_budget_intent({"conditional": None}, []) == {
        "always": [],
        "conditional": {},
        "external": {},
    }

    errors: list[str] = []
    result = helper.runtime_budget_intent(
        {
            "always": "pytest",
            "conditional": ["not-a-mapping"],
            "external": {"": "trigger", "empty": "", "bad": 1},
            "unexpected": {},
        },
        errors,
    )

    assert result == {"always": [], "conditional": {}, "external": {}}
    assert any("always must be a list" in error for error in errors)
    assert any("conditional must be a mapping" in error for error in errors)
    assert any("external keys must be non-empty" in error for error in errors)
    assert any("external.empty must be a non-empty" in error for error in errors)
    assert any("external.bad must be a non-empty" in error for error in errors)
    assert any("unexpected is not a recognized" in error for error in errors)


def test_runtime_budget_universe_validator_keeps_the_consumer_command_shape() -> None:
    errors: list[str] = []
    result = ADAPTER_VALIDATORS.runtime_budget_universe(
        {"command": "./scripts/list-quality-labels.sh"},
        errors,
    )

    assert errors == []
    assert result == {"command": "./scripts/list-quality-labels.sh"}

    errors = []
    result = ADAPTER_VALIDATORS.runtime_budget_universe({"command": 7}, errors)
    assert result == {"command": 7}
    assert errors == ["runtime_budget_universe.command must be a string"]

    errors = []
    assert ADAPTER_VALIDATORS.runtime_budget_universe("broken", errors) is None
    assert errors == ["runtime_budget_universe must be a mapping"]


def test_adapter_validators_adds_its_sibling_directory_for_standalone_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolver_dir = str(Path(ADAPTER_VALIDATORS.__file__).resolve().parent)
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != resolver_dir])
    spec = importlib.util.spec_from_file_location(
        "adapter_validators_sibling_path_under_test",
        ADAPTER_VALIDATORS.__file__,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert resolver_dir in sys.path


def test_adapter_lib_loads_quoted_list_items_with_colons() -> None:
    loaded = ADAPTER_LIB.load_yaml(
        "\n".join(
            [
                "markers:",
                '  - "proof: pointer"',
                '  - "executable_proof: pointer"',
                "  - https://example.test/path",
                "",
            ]
        )
    )
    assert loaded == {
        "markers": ["proof: pointer", "executable_proof: pointer", "https://example.test/path"]
    }


def test_adapter_lib_loads_quoted_mapping_keys_with_colons() -> None:
    loaded = ADAPTER_LIB.load_yaml(
        "\n".join(
            [
                "runtime_budgets:",
                "  scripts/run-pre-push.py: 45000",
                '  "pre-push:full-pytest": 19000',
                '  "pre-push:meta-fast": 27000',
                "",
            ]
        )
    )
    assert loaded == {
        "runtime_budgets": {
            "scripts/run-pre-push.py": 45000,
            "pre-push:full-pytest": 19000,
            "pre-push:meta-fast": 27000,
        }
    }


def test_adapter_lib_renders_mapping_keys_with_colons_as_quoted_keys() -> None:
    rendered = ADAPTER_RENDER_LIB.render_yaml_mapping(
        [
            (
                "runtime_budgets",
                {
                    "scripts/run-pre-push.py": 45000,
                    "pre-push:full-pytest": 19000,
                    "pre-push:meta-fast": 27000,
                },
            )
        ]
    )
    assert '  "pre-push:full-pytest": 19000' in rendered
    assert ADAPTER_LIB.load_yaml(rendered) == {
        "runtime_budgets": {
            "scripts/run-pre-push.py": 45000,
            "pre-push:full-pytest": 19000,
            "pre-push:meta-fast": 27000,
        }
    }


def test_adapter_lib_loads_single_quoted_mapping_keys_with_escaped_quotes() -> None:
    loaded = ADAPTER_LIB.load_yaml("'pre''push:full': 19000\n")
    assert loaded == {"pre'push:full": 19000}


def test_adapter_lib_renders_newline_scalars_as_round_trippable_escapes() -> None:
    rendered = ADAPTER_RENDER_LIB.render_yaml_mapping([("body", "line1\nline2")])
    assert rendered == 'body: "line1\\nline2"\n'
    assert ADAPTER_LIB.load_yaml(rendered) == {"body": "line1\nline2"}


def test_adapter_lib_loads_carriage_return_escape_and_inline_empty_list_item() -> None:
    loaded = ADAPTER_LIB.load_yaml(
        "\n".join(
            [
                'body: "line1\\rline2"',
                "steps:",
                "  - command: []",
                "",
            ]
        )
    )
    assert loaded == {"body": "line1\rline2", "steps": [{"command": []}]}


def test_adapter_lib_loads_block_scalars_without_dropping_body() -> None:
    assert ADAPTER_LIB.load_yaml("body: |\n  line1\n  line2\n") == {"body": "line1\nline2\n"}
    assert ADAPTER_LIB.load_yaml("body: >-\n  line1\n  line2\n") == {"body": "line1 line2"}


@pytest.mark.parametrize("yaml_text", ["alias: *shared\n", "tagged: !custom value\n", "body: |+\n  line1\n"])
def test_adapter_lib_rejects_unsupported_yaml_constructs_loudly(yaml_text: str) -> None:
    with pytest.raises(ValueError, match="unsupported YAML construct"):
        ADAPTER_LIB.load_yaml(yaml_text)


def test_render_yaml_round_trips_a_list_item_carrying_nested_mappings_and_lists() -> None:
    """The nested branches inside a LIST ITEM had no coverage.

    A list of mappings whose values are themselves a mapping and a list is the shape
    adapter files actually use (reviewer tiers, quality phases), and it is the one the
    emitter renders through its deepest path. Round-tripped rather than string-matched,
    so the assertion pins the emitter's contract with the parser rather than its
    formatting.
    """
    value = [{"id": "a", "opts": {"k": "v"}, "tags": ["x", "y"], "empty": []}]
    rendered = ADAPTER_RENDER_LIB.render_yaml_mapping([("items", value)])

    assert ADAPTER_LIB.load_yaml(rendered) == {"items": value}
