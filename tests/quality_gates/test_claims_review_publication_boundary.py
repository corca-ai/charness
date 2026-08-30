"""Publication-boundary rendering, refusal, and prepared-stop behavior."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .release_publish_fixtures import (
    _release_env,
    _run_publish,
    _run_publish_patch,
    _seed_publish_release_repo,
    commit_claims_review,
)
from .release_script_loading import load_release_script

CLAIMS_REVIEW = load_release_script("publish_release_claims_review", suffix="publication")
CLAIMS_EVIDENCE = load_release_script("claims_review_evidence", suffix="publication")
EXECUTE = load_release_script("publish_release_execute", suffix="publication")
PREFLIGHT = load_release_script("publish_release_preflight", suffix="publication")
SECTIONS = load_release_script("publish_release_artifact_sections", suffix="publication")


def _run(command: list[str], *, cwd: Path, check: bool = True):
    return subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)


def test_the_claims_review_section_renders_each_state_it_can_be_in() -> None:
    """The section is the only channel that reaches readers outside the session, so every
    state it can be in has to say the right thing on its own. The end-to-end publish tests
    drive this through `subprocess` and cannot see the branches."""
    heading = "## Claims Review"

    # `pass`: the record path, verdict, distinctness kind, its signal, and the narrative.
    rendered = "\n".join(
        SECTIONS.claims_review_lines(
            {
                "path": "charness-artifacts/release-review/r.json",
                "verdict": "pass",
                "observer_distinctness": {
                    "kind": "separate-agent-context",
                    "signal": "a bounded reviewer ran\nin a separate agent context",
                    "review_artifact": "charness-artifacts/release-review/r.md",
                },
            }
        )
    )
    assert heading in rendered
    assert "`charness-artifacts/release-review/r.json`" in rendered
    assert "verdict: `pass`" in rendered
    assert "`separate-agent-context`" in rendered
    assert "`charness-artifacts/release-review/r.md`" in rendered
    # Flattened at render time too, not only refused at the validator: a record committed
    # under an earlier build never saw that refusal, and one newline here turns a single
    # field into arbitrary lines of a document other gates parse.
    assert "a bounded reviewer ran in a separate agent context" in rendered
    # Discriminating form. Counting `- Recorded signal:` lines is NOT: with flattening
    # removed the injected remainder lands on its own line carrying no such prefix, so the
    # count stays 1 and the assertion passes over the exact defect it names. Every emitted
    # line must be blank, a heading, or a bullet -- an injected line is none of those.
    assert all(line == "" or line.startswith(("## ", "- ")) for line in rendered.splitlines()), rendered
    assert "None" not in rendered

    # `unproven`: the NEGATIVE property, not the bare token. A reader scanning headings
    # sees a "Claims Review" section and infers a review happened.
    rendered = "\n".join(
        SECTIONS.claims_review_lines(
            {
                "path": "charness-artifacts/release-review/r.json",
                "verdict": "unproven",
                "observer_distinctness": {
                    "kind": "unproven",
                    "signal": "host refused the spawn",
                    "review_artifact": None,
                },
            }
        )
    )
    assert "the distinct-observer property was NOT established" in rendered
    assert "recorded absence, not a passing review" in rendered
    assert "Review narrative: none" in rendered
    assert "None" not in rendered, "a null narrative must branch, not render as `None`"

    # The prepared record is the SUBJECT of the pending review, so "not recorded" on it
    # reads to that reviewer like a defect in the record they are auditing.
    rendered = "\n".join(SECTIONS.claims_review_lines(None, prepared=True))
    assert "THIS record is the subject of the pending" in rendered

    # A release that never went through the claims lane claims nothing.
    rendered = "\n".join(SECTIONS.claims_review_lines(None))
    assert "no distinct-observer property is claimed" in rendered

    # A field the validator populates today still must not render the literal `None` if it
    # ever stops being populated: a section whose worst output is the word `None` reports an
    # absent field as a present one. Asserted on the `pass` branch too, which is the one
    # that interpolates `review_artifact`.
    for missing in (
        {"path": None, "verdict": "pass", "observer_distinctness": {}},
        {"verdict": "pass", "observer_distinctness": {"kind": "separate-host"}},
    ):
        rendered = "\n".join(SECTIONS.claims_review_lines(missing))
        assert "None" not in rendered, rendered
        assert "not recorded" in rendered

    # One FIXED heading in every state: a heading whose name varies with data is what
    # makes a downstream substring check silently no-op.
    for lines in (
        SECTIONS.claims_review_lines(None),
        SECTIONS.claims_review_lines(None, prepared=True),
        SECTIONS.claims_review_lines(
            {
                "path": "p",
                "verdict": "pass",
                "observer_distinctness": {
                    "kind": "separate-host",
                    "signal": "s",
                    "review_artifact": "r",
                },
            }
        ),
        SECTIONS.claims_review_lines(
            {
                "path": "p",
                "verdict": "unproven",
                "observer_distinctness": {
                    "kind": "unproven",
                    "signal": "s",
                    "review_artifact": None,
                },
            }
        ),
    ):
        assert [line for line in lines if line.startswith("## ")] == [heading]


def test_claims_review_helper_refusals_are_exercised_in_process(tmp_path: Path) -> None:
    """The topology tests drive the publish helper through `subprocess`, so these refusal
    branches are invisible to in-process coverage and the changed-line mutation gate reads
    them as untested. Each one is a refusal, so leaving them unexercised is leaving a
    floor unproven."""

    def absent(command: list[str], *, cwd: Path, check: bool = True):
        return subprocess.CompletedProcess(command, 1, stdout="")

    record_path = "charness-artifacts/release/latest.md"

    # A commit whose record cannot be read carries no marker.
    assert CLAIMS_REVIEW.marker_at_commit(tmp_path, commit="deadbeef", record_path=record_path, run=absent) is False

    # A repo with no release record yet is preparing its FIRST release, not re-preparing
    # over an outstanding stop; refusing it would block every greenfield publish.
    adapter_data = {"output_dir": "charness-artifacts/release"}
    assert EXECUTE.assert_no_outstanding_prepared_stop(tmp_path, adapter_data=adapter_data, run=absent) is None

    def marked(command: list[str], *, cwd: Path, check: bool = True):
        return subprocess.CompletedProcess(command, 0, stdout=f"# Release Surface Check\n<!-- {CLAIMS_REVIEW.MARKER} -->\n")

    with pytest.raises(SystemExit, match="prepared claims-review stop is outstanding"):
        EXECUTE.assert_no_outstanding_prepared_stop(tmp_path, adapter_data=adapter_data, run=marked)

    # The record path is DERIVED from the adapter, and normalized: a trailing slash would
    # otherwise derive `...release//latest.md`, which git reads as a miss — a formatting
    # difference silently reproducing the blindness the derivation exists to end.
    assert CLAIMS_REVIEW.release_record_path({"output_dir": "artifacts/release"}) == "artifacts/release/latest.md"
    assert CLAIMS_REVIEW.release_record_path({"output_dir": "artifacts/release/"}) == "artifacts/release/latest.md"
    # A blank `output_dir` is a declaration of the repo ROOT, not an absent one -- that is
    # what the writer does with it, and a floor that refuses what the writer accepted leaves
    # the prepared stop unresumable by either route. Not stripped, for the same reason:
    # normalization applied on one side only is how the two come to name different files.
    assert CLAIMS_REVIEW.release_record_path({"output_dir": ""}) == "latest.md"
    assert CLAIMS_REVIEW.release_record_path({"output_dir": "."}) == "latest.md"
    assert CLAIMS_REVIEW.release_record_path({"output_dir": " x "}) == " x /latest.md"
    # A missing or non-string key is a caller defect and is named as one, never defaulted:
    # assuming a default is what made this floor blind.
    for adapter_data in ({}, {"output_dir": None}, {"output_dir": 7}):
        with pytest.raises(SystemExit, match="declares no `output_dir`"):
            CLAIMS_REVIEW.release_record_path(adapter_data)

    # An unreadable derived path is a refusal, not a marker miss. Without this the fix
    # converts every malformed, absolute, `..`-bearing, or changed-since-prepare
    # `output_dir` back into a silent fall-through to the lane that validates nothing.
    with pytest.raises(SystemExit, match="the release record is not readable at"):
        CLAIMS_REVIEW.assert_record_readable(tmp_path, record_path=record_path, commit="HEAD", run=absent)

    # A signal that would stop being one field of the published record. Every sentinel some
    # other surface substring-matches IN that record is refused, not just the marker: one
    # rendered field can satisfy any of them, and refusing only the marker left the same
    # shape standing in the closeout-recovery identity checks.
    for signal, message in (
        ("two\nlines", "must be a single line"),
        ("bell\x07", "must be a single line"),
        ("x" * (CLAIMS_EVIDENCE.MAXIMUM_SIGNAL_BYTES + 1), "exceeds"),
    ):
        with pytest.raises(SystemExit, match=message):
            CLAIMS_EVIDENCE.assert_signal_is_renderable(signal)
    assert CLAIMS_REVIEW.MARKER in CLAIMS_EVIDENCE.RECORD_SENTINELS
    for sentinel in CLAIMS_EVIDENCE.RECORD_SENTINELS:
        with pytest.raises(SystemExit, match="must not contain"):
            CLAIMS_EVIDENCE.assert_signal_is_renderable(f"host refused; see {sentinel} in the prior record")
    CLAIMS_EVIDENCE.assert_signal_is_renderable("a bounded reviewer ran in a separate agent context")
    assert SECTIONS.flatten_signal("two\nlines  here") == "two lines here"

    # The path fields are rendered into the published record too, so the sentinel rule that
    # guards `signal` has to guard them. `:` and ` ` are legal filename characters, so a
    # record named after the marker was accepted, published, and then latched the prepare
    # gate on a stop that does not exist.
    for sentinel in CLAIMS_EVIDENCE.RECORD_SENTINELS:
        with pytest.raises(SystemExit, match="must not contain"):
            CLAIMS_EVIDENCE.review_relative_path(
                f"{CLAIMS_EVIDENCE.EVIDENCE_ROOT}{sentinel}-record.json",
                "--claims-review-artifact",
                ".json",
            )
        # The critique artifact path renders into the SAME record (`## Review Proof`) on every
        # write including the published one, so guarding only the claims paths left the latch
        # reachable through a differently-named field. Refused at the critique gate, which runs
        # before the bump: the repair is renaming a file, not amending a published commit.
        with pytest.raises(SystemExit, match="must not contain"):
            PREFLIGHT.validate_critique_artifact_arg(tmp_path, f"charness-artifacts/critique/{sentinel}-review.md", run_command=absent)

    # Path shape refusals.
    for value, message in (
        (None, "must be a repo-relative path"),
        ("", "must be a repo-relative path"),
        ("   ", "must be a repo-relative path"),
        ("/abs/review.json", "must be a normalized repo-relative path"),
        ("charness-artifacts/release-review/../x.json", "must be a normalized repo-relative path"),
        ("charness-artifacts/other/review.json", ".json file under"),
    ):
        with pytest.raises(SystemExit, match=message):
            CLAIMS_EVIDENCE.review_relative_path(value, "--claims-review-artifact", ".json")

    # A narrative git cannot describe is not "added by the evidence commit".
    assert (
        CLAIMS_EVIDENCE.narrative_is_new(
            tmp_path,
            prepared_commit="p",
            evidence_commit="e",
            narrative="charness-artifacts/release-review/r.md",
            run=absent,
        )
        is False
    )

    # The change-set shape classifier's rejections.
    assert CLAIMS_EVIDENCE.claims_record_in_change_set([]) is None
    assert CLAIMS_EVIDENCE.claims_record_in_change_set(["README.md"]) is None
    assert CLAIMS_EVIDENCE.claims_record_in_change_set(["charness-artifacts/release-review/a.json", "charness-artifacts/release-review/b.json"]) is None
    assert CLAIMS_EVIDENCE.claims_record_in_change_set(["charness-artifacts/release-review/a.json", "charness-artifacts/release-review/a.md"]) == "charness-artifacts/release-review/a.json"


@pytest.mark.release_only
def test_execute_refuses_a_second_prepare_over_an_outstanding_stop(tmp_path: Path) -> None:
    """Re-running the prepare at a stop must refuse BEFORE it mutates anything.

    The stop exists to surface record blockers, so the operator standing at one reaches for
    the command that produced it. Unguarded, that second `--execute` succeeded: it bumped a
    second version, re-ran the release quality gates, and committed a second marked record
    whose parent already carried the marker -- after which no single-parent prepared
    boundary exists, the resume refuses, and the only recovery it can name is a reset that
    discards whatever claims review was already committed on top of the stop.
    """
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    prepared = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert prepared.returncode == 0, prepared.stderr
    prepared_commit = yaml.safe_load(prepared.stdout)["prepared_release_commit"]
    manifest = repo / "packaging" / "demo.json"
    manifest_before = manifest.read_text(encoding="utf-8")

    second = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert second.returncode != 0
    assert "prepared claims-review stop is outstanding" in second.stderr
    # Both supported exits are named, so the refusal is actionable without reading source.
    assert "--claims-review-artifact" in second.stderr
    # Nothing moved: no second version bump, no second release commit.
    assert _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip() == prepared_commit
    assert manifest.read_text(encoding="utf-8") == manifest_before
    assert _run(["git", "status", "--porcelain"], cwd=repo).stdout.strip() == ""


@pytest.mark.release_only
def test_the_claims_evidence_commit_is_still_refused_a_second_prepare(tmp_path: Path) -> None:
    """The destructive case, and the reason this is keyed on the INHERITED marker.

    At the claims-evidence commit R the operator's next step is `--resume`; reaching for
    `--execute` instead is the same muscle memory. `prepared_record` declines at R (the
    marker is inherited, not introduced), so a check keyed on the prepared boundary would
    wave this through -- and the resume's recovery advice for the state it produces is a
    reset back past R, i.e. discarding the committed claims review itself.
    """
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    prepared = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert prepared.returncode == 0, prepared.stderr
    payload = yaml.safe_load(prepared.stdout)
    commit = payload["prepared_release_commit"]
    record = _run(["git", "show", f"{commit}:charness-artifacts/release/latest.md"], cwd=repo).stdout
    review_path = commit_claims_review(
        repo,
        prepared_commit=commit,
        prepared_record=record,
        target_version=payload["target_version"],
        tag_name=payload["tag_name"],
        stem="second-prepare-claims",
    )
    evidence = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()

    refused = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert refused.returncode != 0
    assert "prepared claims-review stop is outstanding" in refused.stderr
    assert _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip() == evidence
    # The review the mistaken prepare would have stranded is still the direct child of the
    # prepared record, so the supported resume still publishes it.
    resumed = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--claims-review-artifact",
        review_path,
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert resumed.returncode == 0, resumed.stderr


@pytest.mark.release_only
def test_a_finished_release_does_not_latch_the_second_prepare_refusal(tmp_path: Path) -> None:
    """The guard must not wedge the NEXT release.

    It is keyed on a marker that descendants inherit, so the property it depends on is that
    publication rewrites the release record without it. Asserted here rather than assumed:
    if that ever stops holding, this repo could never cut another release, and the failure
    would surface at the next publish rather than in this suite.
    """
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    published = _run_publish_patch(repo, env)
    assert published.returncode == 0, published.stderr
    # Read at HEAD, which is what the gate reads. A worktree copy can be unmarked while the
    # COMMITTED record still carries the marker, and that committed record is what latches.
    record = _run(["git", "show", "HEAD:charness-artifacts/release/latest.md"], cwd=repo).stdout
    assert CLAIMS_REVIEW.MARKER not in record

    again = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert again.returncode == 0, again.stderr
    assert yaml.safe_load(again.stdout)["target_version"] == "0.0.2"


def test_the_prepared_stop_gate_is_wired_into_the_cli_before_the_plan(tmp_path: Path, monkeypatch) -> None:
    """Proof that the gate is CALLED, in the standing suite rather than the release gate.

    The end-to-end refusals above are `release_only`, so they are excluded from the standing
    pre-push run; the in-process assertions call the function directly and stay green if the
    call site is deleted. That is the inert-guard shape this repo keeps shipping: during
    review of this very slice the call site sat behind `if False and ...` and nothing in the
    standing suite noticed. Everything upstream of the gate is stubbed and the plan builder
    is booby-trapped, so this pins the ORDER too -- the refusal precedes the plan build and
    every mutation after it.
    """
    cli = load_release_script("publish_release_cli", suffix="wiring")

    def reached(*_args, **kwargs):
        # The adapter data is asserted, not discarded: passing a hardcoded default here is
        # the exact defect `release_record_path` refuses a default for, and a stub that
        # ignores its arguments would call that wiring correct.
        assert kwargs["adapter_data"] == {"output_dir": "d"}
        raise SystemExit("prepared-stop gate reached")

    monkeypatch.setattr(cli, "load_adapter", lambda _root: {"valid": True, "data": {"output_dir": "d"}})
    monkeypatch.setattr(cli, "validate_critique_artifact_arg", lambda *a, **k: None)
    monkeypatch.setattr(cli, "enforce_release_critique_gate", lambda *a, **k: {})
    monkeypatch.setattr(cli, "gate_target_version", lambda *a, **k: "1.2.3")
    monkeypatch.setattr(cli, "git_status", lambda _root: [])
    monkeypatch.setattr(
        cli,
        "build_publish_plan",
        lambda *a, **k: pytest.fail("plan built before the prepared-stop gate"),
    )
    monkeypatch.setattr(cli._execute, "assert_no_outstanding_prepared_stop", reached)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "publish_release.py",
            "--repo-root",
            str(tmp_path),
            "--part",
            "patch",
            "--execute",
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ],
    )

    with pytest.raises(SystemExit, match="prepared-stop gate reached"):
        cli.main()

    # ...and NOT on the lane that must reach the claims-review validator instead. A gate that
    # also fired on `--resume` would refuse every publication of the stop it protects.
    def refuse_if_called(*_args, **_kwargs):
        pytest.fail("the prepared-stop gate ran on the resume lane")

    def resume_lane(*_args, **_kwargs):
        raise SystemExit("resume lane")

    monkeypatch.setattr(cli._execute, "assert_no_outstanding_prepared_stop", refuse_if_called)
    monkeypatch.setattr(cli, "preflight_resume_state", resume_lane)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "publish_release.py",
            "--repo-root",
            str(tmp_path),
            "--resume",
            "--publish-current",
            "--execute",
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ],
    )
    with pytest.raises(SystemExit, match="resume lane"):
        cli.main()


@pytest.mark.release_only
def test_an_output_dir_changed_after_the_prepared_stop_is_refused(tmp_path: Path) -> None:
    """Resume derives the release-record path instead of silently losing the stop."""
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    prepared = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert prepared.returncode == 0, prepared.stderr

    adapter = repo / ".agents" / "release-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8").replace(
            "output_dir: charness-artifacts/release",
            "output_dir: artifacts/release",
        ),
        encoding="utf-8",
    )
    _run(["git", "add", "-A"], cwd=repo)
    _run(
        ["git", "commit", "-m", "Point the adapter at a different output_dir"],
        cwd=repo,
    )
    gh_log, git_log = tmp_path / "gh-log.json", tmp_path / "git-log.json"
    prior_gh = json.loads(gh_log.read_text(encoding="utf-8"))
    prior_git = json.loads(git_log.read_text(encoding="utf-8"))

    refused = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert refused.returncode != 0
    assert (
        "the release record is not readable at 'artifacts/release/latest.md'"
        in refused.stderr
    )
    new_gh = json.loads(gh_log.read_text(encoding="utf-8"))[len(prior_gh) :]
    new_git = json.loads(git_log.read_text(encoding="utf-8"))[len(prior_git) :]
    assert not any(entry[:2] == ["release", "create"] for entry in new_gh)
    assert not any(entry and entry[0] == "push" for entry in new_git)


@pytest.mark.release_only
def test_a_non_default_output_dir_publishes_through_the_claims_floor(
    tmp_path: Path,
) -> None:
    """A custom adapter output directory still passes through the claims floor."""
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter = repo / ".agents" / "release-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8").replace(
            "output_dir: charness-artifacts/release",
            "output_dir: artifacts/release",
        ),
        encoding="utf-8",
    )
    _run(["git", "add", "-A"], cwd=repo)
    _run(
        ["git", "commit", "-m", "Point the adapter at a different output_dir"],
        cwd=repo,
    )
    env = _release_env(tmp_path, bin_dir)

    prepared = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert prepared.returncode == 0, prepared.stderr
    payload = yaml.safe_load(prepared.stdout)
    commit = payload["prepared_release_commit"]
    record = _run(
        ["git", "show", f"{commit}:artifacts/release/latest.md"], cwd=repo
    ).stdout
    assert "charness-release-state:prepared-awaiting-claims-review" in record
    review_path = commit_claims_review(
        repo,
        prepared_commit=commit,
        prepared_record=record,
        target_version=payload["target_version"],
        tag_name=payload["tag_name"],
        stem="non-default-output-dir",
        release_record_path="artifacts/release/latest.md",
    )

    resumed = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--claims-review-artifact",
        review_path,
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert resumed.returncode == 0, resumed.stderr
    final = yaml.safe_load(resumed.stdout)
    assert final["claims_review"]["verdict"] == "pass"
    assert final["artifact_path"] == "artifacts/release/latest.md"
    published = repo / "artifacts" / "release" / "latest.md"
    assert published.is_file()
    assert (
        _run(["git", "status", "--porcelain", "--", "artifacts"], cwd=repo)
        .stdout.strip()
        == ""
    )
    text = published.read_text(encoding="utf-8")
    assert "## Claims Review" in text
    assert "Claims review verdict: `pass`" in text
    assert "`separate-agent-context`" in text
