from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.gates.check_temp_producer_inventory import (
    SCHEMA,
    Producer,
    discover_producers,
    validate_inventory,
)
from scripts.runtime_scratch import inspect_scratch_roots

ROOT = Path(__file__).resolve().parents[1]


def _write_manifest(repo: Path, producers: list[Producer], disposition: str) -> Path:
    lines = [f"schema: {SCHEMA}", "producers:"]
    for producer in producers:
        lines.extend(
            [
                f"- identity: {producer.identity}",
                f"  path: {producer.path}",
                f"  symbol: {producer.symbol}",
                f"  disposition: {disposition}",
                "  rationale: fixture classification",
            ]
        )
    manifest = repo / ".agents" / "temp-producers.yaml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def test_inventory_parses_calls_and_excludes_comments_and_prose(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "python_case.py").write_text(
        '"""tempfile.mkdtemp() in documentation is not a producer."""\n'
        "import tempfile\n"
        "# tempfile.mkdtemp() in a comment is not a producer\n"
        "def make():\n"
        "    return tempfile.mkdtemp()\n",
        encoding="utf-8",
    )
    (scripts / "shell_case.sh").write_text(
        '# mktemp -d in a comment\n'
        'echo "mktemp -d in prose"\n'
        'scratch="$(mktemp -d)"\n',
        encoding="utf-8",
    )
    (scripts / "javascript_case.mjs").write_text(
        '// mkdtempSync(tmpdir()) in a comment\n'
        'const prose = "mkdtempSync(tmpdir())";\n'
        "function make() {\n"
        "  return mkdtempSync(tmpdir());\n"
        "}\n",
        encoding="utf-8",
    )

    producers = discover_producers(tmp_path)

    assert [producer.identity for producer in producers] == [
        "scripts/javascript_case.mjs::make::mkdtempSync",
        "scripts/python_case.py::make::mkdtemp",
        "scripts/shell_case.sh::shell::scratch",
    ]
    assert {producer.kind for producer in producers} == {"directory"}


def test_inventory_identities_survive_line_movement(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = scripts / "stable.py"
    source.write_text("import tempfile\ndef create():\n    return tempfile.mkdtemp()\n", encoding="utf-8")
    first = discover_producers(tmp_path)
    source.write_text(
        "# moved without changing the producer identity\n\n"
        "import tempfile\n\n\n\n"
        "def create():\n    return tempfile.mkdtemp()\n",
        encoding="utf-8",
    )
    second = discover_producers(tmp_path)

    assert first[0].identity == second[0].identity
    assert first[0].line != second[0].line


def test_missing_unregistered_and_stale_entries_are_negative_controls(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = scripts / "fixture.py"
    source.write_text(
        "import tempfile\n"
        "def fixture():\n"
        "    return tempfile.TemporaryDirectory()\n",
        encoding="utf-8",
    )
    detected = discover_producers(tmp_path)
    manifest = _write_manifest(tmp_path, detected, "test-compatibility-only")

    assert validate_inventory(tmp_path, manifest_path=manifest)["ok"] is True

    manifest.write_text(f"schema: {SCHEMA}\nproducers: []\n", encoding="utf-8")
    missing = validate_inventory(tmp_path, manifest_path=manifest)
    assert missing["missing"] == [detected[0].identity]
    assert missing["unowned_directory_creators"] == [detected[0].identity]

    _write_manifest(tmp_path, detected, "test-compatibility-only")
    extra = scripts / "new.py"
    extra.write_text("import tempfile\nnew_root = tempfile.mkdtemp()\n", encoding="utf-8")
    unregistered = validate_inventory(tmp_path, manifest_path=manifest)
    assert any("new.py" in identity for identity in unregistered["missing"])
    assert any("new.py" in identity for identity in unregistered["unowned_directory_creators"])

    source.write_text("def fixture():\n    return None\n", encoding="utf-8")
    extra.unlink()
    stale = validate_inventory(tmp_path, manifest_path=manifest)
    assert stale["stale"] == [detected[0].identity]
    assert stale["ok"] is False


def test_owned_shell_registration_is_a_directory_boundary(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = scripts / "owned.sh"
    source.write_text(
        'scratch="$CHARNESS_OWNED_SCRATCH_ROOT/owned"\n'
        'mkdir -p "$scratch"\n',
        encoding="utf-8",
    )
    detected = discover_producers(tmp_path)
    assert len(detected) == 1
    assert detected[0].kind == "owned-directory"
    manifest = _write_manifest(tmp_path, detected, "owned-scratch")
    assert validate_inventory(tmp_path, manifest_path=manifest)["ok"] is True


@pytest.mark.boundary_contract(
    reason="this test crosses a real process to prove the standalone shell owner preserves verdicts"
)
@pytest.mark.parametrize(
    ("mode", "expected_returncode"),
    [("success", 0), ("failure", 7), ("timeout", 124), ("cancellation", 130)],
)
def test_standalone_shell_adapter_preserves_verdict_and_cleans_root(
    tmp_path: Path, mode: str, expected_returncode: int
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    runtime = tmp_path / "runtime"
    child_prefix = (
        "import os, pathlib, sys; "
        "root = pathlib.Path(os.environ['CHARNESS_OWNED_SCRATCH_ROOT']); "
        "(root / 'child-output').mkdir(); "
        "print(root, flush=True); "
    )
    if mode == "success":
        child = child_prefix + "raise SystemExit(0)"
    elif mode == "failure":
        child = child_prefix + "raise SystemExit(7)"
    elif mode == "timeout":
        child = child_prefix + "[None for _ in iter(int, 1)]"
    else:
        child = (
            child_prefix
            + "os.kill(os.getppid(), __import__('signal').SIGINT); "
            + "__import__('signal').pause()"
        )
    environment = {
        **os.environ,
        "CHARNESS_RUNTIME_ROOT": str(runtime),
        "CHARNESS_RUNTIME_ROOT_AUTO": "0",
    }
    command = [
        sys.executable,
        str(ROOT / "scripts/gates/run_owned_scratch_command.py"),
        "--repo-root",
        str(repo),
        "--producer",
        "shell-fixture",
        "--",
        sys.executable,
        "-c",
        child,
    ]
    if mode == "timeout":
        command[6:6] = ["--timeout-seconds", "0.1"]
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == expected_returncode, result.stderr
    if mode != "cancellation":
        owned_path = Path(result.stdout.strip())
        assert owned_path.is_relative_to(runtime / "scratch" / "shell-fixture")
        assert not owned_path.exists()
    assert list((runtime / "scratch" / "shell-fixture").iterdir()) == []
    assert inspect_scratch_roots(repo, runtime_root_path=runtime)["roots"] == []
