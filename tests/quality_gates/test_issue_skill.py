from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path

import yaml

from tests.quality_gates.git_fixture_support import init_git_repo
from tests.quality_gates.seeding_support import (
    close_comment_args,
    environment_with_path,
    write_issue_close_fake,
    write_json_executable,
)
from tests.quality_gates.support import (
    ROOT,
    fake_gh_env,
    run_script,
    write_argv_logging_fake,
    write_issue_adapter_with_backend,
)

ISSUE_SKILL = (ROOT / "skills" / "public" / "issue" / "SKILL.md").read_text(encoding="utf-8")

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


# These tests pin the close-with-comment BACKEND mechanics (adapter templates, argv,
# post-close readback), not the closeout floor. The provenance marker is here because
# the floor now applies to every classification -- it is fixture scaffolding for these
# tests, and the floor itself is pinned in test_issue_closeout_rung1_floors.py.
_CLOSE_BODY = "{text}\n\nAI-provenance: authored by an agent session.\n"


def test_shipped_issue_adapter_example_resolves_every_declared_operation_against_production_grammar() -> None:
    """The worked adapter is consumer input, so it must execute the owner grammar.

    This intentionally resolves the YAML rather than duplicating its placeholder
    allowlists in the assertion. A copied argument from another operation must
    therefore fail here exactly as it would for a consumer before any backend
    command can run.
    """
    scripts = ROOT / "skills" / "public" / "issue" / "scripts"
    backend_owner = runpy.run_path(str(scripts / "issue_backend.py"))
    create = runpy.run_path(str(scripts / "issue_create.py"))
    read = runpy.run_path(str(scripts / "issue_read.py"))
    close = runpy.run_path(str(scripts / "issue_close.py"))
    runtime = runpy.run_path(str(scripts / "issue_runtime.py"))
    tracker = runpy.run_path(str(scripts / "issue_tracker.py"))
    example = yaml.safe_load(
        (ROOT / "skills" / "public" / "issue" / "adapter.example.yaml").read_text(encoding="utf-8")
    )
    backend = example["issue_backend"]
    commands = backend["commands"]

    operation_contracts = {
        "create": (
            create["GH_CREATE_DEFAULT"],
            create["CREATE_PLACEHOLDERS"],
            {},
            {"repo": "corca-ai/demo", "title": "Demo", "body_file": "/tmp/body.md"},
        ),
        "view": (
            read["GH_READ_DEFAULT"],
            read["VIEW_PLACEHOLDERS"],
            {"required": frozenset({"repo", "number", "json_fields"})},
            {"repo": "corca-ai/demo", "number": "42", "json_fields": "number,state"},
        ),
        "close": (
            close["GH_CLOSE_DEFAULT"],
            close["CLOSE_PLACEHOLDERS"],
            {},
            {"repo": "corca-ai/demo", "number": "42", "reason": "completed"},
        ),
        "comment": (
            close["GH_COMMENT_DEFAULT"],
            close["COMMENT_PLACEHOLDERS"],
            {},
            {
                "repo": "corca-ai/demo",
                "number": "42",
                "body_file": "/tmp/comment.md",
                "reason": "completed",
            },
        ),
        "search_newest_open": (
            runtime["GH_NEWEST_OPEN_ARGS"],
            runtime["NEWEST_OPEN_PLACEHOLDERS"],
            {"required": frozenset({"repo"})},
            {"repo": "corca-ai/demo"},
        ),
        "update": (
            tracker["GH_UPDATE_DEFAULT"],
            tracker["UPDATE_PLACEHOLDERS"],
            {"required": frozenset({"repo", "number", "body_file"})},
            {"repo": "corca-ai/demo", "number": "42", "body_file": "/tmp/body.md"},
        ),
        "discover_managed_issues": (
            tracker["GH_DISCOVER_MANAGED_ISSUES_DEFAULT"],
            tracker["DISCOVER_MANAGED_ISSUES_PLACEHOLDERS"],
            {"required": frozenset({"repo"})},
            {"repo": "corca-ai/demo"},
        ),
        "list_sub_issues": (
            tracker["GH_LIST_SUB_ISSUES_DEFAULT"],
            tracker["LIST_SUB_ISSUES_PLACEHOLDERS"],
            {"required": frozenset({"repo", "number"})},
            {"repo": "corca-ai/demo", "number": "42"},
        ),
        "resolve_issue_id": (
            tracker["GH_RESOLVE_ISSUE_ID_DEFAULT"],
            tracker["RESOLVE_ISSUE_ID_PLACEHOLDERS"],
            {"required": frozenset({"repo", "sub_issue_number"})},
            {"repo": "corca-ai/demo", "sub_issue_number": "43"},
        ),
        "add_sub_issue": (
            tracker["GH_ADD_SUB_ISSUE_DEFAULT"],
            tracker["MUTATE_SUB_ISSUE_PLACEHOLDERS"],
            {"required": frozenset({"repo", "number", "sub_issue_id"})},
            {"repo": "corca-ai/demo", "number": "42", "sub_issue_id": "9001", "sub_issue_number": "43"},
        ),
        "remove_sub_issue": (
            tracker["GH_REMOVE_SUB_ISSUE_DEFAULT"],
            tracker["MUTATE_SUB_ISSUE_PLACEHOLDERS"],
            {"required": frozenset({"repo", "number", "sub_issue_id"})},
            {"repo": "corca-ai/demo", "number": "42", "sub_issue_id": "9001", "sub_issue_number": "43"},
        ),
    }

    assert set(commands) == set(operation_contracts)
    for operation, (default, allowed, kwargs, substitutions) in operation_contracts.items():
        argv = backend_owner["resolve_op"](
            backend, operation, default, allowed, **kwargs, **substitutions
        )
        assert argv[0] == "acme"


def test_issue_target_uses_default_org_for_bare_repo(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path), "--target", "demo")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/demo"
    assert payload["target"]["source"] == "argument-default-org"


def test_issue_target_infers_current_repo_from_git_remote(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:corca-ai/charness.git"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/charness"
    assert payload["target"]["source"] == "git-remote:origin"


def test_issue_selector_parses_single_and_range_without_github() -> None:
    single = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "17")
    ranged = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "17-19")

    assert single.returncode == 0, single.stderr
    assert ranged.returncode == 0, ranged.stderr
    assert yaml.safe_load(single.stdout)["numbers"] == [17]
    assert yaml.safe_load(ranged.stdout)["numbers"] == [17, 18, 19]


def test_issue_selector_rejects_non_positive_number_and_range() -> None:
    zero = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "0")
    zero_range = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "0-3")

    assert zero.returncode == 1
    assert yaml.safe_load(zero.stdout)["ok"] is False
    assert zero_range.returncode == 1
    assert yaml.safe_load(zero_range.stdout)["ok"] is False


def test_issue_read_uses_comments_in_default_gh_view(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "print(json.dumps({'number': 42, 'title': 'Demo', 'body': 'Body', 'comments': [{'body': 'comment'}], 'labels': [], 'state': 'OPEN', 'url': 'https://github.com/corca-ai/charness/issues/42'}))",
        ],
    )

    result = run_script(
        SCRIPT,
        "read",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--repo-root",
        str(tmp_path),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin", GH_LOG=str(log)),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["comments_read"] is True
    assert payload["comment_count"] == 1
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert [
        "issue",
        "view",
        "--repo",
        "corca-ai/charness",
        "42",
        "--comments",
        "--json",
        "number,title,body,comments,labels,state,url,author,createdAt,updatedAt",
    ] in entries


def test_issue_brief_path_rejects_non_positive_number_with_structured_error(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "brief-path", "--repo-root", str(tmp_path), "--number", "0")

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "positive integer" in payload["error"]


def test_issue_brief_path_emits_payload_for_valid_number(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT, "brief-path", "--repo-root", str(tmp_path), "--number", "208", "--date", "2026-05-24"
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["issue_number"] == 208
    assert payload["date"] == "2026-05-24"
    assert payload["relpath"].endswith(".md")


def test_issue_resolve_invocation_treats_single_number_as_selector(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-invocation", "--repo-root", str(tmp_path), "--", "120")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target"]["full_name"] == f"corca-ai/{tmp_path.name}"
    assert payload["selector"] == "120"
    assert payload["numbers"] == [120]
    assert payload["selector_source"] == "argument"


def test_issue_resolve_invocation_accepts_repo_plus_selector(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-invocation", "--repo-root", str(tmp_path), "--", "acme", "120")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/acme"
    assert payload["selector"] == "120"
    assert payload["numbers"] == [120]


def test_issue_target_uses_adapter_default_repo_without_remote(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text(
        "\n".join(["version: 1", "default_org: corca-ai", "default_repo: acme", "remote_name: origin", ""]),
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/acme"
    assert payload["target"]["source"] == "adapter-default-repo-default-org"


def test_issue_close_with_comment_runs_adapter_comment_then_close(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_issue_close_fake(bin_dir)
    body = tmp_path / "body.md"
    body.write_text(_CLOSE_BODY.format(text="Multi-line\nclose comment."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *close_comment_args(tmp_path, body),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin", GH_LOG=str(log)),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["repo"] == "corca-ai/charness"
    assert payload["number"] == 42
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["issue", "comment", "--repo", "corca-ai/charness", "42", "--body-file", str(body)] in entries
    assert ["issue", "close", "--repo", "corca-ai/charness", "42", "--reason", "completed"] in entries
    assert ["issue", "view", "--repo", "corca-ai/charness", "42", "--json", "number,state,url"] in entries
    assert payload["verified_state"]["state"] == "CLOSED"


def test_issue_close_with_comment_fails_when_final_state_remains_open(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_json_executable(
        bin_dir / "gh",
        {"number": 42, "state": "OPEN", "url": "https://github.com/corca-ai/charness/issues/42"},
    )
    body = tmp_path / "body.md"
    body.write_text(_CLOSE_BODY.format(text="Body."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *close_comment_args(tmp_path, body),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "is 'OPEN'" in payload["error"]


def test_issue_close_with_comment_surfaces_partial_state_when_close_fails(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "if [[ \"$2\" == \"view\" ]]; then",
                "  echo '{\"number\": 5, \"state\": \"OPEN\", \"url\": \"https://github.com/corca-ai/charness/issues/5\"}'",
                "  exit 0",
                "fi",
                "if [[ \"$2\" == \"close\" ]]; then",
                "  echo 'forbidden' >&2",
                "  exit 1",
                "fi",
                "exit 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "body.md"
    body.write_text(_CLOSE_BODY.format(text="Body."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *close_comment_args(tmp_path, body, number=5),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "comment_succeeded=True" in payload["error"]
    assert "do not re-comment on retry" in payload["error"]


def test_issue_close_with_comment_uses_adapter_template(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "acme-log.json"
    write_argv_logging_fake(
        bin_dir,
        "acme",
        "ACME_LOG",
        [
            "if 'view' in sys.argv: print(json.dumps({'number': 7, 'state': 'CLOSED', 'url': 'https://github.com/corca-ai/charness/issues/7'}))",
        ],
    )
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    comment:",
                "      - github",
                "      - issue",
                "      - comment",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--body-file'",
                "      - '{body_file}'",
                "    close:",
                "      - github",
                "      - issue",
                "      - close",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--reason'",
                "      - '{reason}'",
                "    view:",
                "      - github",
                "      - issue",
                "      - view",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--json'",
                "      - number,state,url",
                "",
            ]
        ),
        encoding="utf-8",
    )
    body = tmp_path / "body.md"
    body.write_text(_CLOSE_BODY.format(text="Body."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *close_comment_args(tmp_path, body, number=7),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin", ACME_LOG=str(log)),
    )

    assert result.returncode == 0, result.stderr
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["github", "issue", "comment", "-R", "corca-ai/charness", "7", "--body-file", str(body)] in entries
    assert ["github", "issue", "close", "-R", "corca-ai/charness", "7", "--reason", "completed"] in entries
    assert ["github", "issue", "view", "-R", "corca-ai/charness", "7", "--json", "number,state,url"] in entries


def test_issue_close_with_comment_requires_adapter_view_template(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "acme"
    fake.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    comment:",
                "      - github",
                "      - issue",
                "      - comment",
                "      - '{number}'",
                "    close:",
                "      - github",
                "      - issue",
                "      - close",
                "      - '{number}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    body = tmp_path / "body.md"
    body.write_text(_CLOSE_BODY.format(text="Body."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *close_comment_args(tmp_path, body, number=7),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode == 2, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "requires backend commands.view" in payload["error"]


def test_issue_close_with_comment_substitutes_reason_when_adapter_comment_uses_it(
    tmp_path: Path,
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "acme-log.json"
    write_argv_logging_fake(
        bin_dir,
        "acme",
        "ACME_LOG",
        [
            "if 'view' in sys.argv: print(json.dumps({'number': 11, 'state': 'CLOSED', 'url': 'https://github.com/corca-ai/charness/issues/11'}))",
        ],
    )
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    comment:",
                "      - github",
                "      - issue",
                "      - comment",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--body-file'",
                "      - '{body_file}'",
                "      - '--reason'",
                "      - '{reason}'",
                "    close:",
                "      - github",
                "      - issue",
                "      - close",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--reason'",
                "      - '{reason}'",
                "    view:",
                "      - github",
                "      - issue",
                "      - view",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--json'",
                "      - number,state,url",
                "",
            ]
        ),
        encoding="utf-8",
    )
    body = tmp_path / "body.md"
    body.write_text(_CLOSE_BODY.format(text="Body."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *close_comment_args(tmp_path, body, number=11),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin", ACME_LOG=str(log)),
    )

    assert result.returncode == 0, result.stderr
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert [
        "github",
        "issue",
        "comment",
        "-R",
        "corca-ai/charness",
        "11",
        "--body-file",
        str(body),
        "--reason",
        "completed",
    ] in entries


def test_issue_close_with_comment_rejects_adapter_template_with_unknown_placeholder(
    tmp_path: Path,
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "acme"
    fake.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="acme-github", binary="acme")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    comment:",
                "      - github",
                "      - issue",
                "      - comment",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--body-file'",
                "      - '{body_file}'",
                "      - '--audit'",
                "      - '{audit_id}'",
                "    close:",
                "      - github",
                "      - issue",
                "      - close",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--reason'",
                "      - '{reason}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    body = tmp_path / "body.md"
    body.write_text(_CLOSE_BODY.format(text="Body."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        *close_comment_args(tmp_path, body, number=13),
        env=environment_with_path(bin_dir, path_tail="/usr/bin:/bin"),
    )

    assert result.returncode != 0, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "audit_id" in payload["error"]
    assert "unknown placeholders" in payload["error"]


def test_issue_skill_records_github_sot_for_omitted_selector() -> None:
    resolve_flow = (ROOT / "skills" / "public" / "issue" / "references" / "resolve-flow.md").read_text(
        encoding="utf-8"
    )

    assert "GitHub is the source of truth" in ISSUE_SKILL
    assert "Do not use the session's last-created issue" in ISSUE_SKILL
    assert "omitted selector means newest open GitHub issue" in resolve_flow


def test_issue_plan_resolve_exposes_backend_refs_and_classification_actions(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT,
        "plan",
        "--repo-root",
        str(tmp_path),
        "--intent",
        "resolve",
        "--",
        "42",
        env=fake_gh_env(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["next_action"]["kind"] == "read_selected_issues_with_comments_then_classify"
    assert payload["selected_backend"]["id"] == "gh"
    assert "auth_status" not in payload["selected_backend"]
    required_paths = {ref["path"] for ref in payload["required_reads"]}
    on_demand_paths = {ref["path"] for ref in payload["on_demand_reads"]}
    assert "references/issue-backend.md" in required_paths
    assert "references/closeout-discipline.md" in required_paths
    assert "references/causal-review.md" in on_demand_paths
    assert "../../shared/references/fresh-eye-subagent-review.md" in on_demand_paths
    assert payload["classification_actions"]["bug"]["action_id"] == "causal_review_before_design"
    assert payload["classification_actions"]["bug"]["fresh_eye_required"] is True
    assert "references/causal-review.md" in payload["classification_actions"]["bug"]["required_reads"]


def test_issue_plan_resolve_without_selector_selects_github_next_action(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT,
        "plan",
        "--repo-root",
        str(tmp_path),
        "--intent",
        "resolve",
        env=fake_gh_env(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["numbers"] is None
    assert payload["selector_source"] == "github-newest-open"
    assert payload["next_action"]["kind"] == "select_newest_open_issue_from_github_then_read"


def test_issue_plan_reports_invalid_adapter_before_planning(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text("version: 1\nfeature_brief_pause: maybe\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "plan",
        "--repo-root",
        str(tmp_path),
        "--intent",
        "resolve",
        env=fake_gh_env(tmp_path),
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["next_action"]["kind"] == "repair_issue_adapter"


def test_issue_plan_reports_invalid_resolve_invocation_flag(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT,
        "plan",
        "--repo-root",
        str(tmp_path),
        "--intent",
        "resolve",
        "--",
        "--bogus",
        env=fake_gh_env(tmp_path),
    )

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "unknown issue resolve flag" in payload["error"]


def test_issue_plan_backend_summary_handles_missing_preflight_selection() -> None:
    module = runpy.run_path(str(ROOT / "skills" / "public" / "issue" / "scripts" / "issue_plan.py"))

    assert module["_backend_summary"]({}) is None


def test_issue_plan_resolve_rejects_ignored_target_flag(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT,
        "plan",
        "--repo-root",
        str(tmp_path),
        "--intent",
        "resolve",
        "--target",
        "corca-ai/other",
        "--",
        "42",
        env=fake_gh_env(tmp_path),
    )

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "--target" in payload["error"]


def test_issue_skill_documents_backend_resolution() -> None:
    backend_ref = (ROOT / "skills" / "public" / "issue" / "references" / "issue-backend.md").read_text(
        encoding="utf-8"
    )

    assert "selected backend comes from the adapter" in " ".join(ISSUE_SKILL.lower().split())
    assert "selected_backend" in ISSUE_SKILL
    assert "issue_backend" in backend_ref
    assert "acme" in backend_ref


def test_resolve_milestone_assigns_existing_match() -> None:
    result = run_script(
        SCRIPT, "resolve-milestone", "--requested", "v1.0", "--existing", "v1.0", "--existing", "backlog"
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["assignable"] is True
    assert payload["action"] == "assign"
    assert payload["milestone"] == "v1.0"


def test_resolve_milestone_never_invents_when_no_match() -> None:
    result = run_script(SCRIPT, "resolve-milestone", "--requested", "made-up", "--existing", "v1.0")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["assignable"] is False
    assert payload["action"] == "leave-unassigned"
    assert payload["milestone"] is None
    assert "not creating a new one" in payload["reason"]


def test_resolve_milestone_leaves_unassigned_when_none_requested() -> None:
    result = run_script(SCRIPT, "resolve-milestone", "--existing", "v1.0")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["assignable"] is False
    assert payload["milestone"] is None
    assert payload["reason"] == "no milestone requested"


def test_issue_skill_documents_existing_milestone_rule() -> None:
    shaping = (ROOT / "skills" / "public" / "issue" / "references" / "issue-shaping.md").read_text(
        encoding="utf-8"
    )
    skill_flat = " ".join(ISSUE_SKILL.split())
    shaping_flat = " ".join(shaping.split())
    assert "Assign only existing repository labels and milestones" in skill_flat
    assert "Never create a new milestone" in shaping_flat
