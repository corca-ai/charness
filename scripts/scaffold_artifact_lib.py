from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path


def validator_command(
    *,
    repo_root: Path,
    script_file: str | Path,
    script_names: Sequence[str],
    artifact_path: str | None = None,
) -> str:
    if not script_names:
        raise ValueError("script_names must not be empty")

    # Repo-local validators win so a consumer repo cites the same strict check
    # as its broad gate; installed-plugin validators are fallback-only.
    suffix = f" --paths {artifact_path}" if artifact_path else ""
    for script_name in script_names:
        repo_local = repo_root / "scripts" / script_name
        if repo_local.is_file():
            return f"python3 scripts/{script_name} --repo-root .{suffix}"
    for ancestor in Path(script_file).resolve().parents:
        for script_name in script_names:
            candidate = ancestor / "scripts" / script_name
            if candidate.is_file():
                return f"python3 {candidate} --repo-root .{suffix}"
    raise FileNotFoundError(f"{script_names[0]} not found in installed Charness layout")


def current_pointer_payload(
    *,
    repo_root: Path,
    output_dir: Path,
    date_text: str,
    title: str,
    template: str,
    validator_command: str,
    size_budget: dict[str, object] | None = None,
) -> dict[str, object]:
    artifact_path = output_dir / "latest.md"
    write_path, write_role, symlink_target = current_pointer_write_path(repo_root, artifact_path)
    payload: dict[str, object] = {
        "artifact_path": str(artifact_path),
        "artifact_role": "current_pointer",
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        **write_target_facts(repo_root, write_path),
        "current_pointer_symlink_target": symlink_target,
        "date": date_text,
        "title": title,
        "template": template,
        "validator_command": validator_command,
    }
    # Surface the artifact's line budget as part of the canonical scaffold
    # contract so a run writes-to-fit up front instead of writing long and then
    # burning a trim-to-fit edit/wc-l loop against a ceiling it could not see
    # until the validator rejected it. Optional: skills without a line ceiling
    # omit it entirely (no field), so existing scaffold consumers are unchanged.
    if size_budget is not None:
        payload["size_budget"] = size_budget
    return payload


def portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


CURRENT_POINTER_STATE_KEYS = (
    "current_pointer_is_symlink",
    "current_pointer_target_path",
    "current_pointer_target_exists",
)


def current_pointer_state(repo_root: Path, artifact_path: Path) -> dict[str, object]:
    """SINGLE OWNER of what a `latest.md` current pointer resolves to.

    #548: this rule was implemented twice -- here, and again inside
    `scripts/resolve_artifact_path.py` -- and both copies produced the same
    `write_artifact_path` / `write_artifact_role` pair from separate code. Nothing forced
    them to agree, so the same key name came to mean different things depending on which
    producer a skill happened to call, and `#538` is the recorded instance of an agent
    nearly writing over a finished review because of it. `resolve_artifact_path` now calls
    this; keep it dependency-free, because skill scaffolds load this module by file path
    with no package context.
    """
    absolute_artifact_path = repo_root / artifact_path
    if not absolute_artifact_path.is_symlink():
        return {
            "current_pointer_is_symlink": False,
            "current_pointer_target_path": None,
            "current_pointer_target_exists": None,
            "current_pointer_symlink_target": None,
        }
    raw_target = os.readlink(absolute_artifact_path)
    target_path = Path(raw_target)
    if not target_path.is_absolute():
        target_path = absolute_artifact_path.parent / target_path
    return {
        "current_pointer_is_symlink": True,
        "current_pointer_target_path": portable_path(repo_root, target_path),
        "current_pointer_target_exists": target_path.exists(),
        "current_pointer_symlink_target": raw_target,
    }


def published_pointer_state(repo_root: Path, artifact_path: Path) -> dict[str, object]:
    """The three pointer keys artifact payloads publish, from the single owner.

    Exists so each payload producer is a one-line delegation rather than its own copy of
    "call the owner, then filter". The duplicate-ratchet gate caught that second-order
    duplication immediately after the first consolidation removed the first-order kind --
    consolidating a rule can create a new shared shape that then drifts, which is the trade
    this repo's boundary rule names.
    """
    state = current_pointer_state(repo_root, artifact_path)
    return {key: state[key] for key in CURRENT_POINTER_STATE_KEYS}


def write_target_facts(repo_root: Path, write_path: str) -> dict[str, object]:
    """What writing to `write_path` actually DOES to what is already there.

    #548: every scaffold payload said WHERE to write and none said whether anything was
    already there. `write_artifact_role: current_pointer_target` is true and reads as
    neutral, while the path it names may be a completed dated review whose content a write
    destroys -- and because the filename is dated, nothing afterwards looks wrong. These
    two keys state the consequence instead of leaving it to be inferred from the role.

    Deliberately a FACT, not a policy: whether overwriting is acceptable differs by skill
    (`debug` continues an open investigation in place; `quality` must never overwrite a
    finished review), so each skill's own contract decides what to do with it.
    """
    exists = (repo_root / write_path).exists()
    return {
        "write_artifact_target_exists": exists,
        "write_artifact_effect": "overwrite_existing_content" if exists else "create_new_file",
    }


def dated_record_payload(
    repo_root: Path,
    *,
    write_artifact_path: str,
    date_text: str,
    title: str,
    template: str,
    validator_command: str,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    """One shape for a records-only scaffold whose write target is a dated file.

    `critique`, `retro`, and `ideation` each built this dict themselves. They were already
    near-identical; adding the write-target facts to all three made them identical enough for
    the duplicate ratchet to call it a new family, which was the correct verdict -- the fix is
    one owner for the shape, not three copies that happen to agree.
    """
    payload: dict[str, object] = {
        "artifact_path": write_artifact_path,
        "artifact_role": "record",
        "write_artifact_path": write_artifact_path,
        "date": date_text,
        "title": title,
        "template": template,
        "validator_command": validator_command,
    }
    payload.update(extra or {})
    return with_write_target_facts(repo_root, payload)


def with_write_target_facts(repo_root: Path, payload: dict[str, object]) -> dict[str, object]:
    """Stamp the write-target facts from the payload's FINAL `write_artifact_path`.

    Producers that build a payload and then REPLACE its write target must call this last.
    `scaffold_debug_artifact.py` does exactly that: it takes the current-pointer payload and
    swaps in a fresh-record target through a fixed key list. The first version of these facts
    was computed before that swap and was not in the list, so the payload reported
    `overwrite_existing_content` for a path guaranteed not to exist -- while `debug/SKILL.md`
    told the agent to trust the key. Recomputing from the final value is what makes a later
    key addition unable to go stale the same way; a longer copy list would not.

    Idempotent, so it is safe to call even where nothing was replaced.
    """
    payload.update(write_target_facts(repo_root, str(payload["write_artifact_path"])))
    return payload


def current_pointer_write_path(repo_root: Path, artifact_path: Path) -> tuple[str, str, str | None]:
    state = current_pointer_state(repo_root, artifact_path)
    if not state["current_pointer_is_symlink"]:
        return str(artifact_path), "current_pointer", None
    return (
        str(state["current_pointer_target_path"]),
        "current_pointer_target",
        str(state["current_pointer_symlink_target"]),
    )


def emit_payload_main(
    payload_for: Callable[..., dict[str, object]],
    *,
    artifact_label: str,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help=f"Repo root to scaffold the {artifact_label} artifact into")
    parser.add_argument("--title", help=f"Title for the scaffolded {artifact_label} artifact")
    args = parser.parse_args()

    # Always emit the full structured payload — the run reads the template from
    # `payload["template"]` and the write target, validator command, and
    # size_budget as sibling fields. There is no bare rendered-template mode: a
    # single output shape removes the "forgot --json → the budget/write-path never
    # reached the run" footgun that a flag-gated structured mode invites.
    payload = payload_for(args.repo_root.resolve(), title=args.title)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return 0
