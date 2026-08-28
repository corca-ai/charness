from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import native_gate_lib

from .support import write_executable


def _repo(tmp_path: Path, *, with_source: bool = False) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    if with_source:
        crate = repo / "native" / "repograph"
        crate.mkdir(parents=True)
        (crate / "Cargo.toml").write_text("[package]\nname = 'repograph'\n", encoding="utf-8")
    return repo


def _binary(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fake binary\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def _unavailable(status: str = "not-distributed") -> SimpleNamespace:
    return SimpleNamespace(status=status, provenance=None, path=None)


def test_override_beats_managed_and_dev_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, with_source=True)
    override = _binary(tmp_path / "override" / "repograph")
    dev_tree = _binary(repo / "native" / "repograph" / "target" / "release" / "repograph")
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(override))
    monkeypatch.setattr(
        native_gate_lib.runtime_bootstrap,
        "native_core_path",
        lambda **_: pytest.fail("managed resolution must follow the override"),
    )

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(override, "override")
    assert dev_tree.is_file()


def test_managed_beats_dev_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, with_source=True)
    managed = _binary(tmp_path / "managed" / "repograph")
    _binary(repo / "native" / "repograph" / "target" / "release" / "repograph")
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    monkeypatch.setattr(
        native_gate_lib.runtime_bootstrap,
        "native_core_path",
        lambda **_: SimpleNamespace(status="healthy", provenance="managed", path=managed),
    )

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(managed, "managed")


def test_dev_tree_is_used_when_source_exists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, with_source=True)
    dev_tree = _binary(repo / "native" / "repograph" / "target" / "release" / "repograph")
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    monkeypatch.setattr(
        native_gate_lib.runtime_bootstrap,
        "native_core_path",
        lambda **_: _unavailable(),
    )

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(dev_tree, "dev-tree")


def test_override_must_name_an_existing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, with_source=True)
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(tmp_path / "missing-repograph"))

    with pytest.raises(native_gate_lib.NativeGateError, match="CHARNESS_NATIVE_CORE.*missing"):
        native_gate_lib.resolve_native_core(repo)


def test_source_present_missing_binary_names_cargo_remediation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, with_source=True)
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    monkeypatch.setattr(
        native_gate_lib.runtime_bootstrap,
        "native_core_path",
        lambda **_: _unavailable(),
    )

    with pytest.raises(native_gate_lib.NativeGateError) as raised:
        native_gate_lib.resolve_native_core(repo)

    message = str(raised.value)
    assert "cargo build --release" in message
    assert str(repo / "native" / "repograph") in message


def test_no_native_source_names_distribution_remediation_without_cargo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path)
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    monkeypatch.setattr(
        native_gate_lib.runtime_bootstrap,
        "native_core_path",
        lambda **_: _unavailable(),
    )

    with pytest.raises(native_gate_lib.NativeGateError) as raised:
        native_gate_lib.resolve_native_core(repo)

    message = str(raised.value)
    assert "not yet distributed" in message
    assert "charness update" in message
    assert "cargo" not in message


def _fake_repograph(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_executable(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import os",
                "import sys",
                "payload = {",
                "    'schema': 'repograph.export_safe.v1',",
                "    'repo_root': 'fixture',",
                "    'listing': 'file-list',",
                "    'files_total': 1,",
                "    'analyzed_files': 1,",
                "    'violations': [] if os.environ['FAKE_EXIT'] == '0' else [{'path': 'x.py'}],",
                "    'unestablished': [] if os.environ['FAKE_EXIT'] != '3' else [{'path': '<scope>'}],",
                "}",
                "print(json.dumps(payload))",
                "sys.exit(int(os.environ['FAKE_EXIT']))",
                "",
            ]
        ),
    )
    return path


@pytest.mark.parametrize("exit_code", [0, 1, 3, 70])
def test_child_exit_code_and_export_safe_document_pass_through(
    tmp_path: Path,
    exit_code: int,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    repo = _repo(tmp_path)
    fake = _fake_repograph(tmp_path / "bin" / "repograph")
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(fake))
    monkeypatch.setenv("FAKE_EXIT", str(exit_code))

    returned = native_gate_lib.main(
        ["--repo-root", str(repo), "export-safe", "--repo-root", str(repo)]
    )

    captured = capfd.readouterr()
    assert returned == exit_code
    assert json.loads(captured.out)["schema"] == "repograph.export_safe.v1"


def test_probe_reports_resolution_without_running_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    repo = _repo(tmp_path)
    fake = _fake_repograph(tmp_path / "bin" / "repograph")
    marker = tmp_path / "ran"
    fake.write_text(
        fake.read_text(encoding="utf-8").replace(
            "payload = {", f"Path({str(marker)!r}).touch()\npayload = {{"
        ).replace("import os", "import os\nfrom pathlib import Path"),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(fake))
    monkeypatch.setenv("FAKE_EXIT", "0")

    returned = native_gate_lib.main(["--repo-root", str(repo), "--probe", "export-safe"])

    captured = capfd.readouterr()
    assert returned == 0
    assert "provenance: override" in captured.out
    assert not marker.exists()
