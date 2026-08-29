"""The release record's quality sentence must be bound to a result, not a default.

`write_current_artifact` reads `version_drift_check`, `bump_rationale`,
`claims_review` and a dozen more fields from `payload`. `quality_status` alone was
a passthrough with a hardcoded default, so any writer that did not name it
rendered `passed before publish` whether the gate ran, failed, or never started.

This is the same defect `version_drift_lines` was already repaired for, on the
line directly beneath it in the rendered record -- its docstring reads: "the
record read `current_release.py reported no version drift` identically whether the
check ran, did not run, or found drift."

It took THREE attempts to repair, which is why it has a test:

1. stamp the payload and forward it at the commit-time writer -- the
   fresh-checkout amend re-rendered from the default;
2. add the amend writer via a shared helper -- a claims round then found
   `commit_post_publish_artifact`, the write that produces the record actually
   pushed to `main`, still rendering the literal;
3. read it from the payload AT THE OWNER, so every writer is correct by
   construction.

There are five writers across four modules. Patching call sites was always going
to lose that race, and these tests pin the owner rather than the callers.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from .seeding_support import load_module
from .support import ROOT

_RELEASE = ROOT / "skills" / "public" / "release" / "scripts"


def _load(name: str):
    return load_module(name, _RELEASE / f"{name}.py")


@pytest.fixture(scope="module")
def artifact():
    return _load("publish_release_artifact")


def _rendered(artifact, monkeypatch, payload_extra: dict, **kwargs) -> dict:
    """Call the owner and capture what it forwards to the renderer."""
    seen: dict = {}
    monkeypatch.setattr(
        artifact, "write_release_artifact", lambda *a, **kw: seen.update(kw) or "path.md"
    )
    payload = {
        "previous_version": "6.2.2",
        "target_version": "6.3.0",
        "remote": "origin",
        "branch": "main",
        "tag_name": "v6.3.0",
        **payload_extra,
    }
    adapter = {
        "output_dir": "charness-artifacts/release",
        "package_id": "charness",
        "quality_command": "./scripts/run-quality.sh --release",
        "update_instructions": [],
    }
    artifact.write_current_artifact(Path("."), adapter, payload, **kwargs)
    return seen


def test_the_stamped_result_reaches_a_writer_that_never_names_it(artifact, monkeypatch) -> None:
    """THE regression. Three of the five writers pass no `quality_status`, and one
    of them produces the record pushed to `main`."""
    seen = _rendered(artifact, monkeypatch, {"quality_status": "exited 0 in 181.0s"})

    assert seen["quality_status"] == "exited 0 in 181.0s"


def test_an_explicit_argument_still_wins(artifact, monkeypatch) -> None:
    """One caller legitimately says the gate is QUEUED, before it has run. The
    payload must not overwrite a caller that knows better."""
    seen = _rendered(
        artifact, monkeypatch,
        {"quality_status": "exited 0 in 181.0s"},
        quality_status="is queued for this publish attempt",
    )

    assert seen["quality_status"] == "is queued for this publish attempt"


def test_the_default_survives_when_nothing_measured_it(artifact, monkeypatch) -> None:
    """A payload with no stamp means the gate never ran under this helper. The
    default's own wording is the honest one there, so it is preserved rather than
    replaced with a fabricated measurement."""
    seen = _rendered(artifact, monkeypatch, {})

    assert seen["quality_status"] == "passed before publish"


def test_no_writer_hardcodes_the_literal_at_a_call_site(artifact) -> None:
    """A structural pin, because this defect recurred by ADDING a writer.

    The literal belongs in exactly one place -- the owner's fallback. A call site
    that spells it out is a fourth copy waiting to drift, and the previous two
    repairs both worked by adding call-site plumbing that the next new writer
    silently skipped.
    """
    offenders = []
    for path in sorted(_RELEASE.glob("publish_release*.py")):
        if path.name == "publish_release_artifact.py":
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            # An assignment or keyword argument, not a comment. Comments quoting
            # the literal are how the repair explains itself, and refusing those
            # would push the reasoning out of the file that needs it.
            if line.lstrip().startswith("#"):
                continue
            if "quality_status" in line and "passed before publish" in line:
                offenders.append(f"{path.name}:{number}")

    assert offenders == [], (
        "the `passed before publish` literal must live only in the owner's "
        f"fallback; found call-site copies at {offenders}"
    )


def test_the_stage_phrase_is_not_a_literal_in_the_owner() -> None:
    """M1, found by claims round 4.

    The repair that killed the `passed before publish` literal wrote a NEW one
    inside its replacement sentence: ``at `post-bump, pre-commit` ``. That is true
    on the prepare lane and false on the resume/claims lane, which runs the same
    gate after the prepared commit exists and without bumping -- and whose payload
    is what gets rewritten and pushed to `main`. A phrase that renders identically
    whether it is true or not is the exact class this module exists to refuse.
    """
    source = (_RELEASE / "publish_release_common.py").read_text(encoding="utf-8")
    body = source.split("def run_pre_push_quality_gates", 1)[1]
    stamp = body.split('payload["quality_status"] = (', 1)[1].split(")", 1)[0]

    assert "post-bump" not in stamp, (
        "the stage belongs to the CALLER -- each lane runs this gate at a different "
        f"point. Found a hardcoded stage in the owner's stamp: {stamp.strip()}"
    )
    assert "{stage}" in stamp, "the stamp must interpolate the caller's stage"


def test_each_lane_states_its_own_true_stage() -> None:
    """`stage` is required, so a new lane cannot inherit another lane's phrase."""
    common = (_RELEASE / "publish_release_common.py").read_text(encoding="utf-8")
    signature = common.split("def run_pre_push_quality_gates", 1)[1].split(":\n", 1)[0]
    assert "stage: str" in signature and "stage: str =" not in signature, (
        f"stage must be required, not defaulted: {signature}"
    )

    lanes = {
        "publish_release_execute.py": "post-bump, pre-commit",
        "publish_release_resume_publish.py": "post-claims-review, pre-push",
    }
    for name, expected in lanes.items():
        text = (_RELEASE / name).read_text(encoding="utf-8")
        assert f'stage="{expected}"' in text, f"{name} must state stage={expected!r}"
