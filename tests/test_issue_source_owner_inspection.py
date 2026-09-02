"""The owner-inspection half of the issue source freeze, after `#562` retired its pin.

A separate module from `test_issue_source_freeze.py` on purpose. That file owns the
SOURCE half — re-derivation from raw bytes, pagination completeness, tamper refusal — and
was at 792 of 800 gated lines when these tests were written, so appending would have
traded a length-gate block for a module boundary the subject already wanted. The split is
along the same seam `#562` drew: content-pinned external source over there, unpinned
locator provenance here.

What these pin is the SHAPE OF THE REMOVAL, which is the part a future session is most
likely to get wrong: the pin must stay gone, its retirement must be legible to whoever
holds an old artifact, and the checks it was the sole carrier of must not have gone with
it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.issue.issue_source_freeze_lib import (
    INSPECTION_SCHEMA,
    FreezeError,
    load_inspection,
    verify_inspection,
    verify_locators,
)
from scripts.issue.validate_issue_source_freeze import preflight, run_refreeze, stamp_inspection
from tests.test_issue_source_freeze import (
    FREEZE_REL,
    SNAPSHOT_REL,
    _build_world,
)

INSPECTION_REL = "spec/inspection.json"


def _write_inspection(tmp_path: Path, **overrides) -> dict:
    """A minimal v2 inspection whose single locator resolves, plus its real file."""
    (tmp_path / "owner.py").write_text("# inspected owner\n", encoding="utf-8")
    payload = {
        "schema": INSPECTION_SCHEMA,
        "issues": [514],
        "locators": [{"role": "owner", "path": "owner.py", "note": "n"}],
        "inspection_identity": "",
    }
    payload.update(overrides)
    path = tmp_path / INSPECTION_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def test_a_noncurrent_schema_is_refused(tmp_path: Path) -> None:
    """Only the exact current schema is accepted."""
    _write_inspection(tmp_path, schema="issue-source-owner-inspection/v3")

    with pytest.raises(FreezeError) as excinfo:
        load_inspection(tmp_path, INSPECTION_REL)

    assert excinfo.value.code == "wrong_schema"
    assert INSPECTION_SCHEMA in excinfo.value.detail


def test_the_refreeze_preflight_refuses_a_bad_locator_before_any_write(tmp_path: Path) -> None:
    """`preflight`'s own contract, pinned at `preflight`.

    In the refreeze lane the preflight deliberately does NOT enforce the inspection identity
    — that is the condition refreeze repairs — so the per-locator rules are the only
    inspection teeth it has left. `stamp_inspection` re-checks them a moment later, which
    means a mutant deleting them from the preflight survives every end-to-end test. A rule
    whose only proof is another function's redundant copy is not proven, so this asserts the
    preflight refuses on its own.
    """
    _build_world(tmp_path)
    inspection = json.loads((tmp_path / INSPECTION_REL).read_text(encoding="utf-8"))
    inspection["locators"][0]["sha256"] = "0" * 64
    (tmp_path / INSPECTION_REL).write_text(json.dumps(inspection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(FreezeError) as excinfo:
        preflight(tmp_path, SNAPSHOT_REL, INSPECTION_REL, [514, 515, 518], require_inspection_identity=False)

    assert excinfo.value.code == "retired_locator_pin"


def test_the_writer_refuses_a_retired_pin_before_it_writes(tmp_path: Path) -> None:
    """The writer must hold the reader's rules, and hold them BEFORE writing.

    Two failures in one shape. A `stamp-inspection` that refused less than `validate`
    exited 0 on an artifact `validate` rejects — a tool reporting good order on a dead
    claim. And because `refreeze` stamps before it freezes, a post-write check left a
    command that REFUSED having already rewritten the file, breaking the atomicity that
    is `refreeze`'s entire justification.
    """
    _write_inspection(
        tmp_path,
        locators=[{"role": "owner", "path": "owner.py", "note": "n", "sha256": "0" * 64}],
    )
    before = (tmp_path / INSPECTION_REL).read_text(encoding="utf-8")

    with pytest.raises(FreezeError) as excinfo:
        stamp_inspection(tmp_path, INSPECTION_REL)

    assert excinfo.value.code == "retired_locator_pin"
    assert "Remedy" in excinfo.value.detail
    assert (tmp_path / INSPECTION_REL).read_text(encoding="utf-8") == before, (
        "a refused stamp must not have rewritten the artifact it refused"
    )


@pytest.mark.parametrize("escape", ["../outside.py", "/etc/hostname"])
def test_a_locator_pointing_outside_the_repo_is_refused(tmp_path: Path, escape: str) -> None:
    """A locator path is untrusted input, exactly like a raw-response path.

    It arrives from the artifact under review. `repo_root / "/etc/hostname"` is
    `/etc/hostname`, and `../` climbs out, so existence alone would let a freeze go green
    asserting inspection of a file nobody in this repo can review. The source half already
    contains its paths for this reason; the surviving locator check now does too.
    """
    outside = tmp_path.parent / "outside.py"
    outside.write_text("# not reviewable from inside the repo\n", encoding="utf-8")
    payload = _write_inspection(tmp_path, locators=[{"role": "owner", "path": escape, "note": "n"}])

    with pytest.raises(FreezeError) as excinfo:
        verify_locators(tmp_path, payload)

    assert excinfo.value.code == "locator_escape"


@pytest.mark.parametrize("missing", ["path", "role"])
def test_a_locator_missing_a_required_key_is_a_typed_refusal_not_a_keyerror(
    tmp_path: Path, missing: str
) -> None:
    """Every other malformed-artifact case here is a typed refusal, and a bare `KeyError`
    escapes the CLI's refusal rendering — so a gate reading the exit code and the JSON
    body gets a traceback instead of a machine-readable cause.

    BOTH keys are parametrized because guarding only `path` is how this defect survived its
    own first repair: `inspection_identity` reads `role` too, so a role-less locator passed
    the guard and raised `KeyError: 'role'` out of every subcommand.
    """
    locator = {"path": "owner.py", "role": "owner", "note": "n"}
    del locator[missing]
    payload = _write_inspection(tmp_path, locators=[locator])

    with pytest.raises(FreezeError) as excinfo:
        verify_locators(tmp_path, payload)

    assert excinfo.value.code == "malformed_locator"
    assert missing in excinfo.value.detail


def test_the_writer_refuses_an_escaping_locator_through_the_real_entrypoint(tmp_path: Path) -> None:
    """The escape rule proven through a COMMAND, not only at the shared function.

    A rule pinned only where it is defined is pinned against being edited, not against
    being unreachable: dropping the writer's call to `verify_locators` would leave the
    function-level test green while `stamp-inspection` happily stamped an identity over a
    path pointing outside the repo.
    """
    _write_inspection(tmp_path, locators=[{"role": "owner", "path": "/etc/hostname", "note": "n"}])

    with pytest.raises(FreezeError) as excinfo:
        stamp_inspection(tmp_path, INSPECTION_REL)

    assert excinfo.value.code == "locator_escape"


def test_a_refusing_refreeze_does_not_mutate_a_single_checked_in_artifact(tmp_path: Path) -> None:
    """The partial-write CLASS, not the one instance round 1 found.

    Fixing `stamp_inspection` to check before its own write left the SEQUENCE untouched:
    `refreeze` writes the inspection, then the freeze receipt, then the crosswalk, and only
    then validates. Demonstrated against the real repo before the repair —
    `refreeze --require-issues 514 515` mutated all three checked-in artifacts, including
    the closeout-authorization crosswalk, and THEN raised `freeze_issue_set_mismatch`.

    A refusing command must leave the repo exactly as it found it, so this asserts bytes on
    every artifact `refreeze` can write, not just the exit code.

    The stale identity below is what gives this test teeth, and its absence is why the first
    version of it passed against a mutant with the preflight deleted: `_build_world` leaves
    the identity already correct, so `stamp_inspection` rewrote byte-identical content and
    the "unchanged" assertion held while the write really had happened. A partial-write test
    whose write is invisible proves nothing.
    """
    _build_world(tmp_path)
    crosswalk_rel = "spec/crosswalk.json"
    (tmp_path / crosswalk_rel).write_text('{"schema": "evidence-boundary-crosswalk/v1"}\n', encoding="utf-8")
    stale = json.loads((tmp_path / INSPECTION_REL).read_text(encoding="utf-8"))
    stale["inspection_identity"] = "0" * 64
    (tmp_path / INSPECTION_REL).write_text(json.dumps(stale, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    watched = [INSPECTION_REL, FREEZE_REL, crosswalk_rel]
    before = {rel: (tmp_path / rel).read_bytes() for rel in watched}

    with pytest.raises(FreezeError) as excinfo:
        run_refreeze(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, [514, 515], crosswalk_rel)

    assert excinfo.value.code == "freeze_issue_set_mismatch"
    for rel in watched:
        assert (tmp_path / rel).read_bytes() == before[rel], f"a refusing refreeze rewrote {rel}"


def test_refreeze_still_repairs_a_stale_identity_which_is_its_whole_purpose(tmp_path: Path) -> None:
    """The preflight must not refuse the condition `refreeze` exists to fix.

    A stale `inspection_identity` is `refreeze`'s INPUT, so a preflight that enforced the
    identity would refuse every legitimate refreeze — turning a partial-write fix into a
    total outage of the command. The per-locator rules still run, because a retired pin or
    an escaping path must never be laundered into a freshly stamped identity.
    """
    _build_world(tmp_path)
    crosswalk_rel = "spec/crosswalk.json"
    (tmp_path / crosswalk_rel).write_text('{"schema": "evidence-boundary-crosswalk/v1"}\n', encoding="utf-8")
    inspection = json.loads((tmp_path / INSPECTION_REL).read_text(encoding="utf-8"))
    inspection["inspection_identity"] = "0" * 64
    (tmp_path / INSPECTION_REL).write_text(json.dumps(inspection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    payload = run_refreeze(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, [514, 515, 518], crosswalk_rel)

    assert payload["ok"] is True
    assert payload["validated"]["ok"] is True
    assert payload["inspection_identity"] != "0" * 64


def test_the_artifacts_prose_is_bound_by_the_inspection_identity(tmp_path: Path) -> None:
    """The blocker's RECURRENCE, not just the blocker.

    Round 1 found `purpose` asserting a content pin that no longer existed. Rewriting it
    moved no identity, because `purpose` and `non_claims` were outside the identity — the
    same gap that let the false claim stand for a whole schema generation with every gate
    green. Prose on an authorization artifact that nothing binds is a declaration without
    corroboration, so it is bound now, and this is what keeps it bound.
    """
    _build_world(tmp_path)
    for field, value in (("purpose", "a silently rewritten purpose"), ("non_claims", ["silently added"])):
        inspection = json.loads((tmp_path / INSPECTION_REL).read_text(encoding="utf-8"))
        inspection[field] = value
        (tmp_path / INSPECTION_REL).write_text(
            json.dumps(inspection, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        with pytest.raises(FreezeError) as excinfo:
            verify_inspection(tmp_path, json.loads((tmp_path / INSPECTION_REL).read_text(encoding="utf-8")))

        assert excinfo.value.code == "inspection_identity_mismatch", field


def test_an_inspection_with_no_locators_is_not_an_inspection(tmp_path: Path) -> None:
    """`#562` narrowed what the inspection claims; it did not make an EMPTY one claim it.
    A zero-locator inspection would satisfy every surviving per-locator rule vacuously."""
    payload = _write_inspection(tmp_path, locators=[])

    with pytest.raises(FreezeError) as excinfo:
        verify_locators(tmp_path, payload)

    assert excinfo.value.code == "empty_inspection"
