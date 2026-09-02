from __future__ import annotations

import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from functools import cache
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.quality_gates.support import run_script
from tests.script_main import load_script_module

ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "skills/public/critique/scripts/prepare_packet.py"
VERIFY_ENTRYPOINTS = (
    ROOT / "skills/public/critique/scripts/verify_packet.py",
    ROOT / "plugins/charness/skills/critique/scripts/verify_packet.py",
)


@cache
def _cached_working_tree_identity() -> dict:
    """Capture one immutable seed identity for verifier-only cases."""
    from tests.reviewed_input_identity_fixtures import reviewed_identity_seed

    return reviewed_identity_seed()


_CRITIQUE_ADAPTER = (
    "version: 1\nrepo: test\npacket_sections:\n"
    "  - id: smoke\n    title: Smoke\n    content_kind: static\n    content: smoke\n"
)


def _git(repo: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", "-c", "user.email=test@example.com", "-c", "user.name=test", *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def _prepare(tmp_path: Path) -> tuple[Path, dict, dict]:
    from tests.quality_gates.repo_shapes import install_committed_repo

    install_committed_repo(
        tmp_path,
        {
            "reviewed.txt": "reviewed bytes\n",
            ".agents/critique-adapter.yaml": _CRITIQUE_ADAPTER,
        },
        message="initial",
    )
    result = run_script(
        str(PREPARE),
        "--repo-root",
        str(tmp_path),
        "--slug",
        "verify",
        "--reviewed-path",
        "reviewed.txt",
    )
    assert result.returncode == 0, result.stderr
    receipt = yaml.safe_load(result.stdout)
    packet_path = tmp_path / receipt["reviewed_input_binding"]["packet_path"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    return packet_path, receipt, packet


def _static_packet(tmp_path: Path) -> tuple[Path, dict, dict]:
    """Install one captured packet for verifier/error semantics tests.

    These cases exercise packet integrity, stale detection, and entrypoint
    behavior.  They do not need to run the prepare CLI again; the identity is
    captured once from the immutable seed and the repository bytes are copied
    unchanged for each isolated test.
    """
    from tests.reviewed_input_identity_fixtures import repo_seed

    shutil.copytree(repo_seed(), tmp_path, dirs_exist_ok=True)
    packet = {
        "kind": "charness.critique_prepare_packet",
        "version": 1,
        "repo": "test",
        "generated_at": "2026-08-30T00:00:00Z",
        "prepared_for": "verify",
        "changed_ref": None,
        "substrate_mode": "working-tree",
        "adapter_path": None,
        "sections": [
            {
                "id": "smoke",
                "title": "Smoke",
                "content_kind": "static",
                "producer": "static-config (inline)",
                "content": "smoke",
                "ok": True,
                "errors": [],
            }
        ],
        "section_count": 1,
        "ok": True,
        "scope_status": "populated",
        "reviewed_input_identity": _cached_working_tree_identity(),
    }
    packet_dir = tmp_path / "charness-artifacts" / "critique"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_path = packet_dir / "verify-packet.json"
    packet_path.write_text(json.dumps(packet, separators=(",", ":")) + "\n", encoding="utf-8")
    packet_sha = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    identity_sha = packet["reviewed_input_identity"]["identity_sha256"]
    binding = {
        "packet_path": packet_path.relative_to(tmp_path).as_posix(),
        "packet_sha256": packet_sha,
        "identity_sha256": identity_sha,
        "verify_command": (
            f"{sys.executable} {VERIFY_ENTRYPOINTS[0]} --repo-root . "
            f"--packet-path {packet_path.relative_to(tmp_path).as_posix()} "
            f"--packet-sha256 {packet_sha} --identity-sha256 {identity_sha}"
        ),
    }
    receipt = {"reviewed_input_binding": binding}
    return packet_path, receipt, packet


def _committed_ref_repo(tmp_path: Path) -> Path:
    from tests.quality_gates.repo_shapes import install_committed_repo

    repo = install_committed_repo(
        tmp_path,
        {
            "reviewed.txt": "before\n",
            ".agents/critique-adapter.yaml": _CRITIQUE_ADAPTER,
        },
        message="initial",
    )
    reviewed = repo / "reviewed.txt"
    reviewed.write_text("after\n", encoding="utf-8")
    _git(repo, "add", "reviewed.txt")
    _git(repo, "commit", "-m", "change")
    return repo


def _run(command: str, *, cwd: Path) -> subprocess.CompletedProcess[str]:
    parts = shlex.split(command)
    if parts and Path(parts[0]).name in {"python", "python3"}:
        return run_script(*parts[1:], cwd=cwd)
    return subprocess.run(parts, cwd=cwd, capture_output=True, text=True)


def _verifier_namespace() -> dict:
    module = load_script_module("critique_verify_packet_under_test", VERIFY_ENTRYPOINTS[0])
    return vars(module)


def test_missing_skill_runtime_bootstrap_raises_explicitly(monkeypatch) -> None:
    verifier = _verifier_namespace()
    loader = verifier["_load_skill_runtime_bootstrap"]
    missing_path = SimpleNamespace(resolve=lambda: SimpleNamespace(parents=[]))
    monkeypatch.setitem(loader.__globals__, "Path", lambda _value: missing_path)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        loader()


def test_identity_owner_exception_becomes_structured_refusal(monkeypatch, capsys) -> None:
    verifier = _verifier_namespace()

    def explode(**_kwargs) -> tuple[bool, str]:
        raise RuntimeError("identity owner exploded")

    monkeypatch.setattr(verifier["_identity"], "verify_packet_binding", explode)
    rc = verifier["main"](
        [
            "--repo-root",
            ".",
            "--packet-path",
            "packet.json",
            "--packet-sha256",
            "0" * 64,
            "--identity-sha256",
            "1" * 64,
        ]
    )

    assert rc == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["status"] == "refused"
    assert payload["reason"] == "cannot verify packet binding: identity owner exploded"


def test_raw_worktree_sha_differs_but_canonical_verifier_passes(tmp_path: Path) -> None:
    packet_path, receipt, packet = _prepare(tmp_path)
    identity = packet["reviewed_input_identity"]
    raw_sha = hashlib.sha256((tmp_path / "reviewed.txt").read_bytes()).hexdigest()

    assert identity["reviewed_content"][0]["content_sha256"] != raw_sha
    result = _run(receipt["reviewed_input_binding"]["verify_command"], cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "current"
    assert payload["reason_code"] == "current"
    assert packet_path.is_file()


def test_tampered_packet_refuses_with_structured_yaml(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _static_packet(tmp_path)
    _packet_path.write_bytes(b"{}\n")

    result = _run(receipt["reviewed_input_binding"]["verify_command"], cwd=tmp_path)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "stale or tampered" in payload["reason"]


def test_committed_ref_packet_records_explicit_mode_and_exact_paths(tmp_path: Path) -> None:
    repo = _committed_ref_repo(tmp_path)
    result = run_script(
        str(PREPARE),
        "--repo-root",
        str(repo),
        "--slug",
        "committed",
        "--commit",
        "HEAD",
        "--reviewed-path",
        "reviewed.txt",
    )
    assert result.returncode == 0, result.stderr
    receipt = yaml.safe_load(result.stdout)
    packet = json.loads(
        (repo / receipt["reviewed_input_binding"]["packet_path"]).read_text(encoding="utf-8")
    )
    identity = packet["reviewed_input_identity"]
    assert packet["substrate_mode"] == "committed-ref"
    assert identity["substrate_mode"] == "committed-ref"
    assert identity["reviewed_paths"] == ["reviewed.txt"]
    assert identity["reviewed_content"][0]["content_sha256"] == hashlib.sha256(
        b"after\n"
    ).hexdigest()
    verify = _run(receipt["reviewed_input_binding"]["verify_command"], cwd=repo)
    assert verify.returncode == 0, verify.stderr
    assert yaml.safe_load(verify.stdout)["status"] == "current"


def test_committed_ref_packet_refuses_mismatched_declared_paths(tmp_path: Path) -> None:
    repo = _committed_ref_repo(tmp_path)
    result = run_script(
        str(PREPARE),
        "--repo-root",
        str(repo),
        "--slug",
        "mismatch",
        "--commit",
        "HEAD",
        "--reviewed-path",
        ".agents/critique-adapter.yaml",
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "refused"
    assert payload["reason_code"] == "changed-ref-path-mismatch"
    assert not (repo / "charness-artifacts/critique/mismatch-packet.json").exists()


def test_verifier_refuses_null_hash_arguments_with_typed_reason(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _static_packet(tmp_path)
    binding = receipt["reviewed_input_binding"]
    result = run_script(
        str(VERIFY_ENTRYPOINTS[0]),
        "--repo-root",
        ".",
        "--packet-path",
        binding["packet_path"],
        "--packet-sha256",
        "null",
        "--identity-sha256",
        binding["identity_sha256"],
        cwd=tmp_path,
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["reason_code"] == "null-or-invalid-hash"


def test_stale_reviewed_input_refuses(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _static_packet(tmp_path)
    (tmp_path / "reviewed.txt").write_text("changed after review\n", encoding="utf-8")

    result = _run(receipt["reviewed_input_binding"]["verify_command"], cwd=tmp_path)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["reason"] == "declared reviewed inputs are stale"


def test_malformed_packet_and_expected_identity_mismatch_refuse(tmp_path: Path) -> None:
    packet_path, receipt, packet = _static_packet(tmp_path)
    binding = receipt["reviewed_input_binding"]
    verifier = str(VERIFY_ENTRYPOINTS[0])
    mismatch = run_script(
        verifier,
        "--repo-root",
        ".",
        "--packet-path",
        binding["packet_path"],
        "--packet-sha256",
        binding["packet_sha256"],
        "--identity-sha256",
        "0" * 64,
        cwd=tmp_path,
    )
    packet_path.write_bytes(b"not-json\n")
    malformed = run_script(
        verifier,
        "--repo-root",
        ".",
        "--packet-path",
        binding["packet_path"],
        "--packet-sha256",
        hashlib.sha256(b"not-json\n").hexdigest(),
        "--identity-sha256",
        packet["reviewed_input_identity"]["identity_sha256"],
        cwd=tmp_path,
    )

    assert mismatch.returncode == 1
    assert yaml.safe_load(mismatch.stdout)["reason"] == "artifact identity does not match the reviewed packet"
    assert malformed.returncode == 1
    assert yaml.safe_load(malformed.stdout)["reason"] == "reviewed packet is not valid JSON"


def test_receipt_and_markdown_carry_one_executable_command(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _prepare(tmp_path)
    binding = receipt["reviewed_input_binding"]
    markdown = (tmp_path / "charness-artifacts/critique/verify-packet.md").read_text(
        encoding="utf-8"
    )
    marker = "```sh\n"
    markdown_command = markdown.split(marker, 1)[1].split("\n```", 1)[0]

    assert binding["verify_command"] == markdown_command
    assert "Raw sha256sum is not the contract" in markdown
    result = _run(markdown_command, cwd=tmp_path)
    assert result.returncode == 0, result.stderr


@pytest.mark.boundary_contract(
    reason="source and generated verifier copies must be self-sufficient in clean interpreters"
)
def test_source_and_generated_plugin_verifier_entrypoints_work(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _static_packet(tmp_path)
    binding = receipt["reviewed_input_binding"]
    assert VERIFY_ENTRYPOINTS[0].read_bytes() == VERIFY_ENTRYPOINTS[1].read_bytes()

    for entrypoint in VERIFY_ENTRYPOINTS:
        result = subprocess.run(
            [
                "python3",
                str(entrypoint),
                "--repo-root",
                ".",
                "--packet-path",
                binding["packet_path"],
                "--packet-sha256",
                binding["packet_sha256"],
                "--identity-sha256",
                binding["identity_sha256"],
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (entrypoint, result.stderr)
        assert yaml.safe_load(result.stdout)["status"] == "current"
