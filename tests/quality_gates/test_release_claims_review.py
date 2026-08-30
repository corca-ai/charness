"""Topology proof for the prepared-record claims-review boundary."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from .release_publish_fixtures import (
    _release_env,
    _run_publish,
    _seed_publish_release_repo,
    claims_review_narrative,
    claims_review_record,
    commit_claims_review,
)
from .release_script_loading import load_release_script

CLAIMS_REVIEW = load_release_script("publish_release_claims_review", suffix="topology")
CLAIMS_EVIDENCE = load_release_script("claims_review_evidence", suffix="topology")


# The prepare-path precondition lives with the prepare process it protects.
EXECUTE = load_release_script("publish_release_execute", suffix="claims_stop")
PREFLIGHT = load_release_script("publish_release_preflight", suffix="claims_stop")
SECTIONS = load_release_script("publish_release_artifact_sections", suffix="claims")
NARRATIVE_PATH = "charness-artifacts/release-review/narrative.md"


def _record(payload: dict, prepared_commit: str, prepared_record: str, narrative_path: str = NARRATIVE_PATH) -> str:
    return (
        json.dumps(
            claims_review_record(
                prepared_commit=prepared_commit,
                prepared_record=prepared_record,
                target_version=payload["target_version"],
                tag_name=payload["tag_name"],
                narrative_path=narrative_path,
            )
        )
        + "\n"
    )


def _write_narrative(repo: Path, prepared_commit: str, payload: dict, narrative_path: str = NARRATIVE_PATH) -> str:
    path = repo / narrative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(claims_review_narrative(prepared_commit, payload["target_version"]), encoding="utf-8")
    return narrative_path


def _run(command: list[str], *, cwd: Path, check: bool = True):
    return subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)


def _source_bound_evidence(tmp_path: Path):
    repo, remote, bin_dir = _seed_publish_release_repo(tmp_path)
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
    path = commit_claims_review(
        repo,
        prepared_commit=commit,
        prepared_record=record,
        target_version=payload["target_version"],
        tag_name=payload["tag_name"],
        stem="source-claims",
    )
    return repo, remote, bin_dir, env, payload, path


@pytest.mark.release_only
def test_claims_review_rejects_non_direct_and_merge_evidence(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    prepared_run = _run_publish(
        repo,
        _release_env(tmp_path, bin_dir),
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert prepared_run.returncode == 0, prepared_run.stderr
    payload = yaml.safe_load(prepared_run.stdout)
    prepared_commit = payload["prepared_release_commit"]
    prepared_record = _run(["git", "show", f"{prepared_commit}:charness-artifacts/release/latest.md"], cwd=repo).stdout
    review_path = "charness-artifacts/release-review/non-direct.json"
    readme = repo / "README.md"
    original = readme.read_text(encoding="utf-8")

    # P -> X -> R restores X, so its net tree delta looks evidence-only.
    readme.write_text(original + "intermediate change\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", "Intermediary source change"], cwd=repo)
    review = repo / review_path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(_record(payload, prepared_commit, prepared_record), encoding="utf-8")
    narrative = _write_narrative(repo, prepared_commit, payload)
    readme.write_text(original, encoding="utf-8")
    _run(["git", "add", "README.md", review_path, narrative], cwd=repo)
    _run(["git", "commit", "-m", "Record non-direct claims review"], cwd=repo)
    evidence = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    prepared = {
        "commit": prepared_commit,
        "path": "charness-artifacts/release/latest.md",
        "sha256": hashlib.sha256(prepared_record.encode("utf-8")).hexdigest(),
    }
    with pytest.raises(SystemExit, match="direct child"):
        CLAIMS_REVIEW.validate_claims_review(
            repo,
            prepared=prepared,
            evidence_commit=evidence,
            artifact_path=review_path,
            target_version=payload["target_version"],
            tag_name=payload["tag_name"],
            run=_run,
        )

    # A merge with P as first parent is not a one-parent reviewer handoff.
    _run(["git", "checkout", "-B", "claims-side", prepared_commit], cwd=repo)
    readme.write_text(original + "merge-side change\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", "Merge-side source change"], cwd=repo)
    _run(["git", "checkout", "-B", "main", prepared_commit], cwd=repo)
    _run(["git", "merge", "--no-ff", "--no-commit", "claims-side"], cwd=repo)
    readme.write_text(original, encoding="utf-8")
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(_record(payload, prepared_commit, prepared_record), encoding="utf-8")
    _write_narrative(repo, prepared_commit, payload)
    _run(["git", "add", "README.md", review_path, NARRATIVE_PATH], cwd=repo)
    _run(["git", "commit", "-m", "Merge claims review"], cwd=repo)
    merge = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    with pytest.raises(SystemExit, match="direct child"):
        CLAIMS_REVIEW.validate_claims_review(
            repo,
            prepared=prepared,
            evidence_commit=merge,
            artifact_path=review_path,
            target_version=payload["target_version"],
            tag_name=payload["tag_name"],
            run=_run,
        )


@pytest.mark.release_only
def test_resume_refuses_inherited_prepared_marker_before_auth_or_publish(tmp_path: Path) -> None:
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
    prepared_commit = payload["prepared_release_commit"]
    prepared_record = _run(["git", "show", f"{prepared_commit}:charness-artifacts/release/latest.md"], cwd=repo).stdout
    review_path = "charness-artifacts/release-review/inherited-marker.json"
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "unreviewed X\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", payload["commit_message"]], cwd=repo)
    review = repo / review_path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(_record(payload, prepared_commit, prepared_record), encoding="utf-8")
    narrative = _write_narrative(repo, prepared_commit, payload)
    _run(["git", "add", review_path, narrative], cwd=repo)
    _run(["git", "commit", "-m", "Record inherited-marker claims review"], cwd=repo)
    gh_log, git_log = tmp_path / "gh-log.json", tmp_path / "git-log.json"
    prior_gh = json.loads(gh_log.read_text(encoding="utf-8"))
    prior_git = json.loads(git_log.read_text(encoding="utf-8"))

    refused = _run_publish(
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

    assert refused.returncode != 0
    # The refusal is now the specific one: the marker is present at HEAD but no
    # single-parent prepared boundary exists, so the claims floor cannot run. Previously
    # this reached the generic "nothing to resume", which is the same refusal a
    # marker-free tree gets and does not say the claims floor was skipped.
    assert "no single-parent prepared boundary" in refused.stderr
    assert "prepared-awaiting-claims-review" in refused.stderr
    assert ["auth", "status"] not in json.loads(gh_log.read_text(encoding="utf-8"))[len(prior_gh) :]
    new_git = json.loads(git_log.read_text(encoding="utf-8"))[len(prior_git) :]
    assert ["push", "origin", "main", "v0.0.1"] not in new_git
    assert ["tag", "v0.0.1"] not in new_git


@pytest.mark.release_only
def test_prepared_record_refuses_merge_that_inherits_marker_from_second_parent(
    tmp_path: Path,
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    base = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    prepared = _run_publish(
        repo,
        _release_env(tmp_path, bin_dir),
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert prepared.returncode == 0, prepared.stderr
    prepared_commit = yaml.safe_load(prepared.stdout)["prepared_release_commit"]
    _run(["git", "checkout", "-B", "merge-first-parent", base], cwd=repo)
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "first-parent source change\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", "First parent before prepared marker"], cwd=repo)
    _run(["git", "merge", "--no-ff", "--no-commit", prepared_commit], cwd=repo)
    _run(["git", "commit", "-m", "Merge prepared marker from second parent"], cwd=repo)
    merge = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()

    assert CLAIMS_REVIEW.prepared_record(repo, commit=merge, record_path="charness-artifacts/release/latest.md", run=_run) is None


def test_claims_review_refuses_invalid_paths_tree_and_bindings(tmp_path: Path) -> None:
    prepared = {
        "commit": "prepared",
        "path": "charness-artifacts/release/latest.md",
        "sha256": "record-sha",
    }

    def invoke(path: str | None, responses: dict[tuple[str, ...], tuple[int, str]]):
        def run(command: list[str], *, cwd: Path, check: bool = True):
            code, stdout = responses.get(tuple(command), (0, ""))
            return subprocess.CompletedProcess(command, code, stdout=stdout)

        return CLAIMS_REVIEW.validate_claims_review(
            tmp_path,
            prepared=prepared,
            evidence_commit="evidence",
            artifact_path=path,
            target_version="1.2.3",
            tag_name="v1.2.3",
            run=run,
        )

    with pytest.raises(SystemExit, match="normalized repo-relative"):
        invoke("../review.json", {})
    with pytest.raises(SystemExit, match=r"\.json file under"):
        invoke("charness-artifacts/other/review.txt", {})

    parents = ("git", "show", "-s", "--format=%P", "evidence")
    diff = ("git", "diff-tree", "--no-commit-id", "--name-only", "-r", "prepared", "evidence")
    path = "charness-artifacts/release-review/review.json"
    with pytest.raises(SystemExit, match="must change only"):
        invoke(path, {parents: (0, "prepared\n"), diff: (0, "README.md\n")})
    with pytest.raises(SystemExit, match="not committed"):
        invoke(
            path,
            {
                parents: (0, "prepared\n"),
                diff: (0, path + "\n"),
                ("git", "show", f"evidence:{path}"): (1, ""),
            },
        )
    with pytest.raises(SystemExit, match="not valid JSON"):
        invoke(
            path,
            {
                parents: (0, "prepared\n"),
                diff: (0, path + "\n"),
                ("git", "show", f"evidence:{path}"): (0, "{"),
            },
        )
    # Not a JSON object at all, and a bound-looking object with a wrong field: two
    # different refusal sites that carry the same message.
    with pytest.raises(SystemExit, match="does not bind"):
        invoke(
            path,
            {
                parents: (0, "prepared\n"),
                diff: (0, path + "\n"),
                ("git", "show", f"evidence:{path}"): (0, "[]"),
            },
        )
    with pytest.raises(SystemExit, match="does not bind"):
        invoke(
            path,
            {
                parents: (0, "prepared\n"),
                diff: (0, path + "\n"),
                ("git", "show", f"evidence:{path}"): (0, "{}"),
            },
        )
    bound = {
        "schema_version": "charness.release.claims-review.v4",
        "prepared_commit": "prepared",
        "release_record_path": "charness-artifacts/release/latest.md",
        "release_record_sha256": "record-sha",
        "target_version": "1.2.3",
        "tag_name": "v1.2.3",
        "verdict": "unproven",
        "preparer_context": "same",
        "reviewer_context": "same",
        "observer_distinctness": {
            "kind": "unproven",
            "signal": "fixture could not establish a reviewer",
            "review_artifact": None,
        },
    }
    with pytest.raises(SystemExit, match="distinct nonempty"):
        invoke(
            path,
            {
                parents: (0, "prepared\n"),
                diff: (0, path + "\n"),
                ("git", "show", f"evidence:{path}"): (0, json.dumps(bound)),
            },
        )


def _distinctness_invoke(tmp_path: Path):
    """Drive `validate_claims_review` against a stubbed git so each refusal branch of the
    distinctness floor is reachable without building a repository per case."""
    prepared = {
        "commit": "prepared0123456789",
        "path": "charness-artifacts/release/latest.md",
        "sha256": "record-sha",
    }
    record_path = "charness-artifacts/release-review/review.json"
    narrative_path = "charness-artifacts/release-review/review.md"
    parents = ("git", "show", "-s", "--format=%P", "evidence")
    diff = (
        "git",
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        prepared["commit"],
        "evidence",
    )
    status = (
        "git",
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "-r",
        prepared["commit"],
        "evidence",
    )
    shallow = ("git", "rev-parse", "--is-shallow-repository")
    describe = (
        "git",
        "describe",
        "--tags",
        "--abbrev=0",
        "--match",
        "v[0-9]*.[0-9]*.[0-9]*",
        f"{prepared['commit']}^",
    )
    ancestor = ("git", "merge-base", "--is-ancestor", "v1.2.2", prepared["commit"])
    release_delta = (
        "git",
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        f"v1.2.2..{prepared['commit']}",
    )

    def invoke(
        record: dict,
        *,
        changed: list[str] | None = None,
        narrative: str | None = "default",
        narrative_status: str = "A",
    ):
        if narrative == "default":
            narrative = claims_review_narrative(prepared["commit"], "1.2.3")
        changed = [record_path, narrative_path] if changed is None else changed
        responses = {
            parents: (0, prepared["commit"] + "\n"),
            diff: (0, "".join(f"{line}\n" for line in changed)),
            status: (
                0,
                "".join(f"{narrative_status if line.endswith('.md') else 'M'}\t{line}\n" for line in changed),
            ),
            shallow: (0, "false\n"),
            describe: (0, "v1.2.2\n"),
            ancestor: (0, ""),
            release_delta: (0, "scripts/fixture_shipped.py\n"),
            ("git", "show", f"evidence:{record_path}"): (0, json.dumps(record)),
        }
        if narrative is not None:
            responses[("git", "show", f"evidence:{narrative_path}")] = (0, narrative)

        def run(command: list[str], *, cwd: Path, check: bool = True):
            code, stdout = responses.get(tuple(command), (1, ""))
            return subprocess.CompletedProcess(command, code, stdout=stdout)

        return CLAIMS_REVIEW.validate_claims_review(
            tmp_path,
            prepared=prepared,
            evidence_commit="evidence",
            artifact_path=record_path,
            target_version="1.2.3",
            tag_name="v1.2.3",
            run=run,
        )

    def record(**overrides) -> dict:
        base = claims_review_record(
            prepared_commit=prepared["commit"],
            prepared_record="",
            target_version="1.2.3",
            tag_name="v1.2.3",
            narrative_path=narrative_path,
        )
        base["release_record_sha256"] = "record-sha"
        base["scope_basis"] = {
            "base_ref": "v1.2.2",
            "changed_paths_sha256": hashlib.sha256(b"scripts/fixture_shipped.py").hexdigest(),
            "changed_path_count": 1,
        }
        base.update(overrides)
        if base["verdict"] == "unproven":
            for field in ("review_scope", "scope_basis", "advisory_findings"):
                base.pop(field, None)
        return base

    return invoke, record, prepared, narrative_path


def test_distinctness_must_be_declared_not_inferred(tmp_path: Path) -> None:
    """The reported defect exactly: two unequal strings and nothing that says what
    relationship they stand in. The publication boundary already requires the other
    release verdict to name its observer as a recorded observable; this makes the claims
    verdict match."""
    invoke, record, _prepared, _narrative = _distinctness_invoke(tmp_path)
    missing = record()
    del missing["observer_distinctness"]
    with pytest.raises(SystemExit, match=r"missing=\['observer_distinctness'\]"):
        invoke(missing)
    with pytest.raises(SystemExit, match="must name the concrete signal"):
        invoke(
            record(
                observer_distinctness={
                    "kind": "separate-host",
                    "signal": "  ",
                    "review_artifact": _narrative,
                }
            )
        )


def test_a_same_agent_reread_has_no_passing_kind(tmp_path: Path) -> None:
    """A same-agent reread is the observer this floor exists to exclude, so it must not
    be spellable as a `pass` at all -- its honest record is `verdict: unproven`."""
    invoke, record, _prepared, narrative_path = _distinctness_invoke(tmp_path)
    for kind in ("same-agent", "self", "unproven"):
        with pytest.raises(SystemExit, match="must be one of"):
            invoke(
                record(
                    observer_distinctness={
                        "kind": kind,
                        "signal": "same session reread",
                        "review_artifact": narrative_path,
                    }
                )
            )


def test_an_unproven_verdict_is_accepted_with_its_concrete_signal(tmp_path: Path) -> None:
    """`critique-boundary.md` already names this behaviour -- record the concrete signal
    and publish with the review unproven rather than substituting a same-agent reread --
    and the validator previously provided no way to express it, leaving `verdict: pass`
    as a spawn-blocked session's only path forward."""
    invoke, record, _prepared, _narrative = _distinctness_invoke(tmp_path)
    result = invoke(
        record(
            verdict="unproven",
            observer_distinctness={
                "kind": "unproven",
                "signal": "host rejected the subagent spawn: Agent tool not exposed",
                "review_artifact": None,
            },
        ),
        changed=["charness-artifacts/release-review/review.json"],
        narrative=None,
    )
    assert result["verdict"] == "unproven"
    assert result["observer_distinctness"]["signal"].startswith("host rejected")
    assert result["observer_distinctness"]["review_artifact"] is None

    with pytest.raises(SystemExit, match="requires `observer_distinctness.kind"):
        invoke(
            record(
                verdict="unproven",
                observer_distinctness={
                    "kind": "separate-host",
                    "signal": "s",
                    "review_artifact": None,
                },
            ),
            changed=["charness-artifacts/release-review/review.json"],
            narrative=None,
        )


def test_an_unknown_verdict_is_refused(tmp_path: Path) -> None:
    invoke, record, _prepared, _narrative = _distinctness_invoke(tmp_path)
    with pytest.raises(SystemExit, match="`verdict` must be one of"):
        invoke(record(verdict="blocked"))


def test_a_pass_must_carry_the_product_of_the_review_it_asserts(tmp_path: Path) -> None:
    """The v5.1.0 record that passed the old floor was 11 lines: a verdict and two context
    strings, with none of the products a claims reviewer is asked to produce."""
    invoke, record, prepared, narrative_path = _distinctness_invoke(tmp_path)
    # A narrative the evidence commit does not carry at all is refused by the
    # added-not-edited check, which is the accurate description of that input.
    with pytest.raises(SystemExit, match="must be ADDED by the evidence commit"):
        invoke(record(), narrative=None, changed=["charness-artifacts/release-review/review.json"])
    # Recorded as added but unreadable at that commit: a distinct refusal, because the
    # name-status and the blob are two different reads and either can be the liar.
    with pytest.raises(SystemExit, match="not committed at the evidence commit"):
        invoke(record(), narrative=None, narrative_status="A")
    with pytest.raises(SystemExit, match="under 500 bytes"):
        invoke(record(), narrative="# Claims review\n\nlooks fine to me\n")
    # Bound to THIS release: an earlier release's narrative cannot be re-pointed.
    with pytest.raises(SystemExit, match="must name the prepared commit"):
        invoke(record(), narrative=claims_review_narrative("otherprepared99", "9.9.9"))
    accepted = invoke(record())
    assert accepted["verdict"] == "pass"
    assert accepted["observer_distinctness"]["review_artifact"] == narrative_path
    assert prepared["commit"][:12] in claims_review_narrative(prepared["commit"], "1.2.3")


def test_the_evidence_commit_may_carry_only_the_named_review_files(tmp_path: Path) -> None:
    """Allowing the narrative through must not reopen the ride-along it replaced."""
    invoke, record, _prepared, _narrative = _distinctness_invoke(tmp_path)
    with pytest.raises(SystemExit, match="must change only claims-review evidence"):
        invoke(record(), changed=["charness-artifacts/release-review/review.json", "README.md"])
    with pytest.raises(SystemExit, match="and the review_artifact it names"):
        invoke(
            record(),
            changed=[
                "charness-artifacts/release-review/review.json",
                "charness-artifacts/release-review/review.md",
                "charness-artifacts/release-review/extra.md",
            ],
            narrative_status="A",
        )


def test_the_narrative_must_be_added_by_the_evidence_commit_not_appended_to(tmp_path: Path) -> None:
    """The cheapest accepted `pass` round 2 found, and it cost one line. The byte floor
    and the naming check both read the whole FILE, so an earlier release's 4 KB narrative
    with `Re-checked for prepared commit <sha>, target version 1.2.3.` appended clears 500
    bytes (inherited) and names this commit and version (appended). The review's product
    is produced BY this review, so it must be new."""
    invoke, record, _prepared, _narrative = _distinctness_invoke(tmp_path)
    with pytest.raises(SystemExit, match="must be ADDED by the evidence commit"):
        invoke(record(), narrative_status="M")
    # Added is still accepted, so the floor narrows rather than disarming.
    assert invoke(record(), narrative_status="A")["verdict"] == "pass"


@pytest.mark.release_only
def test_publish_cli_refuses_claims_artifact_without_resume(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    result = _run_publish(
        repo,
        _release_env(tmp_path, bin_dir),
        "--part",
        "patch",
        "--claims-review-artifact",
        "charness-artifacts/release-review/review.json",
    )

    assert result.returncode != 0
    assert "only valid with --resume --publish-current" in result.stderr


@pytest.mark.release_only
@pytest.mark.parametrize("remote_leg", ["tag", "branch"])
def test_source_resume_repairs_only_the_missing_claims_publication_leg(tmp_path: Path, remote_leg: str) -> None:
    repo, _remote, _bin_dir, env, payload, path = _source_bound_evidence(tmp_path)
    if remote_leg == "tag":
        _run(["git", "tag", payload["tag_name"], payload["prepared_release_commit"]], cwd=repo)
        _run(["git", "push", "origin", payload["tag_name"]], cwd=repo)
    else:
        _run(["git", "push", "origin", "main"], cwd=repo)
    git_log = tmp_path / "git-log.json"
    before = json.loads(git_log.read_text(encoding="utf-8"))

    resumed = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--claims-review-artifact",
        path,
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert resumed.returncode == 0, resumed.stderr
    new = json.loads(git_log.read_text(encoding="utf-8"))[len(before) :]
    expected = ["push", "origin", "main"] if remote_leg == "tag" else ["push", "origin", payload["tag_name"]]
    assert expected in new


@pytest.mark.release_only
def test_a_second_prepare_over_an_outstanding_marker_cannot_publish_unreviewed(
    tmp_path: Path,
) -> None:
    """The fall-through the claims floor could not see. `prepared_record` declines when the
    marker is INHERITED rather than introduced -- correct for choosing the review boundary,
    wrong as a lane selector. Every prepared branch then declined, the phase fell back to
    the legacy marker-free lane, and that lane never calls `validate_claims_review` at all:
    a release published with no claims review and no refusal.

    The trigger is the likeliest action at a prepared stop, because the stop exists to
    surface record blockers -- the operator re-prepares after finding one. `--execute` now
    refuses that route outright (asserted below), so the state is built here the way the
    routes it cannot guard still build it: a marker-bearing commit on top of the stop from
    an older helper build, a hand-authored commit, or a cherry-pick. Both layers are
    proven -- the CLI will not create this state, and the resume refuses it if it exists."""
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    first = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert first.returncode == 0, first.stderr
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
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "second marked release commit\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", yaml.safe_load(first.stdout)["commit_message"]], cwd=repo)
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
    assert "no single-parent prepared boundary" in refused.stderr
    new_gh = json.loads(gh_log.read_text(encoding="utf-8"))[len(prior_gh) :]
    new_git = json.loads(git_log.read_text(encoding="utf-8"))[len(prior_git) :]
    assert not any(entry[:2] == ["release", "create"] for entry in new_gh)
    assert ["auth", "status"] not in new_gh
    assert not any(entry and entry[0] == "push" for entry in new_git)


@pytest.mark.release_only
def test_a_claims_artifact_supplied_outside_the_claims_lane_is_refused(tmp_path: Path) -> None:
    """Accepted-and-ignored was the worse half of the fall-through: the operator supplies
    a real record, the planner told them to, and nothing ever opened it. The marker is
    removed here so the resume resolves to the legacy lane, which is the state in which
    the flag is meaningless."""
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
    record = repo / "charness-artifacts" / "release" / "latest.md"
    record.write_text(
        "\n".join(line for line in record.read_text(encoding="utf-8").splitlines() if "prepared-awaiting-claims-review" not in line) + "\n",
        encoding="utf-8",
    )
    _run(["git", "add", "-A"], cwd=repo)
    _run(["git", "commit", "--amend", "--no-edit"], cwd=repo)
    gh_log, git_log = tmp_path / "gh-log.json", tmp_path / "git-log.json"
    prior_gh = json.loads(gh_log.read_text(encoding="utf-8"))
    prior_git = json.loads(git_log.read_text(encoding="utf-8"))

    refused = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--claims-review-artifact",
        "charness-artifacts/release-review/absent.json",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert refused.returncode != 0
    assert "does not read it" in refused.stderr
    new_gh = json.loads(gh_log.read_text(encoding="utf-8"))[len(prior_gh) :]
    new_git = json.loads(git_log.read_text(encoding="utf-8"))[len(prior_git) :]
    assert ["auth", "status"] not in new_gh
    assert not any(entry and entry[0] == "push" for entry in new_git)


@pytest.mark.release_only
def test_an_unproven_verdict_publishes_but_says_so_on_stderr(tmp_path: Path) -> None:
    """`unproven` is a first-class state: publication proceeds, and the operator is told
    at the boundary that the distinct-observer property was never established. stderr
    carries it to the operator standing at the boundary; the published release record
    carries it to the readers outside the session who only ever see that record."""
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
        stem="unproven-claims",
        verdict="unproven",
        kind="unproven",
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
    assert "verdict is `unproven`" in resumed.stderr
    assert "was NOT established" in resumed.stderr
    final = yaml.safe_load(resumed.stdout)
    assert final["claims_review"]["verdict"] == "unproven"
    assert final["claims_review"]["observer_distinctness"]["review_artifact"] is None
    # The record a reader outside the session gets. The bare token would reproduce the
    # fail-quiet one layer over: a `## Claims Review` heading reads as "a review happened".
    published = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "## Claims Review" in published
    assert "the distinct-observer property was NOT established" in published
    assert "recorded absence, not a passing review" in published
