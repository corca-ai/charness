from __future__ import annotations

import textwrap
from pathlib import Path


def make_fake_cautilus(tmp_path: Path) -> Path:
    script = tmp_path / "bin" / "cautilus"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("cautilus 1.2.3")
                raise SystemExit(0)
            if args == ["doctor", "--help"]:
                print("cautilus doctor")
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def make_fake_pry(tmp_path: Path) -> Path:
    """Fake `pry` binary so the script-installer update can detect/healthcheck it.

    pry is a script-installer external tool (like nose); the fake `curl` from
    make_fake_nose handles the installer download, and this stub satisfies the
    manifest's detect (`pry --version` -> contains "pry") and healthcheck
    (`pry map --help` -> contains "risk ranking").
    """
    bin_dir = tmp_path / "pry-bin"
    pry = bin_dir / "pry"
    bin_dir.mkdir(parents=True, exist_ok=True)
    pry.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("pry 0.1.0")
                raise SystemExit(0)
            if args[:2] == ["map", "--help"]:
                print("Emit the risk map (risk ranking, NOT a bug list) for a path of TS/JS files")
                raise SystemExit(0)
            if args and args[0] == "map":
                print('{"corpus": "stub", "findings": [], "summary": {"files_scanned": 0, '
                      '"welded": 0, "seamed": 0, '
                      '"substitution_demand_subset": {"total": 0, "welded": 0, "seamed": 0}}}')
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    pry.chmod(0o755)
    return pry


def make_fake_nose(tmp_path: Path) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    nose = bin_dir / "nose"
    curl = bin_dir / "curl"
    bin_dir.mkdir(parents=True, exist_ok=True)
    nose.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("nose 0.6.0")
                raise SystemExit(0)
            if args == ["scan", "--help"]:
                print("Find duplicated code")
                raise SystemExit(0)
            if args and args[0] == "scan":
                print("[]")
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    nose.chmod(0o755)
    curl.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    curl.chmod(0o755)
    return curl, nose
