"""The drafter's INGESTION seam: how a producer payload becomes a mapping.

`test_dup_ratchet_triage_draft.py` covers what the drafter suggests once it holds a
payload. Everything here is upstream of that: the producer call whose stdout it reads,
and the two ways a `--detail` payload can arrive unreadable. Both refusals matter for
the same reason the suggestion rules do -- this script's output drafts a permanent
`intentional` accept into dup-review.json, so a payload it could not read must surface
as a named refusal rather than as a traceback or, worse, an empty family set.

Nothing here runs a producer or touches `charness-artifacts/quality/dup-review.json`:
the subprocess seam is fed a recorded result, so the tests assert the drafter's own
reading rather than the ratchet's current verdict.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.script_loader import load_script_module

from .support import ROOT

TRIAGE = load_script_module(
    "tests.quality_gates.dup_ratchet_triage_ingestion",
    ROOT / "skills/public/quality/scripts/draft_dup_ratchet_triage.py",
)

RATCHET_SCRIPT = Path("skills/public/quality/scripts/check_dup_ratchet.py")
RATCHET_ARGS = ["--repo-root", ".", "--detail"]


def _recorded_producer(returncode: int, stdout: str, *, stderr: str = "", log: list | None = None):
    """Stand in for the loaded producer module, returning one recorded result."""

    def main(argv):
        if log is not None:
            log.append(list(argv))
        print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)
        return returncode

    return SimpleNamespace(main=main)


def _patch_recorded_producer(monkeypatch: pytest.MonkeyPatch, producer) -> None:
    monkeypatch.setattr(TRIAGE.SKILL_RUNTIME, "load_local_skill_module", lambda *_args: producer)


def test_a_hard_blocking_producer_is_read_rather_than_treated_as_a_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exit 1 is the ratchet's BLOCK verdict, and it is exactly the run worth triaging.

    The payload arrives on stdout, so refusing a non-zero exit here would make the
    drafter unusable in the only situation it exists for.
    """
    calls: list = []
    _patch_recorded_producer(
        monkeypatch,
        _recorded_producer(1, "status: hard-block\nnew_code_families: [fam1]\n", log=calls),
    )

    assert TRIAGE._run_detail(RATCHET_SCRIPT, RATCHET_ARGS) == {
        "status": "hard-block",
        "new_code_families": ["fam1"],
    }
    assert calls == [RATCHET_ARGS]


def test_a_producer_that_crashed_is_named_with_its_own_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exit 2 is not a verdict -- it is a producer that did not run.

    Parsing its (empty) stdout instead would hand `build_report` a payload with no
    family list, which the unestablished-reason guard would then report as the
    ratchet's shape rather than as the crash it actually is.
    """
    _patch_recorded_producer(
        monkeypatch, _recorded_producer(2, "", stderr="adapter file is unreadable\n")
    )

    with pytest.raises(RuntimeError) as excinfo:
        TRIAGE._run_detail(RATCHET_SCRIPT, RATCHET_ARGS)

    assert "rc=2" in str(excinfo.value)
    assert "adapter file is unreadable" in str(excinfo.value)


def test_an_unreadable_producer_payload_names_the_command_it_came_from(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A spawned producer has no filename to blame, so its ARGV is the source label.

    Two producers feed this script. A refusal that says only "payload is not a
    mapping" leaves the operator guessing which of them misbehaved, and the injected
    `--ratchet-report` / `--code-inventory` files at least name themselves.
    """
    _patch_recorded_producer(monkeypatch, _recorded_producer(0, "- one\n- two\n"))

    with pytest.raises(RuntimeError) as excinfo:
        TRIAGE._run_detail(RATCHET_SCRIPT, RATCHET_ARGS)

    assert str(excinfo.value).startswith(" ".join([str(RATCHET_SCRIPT), *RATCHET_ARGS]))
    assert "not a mapping" in str(excinfo.value)


def test_a_yaml_payload_with_no_pyyaml_to_read_it_names_the_remedy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`render_yaml` emits real YAML when PyYAML is present and compact JSON when it is
    not -- but the producer and this reader can be different interpreters, so a YAML
    payload can arrive where nothing can parse it. A bare ImportError traceback here
    would read as a broken drafter; the install line is the actual fix.
    """
    monkeypatch.setitem(sys.modules, "yaml", None)

    with pytest.raises(RuntimeError) as excinfo:
        TRIAGE._parse_detail_payload(
            "status: hard-block\nnew_code_families: []\n", "probe --detail"
        )

    message = str(excinfo.value)
    assert "probe --detail" in message
    assert "PyYAML is not importable here" in message
    assert "install PyYAML" in message


def test_a_corrupt_yaml_payload_is_reported_as_such_not_as_a_parse_traceback() -> None:
    """A truncated payload (a killed producer, a half-written saved file) is neither
    JSON nor YAML. The drafter already handles the JSON case, so letting the YAML
    parser's exception escape would be the one input shape whose failure looks like a
    defect in this script rather than a bad input.
    """
    with pytest.raises(RuntimeError) as excinfo:
        TRIAGE._parse_detail_payload("status: [unclosed\n", "probe --detail")

    message = str(excinfo.value)
    assert message.startswith("probe --detail: unreadable `--detail` payload")
