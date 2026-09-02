"""Date-channel coherence for quality records (#620).

A quality record whose `Date:` header disagrees with its own filename date is a record
that was overwritten in place: the scaffold writes a FRESH date into the STALE path the
current pointer resolves to, so a new review lands on top of the previous review's dated
file with no rename and no error. These tests own the refusal, its exemptions, and the
one measured grandfather — and they guard the two ways a well-meaning edit would put the
hole back: reading the pointer's own name instead of its target, and widening the rule to
a +/-1 day tolerance (the #620 instance is itself exactly +1 day).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module
from tests.test_quality_artifact import seed_repo, valid_quality_artifact

from .support import ROOT

_validate_quality_artifact = import_repo_module(__file__, "scripts.validate_quality_artifact")
ValidationError = _validate_quality_artifact.ValidationError

RUNTIME_SOURCE = (
    "structured metrics from `.charness/quality/runtime-signals.json`"
    " rendered by `render_runtime_summary.py` via `scripts/gates_support/record_quality_runtime.py`."
)
QUALITY_FAMILY = ROOT / "charness-artifacts" / "quality"


def dated_record_repo(tmp_path: Path, *, filename: str, body_date: str, as_pointer_symlink: bool = False) -> Path:
    """A seeded quality repo whose record lives at `filename` and records `body_date`.

    `seed_repo` writes the artifact to a real-file `latest.md`; the dated cases move it
    to its own name, and the pointer case replaces `latest.md` with the symlink the repo
    actually ships so the read-through behavior is exercised, not asserted about.
    """
    repo = seed_repo(tmp_path, valid_quality_artifact(runtime_source=RUNTIME_SOURCE).replace("Date: 2026-04-20", f"Date: {body_date}"))
    pointer = repo / "charness-artifacts" / "quality" / "latest.md"
    if filename != "latest.md":
        record = pointer.parent / filename
        record.write_text(pointer.read_text(encoding="utf-8"), encoding="utf-8")
        pointer.unlink()
        if as_pointer_symlink:
            pointer.symlink_to(filename)
    return repo


def validate(repo: Path, relative: str) -> None:
    _validate_quality_artifact.validate_quality_artifact(
        repo / "charness-artifacts" / "quality" / relative, repo_root=repo
    )


def test_a_fresh_date_written_into_a_stale_dated_record_is_refused(tmp_path: Path) -> None:
    """The #620 shape: the 2026-08-14 review landed in the 2026-08-13 record's file."""
    repo = dated_record_repo(tmp_path, filename="2026-08-13-issue-616-applied-lifecycle.md", body_date="2026-08-14")
    with pytest.raises(ValidationError, match="overwritten in place"):
        validate(repo, "2026-08-13-issue-616-applied-lifecycle.md")


def test_a_coherent_dated_record_passes(tmp_path: Path) -> None:
    repo = dated_record_repo(tmp_path, filename="2026-08-14-current-contract-cleanup.md", body_date="2026-08-14")
    validate(repo, "2026-08-14-current-contract-cleanup.md")


@pytest.mark.parametrize("body_date", ["2026-08-14", "2026-08-12", "2026-09-13"])
def test_a_near_miss_is_refused_rather_than_tolerated(tmp_path: Path, body_date: str) -> None:
    """No +/-1 day slack. A tolerance would be a hole exactly the size of #620."""
    repo = dated_record_repo(tmp_path, filename="2026-08-13-record.md", body_date=body_date)
    with pytest.raises(ValidationError, match="overwritten in place"):
        validate(repo, "2026-08-13-record.md")


def test_the_current_pointer_symlink_is_read_through_to_its_dated_target(tmp_path: Path) -> None:
    """`run-quality.sh` validates the pointer, and #620 was written through the pointer.

    Reading the LINK's name would exempt the repo's own broad gate run from the rule and
    leave only the changed-path preflight to catch an overwrite.
    """
    repo = dated_record_repo(
        tmp_path, filename="2026-08-13-issue-616-applied-lifecycle.md", body_date="2026-08-14", as_pointer_symlink=True
    )
    with pytest.raises(ValidationError, match="overwritten in place"):
        validate(repo, "latest.md")


def test_a_current_pointer_that_is_a_real_file_keeps_its_own_date(tmp_path: Path) -> None:
    """`charness-artifacts/quality/sloc-inventory/latest.md` carries `Date: 2026-05-04` by design."""
    repo = dated_record_repo(tmp_path, filename="latest.md", body_date="2026-05-04")
    validate(repo, "latest.md")


def test_an_undated_filename_has_no_second_channel_to_disagree_with(tmp_path: Path) -> None:
    repo = dated_record_repo(tmp_path, filename="draft-quality-review.md", body_date="2026-08-14")
    validate(repo, "draft-quality-review.md")


def test_preamble_date_stops_at_the_first_heading() -> None:
    """A `Date:` line inside the body is prose, not the artifact's date channel."""
    assert _validate_quality_artifact.preamble_date(["# Quality Review", "Date: 2026-08-14"]) == "2026-08-14"
    assert _validate_quality_artifact.preamble_date(["# Quality Review", "## Scope", "Date: 2026-08-14"]) is None


def test_the_grandfather_is_one_measured_disagreement_not_a_free_slot(tmp_path: Path) -> None:
    """The exemption is keyed by path AND by the exact date pair measured on that path.

    Keyed by path alone it would make the named record permanently overwritable: a second
    overwrite would carry a third date and pass. It also must not survive the repair — the
    path assertion fails loudly once the record is refiled and the entry should be deleted.
    """
    grandfathered = _validate_quality_artifact.DATE_COHERENCE_GRANDFATHERED
    assert grandfathered == {
        "charness-artifacts/quality/2026-06-25-skill-ergonomics-yaml-summary-quality-review.md": (
            "2026-06-25",
            "2026-06-26",
        )
    }
    for relative in grandfathered:
        assert (ROOT / relative).is_file(), f"grandfathered path no longer exists: {relative}"
    repo = dated_record_repo(
        tmp_path, filename="2026-06-25-skill-ergonomics-yaml-summary-quality-review.md", body_date="2026-07-01"
    )
    with pytest.raises(ValidationError, match="overwritten in place"):
        validate(repo, "2026-06-25-skill-ergonomics-yaml-summary-quality-review.md")


def test_the_checked_in_quality_family_has_no_ungrandfathered_date_disagreement() -> None:
    """The corpus sweep no call site performs.

    `run-quality.sh` validates only the current pointer and the surface preflight only the
    changed paths, so nothing else re-reads the ~130 retained quality records. Without this
    the rule would protect new writes while a past overwrite sat undetected — which is
    exactly how the 2026-06-25 record stayed lost for seven weeks.
    """
    disagreements = []
    for record in sorted(QUALITY_FAMILY.rglob("*.md")):
        if not re.match(r"^\d{4}-\d{2}-\d{2}-", record.name):
            continue
        try:
            _validate_quality_artifact.validate_date_channel_coherence(
                record, record.read_text(encoding="utf-8").splitlines(), ROOT
            )
        except ValidationError as exc:
            disagreements.append(str(exc))
    assert disagreements == []
