"""Decaying-habit advisories (#364).

Two recurring pre-commit-gate author habits, surfaced author-time BEFORE the
blocking gates so the fix happens before the rejected-commit round-trip:
(1) a repo-root scripts/*.py change whose plugin mirror is stale (the
staged-mirror-drift gate enforces it); (2) a test that subprocesses an
import-safe scripts/*.py when an in-process main() exists (the boundary-bypass
ratchet enforces it). Both are non-blocking and reuse the real signals.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import slice_closeout_commit_advisories as adv
from scripts.slice_closeout_commit_advisories import (
    _changed_scripts_mirror_drift,
    _changed_tests_boundary_bypass,
    advise_decaying_habits,
)


def _fake_packaging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make _changed_scripts_mirror_drift resolve the mirror root without loading
    (and validating) the real packaging manifest."""
    real_import = adv.import_repo_module

    def fake(file, module):
        if module == "scripts.packaging_lib":
            return SimpleNamespace(
                load_manifest=lambda repo_root, package_id: {},
                checked_in_plugin_root=lambda manifest: Path("plugins/charness"),
            )
        return real_import(file, module)

    monkeypatch.setattr(adv, "import_repo_module", fake)


# --- habit 1: proactive plugin-mirror sync ---


def _write_script_pair(repo: Path, rel: str, source: str, mirror: str | None) -> None:
    src = repo / rel
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(source, encoding="utf-8")
    if mirror is not None:
        mir = repo / "plugins" / "charness" / rel
        mir.parent.mkdir(parents=True, exist_ok=True)
        mir.write_text(mirror, encoding="utf-8")


def test_mirror_drift_silent_when_mirror_matches(monkeypatch, tmp_path) -> None:
    _fake_packaging(monkeypatch)
    _write_script_pair(tmp_path, "scripts/x.py", "print('hi')\n", "print('hi')\n")
    assert _changed_scripts_mirror_drift(tmp_path, ["scripts/x.py"]) == []


def test_mirror_drift_flags_stale_mirror(monkeypatch, tmp_path) -> None:
    _fake_packaging(monkeypatch)
    _write_script_pair(tmp_path, "scripts/x.py", "print('new')\n", "print('old')\n")
    assert _changed_scripts_mirror_drift(tmp_path, ["scripts/x.py"]) == ["scripts/x.py"]


def test_mirror_drift_flags_missing_mirror(monkeypatch, tmp_path) -> None:
    _fake_packaging(monkeypatch)
    _write_script_pair(tmp_path, "scripts/x.py", "print('new')\n", None)
    assert _changed_scripts_mirror_drift(tmp_path, ["scripts/x.py"]) == ["scripts/x.py"]


def test_mirror_drift_ignores_non_scripts_changes(monkeypatch, tmp_path) -> None:
    _fake_packaging(monkeypatch)
    assert _changed_scripts_mirror_drift(tmp_path, ["docs/x.md", "tests/test_x.py"]) == []


def test_mirror_drift_degrades_when_manifest_unloadable(monkeypatch, tmp_path) -> None:
    def boom(file, module):
        raise RuntimeError("no manifest")

    monkeypatch.setattr(adv, "import_repo_module", boom)
    _write_script_pair(tmp_path, "scripts/x.py", "a\n", "b\n")
    assert _changed_scripts_mirror_drift(tmp_path, ["scripts/x.py"]) == []


# --- habit 2: in-process test default for import-safe scripts ---

_IMPORT_SAFE_SCRIPT = (
    "def main():\n"
    "    return 0\n"
    "\n"
    "\n"
    "if __name__ == '__main__':\n"
    "    raise SystemExit(main())\n"
)


def _seed_boundary_repo(tmp_path: Path, *, test_body: str, exemption: str | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir(parents=True)
    (repo / "scripts" / "y.py").write_text(_IMPORT_SAFE_SCRIPT, encoding="utf-8")
    (repo / "tests" / "test_x.py").write_text(test_body, encoding="utf-8")
    if exemption is not None:
        (repo / "scripts" / "boundary-bypass-exemptions.txt").write_text(exemption, encoding="utf-8")
    return repo


def test_boundary_bypass_flags_subprocess_of_import_safe_script(tmp_path) -> None:
    repo = _seed_boundary_repo(
        tmp_path,
        test_body=(
            "import subprocess\n"
            "def test_it():\n"
            "    subprocess.run(['python3', 'scripts/y.py'], check=True)\n"
        ),
    )
    findings = _changed_tests_boundary_bypass(repo, ["tests/test_x.py"])
    assert findings == [("tests/test_x.py", ["scripts/y.py"])]


def test_boundary_bypass_silent_for_in_process_test(tmp_path) -> None:
    repo = _seed_boundary_repo(
        tmp_path,
        test_body=(
            "from scripts import y\n"
            "def test_it():\n"
            "    assert y.main() == 0\n"
        ),
    )
    assert _changed_tests_boundary_bypass(repo, ["tests/test_x.py"]) == []


def test_boundary_bypass_honors_exemptions(tmp_path) -> None:
    repo = _seed_boundary_repo(
        tmp_path,
        test_body=(
            "import subprocess\n"
            "def test_it():\n"
            "    subprocess.run(['python3', 'scripts/y.py'], check=True)\n"
        ),
        exemption="tests/test_x.py::scripts/y.py # why: intentional exit-code contract\n",
    )
    assert _changed_tests_boundary_bypass(repo, ["tests/test_x.py"]) == []


def test_boundary_bypass_ignores_non_test_changes(tmp_path) -> None:
    repo = _seed_boundary_repo(
        tmp_path,
        test_body="import subprocess\nsubprocess.run(['python3', 'scripts/y.py'])\n",
    )
    assert _changed_tests_boundary_bypass(repo, ["scripts/y.py", "docs/x.md"]) == []


# --- orchestration ---


def test_advise_fires_both_habits(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    monkeypatch.setattr(adv, "_changed_scripts_mirror_drift", lambda r, c: ["scripts/x.py"])
    monkeypatch.setattr(adv, "_changed_tests_boundary_bypass", lambda r, c: [("tests/test_x.py", ["scripts/y.py"])])
    advise_decaying_habits(tmp_path, ["scripts/x.py", "tests/test_x.py"])
    err = capsys.readouterr().err
    assert "stale plugin mirror (#364)" in err
    assert "sync_root_plugin_manifests.py" in err
    assert "subprocess an import-safe" in err
    assert "tests/test_x.py -> scripts/y.py" in err


def test_advise_silent_when_clean(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    monkeypatch.setattr(adv, "_changed_scripts_mirror_drift", lambda r, c: [])
    monkeypatch.setattr(adv, "_changed_tests_boundary_bypass", lambda r, c: [])
    advise_decaying_habits(tmp_path, ["scripts/x.py"])
    assert capsys.readouterr().err == ""


def test_advise_is_non_blocking(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(adv, "_changed_scripts_mirror_drift", lambda r, c: ["scripts/x.py"])
    monkeypatch.setattr(adv, "_changed_tests_boundary_bypass", lambda r, c: [])
    assert advise_decaying_habits(tmp_path, ["scripts/x.py"]) is None


def test_advise_not_wired_into_blocking_commit_gate() -> None:
    # Floor-Addition Restraint: stays an advisory, never a blocking gate.
    from scripts import staged_commit_gate_plan

    text = Path(staged_commit_gate_plan.__file__).read_text(encoding="utf-8")
    assert "advise_decaying_habits" not in text
    assert "decaying_habit" not in text
