from __future__ import annotations

import contextlib
import datetime as dt
import importlib.util
import io
import re
import sys
from pathlib import Path
from typing import Any

from scripts.artifact_naming_lib import dated_artifact_filename
from scripts.goal_lineage import (
    LineageError,
    load_goal_lineage_file,
    not_goal_bound_lineage,
    planning_only_lineage,
)
from scripts.core.helper_provenance_lib import require_repo_local_helper
from scripts.lesson_command_citation import (
    INDEX_SCRIPT_RELATIVE,
    index_build_command,
    repo_carries_index_builder,
    script_tree_root,
)
from scripts.recent_lessons_lib import build_indexed_recent_lessons, lesson_selection_index_path
from scripts.runtime_bootstrap import load_path_module

_PERSISTED_LINE_PATTERN = re.compile(r"^Persisted:.*$", re.MULTILINE)
_GOAL_FIELD_PATTERN = re.compile(r"^Goal:[ \t]*(?P<value>[^\r\n]*)$")
_GOAL_PATH_PATTERN = re.compile(
    r"^charness-artifacts/goals/\d{4}-\d{2}-\d{2}-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
_FENCE_PATTERN = re.compile(r"^[ \t]*(?P<marker>`{3,}|~{3,})(?P<info>.*)$")
_ATX_HEADING_PATTERN = re.compile(r"^[ ]{0,3}#{1,6}[ \t]+")
_H1_PATTERN = re.compile(r"^[ ]{0,3}#[ \t]+")
_SETEXT_H2_PATTERN = re.compile(r"^[ \t]*---+[ \t]*$")


def _load_registered_path_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load module {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module


def stamp_persisted_path(markdown_text: str, relpath: str) -> str:
    """Fill the `## Persisted` line with the durable relpath the persist step just
    computed, so a run does not hand-edit the placeholder after persisting — the
    helper already knows where the file landed (the retro analog of the debug
    size_budget fix: stamp what the tool computes instead of making the agent
    re-derive it). Replaces only the first `Persisted:` line; no-op if the body
    has none, so a hand-authored `Persisted: no: <reason>` without a persist call
    is untouched."""
    replacement = f"Persisted: yes: {relpath}"
    stamped, count = _PERSISTED_LINE_PATTERN.subn(replacement, markdown_text, count=1)
    return stamped if count else markdown_text


_STUB_SUMMARY_MARKERS: tuple[str, ...] = (
    "No current focus bullets found in retro lesson index.",
    "No repeat traps extracted from retro lesson index.",
    "No next improvements extracted from retro lesson index.",
)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def normalize_artifact_name(artifact_name: str) -> tuple[str, bool]:
    """Append `.md` when missing so glob('*.md') downstream readers find the file."""
    if artifact_name.endswith(".md"):
        return artifact_name, False
    return artifact_name + ".md", True


# ANCHORED. `dated_artifact_filename` emits `YYYY-MM-DD-<slug>.md`, so a name that
# already OPENS with that prefix is a dated record whatever else it contains. An
# unanchored search asked a different question -- "does this name contain a date"
# -- and answered yes for the subject key `session-2026-08-29`.
_DATED_RECORD_PREFIX = re.compile(r"\d{4}-\d{2}-\d{2}-")


def resolve_retro_artifact_path(
    output_dir: Path,
    artifact_name: str,
    *,
    artifact_date: dt.date | None = None,
    subject_key: bool = False,
) -> tuple[Path, bool]:
    """Resolve a retro subject key to its one canonical artifact path.

    A dated filename is an explicitly named artifact and remains unchanged for
    compatibility with existing callers. An undated name is a subject key, so it
    uses the dated-record rule. Scaffold callers set ``subject_key`` explicitly so
    a subject containing a date token still follows that rule. Returning whether
    the path was derived lets persistence refuse a collision the caller did not
    name.
    """
    # The role signal is whether the CALLER wrote a filename or a subject, and
    # `normalize_artifact_name` already computes it: it returns True exactly when it
    # had to append `.md`, i.e. when the caller did NOT name a file.
    #
    # This used to key on "the name contains a date", which is not the same question.
    # The subject key `session-2026-08-29` was read as an explicitly named artifact
    # (`session-2026-08-29.md`) while the scaffold resolved the same subject to
    # `2026-08-29-session-2026-08-29.md` -- two paths for one subject key, which is
    # the incident this module exists to close. Worse, the explicit reading also
    # returns derived=False, which disables the collision guard below, so the
    # overwrite came back for exactly the subjects that carry a date.
    normalized_name, was_bare_subject = normalize_artifact_name(artifact_name)
    already_dated = _DATED_RECORD_PREFIX.match(normalized_name) is not None
    if not subject_key and (not was_bare_subject or already_dated):
        return output_dir / normalized_name, False
    return (
        output_dir
        / dated_artifact_filename(Path(normalized_name).stem, artifact_date=artifact_date),
        True,
    )


def _run_index_builder(repo_root: Path, output_dir: Path) -> Path:
    """Ask the target repository's builder to write its own index bytes."""
    command = index_build_command(repo_root, "--write")
    if repo_carries_index_builder(repo_root):
        builder_path = repo_root / INDEX_SCRIPT_RELATIVE
    else:
        builder_path = script_tree_root() / INDEX_SCRIPT_RELATIVE
    if not builder_path.is_file():
        raise FileNotFoundError(
            "retro lesson selection builder is unavailable in the running tree; "
            f"cannot refresh the index with `{command}`"
        )
    module = load_path_module("charness_retro_lesson_selection_builder", builder_path)
    target_recent = builder_path.parent / "recent_lessons_lib.py"
    if builder_path.is_relative_to(repo_root) and target_recent.is_file():
        recent_module = _load_registered_path_module(
            "charness_target_recent_lessons_lib", target_recent
        )
        for name in (
            "build_lesson_selection_index",
            "check_lesson_selection_index",
            "lesson_selection_index_path",
            "write_lesson_selection_index",
        ):
            setattr(module, name, getattr(recent_module, name))
    stdout = io.StringIO()
    stderr = io.StringIO()
    previous_argv = sys.argv
    try:
        sys.argv = [str(builder_path), "--repo-root", str(repo_root), "--write"]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                returncode = int(module.main())
            except SystemExit as exc:
                returncode = int(exc.code or 0)
    finally:
        sys.argv = previous_argv
    if returncode != 0:
        detail = (stderr.getvalue() or stdout.getvalue()).strip()
        raise ValueError(
            f"retro lesson selection builder failed with exit {returncode}"
            + (f": {detail}" if detail else "")
        )
    return lesson_selection_index_path(output_dir)


def is_stub_summary(text: str) -> bool:
    """Return True only when the text matches the empty-stub digest signature.

    Used to distinguish a hand-curated `recent-lessons.md` from one that the
    digest builder itself wrote when no candidates were available.
    """
    return all(marker in text for marker in _STUB_SUMMARY_MARKERS)


def _goal_metadata_field_matches(markdown_text: str) -> list[tuple[int, str]]:
    """Return preamble ``Goal:`` fields and their line indexes.

    The first H1 is the document title and may precede the metadata. Once that
    title has appeared, any ATX heading (H1-H6, with Markdown's 0-3-space
    indentation) ends the preamble so body text cannot bind as metadata.
    """
    fields: list[tuple[int, str]] = []
    fence_marker: tuple[str, int] | None = None
    previous_line: str | None = None
    seen_nonblank = False
    title_seen = False
    for line_number, line in enumerate(markdown_text.splitlines()):
        # The first H1 is the document title. Every later ATX heading is a body
        # boundary; check it before rejecting indented text so Markdown-valid
        # 0-3-space headings cannot leave a later Goal: looking like metadata.
        if _ATX_HEADING_PATTERN.match(line):
            if not seen_nonblank and not title_seen and _H1_PATTERN.match(line):
                title_seen = True
                seen_nonblank = True
                previous_line = line
                continue
            break
        if line.startswith((" ", "\t")):
            previous_line = None
            continue
        fence = _FENCE_PATTERN.match(line)
        if fence is not None:
            marker_text = fence.group("marker")
            marker = marker_text[0]
            if fence_marker is None:
                fence_marker = (marker, len(marker_text))
            elif (
                marker == fence_marker[0]
                and len(marker_text) >= fence_marker[1]
                and not fence.group("info").strip()
            ):
                fence_marker = None
            previous_line = None
            continue
        if fence_marker is not None:
            previous_line = None
            continue
        if line.strip():
            seen_nonblank = True
        if previous_line is not None and _SETEXT_H2_PATTERN.fullmatch(line):
            break
        previous_line = line
        match = _GOAL_FIELD_PATTERN.fullmatch(line)
        if match is not None:
            fields.append((line_number, match.group("value").strip()))
    return fields


def _goal_metadata_fields(markdown_text: str) -> list[str]:
    """Read only top-level preamble fields, excluding fenced/code-block text."""
    return [value for _line_number, value in _goal_metadata_field_matches(markdown_text)]


def _canonicalize_goal_metadata(markdown_text: str, canonical_path: str) -> str:
    """Rewrite the validated slug form to the canonical repo-relative path."""
    fields = _goal_metadata_field_matches(markdown_text)
    if len(fields) != 1:
        return markdown_text
    line_number, _value = fields[0]
    lines = markdown_text.splitlines(keepends=True)
    original = lines[line_number]
    line_end = ""
    if original.endswith("\r\n"):
        line_end = "\r\n"
    elif original.endswith(("\n", "\r")):
        line_end = original[-1]
    lines[line_number] = f"Goal: {canonical_path}{line_end}"
    return "".join(lines)


def _goal_identity(repo_root: Path, goal_path: Path, markdown_text: str) -> dict[str, str]:
    """Resolve and validate the exact identity used by goal-aware persistence."""
    root = repo_root.resolve()
    resolved_goal = (
        (root / goal_path).resolve() if not goal_path.is_absolute() else goal_path.resolve()
    )
    try:
        relative_goal = resolved_goal.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("--goal-path must resolve inside --repo-root") from exc
    path_match = _GOAL_PATH_PATTERN.fullmatch(relative_goal)
    if path_match is None or not resolved_goal.is_file():
        raise ValueError(
            "--goal-path must resolve to an existing canonical goal artifact "
            "under charness-artifacts/goals/YYYY-MM-DD-<slug>.md"
        )

    fields = _goal_metadata_fields(markdown_text)
    if len(fields) != 1 or not fields[0]:
        raise ValueError(
            "goal-aware retro must contain exactly one non-empty `Goal:` metadata field"
        )
    expected_path = relative_goal
    expected_slug = path_match.group("slug")
    if fields[0] not in {expected_path, expected_slug}:
        raise ValueError(
            "retro `Goal:` identity does not match --goal-path: "
            f"expected `{expected_path}` or `{expected_slug}`, got `{fields[0]}`"
        )
    return {"goal_path": expected_path, "goal_slug": expected_slug}


def persist_retro_artifact(
    *,
    repo_root: Path,
    output_dir: Path,
    artifact_name: str,
    markdown_text: str,
    summary_path: Path | None,
    force_empty_summary: bool = False,
    goal_path: Path | None = None,
    goal_lineage_path: Path | None = None,
) -> dict[str, Any]:
    # Guarded here, at the WRITE boundary, rather than only in the CLIs above it:
    # `publish_release` reaches this function directly, and the four failed publishes
    # this check exists for wrote an old-schema lesson index through exactly this
    # path from an installed plugin copy. See scripts/core/helper_provenance_lib.py.
    require_repo_local_helper(__file__, repo_root)
    if goal_path is not None and goal_lineage_path is not None:
        raise ValueError("retro accepts either --goal-path or --goal-lineage-file, not both")
    goal_identity = (
        _goal_identity(repo_root, goal_path, markdown_text) if goal_path is not None else None
    )
    try:
        if goal_lineage_path is not None:
            goal_lineage = load_goal_lineage_file(repo_root, goal_lineage_path)
        elif goal_path is not None:
            goal_lineage = planning_only_lineage(
                repo_root,
                goal_path,
                "legacy goal-aware retro retains draft provenance but has no Goal Run binding",
            )
        else:
            goal_lineage = not_goal_bound_lineage("retro was persisted without a Goal Run identity")
    except LineageError as exc:
        raise ValueError(str(exc)) from exc
    if goal_identity is not None:
        markdown_text = _canonicalize_goal_metadata(markdown_text, goal_identity["goal_path"])
    artifact_path, subject_path_derived = resolve_retro_artifact_path(output_dir, artifact_name)
    relpath = str(artifact_path.relative_to(repo_root))
    if subject_path_derived and artifact_path.exists():
        raise ValueError(
            f"refusing to overwrite existing retro artifact `{relpath}` resolved from subject key "
            f"`{artifact_name}`. Inspect that existing path and rerun with a different subject key, "
            "or explicitly name the existing dated path only when replacement is intentional."
        )
    line_stamped = bool(_PERSISTED_LINE_PATTERN.search(markdown_text))
    markdown_text = stamp_persisted_path(markdown_text, relpath)
    _write_text(artifact_path, markdown_text)

    result: dict[str, Any] = {
        "artifact_path": relpath,
        "summary_refreshed": False,
        "persisted_line_stamped": line_stamped,
    }
    if not artifact_name.endswith(".md"):
        result["artifact_name_normalized"] = True
    if goal_identity is not None:
        result.update(goal_identity)
    result["goal_lineage"] = goal_lineage

    if (
        summary_path is None
        and artifact_path.resolve() != output_dir.resolve() / "recent-lessons.md"
    ):
        index_path = _run_index_builder(repo_root, output_dir)
        result["lesson_selection_index_path"] = str(index_path.relative_to(repo_root))
    elif summary_path is not None and artifact_path.resolve() != summary_path.resolve():
        digest = build_indexed_recent_lessons(
            repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
        )
        section_counts = digest.section_counts
        no_candidates = sum(section_counts.values()) == 0
        existing_text = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
        existing_is_protected = bool(existing_text.strip()) and not is_stub_summary(existing_text)

        if no_candidates and existing_is_protected and not force_empty_summary:
            print(
                f"persist_retro_artifact: lesson selection produced 0 candidates; "
                f"refusing to overwrite existing summary at "
                f"{summary_path.relative_to(repo_root)}. Pass --force-empty-summary "
                f"once you have confirmed it is safe to replace with the empty-stub digest.",
                file=sys.stderr,
            )
            result["summary_path"] = str(summary_path.relative_to(repo_root))
            result["summary_refreshed"] = False
            result["summary_skipped_reason"] = "no_candidates_existing_summary_protected"
        else:
            _write_text(summary_path, digest.summary_text)
            index_path = _run_index_builder(repo_root, output_dir)
            result["summary_path"] = str(summary_path.relative_to(repo_root))
            result["lesson_selection_index_path"] = str(index_path.relative_to(repo_root))
            result["summary_refreshed"] = True

    return result
