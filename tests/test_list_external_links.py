from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "scripts/list_external_links.py", "--repo-root", str(repo_root)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_list_external_links_returns_unique_real_urls(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)

    (repo / "docs" / "guide.md").write_text(
        "\n".join(
            [
                "# Guide",
                "",
                "See https://github.com/corca-ai/charness for the repo homepage.",
                "Repeat https://github.com/corca-ai/charness here should dedupe.",
                "",
                "```bash",
                "curl https://workspace.slack.com/archives/C123/p1234567890123456",
                "```",
                "",
                "Ignore `/abs/path` and [local](/tmp/demo.md).",
                "",
                "Do not keep `https://github.com/corca-ai/specdown` inside inline code.",
                "",
                "Skip placeholders like https://example.com/demo and https://${WORKSPACE}.slack.com/api.",
                "Skip private placeholders like https://hr.example.internal/roster and https://demo.test/path.",
                "Skip localhost helpers like http://localhost:3000/health too.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "integrations" / "tools" / "demo.json").write_text(
        '{\n  "homepage": "https://github.com/corca-ai/specdown"\n}\n',
        encoding="utf-8",
    )
    (repo / "package-lock.json").write_text(
        '{\n  "resolved": "https://registry.npmjs.org/demo/-/demo-1.0.0.tgz"\n}\n',
        encoding="utf-8",
    )

    result = run_script(repo)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "https://github.com/corca-ai/charness",
        "https://github.com/corca-ai/specdown",
    ]
