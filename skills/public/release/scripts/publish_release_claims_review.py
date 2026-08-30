from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

RELEASE_RECORD_FILENAME = "latest.md"
# NOT derived from `output_dir`, deliberately.  The claims record's location is defined by
# this floor and has no adapter key; deriving it would make every already-committed claims
# record unreadable in a repo that later moves its release output, and there is no contract
# behind that move.  Only the RELEASE RECORD is adapter-owned.
# This module is loaded BY SPEC from several entrypoints, so a bare
# `from claims_review_scope import ...` resolves only when the caller happens to
# have this directory on the path. Locating it relative to __file__ works in the
# repo and in the plugin export alike.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import claims_review_evidence as _evidence  # noqa: E402
from claims_review_schema import (  # noqa: E402
    VERDICTS,
    assert_closed_record_shape,
    assert_exact_record_binding,
)
from claims_review_scope import (  # noqa: E402
    assert_scope_is_declared,
    assert_scope_matches_release_delta,
)

MARKER = _evidence.PREPARED_MARKER
REVIEW_ROOT = _evidence.EVIDENCE_ROOT

CLAIMS_PHASES = {
    "prepared-claims-review",
    "post-publication-claims-carrier",
    "post-publication-claims-final",
}


def assert_claims_artifact_is_read(phase: str, claims_review_artifact: str | None) -> None:
    """Refuse a claims artifact the resolved phase will never open.

    Accepted-and-silently-ignored is the worse half of the marker fall-through: the
    operator supplies a real record, the planner told them to, and nothing reads it.

    Its own function because it is only reachable through a CLI subprocess otherwise,
    which is invisible to in-process coverage — a refusal nobody exercised is a floor
    nobody proved.
    """
    if claims_review_artifact and phase not in CLAIMS_PHASES:
        raise SystemExit(
            f"--resume: --claims-review-artifact was supplied but the resolved phase is "
            f"`{phase}`, which does not read it; refusing rather than publishing "
            "with the record unread."
        )


def unproven_claims_warning(claims_review: dict[str, Any], *, write: Any) -> None:
    """Announce an `unproven` verdict at the boundary.

    LOUD, because publication may proceed on `unproven` — that is the point of the state.
    The published release record now carries the verdict too, but that record is read
    AFTER the fact by someone outside the session; stderr is what puts it in front of the
    operator standing at the boundary, while there is still a decision to make.
    """
    if claims_review.get("verdict") != "unproven":
        return
    write(
        "WARNING (release claims review): verdict is `unproven` -- the distinct-observer "
        "property was NOT established for this release. Recorded signal: "
        f"{claims_review['observer_distinctness']['signal']}\n"
    )


def release_record_path(adapter_data: dict[str, Any]) -> str:
    """The release record path THIS run must read, derived from the adapter's `output_dir`.

    A module constant here is what made the floor blind: the artifact writer has always
    honoured `output_dir`, so a consumer that set a different one had every marker lookup
    return "no such file", the resume fall through to the legacy marker-free lane, and the
    release publish with no claims review and no refusal -- the same fall-through the
    marker guard closes, reached by a route that guard is structurally unable to see,
    because it re-asks the question that already returned "no file here".

    A HARD key read, deliberately. `adapter_data.get("output_dir", "<the old default>")`
    is the tempting repair when a caller or fixture omits the key, and it silently
    reinstates exactly this defect for every such caller -- a default that is right for
    the authoring repo and wrong for the repos the fix exists for. The adapter resolver
    always supplies the key, so its absence is a caller defect and is named as one.

    `PurePosixPath` rather than string concatenation: `output_dir: charness-artifacts/release/`
    would otherwise derive `charness-artifacts/release//latest.md`, which git reads as a
    miss (verified: `git show HEAD:a//b` exits 128) -- a formatting difference silently
    reproducing the blindness. Absolute, `..`-bearing, and separator-mismatched values
    normalize to something git still cannot read; `assert_record_readable` below is what
    turns every one of those into a refusal instead of a miss.

    The value is NOT stripped, and that is the point rather than an omission: the writer
    does not strip it either, so any normalization this side alone applies is a way for the
    floor and the writer to name two different files. `""` derives `latest.md`, matching the
    writer's `repo_root / "" / "latest.md"` -- a blank `output_dir` is a declaration of the
    repo root, not an absent one, and refusing it here while the prepare wrote a record
    there made the prepared stop unresumable by either route.
    """
    output_dir = adapter_data.get("output_dir")
    if not isinstance(output_dir, str):
        raise SystemExit(
            "--resume: the release adapter declares no `output_dir`, so the claims-review floor "
            "cannot resolve which release record to read. Refusing rather than assuming a "
            "default: assuming one is what made this floor blind. Repair the adapter first."
        )
    return str(PurePosixPath(output_dir) / RELEASE_RECORD_FILENAME)


def assert_record_readable(repo_root: Path, *, record_path: str, commit: str, run) -> None:
    """Refuse when the release record is not readable at the adapter-derived path.

    This is the replacement for the old value-comparison refusal, and it is strictly
    wider. That one asked "is `output_dir` the default?", which caught a non-default
    consumer only because it caught EVERY non-default consumer, and could not catch the
    case it shares a cause with: the operator edits `output_dir` between the prepared stop
    and the resume. The prepared stop is precisely where record blockers surface, so
    editing the adapter there is an ordinary action -- and the record committed at the stop
    lives at the OLD path while the resume derives the new one.

    Asked positively, one refusal covers every way the derivation can fail to name a
    readable file: absolute, `..`-bearing, empty, separator-mismatched, typo'd, and
    changed-since-prepare. It is checkable because the same flow's writer must have put the
    record there. Without it, deleting the old refusal converts each of those back into a
    silent marker miss and an unreviewed publish.
    """
    result = run(["git", "show", f"{commit}:{record_path}"], cwd=repo_root, check=False)
    if result.returncode != 0:
        raise SystemExit(
            f"--resume: the release record is not readable at {record_path!r} in `{commit}`, so the "
            "claims-review floor cannot run and the resume would fall through to the legacy "
            "marker-free lane, which validates no claims review at all. This path is derived from "
            "the release adapter's `output_dir`; check that it matches the directory the release "
            "record was actually written to -- including for a prepared stop whose adapter changed "
            "since it was recorded, and that the record is TRACKED: a gitignored release output "
            "directory reads here exactly like a wrong path."
        )


def marker_at_commit(repo_root: Path, *, commit: str, record_path: str, run) -> bool:
    """Whether ``commit``'s release record carries the prepared-stop marker at all.

    Distinct from ``prepared_record``, which answers the narrower "did this commit
    INTRODUCE the marker across a single parent". That narrowing is correct for choosing
    the review boundary and wrong as a lane selector: when the marker is present but
    unattributable -- a second prepare while one is outstanding, which is the single most
    likely action at a stop, since the stop exists to surface record blockers -- every
    prepared branch declines and the resume silently falls through to the legacy
    marker-free lane, which never validates a claims review at all.
    """
    result = run(["git", "show", f"{commit}:{record_path}"], cwd=repo_root, check=False)
    return result.returncode == 0 and MARKER in result.stdout


def prepared_record(
    repo_root: Path, *, commit: str, record_path: str, run
) -> dict[str, str] | None:
    result = run(["git", "show", f"{commit}:{record_path}"], cwd=repo_root, check=False)
    if result.returncode != 0 or MARKER not in result.stdout:
        return None
    # The marker is intentionally inherited by descendants.  A prepared record
    # is the commit that *introduced* it, not any later commit that happens to
    # retain the same file; otherwise an unreviewed P -> X -> R sequence can
    # reclassify X as the prepared record and shift the review boundary.
    # A merge can retain the marker from a non-first parent while appearing to
    # introduce it against its first parent.  That is not the one-parent P
    # boundary required by the claims-review topology.
    parents = run(["git", "show", "-s", "--format=%P", commit], cwd=repo_root, check=False)
    if parents.returncode != 0 or len(parents.stdout.split()) != 1:
        return None
    parent = run(
        ["git", "show", f"{parents.stdout.split()[0]}:{record_path}"], cwd=repo_root, check=False
    )
    if parent.returncode == 0 and MARKER in parent.stdout:
        return None
    # `path` is what `validate_claims_review` binds `release_record_path` against, so it
    # must be the DERIVED path too. Threading the three reads and leaving this one a
    # constant yields a floor that reads the right file and then demands the record name
    # the wrong one -- a refusal whose message points at neither.
    return {
        "commit": commit,
        "path": record_path,
        "sha256": hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(),
    }


def validate_claims_review(
    repo_root: Path,
    *,
    prepared: dict[str, str],
    evidence_commit: str,
    artifact_path: str | None,
    target_version: str,
    tag_name: str,
    run,
    previous_version: str | None = None,
) -> dict[str, Any]:
    if not artifact_path:
        raise SystemExit("--resume: prepared claims-review state requires --claims-review-artifact")
    normalized = _evidence.review_relative_path(artifact_path, "--claims-review-artifact", ".json")
    parents = run(["git", "show", "-s", "--format=%P", evidence_commit], cwd=repo_root, check=False)
    if parents.returncode != 0 or parents.stdout.split() != [prepared["commit"]]:
        raise SystemExit(
            "--resume: claims-review evidence must be the direct child of the prepared release record"
        )
    changed = [
        line
        for line in run(
            [
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                prepared["commit"],
                evidence_commit,
            ],
            cwd=repo_root,
        ).stdout.splitlines()
        if line
    ]
    # Early, before anything is read out of the record: unreviewed content must not ride
    # along in R. The exact-set check below additionally binds the second path to the one
    # the record itself names, which cannot be known until the record is parsed.
    if normalized not in changed or any(not path.startswith(REVIEW_ROOT) for path in changed):
        raise SystemExit(
            f"--resume: claims-review evidence commit must change only claims-review evidence; observed {sorted(changed)!r}"
        )
    record = run(["git", "show", f"{evidence_commit}:{normalized}"], cwd=repo_root, check=False)
    if record.returncode != 0:
        raise SystemExit(f"--resume: claims-review artifact is not committed at HEAD: {normalized}")
    try:
        data = json.loads(record.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"--resume: claims-review artifact is not valid JSON: {normalized}"
        ) from exc
    data = assert_exact_record_binding(
        data, prepared=prepared, target_version=target_version, tag_name=tag_name
    )
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        raise SystemExit(f"--resume: claims-review `verdict` must be one of {list(VERDICTS)}")
    assert_closed_record_shape(data, verdict=verdict)
    preparer, reviewer = data.get("preparer_context"), data.get("reviewer_context")
    if (
        not isinstance(preparer, str)
        or not preparer.strip()
        or not isinstance(reviewer, str)
        or not reviewer.strip()
        or preparer == reviewer
    ):
        raise SystemExit(
            "--resume: claims-review artifact requires distinct nonempty preparer_context and reviewer_context"
        )
    # "Who reviewed this" is more fundamental than "what did the verdict cover".
    # Validate the observer first so a record missing both is told about the
    # unestablished review boundary rather than secondary scope bookkeeping.
    distinctness = _evidence.observer_distinctness(
        data,
        verdict=verdict,
        prepared=prepared,
        target_version=target_version,
        evidence_commit=evidence_commit,
        repo_root=repo_root,
        run=run,
    )
    assert_scope_is_declared(data, verdict=verdict)
    if verdict == "pass":
        assert_scope_matches_release_delta(
            repo_root, data, prepared=prepared, run=run, previous_version=previous_version
        )
    # The evidence commit still carries only claims-review evidence.  The narrative is
    # the product of the review, so it lands in the same commit as the record that
    # names it -- and nothing else may ride along.
    allowed = sorted({normalized, *(x for x in [distinctness["review_artifact"]] if x)})
    if sorted(changed) != allowed:
        raise SystemExit(
            f"--resume: claims-review evidence commit must change only the supplied artifact and the "
            f"review_artifact it names; expected {allowed!r}, observed {sorted(changed)!r}"
        )
    return {
        "path": normalized,
        "sha256": hashlib.sha256(record.stdout.encode("utf-8")).hexdigest(),
        "prepared": prepared,
        "reviewer_context": reviewer,
        "verdict": verdict,
        "observer_distinctness": distinctness,
        "review_scope": data.get("review_scope"),
        "scope_basis": data.get("scope_basis"),
        "advisory_findings": data.get("advisory_findings") or [],
    }
