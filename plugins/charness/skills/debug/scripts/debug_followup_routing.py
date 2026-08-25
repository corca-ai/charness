from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def resolved_followup_record_payload(
    repo_root: Path,
    *,
    adapter: dict[str, object],
    resolved_title: str,
    artifact_date: Any,
    current_pointer_target_path: str | None,
    reuse_subject_key: str | None = None,
    scaffold_artifact_lib: Any,
    resolve_artifact_path: Any,
    resolution: Callable[[Path], str],
) -> dict[str, object]:
    def record_payload_for(title_text: str) -> dict[str, object]:
        return resolve_artifact_path.payload_for(
            repo_root,
            "debug",
            title_text,
            intent="record",
            artifact_date=artifact_date,
            adapter=adapter,
        )

    current_target = current_pointer_target_path or ""

    def usable(candidate_path: str) -> bool:
        if candidate_path == current_target:
            return False
        if (
            reuse_subject_key is not None
            and scaffold_artifact_lib.record_subject_slug(candidate_path) == reuse_subject_key
            and resolution(repo_root / candidate_path) != "resolved"
        ):
            return True
        return not (repo_root / candidate_path).exists()

    candidate = record_payload_for(resolved_title)
    if usable(str(candidate["write_artifact_path"])):
        return candidate
    for suffix in ("followup", "followup-2", "followup-3", "followup-4"):
        candidate = record_payload_for(f"{resolved_title} {suffix}")
        if usable(str(candidate["write_artifact_path"])):
            return candidate
    raise SystemExit(
        "resolved current debug artifact needs a fresh dated follow-up record, but every deterministic "
        "default slug for today already exists; rerun scaffold_debug_artifact.py with --title <specific follow-up title>"
    )
