"""The announcement preflight refuses an unhonored declaration instead of clearing a
delivery it exists to block.

Rows 24-25 of slice 5, and `preflight_sources` is the sharpest publish-boundary reading in
the slice: its whole job is to stop a delivery that would claim an in-progress source is
finished, and an unhonored declaration does not degrade that — it INVERTS it.

Measured at `254fa5c44`: a repo declaring one `in_progress_sources` entry got
`delivery_blocked: false`, `ok: true`, `surfaces: []`, exit 0 — clear to announce. The same
repo at a speakable version gets `delivery_blocked: true`, `ok: false`, exit 2.

The mechanism is worth naming because it is why the flip is total rather than partial:
`announcement_preflight_lib.preflight_sources` short-circuits to ok/unblocked the moment
`in_progress_sources` is empty, and an unhonored declaration is indistinguishable there
from a repo that declared none.

`record_announcement`'s guard sits BEFORE its `except Exception` fallback, deliberately.
That fallback is correct for a resolution FAILURE — it records `adapter_resolved: False`
and keeps the disagreement typed and visible. It is wrong for a resolution that SUCCEEDED
while honoring nothing, because `requires_delivery_kind_agreement` then compares the
recorded kind against a charness default.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .support import ROOT, run_script

PREFLIGHT = "skills/public/announcement/scripts/preflight_sources.py"
RECORD = "skills/public/announcement/scripts/record_announcement.py"

# `in_progress_sources` entries are MAPPINGS with a `kind`, not strings — an earlier
# stimulus in this slice used a bare string and the control could not fail, because
# `_validate_in_progress_sources` rejected it and the empty list took the short-circuit.
DECLARED = """version: {v}
repo: demo
delivery_kind: release-notes
release_notes_path: docs/mine-notes.md
in_progress_sources:
  - kind: path
    path: docs/pending-migration.md
    summary: a migration the announcement must not claim finished
"""


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "announcement-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(rel: str, repo: Path, *args: str) -> subprocess.CompletedProcess:
    return run_script(rel, "--repo-root", str(repo), *args)


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_preflight_refuses_rather_than_clearing_the_delivery(
    tmp_path: Path, version: str
) -> None:
    result = _run(PREFLIGHT, _repo(tmp_path, DECLARED.format(v=version)))
    assert result.returncode != 0, result.stdout
    assert "announcement-adapter.yaml" in result.stderr, result.stderr
    if version == "9":
        assert "does not speak" in result.stderr, result.stderr
    else:
        # BOTH doors render a verdict now. This assertion used to expect a raw
        # `Traceback`, because announcement was one of the six resolvers in #673 that call
        # `adapter_lib.load_yaml_file` bare. A bounded review measured what that cost on
        # THIS surface -- a publish gate cleared at exit 0 by an over-indented block -- so
        # the resolver was repaired ahead of #673 and the parse door became reachable.
        assert "could not be parsed" in result.stderr, result.stderr
        assert "Traceback" not in result.stderr, result.stderr
    # The cleared verdict must not be reported alongside the refusal.
    assert "delivery_blocked: false" not in result.stdout
    assert "ok: true" not in result.stdout


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_recorder_refuses_before_its_own_fallback(tmp_path: Path, version: str) -> None:
    """BOTH DOORS REFUSE. An earlier version of this test asserted the opposite and
    argued the asymmetry was CORRECT — that a refused parse should be absorbed by the
    module's `except Exception` and recorded as `adapter_resolved: false`, "a typed,
    visible signal". A bounded review refuted both halves and this docstring records it
    rather than quietly flipping.

    The claim was wrong on the harm: the reason it cited —
    `requires_delivery_kind_agreement` comparing the recorded kind against a charness
    default — only fires for `delivery_kind: human-backend`, and the stimulus declared
    `release-notes`. So the published control could not exercise the harm it named.

    And it was wrong on the outcome. Measured with the harm actually in play
    (`delivery_kind: human-backend`, `--delivery-kind none`): at `version: 1` the run
    raised `fail_delivery_kind_mismatch`; at `version: !!int 9` it exited 0 and appended a
    DURABLE RECORD. One token converted a hard refusal on the self-attestation bypass into
    a written record.

    "Typed and visible" was also not enforcement: no production surface reads
    `adapter_resolved` — only tests and one prose line.
    """
    repo = _repo(tmp_path, DECLARED.format(v=version))
    result = _run(
        RECORD, repo, "--head-commit", "deadbeef", "--delivery-kind", "release-notes",
    )
    assert result.returncode != 0, result.stdout
    assert "announcement-adapter.yaml" in result.stderr


def test_the_delivery_kind_bypass_the_review_found_is_closed(tmp_path: Path) -> None:
    """The measurement the earlier control could not make.

    `requires_delivery_kind_agreement` fires only for `human-backend`, so this is the
    adapter that puts the named harm in play. Before the resolver repair, `!!int 9` here
    exited 0 with a durable record while `version: 1` refused.
    """
    adapter = """version: {v}
repo: demo
delivery_kind: human-backend
post_command_template: slack-post "{{body}}"
delivery_capability: slack-post
"""
    for version in ("9", "!!int 9"):
        repo = _repo(tmp_path / version.replace("!", "x").replace(" ", ""), adapter.format(v=version))
        result = _run(
            RECORD, repo, "--head-commit", "deadbeef", "--delivery-kind", "none",
        )
        assert result.returncode != 0, (version, result.stdout)
        assert not (repo / ".charness" / "announcement" / "announcements.jsonl").exists(), version

    # The polarity control: a speakable adapter still refuses the understated kind, by its
    # OWN gate rather than by the version guard.
    repo = _repo(tmp_path / "speakable", adapter.format(v="1"))
    result = _run(RECORD, repo, "--head-commit", "deadbeef", "--delivery-kind", "none")
    assert result.returncode != 0, result.stdout
    assert "human-backend" in (result.stdout + result.stderr)


def test_a_speakable_version_still_blocks_the_delivery(tmp_path: Path) -> None:
    """The polarity control, and the one that carries the whole claim.

    `delivery_blocked: true` at exit 2 is what the gate is FOR. A control asserting only
    exit 0 would be satisfied by a preflight that blocks nothing, which is the base
    behavior this row repairs.
    """
    result = _run(PREFLIGHT, _repo(tmp_path, DECLARED.format(v="1")))
    assert result.returncode == 2, result.stdout
    assert "delivery_blocked: true" in result.stdout
    assert "ok: false" in result.stdout
    assert "docs/pending-migration.md" in result.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    """Opt-in surface. A repo that declared no in-progress sources is genuinely clear to
    deliver, which is the answer that was wrong only over a repo that declared some."""
    result = _run(PREFLIGHT, _repo(tmp_path, None))
    assert result.returncode == 0, result.stderr
    assert "delivery_blocked: false" in result.stdout


def test_an_ordinary_invalid_field_is_not_refused(tmp_path: Path) -> None:
    """`valid: false` from an unrelated bad field must NOT refuse, and the declared
    sources must still block — asserting both halves."""
    adapter = DECLARED.format(v="1").replace("repo: demo", "repo: demo\npreset_version: 3")
    result = _run(PREFLIGHT, _repo(tmp_path, adapter))
    assert result.returncode == 2, result.stdout
    assert "delivery_blocked: true" in result.stdout


@pytest.mark.parametrize(
    ("label", "adapter", "expect"),
    [
        (
            "over-indented block",
            "version: 1\ndelivery_kind: release-notes\n  in_progress_sources:\n    - kind: path\n      path: docs/p.md\n",
            "could not interpret",
        ),
        (
            "validated-away entry",
            "version: 1\ndelivery_kind: release-notes\nin_progress_sources:\n  - kind: Path\n    path: docs/p.md\n",
            "did not honor",
        ),
    ],
)
def test_a_declaration_that_never_reaches_the_gate_refuses(
    tmp_path: Path, label: str, adapter: str, expect: str
) -> None:
    """Two live exit-0 bypasses of this publish gate, both found by a bounded review and
    both closed. Neither needed a version to be touched.

    ONE: `announcement_adapter_lib` called `adapter_lib.load_yaml_file` bare, discarding
    the uninterpreted-line sink, so an over-indented `in_progress_sources:` block left
    `errors: []`, `valid: true`, no warning — and `delivery_blocked: false / ok: true` at
    exit 0. Two of `adapter_version_verdict`'s three doors were structurally dead for this
    adapter. Repaired by arming the sink, ahead of #673, because the bypass is a publish
    boundary rather than a message shape.

    TWO: `_validate_in_progress_sources` uses `continue` on every rejected entry, so ONE
    bad entry empties the list and the empty list takes the same short-circuit. `kind:
    Path` — one capital letter — cleared the gate. Repaired by reading `field_state`,
    which already carried "the repo wrote this key", against the validated result.

    The slice had ALREADY documented the second input, as a probe-authoring mistake, in
    this file's own `DECLARED` comment — without noticing it was a live bypass of the gate
    being repaired.
    """
    result = _run(PREFLIGHT, _repo(tmp_path, adapter))
    assert result.returncode == 1, result.stdout
    assert expect in result.stderr, result.stderr
    assert "delivery_blocked: false" not in result.stdout


def test_a_valid_entry_still_blocks_and_no_entry_still_clears(tmp_path: Path) -> None:
    """The polarity controls for the two repairs above. Without these, a preflight that
    refuses every adapter passes both tests."""
    blocked = _run(PREFLIGHT, _repo(tmp_path / "a", DECLARED.format(v="1")))
    assert blocked.returncode == 2, blocked.stdout
    assert "delivery_blocked: true" in blocked.stdout

    cleared = _run(
        PREFLIGHT,
        _repo(tmp_path / "b", "version: 1\nrepo: demo\ndelivery_kind: release-notes\n"),
    )
    assert cleared.returncode == 0, cleared.stderr
    assert "delivery_blocked: false" in cleared.stdout


def test_a_partially_lost_declaration_also_refuses(tmp_path: Path) -> None:
    """The bypass the FIRST fix did not close, found by a round-2 bounded review.

    That fix asked whether the validated list ended up EMPTY. `_validate_in_progress_sources`
    drops rejected entries with `continue`, so with two entries — one `kind: Path`, one
    valid — the list is non-empty, the guard never fired, and the preflight cleared the
    delivery at exit 0 over a source the repo declared and this reader dropped.

    The witness is now the ERROR PREFIX, not the emptiness: every message that validator
    emits starts with `in_progress_sources`, so "an entry the repo wrote did not survive"
    is complete. The emptiness arm stays as the second half, because a declaration can be
    lost without an error when the value is not a list at all.
    """
    repo = _repo(
        tmp_path,
        "version: 1\nrepo: demo\ndelivery_kind: release-notes\n"
        "in_progress_sources:\n"
        "  - kind: Path\n    path: docs/pending-migration.md\n"
        "  - kind: path\n    path: docs/done.md\n",
    )
    draft = repo / "charness-artifacts" / "announcement"
    draft.mkdir(parents=True, exist_ok=True)
    (draft / "latest.md").write_text(
        "# Announcement\n\n## Source surfaces\n- path docs/done.md collected\n", encoding="utf-8"
    )
    result = _run(PREFLIGHT, repo)
    assert result.returncode == 1, result.stdout
    assert "did not honor" in result.stderr, result.stderr
    assert "delivery_blocked: false" not in result.stdout


def test_an_explicitly_empty_source_list_still_clears(tmp_path: Path) -> None:
    """The input EVERY scaffolded repo has, and which the first control missed.

    `init_adapter` writes `in_progress_sources: []`, and the shipped `adapter.example.yaml`
    carries it too. That parses to `[]`, which `list_field_state` calls `explicit-empty`
    rather than `configured`, so the guard correctly does not fire. The earlier control
    omitted the key entirely — a different state — so a regression to
    `if "in_progress_sources" in raw_data` would have hard-stopped the publish preflight of
    every scaffolded repo with a green suite.
    """
    result = _run(
        PREFLIGHT,
        _repo(tmp_path, "version: 1\nrepo: demo\ndelivery_kind: release-notes\nin_progress_sources: []\n"),
    )
    assert result.returncode == 0, result.stderr
    assert "delivery_blocked: false" in result.stdout


def test_the_parse_arm_carries_every_key_the_success_arm_does(tmp_path: Path) -> None:
    """The `KeyError` a round-2 bounded review found waiting.

    The parse-failure arm was hand-built with nine keys where the other two carried
    fifteen, omitting `artifact_path` — which `preflight_sources` indexes directly.
    Unreachable only because the version guard refuses first on exactly that input; any
    reordering or unguarded caller turns a refusal into a traceback. All three arms are now
    built by one `_payload`.
    """
    import sys as _sys

    _sys.path.insert(0, str(ROOT))
    from scripts.announcement_adapter_lib import load_announcement_adapter

    parse_repo = _repo(tmp_path / "p", "version: !!int 9\nrepo: demo\n")
    ok_repo = _repo(tmp_path / "o", "version: 1\nrepo: demo\n")
    assert set(load_announcement_adapter(parse_repo)) == set(load_announcement_adapter(ok_repo))
