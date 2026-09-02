from __future__ import annotations

import json
from pathlib import Path

import yaml

from tests.script_main import run_loaded_script_main

from .release_script_loading import load_release_script
from .support import ROOT, run_script


def test_narrative_map_sources_reports_checked_in_docs() -> None:
    result = run_script("skills/public/narrative/scripts/map_sources.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    source_paths = {entry["path"] for entry in payload["source_documents"]}
    assert "README.md" in source_paths
    assert "docs/control-plane.md" in source_paths
    assert payload["artifact_path"] == "charness-artifacts/narrative/latest.md"
    assert payload["freshness"]["status"] in {
        "ahead",
        "current",
        "missing-remote",
        "not-git",
        "unavailable",
    }


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
                "materialized_plugin_root: plugins/demo",
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

    result = run_script(
        "skills/public/release/scripts/bump_version.py", "--repo-root", str(repo), "--part", "patch"
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
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


def test_release_bump_version_refuses_a_missing_sync_command_before_mutating(
    tmp_path: Path,
) -> None:
    """`sync_command` is RUN, and it runs AFTER the version is written.

    The inferred default names THIS authoring repo's `scripts/sync_root_plugin_manifests.py`,
    so a consuming repo that never wrote a release adapter inherits a command that cannot
    exist in its tree. Checked after the write, the bump lands and the sync does not: a
    bumped `packaging/` manifest with an unsynced plugin mirror, repairable only by hand.
    """
    repo, manifest_text = _write_release_repo(tmp_path, with_sync=False)
    bump_version = load_release_script("bump_version")

    # In-process rather than through `run_script`: the refusal is a `SystemExit` from
    # `main`; this assertion checks the returned refusal and does not need a
    # second interpreter or delivery-boundary contract.
    result = run_loaded_script_main(
        "bump_version.py", bump_version, "--repo-root", str(repo), "--part", "patch"
    )

    assert result.returncode != 0
    # A string only the PREFLIGHT emits. `sync_command` alone also appears in `run_sync`'s
    # own failure message, so with the preflight deleted this assertion would still pass
    # and only the unchanged-manifest one below would be red.
    assert "Nothing was bumped" in result.stderr
    assert (repo / "packaging" / "demo.json").read_text(encoding="utf-8") == manifest_text


def test_release_adapter_warns_when_an_executed_command_names_a_missing_script(
    tmp_path: Path,
) -> None:
    repo, _ = _write_release_repo(tmp_path, with_sync=False)

    resolve_adapter = load_release_script("resolve_adapter")

    warnings = " ".join(resolve_adapter.load_adapter(repo)["warnings"])
    # Both EXECUTED fields are unresolvable in this fixture: no `scripts/` at all.
    assert "sync_command" in warnings
    assert "quality_command" in warnings
    assert "set in the release adapter" in warnings

    # With no adapter file at all, the same two commands arrive from `infer_repo_defaults`
    # -- the shipped-default case, which is a charness defect rather than a consumer typo,
    # and the warning has to say which one it is.
    (repo / ".agents" / "release-adapter.yaml").unlink()
    inferred = resolve_adapter.load_adapter(repo)
    assert "inferred default" in " ".join(inferred["warnings"])
    # Exactly one warning per executed field: the loader has three exits and two of them
    # skip validation, so the re-derivation in `load_adapter` must not double-append.
    assert sum(resolve_adapter.EXECUTED_WARNING_MARKER in w for w in inferred["warnings"]) == 2


def test_release_adapter_does_not_judge_a_command_shape_it_cannot_read() -> None:
    """`None` means NOT JUDGED. A recognizer that guessed here would refuse working commands."""
    target = load_release_script("resolve_adapter").command_script_target

    assert target("python3 scripts/sync_root_plugin_manifests.py --repo-root .") == (
        "scripts/sync_root_plugin_manifests.py"
    )
    assert target("./scripts/run-quality.sh") == "scripts/run-quality.sh"
    for unreadable in (
        "",
        "make sync",
        "python3 -m charness.sync",
        "python3 $TOOLS/sync.py",
        "/usr/local/bin/sync.py",
        "npm run sync && python3 scripts/sync.py",
        "python3 ../outside/sync.py",
        # A review round found each of these mis-recognized: the recognizer answered a
        # literal that no shell would resolve, and the caller turns "does not exist" into
        # a hard refusal of a release that would have worked. These are the adversarial
        # half of the blind class -- the cases where guessing costs a false refusal, not
        # the cases the implementation obviously branches on.
        'python3 "scripts/a b.py"',
        "python3 'scripts/sync.py'",
        "python3 ~/tools/sync.py",
        "python3 scripts/*/sync.py",
        "python3 scripts/sync?.py",
        "python3 scripts\\sync.py",
        # Round 2 found each of these in the BLACKLIST written to stop the three above:
        # `split()` breaks on whitespace only, so an unspaced operator stays glued to the
        # candidate and the blacklist never saw it. Each was a hard refusal of a working
        # command. They are why the rule is an allowlist.
        "python3 scripts/sync.py; python3 scripts/mirror.py",
        "python3 scripts/sync.py&&python3 scripts/mirror.py",
        "python3 scripts/sync.py|tee sync.log",
        "python3 scripts/sync.py>sync.log",
        "python3 scripts/sync.py&",
        "python3 scripts/sync_{claude,codex}.py",
        "python3 scripts/sync[0-9].py",
        # Missed detections, named so the docstring's list is testable in both directions.
        "python3 -u scripts/sync.py",
        "FOO=1 python3 scripts/sync.py",
        "python3.11 scripts/sync.py",
        "cd sub && python3 scripts/sync.py",
    ):
        assert target(unreadable) is None, unreadable


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
    payload = yaml.safe_load(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["new_version"] == "1.2.3"
    assert manifest["version"] == "1.2.3"
    assert (repo / "sync-version.txt").read_text(encoding="utf-8").strip() == "1.2.3"
