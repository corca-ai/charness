from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import pytest

from scripts import native_gate_lib
from scripts.subprocess_guard import PhaseOutcome

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


def _fake_which(monkeypatch: pytest.MonkeyPatch, resolver: Callable[[str], str | None]) -> None:
    monkeypatch.setattr(native_gate_lib.shutil, "which", resolver)


def _phase_outcome(command: list[str], *, returncode: int = 0, **kwargs: object) -> PhaseOutcome:
    return PhaseOutcome(
        command,
        str(kwargs.get("phase", "native-build")),
        str(kwargs.get("display") or " ".join(command)),
        returncode,
        "",
        "",
        0.0,
        False,
    )


def _no_cargo_no_installed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Neither `repograph` nor `cargo` is reachable, and no cargo bin dir exists."""
    _fake_which(monkeypatch, lambda _name: None)
    monkeypatch.setenv("CARGO_HOME", str(tmp_path / "absent-cargo-home"))


def test_override_beats_dev_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, with_source=True)
    override = _binary(tmp_path / "override" / "repograph")
    dev_tree = _binary(repo / "native" / "repograph" / "target" / "release" / "repograph")
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(override))

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(override, "override")
    assert dev_tree.is_file()


def test_override_must_name_an_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, with_source=True)
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(tmp_path / "missing-repograph"))

    with pytest.raises(native_gate_lib.NativeGateError, match="CHARNESS_NATIVE_CORE.*missing"):
        native_gate_lib.resolve_native_core(repo)


def test_dev_tree_beats_installed_binary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An edited crate must answer the gate, not a binary built from other source."""
    repo = _repo(tmp_path, with_source=True)
    dev_tree = _binary(repo / "native" / "repograph" / "target" / "release" / "repograph")
    installed = _binary(tmp_path / "bin" / "repograph")
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _fake_which(monkeypatch, lambda name: str(installed) if name == "repograph" else None)

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(dev_tree, "dev-tree")


def test_installed_binary_is_used_when_the_repo_has_no_crate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path)
    installed = _binary(tmp_path / "bin" / "repograph")
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _fake_which(monkeypatch, lambda name: str(installed) if name == "repograph" else None)

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(installed, "installed")


def test_cargo_bin_dir_is_searched_when_it_is_not_on_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`charness tool doctor repograph` and this resolver must never disagree.

    The manifest's detect command prepends `${CARGO_HOME:-$HOME/.cargo}/bin` to
    PATH because `cargo install` writes there and the invoking process's PATH may
    predate that write. If the resolver looked only at PATH, doctor would report
    the binary present while every gate reported it missing.
    """
    repo = _repo(tmp_path)
    cargo_home = tmp_path / "cargo-home"
    installed = _binary(cargo_home / "bin" / "repograph")
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    monkeypatch.setenv("CARGO_HOME", str(cargo_home))
    _fake_which(monkeypatch, lambda _name: None)

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(installed, "installed")


def test_nothing_available_names_the_control_plane_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path)
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _no_cargo_no_installed(monkeypatch, tmp_path)

    with pytest.raises(native_gate_lib.NativeGateError) as raised:
        native_gate_lib.resolve_native_core(repo)

    message = str(raised.value)
    assert "charness tool install repograph" in message
    assert "native/repograph" in message


def test_unbuilt_crate_is_built_and_the_build_is_announced_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, with_source=True)
    crate = repo / "native" / "repograph"
    binary = crate / "target" / "release" / "repograph"
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _fake_which(monkeypatch, lambda name: "/usr/bin/cargo" if name == "cargo" else None)
    calls: list[dict[str, object]] = []

    def fake_run(command, **kwargs):
        calls.append({"command": command, "cwd": kwargs.get("cwd")})
        _binary(binary)
        return _phase_outcome(command, **kwargs)

    monkeypatch.setattr(native_gate_lib, "run_monitored_phase", fake_run)

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(binary, "dev-tree")
    assert calls == [{"command": ["cargo", "build", "--release", "--locked"], "cwd": crate}]
    err = capfd.readouterr().err
    # Said before it happens, and specific about what and why.
    assert "is not built" in err
    assert "cargo build --release --locked" in err
    assert str(crate) in err


def test_source_newer_than_binary_triggers_an_announced_rebuild(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, with_source=True)
    crate = repo / "native" / "repograph"
    binary = _binary(crate / "target" / "release" / "repograph")
    source = crate / "src" / "main.rs"
    source.parent.mkdir(parents=True)
    source.write_text("fn main() {}\n", encoding="utf-8")
    import os

    binary_mtime = binary.stat().st_mtime
    os.utime(source, (binary_mtime + 60, binary_mtime + 60))
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _fake_which(monkeypatch, lambda name: "/usr/bin/cargo" if name == "cargo" else None)
    monkeypatch.setattr(
        native_gate_lib,
        "run_monitored_phase",
        lambda command, **kwargs: _phase_outcome(command, **kwargs),
    )

    resolved = native_gate_lib.resolve_native_core(repo)

    assert resolved == native_gate_lib.NativeGateBinary(binary, "dev-tree")
    err = capfd.readouterr().err
    assert "older than the crate source" in err
    assert "src/main.rs changed" in err


def test_fresh_binary_is_not_rebuilt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, with_source=True)
    crate = repo / "native" / "repograph"
    source = crate / "src" / "main.rs"
    source.parent.mkdir(parents=True)
    source.write_text("fn main() {}\n", encoding="utf-8")
    binary = _binary(crate / "target" / "release" / "repograph")
    import os

    source_mtime = source.stat().st_mtime
    os.utime(binary, (source_mtime + 60, source_mtime + 60))
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    monkeypatch.setattr(
        native_gate_lib,
        "run_monitored_phase",
        lambda *_args, **_kwargs: pytest.fail("a fresh binary must not be rebuilt"),
    )

    assert native_gate_lib.resolve_native_core(repo).path == binary


def test_unbuilt_crate_without_cargo_names_rustup_and_the_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, with_source=True)
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _no_cargo_no_installed(monkeypatch, tmp_path)

    with pytest.raises(native_gate_lib.NativeGateError) as raised:
        native_gate_lib.resolve_native_core(repo)

    message = str(raised.value)
    assert "rustup.rs" in message
    assert "charness tool install repograph" in message


def test_failed_build_does_not_fall_through_to_an_installed_binary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The anti-silent-swap invariant.

    Answering a failed build with a binary compiled from different source is
    exactly the substitution the build announcement exists to prevent.
    """
    repo = _repo(tmp_path, with_source=True)
    installed = _binary(tmp_path / "bin" / "repograph")
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _fake_which(
        monkeypatch,
        lambda name: "/usr/bin/cargo" if name == "cargo" else str(installed),
    )
    monkeypatch.setattr(
        native_gate_lib,
        "run_monitored_phase",
        lambda command, **kwargs: _phase_outcome(command, returncode=101, **kwargs),
    )

    with pytest.raises(native_gate_lib.NativeGateError) as raised:
        native_gate_lib.resolve_native_core(repo)

    message = str(raised.value)
    assert "exit code 101" in message
    assert "will not fall back" in message


def test_cargo_success_without_a_binary_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, with_source=True)
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _fake_which(monkeypatch, lambda name: "/usr/bin/cargo" if name == "cargo" else None)
    monkeypatch.setattr(
        native_gate_lib,
        "run_monitored_phase",
        lambda command, **kwargs: _phase_outcome(command, **kwargs),
    )

    with pytest.raises(native_gate_lib.NativeGateError, match="produced no binary"):
        native_gate_lib.resolve_native_core(repo)


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
                "if sys.argv[1:2] != ['export-safe']:",
                "    sys.stderr.write('fake repograph: unexpected argv %r\\n' % (sys.argv[1:],))",
                "    sys.exit(2)",
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
    # stdout carries ONLY the child's JSON: the provenance line the gate now always
    # prints must not reach a consumer that parses this stream.
    assert json.loads(captured.out)["schema"] == "repograph.export_safe.v1"
    assert "provenance: override" in captured.err


def test_probe_reports_resolution_without_running_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    repo = _repo(tmp_path)
    fake = _fake_repograph(tmp_path / "bin" / "repograph")
    marker = tmp_path / "ran"
    fake.write_text(
        fake.read_text(encoding="utf-8")
        .replace("payload = {", f"Path({str(marker)!r}).touch()\npayload = {{")
        .replace("import os", "import os\nfrom pathlib import Path"),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(fake))
    monkeypatch.setenv("FAKE_EXIT", "0")

    returned = native_gate_lib.main(["--repo-root", str(repo), "--probe", "export-safe"])

    captured = capfd.readouterr()
    assert returned == 0
    assert "provenance: override" in captured.err
    assert not marker.exists()


# --- error paths -------------------------------------------------------------
#
# Every branch below was reported as an uncovered CHANGED line by
# `release-changed-line-coverage` once its instrumentation was repaired. They are
# the paths that decide what an operator sees when something is wrong, so leaving
# them unexercised means the failure messages are unproven.


def test_an_unreadable_source_file_does_not_abort_the_staleness_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A source file that cannot be stat'ed is skipped, not fatal.

    The walk exists to answer "is the binary older than the crate". One
    unreadable file must not turn that question into a crash, because the
    binary may still be perfectly fresh with respect to everything readable.
    """
    repo = _repo(tmp_path, with_source=True)
    crate = repo / "native" / "repograph"
    (crate / "src").mkdir(parents=True)
    (crate / "src" / "main.rs").write_text("fn main() {}\n", encoding="utf-8")
    binary = _binary(crate / "target" / "release" / "repograph")

    real_stat = Path.stat

    def refusing_stat(self, *args, **kwargs):
        if self.name == "main.rs":
            raise OSError("unreadable")
        return real_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", refusing_stat)

    assert native_gate_lib.dev_tree_staleness(crate, binary) is None


def test_an_unstattable_binary_is_treated_as_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown freshness resolves toward rebuilding, never toward trusting.

    The alternative -- treating an unreadable binary as fresh -- is the silent
    pass this module exists to avoid.
    """
    repo = _repo(tmp_path, with_source=True)
    crate = repo / "native" / "repograph"
    binary = crate / "target" / "release" / "repograph"

    def refusing_stat(self, *args, **kwargs):
        raise OSError("unreadable")

    monkeypatch.setattr(Path, "stat", refusing_stat)

    assert native_gate_lib.dev_tree_staleness(crate, binary) == crate / "Cargo.toml"


def test_main_requires_a_repograph_command(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as raised:
        native_gate_lib.main(["--repo-root", str(tmp_path)])

    assert raised.value.code == 2


def test_main_reports_an_unresolvable_binary_on_stderr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path)
    monkeypatch.delenv("CHARNESS_NATIVE_CORE", raising=False)
    _no_cargo_no_installed(monkeypatch, tmp_path)

    returned = native_gate_lib.main(["--repo-root", str(repo), "export-safe"])

    captured = capfd.readouterr()
    assert returned == 1
    assert "charness tool install repograph" in captured.err
    # stdout stays empty: a consumer parsing this stream must not receive prose.
    assert captured.out == ""


def test_main_reports_a_binary_it_cannot_execute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A resolved-but-unexecutable binary is a distinct failure from an absent one."""
    repo = _repo(tmp_path)
    unexecutable = tmp_path / "bin" / "repograph"
    unexecutable.parent.mkdir(parents=True)
    unexecutable.write_text("not executable\n", encoding="utf-8")
    unexecutable.chmod(0o644)
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(unexecutable))

    returned = native_gate_lib.main(["--repo-root", str(repo), "export-safe"])

    captured = capfd.readouterr()
    assert returned == 1
    assert "could not execute" in captured.err
