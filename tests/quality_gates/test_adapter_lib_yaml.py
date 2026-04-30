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
        "\n".join(["markers:", '  - "proof: pointer"', '  - "executable_proof: pointer"', ""])
    )
    assert loaded == {"markers": ["proof: pointer", "executable_proof: pointer"]}
