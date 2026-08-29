from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT, init_git_repo, run_script

SPEC = importlib.util.spec_from_file_location(
    "check_test_production_ratio", ROOT / "scripts" / "check_test_production_ratio.py"
)
assert SPEC is not None and SPEC.loader is not None
RATIO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RATIO)


def test_test_production_ratio_counts_source_truth_without_plugin_exports() -> None:
    summary = RATIO.summarize(ROOT, engine="splitlines")

    assert summary["scope"] == "executable-surface"
    assert summary["engine"] == "splitlines"
    assert summary["engine_selection"] == "explicit"
    # The live hard bound (test LOC < source LOC) stays out of this unit test, and
    # there is no longer a live hard bound to duplicate: run-quality.sh runs the gate
    # ADVISORY again (see test_ratio_gate_stays_advisory_in_the_runner). This measures
    # the surface; it does not gate on it.
    assert summary["source_lines"] > 0
    assert summary["test_lines"] > 0
    assert summary["ratio"] > 0
    assert set(RATIO.SURFACE_BUCKETS) <= set(summary["surface_breakdown"])
    assert summary["surface_breakdown"]["python-shebang"] > 0
    assert summary["surface_breakdown"]["shell"] > 0
    assert summary["surface_breakdown"]["rust"] > 0
    assert summary["surface_breakdown"]["rust-tests"] > 0
    assert "plugins" in summary["excluded_source_dirs"]
    assert summary["skipped"]["status"] == "skipped"
    assert summary["skipped"]["count"] == 0
    assert summary["skipped"]["paths"] == []


def _ratio_invocation(runner_text: str) -> str:
    for line in runner_text.splitlines():
        stripped = line.strip()
        if stripped.startswith('queue_selected "check-test-production-ratio"'):
            return stripped
    raise AssertionError("run-quality.sh no longer queues check-test-production-ratio")


def test_ratio_gate_stays_advisory_in_the_runner() -> None:
    """Pin the posture the #420 resolution critique said nothing pinned.

    `2026-07-08-issue-420-resolution-critique.md:28` — "No gate pins the
    `--advisory` flag itself; silently dropping it restores the hard-block posture
    with no test failing." It was then dropped (`4122f6cd0`), and the hard block
    came back at a ratio with only 4-decimal rounding left, pulling against
    `release-changed-line-coverage`. This is that missing pin.
    """

    invocation = _ratio_invocation((ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8"))
    assert "--advisory" in invocation, (
        "check-test-production-ratio must stay advisory in run-quality.sh: a whole-repo "
        "LOC ratio is a smell sensor, not a release contract, and as a hard block it "
        "makes covering a changed line cost the deletion of production safety code"
    )
    # Negative control: the reader must FAIL a blocking invocation, or it pins nothing.
    blocking = (
        'queue_selected "check-test-production-ratio" python3 '
        'scripts/check_test_production_ratio.py --repo-root "$REPO_ROOT" --require-git-file-listing'
    )
    assert "--advisory" not in _ratio_invocation(blocking)


def test_surface_buckets_include_executable_languages_and_exclude_fixtures(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir()
    (repo / "tests").mkdir()
    (repo / "native" / "demo" / "src").mkdir(parents=True)
    (repo / "native" / "demo" / "tests").mkdir(parents=True)
    (repo / "native" / "demo" / "fixtures").mkdir(parents=True)

    (repo / "scripts" / "app.py").write_text("print('app')\n", encoding="utf-8")
    (repo / "tool").write_text("#!/usr/bin/env python3\nprint('tool')\n", encoding="utf-8")
    (repo / "scripts" / "app.sh").write_text(
        "#!/usr/bin/env bash\nprintf '%s\\n' app\n", encoding="utf-8"
    )
    (repo / ".githooks" / "pre-commit").write_text(
        "#!/usr/bin/env bash\nprintf '%s\\n' hook\n", encoding="utf-8"
    )
    (repo / "native" / "demo" / "src" / "lib.rs").write_text(
        "pub fn app() -> bool {\n    true\n}\n", encoding="utf-8"
    )
    (repo / "native" / "demo" / "build.rs").write_text(
        "fn main() {\n    println!(\"build\");\n}\n", encoding="utf-8"
    )
    (repo / "native" / "demo" / "tests" / "integration.rs").write_text(
        "#[test]\nfn app_works() {\n    assert!(true);\n}\n", encoding="utf-8"
    )
    (repo / "tests" / "test_app.py").write_text(
        "def test_app():\n    assert True\n", encoding="utf-8"
    )
    (repo / "native" / "demo" / "fixtures" / "ignored.py").write_bytes(b"\xff\n")
    (repo / "native" / "demo" / "fixtures" / "ignored.rs").write_text(
        "fn fixture() {}\n", encoding="utf-8"
    )
    (repo / "native" / "demo" / "fixtures" / "ignored.sh").write_text(
        "echo fixture\n", encoding="utf-8"
    )
    for name in ("settings.yaml", "settings.json", "settings.toml"):
        (repo / name).write_text("policy = true\n", encoding="utf-8")

    init_git_repo(
        repo,
        "scripts/app.py",
        "tool",
        "scripts/app.sh",
        ".githooks/pre-commit",
        "native/demo/src/lib.rs",
        "native/demo/build.rs",
        "native/demo/tests/integration.rs",
        "tests/test_app.py",
        "native/demo/fixtures/ignored.py",
        "native/demo/fixtures/ignored.rs",
        "native/demo/fixtures/ignored.sh",
        "settings.yaml",
        "settings.json",
        "settings.toml",
    )

    splitlines = RATIO.summarize(repo, engine="splitlines", require_git=True)
    tokei = RATIO.summarize(repo, engine="tokei", require_git=True)
    split_summary = RATIO._splitlines_summary(repo, require_git=True)
    assert split_summary["surface_file_buckets"] == {
        "python": ["scripts/app.py"],
        "python-shebang": ["tool"],
        "shell": [".githooks/pre-commit", "scripts/app.sh"],
        "rust": ["native/demo/build.rs", "native/demo/src/lib.rs"],
        "rust-tests": ["native/demo/tests/integration.rs"],
        "tests-python": ["tests/test_app.py"],
    }
    assert splitlines["source_lines"] == 1 + 2 + 4 + 6
    assert splitlines["test_lines"] == 4 + 2
    assert splitlines["source_file_count"] == 6
    assert splitlines["test_file_count"] == 2
    assert set(RATIO.SURFACE_BUCKETS) <= set(splitlines["surface_breakdown"])
    assert set(RATIO.SURFACE_BUCKETS) <= set(tokei["surface_breakdown"])
    assert tokei["source_file_count"] == splitlines["source_file_count"]
    assert tokei["test_file_count"] == splitlines["test_file_count"]
    assert tokei["surface_breakdown"]["python"] > 0
    assert tokei["surface_breakdown"]["python-shebang"] > 0
    assert tokei["surface_breakdown"]["shell"] > 0
    assert tokei["surface_breakdown"]["rust"] > 0
    assert tokei["surface_breakdown"]["rust-tests"] > 0
    assert tokei["surface_breakdown"]["tests-python"] > 0
    assert "python-shebang" not in tokei["surface_breakdown"].get("tokei_adjustments", {})
    assert tokei["surface_breakdown"]["tokei_adjustments"]["shell"]["files"] == [
        ".githooks/pre-commit"
    ]


def test_surface_file_buckets_are_shared_by_both_engines(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "native" / "demo" / "src").mkdir(parents=True)
    (repo / "native" / "demo" / "tests").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "script.py").write_text("print('source')\n", encoding="utf-8")
    (repo / "native" / "demo" / "src" / "lib.rs").write_text("fn main() {}\n", encoding="utf-8")
    (repo / "native" / "demo" / "tests" / "test.rs").write_text("#[test]\nfn it_works() {}\n", encoding="utf-8")
    (repo / "tests" / "test_script.py").write_text(
        "def test_script():\n    assert True\n", encoding="utf-8"
    )
    init_git_repo(
        repo,
        "script.py",
        "native/demo/src/lib.rs",
        "native/demo/tests/test.rs",
        "tests/test_script.py",
    )

    split_summary = RATIO._splitlines_summary(repo, require_git=True)
    tokei_summary = RATIO._tokei_summary(repo, require_git=True)

    assert split_summary["surface_file_buckets"] == tokei_summary["surface_file_buckets"]


def test_test_production_ratio_typed_skips_unreadable_python(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "scripts" / "app.py").write_text("print('line')\n", encoding="utf-8")
    (repo / "scripts" / "bad.py").write_bytes(b"\xff\n")
    (repo / "scripts" / "null_byte.py").write_bytes(b'print("before")\x00\n')
    (repo / "tests" / "test_app.py").write_text(
        "def test_app():\n    assert True\n", encoding="utf-8"
    )
    init_git_repo(
        repo,
        "scripts/app.py",
        "scripts/bad.py",
        "scripts/null_byte.py",
        "tests/test_app.py",
    )

    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    summary = RATIO.summarize(repo, engine="splitlines")

    assert summary["source_lines"] == 1
    assert summary["skipped"] == {
        "status": "skipped",
        "reason": "unreadable-python-source",
        "count": 2,
        "paths": ["scripts/bad.py", "scripts/null_byte.py"],
    }
    result = run_script(
        "scripts/check_test_production_ratio.py",
        "--repo-root",
        str(repo),
        "--max-ratio",
        "3",
    )
    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["skipped"] == summary["skipped"]


def test_test_production_ratio_fails_above_max() -> None:
    result = run_script(
        "scripts/check_test_production_ratio.py",
        "--repo-root",
        str(ROOT),
        "--max-ratio",
        "0.01",
    )

    assert result.returncode == 1
    assert "exceeds max" in result.stdout


def test_test_production_ratio_advisory_warns_above_max_without_blocking(monkeypatch, capsys) -> None:
    # --advisory demotes the over-threshold block to a non-blocking WARN posture
    # (north-star P1: a LOC ratio is a smell sensor, not an irreversible-boundary
    # contract). The WARN: prefix is what run-quality.sh:294 surfaces non-blocking.
    # Tested in-process (main() return value + captured stdout) rather than via
    # run_script: a second exit-contract subprocess assertion would flip this test
    # file to a keep-boundary in inventory_boundary_bypass and trip its ratchet.
    monkeypatch.setattr(
        sys, "argv",
        ["check_test_production_ratio.py", "--repo-root", str(ROOT), "--max-ratio", "0.01", "--advisory"],
    )

    rc = RATIO.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert "WARN:" in out
    assert "exceeds max" in out


def test_summarize_rejects_unknown_engine() -> None:
    with pytest.raises(ValueError):
        RATIO.summarize(ROOT, engine="cloc")


def test_auto_engine_falls_back_to_splitlines_without_tokei(monkeypatch) -> None:
    monkeypatch.setattr(RATIO.shutil, "which", lambda name: None)

    summary = RATIO.summarize(ROOT, engine="auto")

    assert summary["engine"] == "splitlines"
    assert summary["engine_selection"] == "auto"


def test_summarize_tokei_engine_raises_when_binary_missing(tmp_path: Path, monkeypatch) -> None:
    # Force the missing-binary path deterministically by pointing PATH at an empty
    # dir. tokei is installed locally AND in CI, so the old `skip` guard meant this
    # degraded-path assertion never ran in any standard environment (#368
    # test-quality fix). The tokei engine checks `shutil.which` before any file/git
    # work, so an empty PATH is safe.
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(RATIO.TokeiUnavailableError):
        RATIO.summarize(ROOT, engine="tokei")


def test_cli_tokei_engine_returns_two_when_binary_missing(tmp_path: Path) -> None:
    # Same #368 fix for the CLI surface: force the degraded path via an empty PATH
    # instead of skipping when tokei is present.
    nobin = tmp_path / "nobin"
    nobin.mkdir()
    result = run_script(
        "scripts/check_test_production_ratio.py",
        "--repo-root",
        str(ROOT),
        "--engine",
        "tokei",
        env={**os.environ, "PATH": str(nobin)},
    )

    assert result.returncode == 2
    assert "tokei" in result.stdout


def test_splitlines_ratio_ignores_gitignored_python_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / ".gitignore").write_text("scripts/generated.py\n", encoding="utf-8")
    (repo / "scripts" / "kept.py").write_text("print('kept')\n", encoding="utf-8")
    (repo / "scripts" / "generated.py").write_text("print('ignored')\n" * 100, encoding="utf-8")
    (repo / "tests" / "test_kept.py").write_text("def test_kept():\n    assert True\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "scripts/kept.py", "tests/test_kept.py")

    summary = RATIO.summarize(repo, engine="splitlines")

    assert summary["source_file_count"] == 1
    assert summary["source_lines"] == 1


def test_cli_under_threshold_returns_zero_on_synthetic_repo(tmp_path: Path, monkeypatch, capsys) -> None:
    # The under-threshold rc-0 main() branch previously had no synthetic fixture
    # (only the live repo exercised it, and the live ratio can sit over the
    # threshold); the other two main() ratio branches (blocking over-threshold
    # rc1, advisory WARN rc0) already have tests.
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "scripts" / "app.py").write_text("print('line')\n" * 20, encoding="utf-8")
    (repo / "tests" / "test_app.py").write_text(
        "def test_app():\n    assert True\n", encoding="utf-8"
    )
    init_git_repo(repo, "scripts/app.py", "tests/test_app.py")

    monkeypatch.setattr(sys, "argv", ["check_test_production_ratio.py", "--repo-root", str(repo)])

    rc = RATIO.main()
    payload = yaml.safe_load(capsys.readouterr().out)

    assert rc == 0
    # The "Test-production ratio: ..." sentence is gone; the same verdict is the
    # payload's `ratio` + `status`. `advisory` is the key the WARN posture adds,
    # so its absence is what "no WARN" means now.
    assert payload["status"] == "within-max"
    assert payload["ratio"] == pytest.approx(0.1)
    assert {
        "schema_version",
        "scope",
        "engine",
        "source_lines",
        "test_lines",
        "ratio",
        "source_file_count",
        "test_file_count",
        "excluded_source_dirs",
        "skipped",
        "max_ratio",
        "status",
    } <= payload.keys()
    assert "engine_selection" in payload
    assert payload["engine_selection"] == "auto"
    assert set(RATIO.SURFACE_BUCKETS) <= set(payload["surface_breakdown"])
    assert "advisory" not in payload
