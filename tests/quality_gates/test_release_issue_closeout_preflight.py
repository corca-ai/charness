from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

from .issue_closeout_support import bug_closeout_body, load_verify_module
from .release_publish_fixtures import _seed_publish_release_repo, _write_exec
from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]


def _load_issue_validate_closeout_draft():
    path = ROOT / "skills" / "public" / "issue" / "scripts" / "issue_validate_closeout_draft.py"
    return load_module("issue_validate_closeout_draft_test", path)


def _load_release_closeout_module():
    path = ROOT / "skills" / "public" / "release" / "scripts" / "release_issue_closeout.py"
    return load_module("release_issue_closeout_test", path)


def _load_release_closeout_message_module():
    path = ROOT / "skills" / "public" / "release" / "scripts" / "release_issue_closeout_message.py"
    return load_module("release_issue_closeout_message_test", path)


def _load_commit_msg_checker():
    path = ROOT / "scripts" / "check_issue_closeout_commit_msg.py"
    return load_module("check_issue_closeout_commit_msg_test", path)


def _release_payload(
    *,
    classification: str,
    carrier_body: str,
    commit_message: str = "Release demo v1.0.0",
) -> dict[str, str]:
    return {
        "tag_name": "v1.0.0",
        "quality_command": "./scripts/run-quality.sh",
        "commit_message": commit_message,
        "issue_closeout_carrier_body": carrier_body,
        "issue_closeout_classification": classification,
    }


def _feature_closeout_body(close_line: str = "Close #44.") -> str:
    return "\n\n".join(
        [
            close_line,
            "JTBD: ship the release feature end-to-end.",
            "Boundary: release helper transports the issue-owned closeout carrier into the final commit.",
            "Resolution brief: validate the final emitted release commit before quality and mutation.",
            "Implementation: release preflight assembles and validates the exact commit message, then commit reuses it.",
            "Prevention: release closeout preflight blocks mismatched carriers before mutation.",
            "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
            "Behavior #44: confirmed via fresh checkout install",
            "Probe record #44: local-only-by-contract",
            "AI-provenance: agent-drafted via charness issue resolve; human-audited per the resolution critique",
        ]
    )


def _publish_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    return env


def _run_publish(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    carrier = Path(env["FAKE_CLOSEOUT_CARRIER"])
    carrier.write_text(
        bug_closeout_body(
            close_line="Close #44.",
            behavior_line=None,
        )
        + "\n",
        encoding="utf-8",
    )
    return _run_close_issue_publish(repo, env, carrier=carrier)


def _run_close_issue_publish(
    repo: Path, env: dict[str, str], *, carrier: Path | None
) -> subprocess.CompletedProcess[str]:
    argv = [
        "python3",
        "skills/public/release/scripts/publish_release.py",
        "--repo-root",
        str(repo),
        "--part",
        "patch",
        "--close-issue",
        "44",
        "--close-issue-classification",
        "bug",
    ]
    if carrier is not None:
        argv.extend(["--close-issue-carrier-file", str(carrier)])
    argv.extend(
        [
            "--close-issue-behavior", "Behavior #44: confirmed via fresh checkout install",
            "--close-issue-probe-record", "Probe record #44: local-only-by-contract",
            "--critique-blocked",
            "synthetic-host-signal for legacy issue-closeout preflight test",
            "--execute",
        ]
    )
    return subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _close_issue_publish_context(
    tmp_path: Path,
) -> tuple[Path, dict[str, str], str]:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    initial_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    issue_state = tmp_path / "issue-state.json"
    issue_state.write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    env["FAKE_GH_ISSUE_STATE"] = str(issue_state)
    return repo, env, initial_head


def test_release_generated_final_message_passes_issue_owned_direct_commit_draft_validation(tmp_path: Path) -> None:
    release_closeout = _load_release_closeout_module()
    validate_closeout_draft = _load_issue_validate_closeout_draft()
    verifier = load_verify_module()
    payload = _release_payload(
        classification="bug",
        carrier_body=bug_closeout_body(
            close_line="Close #44.",
            behavior_line=None,
        ),
    )
    commit_message = tmp_path / "message.txt"
    commit_message.write_text(
        "\n\n".join(
            [
                payload["commit_message"],
                *release_closeout.release_commit_body(
                    payload,
                    [44],
                    ["Behavior #44: confirmed via fresh checkout install"],
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = validate_closeout_draft.validate_closeout_draft(
        verifier=verifier,
        repo_root=tmp_path,
        repo="example/demo",
        numbers=[44],
        classification="bug",
        body_file=None,
        backend={},
        carrier="direct-commit",
        commit_message_file=commit_message,
        manual_fallback_reason=None,
    )

    assert result["ok"] is True
    assert result["status"] == "draft_verified"
    assert result["missing_fields"] == []
    assert result["missing_close_keywords"] == []


def test_release_generated_final_message_refuses_unintended_close_keyword(tmp_path: Path) -> None:
    message = _load_release_closeout_message_module()
    commit_message = "\n\n".join(
        [
            "Release demo v1.0.0",
            bug_closeout_body(
                close_line="Close #44.\n\nClose #45.",
                behavior_line="Behavior #44: confirmed via fresh checkout install",
            ),
        ]
    )

    result = message.validate_release_closeout_commit_message(
        tmp_path,
        repo="example/demo",
        issue_numbers=[44],
        classification="bug",
        commit_message=commit_message,
    )

    assert result["ok"] is False
    assert result["unexpected_close_keywords"] == [{"repo": None, "number": 45}]


def test_release_generated_final_message_passes_commit_msg_gate(tmp_path: Path) -> None:
    release_closeout = _load_release_closeout_module()
    commit_msg_checker = _load_commit_msg_checker()
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    payload = _release_payload(
        classification="feature",
        carrier_body=_feature_closeout_body(
            close_line="Close #44.",
        ),
    )
    message = tmp_path / "message.txt"
    message.write_text(
        release_closeout.release_commit_message(
            payload,
            [44],
            ["Behavior #44: confirmed via fresh checkout install"],
        ),
        encoding="utf-8",
    )

    payload_json = commit_msg_checker.evaluate(
        repo_root=tmp_path,
        commit_msg_file=message,
        repo="example/demo",
    )

    assert payload_json["status"] == "verified"
    assert payload_json["bare_close_numbers"] == [44]
    assert payload_json["reports"][0]["carrier"] == "commit-msg"
    assert payload_json["reports"][0]["classification"] == "feature"
    assert payload_json["reports"][0]["missing_fields"] == []
    assert payload_json["reports"][0]["missing_close_keywords"] == []
    assert "Classification: feature" in message.read_text(encoding="utf-8")


def test_release_closeout_message_refuses_mismatched_carrier_classification() -> None:
    message_module = _load_release_closeout_message_module()
    payload = _release_payload(
        classification="bug",
        carrier_body="\n\n".join(
            [
                "Classification: feature",
                "Close #44.",
                "JTBD: ship the release feature end-to-end.",
                "Boundary: carrier mismatch must refuse before mutation.",
                "Resolution brief: mismatch test only.",
                "Implementation: mismatch test only.",
                "Prevention: release preflight blocks conflicting classifications.",
            ]
        ),
    )

    try:
        message_module.release_commit_body(
            payload,
            [44],
            ["Behavior #44: confirmed via fresh checkout install"],
        )
    except SystemExit as exc:
        assert "conflicts with --close-issue-classification" in str(exc)
        assert "carrier=feature requested=bug" in str(exc)
    else:
        raise AssertionError("expected classification mismatch to refuse")


def test_release_closeout_message_package_root_handles_installed_layout() -> None:
    message_module = _load_release_closeout_message_module()

    package_root, installed_first = message_module._package_root(
        Path("/opt/plugin/skills/release/scripts/release_issue_closeout_message.py")
    )

    assert package_root == Path("/opt/plugin")
    assert installed_first is True


def test_release_closeout_message_refuses_commit_validation_when_issue_helpers_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    message_module = _load_release_closeout_message_module()
    for helper_name in ("_ISSUE_VALIDATE_CLOSEOUT_DRAFT", "_ISSUE_VERIFY_CLOSEOUT"):
        monkeypatch.setattr(message_module, helper_name, None)
    monkeypatch.setattr(message_module, "_ISSUE_CLOSEOUT_DRAFT_ERROR", "missing issue helpers (forced)")

    with pytest.raises(SystemExit, match="closeout draft helpers"):
        message_module.validate_release_closeout_commit_message(
            tmp_path,
            repo="example/demo",
            issue_numbers=[44],
            classification="bug",
            commit_message="Release demo v1.0.0\n",
        )


def _assert_stopped_before_mutation(repo: Path, tmp_path: Path, initial_head: str) -> None:
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
    assert head.stdout.strip() == initial_head
    tags = subprocess.run(["git", "tag", "--list", "v0.0.1"], cwd=repo, check=True, capture_output=True, text=True)
    assert tags.stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry and entry[0] in {"commit", "push"} for entry in git_log)
    assert ["tag", "v0.0.1"] not in git_log


def test_close_issue_preflight_fails_before_mutation(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    initial_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    env["FAKE_GH_ISSUE_VIEW_FAIL"] = "1"
    env["FAKE_CLOSEOUT_CARRIER"] = str(tmp_path / "closeout.md")
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")

    result = _run_publish(repo, env)

    assert result.returncode == 1
    assert "release --close-issue preflight failed before mutation" in result.stderr
    _assert_stopped_before_mutation(repo, tmp_path, initial_head)
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["issue", "view", "44", "--repo", "example/demo", "--json", "number,state,url"] in gh_log
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)
    assert not any(entry[:2] == ["issue", "close"] for entry in gh_log)


def test_close_issue_requires_github_repo_before_mutation(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _write_exec(
        bin_dir / "custom-release",
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json, os, sys
            from pathlib import Path
            log = Path(os.environ["FAKE_RELEASE_BACKEND_LOG"])
            entries = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
            entries.append(sys.argv[1:])
            log.write_text(json.dumps(entries, indent=2) + "\\n", encoding="utf-8")
            raise SystemExit(1 if sys.argv[1:3] == ["release", "view"] else 0)
            """
        ),
    )
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nrelease_backend:\n"
        + "  id: custom-release\n"
        + "  commands:\n"
        + "    auth_check:\n"
        + "      - custom-release\n"
        + "      - auth\n"
        + "    release_view:\n"
        + "      - custom-release\n"
        + "      - release\n"
        + "      - view\n"
        + "      - '{tag}'\n"
        + "    release_create:\n"
        + "      - custom-release\n"
        + "      - release\n"
        + "      - create\n"
        + "      - '{tag}'\n"
        + "      - '--title'\n"
        + "      - '{title}'\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", ".agents/release-adapter.yaml"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Use custom release backend"], cwd=repo, check=True, capture_output=True, text=True)
    initial_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_RELEASE_BACKEND_LOG"] = str(tmp_path / "release-backend-log.json")
    env["FAKE_CLOSEOUT_CARRIER"] = str(tmp_path / "closeout.md")

    result = _run_publish(repo, env)

    assert result.returncode == 1
    assert "release --close-issue requires a GitHub repo before mutation" in result.stderr
    _assert_stopped_before_mutation(repo, tmp_path, initial_head)
    backend_log = json.loads((tmp_path / "release-backend-log.json").read_text(encoding="utf-8"))
    assert ["release", "view", "v0.0.1"] in backend_log
    assert ["release", "create", "v0.0.1", "--title", "v0.0.1"] not in backend_log


def test_close_issue_missing_carrier_file_fails_before_quality_or_mutation(tmp_path: Path) -> None:
    release_closeout = _load_release_closeout_module()

    with pytest.raises(SystemExit, match="--close-issue-carrier-file"):
        release_closeout.preflight_release_issues(
            tmp_path,
            repo="example/demo",
            issue_numbers=[44],
            payload={},
            run=None,
            classification="bug",
        )


def test_close_issue_invalid_carrier_fails_before_quality_or_mutation(tmp_path: Path) -> None:
    release_closeout = _load_release_closeout_module()
    carrier = tmp_path / "closeout.md"
    carrier.write_text("Close #44.\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        release_closeout.preflight_release_issues(
            tmp_path,
            repo="example/demo",
            issue_numbers=[44],
            payload={
                "tag_name": "v1.0.0",
                "quality_command": "./scripts/run-quality.sh",
                "commit_message": "Release demo v1.0.0",
            },
            run=None,
            behavior_lines=["Behavior #44: confirmed via fresh checkout install"],
            probe_record_lines=["Probe record #44: local-only-by-contract"],
            classification="bug",
            carrier_file=carrier,
        )

    message = str(excinfo.value)
    assert "carrier failed issue-owned draft validation" in message
    assert "missing_fields" in message
    assert "resolution_critique_ok: False" in message


def test_close_issue_preflight_without_close_issue_skips_carrier_validation(tmp_path: Path) -> None:
    release_closeout = _load_release_closeout_module()
    payload: dict[str, object] = {}
    release_closeout.preflight_release_issues(
        tmp_path,
        repo="example/demo",
        issue_numbers=[],
        payload=payload,
        run=None,
        behavior_lines=None,
    )

    assert payload["issue_closeout_preflight"] == {"status": "not_requested", "issues": []}


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({}, "close-issue-classification"),
        ({"classification": "bug"}, "close-issue-carrier-file"),
        (
            {
                "classification": "bug",
                "carrier_file": "missing.md",
                "behavior_lines": ["Behavior #44: x"],
            },
            "carrier file not found",
        ),
    ],
)
def test_close_issue_preflight_requires_classification_and_existing_carrier(
    tmp_path: Path, kwargs: dict[str, object], message: str
) -> None:
    release_closeout = _load_release_closeout_module()
    resolved_kwargs = {
        key: tmp_path / value if key == "carrier_file" else value
        for key, value in kwargs.items()
    }
    with pytest.raises(SystemExit, match=message):
        release_closeout.preflight_release_issues(
            tmp_path, repo="example/demo", issue_numbers=[44], payload={}, run=None,
            **resolved_kwargs,
        )
