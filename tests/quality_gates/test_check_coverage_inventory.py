from __future__ import annotations

import importlib.util
import json
import subprocess

from .support import ROOT

SPEC = importlib.util.spec_from_file_location(
    "check_coverage_module", ROOT / "scripts" / "check_coverage.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK_COVERAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_COVERAGE)

EXTRA_SPEC = importlib.util.spec_from_file_location(
    "check_coverage_extra_lib_under_test", ROOT / "scripts" / "check_coverage_extra_lib.py"
)
assert EXTRA_SPEC is not None and EXTRA_SPEC.loader is not None
CHECK_COVERAGE_EXTRA = importlib.util.module_from_spec(EXTRA_SPEC)
EXTRA_SPEC.loader.exec_module(CHECK_COVERAGE_EXTRA)


def test_per_file_floor_report_classifies_floor_violations() -> None:
    report = CHECK_COVERAGE.build_per_file_floor_report(
        [
            {
                "path": "scripts/weak.py",
                "covered": 20,
                "total": 100,
                "coverage": 0.2,
            },
            {
                "path": "scripts/warn.py",
                "covered": 90,
                "total": 100,
                "coverage": 0.9,
            },
            {
                "path": "scripts/small.py",
                "covered": 1,
                "total": 2,
                "coverage": 0.5,
            },
            {
                "path": "scripts/healthy.py",
                "covered": 98,
                "total": 100,
                "coverage": 0.98,
            },
        ]
    )

    assert report["status"] == "enforced"
    assert report["relationship"] == "per-file-floor"
    assert report["floor"] == 0.85
    assert [item["path"] for item in report["violations"]] == ["scripts/weak.py"]
    assert [item["path"] for item in report["warn_band"]] == ["scripts/warn.py"]


def test_check_coverage_json_includes_per_file_floor(monkeypatch, capsys) -> None:
    def fake_collect_counts(repo_root):
        return {
            (repo_root / rel_path).resolve(): CHECK_COVERAGE.executable_lines(repo_root / rel_path)
            for rel_path in CHECK_COVERAGE.TARGET_FILES
        }

    monkeypatch.setattr(CHECK_COVERAGE, "collect_counts", fake_collect_counts)
    monkeypatch.setattr(
        CHECK_COVERAGE.sys,
        "argv",
        ["check_coverage.py", "--repo-root", str(ROOT), "--json"],
    )

    assert CHECK_COVERAGE.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["per_file_floor"]["relationship"] == "per-file-floor"
    assert payload["per_file_floor"]["floor"] == 0.85


def test_executable_lines_ignore_signature_and_import_metadata(tmp_path) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text(
        "\n".join(
            [
                "from pathlib import (",
                "    Path,",
                ")",
                "",
                "def combine(",
                "    left,",
                "    right,",
                "):",
                "    return left / right",
                "",
            ]
        ),
        encoding="utf-8",
    )

    lines = CHECK_COVERAGE.executable_lines(sample)

    assert {1, 5, 9} <= lines
    assert 2 not in lines
    assert 6 not in lines
    assert 7 not in lines


def test_check_coverage_agent_browser_probe_ignores_ambient_orphans(monkeypatch, tmp_path) -> None:
    captured: list[dict[str, str]] = []

    def fake_run_traced_entry(_tracer, _script_path, *, argv, cwd, env_overrides):
        captured.append(env_overrides)

    monkeypatch.setattr(CHECK_COVERAGE, "run_traced_entry", fake_run_traced_entry)
    monkeypatch.setattr(CHECK_COVERAGE, "run_traced_function", lambda *_args, **_kwargs: None)

    # Probe against an isolated empty repo root rather than the live repo: the
    # captured env overrides are a fixed literal, so the live tree adds nothing
    # but its concurrent mutation under xdist can race `collect_counts`' internal
    # copytree and empty `captured`. See #225.
    CHECK_COVERAGE.collect_counts(tmp_path)

    assert captured
    assert all(item["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] == "1" for item in captured)


def test_control_plane_extra_coverage_probe_runs() -> None:
    CHECK_COVERAGE_EXTRA.exercise_control_plane_helper_scenarios()


def test_check_coverage_fixture_npm_does_not_touch_real_global_install(tmp_path) -> None:
    CHECK_COVERAGE.make_fake_npm(tmp_path)

    result = subprocess.run(
        [str(tmp_path / "npm"), "install", "-g", "agent-browser@latest"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "npm fixture installed agent-browser@latest" in result.stdout


def test_check_coverage_tracer_ignores_python_runtime_dirs(monkeypatch, tmp_path) -> None:
    captured: dict[str, tuple[str, ...]] = {}

    class FakeResults:
        counts: dict[tuple[str, int], int] = {}

    class FakeTrace:
        def __init__(self, **kwargs):
            captured["ignoredirs"] = tuple(kwargs.get("ignoredirs") or ())

        def results(self) -> FakeResults:
            return FakeResults()

    monkeypatch.setattr(CHECK_COVERAGE, "python_runtime_ignoredirs", lambda _repo_root: ("/python/runtime",))
    monkeypatch.setattr(CHECK_COVERAGE.trace, "Trace", FakeTrace)
    monkeypatch.setattr(CHECK_COVERAGE, "run_traced_entry", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(CHECK_COVERAGE, "run_traced_function", lambda *_args, **_kwargs: None)

    CHECK_COVERAGE.collect_counts(tmp_path)

    assert captured["ignoredirs"] == ("/python/runtime",)


def test_python_runtime_ignoredirs_collects_runtime_dirs(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        CHECK_COVERAGE.sysconfig,
        "get_paths",
        lambda: {
            "stdlib": "/python/stdlib",
            "platstdlib": "/python/stdlib",
            "purelib": "/python/site-packages",
            "platlib": "",
        },
    )
    monkeypatch.setattr(CHECK_COVERAGE.site, "getusersitepackages", lambda: "/python/user-site")
    monkeypatch.setattr(CHECK_COVERAGE.site, "getsitepackages", lambda: ["/python/global-site"])

    assert CHECK_COVERAGE.python_runtime_ignoredirs(tmp_path) == (
        "/python/global-site",
        "/python/site-packages",
        "/python/stdlib",
        "/python/user-site",
    )


def test_python_runtime_ignoredirs_skips_repo_parent_runtime_dir(monkeypatch, tmp_path) -> None:
    repo = tmp_path / "runtime" / "repo"
    repo.mkdir(parents=True)

    monkeypatch.setattr(
        CHECK_COVERAGE.sysconfig,
        "get_paths",
        lambda: {
            "stdlib": str(tmp_path / "runtime"),
            "platstdlib": "/python/platstdlib",
            "purelib": "",
            "platlib": "",
        },
    )
    monkeypatch.setattr(
        CHECK_COVERAGE.site,
        "getusersitepackages",
        lambda: (_ for _ in ()).throw(RuntimeError("site unavailable")),
    )
    monkeypatch.setattr(CHECK_COVERAGE.site, "getsitepackages", lambda: "/python/site")

    assert CHECK_COVERAGE.python_runtime_ignoredirs(repo) == (
        "/python/platstdlib",
        "/python/site",
    )
