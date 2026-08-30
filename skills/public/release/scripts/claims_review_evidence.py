"""Evidence-carrier and observer contract for release claims reviews."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_SCHEMA = runpy.run_path(
    str(Path(__file__).resolve().with_name("claims_review_schema.py"))
)
DISTINCTNESS_KINDS = _SCHEMA["DISTINCTNESS_KINDS"]

PREPARED_MARKER = "charness-release-state:prepared-awaiting-claims-review"
EVIDENCE_ROOT = "charness-artifacts/release-review/"
MINIMUM_NARRATIVE_BYTES = 500
MAXIMUM_SIGNAL_BYTES = 600
RECORD_SENTINELS = (
    PREPARED_MARKER,
    "carrier-pending-state-verification",
    "Issue closeout verification:",
    "charness-artifacts/probe/",
)


def assert_no_record_sentinel(value: str, field: str) -> None:
    """Keep one rendered field from impersonating another release-state fact."""
    for sentinel in RECORD_SENTINELS:
        if sentinel in value:
            raise SystemExit(
                f"{field} must not contain {sentinel!r}; it is rendered into the published "
                "release record, which other surfaces prove release state by "
                "substring-matching. Rename the file."
            )


def claims_record_in_change_set(changed: list[str]) -> str | None:
    """Return the sole JSON record when paths have the evidence-commit shape."""
    paths = [path for path in changed if path]
    if not paths or not all(path.startswith(EVIDENCE_ROOT) for path in paths):
        return None
    records = [path for path in paths if path.endswith(".json")]
    narratives = [path for path in paths if path.endswith(".md")]
    if len(records) != 1 or len(narratives) > 1 or len(records) + len(narratives) != len(paths):
        return None
    return records[0]


def review_relative_path(value: object, field: str, suffix: str) -> str:
    """Validate one evidence-carrier path without normalizing its identity."""
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"--resume: claims-review {field} must be a repo-relative path")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SystemExit(f"--resume: claims-review {field} must be a normalized repo-relative path")
    normalized = path.as_posix()
    if not normalized.startswith(EVIDENCE_ROOT) or not normalized.endswith(suffix):
        raise SystemExit(
            f"--resume: claims-review {field} must be a {suffix} file under {EVIDENCE_ROOT}"
        )
    assert_no_record_sentinel(normalized, f"--resume: claims-review {field}")
    return normalized


def assert_signal_is_renderable(signal: str) -> None:
    """Refuse free text that could inject or impersonate release-record state."""
    if any(character in signal for character in "\r\n") or any(
        ord(character) < 0x20 for character in signal
    ):
        raise SystemExit(
            "--resume: claims-review `observer_distinctness.signal` must be a single line; "
            "it is rendered into the published release record, and a newline there injects "
            "arbitrary lines into a document other gates parse"
        )
    for sentinel in RECORD_SENTINELS:
        if sentinel in signal:
            raise SystemExit(
                f"--resume: claims-review `observer_distinctness.signal` must not contain "
                f"{sentinel!r}; another surface proves release state by matching that substring"
            )
    if len(signal.encode("utf-8")) > MAXIMUM_SIGNAL_BYTES:
        raise SystemExit(
            f"--resume: claims-review `observer_distinctness.signal` exceeds "
            f"{MAXIMUM_SIGNAL_BYTES} bytes; put review reasoning in the narrative"
        )


def narrative_is_new(
    repo_root: Path,
    *,
    prepared_commit: str,
    evidence_commit: str,
    narrative: str,
    run,
) -> bool:
    result = run(
        [
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-status",
            "-r",
            prepared_commit,
            evidence_commit,
        ],
        cwd=repo_root,
        check=False,
    )
    if result.returncode != 0:
        return False
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[-1] == narrative:
            return parts[0].startswith("A")
    return False


def observer_distinctness(
    data: dict[str, Any],
    *,
    verdict: str,
    prepared: dict[str, str],
    target_version: str,
    evidence_commit: str,
    repo_root: Path,
    run,
) -> dict[str, Any]:
    """Validate the recorded observer boundary and its release-bound product."""
    declared = data.get("observer_distinctness")
    if not isinstance(declared, dict):
        raise SystemExit(
            "--resume: claims-review artifact requires an `observer_distinctness` object; "
            "distinctness is a recorded observable, not an inference from unequal strings"
        )
    kind, signal = declared.get("kind"), declared.get("signal")
    if not isinstance(signal, str) or not signal.strip():
        raise SystemExit(
            "--resume: claims-review `observer_distinctness.signal` must name the concrete "
            "signal behind the recorded kind"
        )
    assert_signal_is_renderable(signal)
    if verdict == "unproven":
        if kind != "unproven":
            raise SystemExit(
                '--resume: `verdict: unproven` requires `observer_distinctness.kind: "unproven"`'
            )
        return {"kind": kind, "signal": signal, "review_artifact": None}
    if kind not in DISTINCTNESS_KINDS:
        raise SystemExit(
            f"--resume: `observer_distinctness.kind` must be one of "
            f"{list(DISTINCTNESS_KINDS)} for a `pass`"
        )
    narrative = review_relative_path(declared.get("review_artifact"), "review_artifact", ".md")
    if not narrative_is_new(
        repo_root,
        prepared_commit=prepared["commit"],
        evidence_commit=evidence_commit,
        narrative=narrative,
        run=run,
    ):
        raise SystemExit(
            "--resume: claims-review review_artifact must be ADDED by the evidence commit, "
            f"not edited: {narrative}"
        )
    shown = run(["git", "show", f"{evidence_commit}:{narrative}"], cwd=repo_root, check=False)
    if shown.returncode != 0:
        raise SystemExit(
            f"--resume: claims-review review_artifact is not committed at the evidence commit: "
            f"{narrative}"
        )
    text = shown.stdout
    if len(text.encode("utf-8")) < MINIMUM_NARRATIVE_BYTES:
        raise SystemExit(
            f"--resume: claims-review review_artifact is under {MINIMUM_NARRATIVE_BYTES} "
            "bytes; a `pass` must carry the product of the review it asserts"
        )
    if prepared["commit"][:12] not in text or target_version not in text:
        raise SystemExit(
            "--resume: claims-review review_artifact must name the prepared commit "
            f"{prepared['commit'][:12]} and target version {target_version}"
        )
    return {"kind": kind, "signal": signal, "review_artifact": narrative}
