#!/usr/bin/env python3
"""How an operator's partial policy block combines with the preset, and what the
merge silently supplied.

Split out of ``quality_policy_defaults`` when that file passed its length cap. The
grouping is the concept, not the spill: these three functions are the merge and the
account OF the merge, and keeping them together is what stops the account from
drifting from the thing it describes -- the defect this module exists to report was
exactly a status computed somewhere the merge could not be seen.
"""
from __future__ import annotations

from typing import Any

# The DEFAULT_* dicts are imported INSIDE the two functions, not at module level, and
# that is not style. `quality_policy_defaults` re-exports these three names, so a
# module-level import here is a real cycle that resolves in exactly one order: import
# `defaults` first and it works, import THIS module first and `defaults` reaches its
# re-export line while this module has defined no functions yet, raising
# `ImportError: ... partially initialized module`. Measured, not theorised -- the first
# cut had it, and it was invisible to the whole test suite because every existing
# importer happens to reach `defaults` first. The first person to write
# `from scripts.quality_policy_merge import ...` at the top of a new test file would
# have found it, in a single-file pytest run that nobody else could reproduce.


def refilled_policy_subkeys(raw_value: Any, defaults: dict[str, Any], merged: dict[str, Any]) -> list[str]:
    """Which sub-keys a policy merge filled from defaults rather than from the operator.

    The merge functions below are permissive by design: a sub-key that is absent, or
    present with a type they do not accept, silently keeps the default. That is the
    right merge behaviour and the wrong thing to stay quiet about -- the field-level
    status is computed from whether the FIELD appears in the adapter, so a block the
    operator kept but partially emptied was reported ``preserved`` while the merge was
    refilling it. That is the deleted-on-purpose sub-key reading as never-set, one
    level below where the field-level absence vocabulary can see it.

    A sub-key counts as refilled when the merged value came from ``defaults`` and the
    raw block did not supply THAT value. A raw value that merely EQUALS the default is
    NOT refilled -- the operator wrote it, and calling that a refill would fire on every
    adapter that spells a default out.

    The test is ``raw_value.get(key) != merged[key]``, NOT ``key not in raw_value``.
    Keying on the key's ABSENCE caught only one of the three ways an operator empties a
    sub-key, and the other two are the same silent loss:

    * ``lefthook_path:`` with a blank value parses to ``{}`` (``adapter_lib._parse_empty_value``),
      so the key IS present, no merge branch accepts ``{}``, and the default was refilled
      while the status still said ``preserved``.
    * ``min_statements_threshold: 30.5`` against an ``int`` default is silently dropped by
      the merge's type check, the default wins, and the bootstrap then REWRITES the file
      with it -- so the operator's value is gone from disk before the resolution-time
      validator that would have complained ever sees it.

    Both are strictly worse than the deleted-line case this function was written for, and
    both were missed by the first cut. Int/float coercion stays safe because ``80 == 80.0``.

    A non-dict block (``coverage_floor_policy: "see docs/quality.md"``) reports EVERY key
    as refilled: the merge kept none of what was written, which is the maximal version of
    the same loss, and returning ``[]`` there reported the largest refill as ``preserved``.
    """
    if not isinstance(raw_value, dict):
        return sorted(defaults)
    return sorted(
        key
        for key, default in defaults.items()
        if merged.get(key) == default and raw_value.get(key) != merged.get(key)
    )


def merge_coverage_floor_policy(value: Any) -> dict[str, Any]:
    from scripts.quality_policy_defaults import DEFAULT_COVERAGE_FLOOR_POLICY

    merged_policy = dict(DEFAULT_COVERAGE_FLOOR_POLICY)
    if not isinstance(value, dict):
        return merged_policy
    for key, default_value in DEFAULT_COVERAGE_FLOOR_POLICY.items():
        item = value.get(key)
        if isinstance(default_value, str) and isinstance(item, str):
            merged_policy[key] = item
        elif isinstance(default_value, float) and isinstance(item, (int, float)):
            merged_policy[key] = float(item)
        elif isinstance(default_value, int) and isinstance(item, int):
            merged_policy[key] = item
    return merged_policy


def merge_prompt_asset_policy(value: Any) -> dict[str, Any]:
    from scripts.quality_policy_defaults import DEFAULT_PROMPT_ASSET_POLICY

    merged_policy = dict(DEFAULT_PROMPT_ASSET_POLICY)
    if not isinstance(value, dict):
        return merged_policy
    for field in ("source_globs", "exemption_globs"):
        item = value.get(field)
        if isinstance(item, list) and all(isinstance(entry, str) for entry in item):
            merged_policy[field] = list(item)
    min_chars = value.get("min_multiline_chars")
    if isinstance(min_chars, int):
        merged_policy["min_multiline_chars"] = min_chars
    return merged_policy
