"""`resolve_artifact_path` refuses when the reader honored nothing the repo declared.

THE REGRESSION THIS PINS WAS INTRODUCED BY `#673` AND FOUND BY A BOUNDED REVIEW, not by the
batch that caused it. That is the second time this exact collateral has arrived that way.

Before `#673`, five resolvers let a parser refusal out as a traceback, so the subprocess
return code was non-zero and `load_adapter`'s `if completed.returncode != 0` stopped this
helper. Making those five render a verdict made them exit 0 like the other eleven — and this
file's ONLY protection went with it. Measured at `a776bd37d` with `version: !!int 9` beside
a declared `output_dir: docs/mine-q`: `write_artifact_path: charness-artifacts/quality/latest.md`,
exit 0. A charness default wearing the repo's name, which is the harm the whole
adapter-consumer debt exists to close, reintroduced by a repair for it.

The guard keys on the CONDITION (`declarations_unhonored` or `declarations_dropped`), not on
the exit code, so the next resolver that changes its exit convention cannot silently disarm
it again.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "artifacts" / "resolve_artifact_path.py"

DECLARED = "docs/mine-q"
# One document per door. `version: 9` is the version door, `!!int 9` the parse door, and the
# over-indented line the dropped-line door — the third was unreachable for quality before
# `#673` and is what makes this a three-arm guard rather than a two-arm one.
UNHONORED = [
    pytest.param(f"version: 9\nrepo: demo\noutput_dir: {DECLARED}\n", id="version-refused"),
    pytest.param(f"version: !!int 9\nrepo: demo\noutput_dir: {DECLARED}\n", id="parse-refused"),
    pytest.param(f"version: 1\nrepo: demo\n  output_dir: {DECLARED}\n", id="line-dropped"),
]


def _repo(tmp_path: Path, adapter: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess:
    return run_script(
        str(CLI), "--repo-root", str(repo), "--skill-id", "quality", "--slug", "probe", cwd=ROOT
    )


# The message each door owes, keyed to the door. Round 2 found the first cut gluing the
# UNHONORED tail onto the dropped-line arm, where it is false: a dropped line leaves the rest
# of the document honored, so `output_dir` is still read and resolution would NOT have
# returned a charness default. Asserting per-arm is what keeps the two from re-merging.
DOOR_CLAUSE = {
    "version-refused": "charness default wearing this repo's name",
    "parse-refused": "charness default wearing this repo's name",
    "line-dropped": "serving an inferred default instead",
}


@pytest.mark.parametrize("adapter", UNHONORED)
def test_an_unhonored_adapter_refuses_instead_of_resolving_a_charness_default(
    tmp_path: Path, adapter: str, request: pytest.FixtureRequest
):
    result = _run(_repo(tmp_path, adapter))
    assert result.returncode != 0, result.stdout
    # The wording has ONE owner (`adapter_version_verdict.unhonored_cause` /
    # `unhonored_remedy`), so this asserts that owner's clause rather than a phrase invented
    # here -- the first cut of the guard invented a third wording and a sibling test caught
    # it, which is the same drift `unhonored_cause` exists to prevent.
    door = request.node.callspec.id
    assert DOOR_CLAUSE[door] in result.stderr, result.stderr
    assert "quality-adapter.yaml" in result.stderr, result.stderr
    # The precise defect: the charness default emitted as this repo's write target.
    assert "charness-artifacts/quality" not in result.stdout
    assert "write_artifact_path" not in result.stdout


def test_a_honored_declaration_still_resolves(tmp_path: Path):
    """The polarity control. Without it the guard above is satisfied by refusing everything,
    and this helper's whole job is resolving a path."""
    result = _run(_repo(tmp_path, f"version: 1\nrepo: demo\noutput_dir: {DECLARED}\n"))
    assert result.returncode == 0, result.stderr
    assert f"write_artifact_path: {DECLARED}/latest.md" in result.stdout


def test_an_ordinary_invalid_field_is_not_refused(tmp_path: Path):
    """The other polarity, and the one this repo's guards keep getting wrong. `valid: false`
    can mean one bad field beside fifteen honored ones; only `declarations_unhonored` means
    the reader honored NOTHING. A typo'd `repo` must not disarm a perfectly good
    `output_dir` — nor block on it."""
    adapter = f"version: 1\nrepo: 12345\noutput_dir: {DECLARED}\n"
    result = _run(_repo(tmp_path, adapter))
    assert result.returncode == 0, result.stderr
    assert f"write_artifact_path: {DECLARED}/latest.md" in result.stdout


def test_a_resolver_that_rendered_no_payload_is_refused_rather_than_read_as_empty():
    """The guard reads a payload the resolver PRINTED. If nothing parseable came back there
    is no `errors` to ask about, and treating that as "no errors, carry on" would resolve the
    charness default on the one input where the reader said nothing at all — the same silence
    the exit-code path used to catch."""
    from tests.script_main import load_script_module

    module = load_script_module("resolve_artifact_path_for_no_payload_test", CLI)
    for rendered in (None, "", ["not", "a", "mapping"]):
        with pytest.raises(SystemExit, match="rendered no payload"):
            module._refuse_unhonored_adapter(rendered, "quality")
