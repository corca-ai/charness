from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import textwrap
from pathlib import Path

from .support import ROOT, init_git_repo

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "run_dead_code_advisory.py"


def _run_dead_code_advisory_stdout(monkeypatch, bin_dir: Path, *args: str) -> str:
    spec = importlib.util.spec_from_file_location("run_dead_code_advisory_cli_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "argv", ["run_dead_code_advisory.py", *args])
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ.get('PATH', '')}")
    with contextlib.redirect_stdout(buffer):
        assert module.main() == 0
    return buffer.getvalue()


def _run_dead_code_advisory(monkeypatch, bin_dir: Path, *args: str) -> dict:
    return json.loads(_run_dead_code_advisory_stdout(monkeypatch, bin_dir, *args))


def _seed_fake_vulture(bin_dir: Path, *, sweep_finding: str | None) -> None:
    """Write a fake `vulture` that emits ``sweep_finding`` (exit 3) at confidence
    <= 60 and is clean (exit 0) otherwise, or is always clean when ``sweep_finding``
    is None."""
    lines = [
        "#!/usr/bin/env python3",
        "import sys",
        "confidence = int(sys.argv[sys.argv.index('--min-confidence') + 1])",
    ]
    if sweep_finding is not None:
        lines += ["if confidence <= 60:", f"    print({sweep_finding!r})", "    raise SystemExit(3)"]
    lines.append("raise SystemExit(0)")
    fake = bin_dir / "vulture"
    fake.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fake.chmod(0o755)


def test_dead_code_advisory_reports_primary_and_sweep(tmp_path: Path, monkeypatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_vulture = bin_dir / "vulture"
    fake_vulture.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            confidence = int(sys.argv[sys.argv.index("--min-confidence") + 1])
            if confidence <= 60:
                print("scripts/example.py:3: unused function 'old_helper' (60% confidence, 2 lines)")
                raise SystemExit(3)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    fake_vulture.chmod(0o755)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "scripts").mkdir()
    (repo / "scripts" / "example.py").write_text("def old_helper():\n    pass\n", encoding="utf-8")

    payload = _run_dead_code_advisory(monkeypatch, bin_dir, "--repo-root", str(repo), "--json")

    assert payload["primary"]["status"] == "clean"
    assert payload["sweep"]["status"] == "findings"
    assert payload["sweep"]["findings"] == [
        {
            "path": "scripts/example.py",
            "line": 3,
            "message": "unused function 'old_helper'",
            "confidence": 60,
            "size": 2,
            "classification": "review_candidate",
        }
    ]


def test_dead_code_advisory_summary_omits_full_command_and_findings(tmp_path: Path, monkeypatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_vulture = bin_dir / "vulture"
    fake_vulture.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            confidence = int(sys.argv[sys.argv.index("--min-confidence") + 1])
            if confidence <= 60:
                print("scripts/example.py:3: unused function 'old_helper' (60% confidence, 2 lines)")
                print("tests/conftest.py:1: unused variable 'pytest_plugins' (60% confidence, 1 line)")
                raise SystemExit(3)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    fake_vulture.chmod(0o755)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "scripts").mkdir()
    (repo / "scripts" / "example.py").write_text("def old_helper():\n    pass\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "conftest.py").write_text("pytest_plugins = []\n", encoding="utf-8")

    payload = _run_dead_code_advisory(
        monkeypatch,
        bin_dir,
        "--repo-root",
        str(repo),
        "--summary",
        "--json",
    )

    assert payload["summary_note"].startswith("summary is triage output")
    assert "command" not in payload["sweep"]
    assert "findings" not in payload["sweep"]
    assert payload["sweep"]["finding_count"] == 2
    assert payload["sweep"]["classification_counts"] == {
        "likely_framework_convention": 1,
        "review_candidate": 1,
    }
    assert payload["sweep"]["review_candidate_sample"] == [
        {
            "path": "scripts/example.py",
            "line": 3,
            "message": "unused function 'old_helper'",
            "confidence": 60,
            "size": 2,
            "classification": "review_candidate",
        }
    ]


def test_dead_code_advisory_human_output_surfaces_advisory_for_review_candidate(
    tmp_path: Path, monkeypatch
) -> None:
    # A review_candidate finding must produce a first-line `ADVISORY:` marker so
    # run-quality.sh's attention filter surfaces the opt-in gate without --verbose.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _seed_fake_vulture(bin_dir, sweep_finding="scripts/example.py:3: unused function 'old_helper' (60% confidence, 2 lines)")
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "example.py").write_text("def old_helper():\n    pass\n", encoding="utf-8")

    output = _run_dead_code_advisory_stdout(monkeypatch, bin_dir, "--repo-root", str(repo))

    first_line = output.splitlines()[0]
    assert first_line.startswith("ADVISORY:")
    assert "review_candidate" in first_line
    assert "never blocks" in first_line


def test_dead_code_advisory_human_output_omits_advisory_when_no_review_candidate(
    tmp_path: Path, monkeypatch
) -> None:
    # A clean sweep must emit no ADVISORY line, so the gate stays silent when there
    # is nothing to triage.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _seed_fake_vulture(bin_dir, sweep_finding=None)
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "example.py").write_text("KEEP = True\n", encoding="utf-8")

    output = _run_dead_code_advisory_stdout(monkeypatch, bin_dir, "--repo-root", str(repo))

    assert "ADVISORY:" not in output


def test_dead_code_advisory_human_output_survives_missing_vulture(tmp_path: Path, monkeypatch) -> None:
    # Regression: with vulture absent, run_vulture() returns a "missing" dict that has
    # no `classification_counts` key. The human output path must NOT crash on it — an
    # opted-in advisory gate has to stay exit-0 even when the tool is not installed,
    # otherwise it turns the quality run red (a blocker the fresh-eye review caught).
    spec = importlib.util.spec_from_file_location("run_dead_code_advisory_missing_vulture", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.shutil, "which", lambda _name: None)
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "example.py").write_text("KEEP = True\n", encoding="utf-8")
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "argv", ["run_dead_code_advisory.py", "--repo-root", str(repo)])
    with contextlib.redirect_stdout(buffer):
        assert module.main() == 0
    out = buffer.getvalue()
    assert "missing" in out
    assert "ADVISORY:" not in out


def test_dead_code_advisory_scans_untracked_nonignored_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text("ignored.py\n", encoding="utf-8")
    (repo / "tracked.py").write_text("TRACKED = True\n", encoding="utf-8")
    (repo / "untracked.py").write_text("UNTRACKED = True\n", encoding="utf-8")
    (repo / "ignored.py").write_text("IGNORED = True\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "tracked.py")

    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.git_visible_python_paths(repo, ("tracked.py", "untracked.py", "ignored.py")) == [
        "tracked.py",
        "untracked.py",
    ]


def test_dead_code_advisory_skips_deleted_tracked_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "tracked.py").write_text("TRACKED = True\n", encoding="utf-8")
    init_git_repo(repo, "tracked.py")
    (repo / "tracked.py").unlink()

    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.git_visible_python_paths(repo, ("tracked.py",)) == []


def test_dead_code_advisory_marks_pytest_conventions() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "tests/conftest.py:1: unused variable 'pytest_plugins' (60% confidence, 1 line)\n"
    )

    assert findings[0]["classification"] == "likely_framework_convention"


def test_dead_code_advisory_marks_pytest_fixture_candidates() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings("tests/conftest.py:12: unused function 'driver' (60% confidence, 5 lines)\n")

    assert findings[0]["classification"] == "likely_pytest_fixture"


def test_dead_code_advisory_marks_mock_and_test_protocol_noise() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "\n".join(
            [
                "tests/test_driver.py:8: unused attribute 'side_effect' (60% confidence, 1 line)",
                "tests/test_driver.py:20: unused method 'connect' (60% confidence, 3 lines)",
            ]
        )
        + "\n"
    )

    assert [finding["classification"] for finding in findings] == [
        "likely_mock_protocol",
        "likely_test_protocol",
    ]
    assert module.classification_counts(findings) == {
        "likely_mock_protocol": 1,
        "likely_test_protocol": 1,
    }


def test_dead_code_advisory_marks_structured_output_fields() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "scripts/agent_browser_runtime_guard.py:44: "
        "unused variable 'rss_kib' (60% confidence, 1 line)\n"
    )

    assert findings[0]["classification"] == "structured_output_field"


def test_dead_code_advisory_reclassifies_dataclass_annotated_fields(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    repo = tmp_path / "repo"
    source_path = repo / "scripts" / "payloads.py"
    source_path.parent.mkdir(parents=True)
    source_path.write_text(
        textwrap.dedent(
            """\
            from dataclasses import dataclass
            import dataclasses

            @dataclass
            class Payload:
                schema_value: str

            class Outer:
                @dataclasses.dataclass(frozen=True)
                class Nested:
                    nested_value: str

            class Ordinary:
                schema_value: str

            module_value: str
            """
        ),
        encoding="utf-8",
    )

    findings = module.parse_findings(
        "\n".join(
            [
                "scripts/payloads.py:6: unused variable 'schema_value' (60% confidence, 1 line)",
                "scripts/payloads.py:11: unused variable 'nested_value' (60% confidence, 1 line)",
                "scripts/payloads.py:14: unused variable 'schema_value' (60% confidence, 1 line)",
                "scripts/payloads.py:16: unused variable 'module_value' (60% confidence, 1 line)",
            ]
        ),
        repo_root=repo,
    )

    assert [finding["classification"] for finding in findings] == [
        "structured_output_field",
        "structured_output_field",
        "review_candidate",
        "review_candidate",
    ]


def test_dead_code_advisory_ignores_unreadable_dataclass_source(tmp_path: Path) -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory_unreadable_source", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    invalid_syntax = tmp_path / "invalid_syntax.py"
    invalid_syntax.write_text("def broken(:\n", encoding="utf-8")
    invalid_utf8 = tmp_path / "invalid_utf8.py"
    invalid_utf8.write_bytes(b"\xff")

    assert module._dataclass_field_locations(tmp_path / "missing.py") == set()
    assert module._dataclass_field_locations(invalid_syntax) == set()
    assert module._dataclass_field_locations(invalid_utf8) == set()
