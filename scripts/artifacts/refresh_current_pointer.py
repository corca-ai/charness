#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from collections.abc import Callable
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_resolve_artifact_path = import_repo_module(__file__, "scripts.artifacts.resolve_artifact_path")
load_adapter = _resolve_artifact_path.load_adapter

_artifact_naming = import_repo_module(__file__, "scripts.artifacts.artifact_naming_lib")
ArtifactClassError = _artifact_naming.ArtifactClassError
artifact_class_from_adapter = _artifact_naming.artifact_class_from_adapter
current_artifact_filename = _artifact_naming.current_artifact_filename
record_artifact_supported = _artifact_naming.record_artifact_supported


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--record-artifact-path", type=Path, required=True)
    parser.add_argument("--strategy", choices=("auto", "copy", "symlink"), default="auto")
    parser.add_argument("--execute", action="store_true", help="Apply the pointer refresh. Defaults to dry-run.")
    return parser.parse_args()


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _blocked(payload: dict[str, object], reason: str) -> int:
    payload["status"] = "blocked"
    payload["reason"] = reason
    emit_yaml(payload)
    return 1


def _current_path(repo_root: Path, skill_id: str, adapter: dict[str, object]) -> Path:
    data = adapter.get("data", {})
    if not isinstance(data, dict) or not isinstance(data.get("output_dir"), str):
        raise SystemExit("adapter data must include output_dir")
    artifact_filename = adapter.get("artifact_filename")
    filename = artifact_filename if isinstance(artifact_filename, str) else current_artifact_filename(skill_id)
    return repo_root / Path(data["output_dir"]) / filename


def _resolve_record_path(repo_root: Path, raw_path: Path) -> Path:
    return raw_path.resolve() if raw_path.is_absolute() else (repo_root / raw_path).resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _same_symlink_target(current_path: Path, record_path: Path) -> bool:
    if not current_path.is_symlink():
        return False
    raw_target = Path(os.readlink(current_path))
    target_path = raw_target if raw_target.is_absolute() else current_path.parent / raw_target
    try:
        return target_path.resolve() == record_path.resolve()
    except FileNotFoundError:
        return False


def _finish_pointer_update(
    *,
    current_path: Path,
    payload: dict[str, object],
    execute: bool,
    write: Callable[[], None],
) -> int:
    """Shared tail of both pointer strategies: mark the intended update, apply it
    only under `--execute`, and emit the same payload shape either way.

    The two strategies differ in their guards, their no-op test, and the write
    itself; everything after "we are going to update" is identical, and keeping one
    copy is what makes dry-run and execute provably agree for both.
    """
    payload["would_update"] = True
    if execute:
        current_path.parent.mkdir(parents=True, exist_ok=True)
        write()
        payload["status"] = "updated"
    else:
        payload["status"] = "planned"
    emit_yaml(payload)
    return 0


def _copy_pointer(
    *,
    current_path: Path,
    record_path: Path,
    execute: bool,
    payload: dict[str, object],
) -> int:
    if current_path.is_symlink():
        return _blocked(payload, "copy strategy would follow an existing symlink; use symlink strategy")
    if current_path.exists() and current_path.is_dir():
        return _blocked(payload, "current pointer path is a directory")
    if current_path.exists() and current_path.read_bytes() == record_path.read_bytes():
        payload["status"] = "noop"
        payload["reason"] = "current pointer content already matches the record artifact"
        emit_yaml(payload)
        return 0
    return _finish_pointer_update(
        current_path=current_path,
        payload=payload,
        execute=execute,
        write=lambda: shutil.copyfile(record_path, current_path),
    )


def _symlink_pointer(
    *,
    current_path: Path,
    record_path: Path,
    execute: bool,
    payload: dict[str, object],
) -> int:
    # Hard refusal, not an overridable one. The escape hatch that used to relax this
    # (`--replace-file`) was unreachable: `main` resolves `auto -> symlink` only when
    # the pointer is ALREADY a symlink, so this precondition could never hold on the
    # default path. Keeping the guard preserves the shared writer-surface property
    # that a helper does not clobber a file it did not create; a copy -> symlink
    # migration (never yet performed) would need a deliberate new affordance.
    if current_path.exists() and not current_path.is_symlink():
        return _blocked(payload, "symlink strategy would replace an existing regular file")
    if current_path.exists() and current_path.is_dir():
        return _blocked(payload, "current pointer path is a directory")
    if _same_symlink_target(current_path, record_path):
        payload["status"] = "noop"
        payload["reason"] = "current pointer symlink already targets the record artifact"
        emit_yaml(payload)
        return 0
    relative_target = os.path.relpath(record_path, start=current_path.parent)
    payload["current_pointer_target_path"] = Path(relative_target).as_posix()

    def _write_symlink() -> None:
        if current_path.exists() or current_path.is_symlink():
            current_path.unlink()
        current_path.symlink_to(relative_target)

    return _finish_pointer_update(
        current_path=current_path,
        payload=payload,
        execute=execute,
        write=_write_symlink,
    )


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    # Before `_current_path`: this is the family-agnostic pointer writer, so on a version
    # this reader cannot speak it would place `latest.md` -- the file other sessions read
    # as "the current asset" -- under the shipped default directory. The containment check
    # further down catches the mixed case, but it reports `record artifact path is outside
    # the skill output directory`, which points the operator at the record path when the
    # wrong line is in the adapter; and when the CALLER resolved from the same
    # misversioned adapter, both paths are the default and nothing catches it at all.
    # NO SECOND GUARD HERE, and its absence is the repair rather than a gap. This file used
    # to call `refuse_unspeakable_version` with `resolve_artifact_path.load_adapter` as the
    # loader. Since `#673` that loader REFUSES by raising `SystemExit`, which is a
    # `BaseException` and so is not caught by `unspeakable_version_message`'s `except
    # Exception` -- so the refusal propagates and `refused` could only ever be None. The
    # block was unreachable, its AST call still satisfied the census witness, and deleting
    # it left all 39 assertions in `test_adapter_version_refusal_is_loud.py` green: a guard
    # nothing could prove load-bearing. It also ran the resolver subprocess twice per call.
    #
    # The surface still refuses -- `load_adapter` below does it, with one owner for the
    # wording -- and that IS pinned, by this surface's own case in that test file.
    adapter = load_adapter(repo_root, args.skill_id)
    try:
        artifact_class = artifact_class_from_adapter(adapter)
    except ArtifactClassError as exc:
        raise SystemExit(str(exc)) from exc
    current_path = _current_path(repo_root, args.skill_id, adapter)
    record_path = _resolve_record_path(repo_root, args.record_artifact_path)
    strategy = "symlink" if args.strategy == "auto" and current_path.is_symlink() else args.strategy
    if strategy == "auto":
        strategy = "copy"

    payload: dict[str, object] = {
        "skill_id": args.skill_id,
        "artifact_class": artifact_class,
        "strategy": strategy,
        "execute": args.execute,
        "would_update": False,
        "current_artifact_path": _portable_path(repo_root, current_path),
        "record_artifact_path": _portable_path(repo_root, record_path),
        "current_pointer_is_symlink": current_path.is_symlink(),
        "current_pointer_target_path": None,
    }

    if not record_artifact_supported(artifact_class):
        return _blocked(payload, f"artifact_class `{artifact_class}` does not support dated records")
    nominal_current_parent = current_path.parent.resolve()
    if not _is_relative_to(nominal_current_parent, repo_root):
        return _blocked(payload, "current pointer path is outside repo_root")
    if not _is_relative_to(record_path, repo_root):
        return _blocked(payload, "record artifact path is outside repo_root")
    if not _is_relative_to(record_path, nominal_current_parent):
        return _blocked(payload, "record artifact path is outside the skill output directory")
    if not record_path.is_file():
        return _blocked(payload, "record artifact path does not exist or is not a file")
    # An EMPTY record is not a record. This helper's whole job is to replace the
    # pointer other sessions read as "the current asset", so pointing it at a 0-byte
    # (or whitespace-only) file destroys a real asset and reports
    # `status: updated` — the same wrong output as sweep row S19, one command
    # over. `is_file()` alone was the only content check, and a 0-byte file passes it.
    try:
        record_text = record_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return _blocked(payload, f"record artifact path could not be read: {exc}")
    if not record_text.strip():
        return _blocked(
            payload,
            f"record artifact is empty ({record_path.stat().st_size} byte(s), no non-whitespace "
            "content); repointing the current pointer at it would replace a real asset with "
            "nothing while reporting success",
        )
    nominal_current_path = nominal_current_parent / current_path.name
    if record_path == nominal_current_path:
        return _blocked(payload, "record artifact path is already the current pointer path")

    if strategy == "copy":
        return _copy_pointer(
            current_path=current_path,
            record_path=record_path,
            execute=args.execute,
            payload=payload,
        )
    return _symlink_pointer(
        current_path=current_path,
        record_path=record_path,
        execute=args.execute,
        payload=payload,
    )


if __name__ == "__main__":
    raise SystemExit(main())
