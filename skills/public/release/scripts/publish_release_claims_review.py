from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MARKER = "charness-release-state:prepared-awaiting-claims-review"
SCHEMA_VERSION = "charness.release.claims-review.v2"
# v1's only distinctness test was `preparer_context != reviewer_context`, so one agent
# writing two different strings satisfied the distinct-observer floor completely, and a
# spawn-blocked session had `verdict: pass` as its only path forward.  Accepting v1 here
# would leave that path open, so it is refused by name.
SUPERSEDED_SCHEMA_VERSIONS = {"charness.release.claims-review.v1"}
RELEASE_RECORD_PATH = "charness-artifacts/release/latest.md"
REVIEW_ROOT = "charness-artifacts/release-review/"
VERDICTS = ("pass", "unproven")
# Every accepted kind names a boundary the review actually crossed.  There is
# deliberately no `same-agent` value: a same-agent reread is the observer this floor
# exists to exclude, and its honest record is `verdict: unproven`.
DISTINCTNESS_KINDS = ("separate-agent-context", "separate-host", "separate-operator")
# A floor against the SHAPE that was observed passing -- an 11-line record carrying a
# verdict and two context strings and no review product at all.  It is not a proof that
# a review happened; nothing checkable on the publishing machine is.
MINIMUM_NARRATIVE_BYTES = 500


def claims_record_in_change_set(changed: list[str]) -> str | None:
    """The claims record in a changed-path set with the claims-evidence SHAPE, else None.

    One owner for the shape, because two had it: the resume phase classifier and the run
    planner each decided independently what an evidence commit looks like, and a rule
    split across two readers is one edit away from disagreeing about which commits the
    claims floor applies to. `validate_claims_review` is still what binds the narrative to
    the record the JSON itself names; this only answers "does this look like R".
    """
    paths = [path for path in changed if path]
    if not paths or not all(path.startswith(REVIEW_ROOT) for path in paths):
        return None
    records = [path for path in paths if path.endswith(".json")]
    narratives = [path for path in paths if path.endswith(".md")]
    if len(records) != 1 or len(narratives) > 1 or len(records) + len(narratives) != len(paths):
        return None
    return records[0]


def blob_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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

    LOUD, because publication may proceed on `unproven` — that is the point of the
    state — but the published release record does not yet mirror it, so stderr is the
    only channel that puts it in front of the operator.
    """
    if claims_review.get("verdict") != "unproven":
        return
    write(
        "WARNING (release claims review): verdict is `unproven` -- the distinct-observer "
        "property was NOT established for this release. Recorded signal: "
        f"{claims_review['observer_distinctness']['signal']}\n"
    )


def assert_record_path_matches_adapter(output_dir: str | None) -> None:
    """Refuse when the adapter writes the release record somewhere this module cannot read.

    This module reads a HARDCODED record path while the artifact writer honours the
    adapter's `output_dir`. In a consumer repo that sets a non-default one, every marker
    lookup returns "no such file", the phase falls to the legacy marker-free lane, and the
    release publishes with no claims review and no refusal -- the same fall-through the
    marker guard closes, reached by a route that guard is structurally unable to see,
    because it re-asks the question that already returned "no file here".

    Owned here rather than at the call site because this module is what pins the path and
    therefore what knows when it has been aimed somewhere else.
    """
    configured = str(output_dir or "").rstrip("/")
    expected = RELEASE_RECORD_PATH.rsplit("/", 1)[0]
    if configured and configured != expected:
        raise SystemExit(
            f"--resume: adapter `output_dir` is {configured!r}, but the claims-review floor reads "
            f"the release record at {expected!r}. Every marker lookup would miss, and the resume "
            "would publish through the marker-free lane with no claims review. Refusing; the "
            "record path needs threading through the claims module before a non-default "
            "`output_dir` can publish."
        )


def marker_at_commit(repo_root: Path, *, commit: str, run) -> bool:
    """Whether ``commit``'s release record carries the prepared-stop marker at all.

    Distinct from ``prepared_record``, which answers the narrower "did this commit
    INTRODUCE the marker across a single parent". That narrowing is correct for choosing
    the review boundary and wrong as a lane selector: when the marker is present but
    unattributable -- a second prepare while one is outstanding, which is the single most
    likely action at a stop, since the stop exists to surface record blockers -- every
    prepared branch declines and the resume silently falls through to the legacy
    marker-free lane, which never validates a claims review at all.
    """
    result = run(["git", "show", f"{commit}:{RELEASE_RECORD_PATH}"], cwd=repo_root, check=False)
    return result.returncode == 0 and MARKER in result.stdout


def prepared_record(repo_root: Path, *, commit: str, run) -> dict[str, str] | None:
    result = run(["git", "show", f"{commit}:{RELEASE_RECORD_PATH}"], cwd=repo_root, check=False)
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
    parent = run(["git", "show", f"{parents.stdout.split()[0]}:{RELEASE_RECORD_PATH}"], cwd=repo_root, check=False)
    if parent.returncode == 0 and MARKER in parent.stdout:
        return None
    return {"commit": commit, "path": RELEASE_RECORD_PATH, "sha256": blob_sha256(result.stdout)}


def _review_relative_path(value: object, field: str, suffix: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"--resume: claims-review {field} must be a repo-relative path")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SystemExit(f"--resume: claims-review {field} must be a normalized repo-relative path")
    normalized = path.as_posix()
    if not normalized.startswith(REVIEW_ROOT) or not normalized.endswith(suffix):
        raise SystemExit(f"--resume: claims-review {field} must be a {suffix} file under {REVIEW_ROOT}")
    return normalized


def _narrative_is_new(repo_root: Path, *, prepared_commit: str, evidence_commit: str,
                      narrative: str, run) -> bool:
    """Whether the evidence commit ADDED the narrative rather than editing an old one.

    The byte floor and the naming check both read the whole FILE, so an accepted `pass`
    cost one appended line on a previous release's 4 KB narrative: it clears 500 bytes
    (inherited) and names this prepared commit and version (appended). The review's
    product is produced BY this review, so requiring it to be new is both the honest rule
    and the one that closes that.
    """
    result = run(
        ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", prepared_commit, evidence_commit],
        cwd=repo_root, check=False,
    )
    if result.returncode != 0:
        return False
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[-1] == narrative:
            return parts[0].startswith("A")
    return False


def _observer_distinctness(data: dict[str, Any], *, verdict: str, prepared: dict[str, str],
                           target_version: str, evidence_commit: str, repo_root: Path, run) -> dict[str, Any]:
    """Read the RECORDED distinctness claim, in the shape the publication boundary
    already uses for the other release verdict: each verdict record names its observer
    identity explicitly, so distinctness is an observable the audit reads rather than a
    property inferred from two strings being unequal.

    The honest non-claim, stated once here: nothing runnable on the publishing machine
    can prove a distinct observer existed.  What this can do is refuse the shapes that
    made the claim unfalsifiable -- an undeclared relationship, a same-agent reread with
    nowhere to say so, and a `pass` carrying no product of the review it asserts.
    """
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
    if verdict == "unproven":
        # The state `critique-boundary.md` already names and the validator never had:
        # record the concrete signal and publish with the review unproven rather than
        # substituting a same-agent reread.
        if kind != "unproven":
            raise SystemExit(
                "--resume: `verdict: unproven` requires `observer_distinctness.kind: \"unproven\"`"
            )
        return {"kind": kind, "signal": signal, "review_artifact": None}
    if kind not in DISTINCTNESS_KINDS:
        raise SystemExit(
            f"--resume: `observer_distinctness.kind` must be one of {list(DISTINCTNESS_KINDS)} for a "
            "`pass`; a same-agent reread has no passing kind and is recorded as `verdict: unproven`"
        )
    narrative = _review_relative_path(declared.get("review_artifact"), "review_artifact", ".md")
    if not _narrative_is_new(repo_root, prepared_commit=prepared["commit"],
                             evidence_commit=evidence_commit, narrative=narrative, run=run):
        raise SystemExit(
            f"--resume: claims-review review_artifact must be ADDED by the evidence commit, not "
            f"edited: {narrative}. The byte floor and the naming check read the whole file, so an "
            "appended line on an earlier release's narrative would otherwise satisfy both."
        )
    shown = run(["git", "show", f"{evidence_commit}:{narrative}"], cwd=repo_root, check=False)
    if shown.returncode != 0:
        raise SystemExit(f"--resume: claims-review review_artifact is not committed at the evidence commit: {narrative}")
    text = shown.stdout
    if len(text.encode("utf-8")) < MINIMUM_NARRATIVE_BYTES:
        raise SystemExit(
            f"--resume: claims-review review_artifact is under {MINIMUM_NARRATIVE_BYTES} bytes; a "
            "`pass` must carry the product of the review it asserts"
        )
    # Bound to THIS release. The re-pointing this blocks is a WHOLE-file reuse; an
    # appended line is blocked by the added-not-edited check above, not by this one.
    if prepared["commit"][:12] not in text or target_version not in text:
        raise SystemExit(
            f"--resume: claims-review review_artifact must name the prepared commit "
            f"{prepared['commit'][:12]} and target version {target_version}"
        )
    return {"kind": kind, "signal": signal, "review_artifact": narrative}


def validate_claims_review(repo_root: Path, *, prepared: dict[str, str], evidence_commit: str,
                           artifact_path: str | None, target_version: str, tag_name: str, run) -> dict[str, Any]:
    if not artifact_path:
        raise SystemExit("--resume: prepared claims-review state requires --claims-review-artifact")
    normalized = _review_relative_path(artifact_path, "--claims-review-artifact", ".json")
    parents = run(["git", "show", "-s", "--format=%P", evidence_commit], cwd=repo_root, check=False)
    if parents.returncode != 0 or parents.stdout.split() != [prepared["commit"]]:
        raise SystemExit("--resume: claims-review evidence must be the direct child of the prepared release record")
    changed = [line for line in run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", prepared["commit"], evidence_commit], cwd=repo_root).stdout.splitlines() if line]
    # Early, before anything is read out of the record: unreviewed content must not ride
    # along in R. The exact-set check below additionally binds the second path to the one
    # the record itself names, which cannot be known until the record is parsed.
    if normalized not in changed or any(not path.startswith(REVIEW_ROOT) for path in changed):
        raise SystemExit(f"--resume: claims-review evidence commit must change only claims-review evidence; observed {sorted(changed)!r}")
    record = run(["git", "show", f"{evidence_commit}:{normalized}"], cwd=repo_root, check=False)
    if record.returncode != 0:
        raise SystemExit(f"--resume: claims-review artifact is not committed at HEAD: {normalized}")
    try:
        data = json.loads(record.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--resume: claims-review artifact is not valid JSON: {normalized}") from exc
    if not isinstance(data, dict):
        raise SystemExit("--resume: claims-review artifact does not bind the exact prepared release record")
    if data.get("schema_version") in SUPERSEDED_SCHEMA_VERSIONS:
        raise SystemExit(
            f"--resume: claims-review artifact uses superseded schema {data['schema_version']!r}; "
            f"{SCHEMA_VERSION} requires an `observer_distinctness` object and accepts "
            f"`verdict: unproven` so a host with no distinct observer has an honest record. "
            "Recovery for an already-committed v1 record: AMEND that commit in place (a "
            "follow-on commit is not the direct child of the prepared record and is refused); "
            "if it was already pushed, the amend needs a force-push to the release branch, "
            "which is its own grant-requiring boundary."
        )
    expected = {"schema_version": SCHEMA_VERSION, "prepared_commit": prepared["commit"],
                "release_record_path": prepared["path"], "release_record_sha256": prepared["sha256"],
                "target_version": target_version, "tag_name": tag_name}
    if any(data.get(key) != value for key, value in expected.items()):
        raise SystemExit("--resume: claims-review artifact does not bind the exact prepared release record")
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        raise SystemExit(f"--resume: claims-review `verdict` must be one of {list(VERDICTS)}")
    preparer, reviewer = data.get("preparer_context"), data.get("reviewer_context")
    if not isinstance(preparer, str) or not preparer.strip() or not isinstance(reviewer, str) or not reviewer.strip() or preparer == reviewer:
        raise SystemExit("--resume: claims-review artifact requires distinct nonempty preparer_context and reviewer_context")
    distinctness = _observer_distinctness(data, verdict=verdict, prepared=prepared, target_version=target_version,
                                          evidence_commit=evidence_commit, repo_root=repo_root, run=run)
    # The evidence commit still carries only claims-review evidence.  The narrative is
    # the product of the review, so it lands in the same commit as the record that
    # names it -- and nothing else may ride along.
    allowed = sorted({normalized, *(x for x in [distinctness["review_artifact"]] if x)})
    if sorted(changed) != allowed:
        raise SystemExit(
            f"--resume: claims-review evidence commit must change only the supplied artifact and the "
            f"review_artifact it names; expected {allowed!r}, observed {sorted(changed)!r}"
        )
    return {"path": normalized, "sha256": blob_sha256(record.stdout), "prepared": prepared,
            "reviewer_context": reviewer, "verdict": verdict, "observer_distinctness": distinctness}
