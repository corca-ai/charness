from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_inventory_standing_gate_verbosity_flags_loud_runner_and_missing_escape_hatch(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    hook_path = repo / ".githooks" / "pre-push"
    hook_path.parent.mkdir(parents=True)
    hook_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "npm run verify",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "package.json").write_text(
        json.dumps(
            {
                "scripts": {
                    "verify": "node --test && pylint src",
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_standing_gate_verbosity.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["axes"]["test_runner_reporter"]["status"] == "weak"
    assert payload["axes"]["per_gate_chatter"]["status"] == "weak"
    assert payload["axes"]["escape_hatch"]["status"] == "missing"
    assert any(
        finding["type"] == "test_runner_reporter" and finding["tool"] == "node --test"
        for finding in payload["findings"]
    )
    assert any(
        finding["type"] == "per_gate_chatter" and finding["tool"] == "pylint"
        for finding in payload["findings"]
    )


def test_inventory_standing_gate_verbosity_flags_parallel_lefthook_output_risk(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "lefthook.yml").write_text(
        "\n".join(
            [
                "pre-push:",
                "  parallel: true",
                "  commands:",
                "    tests:",
                "      run: pytest -q",
                "    lint:",
                "      run: pylint src",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_standing_gate_verbosity.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["axes"]["test_runner_reporter"]["status"] == "healthy"
    assert payload["axes"]["orchestrator_output_mode"]["status"] == "weak"
    assert any(
        finding["type"] == "lefthook_parallel_output_unconfigured"
        for finding in payload["findings"]
    )


def test_inventory_standing_gate_verbosity_recognizes_shell_runner_thin_launcher(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run-pre-push.sh").write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'echo "pre-push: ok"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "lefthook.yml").write_text(
        "\n".join(
            [
                "pre-push:",
                "  parallel: true",
                "  commands:",
                "    quality:",
                "      run: ./scripts/run-pre-push.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_standing_gate_verbosity.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["axes"]["orchestrator_output_mode"]["status"] == "healthy"
    assert any(
        finding["type"] == "lefthook_thin_launcher"
        for finding in payload["findings"]
    )
    assert not any(
        finding["type"] == "lefthook_parallel_output_unconfigured"
        for finding in payload["findings"]
    )


def test_inventory_standing_gate_verbosity_recognizes_node_runner_thin_launcher(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run-pre-push.mjs").write_text(
        "console.log('pre-push: ok')\n",
        encoding="utf-8",
    )
    (repo / "lefthook.yml").write_text(
        "\n".join(
            [
                "pre-push:",
                "  parallel: true",
                "  commands:",
                "    quality:",
                "      run: node scripts/run-pre-push.mjs",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_standing_gate_verbosity.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["axes"]["orchestrator_output_mode"]["status"] == "healthy"
    assert any(
        finding["type"] == "lefthook_thin_launcher"
        for finding in payload["findings"]
    )


def test_inventory_standing_gate_verbosity_recognizes_charness_quiet_default() -> None:
    result = run_script(
        "skills/public/quality/scripts/inventory_standing_gate_verbosity.py",
        "--repo-root",
        str(ROOT),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["axes"]["test_runner_reporter"]["status"] == "healthy"
    assert payload["axes"]["per_gate_chatter"]["status"] == "healthy"
    assert payload["axes"]["phase_level_signal"]["status"] == "healthy"
    assert payload["axes"]["escape_hatch"]["status"] == "healthy"
