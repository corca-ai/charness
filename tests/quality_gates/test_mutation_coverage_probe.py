from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.mutation_sampling_lib import run_test_coverage  # noqa: E402


def test_mutation_coverage_ignores_deleted_sources_outside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script = repo / "scripts" / "repo_target.py"
    test_file = repo / "tests" / "test_repo_target.py"
    outside_script = tmp_path / "outside" / "deleted_source.py"
    script.parent.mkdir(parents=True)
    test_file.parent.mkdir(parents=True)
    outside_script.parent.mkdir(parents=True)
    script.write_text("def value() -> int:\n    return 42\n", encoding="utf-8")
    outside_script.write_text("print('temporary source')\n", encoding="utf-8")
    test_file.write_text(
        dedent(
            f"""\
            from __future__ import annotations

            import runpy
            from pathlib import Path

            from scripts.repo_target import value


            def test_repo_and_deleted_outside_source() -> None:
                assert value() == 42
                runpy.run_path({str(outside_script)!r})
                Path({str(outside_script)!r}).unlink()
            """
        ),
        encoding="utf-8",
    )

    coverage_json = repo / "reports" / "mutation" / "coverage.json"
    run_test_coverage(repo, "python3 -m pytest -q tests/test_repo_target.py", coverage_json)

    payload = json.loads(coverage_json.read_text(encoding="utf-8"))
    assert "scripts/repo_target.py" in payload["files"]
    assert all("deleted_source.py" not in path for path in payload["files"])
