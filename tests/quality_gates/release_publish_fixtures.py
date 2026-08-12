from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

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
                "checked_in_plugin_root: plugins/demo",
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


def _setup_git(repo: Path, remote: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo, check=True, capture_output=True, text=True)


def _seed_publish_release_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo, remote, bin_dir = _make_release_paths(tmp_path)
    _prepare_release_tree(repo, remote, bin_dir)
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True, text=True)
    _write_release_adapter(repo)
    _write_fake_git(repo, bin_dir)
    _write_sync_script(repo)
    _write_quality_script(repo)
    _write_fake_gh(bin_dir)
    _write_fake_distinct_channel_probe(bin_dir)
    _setup_git(repo, remote)
    return repo, remote, bin_dir


def _release_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
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
    payload = json.loads(prepared.stdout)
    prepared_commit = payload["prepared_release_commit"]
    record = subprocess.run(
        ["git", "show", f"{prepared_commit}:charness-artifacts/release/latest.md"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout
    review_path = "charness-artifacts/release-review/fixture-claims.json"
    review = {
        "schema_version": "charness.release.claims-review.v1",
        "prepared_commit": prepared_commit,
        "release_record_path": "charness-artifacts/release/latest.md",
        "release_record_sha256": hashlib.sha256(record.encode("utf-8")).hexdigest(),
        "target_version": payload["target_version"],
        "tag_name": payload["tag_name"],
        "verdict": "pass",
        "preparer_context": "fixture-preparer",
        "reviewer_context": "fixture-reviewer",
    }
    path = repo / review_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review) + "\n", encoding="utf-8")
    subprocess.run(["git", "add", review_path], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Record fixture claims review"], cwd=repo, check=True, capture_output=True, text=True)
    resumed = _run_publish(
        repo, env, "--resume", "--publish-current", *extras,
        "--claims-review-artifact", review_path, "--execute",
    )
    if resumed.returncode == 0:
        final_payload = json.loads(resumed.stdout)
        final_payload["previous_version"] = payload["previous_version"]
        final_payload["target_version"] = payload["target_version"]
        return subprocess.CompletedProcess(resumed.args, resumed.returncode, json.dumps(final_payload), resumed.stderr)
    return resumed


def _run_review_gate(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", REVIEW_GATE_SCRIPT, "--repo-root", str(repo), *extra],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
