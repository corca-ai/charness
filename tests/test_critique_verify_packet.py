from __future__ import annotations

import hashlib
import json
import runpy
import shlex
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "skills/public/critique/scripts/prepare_packet.py"
VERIFY_ENTRYPOINTS = (
    ROOT / "skills/public/critique/scripts/verify_packet.py",
    ROOT / "plugins/charness/skills/critique/scripts/verify_packet.py",
)


def _git(repo: Path, *args: str) -> None:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def _prepare(tmp_path: Path) -> tuple[Path, dict, dict]:
    _git(tmp_path, "init")
    reviewed = tmp_path / "reviewed.txt"
    reviewed.write_text("reviewed bytes\n", encoding="utf-8")
    _git(tmp_path, "add", "reviewed.txt")
    _git(tmp_path, "commit", "-m", "initial")
    result = subprocess.run(
        [
            "python3",
            str(PREPARE),
            "--repo-root",
            str(tmp_path),
            "--slug",
            "verify",
            "--reviewed-path",
            "reviewed.txt",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    receipt = yaml.safe_load(result.stdout)
    packet_path = tmp_path / receipt["reviewed_input_binding"]["packet_path"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    return packet_path, receipt, packet


def _run(command: str, *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(shlex.split(command), cwd=cwd, capture_output=True, text=True)


def _verifier_namespace() -> dict:
    return runpy.run_path(str(VERIFY_ENTRYPOINTS[0]), run_name="critique_verify_packet_test")


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
    assert yaml.safe_load(result.stdout)["status"] == "current"
    assert packet_path.is_file()


def test_tampered_packet_refuses_with_structured_yaml(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _prepare(tmp_path)
    _packet_path.write_bytes(b"{}\n")

    result = _run(receipt["reviewed_input_binding"]["verify_command"], cwd=tmp_path)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "stale or tampered" in payload["reason"]


def test_stale_reviewed_input_refuses(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _prepare(tmp_path)
    (tmp_path / "reviewed.txt").write_text("changed after review\n", encoding="utf-8")

    result = _run(receipt["reviewed_input_binding"]["verify_command"], cwd=tmp_path)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["reason"] == "declared reviewed inputs are stale"


def test_malformed_packet_and_expected_identity_mismatch_refuse(tmp_path: Path) -> None:
    packet_path, receipt, packet = _prepare(tmp_path)
    binding = receipt["reviewed_input_binding"]
    verifier = str(VERIFY_ENTRYPOINTS[0])
    mismatch = subprocess.run(
        [
            "python3",
            verifier,
            "--repo-root",
            ".",
            "--packet-path",
            binding["packet_path"],
            "--packet-sha256",
            binding["packet_sha256"],
            "--identity-sha256",
            "0" * 64,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    packet_path.write_bytes(b"not-json\n")
    malformed = subprocess.run(
        [
            "python3",
            verifier,
            "--repo-root",
            ".",
            "--packet-path",
            binding["packet_path"],
            "--packet-sha256",
            hashlib.sha256(b"not-json\n").hexdigest(),
            "--identity-sha256",
            packet["reviewed_input_identity"]["identity_sha256"],
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
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


def test_source_and_generated_plugin_verifier_entrypoints_work(tmp_path: Path) -> None:
    _packet_path, receipt, _packet = _prepare(tmp_path)
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
