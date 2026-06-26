from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from .support import ROOT

# In-process boundary conversion (testability-dsl-initiative goal 1): load the
# inventory entrypoint by file and call its `inventory()` lib function directly
# instead of spawning it as a subprocess. The script's `__file__`-based bootstrap
# resolves its sibling `standing_gate_verbosity_lib` regardless of sys.path, so no
# path setup is needed. `inventory()` returns the same payload the CLI `--json`
# mode serializes.
_SPEC = importlib.util.spec_from_file_location(
    "inventory_standing_gate_verbosity",
    ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_standing_gate_verbosity.py",
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
INVENTORY = _MODULE.inventory


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

    payload = INVENTORY(repo)
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

    payload = INVENTORY(repo)
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

    payload = INVENTORY(repo)
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

    payload = INVENTORY(repo)
    assert payload["axes"]["orchestrator_output_mode"]["status"] == "healthy"
    assert any(
        finding["type"] == "lefthook_thin_launcher"
        for finding in payload["findings"]
    )


def test_inventory_standing_gate_verbosity_recognizes_charness_quiet_default() -> None:
    payload = INVENTORY(ROOT)
    assert payload["axes"]["test_runner_reporter"]["status"] == "healthy"
    assert payload["axes"]["per_gate_chatter"]["status"] == "healthy"
    assert payload["axes"]["phase_level_signal"]["status"] == "healthy"
    assert payload["axes"]["escape_hatch"]["status"] == "healthy"
    assert payload["axes"]["failure_detail"]["status"] == "healthy"


def test_inventory_standing_gate_verbosity_flags_quiet_failure_without_detail(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".githooks").mkdir(parents=True)
    (repo / ".githooks" / "pre-push").write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [ "${VERBOSE:-0}" = "1" ]; then',
                "  specdown run -no-report",
                "else",
                "  specdown run -quiet -no-report",
                "fi",
                'echo "Spec runner summary: PASS"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = INVENTORY(repo)
    assert payload["axes"]["escape_hatch"]["status"] == "healthy"
    assert payload["axes"]["failure_detail"]["status"] == "weak"
    assert any(
        finding["type"] == "quiet_failure_detail"
        and finding["state"] == "needs_failure_detail"
        and "failing spec/case" in finding["suggestion"]
        for finding in payload["findings"]
    )


def test_inventory_standing_gate_verbosity_flags_suppressed_quiet_pytest_detail(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".githooks").mkdir(parents=True)
    (repo / ".githooks" / "pre-push").write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "pytest -q --tb=no >/dev/null",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = INVENTORY(repo)
    assert payload["axes"]["failure_detail"]["status"] == "weak"
    assert any(
        finding.get("tool") == "pytest"
        and finding["state"] == "needs_failure_detail"
        and "failing test/case" in finding["suggestion"]
        for finding in payload["findings"]
    )


def test_inventory_standing_gate_verbosity_cli_summary_omits_full_surfaces(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    hook_path = repo / ".githooks" / "pre-push"
    hook_path.parent.mkdir(parents=True)
    hook_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "pytest -q --tb=no >/dev/null",
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["inventory_standing_gate_verbosity.py", "--repo-root", str(repo), "--summary"],
    )

    assert _MODULE.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert "surfaces" not in payload
    assert "findings" not in payload
    assert payload["surface_count"] == 1
    assert payload["axes"]["failure_detail"]["status"] == "weak"
    assert any(finding["type"] == "quiet_failure_detail" for finding in payload["findings_sample"])
