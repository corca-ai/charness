#!/usr/bin/env python3

"""What an adapter RESOLVER owes: reconcile the version, validate the fields, build the payload.

The YAML dialect itself lives in ``adapter_yaml_parse`` and is re-exported below, so every
existing `from scripts.adapter_lib import load_yaml_file` keeps working. See that module's
docstring for the split and its reason.
"""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

# LOADED BY PATH WITH STDLIB ONLY, and that is a hard constraint rather than a style
# choice. This module is imported three ways: as `scripts.adapter_lib`, as a bare
# `adapter_lib` from a seeded test repo, and by absolute PATH from a skill script whose
# loader puts nothing on `sys.path`. The first cut of this split used
# `runtime_bootstrap.import_repo_module` and broke the third: every achieve and handoff
# skill script that reaches `adapter_lib` died with `No module named 'runtime_bootstrap'`.
# The pre-split file had no repo imports at all, which is why it worked everywhere.
#
# Registered in `sys.modules` under a stable key so the three load paths SHARE one
# instance. `_UNINTERPRETED_SINK` is a ContextVar living in that module: two copies means
# `load_yaml_report` arms one sink while `_parse_block` records into another, and the
# report comes back empty while the parse silently drops lines -- the exact silence this
# repo built the sink to end.
# KEYED ON THE RESOLVED PATH, not on a bare name. A bare key means the FIRST `adapter_lib`
# loaded in a process binds the parser for every later one from any tree -- so a vendored or
# stale charness beside a fresh one would silently share a parser, which is the wrong answer
# rendered as agreement. Same file therefore still means one instance and one sink; a
# different tree gets its own, which is what a different tree should get.
_YAML_PATH = Path(__file__).resolve().parent / "adapter_yaml_parse.py"
_YAML_MODULE_KEY = f"charness_adapter_yaml_parse::{_YAML_PATH}"
if (_yaml := sys.modules.get(_YAML_MODULE_KEY)) is None:
    _yaml_spec = importlib.util.spec_from_file_location(_YAML_MODULE_KEY, _YAML_PATH)
    _yaml = importlib.util.module_from_spec(_yaml_spec)
    sys.modules[_YAML_MODULE_KEY] = _yaml
    try:
        _yaml_spec.loader.exec_module(_yaml)
    except BaseException:
        # UNREGISTER ON FAILURE, as CPython's own importer does. Left registered, the empty
        # module short-circuits every later load in the process and each one dies with
        # `AttributeError: no attribute 'SUPPORTED_BLOCK_SCALAR_RE'` -- the second error
        # hiding the first. `plugin_import_smoke` execs every module in one process, so an
        # install missing this file would report the wrong cause for every adapter module.
        del sys.modules[_YAML_MODULE_KEY]
        raise

# Re-exported so `adapter_lib` remains the one import site for anything that reads or
# resolves an adapter. NOT fully transparent, and the difference is worth knowing before it
# bites: these are name BINDINGS, so `adapter_lib.load_yaml_file` is now
# `adapter_yaml_parse.load_yaml_file` and resolves `load_yaml` from THAT module's globals. A
# test that monkeypatches `adapter_lib.load_yaml` no longer reaches the file readers. No
# current seam depends on it -- every patcher in the suite calls the patched name directly --
# but "implementation detail" would overclaim.
SUPPORTED_BLOCK_SCALAR_RE = _yaml.SUPPORTED_BLOCK_SCALAR_RE
strip_inline_comment = _yaml.strip_inline_comment
inline_comment_start = _yaml.inline_comment_start
load_yaml = _yaml.load_yaml
load_yaml_file = _yaml.load_yaml_file
load_yaml_report = _yaml.load_yaml_report
load_yaml_file_report = _yaml.load_yaml_file_report
# PRIVATE names other modules and tests reach for by name. Re-exported deliberately rather
# than left to break: they are the parser internals this repo's own gates probe (`#530`'s
# indent axis, the flow-sequence class, the document-marker rule), and a split that silently
# renamed them would be the split hiding a behavior change.
_DOCUMENT_MARKERS = _yaml._DOCUMENT_MARKERS
_find_mapping_separator = _yaml._find_mapping_separator
_line_shape = _yaml._line_shape
_mapping_value = _yaml._mapping_value
_parse_block = _yaml._parse_block
_parse_empty_value = _yaml._parse_empty_value
_reject_unsupported_scalar = _yaml._reject_unsupported_scalar
_coerce_scalar = _yaml._coerce_scalar
_split_mapping_entry = _yaml._split_mapping_entry
_parse_list_items = _yaml._parse_list_items
_parse_block_scalar = _yaml._parse_block_scalar
_UNINTERPRETED_SINK = _yaml._UNINTERPRETED_SINK

def uninterpreted_warnings(uninterpreted: list[dict[str, Any]]) -> list[str]:
    """One operator-facing line per line the parser could not interpret. Lives here, with
    the producer of the facts, so every adapter resolver words the same finding the same
    way instead of each inventing its own phrasing."""
    return [
        f"line {entry['line']} was not interpreted ({entry['reason']}): {entry['text'].strip()!r}. "
        "Any field it meant to set is serving an inferred default instead."
        for entry in uninterpreted
    ]


UNINTERPRETED_WARNING_MARKER = " was not interpreted ("


def unreadable_reasons(adapter: dict[str, Any]) -> list[str]:
    """The loader's own complaints that make ANY verdict from this adapter unsafe.

    A refused parse, plus every line the parser silently DROPPED -- a dropped line is
    exactly where the key a probe reads would have been, and `uninterpreted_warnings`
    above says so in its own text ("Any field it meant to set is serving an inferred
    default instead"). So a half-read adapter can establish neither a `no` nor an
    opt-out; only `not-established` is honest.

    Lives beside the producer of both facts because a consumer that re-derives this
    grows a second, drifting copy of the loader's verdict. Other warnings are NOT
    reasons: "no adapter found" is the opt-in design, not a failure to read one.
    """
    reasons = [str(error) for error in (adapter.get("errors") or [])]
    reasons += [
        str(warning)
        for warning in (adapter.get("warnings") or [])
        if UNINTERPRETED_WARNING_MARKER in str(warning)
    ]
    return reasons


def read_declared_adapter(path: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    """``(raw_data, parse_errors, warnings)`` for one adapter document, BOTH channels live.

    The single owner of the lines every resolver in this repo writes before it validates
    anything: read the file, refuse a document the parser cannot read, and report the lines
    it silently dropped. `simple_skill_adapter_lib` already did all three for the eleven
    skills that route through it; five more libraries called `load_yaml_file` bare and got
    neither (#673).

    WHAT THAT COST, and it is a consumer-guard hole rather than a message-shape complaint.
    `adapter_version_verdict` refuses on the CONDITION "this reader honored nothing the repo
    declared", and reaches it through three doors: a refused `version`, a refused PARSE, and
    a silently DROPPED line. The second door keys on `errors` and the third on `warnings`,
    so for a resolver that raises before either exists, both are structurally dead --
    `parse_refused` and `declarations_dropped` answer False for inputs that are exactly what
    they were written to catch. Every consumer guard in those skills had a blind arm that
    the others did not, and no test could tell, because the resolver never returned.

    Returning parse errors SEPARATELY from validation errors, rather than raising, is what
    lets each caller keep its own payload shape: it feeds `{}` to its own validator, gets its
    own inferred defaults, and prepends these. That is the same end state
    `simple_skill_adapter_lib` produces -- defaults plus `parse_failure_error` in `errors` --
    reached without every caller re-deciding what a refused document should return -- with one
    measured DIFFERENCE, stated rather than left silent: the five run their own validator over
    `{}` on the refusal path, so they emit that validator's absent-field WARNINGS (quality's
    "No gate_commands configured", achieve's audit-only default) where
    `simple_skill_adapter_lib` returns `warnings=[]`. Harmless for `declarations_dropped`,
    which is marker-keyed, and more informative for an operator; not identical, so the
    sentence above says "the same end state" about `data` and `errors`, not about `warnings`.
    """
    try:
        raw, uninterpreted = load_yaml_file_report(path)
    except ValueError as exc:
        return {}, [parse_failure_error(exc)], []
    # NO non-mapping arm. `load_yaml` returns `_parse_block(...)[0]`, which is always a
    # dict, so the guard the four callers used to write here could not fire -- and the
    # changed-line gate is what made that visible, because an unreachable branch has no
    # covering test by construction. The shape those callers were guarding against is
    # reported by the uninterpreted-line sink instead, which is what actually sees it.
    return raw, [], uninterpreted_warnings(uninterpreted)


def resolve_declared_adapter(
    path: Path, validate: Callable[[dict[str, Any], Path], tuple[dict[str, Any], list[str], list[str]]],
    repo_root: Path,
) -> tuple[dict[str, Any], list[str], list[str]]:
    """``(data, errors, warnings)`` for one adapter document and its skill's own validator.

    `read_declared_adapter` plus the caller's validator, with the two error channels merged
    in the order that reads correctly: a PARSE refusal first, because it is the reason every
    field below it is an inferred default rather than a declared value.
    """
    raw_data, parse_errors, warnings = read_declared_adapter(path)
    data, errors, extra_warnings = validate(raw_data, repo_root)
    return data, [*parse_errors, *errors], [*warnings, *extra_warnings]


def resolve_adapter_payload(
    repo_root: Path,
    *,
    candidates: Sequence[Path],
    infer_defaults: Callable[[Path], dict[str, Any]],
    validate: Callable[[dict[str, Any], Path], tuple[dict[str, Any], list[str], list[str]]],
    absent_warnings: Callable[[dict[str, Any]], list[str]],
    derive: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """The seven-key resolver payload every adapter library in this repo returns.

    `simple_skill_adapter_lib` has been this for eleven skills since it was written. The
    five that did not route through it hand-wrote the same two branches -- find the file,
    return inferred defaults with an opt-in warning when it is absent, otherwise read,
    validate and report -- and `#673` made them converge the rest of the way, which the
    duplicate ratchet caught in the same run. That is `#550`'s subject ("adapter resolver
    bodies are near-identical") narrowing, not a new debt.

    `derive` is the escape hatch for what is genuinely per-skill, and it is deliberately a
    function of `data` ALONE: `artifact_path`, `record_artifact_pattern` and
    `bootstrap_expectations` are computed from the resolved payload in BOTH branches today,
    and writing them twice per caller is how the found/absent arms drift apart. Anything
    that needs the adapter PATH -- create-skill's shape check re-reads the file -- or the RAW
    mapping -- announcement's `field_state` -- stays with its caller rather than growing a
    second parameter here, which would re-admit exactly that drift.

    NOT a replacement for `simple_skill_adapter_lib`, which also owns preset lineage and
    host extensions. This is the smaller shape those five actually share.
    """
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in candidates]
    adapter_path = next(
        (repo_root / candidate for candidate in candidates if (repo_root / candidate).is_file()), None
    )
    if adapter_path is None:
        data = infer_defaults(repo_root)
        errors: list[str] = []
        warnings = list(absent_warnings(data))
    else:
        data, errors, warnings = resolve_declared_adapter(adapter_path, validate, repo_root)
    return {
        "found": adapter_path is not None,
        "valid": not errors,
        "path": str(adapter_path) if adapter_path is not None else None,
        "data": data,
        **(derive(data) if derive is not None else {}),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def parse_failure_error(exc: Exception) -> str:
    """The message for a construct the parser refuses outright, as opposed to one it
    silently drops. A refusal is not a drop and must not read like one."""
    return f"adapter could not be parsed: {exc}"


# The one adapter schema version every resolver in this repo speaks. It lives here, with
# the loader the resolvers already share, because the alternative was measured: 17 sites
# hand-copied a `version` check and 16 of them only asked "is it an int?", then wrote the
# answer into the resolved payload as authoritative. A repo could declare `version: 9` and
# every one of those 16 echoed 9 back as if it had been honoured. `bool` is excluded
# explicitly because `isinstance(True, int)` is True and this module's own scalar coercion
# turns a bare `true` into `True` -- so `version: true` read as a valid integer version at
# all 17 sites, including the one that did check a supported value.
SUPPORTED_ADAPTER_VERSION = 1


def validate_adapter_version(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str],
    *, supported: int | None = None, field: str = "version", required: bool = False,
) -> None:
    """Reconcile a declared adapter ``version`` against the version this reader speaks.

    Absent is legal by default and leaves the caller's inferred default in place. A
    non-integer and an unsupported integer are both errors, and neither writes
    ``validated[field]``: a version the reader cannot interpret must not come back out as
    authoritative. Message wording is fixed by existing callers' fixtures and is
    deliberately not reworded here.

    ``supported`` resolves at CALL time, not at definition time. As a plain default it
    would bind ``SUPPORTED_ADAPTER_VERSION``'s value once at import, so rebinding the
    module constant -- which is exactly what a bump, or a test proving the bump path,
    would do -- changed nothing while appearing to work.

    ``required`` is a parameter rather than a caller-side pre-check because the
    commit-time gate needs a stricter answer than the resolvers do: it refuses an adapter
    declaring no version at all, while a resolver falls back to its inferred default.
    That difference lives here, with the contract, so the strict site does not hand-roll a
    predicate beside the shared one -- hand-rolled predicates beside a shared check are
    exactly how 18 sites came to disagree in the first place.
    """
    supported = SUPPORTED_ADAPTER_VERSION if supported is None else supported
    value = data.get(field)
    if value is None:
        if required:
            errors.append(f"{field} is required")
        return
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{field} must be an integer")
    elif value != supported:
        errors.append(f"{field} must be {supported}")
    else:
        validated[field] = value


def declared_fields_after_version_check(
    data: dict[str, Any], validated: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    """The declared fields a reader may honor: the adapter's own on a version this reader SPEAKS,
    an EMPTY mapping on one it does not. The question every caller of `validate_adapter_version`
    answers next, and 15 of 18 answered wrong -- a `version: 9` adapter still selected
    `output_dir`, `repo` and the debug/quality line ceilings. A version the reader cannot
    interpret says nothing about what its siblings MEAN, so honoring them is the "silent
    honoring of the bad value" `apply_optional_fields` refuses for a single refused FIELD. An
    EMPTY mapping, not an early return: these validators derive keys `infer_defaults` never
    seeds, so a bare `return` hands consumers a payload missing keys they index. Census proof in
    `tests/quality_gates/test_adapter_version_reconciliation.py`.
    """
    before = len(errors)
    validate_adapter_version(data, validated, errors)
    return {} if len(errors) > before else data


def optional_string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def optional_string_list(value: Any, field: str, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return None
    return list(value)


def optional_int(value: Any, field: str, errors: list[str], *, minimum: int = 0) -> int | None:
    """The numeric member of this module's adapter-field vocabulary.

    Its absence is why every numeric policy in the artifact-validator family --
    `MAX_ARTIFACT_LINES` in debug/quality, `DEFAULT_MAX_CONTENT_LINES` in handoff --
    was a module constant a consuming repo could not touch: the vocabulary offered
    `optional_string`, `optional_string_list` and `optional_bool`, so a numeric field
    had nowhere to land and each caller that needed one hand-rolled its own
    `isinstance` check outside the vocabulary.

    `isinstance(True, int)` is True, so the bool guard is load-bearing rather than
    defensive: without it `max_artifact_lines: yes` parses to `True` and validates as
    the integer 1, which refuses every artifact past its title line.

    There is deliberately NO upper bound. A ceiling a repo sets on its own artifacts is
    not an external boundary -- the same adapter already owns `output_dir` and
    `artifact_class` -- and clamping it would reintroduce a charness-chosen number by
    the back door, which is the defect this field exists to remove.
    """
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{field} must be an integer")
        return None
    if value < minimum:
        errors.append(f"{field} must be greater than or equal to {minimum}")
        return None
    return value


def optional_bool(value: Any, field: str, errors: list[str]) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        errors.append(f"{field} must be a boolean")
        return None
    return value


def list_field_state(data: dict[str, Any], field: str) -> str:
    if field not in data:
        return "unset"
    value = data.get(field)
    if isinstance(value, list) and len(value) == 0:
        return "explicit-empty"
    return "configured"


def plan_generated_write(
    existing_text: str | None, rendered_text: str, *, also_unchanged_when: bool = False
) -> str:
    """Classify what writing `rendered_text` over `existing_text` would do.

    Returns `absent` (no file yet), `unchanged`, or `differs`. Deciding this BEFORE
    touching the disk is what lets a dry run report the same verdict a real run would
    reach, and what keeps a generator from rewriting a file it has nothing to change in.
    Callers map the three outcomes onto their own status vocabulary and their own policy
    for whether `differs` may overwrite.
    """
    if existing_text is None:
        return "absent"
    return "unchanged" if existing_text == rendered_text or also_unchanged_when else "differs"


def write_adapter_scaffold(repo_root: Path, output: Path, contents: str, force: bool) -> Path:
    resolved_output = output if output.is_absolute() else repo_root / output
    if resolved_output.exists() and not force:
        raise SystemExit(f"Adapter already exists at {resolved_output}. Use --force to overwrite.")

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(contents, encoding="utf-8")
    return resolved_output
