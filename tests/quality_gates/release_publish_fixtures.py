from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.yaml_output import render_yaml

from .issue_closeout_support import bug_closeout_body

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLISH_SCRIPT = "skills/public/release/scripts/publish_release.py"
REVIEW_GATE_SCRIPT = "skills/public/release/scripts/check_requested_review_gate.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _write_exec(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _make_release_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    return tmp_path / "repo", tmp_path / "remote.git", tmp_path / "bin"


def _prepare_release_tree(repo: Path, remote: Path, bin_dir: Path) -> None:
    repo.mkdir()
    remote.mkdir()
    bin_dir.mkdir()
    (repo / ".agents").mkdir(parents=True)
    (repo / "packaging").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)


def _write_release_adapter(repo: Path) -> None:
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/release",
                "preset_id: portable-defaults",
                "customized_from: portable-defaults",
                "package_id: demo",
                "packaging_manifest_path: packaging/demo.json",
                "materialized_plugin_root: plugins/demo",
                "sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .",
                "quality_command: ./scripts/run-quality.sh",
                "post_publish_distinct_channel_probe: distinct-channel-probe {tag}",
                "update_instructions:",
                "- Run `demo update`.",
                "- Restart the host if the previous version is still visible.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.0.0",
                "summary": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "source": {
                    "readme": "README.md",
                    "skills_dir": "skills",
                    "public_skills_dir": "skills/public",
                    "support_skills_dir": "skills/support",
                    "profiles_dir": "profiles",
                    "presets_dir": "presets",
                    "integrations_dir": "integrations/tools",
                },
                "codex": {"manifest": {"version": "0.0.0"}},
                "claude": {"manifest": {"version": "0.0.0"}},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _install_fake_git(bin_dir: Path, *, real_git: str | None = None) -> None:
    script = bin_dir / "git"
    real_git = real_git or shutil.which("git") or "/usr/bin/git"
    script.write_text(
        (FIXTURES / "release_publish_fake_git.sh")
        .read_text(encoding="utf-8")
        .replace("__REAL_GIT__", shlex.quote(real_git)),
        encoding="utf-8",
    )
    script.chmod(0o755)


def _write_fake_git(repo: Path, bin_dir: Path) -> None:
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    _install_fake_git(bin_dir)


def _write_sync_script(repo: Path) -> None:
    script = repo / "scripts" / "sync_root_plugin_manifests.py"
    shutil.copy2(FIXTURES / "release_publish_sync_root_plugin_manifests.py", script)
    script.chmod(0o755)


def _write_quality_script(repo: Path) -> None:
    script = repo / "scripts" / "run-quality.sh"
    shutil.copy2(FIXTURES / "release_publish_run_quality.sh", script)
    script.chmod(0o755)


def _write_fake_gh(bin_dir: Path) -> None:
    script = bin_dir / "gh"
    shutil.copy2(FIXTURES / "release_publish_fake_gh.py", script)
    script.chmod(0o755)


def _write_fake_distinct_channel_probe(bin_dir: Path) -> None:
    """A network-free stand-in for the rung-2 distinct-channel probe. Exit 0
    (confirmed) by default; ``FAKE_DISTINCT_CHANNEL_RESULT=fail`` -> exit 1
    (a typed non-`verified` disposition). It logs its invocation so a test can
    assert the distinct channel ran and is NOT `gh release view`."""
    script = bin_dir / "distinct-channel-probe"
    shutil.copy2(FIXTURES / "release_publish_distinct_channel_probe.py", script)
    script.chmod(0o755)


def _setup_git(repo: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)


def _attach_remote_and_push(repo: Path, remote: Path) -> None:
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo, check=True, capture_output=True, text=True)


def ensure_fixture_release_base(repo: Path) -> None:
    """Give claims-review fixtures a prior release without changing the shared seed."""
    present = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/tags/v0.0.0"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if present.returncode == 0:
        return
    root = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()[0]
    subprocess.run(
        ["git", "tag", "v0.0.0", root],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "push", "origin", "v0.0.0"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _build_release_publish_seed(staging: Path) -> None:
    repo = staging / "repo"
    remote = staging / "remote.git"
    bin_dir = staging / "bin"
    _prepare_release_tree(repo, remote, bin_dir)
    subprocess.run(
        ["git", "init", "--bare", str(remote)],
        check=True,
        capture_output=True,
        text=True,
    )
    _write_release_adapter(repo)
    _write_fake_git(repo, bin_dir)
    _write_sync_script(repo)
    _write_quality_script(repo)
    _write_fake_gh(bin_dir)
    _write_fake_distinct_channel_probe(bin_dir)
    _setup_git(repo)


def release_publish_seed(*, cache_get_or_build=None) -> Path:
    """Return one source-bound immutable release-fixture bundle.

    The bundle contains a committed repository with no remote, an empty bare remote,
    and the static fake-tool binaries. Tests copy all three parts before attaching the
    test-local remote, so pushes, tags, and readbacks remain per-test operations.
    ``cache_get_or_build`` is injectable only for the focused wiring test.
    """
    if cache_get_or_build is None:
        from tests.seed_cache import get_or_build

        cache_get_or_build = get_or_build
    return cache_get_or_build("release-publish-repo-seed", _build_release_publish_seed)


def _copy_release_publish_seed(tmp_path: Path, seed: Path) -> tuple[Path, Path, Path]:
    repo, remote, bin_dir = _make_release_paths(tmp_path)
    shutil.copytree(seed / "repo", repo)
    shutil.copytree(seed / "remote.git", remote)
    shutil.copytree(seed / "bin", bin_dir)
    _attach_remote_and_push(repo, remote)
    return repo, remote, bin_dir


def _seed_publish_release_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    return _copy_release_publish_seed(tmp_path, release_publish_seed())


def _simulate_partial_publish(
    repo: Path,
    *,
    closeout_body: str | None = None,
    create_tag: bool = True,
) -> None:
    """Materialize a valid generated surface in the resumable partial-publish fixture."""
    output_dir = repo / "charness-artifacts" / "release"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest.md").write_text("# Release demo 0.0.0 (partial)\n", encoding="utf-8")
    # Resume revalidates generated surfaces after claims review. Keep this success
    # fixture synced; an absent tree belongs in a refusal fixture instead.
    subprocess.run(
        [sys.executable, str(repo / "scripts" / "sync_root_plugin_manifests.py"), "--repo-root", str(repo)],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    commit_args = ["git", "commit", "-m", "Release demo 0.0.0"]
    if closeout_body is not None:
        commit_args.extend(["-m", closeout_body])
    subprocess.run(commit_args, cwd=repo, check=True, capture_output=True, text=True)
    if create_tag:
        subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)


def _release_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
    env["FAKE_GH_RELEASE_ASSET_STATE"] = str(tmp_path / "release-assets.json")
    env["FAKE_DISTINCT_CHANNEL_LOG"] = str(tmp_path / "distinct-channel-log.json")
    return env


def _run_publish(repo: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", PUBLISH_SCRIPT, "--repo-root", str(repo), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def claims_review_narrative(prepared_commit: str, target_version: str) -> str:
    """A claims-review narrative of the shape the v2 floor requires.

    The v1 floor accepted an 11-line JSON carrying a verdict and two context strings and
    no product of a review at all; the narrative is what a `pass` now has to carry, bound
    to this exact prepared commit so an earlier release's record cannot be re-pointed."""
    return (
        f"# Claims review for {target_version}\n\n"
        f"Prepared commit: {prepared_commit}\n\n"
        "## Re-derived figures\n\n"
        "- Version claim in the release record matches the bumped manifest version.\n"
        "- Gate counts in the record match the quality receipt they cite.\n\n"
        "## Reasons checked against their citations\n\n"
        "- Each recorded reason cites a path that exists at the prepared commit.\n\n"
        "## Claimed-as-proven that was only reasoned about\n\n"
        "- None found in this synthetic fixture record.\n\n"
        "## Promised verification steps against recorded evidence\n\n"
        "- Every promised step names a receipt in the prepared release record.\n"
    )


def claims_review_record(
    *,
    prepared_commit: str,
    prepared_record: str,
    target_version: str,
    tag_name: str,
    narrative_path: str,
    verdict: str = "pass",
    kind: str = "separate-agent-context",
    release_record_path: str = "charness-artifacts/release/latest.md",
) -> dict:
    record = {
        "schema_version": "charness.release.claims-review.v4",
        "prepared_commit": prepared_commit,
        "release_record_path": release_record_path,
        "release_record_sha256": hashlib.sha256(prepared_record.encode("utf-8")).hexdigest(),
        "target_version": target_version,
        "tag_name": tag_name,
        "verdict": verdict,
        "preparer_context": "fixture-preparer",
        "reviewer_context": "fixture-reviewer",
        "observer_distinctness": {
            "kind": kind,
            "signal": "fixture harness records a bounded reviewer in a separate agent context",
            "review_artifact": narrative_path,
        },
    }
    if verdict == "unproven":
        record["observer_distinctness"]["review_artifact"] = None
    else:
        # v3: a `pass` declares what it covered and what it waived. Required so a
        # scope split can never become a way to launder findings out of a release.
        record["review_scope"] = {
            "blocking_paths": ["scripts/fixture_shipped.py"],
            "advisory_paths": [],
        }
        record["scope_basis"] = {
            "base_ref": "refs/tags/v0.0.0",
            "changed_paths_sha256": "fixture-overwritten-after-scope-derivation",
            "changed_path_count": 1,
        }
        record["advisory_findings"] = []
    return record


def _derive_review_scope(repo: Path, prepared_commit: str) -> tuple[dict[str, list[str]], dict]:
    """Partition the real prepared-commit delta, the way a reviewer would."""
    import sys as _sys
    release_scripts = REPO_ROOT / "skills" / "public" / "release" / "scripts"
    if str(release_scripts) not in _sys.path:
        _sys.path.insert(0, str(release_scripts))
    from claims_review_scope import changed_paths_sha256, partition  # noqa: PLC0415

    described = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", f"{prepared_commit}^"],
        cwd=repo, capture_output=True, text=True,
    )
    base = described.stdout.strip()
    # No previous tag is the NORMAL case in a seeded harness repo. Fall back to
    # the prepared commit's own diff, which is still a real delta -- returning
    # empty lists produced a record the validator then refused for having "a
    # pass over no blocking surface", i.e. the fixture failing its own floor.
    span = f"{base}..{prepared_commit}" if (described.returncode == 0 and base) else prepared_commit
    listed = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", span],
        cwd=repo, capture_output=True, text=True,
    )
    paths = [line for line in listed.stdout.splitlines() if line]
    split = partition(paths)
    return (
        {"blocking_paths": split["blocking"], "advisory_paths": split["advisory"]},
        {
            "base_ref": f"refs/tags/{base}" if base else "<fixture-no-release-base>",
            "changed_paths_sha256": changed_paths_sha256(paths),
            "changed_path_count": len(set(paths)),
        },
    )


def commit_claims_review(
    repo: Path,
    *,
    prepared_commit: str,
    prepared_record: str,
    target_version: str,
    tag_name: str,
    stem: str,
    verdict: str = "pass",
    kind: str = "separate-agent-context",
    release_record_path: str = "charness-artifacts/release/latest.md",
) -> str:
    """Write and commit the v4 record plus its narrative; return the record's path."""
    ensure_fixture_release_base(repo)
    review_path = f"charness-artifacts/release-review/{stem}.json"
    narrative_path = f"charness-artifacts/release-review/{stem}.md"
    record = claims_review_record(
        prepared_commit=prepared_commit, prepared_record=prepared_record,
        target_version=target_version, tag_name=tag_name, narrative_path=narrative_path,
        verdict=verdict, kind=kind, release_record_path=release_record_path,
    )
    if verdict == "pass":
        # DERIVE the scope from the repo, exactly as a real reviewer must: the
        # record is the prepared commit's child, so the delta is knowable when
        # it is written. A hardcoded scope here would make the fixture pass a
        # completeness check that no real record could satisfy.
        record["review_scope"], record["scope_basis"] = _derive_review_scope(repo, prepared_commit)
    paths = [review_path]
    (repo / review_path).parent.mkdir(parents=True, exist_ok=True)
    (repo / review_path).write_text(json.dumps(record) + "\n", encoding="utf-8")
    if record["observer_distinctness"]["review_artifact"]:
        (repo / narrative_path).write_text(
            claims_review_narrative(prepared_commit, target_version), encoding="utf-8"
        )
        paths.append(narrative_path)
    subprocess.run(["git", "add", *paths], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Record claims review"], cwd=repo, check=True,
                   capture_output=True, text=True)
    return review_path


def _run_publish_patch(repo: Path, env: dict[str, str], *extra: str) -> subprocess.CompletedProcess[str]:
    # The release critique gate refuses publish unless one of
    # --critique-artifact / --critique-blocked is supplied. Tests that already
    # pass a critique flag are honored; tests that target a downstream failure
    # get a synthetic blocked-skip injected so they still reach their assertion.
    has_critique_flag = any(arg in ("--critique-artifact", "--critique-blocked") for arg in extra)
    extras = list(extra)
    has_close_issue = "--close-issue" in extras
    has_close_issue_classification = "--close-issue-classification" in extras
    has_close_issue_carrier_file = "--close-issue-carrier-file" in extras
    if has_close_issue and not has_close_issue_classification:
        extras.extend(["--close-issue-classification", "bug"])
    if has_close_issue and not has_close_issue_carrier_file:
        carrier = repo.parent / "synthetic-release-closeout.md"
        carrier.write_text(
            bug_closeout_body(
                close_line="Close #44.",
                behavior_line=None,
            )
            + "\n",
            encoding="utf-8",
        )
        extras.extend(["--close-issue-carrier-file", str(carrier)])
    if not has_critique_flag:
        extras.extend([
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ])
    prepared = _run_publish(repo, env, "--part", "patch", *extras, "--execute")
    if prepared.returncode != 0:
        return prepared
    payload = yaml.safe_load(prepared.stdout)
    prepared_commit = payload["prepared_release_commit"]
    record = subprocess.run(
        ["git", "show", f"{prepared_commit}:charness-artifacts/release/latest.md"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout
    review_path = commit_claims_review(
        repo, prepared_commit=prepared_commit, prepared_record=record,
        target_version=payload["target_version"], tag_name=payload["tag_name"], stem="fixture-claims",
    )
    resumed = _run_publish(
        repo, env, "--resume", "--publish-current", *extras,
        "--claims-review-artifact", review_path, "--execute",
    )
    if resumed.returncode == 0:
        final_payload = yaml.safe_load(resumed.stdout)
        final_payload["previous_version"] = payload["previous_version"]
        final_payload["target_version"] = payload["target_version"]
        # Re-rendered through the command's OWN renderer, not `json.dumps`. This synthetic
        # CompletedProcess stands in for real publish stdout, so it has to carry the same
        # YAML shape the real command emits -- otherwise a consumer that reads the stream
        # rather than the parsed payload would be testing against a stdout no command
        # produces. (JSON parses as YAML, so the difference is invisible to `yaml.safe_load`
        # consumers and only bites the ones that look at the text.)
        return subprocess.CompletedProcess(
            resumed.args, resumed.returncode, render_yaml(final_payload), resumed.stderr
        )
    return resumed


def _run_review_gate(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", REVIEW_GATE_SCRIPT, "--repo-root", str(repo), *extra],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
