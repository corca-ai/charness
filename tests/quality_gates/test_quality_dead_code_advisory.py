from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from .support import ROOT, init_git_repo

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "run_dead_code_advisory.py"


def test_dead_code_advisory_reports_primary_and_sweep(tmp_path: Path) -> None:
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

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"},
    )
    payload = json.loads(result.stdout)

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


def test_dead_code_advisory_marks_structured_output_fields() -> None:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("run_dead_code_advisory", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.parse_findings(
        "skills/support/agent-browser/scripts/runtime_guard.py:44: "
        "unused variable 'rss_kib' (60% confidence, 1 line)\n"
    )

    assert findings[0]["classification"] == "structured_output_field"
