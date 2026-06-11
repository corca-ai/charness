from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from tests.quality_gates.support import ROOT, run_script, write_issue_adapter_with_backend

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def test_issue_target_uses_default_org_for_bare_repo(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path), "--target", "demo")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/demo"
    assert payload["target"]["source"] == "argument-default-org"


def test_issue_target_infers_current_repo_from_git_remote(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:corca-ai/charness.git"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/charness"
    assert payload["target"]["source"] == "git-remote:origin"


def test_issue_selector_parses_single_and_range_without_github() -> None:
    single = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "17")
    ranged = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "17-19")

    assert single.returncode == 0, single.stderr
    assert ranged.returncode == 0, ranged.stderr
    assert json.loads(single.stdout)["numbers"] == [17]
    assert json.loads(ranged.stdout)["numbers"] == [17, 18, 19]


def test_issue_selector_rejects_non_positive_number_and_range() -> None:
    zero = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "0")
    zero_range = run_script(SCRIPT, "select", "--repo", "corca-ai/charness", "--selector", "0-3")

    assert zero.returncode == 1
    assert json.loads(zero.stdout)["ok"] is False
    assert zero_range.returncode == 1
    assert json.loads(zero_range.stdout)["ok"] is False


def test_issue_read_uses_comments_in_default_gh_view(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['GH_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "print(json.dumps({'number': 42, 'title': 'Demo', 'body': 'Body', 'comments': [{'body': 'comment'}], 'labels': [], 'state': 'OPEN', 'url': 'https://example.test/42'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)

    result = run_script(
        SCRIPT,
        "read",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "positive integer" in payload["error"]


def test_issue_brief_path_emits_payload_for_valid_number(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT, "brief-path", "--repo-root", str(tmp_path), "--number", "208", "--date", "2026-05-24"
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["issue_number"] == 208
    assert payload["date"] == "2026-05-24"
    assert payload["relpath"].endswith(".md")


def test_issue_resolve_invocation_treats_single_number_as_selector(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-invocation", "--repo-root", str(tmp_path), "--", "120")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == f"corca-ai/{tmp_path.name}"
    assert payload["selector"] == "120"
    assert payload["numbers"] == [120]
    assert payload["selector_source"] == "argument"


def test_issue_resolve_invocation_accepts_repo_plus_selector(tmp_path: Path) -> None:
    result = run_script(SCRIPT, "resolve-invocation", "--repo-root", str(tmp_path), "--", "ceal", "120")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/ceal"
    assert payload["selector"] == "120"
    assert payload["numbers"] == [120]


def test_issue_target_uses_adapter_default_repo_without_remote(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text(
        "\n".join(["version: 1", "default_org: corca-ai", "default_repo: ceal", "remote_name: origin", ""]),
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "resolve-target", "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target"]["full_name"] == "corca-ai/ceal"
    assert payload["target"]["source"] == "adapter-default-repo-default-org"


def test_issue_close_with_comment_runs_adapter_comment_then_close(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['GH_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "if 'comment' in sys.argv: print('commented')",
                "if 'close' in sys.argv: print('closed')",
                "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "body.md"
    body.write_text("Multi-line\nclose comment.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "if 'comment' in sys.argv: print('commented')",
                "if 'close' in sys.argv: print('closed')",
                "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'OPEN', 'url': 'https://example.test/42'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "body.md"
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stderr
    payload = json.loads(result.stdout)
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
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "5",
        "--body-file",
        str(body),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "comment_succeeded=True" in payload["error"]
    assert "do not re-comment on retry" in payload["error"]


def test_issue_close_with_comment_uses_adapter_template(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "ceal-log.json"
    fake = bin_dir / "ceal"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['CEAL_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "if 'view' in sys.argv: print(json.dumps({'number': 7, 'state': 'CLOSED', 'url': 'https://example.test/7'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
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
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "7",
        "--body-file",
        str(body),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "CEAL_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["github", "issue", "comment", "-R", "corca-ai/charness", "7", "--body-file", str(body)] in entries
    assert ["github", "issue", "close", "-R", "corca-ai/charness", "7", "--reason", "completed"] in entries
    assert ["github", "issue", "view", "-R", "corca-ai/charness", "7", "--json", "number,state,url"] in entries


def test_issue_close_with_comment_requires_adapter_view_template(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "ceal"
    fake.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
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
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "7",
        "--body-file",
        str(body),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "requires backend commands.view" in payload["error"]


def test_issue_close_with_comment_substitutes_reason_when_adapter_comment_uses_it(
    tmp_path: Path,
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "ceal-log.json"
    fake = bin_dir / "ceal"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['CEAL_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "if 'view' in sys.argv: print(json.dumps({'number': 11, 'state': 'CLOSED', 'url': 'https://example.test/11'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
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
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "11",
        "--body-file",
        str(body),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "CEAL_LOG": str(log)},
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
    fake = bin_dir / "ceal"
    fake.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
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
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "13",
        "--body-file",
        str(body),
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode != 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "audit_id" in payload["error"]
    assert "unknown placeholders" in payload["error"]


def test_issue_skill_records_github_sot_for_omitted_selector() -> None:
    skill_text = (ROOT / "skills" / "public" / "issue" / "SKILL.md").read_text(encoding="utf-8")
    resolve_flow = (ROOT / "skills" / "public" / "issue" / "references" / "resolve-flow.md").read_text(
        encoding="utf-8"
    )

    assert "GitHub is the source of truth" in skill_text
    assert "It must not use the current session's last created issue" in skill_text
    assert "omitted selector means newest open GitHub issue" in resolve_flow


def test_issue_skill_documents_backend_resolution() -> None:
    skill_text = (ROOT / "skills" / "public" / "issue" / "SKILL.md").read_text(encoding="utf-8")
    backend_ref = (ROOT / "skills" / "public" / "issue" / "references" / "issue-backend.md").read_text(
        encoding="utf-8"
    )

    assert "resolves the issue backend through the adapter" in skill_text
    assert "selected_backend" in skill_text
    assert "issue_backend" in backend_ref
    assert "ceal" in backend_ref


def test_resolve_milestone_assigns_existing_match() -> None:
    result = run_script(
        SCRIPT, "resolve-milestone", "--requested", "v1.0", "--existing", "v1.0", "--existing", "backlog"
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["assignable"] is True
    assert payload["action"] == "assign"
    assert payload["milestone"] == "v1.0"


def test_resolve_milestone_never_invents_when_no_match() -> None:
    result = run_script(SCRIPT, "resolve-milestone", "--requested", "made-up", "--existing", "v1.0")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["assignable"] is False
    assert payload["action"] == "leave-unassigned"
    assert payload["milestone"] is None
    assert "not creating a new one" in payload["reason"]


def test_resolve_milestone_leaves_unassigned_when_none_requested() -> None:
    result = run_script(SCRIPT, "resolve-milestone", "--existing", "v1.0")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["assignable"] is False
    assert payload["milestone"] is None
    assert payload["reason"] == "no milestone requested"


def test_issue_skill_documents_existing_milestone_rule() -> None:
    skill_text = (ROOT / "skills" / "public" / "issue" / "SKILL.md").read_text(encoding="utf-8")
    shaping = (ROOT / "skills" / "public" / "issue" / "references" / "issue-shaping.md").read_text(
        encoding="utf-8"
    )
    skill_flat = " ".join(skill_text.split())
    shaping_flat = " ".join(shaping.split())
    assert "Assign only existing repository labels and milestones" in skill_flat
    assert "Never create a new milestone" in shaping_flat
