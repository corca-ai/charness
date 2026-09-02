"""Behavioural cover for `scripts/plugin_export/specdown_ephemeral_config.py`.

The failure this helper exists to stop: the quality gate rewriting the tracked
specdown report it only reads, dirtying the worktree on every run for a changed
`generatedAt` timestamp. So the load-bearing behaviour is narrow and specific --
reporters that declare an `outFile` get it redirected into the throwaway out-dir,
reporters that do not are left alone (specdown owns their default, and inventing
one here would be the helper deciding a question it was not asked), the source
config is never mutated, and the generated file lands *beside the source config*
so a relative `entry` still resolves.

These run in-process rather than through the CLI: the behaviour under test is
ordinary domain logic plus a thin argparse shell, not a packaging, exit-code, or
stderr-protocol contract, so it does not need a delivery-boundary crossing.
`main()` is driven by patching `sys.argv` and read back through `capsys`.
`test_quality_runner.py` separately covers the wiring into the runner script.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.plugin_export.specdown_ephemeral_config import (
    EPHEMERAL_CONFIG_NAME,
    build_ephemeral_config,
    main,
)

from .support import ROOT

SOURCE_CONFIG = {
    "entry": "specs/index.spec.md",
    "adapters": [],
    "reporters": [
        {"builtin": "html", "outFile": ".charness/specdown/report"},
        {"builtin": "json", "outFile": ".charness/specdown/report.json"},
    ],
    "defaultTimeoutMsec": 120000,
}


def _write_source(root: Path, config: dict | None = None) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "specdown.json"
    path.write_text(json.dumps(config if config is not None else SOURCE_CONFIG), encoding="utf-8")
    return path


def test_reporter_with_out_file_is_redirected_into_out_dir_keeping_its_basename(
    tmp_path: Path,
) -> None:
    """The whole point: a declared destination moves into the throwaway directory,
    and keeps its filename so the report is still recognisable there."""
    out_dir = tmp_path / "throwaway"

    config = build_ephemeral_config(SOURCE_CONFIG, out_dir)

    by_builtin = {reporter["builtin"]: reporter for reporter in config["reporters"]}
    assert by_builtin["json"]["outFile"] == str(out_dir / "report.json")
    assert by_builtin["html"]["outFile"] == str(out_dir / "report")
    for reporter in config["reporters"]:
        assert Path(reporter["outFile"]).parent == out_dir, reporter


def test_reporter_without_an_out_file_is_left_alone(tmp_path: Path) -> None:
    """Deliberate non-behaviour: specdown owns the default destination for a
    reporter that declares none. Synthesising one here would be this helper
    answering a question nobody asked it -- and would silently change where a
    default-destination reporter writes."""
    source = {"reporters": [{"builtin": "html"}, {"builtin": "json", "outFile": "r.json"}]}

    config = build_ephemeral_config(source, tmp_path / "out")

    assert config["reporters"][0] == {"builtin": "html"}
    assert "outFile" not in config["reporters"][0]
    assert config["reporters"][1]["outFile"] == str(tmp_path / "out" / "r.json")


@pytest.mark.parametrize("empty", ["", None])
def test_falsy_out_file_is_treated_as_absent(tmp_path: Path, empty: str | None) -> None:
    """An empty or null `outFile` is not a path to redirect; joining it onto the
    out-dir would invent the out-dir itself as the destination."""
    source = {"reporters": [{"builtin": "json", "outFile": empty}]}

    config = build_ephemeral_config(source, tmp_path / "out")

    assert config["reporters"][0]["outFile"] == empty


def test_non_reporter_keys_are_copied_through_unchanged(tmp_path: Path) -> None:
    """Everything the helper was not asked about survives verbatim -- especially
    `entry`, which specdown resolves against the config file's own directory, so
    absolutising it would send specdown looking in the wrong tree."""
    config = build_ephemeral_config(SOURCE_CONFIG, tmp_path / "out")

    assert config["entry"] == SOURCE_CONFIG["entry"]
    assert not Path(config["entry"]).is_absolute()
    assert config["adapters"] == SOURCE_CONFIG["adapters"]
    assert config["defaultTimeoutMsec"] == SOURCE_CONFIG["defaultTimeoutMsec"]
    assert set(config) == set(SOURCE_CONFIG)


def test_source_config_is_not_mutated(tmp_path: Path) -> None:
    """The caller's dict is input, not scratch space: a shallow copy would leave
    the caller's own reporter dicts rewritten to point at a directory that is
    deleted when the run ends."""
    source = json.loads(json.dumps(SOURCE_CONFIG))
    before = json.dumps(source, sort_keys=True)

    config = build_ephemeral_config(source, tmp_path / "out")

    assert json.dumps(source, sort_keys=True) == before
    assert config["reporters"][0] is not source["reporters"][0]


def test_config_without_reporters_is_passed_through(tmp_path: Path) -> None:
    """A config that declares no reporters is not an error condition."""
    assert build_ephemeral_config({"entry": "s.md"}, tmp_path / "out") == {"entry": "s.md"}


def _run_main(monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    monkeypatch.setattr(sys, "argv", ["specdown_ephemeral_config.py", *argv])
    return main()


def test_main_writes_the_config_beside_the_source_and_prints_its_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Location is the contract: specdown joins `entry` onto the config file's own
    directory, so a config parked in the out-dir would look for the specs there."""
    repo = tmp_path / "repo"
    source_path = _write_source(repo)
    out_dir = tmp_path / "out"

    exit_code = _run_main(monkeypatch, "--repo-root", str(repo), "--out-dir", str(out_dir))

    assert exit_code == 0
    written = repo / EPHEMERAL_CONFIG_NAME
    assert written.exists()
    assert not (out_dir / EPHEMERAL_CONFIG_NAME).exists()
    assert written.parent == source_path.parent
    printed = capsys.readouterr().out.strip()
    assert printed == str(written)
    assert Path(printed).exists()


def test_main_out_dir_is_created_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Callers hand over a directory the reporters must be able to write into;
    specdown will not create a missing parent for them."""
    repo = tmp_path / "repo"
    _write_source(repo)
    out_dir = tmp_path / "missing" / "nested" / "out"
    assert not out_dir.exists()

    assert _run_main(monkeypatch, "--repo-root", str(repo), "--out-dir", str(out_dir)) == 0

    capsys.readouterr()
    assert out_dir.is_dir()


def test_main_written_config_redirects_reporters_out_of_the_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end: whatever lands on disk is what specdown is handed, so assert on
    the file rather than on the in-memory return value."""
    repo = tmp_path / "repo"
    _write_source(repo)
    out_dir = tmp_path / "out"

    assert _run_main(monkeypatch, "--repo-root", str(repo), "--out-dir", str(out_dir)) == 0

    written = Path(capsys.readouterr().out.strip())
    config = json.loads(written.read_text(encoding="utf-8"))
    assert config["entry"] == SOURCE_CONFIG["entry"]
    for reporter in config["reporters"]:
        out_file = Path(reporter["outFile"])
        assert out_file.is_absolute(), reporter
        assert out_file.is_relative_to(out_dir), reporter
        assert not out_file.is_relative_to(repo), reporter


def test_main_explicit_config_flag_overrides_the_repo_root_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--config` names the source config; the ephemeral file must follow it, not
    the repo root, or the relative `entry` resolves against the wrong directory."""
    repo = tmp_path / "repo"
    _write_source(repo, {"entry": "repo.spec.md", "reporters": []})
    elsewhere = tmp_path / "elsewhere"
    other_source = _write_source(elsewhere, {"entry": "other.spec.md", "reporters": []})

    assert (
        _run_main(
            monkeypatch,
            "--repo-root",
            str(repo),
            "--config",
            str(other_source),
            "--out-dir",
            str(tmp_path / "out"),
        )
        == 0
    )

    written = Path(capsys.readouterr().out.strip())
    assert written == elsewhere / EPHEMERAL_CONFIG_NAME
    assert not (repo / EPHEMERAL_CONFIG_NAME).exists()
    assert json.loads(written.read_text(encoding="utf-8"))["entry"] == "other.spec.md"


def test_main_reads_consumer_specdown_config_universe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "consumer"
    config = _write_source(repo / "src", {"entry": "consumer.spec.md", "reporters": []})
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nuniverses:\n  specdown_config: src/specdown.json\n",
        encoding="utf-8",
    )

    assert _run_main(monkeypatch, "--repo-root", str(repo), "--out-dir", str(tmp_path / "out")) == 0

    written = Path(capsys.readouterr().out.strip())
    assert config == repo / "src" / "specdown.json"
    assert written == config.parent / EPHEMERAL_CONFIG_NAME
    assert json.loads(written.read_text(encoding="utf-8"))["entry"] == "consumer.spec.md"


def test_main_refuses_missing_declared_specdown_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nuniverses:\n  specdown_config: src/specdown.json\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as excinfo:
        _run_main(monkeypatch, "--repo-root", str(repo), "--out-dir", str(tmp_path / "out"))

    assert "specdown: refusing empty declared universe" in str(excinfo.value)


def test_main_defaults_the_source_config_to_the_cwd_repo_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--repo-root` defaults to the working directory, which is how the documented
    one-liner (`--out-dir "$tmpdir"` alone) finds `specdown.json` at all."""
    repo = tmp_path / "repo"
    _write_source(repo)
    monkeypatch.chdir(repo)

    assert _run_main(monkeypatch, "--out-dir", str(tmp_path / "out")) == 0

    assert Path(capsys.readouterr().out.strip()) == repo / EPHEMERAL_CONFIG_NAME


def test_main_requires_an_out_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a destination there is nothing to redirect into; failing loudly beats
    defaulting to somewhere inside the repo."""
    _write_source(tmp_path / "repo")

    with pytest.raises(SystemExit) as excinfo:
        _run_main(monkeypatch, "--repo-root", str(tmp_path / "repo"))

    assert excinfo.value.code != 0


@pytest.mark.boundary_contract(
    reason="exercise specdown ephemeral config's __main__ dispatch as a real executable"
)
def test_cli_entrypoint_dispatches_through_main_and_exits_zero(tmp_path: Path) -> None:
    """One real CLI smoke, deliberately at the process boundary.

    Everything above runs in-process. This one case exists because the
    `if __name__ == "__main__": raise SystemExit(main())` dispatch is only
    reachable by actually starting the script, and `run-quality.sh` consumes this
    helper exactly that way -- it reads the written path off stdout and branches on
    the exit code. An in-process call cannot prove the script starts, resolves its
    imports, or propagates `main()`'s return code as an exit status.
    """
    repo = tmp_path / "repo"
    _write_source(repo)
    out_dir = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "plugin_export" / "specdown_ephemeral_config.py"),
            "--repo-root",
            str(repo),
            "--out-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    written = Path(result.stdout.strip())
    assert written == repo / EPHEMERAL_CONFIG_NAME
    assert written.is_file()
    # The redirected reporter really landed outside the source tree.
    config = json.loads(written.read_text(encoding="utf-8"))
    assert all(
        Path(reporter["outFile"]).parent == out_dir
        for reporter in config["reporters"]
        if reporter.get("outFile")
    )
