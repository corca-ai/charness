from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.gates import check_temp_producer_inventory as inventory_cli
from scripts.gates import run_owned_scratch_command as scratch_adapter
from scripts.gates import temp_producer_inventory_lib as temp_inventory_lib
from scripts.gates.check_temp_producer_inventory import (
    SCHEMA,
    Producer,
    discover_producers,
    validate_inventory,
)
from scripts.gates.temp_producer_inventory_lib import (
    javascript_producers,
    python_producers,
    shell_producers,
)
from scripts.runtime_scratch import inspect_scratch_roots

ROOT = Path(__file__).resolve().parents[1]


def test_direct_run_bootstraps_restore_repo_import_path() -> None:
    root = str(ROOT)
    original = sys.path[:]
    try:
        sys.path[:] = [entry for entry in sys.path if entry != root]
        inventory_cli._load_repo_runtime_bootstrap()
        assert root in sys.path
        sys.path[:] = [entry for entry in sys.path if entry != root]
        temp_inventory_lib._load_repo_runtime_bootstrap()
        assert root in sys.path
    finally:
        sys.path[:] = original


def test_manifest_validation_reports_malformed_rows_and_cli_failure(tmp_path: Path, capsys) -> None:
    missing = inventory_cli.load_manifest(tmp_path, Path("missing.yaml"))
    assert "cannot read manifest" in missing[1][0]
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("schema: wrong\nproducers: []\n", encoding="utf-8")
    assert "manifest schema" in inventory_cli.load_manifest(tmp_path, manifest)[1][0]
    manifest.write_text(f"schema: {SCHEMA}\nproducers: nope\n", encoding="utf-8")
    assert inventory_cli.load_manifest(tmp_path, manifest)[1] == [
        "manifest.producers must be a list"
    ]
    manifest.write_text(
        f"schema: {SCHEMA}\nproducers:\n- nope\n- identity: ''\n"
        "- identity: duplicate\n  path: x\n  symbol: x\n  disposition: bad\n  rationale: x\n"
        "- identity: duplicate\n  path: ''\n  symbol: ''\n  disposition: owned-scratch\n  rationale: ''\n",
        encoding="utf-8",
    )
    _rows, errors = inventory_cli.load_manifest(tmp_path, manifest)
    assert len(errors) == 7
    assert inventory_cli.main(["--repo-root", str(tmp_path), "--manifest", str(manifest)]) == 1
    assert "check-temp-producer-inventory:" in capsys.readouterr().err
    clean = tmp_path / "clean"
    clean.mkdir()
    clean_manifest = clean / "manifest.yaml"
    clean_manifest.write_text(f"schema: {SCHEMA}\nproducers: []\n", encoding="utf-8")
    assert inventory_cli.main(["--repo-root", str(clean), "--manifest", str(clean_manifest)]) == 0
    assert "Validated temporary-output inventory" in capsys.readouterr().err


def test_inventory_reports_parse_and_manifest_identity_mismatches(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = scripts / "broken.py"
    source.write_text("def broken(:\n", encoding="utf-8")
    parse_report = validate_inventory(tmp_path, producers=python_producers(source, tmp_path))
    assert parse_report["errors"][-1] == "one or more producer files could not be parsed"

    source.write_text(
        "import tempfile\ndef make():\n    return tempfile.mkdtemp()\n", encoding="utf-8"
    )
    detected = python_producers(source, tmp_path)
    manifest = _write_manifest(tmp_path, detected, "owned-scratch")
    text_value = manifest.read_text(encoding="utf-8")
    manifest.write_text(
        text_value.replace("path: scripts/broken.py", "path: wrong.py").replace(
            "symbol: mkdtemp", "symbol: wrong"
        ),
        encoding="utf-8",
    )
    report = validate_inventory(tmp_path, manifest_path=manifest, producers=detected)
    assert any("path does not match" in error for error in report["errors"])
    assert any("symbol does not match" in error for error in report["errors"])
    owned = [
        Producer(item.identity, item.path, "owned-directory", item.symbol, item.line, item.evidence)
        for item in detected
    ]
    manifest.write_text(
        text_value.replace("disposition: owned-scratch", "disposition: durable-output"),
        encoding="utf-8",
    )
    assert any(
        "must use disposition 'owned-scratch'" in error
        for error in validate_inventory(tmp_path, manifest_path=manifest, producers=owned)["errors"]
    )


def test_language_scanners_cover_alias_scope_quote_and_comment_edges(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    py = scripts / "edges.py"
    py.write_text(
        "from tempfile import mkdtemp as make_temp, TemporaryDirectory\n"
        "class Scope:\n    async def build(self):\n        annotated: str = make_temp()\n        with TemporaryDirectory() as held:\n            return annotated, held\n",
        encoding="utf-8",
    )
    found = python_producers(py, tmp_path)
    assert {item.symbol for item in found} == {"annotated", "held"}
    assert all("Scope.build" in item.identity for item in found)

    shell = scripts / "edges.sh"
    shell.write_text(
        "echo 'mktemp -d'\nvalue=\"$NAME $(echo nested)\"\n"
        "cat <<'EOF'\nmktemp -d\nEOF\nactual=$(mktemp -d)\n"
        'nested="$(echo $(mktemp -d))" # trailing comment\n',
        encoding="utf-8",
    )
    assert [item.symbol for item in shell_producers(shell, tmp_path)] == ["actual", "command"]

    js = scripts / "edges.mjs"
    js.write_text(
        "// mkdtempSync(tmpdir())\nconst quoted = 'mkdtempSync(tmpdir())';\n"
        '/* ignored */\nconst escaped = "x\\\\ny";\n'
        "function build() { return mkdtempSync(tmpdir()); }\n"
        "const owned = join(process.env.CHARNESS_OWNED_SCRATCH_ROOT, 'child');\n",
        encoding="utf-8",
    )
    js_found = javascript_producers(js, tmp_path)
    assert js_found[0].identity.endswith("::build::mkdtempSync")
    assert js_found[1].kind == "owned-directory"
    assert temp_inventory_lib._dotted(__import__("ast").Constant(value=1)) == ""
    assert shell_producers(scripts / "missing.sh", tmp_path)[0].kind == "parse-error"
    assert javascript_producers(scripts / "missing.mjs", tmp_path)[0].kind == "parse-error"


class _FakeOwner:
    def __init__(self, root: Path, *, close_error: bool = False) -> None:
        self.root = root
        self.close_error = close_error
        self.states: list[str] = []

    def open(self) -> Path:
        self.root.mkdir()
        return self.root

    def close(self, *, state: str) -> None:
        self.states.append(state)
        if self.close_error:
            raise OSError("cleanup failed")


def test_owned_scratch_adapter_in_process_verdicts_and_cleanup_warning(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    owner = _FakeOwner(tmp_path / "owned", close_error=True)
    monkeypatch.setattr(scratch_adapter, "owned_scratch", lambda *_args: owner)
    monkeypatch.setattr(
        scratch_adapter,
        "run_monitored_phase",
        lambda *_args, **kwargs: type("Outcome", (), {"returncode": -9})(),
    )
    assert (
        scratch_adapter.main(["--repo-root", str(tmp_path), "--producer", "fixture", "--", "child"])
        == 137
    )
    assert owner.states == ["failed"]
    assert "cleanup failed" in capsys.readouterr().err
    with pytest.raises(SystemExit, match="a command is required"):
        scratch_adapter.main(["--repo-root", str(tmp_path), "--producer", "fixture"])


@pytest.mark.parametrize("raised", [KeyboardInterrupt(), RuntimeError("boom")])
def test_owned_scratch_adapter_in_process_interruptions(
    tmp_path: Path, monkeypatch, raised: BaseException
) -> None:
    owner = _FakeOwner(tmp_path / "owned")
    monkeypatch.setattr(scratch_adapter, "owned_scratch", lambda *_args: owner)
    monkeypatch.setattr(
        scratch_adapter,
        "run_monitored_phase",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(raised),
    )
    argv = ["--repo-root", str(tmp_path), "--producer", "fixture", "child"]
    if isinstance(raised, KeyboardInterrupt):
        assert scratch_adapter.main(argv) == 130
    else:
        with pytest.raises(RuntimeError, match="boom"):
            scratch_adapter.main(argv)
    assert owner.states == ["failed"]


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
        '# mktemp -d in a comment\necho "mktemp -d in prose"\nscratch="$(mktemp -d)"\n',
        encoding="utf-8",
    )
    (scripts / "javascript_case.mjs").write_text(
        "// mkdtempSync(tmpdir()) in a comment\n"
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
    source.write_text(
        "import tempfile\ndef create():\n    return tempfile.mkdtemp()\n", encoding="utf-8"
    )
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
        "import tempfile\ndef fixture():\n    return tempfile.TemporaryDirectory()\n",
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
        'scratch="$CHARNESS_OWNED_SCRATCH_ROOT/owned"\nmkdir -p "$scratch"\n',
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
    if mode in {"success", "failure"}:
        owned_path = Path(result.stdout.strip())
        assert owned_path.is_relative_to(runtime / "scratch" / "shell-fixture")
        assert not owned_path.exists()
    assert list((runtime / "scratch" / "shell-fixture").iterdir()) == []
    assert inspect_scratch_roots(repo, runtime_root_path=runtime)["roots"] == []
