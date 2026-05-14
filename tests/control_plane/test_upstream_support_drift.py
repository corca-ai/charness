"""Regression tests for scripts/check_upstream_support_drift.py.

The drift gate is the corca-ai/cautilus#32 root-cause prevention: a maintainer
who bumps `support_skill_source.ref` to a sibling release where the declared
`path` no longer exists must surface a hard fail, not a silent support-sync
regression masked by the v0.14.2 pin.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_upstream_support_drift.py"


def _run(repo_root: Path, fixture_path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    env = {
        "PATH": "/usr/bin:/bin",
        "CHARNESS_UPSTREAM_SUPPORT_PROBE_FIXTURES": str(fixture_path),
        "CHARNESS_UPSTREAM_SUPPORT_PROBE_NO_GH": "1",
    }
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root), *extra],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _seed_manifest(tmp_path: Path, **support_skill_source: object) -> Path:
    integrations_dir = tmp_path / "integrations" / "tools"
    integrations_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1",
        "tool_id": "demo",
        "kind": "external_binary_with_skill",
        "display_name": "demo",
        "summary": "test",
        "upstream_repo": "demo/upstream",
        "homepage": "https://github.com/demo/upstream",
        "platforms": ["linux"],
        "status": "active",
        "lifecycle": {"install": {"mode": "none"}},
        "checks": {
            "detect": {"commands": ["demo --version"], "success_criteria": ["exit_code:0"], "failure_hint": "."},
        },
        "access_modes": ["binary"],
        "version_expectation": {"policy": "advisory", "constraint": "", "detected_by": "stdout"},
        "supports_public_skills": ["impl"],
        "intent_triggers": ["demo trigger"],
        "recommendation_role": "runtime",
        "support_skill_source": support_skill_source,
    }
    path = integrations_dir / "demo.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def test_reports_ok_when_fixture_says_exists(tmp_path: Path) -> None:
    _seed_manifest(
        tmp_path,
        source_type="upstream_repo",
        path="skills/demo",
        ref="v1.0.0",
    )
    fixture = tmp_path / "fixtures.json"
    fixture.write_text(json.dumps({"demo/upstream:v1.0.0:skills/demo": "exists"}), encoding="utf-8")

    result = _run(tmp_path, fixture, "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["drift_count"] == 0
    assert payload["checked"][0]["status"] == "exists"
    assert payload["checked"][0]["tool_id"] == "demo"


def test_reports_drift_and_exits_nonzero_when_fixture_says_missing(tmp_path: Path) -> None:
    _seed_manifest(
        tmp_path,
        source_type="upstream_repo",
        path="skills/cautilus-agent",
        ref="v0.15.0",
    )
    fixture = tmp_path / "fixtures.json"
    fixture.write_text(
        json.dumps({"demo/upstream:v0.15.0:skills/cautilus-agent": "missing"}),
        encoding="utf-8",
    )

    result = _run(tmp_path, fixture, "--json")

    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["drift_count"] == 1
    assert payload["checked"][0]["status"] == "missing"


def test_probe_blocked_does_not_fail(tmp_path: Path) -> None:
    _seed_manifest(
        tmp_path,
        source_type="upstream_repo",
        path="skills/demo",
        ref="v1.0.0",
    )
    fixture = tmp_path / "fixtures.json"
    fixture.write_text(
        json.dumps({"demo/upstream:v1.0.0:skills/demo": "error:gh-forbidden"}),
        encoding="utf-8",
    )

    result = _run(tmp_path, fixture, "--json")

    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["drift_count"] == 0
    assert payload["checked"][0]["status"] == "error"
    assert payload["checked"][0]["reason"] == "gh-forbidden"


def test_skips_manifests_without_support_skill_source(tmp_path: Path) -> None:
    integrations_dir = tmp_path / "integrations" / "tools"
    integrations_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1",
        "tool_id": "no-support",
        "upstream_repo": "demo/upstream",
    }
    (integrations_dir / "no-support.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    fixture = tmp_path / "fixtures.json"
    fixture.write_text("{}", encoding="utf-8")

    result = _run(tmp_path, fixture, "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target_count"] == 0
    assert payload["checked"] == []


def test_text_output_labels_drift_explicitly(tmp_path: Path) -> None:
    _seed_manifest(
        tmp_path,
        source_type="upstream_repo",
        path="skills/missing",
        ref="main",
    )
    fixture = tmp_path / "fixtures.json"
    fixture.write_text(
        json.dumps({"demo/upstream:main:skills/missing": "missing"}),
        encoding="utf-8",
    )

    result = _run(tmp_path, fixture)

    assert result.returncode == 1, result.stdout
    assert "DRIFT: demo -> demo/upstream@main:skills/missing" in result.stdout
    assert "1 drift / 1 checked" in result.stdout
