#!/usr/bin/env python3

"""Apply `adapter_lib`'s optional-field vocabulary over a declared field spec.

Separate from `adapter_lib` for a portability reason, not a length one: that module
is deliberately stdlib-only so it can be imported as a bare sibling by scripts running
outside the `scripts` package, and this one imports from it. Callers of this helper are
already `scripts.`-package modules, so the dependency costs them nothing.

One loop instead of a copy per validator: the per-validator copies were a lexical clone
family the duplication gate caught the moment a fourth typed loop appeared.
"""

from __future__ import annotations

from typing import Any, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.adapter_lib import optional_int, optional_string, optional_string_list  # noqa: E402

__all__ = ["apply_optional_fields"]


def apply_optional_fields(
    data: dict[str, Any],
    validated: dict[str, Any],
    errors: list[str],
    *,
    string_fields: Sequence[str] = (),
    list_fields: Sequence[str] = (),
    int_fields: Sequence[tuple[str, int]] = (),
) -> None:
    """Write only what the adapter DECLARED; leave everything else to the consumer.

    An absent field is left out of `validated` rather than defaulted here, so a default
    keeps living with the consumer that enforces it -- a default written in two places
    is exactly the drift that makes a gate and its forecast disagree. A REFUSED field is
    likewise left out: the error is reported, and the consumer's fallback is the
    conservative arm, never a silent honoring of the bad value.

    `int_fields` entries are `(name, minimum)`. A caller whose refusal message carries
    field-specific operator guidance keeps its own loop; this is the shape for the ones
    that do not.
    """
    for field in string_fields:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value
    for field in list_fields:
        items = optional_string_list(data.get(field), field, errors)
        if items is not None:
            validated[field] = items
    for field, minimum in int_fields:
        number = optional_int(data.get(field), field, errors, minimum=minimum)
        if number is not None:
            validated[field] = number
