"""The requested-review gate refuses an unhonored adapter declaration instead of
reporting the opposite of what the repo declared.

Measured on the real CLI before the repair, not argued: with `version: 9` and a declared
`requested_review_commands`, the gate printed `configuration status: not_configured` —
"this repo declares none" — over a repo that declared a command, at exit 0.

Two claims this docstring USED to carry were refuted by bounded review and are recorded
here rather than quietly dropped, because both were published into several surfaces:

* "a refusal in `main()` would have left two importers reading charness defaults." False.
  Under an unhonored declaration both stop earlier — `publish_release_cli` at
  `_valid_adapter_data`, `plan_release_run` behind `if adapter.get("valid")`. The measured
  count is ZERO. Read-site placement buys POSITIONAL INDEPENDENCE, which is a real and
  smaller property.
* "the repo declared a `block-if-unconfigured` policy and the gate downgraded its own
  enforcement to advisory." `resolve_adapter` accepts exactly
  `{warn-if-unconfigured, advisory-only}`, so that clause described a configuration no
  repo can hold. The measured half — a declared COMMAND read back as `not_configured` —
  is the whole finding.

Round 2 then found the guard keyed on one door: `version: !!int 9` makes the parser refuse
the document and reaches the same charness defaults. Both doors are pinned below.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .support import ROOT, run_script

GATE = ROOT / "skills" / "public" / "release" / "scripts" / "check_requested_review_gate.py"


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text("# release\n", encoding="utf-8")
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "release-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(repo: Path) -> subprocess.CompletedProcess:
    return run_script(str(GATE), "--repo-root", str(repo))


# `advisory-only`, not `block-if-unconfigured`. A round-1 bounded review found the
# latter is not a value this schema accepts (`resolve_adapter` validates against exactly
# `{warn-if-unconfigured, advisory-only}`), so the polarity control below was passing over
# a repo that was `valid: false` for a reason unrelated to the version — and the recorded
# harm described a configuration the adapter never honors. The measured half stands: a
# DECLARED COMMAND read back as `not_configured`.
DECLARED = 'requested_review_commands:\n  - echo declared\nrequested_review_policy: advisory-only\n'


def test_an_unspeakable_version_refuses_rather_than_reporting_not_configured(tmp_path: Path) -> None:
    # The behavioral flip this row is paid down by. Before the guard this exact input
    # printed `configuration status: not_configured` and warned that enforcement was
    # advisory-only, exit 0 — over a repo that declared a command.
    result = _run(_repo(tmp_path, "version: 9\n" + DECLARED))
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    assert "release-adapter.yaml" in result.stderr
    assert "not_configured" not in result.stdout


def test_a_speakable_version_still_reports_what_the_repo_declared(tmp_path: Path) -> None:
    # The polarity control. Every assertion above is satisfied by a gate that refuses
    # everything; this is the one that would catch it.
    result = _run(_repo(tmp_path, "version: 1\n" + DECLARED))
    assert result.returncode == 0, result.stderr
    assert "configuration status: configured" in result.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    # The opt-in design survives: a repo that declares nothing is not a repo whose
    # declaration could not be read, and conflating them would refuse every consumer
    # that never opted in.
    result = _run(_repo(tmp_path, None))
    assert result.returncode == 0, result.stderr
    assert "configuration status: not_configured" in result.stdout


@pytest.mark.parametrize("importer", ["plan_release_run", "publish_release_cli"])
def test_every_importer_of_build_payload_inherits_the_guard(tmp_path: Path, importer: str) -> None:
    """Each importer's BOUND SYMBOL carries the guard — which is less than call-site
    coverage, and a round-1 bounded review was right to say so.

    `build_payload` has three entrypoints and the guard is inside it, so the two modules
    that import it cannot be guarded at one call site and unguarded at another. What this
    does NOT show is that either importer would otherwise have reached the read: both stop
    earlier under an unhonored declaration, `publish_release_cli` at `_valid_adapter_data`
    and `plan_release_run` behind `if adapter.get("valid")`. The property proven here is
    positional independence, not a removed live harm at those two sites.
    """
    from tests.script_main import load_script_module

    module = load_script_module(
        f"{importer}_for_guard_test",
        ROOT / "skills" / "public" / "release" / "scripts" / f"{importer}.py",
    )
    repo = _repo(tmp_path, "version: 9\n" + DECLARED)
    with pytest.raises(SystemExit) as excinfo:
        module.build_review_gate_payload(repo)
    assert "does not speak" in str(excinfo.value)


def test_a_parser_refusal_reaches_the_same_guard(tmp_path: Path) -> None:
    """The round-1 review's blocker, at a real CLI.

    `version: !!int 9` is one token added to the input above. The parser refuses the
    document, the resolver hands back `infer_repo_defaults(...)`, and before the guard
    keyed on the CONDITION rather than on one check's wording this printed
    `configuration status: not_configured` at exit 0 — byte-identical to the pre-repair
    harm this file exists to stop.

    Only this gate and `bootstrap_review` carry a consumer-level test for the second
    door; the other three wire the identical call and are covered by
    `test_adapter_version_refusal_is_loud.py`, which pins the predicate itself. That is a
    deliberate stopping point, recorded rather than left as an implied "all five proven".
    """
    result = _run(_repo(tmp_path, "version: !!int 9\n" + DECLARED))
    assert result.returncode == 1, result.stdout
    assert "could not be parsed" in result.stderr
    assert "not_configured" not in result.stdout
