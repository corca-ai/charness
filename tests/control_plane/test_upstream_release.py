from __future__ import annotations

import os
from pathlib import Path

from scripts.upstream_release_lib import probe_github_release


def test_probe_github_release_prefers_authenticated_gh_cli(
    tmp_path: Path, monkeypatch
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'printf "%s\\n" "$*" > "$GH_ARGS_PATH"',
                'cat <<\'JSON\'',
                "{",
                '  "tag_name": "v1.2.3",',
                '  "html_url": "https://github.com/example/tool/releases/tag/v1.2.3",',
                '  "published_at": "2026-04-15T00:00:00Z",',
                '  "assets": [{"name": "tool-linux-arm64.tar.gz"}]',
                "}",
                "JSON",
                "",
            ]
        ),
        encoding="utf-8",
    )
    gh.chmod(0o755)
    args_path = tmp_path / "gh-args.txt"

    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("GH_ARGS_PATH", str(args_path))
    monkeypatch.delenv("CHARNESS_RELEASE_PROBE_FIXTURES", raising=False)

    release = probe_github_release("example/tool")

    assert release["status"] == "ok"
    assert release["latest_tag"] == "v1.2.3"
    assert release["latest_version"] == "1.2.3"
    assert release["asset_names"] == ["tool-linux-arm64.tar.gz"]
    assert args_path.read_text(encoding="utf-8").strip() == (
        "api /repos/example/tool/releases/latest"
    )
