from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.repo_shapes import install_two_commit_repo
from tests.script_main import load_script_module, run_loaded_script_main

from .seeding_support import write_surface
from .support import ROOT, run_script

# `triggered` is a VERDICT KEY: present only when the probe reached a real answer, and
# `state` is key #1 of every payload. These cases pin the exit contract as much as the
# payload, because the reported miss was a caller that read `triggered: false` — the
# value that means "do nothing" — out of four different worlds where the probe had told
# it nothing. 0 = answered, 3 = could not tell, 1 = refused (broken config / hard error).
#
# The cases added for that fix run `main()` IN-PROCESS (`_run_main`) rather than through
# a new subprocess call site: the exit byte is what they are proving, and the in-process
# runner returns it without adding another process boundary. The existing subprocess
# cases stay subprocess cases because their process-level contract is the claim.
CHECK_AUTO_TRIGGER = load_script_module(
    "tests.quality_gates.retro_check_auto_trigger_main",
    ROOT / "skills/public/retro/scripts/check_auto_trigger.py",
)


def _run_main(*args: str):
    return run_loaded_script_main("check_auto_trigger.py", CHECK_AUTO_TRIGGER, *args)


def _write_adapter(repo: Path, *lines: str) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            ["version: 1", "repo: consumer", "output_dir: charness-artifacts/retro", *lines, ""]
        ),
        encoding="utf-8",
    )


def test_retro_auto_trigger_hits_configured_install_surface() -> None:
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["triggered"] is True
    assert "materialized-plugin-export" in payload["surface_hits"]


def test_retro_auto_trigger_skips_non_matching_slice() -> None:
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness-artifacts/docs-archive/retro-self-improvement-spec.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "evaluated"
    assert payload["triggered"] is False
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []


def test_retro_auto_trigger_matches_a_nested_capability_catalog_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(
        repo, "auto_session_trigger_path_globs:", "  - scripts/**/capability_catalog*.py"
    )

    result = _run_main(
        "--repo-root",
        str(repo),
        "--paths",
        "scripts/package/capability_catalog.py",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["triggered"] is True
    assert payload["path_hits"] == ["scripts/package/capability_catalog.py"]


# The four adapter-side worlds that all printed `triggered: false` + `"missing"` before.
# Each is a repo that never answered the trigger question, and none of them is a `no`.
@pytest.mark.parametrize(
    "adapter_lines, configuration_status",
    [
        pytest.param(None, "adapter-missing", id="no-adapter-on-disk"),
        pytest.param((), "unset", id="adapter-present-trigger-keys-unset"),
        pytest.param(
            ("auto_session_trigger_path_globs",),
            "adapter-partially-uninterpreted",
            id="trigger-line-the-parser-dropped",
        ),
        pytest.param(
            ("alias_target: &anchor x", "echo: *anchor"),
            "adapter-unreadable",
            id="adapter-the-parser-refused",
        ),
    ],
)
def test_retro_auto_trigger_is_undetermined_when_config_was_never_established(
    tmp_path: Path, adapter_lines, configuration_status: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    if adapter_lines is not None:
        _write_adapter(repo, *adapter_lines)

    result = _run_main("--repo-root", str(repo), "--paths", "README.md")

    # Exit 3, not 0: a shell caller must not be silently told "no". `triggered` is absent
    # entirely, so a caller reading key #1 cannot mistake a failure mode for a verdict.
    assert result.returncode == 3, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "not-established"
    assert "triggered" not in payload
    assert payload["configuration_status"] == configuration_status
    assert "no answer either way" in payload["reason"]
    assert "intentional opt-out" in payload["remediation"]
    if configuration_status in {"adapter-partially-uninterpreted", "adapter-unreadable"}:
        # The loader's own complaint is carried through verbatim. This also pins the
        # `" was not interpreted ("` marker `check_auto_trigger` matches on: if
        # `adapter_lib.uninterpreted_warnings` ever rewords, this case fails loudly
        # instead of the state quietly degrading back to a bare `missing`.
        assert payload["undetermined"], payload


def test_retro_auto_trigger_distinguishes_intentional_empty_trigger_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "auto_session_trigger_surfaces: []", "auto_session_trigger_path_globs: []")

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
    )

    # The ONE `triggered: false` that survives: an opt-out the repo wrote down, in an
    # adapter the loader read whole. Determined, so exit 0 and the key is present.
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "not-configured"
    assert payload["triggered"] is False
    assert payload["configuration_status"] == "intentional-empty"
    assert payload["reason"] == "Auto-retro trigger surfaces and path globs are explicitly empty."
    assert "remediation" not in payload


def test_retro_auto_trigger_intentional_empty_is_not_credited_from_a_half_read_adapter(
    tmp_path: Path,
) -> None:
    """Both trigger fields explicit `[]`, plus one line the parser dropped.

    The dropped line is exactly where a trigger key would have been — the loader says so
    itself — so this adapter cannot establish an opt-out either, and crediting one here
    would restore the hole through the back door."""
    repo = tmp_path / "repo"
    _write_adapter(
        repo,
        "auto_session_trigger_surfaces: []",
        "auto_session_trigger_path_globs: []",
        "metrics_commands",
    )

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 3, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "not-established"
    assert "triggered" not in payload
    assert payload["configuration_status"] == "adapter-partially-uninterpreted"


def test_retro_auto_trigger_undetermined_on_empty_changed_set() -> None:
    """The repeat trap this repo already walked into: a release helper committed and
    pushed, the working-tree diff went empty, and the probe answered `triggered: false`
    about a slice it could no longer see. Configured triggers plus zero changed paths
    compares nothing, so it is not a miss."""
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
    )
    assert result.returncode == 3, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "not-established"
    assert "triggered" not in payload
    assert payload["changed_paths"] == []
    assert any("EMPTY" in reason for reason in payload["undetermined"])


def test_retro_auto_trigger_hit_short_circuits_every_doubt(tmp_path: Path) -> None:
    """A hit is established by the paths that matched, so a half-read adapter downgrades
    it to an advisory rather than to `not-established`. Downgrading a hit would DISARM the
    trigger — the opposite of the defect being fixed."""
    repo = tmp_path / "repo"
    _write_adapter(
        repo,
        "auto_session_trigger_path_globs:",
        "  - 'docs/**'",
        "metrics_commands",
    )

    result = _run_main("--repo-root", str(repo), "--paths", "docs/index.md")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "evaluated"
    assert payload["triggered"] is True
    assert payload["path_hits"] == ["docs/index.md"]
    assert payload["advisories"], payload


def test_retro_auto_trigger_commit_range_survives_clean_tree(tmp_path: Path) -> None:
    adapter = "\n".join(
        [
            "version: 1",
            "repo: consumer",
            "output_dir: charness-artifacts/retro",
            "auto_session_trigger_surfaces:",
            "  - release-helper",
            "",
        ]
    )
    surfaces = {
        "version": 1,
        "surfaces": [
            {
                "surface_id": "release-helper",
                "description": "release helper scripts",
                "source_paths": ["skills/public/release/**"],
                "derived_paths": [],
                "sync_commands": [],
                "verify_commands": [],
                "notes": [],
            }
        ],
    }
    repo, _base, _head = install_two_commit_repo(
        tmp_path / "repo",
        {
            ".agents/retro-adapter.yaml": adapter,
            ".agents/surfaces.json": json.dumps(surfaces, indent=2) + "\n",
            "skills/public/release/scripts/publish_release.py": "print('before')\n",
        },
        {
            "skills/public/release/scripts/publish_release.py": "print('after')\n",
        },
        first_message="seed",
        second_message="change release helper",
    )

    # The clean tree is the point of this case: post-commit there is nothing to compare,
    # which is undetermined, NOT a miss. The explicit range below is how the same slice
    # gets a real answer, and that contrast is what the caller has to learn.
    clean_result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
    )
    assert clean_result.returncode == 3, clean_result.stdout
    clean_payload = yaml.safe_load(clean_result.stdout)
    assert clean_payload["state"] == "not-established"
    assert "triggered" not in clean_payload

    range_result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
        "--base-ref",
        "HEAD~1",
        "--head-ref",
        "HEAD",
    )

    assert range_result.returncode == 0, range_result.stderr
    payload = yaml.safe_load(range_result.stdout)
    assert payload["state"] == "evaluated"
    assert payload["triggered"] is True
    assert payload["input"]["mode"] == "commit_range"
    assert payload["changed_paths"] == ["skills/public/release/scripts/publish_release.py"]
    assert payload["surface_hits"] == ["release-helper"]


def test_retro_auto_trigger_fails_loud_on_unresolved_surface_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "auto_session_trigger_surfaces:", "  - release-packagng")
    write_surface(
        repo,
        "release-packaging",
        "release packaging surface",
        ["scripts/release/**"],
        derived_paths=["dist/**"],
    )

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
        "--paths",
        "scripts/release/verify-public-release.mjs",
    )

    # Exit 1, not 3: a typo'd surface id is a REFUSAL that needs an edit, not a re-run.
    # Both are nonzero and both carry `state: not-established`, so the JSON contract is
    # uniform ("not a no") while the byte still separates "fix this" from "ask again".
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    payload = yaml.safe_load(result.stderr)
    assert payload["state"] == "not-established"
    assert "triggered" not in payload
    assert payload["configuration_status"] == "broken"
    assert payload["unresolved_trigger_surfaces"] == ["release-packagng"]
    assert "auto_session_trigger_surfaces" in payload["reason"]
    assert "Fix the typo" in payload["remediation"]


def test_retro_auto_trigger_reports_missing_surfaces_remediation_when_configured(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "auto_session_trigger_surfaces:", "  - materialized-plugin-export")

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        real_process=True,
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    payload = yaml.safe_load(result.stderr)
    assert payload["state"] == "not-established"
    assert "triggered" not in payload
    assert "missing surfaces manifest" in payload["error"]
    assert ".agents/surfaces.json" in payload["remediation"]
