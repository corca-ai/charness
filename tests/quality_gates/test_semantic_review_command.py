"""End-to-end contract for the semantic critique review command."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "skills/public/critique/scripts/run_review.py"
PACKET_HELPER = ROOT / "skills/public/critique/scripts/run_review_packet.py"


def _write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def _repo(tmp_path: Path, *, timeout: int = 5, with_packet_sections: bool = True) -> None:
    _git(tmp_path, "init")
    (tmp_path / "reviewed.txt").write_text("base\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(".charness/\n", encoding="utf-8")
    (tmp_path / ".agents").mkdir()
    adapter_lines = [
        "version: 1",
        "repo: semantic-review-fixture",
        "reviewer_runner:",
        "  mode: file-backed-worker",
        "  backend: codex_exec",
        f"  timeout_seconds: {timeout}",
    ]
    if with_packet_sections:
        adapter_lines.extend(
            [
                "packet_sections:",
                "  - id: smoke",
                "    title: Smoke",
                "    content_kind: static",
                "    content: smoke-body",
            ]
        )
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "\n".join(adapter_lines) + "\n", encoding="utf-8"
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "fixture")


def _fake_codex(path: Path) -> None:
    _write_executable(
        path,
        """#!/usr/bin/env python3
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sleep_for = float(os.environ.get("FAKE_REVIEW_SLEEP", "0"))
if sleep_for:
    child_pid_file = os.environ.get("FAKE_REVIEW_CHILD_PID_FILE")
    if child_pid_file:
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        Path(child_pid_file).write_text(str(child.pid), encoding="utf-8")
    time.sleep(sleep_for)
prompt = sys.stdin.read()
packet = re.search(r"^Packet identity \\(copy exactly\\): ([0-9a-f]{64})$", prompt, re.MULTILINE).group(1)
reviewed = re.search(r"^Reviewed input identity \\(copy exactly\\): ([0-9a-f]{64})$", prompt, re.MULTILINE).group(1)
lens = re.search(r"^Lens: (.+)$", prompt, re.MULTILINE).group(1)
out = Path(sys.argv[sys.argv.index("-o") + 1])
payload = {
    "kind": "charness.bounded_review.v1",
    "lens": lens,
    "packet_sha256": packet,
    "reviewed_input_identity_sha256": reviewed,
    "verdict": os.environ.get("FAKE_REVIEW_VERDICT", "pass"),
    "findings": [],
    "counterweight_triage": [],
    "next_move": "consume the typed result",
    "non_claims": ["the fixture does not prove external systems"],
    "capability_non_claims": [],
    "capability_non_claims_sha256": hashlib.sha256(b"[]").hexdigest(),
}
out.write_text(json.dumps(payload), encoding="utf-8")
""",
    )


def _seed_lineage(repo: Path) -> str:
    draft = repo / "charness-artifacts" / "goals" / "draft.md"
    binding = repo / "charness-artifacts" / "goals" / "draft.binding.json"
    draft.parent.mkdir(parents=True)
    draft.write_text("# Frozen draft\n", encoding="utf-8")
    binding.write_text("{\"kind\": \"binding\"}\n", encoding="utf-8")
    lineage = repo / ".charness" / "lineage.json"
    lineage.parent.mkdir(exist_ok=True)
    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    lineage.write_text(
        json.dumps(
            {
                "kind": "charness.goal-lineage",
                "schema_version": 1,
                "disposition": "goal-bound",
                "draft": {"path": "charness-artifacts/goals/draft.md", "sha256": sha(draft)},
                "binding": {"path": "charness-artifacts/goals/draft.binding.json", "sha256": sha(binding)},
                "goal_run": {
                    "repo": "acme/project",
                    "number": 10,
                    "url": "https://github.com/acme/project/issues/10",
                },
                "work_item": {
                    "key": "implementation",
                    "repo": "acme/project",
                    "number": 11,
                    "url": "https://github.com/acme/project/issues/11",
                },
                "reason": None,
            }
        ),
        encoding="utf-8",
    )
    return ".charness/lineage.json"


def _run(
    repo: Path,
    bin_dir: Path,
    attempt: str,
    *,
    verdict: str = "pass",
    sleep: float | None = None,
    packet_file: str | None = None,
    dry_run: bool = False,
    goal_lineage: str | None = None,
    reviewed_path: str | None = "reviewed.txt",
) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_REVIEW_VERDICT": verdict}
    if sleep is not None:
        env["FAKE_REVIEW_SLEEP"] = str(sleep)
    command = [
        sys.executable,
        str(WRAPPER),
        "--repo-root", str(repo),
        "--scope", "semantic command",
        "--lens", "operability",
        "--attempt-id", attempt,
        "--backend", "codex_exec",
    ]
    if reviewed_path is not None and packet_file is None:
        command.extend(["--reviewed-path", reviewed_path])
    elif packet_file is not None:
        command.extend(["--packet-file", packet_file])
    if goal_lineage is not None:
        command.extend(["--goal-lineage-file", goal_lineage])
    if dry_run:
        command.append("--dry-run")
    return subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)


def _packet_helper():
    spec = importlib.util.spec_from_file_location("test_run_review_packet", PACKET_HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _deleted_packet(path: str, content_sha256: str) -> dict:
    return {
        "reviewed_input_identity": {
            "mode": "working-tree",
            "substrate_mode": "working-tree",
            "changed_ref": None,
            "reviewed_paths": [path],
            "reviewed_content": [
                {"path": path, "content_sha256": content_sha256, "disposition": "deleted"}
            ],
        }
    }


def _payload(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.stdout, result.stderr
    return yaml.safe_load(result.stdout)


def test_dry_run_derives_one_typed_carrier_without_starting_backend(tmp_path: Path) -> None:
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "dry-run", dry_run=True)
    payload = _payload(result)

    assert result.returncode == 0, result.stderr
    assert payload["status"] == "dry-run-ready"
    assert payload["execution_state"] == "preflight-blocked"
    assert payload["reviewer_started"] is False
    assert payload["delivery_state"] == "none"
    assert payload["verdict_state"] == "not-applicable"
    assert payload["paths"]["schema"].startswith(".charness/reviewer-round-dry-run/")
    assert (tmp_path / payload["paths"]["schema"]).read_bytes() == (
        ROOT / "skills/shared/references/bounded-review-result.schema.json"
    ).read_bytes()
    assert not (tmp_path / "bin" / "review-called").exists()


def test_sectionless_adapter_refuses_before_reviewer_run_is_created(tmp_path: Path) -> None:
    _repo(tmp_path, with_packet_sections=False)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "sectionless", dry_run=True)
    payload = _payload(result)

    assert result.returncode != 0
    assert payload["reason_code"] == "adapter-no-sections"
    assert payload["scope_status"] == "adapter-no-sections"
    assert payload["section_count"] == 0
    assert payload["adapter_path"] == ".agents/critique-adapter.yaml"
    assert "Declare at least one packet_sections entry" in payload["remedy"]
    assert not (tmp_path / ".charness").exists()


def test_empty_declared_producer_refuses_before_reviewer_start_with_its_own_cause(
    tmp_path: Path,
) -> None:
    _repo(tmp_path)
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nrepo: semantic-review-fixture\n"
        "reviewer_runner:\n  mode: file-backed-worker\n  backend: codex_exec\n"
        "  timeout_seconds: 5\npacket_sections:\n"
        "  - id: empty\n    title: Empty\n    content_kind: script\n    command: \"printf ''\"\n",
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "empty-producer", dry_run=True)
    payload = _payload(result)

    assert result.returncode != 0
    assert payload["reason_code"] == "producer-empty"
    assert payload["scope_status"] == "producer-empty"
    assert payload["section_count"] == 1
    assert payload["usable"] is False
    assert "producer failure" in payload["warning"]
    assert "Repair the declared packet producer" in payload["remedy"]
    assert not (tmp_path / ".charness").exists()
    packet = json.loads(
        (tmp_path / "charness-artifacts/critique/empty-producer-packet.json").read_text(
            encoding="utf-8"
        )
    )
    assert packet["ok"] is False
    assert packet["reason_code"] == "producer-empty"


def test_prompt_reaches_explicit_reviewed_path_beyond_unrelated_section(tmp_path: Path) -> None:
    _repo(tmp_path)
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nrepo: semantic-review-fixture\n"
        "reviewer_runner:\n  mode: file-backed-worker\n  backend: codex_exec\n"
        "packet_sections:\n  - id: unrelated\n    title: Unrelated\n"
        "    content_kind: static\n    content: unrelated context\n",
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "path-prompt", dry_run=True)
    payload = _payload(result)

    assert result.returncode == 0, result.stderr
    prompt = (tmp_path / payload["paths"]["prompt"]).read_text(encoding="utf-8")
    assert "Every explicitly declared `--reviewed-path`" in prompt
    assert "Judge the inline payload, not the current workspace path" in prompt
    assert '"path": "reviewed.txt"' in prompt
    assert '"prompt_content": "base\\n"' in prompt
    assert "Do not infer reviewed content from hashes or unrelated packet sections" in prompt


def test_deletion_only_reviewed_input_reaches_worker_with_hash_checked_preimage(
    tmp_path: Path,
) -> None:
    _repo(tmp_path)
    (tmp_path / "reviewed.txt").unlink()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "deleted-only")
    payload = _payload(result)

    assert result.returncode == 0, result.stderr
    assert payload["execution_state"] == "terminal"
    assert payload["reviewer_started"] is True
    assert payload["delivery_state"] == "findings-received"
    plan = json.loads((tmp_path / payload["paths"]["plan"]).read_text(encoding="utf-8"))
    entry = plan["semantic_input"]["entries"][0]
    carrier = tmp_path / entry["carrier_path"]
    assert carrier.read_bytes() == b"base\n"
    assert stat.S_IMODE(carrier.stat().st_mode) == 0o444
    prompt = (tmp_path / payload["paths"]["prompt"]).read_text(encoding="utf-8")
    assert '"disposition": "deleted-preimage"' in prompt
    assert '"prompt_content": "base\\n"' in prompt
    assert entry["carrier_path"] in prompt


def test_present_committed_ref_uses_bound_target_bytes_not_current_workspace(
    tmp_path: Path,
) -> None:
    _repo(tmp_path)
    (tmp_path / "reviewed.txt").write_text("bound target\n", encoding="utf-8")
    _git(tmp_path, "add", "reviewed.txt")
    _git(tmp_path, "commit", "-m", "bound target")
    target = _git_output(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "reviewed.txt").write_text("later workspace\n", encoding="utf-8")
    content = b"bound target\n"
    packet = {
        "reviewed_input_identity": {
            "mode": "committed-ref",
            "substrate_mode": "committed-ref",
            "changed_ref": target,
            "base_head": target,
            "resolved_changed_ref": [target],
            "reviewed_paths": ["reviewed.txt"],
            "reviewed_content": [{
                "path": "reviewed.txt",
                "content_sha256": hashlib.sha256(content).hexdigest(),
            }],
        }
    }
    module = _packet_helper()
    run_dir = tmp_path / ".charness" / "committed-present"
    run_dir.mkdir(parents=True)

    semantic_input = module.materialize_semantic_input(tmp_path, packet, run_dir)

    entry = semantic_input["entries"][0]
    assert entry["prompt_content"] == "bound target\n"
    assert (tmp_path / entry["carrier_path"]).read_bytes() == content
    assert entry["source"] == f"{target}:reviewed.txt"


@pytest.mark.parametrize("ref_kind", ("commit", "range"))
def test_committed_deletion_preimage_reaches_carrier_for_commit_and_range(
    tmp_path: Path, ref_kind: str
) -> None:
    _repo(tmp_path)
    parent = _git_output(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "reviewed.txt").unlink()
    _git(tmp_path, "add", "reviewed.txt")
    _git(tmp_path, "commit", "-m", "delete reviewed input")
    target = _git_output(tmp_path, "rev-parse", "HEAD")
    changed_ref = target if ref_kind == "commit" else f"{parent}..{target}"
    resolved = [target] if ref_kind == "commit" else [parent, target]
    packet = {
        "reviewed_input_identity": {
            "mode": "committed-ref",
            "substrate_mode": "committed-ref",
            "changed_ref": changed_ref,
            "resolved_changed_ref": resolved,
            "reviewed_paths": ["reviewed.txt"],
            "reviewed_content": [
                {
                    "path": "reviewed.txt",
                    "content_sha256": hashlib.sha256(b"base\n").hexdigest(),
                    "disposition": "deleted",
                }
            ],
        }
    }
    module = _packet_helper()
    run_dir = tmp_path / ".charness" / f"committed-{ref_kind}"
    run_dir.mkdir(parents=True)

    semantic_input = module.materialize_semantic_input(tmp_path, packet, run_dir)

    entry = semantic_input["entries"][0]
    assert (tmp_path / entry["carrier_path"]).read_bytes() == b"base\n"
    assert entry["source"] == f"{parent}:reviewed.txt"


def test_deleted_preimage_hash_mismatch_refuses_explicitly(tmp_path: Path) -> None:
    _repo(tmp_path)
    (tmp_path / "reviewed.txt").unlink()
    packet = _deleted_packet("reviewed.txt", "0" * 64)
    module = _packet_helper()
    run_dir = tmp_path / ".charness" / "hash-mismatch"
    run_dir.mkdir(parents=True)

    with pytest.raises(module.SemanticInputError) as caught:
        module.materialize_semantic_input(tmp_path, packet, run_dir)

    assert caught.value.code == "preimage-hash-mismatch"
    assert caught.value.details["path"] == "reviewed.txt"


def test_deleted_preimage_unavailable_refuses_explicitly(tmp_path: Path) -> None:
    _repo(tmp_path)
    packet = _deleted_packet("missing.txt", hashlib.sha256(b"missing\n").hexdigest())
    module = _packet_helper()
    run_dir = tmp_path / ".charness" / "preimage-unavailable"
    run_dir.mkdir(parents=True)

    with pytest.raises(module.SemanticInputError) as caught:
        module.materialize_semantic_input(tmp_path, packet, run_dir)

    assert caught.value.code == "preimage-unavailable"
    assert caught.value.details["path"] == "missing.txt"


def test_deleted_preimage_oversize_refuses_without_truncation(tmp_path: Path) -> None:
    _repo(tmp_path)
    module = _packet_helper()
    content = b"x" * (module.MAX_PREIMAGE_BYTES + 1)
    (tmp_path / "large.bin").write_bytes(content)
    _git(tmp_path, "add", "large.bin")
    _git(tmp_path, "commit", "-m", "large fixture")
    (tmp_path / "large.bin").unlink()
    packet = _deleted_packet("large.bin", hashlib.sha256(content).hexdigest())
    run_dir = tmp_path / ".charness" / "preimage-oversize"
    run_dir.mkdir(parents=True)

    with pytest.raises(module.SemanticInputError) as caught:
        module.materialize_semantic_input(tmp_path, packet, run_dir)

    assert caught.value.code == "preimage-too-large"
    assert caught.value.details["path"] == "large.bin"
    assert caught.value.details["max_bytes"] == module.MAX_PREIMAGE_BYTES


def test_empty_reviewed_input_refuses_even_with_unrelated_section(tmp_path: Path) -> None:
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"

    result = _run(tmp_path, bin_dir, "empty-input", dry_run=True, reviewed_path=None)
    payload = _payload(result)

    assert result.returncode == 2
    assert payload["reason_code"] == "empty-reviewed-paths"
    assert payload["scope_status"] == "empty-reviewed-input"
    assert payload["reviewer_started"] is False
    assert payload["usable"] is False
    assert not (tmp_path / ".charness").exists()


def test_goal_run_lineage_is_carried_into_plan_prompt_and_carrier(tmp_path: Path) -> None:
    _repo(tmp_path)
    lineage = _seed_lineage(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "lineage", dry_run=True, goal_lineage=lineage)
    payload = _payload(result)

    assert result.returncode == 0, result.stderr
    assert payload["goal_lineage"]["disposition"] == "goal-bound"
    plan = tmp_path / payload["paths"]["plan"]
    prompt = tmp_path / payload["paths"]["prompt"]
    plan_data = json.loads(plan.read_text(encoding="utf-8"))
    assert plan_data["goal_lineage"]["work_item"]["number"] == 11
    assert "Goal evidence lineage (copy exactly):" in prompt.read_text(encoding="utf-8")


def test_delivered_pass_and_block_are_distinct_from_runner_failure(tmp_path: Path) -> None:
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    passed = _payload(_run(tmp_path, bin_dir, "delivered-pass"))
    blocked = _payload(_run(tmp_path, bin_dir, "delivered-block", verdict="block"))

    assert passed["execution_state"] == "terminal"
    assert passed["reviewer_started"] is True
    assert passed["delivery_state"] == "findings-received"
    assert passed["verdict_state"] == "pass"
    assert passed["approval_eligible"] is True
    assert passed["runner_stream"]["consistent"] is True
    assert blocked["execution_state"] == "terminal"
    assert blocked["reviewer_started"] is True
    assert blocked["delivery_state"] == "findings-received"
    assert blocked["verdict_state"] == "block"
    assert blocked["approval_eligible"] is False
    assert "reviewer block" in blocked["next_move"]


def test_worker_timeout_keeps_started_and_non_approval_state(tmp_path: Path) -> None:
    _repo(tmp_path, timeout=1)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "backend-timeout", sleep=10)
    payload = _payload(result)

    assert result.returncode == 1, result.stderr
    assert payload["reviewer_started"] is True
    assert payload["delivery_state"] == "timed-out"
    assert payload["verdict_state"] == "not-applicable"
    assert payload["approval_eligible"] is False
    assert payload["execution_state"] == "started"


def test_stale_packet_is_preflight_blocked_without_reviewer_start(tmp_path: Path) -> None:
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    prepared = _payload(_run(tmp_path, bin_dir, "prepare-only", dry_run=True))
    (tmp_path / "reviewed.txt").write_text("changed after packet\n", encoding="utf-8")
    stale = _payload(
        _run(
            tmp_path,
            bin_dir,
            "stale-packet",
            packet_file=prepared["paths"]["packet"],
        )
    )

    assert stale["status"] == "runner-invalid"
    assert stale["execution_state"] == "preflight-blocked"
    assert stale["reviewer_started"] is False
    assert stale["delivery_state"] == "none"
    assert stale["verdict_state"] == "not-applicable"
    assert stale["reason_code"] == "packet-stale"


def test_parent_interrupt_returns_typed_state_and_kills_backend_descendant(tmp_path: Path) -> None:
    _repo(tmp_path, timeout=30)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")
    child_pid_file = tmp_path / "child.pid"
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "FAKE_REVIEW_SLEEP": "30",
        "FAKE_REVIEW_CHILD_PID_FILE": str(child_pid_file),
    }
    command = [
        sys.executable,
        str(WRAPPER),
        "--repo-root", str(tmp_path),
        "--scope", "semantic command",
        "--lens", "operability",
        "--attempt-id", "parent-interrupt",
        "--backend", "codex_exec",
        "--reviewed-path", "reviewed.txt",
    ]
    process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, text=True)
    child_pid = None
    try:
        deadline = time.monotonic() + 5
        while not child_pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert child_pid_file.exists()
        child_pid = int(child_pid_file.read_text(encoding="utf-8"))
        process.send_signal(signal.SIGTERM)
        stdout, _ = process.communicate(timeout=10)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)

    assert child_pid is not None
    payload = yaml.safe_load(stdout)
    assert payload["status"] == "runner-interrupted"
    assert payload["reviewer_started"] is True
    assert payload["delivery_state"] == "interrupted"
    assert payload["approval_eligible"] is False
    for _ in range(40):
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    else:
        raise AssertionError("backend descendant survived parent interruption")
