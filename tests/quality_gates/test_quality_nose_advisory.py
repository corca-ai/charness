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


def test_nose_advisory_missing_json_preserves_scope_filters(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--exclude",
            "**/resolve_adapter.py",
            "--ignore-file",
            "nose.ignore.json",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": str(tmp_path / "empty-bin"), "NOSE_BIN": ""},
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "missing"
    assert payload["excludes"] == ["**/resolve_adapter.py"]
    assert payload["ignore_file"] == "nose.ignore.json"
    assert payload["scope"] == {}
    assert payload["ranking"] == {}


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

            args = sys.argv[1:]
            assert args[0] == "scan"
            assert args[args.index("--min-size") + 1] == "24"
            for legacy_flag in ("--threshold", "--min-lines", "--min-tokens"):
                assert legacy_flag not in args
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


def test_nose_advisory_passes_exclude_filters_to_nose(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_nose = bin_dir / "nose"
    fake_nose.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import sys

            args = sys.argv[1:]
            assert args[0] == "scan"
            assert args[args.index("--min-size") + 1] == "24"
            assert args.count("--exclude") == 2
            excludes = [args[index + 1] for index, value in enumerate(args) if value == "--exclude"]
            assert excludes == ["**/resolve_adapter.py", "plugins/**"]
            assert args[args.index("--ignore-file") + 1] == "nose.ignore.json"
            for legacy_flag in ("--threshold", "--min-lines", "--min-tokens"):
                assert legacy_flag not in args
            print(json.dumps({"schema_version": 1, "tool_version": "0.6.0", "families": []}))
            """
        ),
        encoding="utf-8",
    )
    fake_nose.chmod(0o755)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--exclude",
            "**/resolve_adapter.py",
            "--exclude",
            "plugins/**",
            "--ignore-file",
            "nose.ignore.json",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}", "NOSE_BIN": ""},
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "clean"
    assert payload["excludes"] == ["**/resolve_adapter.py", "plugins/**"]
    assert payload["ignore_file"] == "nose.ignore.json"


def test_nose_advisory_human_output_discloses_filtered_scope(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_nose = bin_dir / "nose"
    fake_nose.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            print(json.dumps({"schema_version": 1, "tool_version": "0.6.0", "families": []}))
            """
        ),
        encoding="utf-8",
    )
    fake_nose.chmod(0o755)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--exclude",
            "**/resolve_adapter.py",
            "--ignore-file",
            "nose.ignore.json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}", "NOSE_BIN": ""},
    )

    assert "SCOPE: filtered scan" in result.stdout
    assert "excludes=**/resolve_adapter.py" in result.stdout
    assert "ignore_file=nose.ignore.json" in result.stdout
    assert "Excluded findings are not resolved" in result.stdout


def test_nose_advisory_human_output_discloses_top_n_ranking(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_nose = bin_dir / "nose"
    fake_nose.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            print(json.dumps({
                "schema_version": 1,
                "tool_version": "0.6.0",
                "scope": {"files": 2},
                "ranking": {"total_families": 526, "shown_families": 20},
                "families": []
            }))
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

    assert "RANKING: showing 20 of 526 ranked families" in result.stdout


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

            args = sys.argv[1:]
            assert args[0] == "scan"
            assert args[args.index("--min-size") + 1] == "24"
            for legacy_flag in ("--threshold", "--min-lines", "--min-tokens"):
                assert legacy_flag not in args
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

            args = sys.argv[1:]
            assert args[0] == "scan"
            assert args[args.index("--min-size") + 1] == "24"
            for legacy_flag in ("--threshold", "--min-lines", "--min-tokens"):
                assert legacy_flag not in args
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
    assert payload["scope"] == {"files": 2}
    assert payload["ranking"] == {"total_families": 1, "shown_families": 1}
    assert payload["total_dup_lines"] == 12
    assert payload["families"][0]["sample_locations"][0]["file"] == "scripts/a.py"
