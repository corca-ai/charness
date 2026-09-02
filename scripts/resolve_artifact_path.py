#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import shlex
import sys
from datetime import date
from pathlib import Path

import yaml

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_verdict = import_repo_module(__file__, "scripts.adapters.adapter_version_verdict")

_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
_scaffold_artifact_lib = import_repo_module(__file__, "scripts.core.scaffold_artifact_lib")
ArtifactClassError = _scripts_artifact_naming_lib_module.ArtifactClassError
artifact_class_from_adapter = _scripts_artifact_naming_lib_module.artifact_class_from_adapter
current_artifact_filename = _scripts_artifact_naming_lib_module.current_artifact_filename
dated_artifact_filename = _scripts_artifact_naming_lib_module.dated_artifact_filename
record_artifact_supported = _scripts_artifact_naming_lib_module.record_artifact_supported
slugify = _scripts_artifact_naming_lib_module.slugify


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--date")
    parser.add_argument(
        "--intent",
        choices=("record", "current"),
        help=(
            "`record` returns the dated durable artifact as the edit target when supported; "
            "`current` returns the current pointer or its symlink target as the edit target."
        ),
        default="current",
    )
    return parser.parse_args()


def load_adapter(repo_root: Path, skill_id: str) -> dict[str, object]:
    resolver = next(
        (
            candidate
            for candidate in (
                repo_root / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py",
                repo_root / "skills" / skill_id / "scripts" / "resolve_adapter.py",
                REPO_ROOT / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py",
                REPO_ROOT / "skills" / skill_id / "scripts" / "resolve_adapter.py",
            )
            if candidate.is_file()
        ),
        None,
    )
    if resolver is None:
        raise SystemExit(
            "No skill adapter resolver found in the consumer repo or installed Charness plugin "
            f"for skill `{skill_id}`"
        )
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        module = load_path_module("charness_artifact_resolve_adapter", resolver)
        loader = getattr(module, "load_adapter", None)
        if callable(loader):
            try:
                adapter = loader(repo_root)
            except Exception as exc:
                raise SystemExit(str(exc) or f"{resolver} failed") from exc
        else:
            main = getattr(module, "main", None)
            previous_argv = sys.argv
            try:
                sys.argv = [str(resolver), "--repo-root", str(repo_root)]
                if callable(main):
                    try:
                        returncode = int(main() or 0)
                    except SystemExit as exc:
                        returncode = int(exc.code or 0)
                else:
                    returncode = 0
            finally:
                sys.argv = previous_argv
            if returncode != 0:
                raise SystemExit(stderr.getvalue().strip() or f"{resolver} failed")
            adapter = yaml.safe_load(stdout.getvalue())
    _refuse_unhonored_adapter(adapter, skill_id)
    return adapter


def _refuse_unhonored_adapter(adapter: object, skill_id: str) -> None:
    """Refuse a resolved payload whose reader honored NOTHING the repo declared.

    THE SUBPROCESS RETURN CODE WAS THIS FILE'S ONLY PROTECTION, and `#673` removed it. Five
    resolvers used to let a parser refusal out as a traceback, so a non-zero exit stopped
    this helper; now they render a verdict at exit 0 like the other eleven, and fourteen of
    sixteen exit 0 on a refused document. Measured against
    `version: !!int 9` beside a declared `output_dir: docs/mine-q`: before, a traceback and
    a stop; after, `write_artifact_path: charness-artifacts/quality/latest.md` -- the
    charness default, over a repo that declared something else, at exit 0. A bounded review
    caught it, which is the second time this exact collateral has been found by review
    rather than declared by the batch that caused it (the census records the first, for
    `announcement`).

    Keyed on the CONDITION rather than on the exit code, so a resolver's exit convention
    can change again without silently disarming this. `declarations_dropped` is the third
    door and is checked here too: it is now reachable for all sixteen, and a dropped
    `output_dir` line lands on exactly the same default.

    ONE DOOR IT DOES NOT COVER, named because the sentence above is about the exit-code door
    only: `payload_for(adapter=...)` skips `load_adapter` and therefore skips this. The one
    production caller that passes it (`scaffold_debug_artifact`) is guarded upstream on all
    three doors, so there is no live escape -- but a new caller inherits nothing here, and no
    test pins that parameter's contract.
    """
    if not isinstance(adapter, dict):
        raise SystemExit(f"the `{skill_id}` adapter resolver rendered no payload to read")
    errors = adapter.get("errors")
    if not (_verdict.declarations_unhonored(errors) or _verdict.declarations_dropped(adapter)):
        return
    adapter_name = f"{skill_id}-adapter.yaml"
    if _verdict.declarations_unhonored(errors):
        # `unhonored_cause` / `unhonored_remedy` exist so a caller can phrase its own
        # refusal WITHOUT hand-rolling the version-versus-parse branch. Hand-rolling it is
        # how four surfaces came to tell an operator to "set `version: 1`" for a document
        # the parser never read; the first cut of this guard invented a third wording and a
        # sibling test caught it for the same reason.
        detail = "; ".join(str(item) for item in errors if isinstance(item, str))
        lead = f"`.agents/{adapter_name}` {_verdict.unhonored_cause(errors)} ({detail})."
        fix = _verdict.unhonored_remedy(errors, adapter_name)
        tail = (
            "Nothing it declares is being honored, so resolving an artifact path here would "
            "return a charness default wearing this repo's name -- refusing instead."
        )
    else:
        # A DIFFERENT SENTENCE, because the dropped-line arm is a different fact and the
        # shared tail was FALSE for it. A dropped line leaves the rest of the document
        # honored: with a stray indent on an unrelated key, `output_dir` is still read and
        # resolution would NOT have returned a charness default. Round 2 caught the first cut
        # gluing the unhonored tail onto this arm -- the same overclaim
        # `unspeakable_version_message` words carefully ("what THEY declared is serving an
        # inferred default"), reproduced by the repair that cited it.
        dropped = "; ".join(
            str(warning)
            for warning in adapter.get("warnings", [])
            if _verdict.UNINTERPRETED_WARNING_MARKER in str(warning)
        )
        lead = f"`.agents/{adapter_name}` has lines this reader could not interpret ({dropped})."
        tail = (
            "Whatever those lines meant to declare is serving an inferred default instead, so "
            "an artifact path resolved here may not be the one this repo declared -- refusing "
            "rather than guessing which."
        )
        fix = "Fix the indentation or the syntax on those lines, then re-run."
    raise SystemExit(f"{lead} {tail} {fix}")


def _refresh_current_pointer_argv(skill_id: str, record_path: Path) -> list[str]:
    helper = Path(__file__).resolve().parent / "refresh_current_pointer.py"
    return [
        "python3",
        str(helper),
        "--repo-root",
        ".",
        "--skill-id",
        skill_id,
        "--record-artifact-path",
        str(record_path),
        "--execute",
    ]


def payload_for(
    repo_root: Path,
    skill_id: str,
    slug_text: str,
    *,
    intent: str = "current",
    artifact_date: date | None = None,
    adapter: dict[str, object] | None = None,
) -> dict[str, object]:
    repo_root = repo_root.resolve()
    adapter = adapter or load_adapter(repo_root, skill_id)
    data = adapter.get("data", {})
    if not isinstance(data, dict) or not isinstance(data.get("output_dir"), str):
        raise SystemExit("adapter data must include output_dir")
    artifact_date = artifact_date or date.today()
    slug = slugify(slug_text)
    record_name = dated_artifact_filename(slug, artifact_date=artifact_date)
    output_dir = Path(data["output_dir"])
    artifact_filename = adapter.get("artifact_filename")
    current_filename = (
        artifact_filename
        if isinstance(artifact_filename, str)
        else current_artifact_filename(skill_id)
    )
    current_path = output_dir / current_filename
    try:
        artifact_class = artifact_class_from_adapter(adapter)
    except ArtifactClassError as exc:
        raise SystemExit(str(exc)) from exc
    records_supported = record_artifact_supported(artifact_class)
    record_path = output_dir / record_name if records_supported else None
    absolute_current_path = repo_root / current_path
    pointer_state = _scaffold_artifact_lib.published_pointer_state(repo_root, absolute_current_path)
    if intent == "record" and record_path is not None:
        write_path = str(record_path)
        write_role = "durable_record"
        update_current_pointer_after_write = True
        refresh_argv = _refresh_current_pointer_argv(skill_id, record_path)
        refresh_command = shlex.join(refresh_argv)
    else:
        write_path, write_role, _ = _scaffold_artifact_lib.current_pointer_write_path(
            repo_root, current_path
        )
        update_current_pointer_after_write = False
        refresh_argv = None
        refresh_command = None
    payload = {
        "skill_id": skill_id,
        "artifact_class": artifact_class,
        "slug": slug,
        "date": artifact_date.isoformat(),
        "intent": intent,
        "artifact_path": str(current_path),
        "record_artifact_path": str(record_path) if record_path is not None else None,
        "record_artifact_supported": records_supported,
        "current_artifact_path": str(current_path),
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        **_scaffold_artifact_lib.write_target_facts(repo_root, write_path),
        "update_current_pointer_after_write": update_current_pointer_after_write,
        "refresh_current_pointer_argv": refresh_argv,
        "refresh_current_pointer_command": refresh_command,
        "frontmatter": {
            "artifact_kind": "record",
            "status": "current",
            "created": artifact_date.isoformat(),
            "slug": slug,
        },
    }
    payload.update(pointer_state)
    return payload


def main() -> int:
    args = parse_args()
    artifact_date = date.fromisoformat(args.date) if args.date else None
    payload = payload_for(
        args.repo_root,
        args.skill_id,
        args.slug,
        intent=args.intent,
        artifact_date=artifact_date,
    )
    emit_yaml(dict(sorted(payload.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
