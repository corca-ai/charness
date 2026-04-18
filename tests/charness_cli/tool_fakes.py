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
