from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_nose_clones.py"


def test_nose_advisory_reports_missing_without_failing(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": str(tmp_path / "empty-bin"), "NOSE_BIN": ""},
    )

    assert result.returncode == 0
    assert "ADVISORY: nose missing" in result.stdout


def test_nose_advisory_uses_installed_binary(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_nose = bin_dir / "nose"
    fake_nose.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import sys

            assert sys.argv[1] == "scan"
            print(json.dumps([
                {
                    "value": 10.0,
                    "members": 2,
                    "files": 2,
                    "modules": 1,
                    "languages": 1,
                    "mean_score": 1.0,
                    "dup_lines": 12,
                    "shared_lines": 10,
                    "params": 1,
                    "locations": [
                        {"file": "scripts/a.py", "start_line": 1, "end_line": 10, "name": "a", "kind": "Function"},
                        {"file": "scripts/b.py", "start_line": 1, "end_line": 10, "name": "b", "kind": "Function"}
                    ]
                }
            ]))
            """
        ),
        encoding="utf-8",
    )
    fake_nose.chmod(0o755)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}", "NOSE_BIN": ""},
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "findings"
    assert payload["family_count"] == 1
    assert payload["total_dup_lines"] == 12
    assert payload["families"][0]["sample_locations"][0]["file"] == "scripts/a.py"
    # Advisory-interpretation contract: the proxy self-declares its blind spots
    # and the question the consumer must answer (inference-layer, not a verdict).
    interpretation = payload["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)


def test_nose_advisory_emits_interpretation_self_declaration(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_nose = bin_dir / "nose"
    fake_nose.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import sys

            assert sys.argv[1] == "scan"
            print(json.dumps([
                {
                    "value": 10.0, "members": 2, "files": 2, "modules": 1,
                    "languages": 1, "mean_score": 1.0, "dup_lines": 12,
                    "shared_lines": 10, "params": 1,
                    "locations": [
                        {"file": "scripts/a.py", "start_line": 1, "end_line": 10, "name": "a", "kind": "Function"},
                        {"file": "scripts/b.py", "start_line": 1, "end_line": 10, "name": "b", "kind": "Function"}
                    ]
                }
            ]))
            """
        ),
        encoding="utf-8",
    )
    fake_nose.chmod(0o755)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}", "NOSE_BIN": ""},
    )
    assert result.returncode == 0
    assert "INTERPRETATION" in result.stdout
    assert "Consumer must answer first" in result.stdout
    assert "intentional" in result.stdout  # the load-bearing blind spot


def test_nose_advisory_parses_v05_object_schema(tmp_path: Path) -> None:
    # nose 0.5 wraps families in a top-level object with tool_version; reading it
    # as a bare 0.4 array silently reported zero families. Lock the new shape in.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_nose = bin_dir / "nose"
    fake_nose.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import sys

            assert sys.argv[1] == "scan"
            print(json.dumps({
                "schema_version": 1,
                "tool_version": "0.5.0",
                "scope": {"files": 2},
                "ranking": {"total_families": 1, "shown_families": 1},
                "families": [
                    {
                        "value": 10.0,
                        "members": 2,
                        "files": 2,
                        "modules": 1,
                        "languages": 1,
                        "mean_score": 1.0,
                        "dup_lines": 12,
                        "shared_lines": 10,
                        "params": 1,
                        "locations": [
                            {"file": "scripts/a.py", "start_line": 1, "end_line": 10, "name": "a", "kind": "Function"},
                            {"file": "scripts/b.py", "start_line": 1, "end_line": 10, "name": "b", "kind": "Function"}
                        ]
                    }
                ]
            }))
            """
        ),
        encoding="utf-8",
    )
    fake_nose.chmod(0o755)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}", "NOSE_BIN": ""},
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "findings"
    assert payload["family_count"] == 1
    assert payload["tool_version"] == "0.5.0"
    assert payload["total_dup_lines"] == 12
    assert payload["families"][0]["sample_locations"][0]["file"] == "scripts/a.py"
