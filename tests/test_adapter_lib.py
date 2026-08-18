from __future__ import annotations

from scripts.adapter_lib import (
    list_field_state,
    optional_bool,
    optional_int,
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


def test_optional_int_refuses_bools_and_values_below_the_minimum() -> None:
    errors: list[str] = []

    assert optional_int(240, "max_artifact_lines", errors, minimum=1) == 240
    assert optional_int(None, "max_artifact_lines", errors, minimum=1) is None
    assert optional_int(0, "max_artifact_lines", errors, minimum=1) is None
    assert optional_int(0, "guard_min_lines", errors) == 0
    # `isinstance(True, int)` is True, so without the explicit bool guard
    # `max_artifact_lines: yes` would validate as the integer 1 and refuse every
    # artifact past its title line. This asserts the refusal, not the coercion.
    assert optional_int(True, "max_artifact_lines", errors, minimum=1) is None
    assert optional_int("240", "max_artifact_lines", errors, minimum=1) is None

    assert errors == [
        "max_artifact_lines must be greater than or equal to 1",
        "max_artifact_lines must be an integer",
        "max_artifact_lines must be an integer",
    ]


def test_optional_int_has_no_upper_bound() -> None:
    """A ceiling the repo sets on its own artifacts is not an external boundary.

    Clamping it would reintroduce a charness-chosen number by the back door, which
    is the defect the adapter-configurable budget exists to remove.
    """
    errors: list[str] = []

    assert optional_int(100_000, "max_artifact_lines", errors, minimum=1) == 100_000
    assert errors == []


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
