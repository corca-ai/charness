from __future__ import annotations

from scripts.adapter_lib import (
    list_field_state,
    optional_bool,
    optional_string,
    optional_string_list,
)


def test_optional_field_helpers_validate_shape_and_preserve_values() -> None:
    errors: list[str] = []

    assert optional_string("demo", "name", errors) == "demo"
    assert optional_string(None, "name", errors) is None
    assert optional_string(3, "name", errors) is None
    assert optional_string_list(["a", "b"], "items", errors) == ["a", "b"]
    assert optional_string_list(None, "items", errors) is None
    assert optional_string_list(["a", 2], "items", errors) is None
    assert optional_bool(True, "enabled", errors) is True
    assert optional_bool(None, "enabled", errors) is None
    assert optional_bool("yes", "enabled", errors) is None

    assert errors == [
        "name must be a string",
        "items must be a list of strings",
        "enabled must be a boolean",
    ]


def test_list_field_state_distinguishes_absent_empty_and_configured() -> None:
    data = {
        "empty": [],
        "values": ["one"],
        "scalar": "configured",
    }

    assert list_field_state(data, "missing") == "unset"
    assert list_field_state(data, "empty") == "explicit-empty"
    assert list_field_state(data, "values") == "configured"
    assert list_field_state(data, "scalar") == "configured"
