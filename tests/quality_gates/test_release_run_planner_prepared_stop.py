"""Prepared-release stop and resume-packet tests for the release planner.

This module owns the planner's prepared-stop state machine: discovering the
committed stop, selecting acceptable artifacts, and emitting resumable packets.
Those cases form one boundary distinct from ordinary inspect/publish planning.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from tests.quality_gates.git_fixture_support import init_git_repo
from tests.seed_cache import get_or_build

from .release_publish_fixtures import (
    PUBLISH_SCRIPT,
    REPO_ROOT,
    _release_env,
    _seed_publish_release_repo,
    commit_claims_review,
)
from .test_release_run_planner import (
    _CLOSEOUT_EVIDENCE,
    _CLOSEOUT_TOKENS,
    _PACKETS,
    _PLANNER,
    _PREPARED_STOP,
    _args,
    _git,
    _run_plan,
)

pytestmark = pytest.mark.boundary_contract(
    reason="observe the release publish preparation's real git and external release child commands"
)


def _build_prepared_stop_seed(staging: Path) -> None:
    """Cache the one real prepare needed to exercise planner stop discovery."""
    repo, _remote, bin_dir = _seed_publish_release_repo(staging)
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / PUBLISH_SCRIPT),
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ],
        cwd=REPO_ROOT,
        env=_release_env(staging, bin_dir),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    (staging / "payload.yaml").write_text(result.stdout, encoding="utf-8")
    _git(repo, "remote", "remove", "origin")


def _prepared_stop_seed() -> Path:
    return get_or_build("release-prepared-stop-planner", _build_prepared_stop_seed)


def _copy_prepared_stop(tmp_path: Path) -> tuple[Path, dict[str, str], dict[str, object]]:
    seed = _prepared_stop_seed()
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    bin_dir = tmp_path / "bin"
    shutil.copytree(seed / "repo", repo)
    shutil.copytree(seed / "remote.git", remote)
    shutil.copytree(seed / "bin", bin_dir)
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "fetch", "origin")
    payload = yaml.safe_load((seed / "payload.yaml").read_text(encoding="utf-8"))
    return repo, _release_env(tmp_path, bin_dir), payload


def _prepare_release_stop(tmp_path: Path):
    """Drive a real prepare so the planner reads the marker the helper actually writes."""
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    prepared = subprocess.run(
        [
            "python3",
            str(PUBLISH_SCRIPT),
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert prepared.returncode == 0, prepared.stderr
    return repo, env, yaml.safe_load(prepared.stdout)


@pytest.mark.release_only
def test_planner_routes_a_prepared_claims_stop_to_a_resume_not_inspect_only(tmp_path: Path) -> None:
    """Normal preparation stops at a marked local record. Neither planner read that
    marker, so the planner said `inspect_only` -- "no target selector was provided" --
    while a release sat mid-flight, and the five-flag resume invocation had to be
    reconstructed by hand."""
    repo, env, payload = _prepare_release_stop(tmp_path)

    result = _run_plan(repo, env)

    assert result.returncode == 0, result.stderr
    plan = yaml.safe_load(result.stdout)
    assert plan["next_action"]["kind"] == "resume_prepared_claims_review"
    assert payload["tag_name"] in plan["next_action"]["reason"]
    assert plan["prepared_claims_review"]["target_version"] == payload["target_version"]
    assert (
        plan["prepared_claims_review"]["marker"]
        == "charness-release-state:prepared-awaiting-claims-review"
    )


@pytest.mark.release_only
def test_planner_emits_the_resume_command_with_every_required_flag(tmp_path: Path) -> None:
    """`inspect_only` emitted no publish packet at all, so nothing named `--resume`,
    `--publish-current`, or the two artifact flags the stop requires."""
    repo, env, _payload = _prepare_release_stop(tmp_path)

    plan = yaml.safe_load(_run_plan(repo, env).stdout)

    packets = {packet["id"]: packet for packet in plan["publish_packets"]}
    assert set(packets) == {
        "claims-review-scaffold",
        "publish-resume-dry-run",
        "publish-resume-execute",
    }
    scaffold = packets["claims-review-scaffold"]
    assert "scaffold_claims_review.py" in scaffold["command"]
    assert "--write" in scaffold["command"]
    assert scaffold["requires_user_confirmation"] is False
    execute = packets["publish-resume-execute"]
    for flag in (
        "--resume",
        "--publish-current",
        "--claims-review-artifact",
        "--critique-artifact",
        "--execute",
    ):
        assert flag in execute["command"], execute["command"]
    assert execute["requires_user_confirmation"] is True
    assert packets["publish-resume-dry-run"]["requires_user_confirmation"] is False
    assert "--execute" not in packets["publish-resume-dry-run"]["command"]

    # And on the summary line, which is where an operator at a prepared stop looks.
    summary = _run_plan(repo, env, detail=False)
    assert summary.returncode == 0, summary.stderr
    assert "publish-resume-execute:" in summary.stdout
    assert "claims-review-scaffold:" in summary.stdout
    assert "--claims-review-artifact" in summary.stdout


@pytest.mark.release_only
def test_planner_names_only_a_critique_artifact_the_publish_gate_accepts(tmp_path: Path) -> None:
    """The refusal an operator hits is "standalone critique not satisfied", which never
    names an artifact that WOULD bind. Binding is not the whole question, though: the gate
    also requires the artifact to be TRACKED and to clear a stub-residual floor. A
    binding-only filter named an untracked file (whose real refusal is a dirty-worktree
    complaint that never says "commit this first") and a four-byte stub (whose refusal is
    the exact message this packet exists to prevent)."""
    repo, env, payload = _prepare_release_stop(tmp_path)
    version = payload["target_version"]
    slug = version.replace(".", "-")

    plan = yaml.safe_load(_run_plan(repo, env).stdout)
    assert plan["prepared_claims_review"]["critique_artifact_candidates"] == []
    assert "no artifact under charness-artifacts/critique binds" in plan["next_action"]["reason"]

    critique_dir = repo / "charness-artifacts" / "critique"
    critique_dir.mkdir(parents=True, exist_ok=True)
    good = critique_dir / f"release-{slug}.md"
    good.write_text(
        f"# Release critique for {version}\n\nScope, risks, and the counterweight pass "
        f"for the {version} release candidate.\n",
        encoding="utf-8",
    )
    untracked = critique_dir / f"untracked-{slug}.md"
    untracked.write_text(f"# Untracked critique\n\nRelease: {version}\n", encoding="utf-8")
    stub = critique_dir / f"stub-{slug}.md"
    stub.write_text(f"# {version}\n", encoding="utf-8")
    unrelated = critique_dir / "unrelated.md"
    unrelated.write_text(
        "# Some other critique\n\nAbout nothing in particular.\n", encoding="utf-8"
    )
    _git(repo, "add", str(good), str(stub), str(unrelated))
    _git(repo, "commit", "-m", "Add critique candidates")

    plan = yaml.safe_load(_run_plan(repo, env).stdout)
    candidates = plan["prepared_claims_review"]["critique_artifact_candidates"]
    assert candidates == [good.relative_to(repo).as_posix()], candidates
    for rejected in (untracked, stub, unrelated):
        assert rejected.relative_to(repo).as_posix() not in candidates
    # A single unambiguous candidate is placed into the command, not left as a hole.
    execute = next(p for p in plan["publish_packets"] if p["id"] == "publish-resume-execute")
    assert f"--critique-artifact {candidates[0]}" in execute["command"]


@pytest.mark.release_only
def test_the_resume_packet_names_the_arguments_the_claims_lane_will_not_enforce(
    tmp_path: Path,
) -> None:
    """The claims lane skips the narrative audit and never runs the notes-file preflight,
    so a resume that drops `--notes-file` publishes with `--generate-notes` instead of the
    drafted notes the prepare validated, and a dropped `--close-issue*` just leaves the
    issue open. Neither is refused, so the packet has to say so."""
    repo, env, _payload = _prepare_release_stop(tmp_path)

    plan = yaml.safe_load(_run_plan(repo, env).stdout)

    execute = next(p for p in plan["publish_packets"] if p["id"] == "publish-resume-execute")
    assert "--notes-file" in execute["repeat_original_arguments"]
    assert "--close-issue" in execute["repeat_original_arguments"]


@pytest.mark.release_only
def test_the_resume_packet_uses_the_committed_claims_record_when_there_is_one(
    tmp_path: Path,
) -> None:
    """At the second half of the stop the record is committed and its path is fully
    derivable, so leaving it a `<placeholder>` defeats the point of emitting the command
    in exactly the state where it is knowable."""
    repo, env, payload = _prepare_release_stop(tmp_path)
    record = subprocess.run(
        [
            "git",
            "show",
            f"{payload['prepared_release_commit']}:charness-artifacts/release/latest.md",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    review_path = commit_claims_review(
        repo,
        prepared_commit=payload["prepared_release_commit"],
        prepared_record=record,
        target_version=payload["target_version"],
        tag_name=payload["tag_name"],
        stem="planner-claims",
    )

    plan = yaml.safe_load(_run_plan(repo, env).stdout)

    assert plan["prepared_claims_review"]["committed_claims_record"] == review_path
    execute = next(p for p in plan["publish_packets"] if p["id"] == "publish-resume-execute")
    assert f"--claims-review-artifact {review_path}" in execute["command"]
    assert "<claims-review-record>" not in execute["command"]


@pytest.mark.release_only
def test_the_planner_reads_the_marker_from_the_commit_not_the_worktree(tmp_path: Path) -> None:
    """Every publish-side consumer reads `git show <commit>:...`. A worktree-only read
    makes the planner confidently prescribe a claims resume for a HEAD the publish helper
    does not treat as a prepared stop -- and, worse, prescribe a `--claims-review-artifact`
    for a run that would ignore it."""
    repo, env, _payload = _prepare_release_stop(tmp_path)
    record = repo / "charness-artifacts" / "release" / "latest.md"

    # Uncommitted removal of the marker: the COMMIT still carries it, so the stop stands.
    record.write_text("# release\n\nno marker here\n", encoding="utf-8")
    plan = yaml.safe_load(_run_plan(repo, env).stdout)
    assert plan["next_action"]["kind"] == "resume_prepared_claims_review"

    # Uncommitted ADDITION of the marker on a tree whose commit lacks it: no stop.
    second = tmp_path / "second"
    second.mkdir()
    repo2, _remote2, bin_dir2 = _seed_publish_release_repo(second)
    env2 = _release_env(second, bin_dir2)
    target = repo2 / "charness-artifacts" / "release" / "latest.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "<!-- charness-release-state:prepared-awaiting-claims-review -->\n", encoding="utf-8"
    )
    plan2 = yaml.safe_load(_run_plan(repo2, env2).stdout)
    assert plan2["next_action"]["kind"] != "resume_prepared_claims_review"
    assert plan2["prepared_claims_review"] is None


def test_planner_prepared_stop_helpers_are_exercised_in_process(tmp_path: Path) -> None:
    """The planner tests drive `plan_release_run.py` through `subprocess`, which is the
    honest way to test a CLI but leaves these helpers invisible to in-process coverage --
    so the changed-line mutation gate reads them as untested. This calls them directly.
    """
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "critique").mkdir(parents=True)
    init_git_repo(repo)
    _git(repo, "config", "user.email", "t@example.test")
    _git(repo, "config", "user.name", "T")

    # The record path is derived from the adapter, and the planner is TOLERANT where the
    # publish helper refuses: an adapter that declares no `output_dir` means "no prepared
    # stop detected", not a crash in a read-only planner.
    assert (
        _PREPARED_STOP.release_record_path({"output_dir": "artifacts/release"})
        == "artifacts/release/latest.md"
    )
    assert (
        _PREPARED_STOP.release_record_path({"output_dir": "artifacts/release/"})
        == "artifacts/release/latest.md"
    )
    assert _PREPARED_STOP.release_record_path({}) is None
    assert _PREPARED_STOP.release_record_path({"output_dir": "  "}) is None
    assert _PREPARED_STOP.head_release_record(repo, None) is None

    # Tolerant where the publish helper refuses, including when the listing itself fails:
    # the planner is read-only, so its worst honest outcome is "no candidate to place",
    # never a crash. The publish helper owns the refusal.
    def _raises(*_args, **_kwargs):
        raise OSError("notes directory is unreadable")

    assert (
        _PREPARED_STOP.drafted_notes_candidates(
            repo, {"output_dir": "charness-artifacts/release"}, "v1.2.3", find_drafted_notes=_raises
        )
        == []
    )
    assert (
        _PREPARED_STOP.drafted_notes_candidates(repo, {}, "v1.2.3", find_drafted_notes=_raises)
        == []
    )
    assert (
        _PREPARED_STOP.drafted_notes_candidates(
            repo, {"output_dir": "charness-artifacts/release"}, None, find_drafted_notes=_raises
        )
        == []
    )
    assert _PREPARED_STOP.drafted_notes_candidates(
        repo,
        {"output_dir": "charness-artifacts/release"},
        "v1.2.3",
        find_drafted_notes=lambda root, _dir, *, target_tag: [
            root / "charness-artifacts" / "release" / "notes-v1.2.3.md"
        ],
    ) == ["charness-artifacts/release/notes-v1.2.3.md"]

    # No release record at HEAD (no commits yet) -> no marker, so no prepared stop.
    assert _PREPARED_STOP.head_release_record(repo, "charness-artifacts/release/latest.md") is None
    assert (
        _PREPARED_STOP.committed_claims_record(
            repo, claims_record_in_change_set=lambda changed: None
        )
        is None
    )

    bound = repo / "charness-artifacts" / "critique" / "release-1-2-3.md"
    bound.write_text(
        "# Release critique\n\nScope and risks for the 1.2.3 candidate.\n", encoding="utf-8"
    )
    stub = repo / "charness-artifacts" / "critique" / "stub-1-2-3.md"
    stub.write_text("# 1.2.3\n", encoding="utf-8")
    untracked = repo / "charness-artifacts" / "critique" / "untracked-1-2-3.md"
    untracked.write_text(
        "# Untracked\n\nRelease: 1.2.3 and some substance here.\n", encoding="utf-8"
    )
    _git(repo, "add", str(bound), str(stub))
    _git(repo, "commit", "-m", "critique candidates")

    accepts = _PREPARED_STOP.critique_acceptor(
        repo, _CLOSEOUT_TOKENS("1.2.3"), closeout_evidence=_CLOSEOUT_EVIDENCE
    )
    assert accepts("charness-artifacts/critique/release-1-2-3.md") is True
    # Untracked: the gate's dirty-worktree refusal never says "commit this first".
    assert accepts("charness-artifacts/critique/untracked-1-2-3.md") is False
    # Stub: the gate's refusal is the exact message the resume packet exists to prevent.
    assert accepts("charness-artifacts/critique/stub-1-2-3.md") is False
    # No resolvable version -> presence-only tokens; the acceptor still requires tracked.
    assert (
        _PREPARED_STOP.critique_acceptor(
            repo, _CLOSEOUT_TOKENS(None), closeout_evidence=_CLOSEOUT_EVIDENCE
        )("charness-artifacts/critique/untracked-1-2-3.md")
        is False
    )


def test_prepared_claims_packets_are_exercised_in_process(tmp_path: Path) -> None:
    """Same reason: `prepared_claims_state`, `resume_claims_packets`, and the
    `resume_prepared_claims_review` branch of `next_action` are only ever reached through
    a subprocess planner run."""
    marker = "<!-- charness-release-state:prepared-awaiting-claims-review -->"
    RECORD = "artifacts/release/latest.md"
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "critique").mkdir(parents=True)

    assert (
        _PACKETS.prepared_claims_state(
            repo,
            current_version="1.2.3",
            binding_tokens=["1.2.3"],
            accepts=lambda _rel: True,
            marker_text="no marker here",
            release_record=RECORD,
        )
        is None
    )
    assert (
        _PACKETS.prepared_claims_state(
            repo,
            current_version="1.2.3",
            binding_tokens=["1.2.3"],
            accepts=lambda _rel: True,
            marker_text=None,
            release_record=RECORD,
        )
        is None
    )

    (repo / "charness-artifacts" / "critique" / "a.md").write_text("a\n", encoding="utf-8")
    (repo / "charness-artifacts" / "critique" / "b.md").write_text("b\n", encoding="utf-8")

    one = _PACKETS.prepared_claims_state(
        repo,
        current_version="1.2.3",
        binding_tokens=["1.2.3"],
        accepts=lambda rel: rel.endswith("a.md"),
        marker_text=marker,
        release_record=RECORD,
    )
    assert one["critique_artifact_candidates"] == ["charness-artifacts/critique/a.md"]
    assert one["tag_name"] == "v1.2.3"
    packets = {p["id"]: p for p in _PACKETS.resume_claims_packets(one)}
    assert (
        "--critique-artifact charness-artifacts/critique/a.md"
        in packets["publish-resume-execute"]["command"]
    )
    assert "<claims-review-record>" in packets["publish-resume-execute"]["command"]
    assert "--notes-file" in packets["publish-resume-execute"]["repeat_original_arguments"]
    assert _PACKETS.resume_claims_packets(None) == []

    both = _PACKETS.prepared_claims_state(
        repo,
        current_version="1.2.3",
        binding_tokens=["1.2.3"],
        accepts=lambda _rel: True,
        marker_text=marker,
        release_record=RECORD,
        committed_record="charness-artifacts/release-review/r.json",
    )
    assert len(both["critique_artifact_candidates"]) == 2
    execute = next(
        p for p in _PACKETS.resume_claims_packets(both) if p["id"] == "publish-resume-execute"
    )
    assert "<release-critique-artifact>" in execute["command"]
    assert "--claims-review-artifact charness-artifacts/release-review/r.json" in execute["command"]

    none_bound = _PACKETS.prepared_claims_state(
        repo,
        current_version="1.2.3",
        binding_tokens=["1.2.3"],
        accepts=lambda _rel: False,
        marker_text=marker,
        release_record=RECORD,
    )
    base = {"found": True, "valid": True}
    payload = {"drift": [], "git_status": ""}
    for prepared, expected in (
        (one, "--critique-artifact charness-artifacts/critique/a.md"),
        (both, "one of"),
        (none_bound, "no artifact under"),
    ):
        action = _PACKETS.next_action(
            args=_args(),
            adapter=base,
            release_payload=payload,
            target_version=None,
            update_blocker=None,
            prepared_claims=prepared,
        )
        assert action["kind"] == "resume_prepared_claims_review"
        assert expected in action["reason"]
        # The reason names the ADAPTER's record path. A second constant in the planner made
        # it blind in exactly the repos the publish helper's copy made the claims floor
        # blind: it read no marker and reported `inspect_only` at a live prepared stop.
        assert RECORD in action["reason"]


def test_resume_summary_lines_selects_scaffold_and_resume_packets() -> None:
    """The summary line is the operator-facing half of the prepared-stop repair, and it
    is only ever reached through a subprocess planner run."""
    assert _PLANNER.resume_summary_lines({}) == []
    assert _PLANNER.resume_summary_lines({"publish_packets": None}) == []
    assert _PLANNER.resume_summary_lines(
        {
            "publish_packets": [
                {"id": "publish-dry-run", "command": "not this one"},
                {"id": "claims-review-scaffold", "command": "scaffold"},
                {"id": "publish-resume-dry-run", "command": "dry"},
                {"id": "publish-resume-execute", "command": "exec"},
                {"command": "no id at all"},
            ]
        }
    ) == [
        "claims-review-scaffold: scaffold",
        "publish-resume-dry-run: dry",
        "publish-resume-execute: exec",
    ]


# Deliberately NOT `release_only`. Its siblings are excluded from the standing set for
# cost, but this one is the only in-process reader of `main()`'s summary emission, and a
# release_only test contributes no standing coverage — so excluding it left the
# operator-facing half of the prepared-stop repair as an uncovered changed line that the
# local pre-push lane skipped and CI blocked on.
def test_the_planner_summary_prints_the_resume_command_in_process(tmp_path: Path) -> None:
    """`main()`'s summary emission is only reached through a CLI subprocess, which
    in-process coverage cannot see. The summary line is the operator-facing half of the
    prepared-stop repair, so it is driven here through `main()` directly."""
    from tests.script_main import run_loaded_script_main

    repo, env, _payload = _copy_prepared_stop(tmp_path)
    with patch.object(_PLANNER._current_release, "_git_status", return_value=[]):
        result = run_loaded_script_main(
            "plan_release_run.py", _PLANNER, "--repo-root", str(repo), env=env
        )

    assert result.returncode == 0, result.stderr
    assert "next_action=resume_prepared_claims_review" in result.stdout
    assert "publish-resume-dry-run: " in result.stdout
    assert "publish-resume-execute: " in result.stdout
    assert "--claims-review-artifact" in result.stdout
