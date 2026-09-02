from __future__ import annotations

import importlib.util
import subprocess

import pytest
import yaml

from .support import ROOT

SPEC = importlib.util.spec_from_file_location(
    "check_coverage_module", ROOT / "tools" / "check_coverage.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK_COVERAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_COVERAGE)

EXTRA_SPEC = importlib.util.spec_from_file_location(
    "check_coverage_extra_lib_under_test", ROOT / "tools" / "check_coverage_extra_lib.py"
)
assert EXTRA_SPEC is not None and EXTRA_SPEC.loader is not None
CHECK_COVERAGE_EXTRA = importlib.util.module_from_spec(EXTRA_SPEC)
EXTRA_SPEC.loader.exec_module(CHECK_COVERAGE_EXTRA)

LIB_SPEC = importlib.util.spec_from_file_location(
    "check_coverage_lib_under_test", ROOT / "scripts" / "check_coverage_lib.py"
)
assert LIB_SPEC is not None and LIB_SPEC.loader is not None
CHECK_COVERAGE_LIB = importlib.util.module_from_spec(LIB_SPEC)
LIB_SPEC.loader.exec_module(CHECK_COVERAGE_LIB)


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


def test_check_coverage_payload_includes_per_file_floor(monkeypatch, capsys) -> None:
    def fake_collect_counts(repo_root):
        return {
            (repo_root / rel_path).resolve(): CHECK_COVERAGE.executable_lines(repo_root / rel_path)
            for rel_path in CHECK_COVERAGE.TARGET_FILES
        }

    monkeypatch.setattr(CHECK_COVERAGE, "collect_counts", fake_collect_counts)
    monkeypatch.setattr(
        CHECK_COVERAGE.sys,
        "argv",
        ["check_coverage.py", "--repo-root", str(ROOT)],
    )

    assert CHECK_COVERAGE.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
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


def test_exercise_control_plane_scenarios_executes_cleanly() -> None:
    CHECK_COVERAGE_LIB.exercise_control_plane_scenarios()


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


def test_per_file_floor_reports_the_population_it_exempts() -> None:
    """E5 regression, exemption half: the sub-threshold exemption was SILENT.

    A 0%-covered 29-statement file vanished from the report entirely while the
    same file at 30 statements was a violation, so "no violations" meant "no
    violations among the files we chose to look at". The threshold stays; the
    population it excuses is now named."""
    spec = importlib.util.spec_from_file_location(
        "check_coverage_lib_test", ROOT / "scripts" / "check_coverage_lib.py"
    )
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    files = [
        {"path": "tiny.py", "covered": 0, "total": 29, "coverage": 0.0},
        {"path": "big.py", "covered": 0, "total": 30, "coverage": 0.0},
        {"path": "fine.py", "covered": 29, "total": 29, "coverage": 1.0},
    ]

    report = lib.build_per_file_floor_report(files, floor=0.8)

    # The threshold is deliberate policy, but it was SILENT: a 0%-covered
    # 29-statement file vanished from the report while the same file at 30
    # statements was a violation.
    assert [item["path"] for item in report["violations"]] == ["big.py"]
    assert "tiny.py" in [item["path"] for item in report["exempt_below_threshold"]]
    assert [item["path"] for item in report["exempt_below_floor"]] == ["tiny.py"]
    # Falsifiable counterpart: an exempt file that meets the floor is not in the
    # hidden population.
    assert "fine.py" not in [item["path"] for item in report["exempt_below_floor"]]


def _coverage_module():
    spec = importlib.util.spec_from_file_location(
        "check_coverage_test", ROOT / "tools" / "check_coverage.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_coverage_summary_refuses_to_report_a_number_it_never_measured() -> None:
    """E5 regression, headline half: `covered/total if total else 1.0` reported
    a PERFECT score over zero observations, on the gate whose whole job is
    reporting test confidence.

    The summary now carries `measurement_scope` and a `None` coverage, and the
    CLI refuses legibly rather than reaching a `None < float` comparison — which
    is what shipped when this branch had no test at all."""
    from pathlib import Path as _Path

    module = _coverage_module()
    module.TARGET_FILES = ()

    summary = module.summarize(_Path("."), {})

    assert summary["measurement_scope"] == "empty"
    assert summary["coverage"] is None
    assert summary["unmeasured_files"] == []


def test_unmeasured_files_are_not_recorded_as_perfectly_covered() -> None:
    """A file with zero executable lines still carries `coverage: 1.0` from the
    per-file formula, so filing it under the small-file exemption recorded it as
    a perfectly-covered small file — and, being at the floor, kept it OUT of the
    list documented as the population the threshold hides. Unmeasured is its own
    bucket."""
    spec = importlib.util.spec_from_file_location(
        "check_coverage_lib_unmeasured", ROOT / "scripts" / "check_coverage_lib.py"
    )
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)

    report = lib.build_per_file_floor_report(
        [
            {"path": "empty.py", "covered": 0, "total": 0, "coverage": 1.0},
            {"path": "tiny.py", "covered": 0, "total": 29, "coverage": 0.0},
        ],
        floor=0.8,
    )

    assert [item["path"] for item in report["unmeasured"]] == ["empty.py"]
    assert "empty.py" not in [item["path"] for item in report["exempt_below_threshold"]]
    assert [item["path"] for item in report["exempt_below_floor"]] == ["tiny.py"]


def test_the_report_names_the_exempt_and_unmeasured_populations(monkeypatch, capsys) -> None:
    """The gate emits one payload on every run, and that payload is the only
    surface an operator reads. This is the whole reason the exemption stopped
    being silent: a file excused for having fewer than `PER_FILE_MIN_STATEMENTS`
    statements, and a file that contributed no observation at all, must both be
    NAMED rather than folded into the percent.
    """
    summary = {
        "coverage": 0.5,
        "covered": 1,
        "total": 2,
        "files": [
            {"path": "scripts/measured.py", "covered": 1, "total": 2, "coverage": 0.5, "measured": True},
            {"path": "scripts/empty.py", "covered": 0, "total": 0, "coverage": 1.0, "measured": False},
        ],
        "per_file_floor": {
            # `files_received`/`files_evaluated` are load-bearing in this fixture:
            # without them `coverage_report` fails CLOSED onto the UNESTABLISHED
            # caveat (correctly), and this — the only test that drives `main()`'s
            # emitted document — would stop observing the POPULATED arm that ships
            # on every real run. Round 2 caught the repair un-covering the old
            # branch while making the new one reachable.
            "files_received": 2,
            "files_evaluated": 1,
            "violations": [],
            "warn_band": [],
            "exempt_below_floor": [{"path": "scripts/tiny.py", "coverage": 0.1}],
            "min_statements_threshold": 30,
        },
        "unmeasured_files": ["scripts/empty.py"],
    }
    monkeypatch.setattr(CHECK_COVERAGE, "collect_counts", lambda repo_root: {})
    monkeypatch.setattr(CHECK_COVERAGE, "summarize", lambda *a, **k: summary)
    monkeypatch.setattr(
        CHECK_COVERAGE.sys, "argv", ["check_coverage.py", "--repo-root", str(ROOT), "--min-coverage", "0.1"]
    )

    assert CHECK_COVERAGE.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    # A file that contributed no observation is flagged as such per file, and
    # named again in its own bucket — never folded into the percent.
    unmeasured = [item for item in payload["files"] if not item["measured"]]
    assert [item["path"] for item in unmeasured] == ["scripts/empty.py"]
    assert payload["unmeasured_files"] == ["scripts/empty.py"]
    # The POPULATED arm: a floor comparison that actually ran reports its
    # violation/warn-band counts and carries no UNESTABLISHED caveat.
    floor = payload["per_file_floor"]
    assert (floor["files_received"], floor["files_evaluated"]) == (2, 1)
    assert floor["violations"] == [] and floor["warn_band"] == []
    assert "per_file_floor_caveat" not in payload
    # The excused population is named, together with the threshold that excused it.
    assert [item["path"] for item in floor["exempt_below_floor"]] == ["scripts/tiny.py"]
    assert floor["min_statements_threshold"] == 30


def test_cli_refuses_legibly_when_nothing_was_measured(monkeypatch) -> None:
    """The E5 refusal's CLI half: a `None` coverage must surface as this gate's
    own named error, not as a `None < float` TypeError traceback and not as the
    pre-fix perfect 1.0 over zero observations."""
    monkeypatch.setattr(CHECK_COVERAGE, "TARGET_FILES", ())
    monkeypatch.setattr(CHECK_COVERAGE, "collect_counts", lambda repo_root: {})
    monkeypatch.setattr(CHECK_COVERAGE.sys, "argv", ["check_coverage.py", "--repo-root", str(ROOT)])

    with pytest.raises(CHECK_COVERAGE.CoverageError) as excinfo:
        CHECK_COVERAGE.main()
    message = str(excinfo.value)
    assert "never measured" in message
    assert "no target files configured" in message
