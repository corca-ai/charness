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
# `from scripts.adapters.quality_policy_merge import ...` at the top of a new test file would
# have found it, in a single-file pytest run that nobody else could reproduce.


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

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

    A NESTED block the operator partially supplied is recursed into and its refilled
    leaves reported dotted (``report_paths.sample_md``). Comparing only top-level keys
    was this rule stopping exactly one level above the next instance, for the third time
    in the family -- whole-field, then sub-key, then sub-sub-key. It had two arms, and the
    quieter one is worse: with ``report_paths`` refilled to exactly the default the block
    at least got named, but once the operator customised ONE leaf the block no longer
    equalled the default, the ``merged == default`` test failed, and a partially refilled
    block vanished from the report entirely.

    Recursion is for a block the operator wrote SOMETHING into. An absent, non-dict, or
    empty raw block was refilled WHOLE, and naming its block once says that better than
    naming every leaf under it -- a report nobody reads is the failure mode this repo has
    already measured, so the granularity goes where the ambiguity is. (A block whose keys
    are all typos was also refilled whole, but takes the recursion branch and names its
    leaves; that is the more useful answer, not an accident to preserve.)

    Whether to recurse at all is a STRUCTURAL question -- did the merge produce a block
    carrying every default key? If it did not (absent, non-dict, ``{}``, or missing keys)
    the recursion can find nothing, so the BLOCK name is reported rather than nothing:
    going quiet about a block the operator wrote is the arm of this defect that was worse
    than the coarseness. Asking it as ``merged != default`` instead was measured wrong in
    the opposite direction -- a block written out IN FULL with customised values is also
    unequal to the defaults, and naming it as refilled is a MIS-name. Over-naming a real
    loss is the only direction this function may err in.

    Dotted names are also the deliberate-absence vocabulary. Bootstrap records refills
    first, then removes a declared dotted leaf before rendering and removes that leaf
    from the refill report, so the merge stays permissive without overriding intent.
    """
    if not isinstance(raw_value, dict):
        return sorted(defaults)
    names: list[str] = []
    for key, default in defaults.items():
        raw_sub = raw_value.get(key)
        merged_sub = merged.get(key)
        if isinstance(default, dict) and isinstance(raw_sub, dict) and raw_sub:
            # Did the merge actually produce a whole block? That is a STRUCTURAL question,
            # and asking it any other way has been wrong twice. A merged block that is
            # absent, non-dict, `{}`, or missing keys yields no leaves from the recursion
            # -- every leaf test compares against `merged_sub.get(leaf)` -- so swallowing
            # the block name on top of that would report a refilled block as NOTHING, and
            # silence is the arm of this defect that was worse than the coarseness.
            #
            # Two rejected predicates, both measured wrong:
            #   `isinstance(merged_sub, dict)` stopped at the TYPE boundary, and `{}` is a
            #   dict, so it recursed, found nothing, and went silent anyway.
            #   `merged_sub != default` then over-fired in the other direction: a block the
            #   operator wrote out IN FULL with customised values is also unequal to the
            #   defaults, so it got named as refilled when nothing was. That is a
            #   MIS-name, which this function must never do -- over-naming is the only
            #   direction it is allowed to err in.
            if isinstance(merged_sub, dict) and set(default) <= set(merged_sub):
                names.extend(
                    f"{key}.{leaf}"
                    for leaf in refilled_policy_subkeys(raw_sub, default, merged_sub)
                )
            else:
                names.append(key)
            continue
        if merged_sub == default and raw_sub != merged_sub:
            names.append(key)
    return sorted(names)


def merge_coverage_floor_policy(value: Any) -> dict[str, Any]:
    from scripts.adapters.quality_policy_defaults import DEFAULT_COVERAGE_FLOOR_POLICY

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
    from scripts.adapters.quality_policy_defaults import DEFAULT_PROMPT_ASSET_POLICY

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
