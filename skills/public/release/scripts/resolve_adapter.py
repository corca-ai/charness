#!/usr/bin/env python3
from __future__ import annotations

import re
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()

_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.simple_skill_adapter_lib"
)
load_adapter_contract = _scripts_simple_skill_adapter_lib_module.load_adapter_contract
_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
optional_string = _scripts_adapter_lib_module.optional_string
declared_fields_after_version_check = _scripts_adapter_lib_module.declared_fields_after_version_check
optional_string_list = _scripts_adapter_lib_module.optional_string_list
optional_bool = _scripts_adapter_lib_module.optional_bool

STRING_FIELDS = (
    "repo", "language", "output_dir", "preset_id", "preset_version", "customized_from",
    "package_id", "packaging_manifest_path", "checked_in_plugin_root", "sync_command",
    "quality_command", "post_publish_install_refresh", "post_publish_distinct_channel_probe",
    "post_publish_version_readback", "post_publish_doctor_readback", "requested_review_policy",
)
LIST_FIELDS = (
    "update_instructions",
    "requested_review_commands", "review_unavailable_patterns", "review_waiver_phrases", "product_surfaces",
    "cli_skill_surface_probe_commands", "cli_skill_surface_command_docs", "cli_skill_surface_skill_paths",
    "cli_skill_surface_change_globs", "fresh_checkout_probes", "required_release_surfaces",
    "unpublished_release_surfaces",
)
SPECIALIZED_RELEASE_LANE_FIELDS = ("id", "workflow", "tag_pattern", "command")
#: Boolean adapter fields, each with its default in `infer_repo_defaults`.
#:
#: `require_derived_release_claims` defaults to TRUE, and the direction is the whole
#: point. A gate armed by an opt-IN line is disarmed by deleting that line, with
#: nothing red -- the `bar-recorded-as-prose` shape this repo has already paid
#: for. Defaulting to true inverts it: deleting the line RE-ARMS the gate, so the
#: only way to publish unguarded notes is to write the opt-out down, where a
#: reviewer can see it.
BOOL_FIELDS = ("require_derived_release_claims",)

ARTIFACT_FILENAME = "latest.md"

#: The two adapter fields whose value is RUN by a subprocess rather than read by a
#: human: `bump_version.run_sync` shells out to `sync_command`, and the release lane
#: shells out to `quality_command`. Their `infer_repo_defaults` values name THIS
#: authoring repo's own tooling, so a consumer who never wrote a release adapter
#: inherits a command that cannot exist in their tree. Naming them here is what keeps
#: the check below on executed fields only -- a documentation placeholder is correct
#: in a field a reader reads and is a broken command in one an executor runs.
EXECUTED_COMMAND_FIELDS = ("sync_command", "quality_command")
#: The stable substring every executed-command warning carries, so `load_adapter` can
#: tell whether validation already emitted them without knowing which loader exit ran.
EXECUTED_WARNING_MARKER = "is EXECUTED and names"
#: The only candidate shape `command_script_target` will answer for. An allowlist, so a
#: character it has never seen is a silent no-judgement instead of a false refusal.
_PLAIN_PATH_RE = re.compile(r"(?:\./)?[A-Za-z0-9._/-]+")


def command_script_target(command: str) -> str | None:
    """The repo-relative script path a command STRING would execute, or ``None``.

    Blind class, stated before the acceptance rather than after it: this reads a
    string, not a shell. It recognizes exactly the two shapes this repo's own
    defaults use -- ``python3 <relative-path>`` and ``./<relative-path>`` -- and
    answers ``None`` for everything else. ``None`` means THIS DID NOT JUDGE, never
    "the command is fine".

    NOT JUDGED, and each of these is a missed warning rather than a wrong one: a
    pipeline, chain, redirect or grouping in ANY spelling, spaced or not; a ``cd``
    prefix; an env assignment prefix (``FOO=1 python3 ...``); any interpreter
    spelled other than ``python3`` (``python``, ``python3.11``, ``bash``, ``node``,
    ``uv run``); an interpreter option before the path (``python3 -u ...``); the
    ``-m`` module form; an absolute path; a path built from a variable; a bare
    relative path with no ``./``; a parent-relative path (``../x/y.py``); and any
    candidate carrying a character outside ``[A-Za-z0-9._/-]`` -- a quote, ``~``, a
    glob or glob class, a brace expansion, a backslash -- whose real target only
    the shell knows.

    The narrowness is deliberate and is the point of the READ/RUN field split. These
    fields are EXECUTED, so a recognizer that guessed wrong would refuse a command
    that works -- the failure mode that got the previous attempt at this class
    reverted. Two review rounds found such guesses: first quoted, tilde and glob
    candidates, then -- in the blacklist written to stop those -- ``;``, ``|``,
    ``&``, redirects, brace expansion and glob classes, every one of them a hard
    refusal of a working release. The allowlist below is what that cost, and it is
    the shape a blacklist could not have: it cannot go stale.
    """
    parts = command.split()
    if not parts:
        return None
    if parts[0] == "python3" and len(parts) >= 2:
        candidate = parts[1]
    elif parts[0].startswith("./"):
        candidate = parts[0]
    else:
        return None
    if candidate.startswith("-") or candidate.startswith("/"):
        return None
    # An ALLOWLIST, not a blacklist of shell metacharacters. `command.split()` splits on
    # whitespace only, so any unspaced operator stays glued to the token: `scripts/x.py;`,
    # `scripts/x.py|tee`, `scripts/x.py&&python3`, `scripts/x{a,b}.py`, `scripts/x[0-9].py`
    # are all candidates the shell rewrites and this cannot. A blacklist missed every one
    # of those and turned each into a hard refusal of a working release -- and could never
    # be proven complete, since it goes stale as shells add syntax. Inverted, an unlisted
    # character is a silent None: a missed warning, which is the harmless direction.
    if not _PLAIN_PATH_RE.fullmatch(candidate):
        return None
    if ".." in Path(candidate).parts:
        return None
    return candidate.removeprefix("./")


def _executed_command_warnings(
    data: dict[str, Any], validated: dict[str, Any], repo_root: Path
) -> list[str]:
    """One warning per EXECUTED command field naming a script this repo does not have.

    A warning rather than an error: the command may legitimately be resolvable at run
    time in a way this recognizer cannot see (a `PATH` lookup, a generated script), and
    refusing adapter resolution over a string parse would make the release lane
    unusable for a shape nobody predicted.

    The teeth are at `bump_version`, and they cover `sync_command` ONLY -- that is the
    one whose executor mutates the packaging manifest BEFORE running it, so a missing
    script there leaves half-applied state. `quality_command` runs in
    `publish_release_common` where a failure aborts before anything is published, so it
    is warned about and not preflighted. Stated because "the teeth are at bump_version"
    reads as covering both members of the tuple and does not.
    """
    warnings: list[str] = []
    for field in EXECUTED_COMMAND_FIELDS:
        target = command_script_target(validated[field])
        if target is None or (repo_root / target).exists():
            continue
        # Three origins, not two. A key present with an UNUSABLE value (a number, or a
        # bare `sync_command:` with nothing after it) is dropped by `optional_string`, so
        # `validated[field]` is this repo's inferred default while `field in data` is
        # true. Reported as either extreme, the operator is told their adapter set a path
        # their adapter does not contain -- and the bare-key spelling raises no error at
        # all, so nothing else would correct them.
        if field not in data:
            origin = "the inferred default, which names this authoring repo's own tooling"
        elif data[field] == validated[field]:
            origin = "set in the release adapter"
        else:
            origin = (
                "the key is present in the release adapter but its value was not usable, "
                "so the inferred default is in force"
            )
        warnings.append(
            f"{field} {EXECUTED_WARNING_MARKER} {target!r}, which does not exist under "
            f"{repo_root} ({origin}); set {field} to a command this repo can run"
        )
    return warnings

_release_backend_module = SKILL_RUNTIME.load_local_skill_module(__file__, "release_backend")
default_release_backend = _release_backend_module.default_release_backend
_parse_release_backend = _release_backend_module.parse_release_backend


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    package_id = repo_root.name
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "charness-artifacts/release",
        "artifact_class": "history",
        "package_id": package_id,
        "packaging_manifest_path": f"packaging/{package_id}.json",
        "checked_in_plugin_root": f"plugins/{package_id}",
        "sync_command": "python3 scripts/sync_root_plugin_manifests.py --repo-root .",
        "quality_command": "./scripts/run-quality.sh",
        "post_publish_install_refresh": "",
        "post_publish_version_readback": "",
        "post_publish_doctor_readback": "",
        "post_publish_distinct_channel_probe": "",
        "update_instructions": [],
        "requested_review_commands": [],
        "requested_review_policy": "warn-if-unconfigured",
        "review_unavailable_patterns": [
            "review unavailable", "requested review unavailable", "review gate unavailable",
            "review skipped because", "executor_variants", "no executor_variants",
        ],
        "review_waiver_phrases": [
            "review waiver:", "explicit review waiver:", "requested review waiver:",
        ],
        "product_surfaces": [],
        "cli_skill_surface_probe_commands": [],
        "cli_skill_surface_command_docs": [],
        "cli_skill_surface_skill_paths": [],
        "cli_skill_surface_change_globs": [],
        "fresh_checkout_probes": [],
        # Generated release surfaces this repo asserts it publishes. An ABSENT surface is
        # otherwise indistinguishable from a matching one at the version-drift check
        # (sweep row S35), so declaring them here is what turns "the file is gone" into
        # drift. Empty by default: a consumer that publishes only some surfaces must not
        # be forced red by a list it never wrote.
        "required_release_surfaces": [],
        # D48: the opt-out channel, deliberately NOT an overload of the field above.
        # `required_release_surfaces` means "these must exist", so naming a surface you
        # do not publish there makes it drift -- it cannot be the remedy for not
        # publishing it. A repo states here, once, which generated surfaces it does not
        # ship; their absence then reads as intent instead of as an unexplained pass that
        # nothing corroborates. Empty by default, and absence alone is still never drift.
        "unpublished_release_surfaces": [],
        "specialized_release_lanes": [],
        # Notes supplied to publish must carry a derived claim block that agrees
        # with the tree. See BOOL_FIELDS for why the default is true rather than
        # an opt-in.
        "require_derived_release_claims": True,
        "release_backend": default_release_backend(),
    }


def _specialized_release_lanes(value: Any, errors: list[str]) -> list[dict[str, str]]:
    """Read the optional, repo-declared release route without executing it.

    A specialized lane is an explicit escape from the generic release adapter. Keeping
    the declaration structured makes the planner's route exact and keeps a typo from
    becoming an inert adapter key. The command is read-only to this resolver; the release
    planner only emits it for an operator to inspect or run through that repo's lane.
    """
    if value is None:
        return []
    if not isinstance(value, list):
        errors.append("specialized_release_lanes must be a list of mappings")
        return []
    lanes: list[dict[str, str]] = []
    allowed = set(SPECIALIZED_RELEASE_LANE_FIELDS)
    seen: set[str] = set()
    for index, raw_lane in enumerate(value):
        label = f"specialized_release_lanes[{index}]"
        if not isinstance(raw_lane, dict):
            errors.append(f"{label} must be a mapping")
            continue
        for key in sorted(set(raw_lane) - allowed):
            errors.append(f"{label}.{key} is not a recognized key")
        lane: dict[str, str] = {}
        for field in SPECIALIZED_RELEASE_LANE_FIELDS:
            field_value = raw_lane.get(field)
            if not isinstance(field_value, str) or not field_value.strip():
                errors.append(f"{label}.{field} must be a non-empty string")
                continue
            lane[field] = field_value
        lane_id = lane.get("id")
        if lane_id is not None:
            if lane_id in seen:
                errors.append(f"{label}.id duplicates specialized release lane {lane_id!r}")
            seen.add(lane_id)
        if len(lane) == len(SPECIALIZED_RELEASE_LANE_FIELDS):
            lanes.append(lane)
    return lanes


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

    data = declared_fields_after_version_check(data, validated, errors)

    for field in STRING_FIELDS:
        value = optional_string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    for field in LIST_FIELDS:
        value = optional_string_list(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    for field in BOOL_FIELDS:
        flag = optional_bool(data.get(field), field, errors)
        if flag is not None:
            validated[field] = flag

    specialized_lanes = _specialized_release_lanes(data.get("specialized_release_lanes"), errors)
    if not errors or specialized_lanes:
        validated["specialized_release_lanes"] = specialized_lanes

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["sync_command"]:
        errors.append("sync_command must not be empty")
    if not validated["quality_command"]:
        errors.append("quality_command must not be empty")
    if validated["requested_review_policy"] not in {"warn-if-unconfigured", "advisory-only"}:
        errors.append("requested_review_policy must be 'warn-if-unconfigured' or 'advisory-only'")

    validated["release_backend"] = _parse_release_backend(data.get("release_backend"), errors, warnings)
    warnings.extend(_executed_command_warnings(data, validated, repo_root))

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    return _scripts_simple_skill_adapter_lib_module.find_adapter(repo_root, "release")


def load_adapter(repo_root: Path) -> dict[str, Any]:
    payload = _load_adapter_contract(repo_root)
    # TWO of `load_adapter_contract`'s three exits skip `validate_adapter_data`, and both
    # hand back `infer_repo_defaults` -- commands naming THIS repo's `scripts/`. One is
    # the no-adapter path (the case that matters most: a consuming repo that never wrote
    # a release adapter). The other is an adapter the YAML parser refused outright, which
    # returns `found=True` with errors; its reader is still shown foreign commands, so it
    # gets the warning too. The parsed-and-valid path is covered inside validation and
    # must not be double-appended here.
    #
    # Idempotent by construction rather than by knowing which exit ran: re-deriving the
    # same check over `payload["data"]` adds nothing when validation already covered it,
    # and the marker test stops the one case that would DUPLICATE -- a parsed adapter
    # whose validation already emitted these warnings with a different origin clause.
    if not any(EXECUTED_WARNING_MARKER in warning for warning in payload["warnings"]):
        payload["warnings"].extend(_executed_command_warnings({}, payload["data"], repo_root))
    return payload


def _load_adapter_contract(repo_root: Path) -> dict[str, Any]:
    return load_adapter_contract(
        repo_root,
        skill_id="release",
        infer_defaults=infer_repo_defaults,
        validate_adapter_data=validate_adapter_data,
        missing_warnings=(
            "No release adapter found. Using inferred packaging defaults.",
            "Create .agents/release-adapter.yaml to record the canonical packaging manifest, sync command, and user update steps.",
        ),
        artifact_filename=ARTIFACT_FILENAME,
        artifact_class_key=None,
    )
def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="release resolve_adapter", repo_root_help="Repo root used to locate the release adapter")
if __name__ == "__main__":
    main()
