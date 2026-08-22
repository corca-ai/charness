from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

MARKER = "charness-release-state:prepared-awaiting-claims-review"
#: v3 adds two REQUIRED fields on a `pass`: `review_scope` (which paths the
#: verdict covers) and `advisory_findings` (what it saw and waived). The bump is
#: honest rather than cosmetic -- a v2 record has no way to express either, so
#: silently accepting one would let a pre-split verdict masquerade as a scoped
#: one. There are no external v2 records to stay compatible with: every prior
#: record is historical and already published.
SCHEMA_VERSION = "charness.release.claims-review.v3"
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

from claims_review_scope import (  # noqa: E402
    assert_scope_is_declared,
    assert_scope_matches_release_delta,
)

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
# `signal` is the only operator-authored free text this floor accepts -- `verdict` and
# `kind` are closed enums and both paths go through `_review_relative_path` -- and it is
# now rendered into the PUBLISHED release record, which other gates parse.  A newline turns
# one field into arbitrary lines of that record.  Two measured consequences: a line
# reading `- target version: 9.9.9` makes `validate_current_pointer_freshness.py` refuse
# every post-publication push with "disagreeing target-version claims", and the prepared
# marker inside the signal makes `marker_at_commit` (a bare substring test) classify the
# finished release as an outstanding prepared stop forever.  Refused at the validator, so
# the record never reaches a tag, and flattened again at render time for records committed
# under an older build.
MAXIMUM_SIGNAL_BYTES = 600
# Every string some other surface substring-matches IN the release record. A field
# rendered into that document can satisfy any of them, which is one defect, not four --
# refusing the marker alone left the same shape standing in three more places. This list is
# the single owner of that rule, and it MUST grow whenever a new reader starts matching a
# sentinel in the record; the two closeout ones below are read from raw text with no
# code-stripping, so quoting the field is not a substitute.
RECORD_SENTINELS = (
    MARKER,
    # `publish_release_resume_closeout.py` proves carrier and final closeout identity by
    # asking whether these appear anywhere in the record.
    "carrier-pending-state-verification",
    "Issue closeout verification:",
    "charness-artifacts/probe/",
)


# The single owner of the `RECORD_SENTINELS` rule, because the comment above already CLAIMED
# to be one while the rendered PATH fields never reached it: free text was guarded and paths
# were not, and `:` and ` ` are legal filename characters. A critique artifact or claims
# record simply NAMED after the prepared-stop marker publishes a finished release whose
# record contains it, and `marker_at_commit` is a bare substring test -- so the prepare gate
# then refuses every later release over a stop that does not exist. Callers must refuse
# BEFORE mutation; every current one runs at gate time, so the repair is renaming a file
# rather than amending a published commit.
def assert_no_record_sentinel(value: str, field: str) -> None:
    """Refuse an operator-supplied value rendered verbatim into the release record."""
    for sentinel in RECORD_SENTINELS:
        if sentinel in value:
            raise SystemExit(
                f"{field} must not contain {sentinel!r}; it is rendered into the published "
                "release record, which other surfaces prove release state by "
                "substring-matching. Rename the file."
            )


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


def prepared_record(repo_root: Path, *, commit: str, record_path: str, run) -> dict[str, str] | None:
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
    parent = run(["git", "show", f"{parents.stdout.split()[0]}:{record_path}"], cwd=repo_root, check=False)
    if parent.returncode == 0 and MARKER in parent.stdout:
        return None
    # `path` is what `validate_claims_review` binds `release_record_path` against, so it
    # must be the DERIVED path too. Threading the three reads and leaving this one a
    # constant yields a floor that reads the right file and then demands the record name
    # the wrong one -- a refusal whose message points at neither.
    return {"commit": commit, "path": record_path, "sha256": blob_sha256(result.stdout)}


def _review_relative_path(value: object, field: str, suffix: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"--resume: claims-review {field} must be a repo-relative path")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SystemExit(f"--resume: claims-review {field} must be a normalized repo-relative path")
    normalized = path.as_posix()
    if not normalized.startswith(REVIEW_ROOT) or not normalized.endswith(suffix):
        raise SystemExit(f"--resume: claims-review {field} must be a {suffix} file under {REVIEW_ROOT}")
    assert_no_record_sentinel(normalized, f"--resume: claims-review {field}")
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


def _assert_signal_is_renderable(signal: str) -> None:
    """Refuse a signal that would stop being one field of the published release record.

    Refused HERE rather than sanitized at render time, because here is before the tag and
    the GitHub release exist. Both blocked shapes fire only on the post-publication
    commits, where the operator is already past the point of amending the record.
    """
    if any(character in signal for character in "\r\n") or any(ord(character) < 0x20 for character in signal):
        raise SystemExit(
            "--resume: claims-review `observer_distinctness.signal` must be a single line; it is "
            "rendered into the published release record, and a newline there injects arbitrary "
            "lines into a document other gates parse (a `target version:` line refuses every "
            "later push; the prepared-stop marker permanently reclassifies the finished release "
            "as an outstanding stop)."
        )
    for sentinel in RECORD_SENTINELS:
        if sentinel in signal:
            raise SystemExit(
                f"--resume: claims-review `observer_distinctness.signal` must not contain "
                f"{sentinel!r}. Another surface proves release state by matching that string as a "
                "SUBSTRING of the published record, so a signal carrying it lets this field answer "
                "a question it is not evidence for -- the marker one reclassifies a finished "
                "release as an unresolved prepared stop, the closeout ones let free text stand in "
                "for the closeout evidence they check."
            )
    if len(signal.encode("utf-8")) > MAXIMUM_SIGNAL_BYTES:
        raise SystemExit(
            f"--resume: claims-review `observer_distinctness.signal` exceeds {MAXIMUM_SIGNAL_BYTES} "
            "bytes. It names the concrete distinctness signal in the published record; the review's "
            "own narrative is where the reasoning belongs."
        )


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
    _assert_signal_is_renderable(signal)
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
    expected = {"schema_version": SCHEMA_VERSION, "prepared_commit": prepared["commit"],
                "release_record_path": prepared["path"], "release_record_sha256": prepared["sha256"],
                "target_version": target_version, "tag_name": tag_name}
    # Name the mismatching FIELDS. `release_record_path` is now derived from the adapter
    # rather than a constant an operator can copy out of the reference doc, and there is no
    # scaffolder for this record, so a bare "does not bind" left the one hand-written field
    # most likely to be wrong unnamed. The recovery is expensive enough to state: the
    # evidence commit must be the direct child of the prepared record, so the only repair is
    # to amend it in place.
    mismatched = {key: value for key, value in expected.items() if data.get(key) != value}
    if mismatched:
        detail = "; ".join(
            f"{key}: expected {value!r}, record carries {data.get(key)!r}" for key, value in sorted(mismatched.items())
        )
        raise SystemExit(
            "--resume: claims-review artifact does not bind the exact prepared release record -- "
            f"{detail}. Repair by AMENDING the evidence commit in place; a follow-on commit is not "
            "the direct child of the prepared record and is refused."
        )
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        raise SystemExit(f"--resume: claims-review `verdict` must be one of {list(VERDICTS)}")
    preparer, reviewer = data.get("preparer_context"), data.get("reviewer_context")
    if not isinstance(preparer, str) or not preparer.strip() or not isinstance(reviewer, str) or not reviewer.strip() or preparer == reviewer:
        raise SystemExit("--resume: claims-review artifact requires distinct nonempty preparer_context and reviewer_context")
    # AFTER the distinctness check. "Who reviewed this" is the more fundamental
    # question than "what did the verdict cover", and a record missing both
    # should be told about the observer first.
    assert_scope_is_declared(data, verdict=verdict)
    if verdict == "pass":
        assert_scope_matches_release_delta(repo_root, data, prepared=prepared, run=run)
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
            "reviewer_context": reviewer, "verdict": verdict, "observer_distinctness": distinctness,
            "review_scope": data.get("review_scope"),
            "advisory_findings": data.get("advisory_findings") or []}
