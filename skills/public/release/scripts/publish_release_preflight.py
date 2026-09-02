from __future__ import annotations

import importlib.util
import json
import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

try:
    from scripts.core import subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir.parent))
    import scripts.core.subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process

subprocess = _subprocess_guard.subprocess

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"
SEMVER_PIN_RE = re.compile(
    r"(?<![\w.])v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?![\w]|\.\d)"
)
_INVALID_IDENTITY_SUFFIX = ".invalid"
_IDENTITY_EMAIL_RE = re.compile(r"<([^<>]*)>")
_IDENTITY_VARS: tuple[tuple[str, str], ...] = (
    ("author", "GIT_AUTHOR_IDENT"),
    ("committer", "GIT_COMMITTER_IDENT"),
)


def _load_adapter_preflight_helper() -> Any:
    helper_path = Path(__file__).resolve().with_name("publish_release_adapter_preflight.py")
    spec = importlib.util.spec_from_file_location("publish_release_adapter_preflight", helper_path)
    if spec is None or spec.loader is None:
        raise ImportError("publish_release_adapter_preflight.py not found")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_adapter_preflight = _load_adapter_preflight_helper()
# Operator-supplied argument guards live beside the command surface they guard.
# Re-exported so `publish_release_cli` keeps one import site.
_arg_guards = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_arg_guards.py"))
)
validate_critique_artifact_arg = _arg_guards["validate_critique_artifact_arg"]
validate_bump_rationale_arg = _arg_guards["validate_bump_rationale_arg"]
# One owner for the record-sentinel rule. This path is rendered into the release record as
# `## Review Proof` on every write, including the published one.
_claims_review = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_claims_review.py"))
)


def _version_pins(text: str) -> list[str]:
    pins: list[str] = []
    seen: set[str] = set()
    for match in SEMVER_PIN_RE.finditer(text):
        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch"))
        if 1900 <= major <= 2199 and 1 <= minor <= 12 and 1 <= patch <= 31:
            continue
        version = f"{major}.{minor}.{patch}"
        if version not in seen:
            seen.add(version)
            pins.append(version)
    return pins


def _load_shared_closeout_helper() -> Any:
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:  # pragma: no cover - defensive broken-install layout
        raise ImportError("skill_runtime_bootstrap.py not found")
    runtime = SimpleNamespace(**runpy.run_path(str(bootstrap)))
    return runtime.load_repo_module_from_skill_script(
        __file__,
        "scripts.gates.check_prescribed_skill_executed_lib",
    )


def _resolve_git_ident(repo_root: Path, var_name: str) -> str | None:
    proc = run_process(
        ["git", "-C", str(repo_root), "var", var_name],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout.strip()


def invalid_git_identity_blocker(repo_root: Path) -> str | None:
    """Refuse a lingering `.invalid` placeholder git author/committer identity
    before release mutation starts.

    Duplicates (does not import) a small resolve+check helper that also lives at
    the repo root for the commit-boundary gate -- this skill ships standalone in
    the plugin and must not import outside its own package. This check is
    unconditional: it always runs, not only when a release-adapter field
    changed in the delta.
    """
    for kind, var_name in _IDENTITY_VARS:
        ident = _resolve_git_ident(repo_root, var_name)
        if ident is None:
            continue
        match = _IDENTITY_EMAIL_RE.search(ident)
        email = match.group(1) if match else None
        if email is None or not email.strip().lower().endswith(_INVALID_IDENTITY_SUFFIX):
            continue
        # floor-addition-restraint: keep -- recorded recurrence: a lingering
        # synthetic proof identity misattributed dozens of real pushed commits
        # before anyone noticed; environment check, adds no authoring-shape weight
        return (
            f"release publish gate: effective git {kind} identity resolves to a "
            f"`.invalid` placeholder domain: {ident}; publishing now would "
            "durably misattribute published history to a synthetic identity. "
            "Unset the lingering identity (`git config --unset user.email` / "
            "`user.name`, or the GIT_AUTHOR_*/GIT_COMMITTER_* env override) or "
            "scope a synthetic identity per command instead of durably mutating "
            "config."
        )
    return None


def update_instructions_version_blocker(
    update_instructions: Any, *, target_version: str, previous_version: str | None
) -> str | None:
    """Return a blocker when adapter `update_instructions` carry release-pinned
    narrative instead of an evergreen refresh path.

    The adapter-focused preflight only triggers when the adapter FILE changed in the
    release delta, so a release that should repair `update_instructions` but does not
    touch the file is never flagged. This check is unconditional. It uses plain
    a release-version pin detector that ignores common dotted dates while still
    catching older non-previous release notes left in the adapter field.
    """
    if isinstance(update_instructions, (list, tuple)):
        text = "\n".join(str(item) for item in update_instructions)
    else:
        text = str(update_instructions or "")
    pins = _version_pins(text)
    if not pins:
        return None
    pins_text = ", ".join(f"`{pin}`" for pin in pins)
    return (
        "release adapter update_instructions contain version-pinned release narrative "
        f"({pins_text}); keep adapter update_instructions "
        "version-agnostic and put release-specific behavior, migration, and rollback notes "
        "in the release notes or release artifact"
    )


def build_update_instructions_prep_payload(
    *,
    package_id: str,
    current_version: str,
    target_version: str,
    previous_version: str | None,
    update_instructions: Any,
) -> dict[str, Any]:
    """Pre-publish affordance: surface evergreen `update_instructions` guidance
    BEFORE the release critique so the maintainer can refresh the adapter early and
    the staleness guard (`update_instructions_version_blocker`) does not HOLD the
    publish at the critique gate.

    Reports staleness as *data* and never raises — the whole point is to run before
    the clean-worktree / critique gate so the maintainer acts on it first. The
    suggested adapter text deliberately avoids the target version; per-release
    narrative belongs in release notes, not in the adapter contract.
    """
    if isinstance(update_instructions, (list, tuple)):
        current_list = [str(item) for item in update_instructions]
    elif update_instructions:
        current_list = [str(update_instructions)]
    else:
        current_list = []
    blocker = update_instructions_version_blocker(
        update_instructions, target_version=target_version, previous_version=previous_version
    )
    suggestion = [
        f"Run the repo-owned update command for {package_id} to install the latest published release.",
        "Read the release notes for release-specific behavior changes, migrations, or rollback notes.",
    ]
    return {
        "mode": "prep-update-instructions",
        "package_id": package_id,
        "current_version": current_version,
        "target_version": target_version,
        "previous_version": previous_version,
        "current_update_instructions": current_list,
        "update_instructions_stale": blocker is not None,
        "staleness_blocker": blocker,
        "suggested_update_instructions": suggestion,
        "stub_update_instructions_entry": suggestion[0],
        "next_step": (
            "Refresh the release adapter `update_instructions` to a version-agnostic "
            "operator refresh path, and put release-specific behavior, migration, or "
            "rollback notes in the release notes/artifact. Then run the release critique "
            "and publish; doing this now pre-empts the update_instructions HOLD at the "
            "critique gate."
        ),
    }


def release_binding_tokens(version: str | None) -> list[str]:
    """Context-identity tokens for a release closeout, from its target version.

    Both spellings, because this repo names release artifacts either way: the
    dotted `2.12.0` is what the manifest and the release notes carry, and the
    hyphenated `2-12-0` is what the checked-in critique BASENAMES use
    (`v2-1-6-release-candidate-packet.md`). Binding on only one form would
    refuse artifacts the repo already writes, which is how a correctness gate
    earns a bypass.
    """
    if not version:
        return []
    stripped = version.strip().lstrip("vV")
    if not stripped:
        return []
    return sorted({stripped, stripped.replace(".", "-")})


def enforce_release_critique_gate(
    repo_root: Path,
    *,
    critique_artifact: str | None,
    critique_blocked: str | None,
    target_version: str | None = None,
) -> dict[str, Any]:
    """Refuse the publish unless the standalone critique either ran (artifact
    exists) or was honestly skipped with a blocked host signal.

    Closes the release-closeout self-substitution gap. The release skill's prose already required a
    critique; this gate makes the requirement non-optional at the publish
    boundary. Returns the shared helper's report so callers can include it
    in their structured payload.
    """
    helper = _load_shared_closeout_helper()
    if critique_artifact and critique_blocked:
        raise SystemExit(
            "release publish gate: pass exactly one of "
            "`--critique-artifact <path>` or `--critique-blocked <host-signal>`"
        )
    if critique_artifact:
        # Bound, not merely present. The closeout contract carried "`release`
        # (version binding) remains a follow-up and still calls the same
        # presence-only `check()` today" -- so until now any tracked critique
        # under the artifact prefix satisfied the publish gate, including one
        # written for an unrelated release.
        result = helper.check(
            repo_root=repo_root,
            required=["standalone_critique"],
            evidence={"standalone_critique": critique_artifact},
            skips={},
            kind="release",
            tokens=release_binding_tokens(target_version),
        )
    elif critique_blocked:
        signal = critique_blocked.strip()
        result = helper.check(
            repo_root=repo_root,
            required=["standalone_critique"],
            evidence={},
            skips={"standalone_critique": f"host-blocked-subagent: {signal}"},
            kind="release",
        )
    else:
        result = helper.check(
            repo_root=repo_root,
            required=["standalone_critique"],
            evidence={},
            skips={},
            kind="release",
        )
    if not result["ok"]:
        raise SystemExit(
            "release publish gate refused: standalone critique not satisfied\n"
            + json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        )
    if critique_artifact and not result.get("binding_checked"):
        # LOUD, because this is the publish boundary and the run just silently
        # degraded to presence-only: any tracked critique would have satisfied
        # it. The report alone is not enough -- its only caller discarded the
        # return value, so "the weaker run is visible" was not true of anything
        # an operator could see.
        sys.stderr.write(
            "WARNING (release publish gate): the target version could not be resolved, so "
            "the standalone critique was accepted on PRESENCE alone -- it was not checked "
            "against the release being published.\n"
        )
    return result


def release_adapter_preflight_payload(
    repo_root: Path,
    *,
    release_content_paths: list[str],
    previous_version: str | None,
) -> dict[str, Any]:
    return _adapter_preflight.release_adapter_preflight_payload(
        repo_root,
        release_content_paths=release_content_paths,
        previous_version=previous_version,
    )


def run_release_adapter_preflight(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    run_command: Callable,
) -> None:
    _adapter_preflight.run_release_adapter_preflight(
        repo_root,
        payload,
        run_command=run_command,
    )


def release_surface_blocker(release_payload: dict, expected_version: str) -> str | None:
    """Why publishing this release surface must not proceed, or ``None``.

    Lives with the other pre-publish blockers rather than in the CLI, and returns a
    message instead of raising so the reason is testable without a SystemExit.
    """
    if release_payload["drift"]:
        return f"release surface drift detected: {release_payload['drift']}"
    # D48: an absent surface the declaration does not name is a pass nothing corroborates.
    # `current_release` keeps it out of `drift` on purpose -- a read-only status call must
    # not redden a lane a consumer never published -- so the refusal lives here, at the
    # irreversible boundary, where a wrong answer actually escapes. Deleting the four
    # declaration lines used to buy a silent green publish over a surface a failed sync
    # had removed ("deleting those four adapter lines disarms it with nothing
    # corroborating them").
    if release_payload.get("absence_corroboration") == "uncorroborated":
        return (
            "release surface absence is uncorroborated: "
            f"{release_payload['undeclared_absent_surfaces']} absent and named by neither "
            "`required_release_surfaces` nor `unpublished_release_surfaces`. Restore the "
            "surface(s), or -- if this repo does not ship them -- name them in "
            "`unpublished_release_surfaces`. Naming them as REQUIRED is not the remedy: "
            "that field means they must exist, so it turns this into drift."
        )
    if release_payload["surface_versions"]["packaging_manifest"] != expected_version:
        return f"expected packaging manifest version `{expected_version}`"
    return None
