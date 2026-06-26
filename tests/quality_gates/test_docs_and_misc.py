from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_narrative_map_sources_reports_checked_in_docs() -> None:
    result = run_script("skills/public/narrative/scripts/map_sources.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    source_paths = {entry["path"] for entry in payload["source_documents"]}
    assert "README.md" in source_paths
    assert "docs/handoff.md" in source_paths
    assert payload["artifact_path"] == "charness-artifacts/narrative/latest.md"
    assert payload["freshness"]["status"] in {"ahead", "current", "missing-remote", "not-git", "unavailable"}


def _write_release_repo(tmp_path: Path, *, with_sync: bool = True) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "packaging").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/release",
                "preset_id: portable-defaults",
                "customized_from: portable-defaults",
                "package_id: demo",
                "packaging_manifest_path: packaging/demo.json",
                "checked_in_plugin_root: plugins/demo",
                "sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .",
                "quality_command: ./scripts/run-quality.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest_text = (
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.0.0-dev",
                "summary": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "source": {"readme": "README.md", "skills_dir": "skills"},
                "codex": {"manifest": {"version": "0.0.0-dev"}},
                "claude": {"manifest": {"version": "0.0.0-dev"}},
            },
            indent=2,
        )
        + "\n"
    )
    (repo / "packaging" / "demo.json").write_text(manifest_text, encoding="utf-8")
    if with_sync:
        (repo / "scripts").mkdir(parents=True)
        (repo / "scripts" / "sync_root_plugin_manifests.py").write_text(
            "\n".join(
                [
                    "import argparse",
                    "import json",
                    "from pathlib import Path",
                    "",
                    "parser = argparse.ArgumentParser()",
                    "parser.add_argument('--repo-root', type=Path, required=True)",
                    "args = parser.parse_args()",
                    "repo_root = args.repo_root.resolve()",
                    "version = json.loads((repo_root / 'packaging' / 'demo.json').read_text())['version']",
                    "(repo_root / 'sync-version.txt').write_text(version + '\\n')",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    return repo, manifest_text


def test_release_bump_version_updates_manifest_and_runs_sync(tmp_path: Path) -> None:
    repo, _ = _write_release_repo(tmp_path)

    result = run_script("skills/public/release/scripts/bump_version.py", "--repo-root", str(repo), "--part", "patch")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["old_version"] == "0.0.0-dev"
    assert payload["new_version"] == "0.0.1"
    assert manifest["version"] == "0.0.1"
    assert manifest["claude"]["manifest"]["version"] == "0.0.1"
    assert manifest["codex"]["manifest"]["version"] == "0.0.1"
    assert (repo / "sync-version.txt").read_text(encoding="utf-8").strip() == "0.0.1"


def test_release_bump_version_rejects_malformed_set_version_without_mutating_manifest(
    tmp_path: Path,
) -> None:
    repo, manifest_text = _write_release_repo(tmp_path, with_sync=False)

    result = run_script(
        "skills/public/release/scripts/bump_version.py",
        "--repo-root",
        str(repo),
        "--set-version",
        "not.a.version",
    )

    assert result.returncode != 0
    assert (repo / "packaging" / "demo.json").read_text(encoding="utf-8") == manifest_text


def test_release_bump_version_applies_valid_set_version_and_runs_sync(tmp_path: Path) -> None:
    repo, _ = _write_release_repo(tmp_path)

    result = run_script(
        "skills/public/release/scripts/bump_version.py",
        "--repo-root",
        str(repo),
        "--set-version",
        "1.2.3",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["new_version"] == "1.2.3"
    assert manifest["version"] == "1.2.3"
    assert (repo / "sync-version.txt").read_text(encoding="utf-8").strip() == "1.2.3"
