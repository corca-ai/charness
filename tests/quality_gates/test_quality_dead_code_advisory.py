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


def _run_dead_code_advisory(monkeypatch, bin_dir: Path, *args: str) -> dict:
    spec = importlib.util.spec_from_file_location("run_dead_code_advisory_cli_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "argv", ["run_dead_code_advisory.py", *args])
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ.get('PATH', '')}")
    with contextlib.redirect_stdout(buffer):
        assert module.main() == 0
    return json.loads(buffer.getvalue())


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

    payload = _run_dead_code_advisory(monkeypatch, bin_dir, "--repo-root", str(repo), "--summary")

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
