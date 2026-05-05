from __future__ import annotations

from .support import ADAPTER_LIB


def test_adapter_lib_renders_and_loads_simple_yaml_mapping() -> None:
    rendered = ADAPTER_LIB.render_yaml_mapping(
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
    rendered = ADAPTER_LIB.render_yaml_mapping(
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
    rendered = ADAPTER_LIB.render_yaml_mapping(
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
